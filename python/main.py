#!/usr/bin/env python3

"""
Chandelier Exit - Tick CSV -> OHLC Candles -> CE Calculation -> Plot

Input CSV format:

Timestamp,Epoch,Symbol,Price,Delta_Change,Change_Percent
2026-09-15 10:45:05.730,1789449304,R_10,4905.7680,0.0000,0.000
...

The program:

    Tick data
        ↓
    OHLC candles
        ↓
    True Range
        ↓
    ATR (Wilder's RMA)
        ↓
    Chandelier Exit
        ↓
    Direction
        ↓
    Buy / Sell signals
        ↓
    Plot

No pandas_ta or TA-Lib is required.
The Chandelier Exit mathematics is implemented manually.
"""

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# USER SETTINGS
# ============================================================

CSV_FILE = "deriv_ticks_R_10_20260911_194045.csv"
# deriv_ticks_R_10_20260915_111147.csv
# deriv_ticks_R_10_20260915_104502.csv




# Candle size in seconds.
#
# Examples:
#   15   = 15-second candles
#   30   = 30-second candles
#   60   = 1-minute candles
#   120  = 2-minute candles
#   300  = 5-minute candles
#
TIMEFRAME_SECONDS = 300

# Chandelier Exit parameters
ATR_PERIOD = 22
ATR_MULTIPLIER = 3.0

# TradingView source:
#
# useClose = true
#
# True:
#     Highest/Lowest uses CLOSE
#
# False:
#     Highest uses HIGH
#     Lowest uses LOW
#
USE_CLOSE = True

# Plot options
SHOW_BUY_SELL = True
SHOW_RAW_STOPS = False
SHOW_ATR = False

# How many latest candles to display.
#
# None = display everything
# Example:
# PLOT_LAST_N = 500
#
PLOT_LAST_N = None


# ============================================================
# DATA CLASS
# ============================================================

@dataclass
class ChandelierResult:
    """
    Stores the final Chandelier Exit calculation.
    """

    data: pd.DataFrame


# ============================================================
# TICK DATA LOADER
# ============================================================

class TickDataLoader:
    """
    Loads tick CSV data and prepares it for candle generation.
    """

    REQUIRED_COLUMNS = [
        "Timestamp",
        "Epoch",
        "Symbol",
        "Price",
        "Delta_Change",
        "Change_Percent",
    ]

    def __init__(self, filename: str):
        self.filename = Path(filename)

    def load(self) -> pd.DataFrame:
        """
        Read CSV and validate required columns.
        """

        if not self.filename.exists():
            raise FileNotFoundError(
                f"CSV file not found: {self.filename}"
            )

        df = pd.read_csv(self.filename)

        # Check columns
        missing = [
            column
            for column in self.REQUIRED_COLUMNS
            if column not in df.columns
        ]

        if missing:
            raise ValueError(
                f"Missing CSV columns: {missing}"
            )

        # Convert timestamp
        df["Timestamp"] = pd.to_datetime(
            df["Timestamp"],
            errors="coerce"
        )

        # Convert price
        df["Price"] = pd.to_numeric(
            df["Price"],
            errors="coerce"
        )

        # Remove invalid rows
        df = df.dropna(
            subset=["Timestamp", "Price"]
        )

        # Sort by time
        df = df.sort_values(
            "Timestamp"
        )

        # Remove duplicate timestamps if any
        df = df.drop_duplicates(
            subset=["Timestamp"],
            keep="last"
        )

        # Timestamp becomes index
        df = df.set_index("Timestamp")

        return df


# ============================================================
# TICK -> OHLC CANDLE BUILDER
# ============================================================

class CandleBuilder:
    """
    Converts tick prices into OHLC candles.

    Example:

        15 seconds:
            10:00:00 -> 10:00:15
            10:00:15 -> 10:00:30

        60 seconds:
            10:00:00 -> 10:01:00
            10:01:00 -> 10:02:00
    """

    def __init__(self, timeframe_seconds: int):
        if timeframe_seconds <= 0:
            raise ValueError(
                "Timeframe must be greater than zero."
            )

        self.timeframe_seconds = timeframe_seconds

    @property
    def pandas_rule(self) -> str:
        """
        Convert seconds into pandas resampling rule.
        """

        return f"{self.timeframe_seconds}s"

    def build(self, ticks: pd.DataFrame) -> pd.DataFrame:
        """
        Build OHLC candles from tick prices.
        """

        candles = ticks["Price"].resample(
            self.pandas_rule
        ).ohlc()

        # Number of ticks inside each candle
        tick_count = ticks["Price"].resample(
            self.pandas_rule
        ).count()

        candles["TickCount"] = tick_count

        # Remove candles where there were no ticks
        candles = candles.dropna(
            subset=["open", "high", "low", "close"]
        )

        return candles


# ============================================================
# TRUE RANGE
# ============================================================

class TrueRangeCalculator:
    """
    Calculates True Range.

    TR = max(
        High - Low,
        abs(High - Previous Close),
        abs(Low - Previous Close)
    )
    """

    def calculate(self, candles: pd.DataFrame) -> pd.Series:

        high = candles["high"]
        low = candles["low"]
        close = candles["close"]

        previous_close = close.shift(1)

        range_high_low = high - low

        range_high_previous_close = (
            high - previous_close
        ).abs()

        range_low_previous_close = (
            low - previous_close
        ).abs()

        tr = pd.concat(
            [
                range_high_low,
                range_high_previous_close,
                range_low_previous_close,
            ],
            axis=1,
        ).max(axis=1)

        # First candle has no previous close.
        # For the first candle, High-Low is used.
        tr.iloc[0] = (
            high.iloc[0] - low.iloc[0]
        )

        return tr


# ============================================================
# ATR - WILDER'S RMA
# ============================================================

class ATRCalculator:
    """
    Calculates ATR using Wilder's RMA.

    Initial ATR:

        ATR[n] =
            SUM(TR[1:n]) / n

    Following values:

        ATR[t] =
            ATR[t-1] +
            (TR[t] - ATR[t-1]) / n

    This is equivalent to Wilder's RMA.
    """

    def __init__(self, period: int):
        if period <= 0:
            raise ValueError(
                "ATR period must be greater than zero."
            )

        self.period = period

    def calculate(
        self,
        true_range: pd.Series
    ) -> pd.Series:

        tr = true_range.to_numpy(
            dtype=float
        )

        atr = np.full(
            len(tr),
            np.nan,
            dtype=float
        )

        n = self.period

        # Not enough data
        if len(tr) < n:
            return pd.Series(
                atr,
                index=true_range.index,
                name="ATR",
            )

        # ----------------------------------------------------
        # Initial Wilder ATR = SMA of first N TR values
        # ----------------------------------------------------

        first_atr = np.mean(
            tr[:n]
        )

        atr[n - 1] = first_atr

        # ----------------------------------------------------
        # Wilder recursive calculation
        # ----------------------------------------------------

        for i in range(n, len(tr)):

            atr[i] = (
                atr[i - 1]
                + (tr[i] - atr[i - 1]) / n
            )

        return pd.Series(
            atr,
            index=true_range.index,
            name="ATR",
        )


# ============================================================
# CHANDELIER EXIT
# ============================================================

class ChandelierExit:
    """
    Implements the mathematical core of the TradingView
    Chandelier Exit by everget.

    Main equations:

        ATR distance = ATR * multiplier

        Long Stop =
            Highest(Close, period) - ATR distance

        Short Stop =
            Lowest(Close, period) + ATR distance

    When use_close=False:

        Long Stop =
            Highest(High, period) - ATR distance

        Short Stop =
            Lowest(Low, period) + ATR distance
    """

    def __init__(
        self,
        period: int = 22,
        multiplier: float = 3.0,
        use_close: bool = True,
    ):

        if period <= 0:
            raise ValueError(
                "Period must be greater than zero."
            )

        if multiplier <= 0:
            raise ValueError(
                "Multiplier must be greater than zero."
            )

        self.period = period
        self.multiplier = multiplier
        self.use_close = use_close

    def calculate(
        self,
        candles: pd.DataFrame
    ) -> ChandelierResult:

        df = candles.copy()

        # ====================================================
        # STEP 1
        # ====================================================

        tr_calculator = TrueRangeCalculator()

        df["TR"] = tr_calculator.calculate(
            df
        )

        # ====================================================
        # STEP 2
        # ATR
        # ====================================================

        atr_calculator = ATRCalculator(
            self.period
        )

        df["ATR"] = atr_calculator.calculate(
            df["TR"]
        )

        # ====================================================
        # STEP 3
        # ATR DISTANCE
        # ====================================================

        df["ATR_Distance"] = (
            df["ATR"] *
            self.multiplier
        )

        # ====================================================
        # STEP 4
        # EXTREMUM
        # ====================================================

        if self.use_close:

            highest = (
                df["close"]
                .rolling(
                    window=self.period
                )
                .max()
            )

            lowest = (
                df["close"]
                .rolling(
                    window=self.period
                )
                .min()
            )

        else:

            highest = (
                df["high"]
                .rolling(
                    window=self.period
                )
                .max()
            )

            lowest = (
                df["low"]
                .rolling(
                    window=self.period
                )
                .min()
            )

        df["Highest"] = highest
        df["Lowest"] = lowest

        # ====================================================
        # STEP 5
        # RAW LONG STOP
        # ====================================================

        df["LongStopRaw"] = (
            df["Highest"]
            - df["ATR_Distance"]
        )

        # ====================================================
        # STEP 6
        # RAW SHORT STOP
        # ====================================================

        df["ShortStopRaw"] = (
            df["Lowest"]
            + df["ATR_Distance"]
        )

        # ====================================================
        # STEP 7
        # FINAL TRAILING STOPS
        # ====================================================

        long_stop = np.full(
            len(df),
            np.nan,
            dtype=float
        )

        short_stop = np.full(
            len(df),
            np.nan,
            dtype=float
        )

        close = df["close"].to_numpy(
            dtype=float
        )

        raw_long = df["LongStopRaw"].to_numpy(
            dtype=float
        )

        raw_short = df["ShortStopRaw"].to_numpy(
            dtype=float
        )

        # ----------------------------------------------------
        # Calculate each candle sequentially.
        #
        # This is important because Chandelier Exit has
        # memory of the previous stop.
        # ----------------------------------------------------

        for i in range(len(df)):

            # Need a valid raw value first
            if np.isnan(raw_long[i]):
                continue

            # First valid candle
            if i == 0:

                long_stop[i] = raw_long[i]
                short_stop[i] = raw_short[i]

                continue

            # Previous stops
            previous_long = long_stop[i - 1]
            previous_short = short_stop[i - 1]

            # If previous values are not valid,
            # simply use current raw values.
            if np.isnan(previous_long):

                long_stop[i] = raw_long[i]
                short_stop[i] = raw_short[i]

                continue

            # =================================================
            # LONG STOP
            #
            # TradingView:
            #
            # close[1] > longStopPrev
            #
            #     longStop =
            #         max(longStop, longStopPrev)
            #
            # else:
            #
            #     longStop = longStop
            # =================================================

            if close[i - 1] > previous_long:

                long_stop[i] = max(
                    raw_long[i],
                    previous_long
                )

            else:

                long_stop[i] = raw_long[i]

            # =================================================
            # SHORT STOP
            #
            # TradingView:
            #
            # close[1] < shortStopPrev
            #
            #     shortStop =
            #         min(shortStop, shortStopPrev)
            #
            # else:
            #
            #     shortStop = shortStop
            # =================================================

            if close[i - 1] < previous_short:

                short_stop[i] = min(
                    raw_short[i],
                    previous_short
                )

            else:

                short_stop[i] = raw_short[i]

        df["LongStop"] = long_stop
        df["ShortStop"] = short_stop

        # ====================================================
        # STEP 8
        # DIRECTION STATE MACHINE
        # ====================================================

        direction = np.full(
            len(df),
            np.nan,
            dtype=float
        )

        # TradingView starts with:
        #
        # var int dir = 1
        #
        current_direction = 1

        for i in range(len(df)):

            if i == 0:
                direction[i] = current_direction
                continue

            previous_long = long_stop[i - 1]
            previous_short = short_stop[i - 1]

            if np.isnan(
                previous_long
            ) or np.isnan(
                previous_short
            ):

                direction[i] = current_direction
                continue

            # ------------------------------------------------
            # TradingView:
            #
            # close > shortStopPrev ? 1 :
            # close < longStopPrev ? -1 :
            # dir
            # ------------------------------------------------

            if close[i] > previous_short:

                current_direction = 1

            elif close[i] < previous_long:

                current_direction = -1

            # Otherwise:
            #
            # Keep previous direction.

            direction[i] = current_direction

        df["Direction"] = direction

        # ====================================================
        # STEP 9
        # BUY / SELL SIGNALS
        # ====================================================

        previous_direction = (
            df["Direction"].shift(1)
        )

        df["BuySignal"] = (
            (df["Direction"] == 1)
            &
            (previous_direction == -1)
        )

        df["SellSignal"] = (
            (df["Direction"] == -1)
            &
            (previous_direction == 1)
        )

        # ====================================================
        # STEP 10
        # ACTIVE STOP
        # ====================================================

        df["ActiveStop"] = np.where(
            df["Direction"] == 1,
            df["LongStop"],
            df["ShortStop"],
        )

        return ChandelierResult(
            data=df
        )


# ============================================================
# PLOTTER
# ============================================================

class ChandelierPlotter:
    """
    Displays price, Chandelier stops and signals.
    """

    def __init__(
        self,
        data: pd.DataFrame,
        timeframe_seconds: int,
        atr_period: int,
        atr_multiplier: float,
    ):

        self.data = data
        self.timeframe_seconds = timeframe_seconds
        self.atr_period = atr_period
        self.atr_multiplier = atr_multiplier

    def plot(
        self,
        show_buy_sell: bool = True,
        show_raw_stops: bool = False,
        show_atr: bool = False,
        last_n=None,
    ):

        df = self.data.copy()

        # Display only latest N candles if requested
        if last_n is not None:
            df = df.tail(last_n)

        if df.empty:
            print("Nothing to plot.")
            return

        # ----------------------------------------------------
        # Create figure
        # ----------------------------------------------------

        if show_atr:

            fig, (ax_price, ax_atr) = plt.subplots(
                2,
                1,
                figsize=(15, 9),
                sharex=True,
                gridspec_kw={
                    "height_ratios": [3, 1]
                },
            )

        else:

            fig, ax_price = plt.subplots(
                figsize=(15, 8)
            )

            ax_atr = None

        # ====================================================
        # PRICE
        # ====================================================

        ax_price.plot(
            df.index,
            df["close"],
            label="Close",
            linewidth=1.2,
        )

        # ----------------------------------------------------
        # Long Stop
        # ----------------------------------------------------

        long_data = df["LongStop"].where(
            df["Direction"] == 1
        )

        ax_price.plot(
            df.index,
            long_data,
            label="Long Stop",
            linewidth=1.8,
        )

        # ----------------------------------------------------
        # Short Stop
        # ----------------------------------------------------

        short_data = df["ShortStop"].where(
            df["Direction"] == -1
        )

        ax_price.plot(
            df.index,
            short_data,
            label="Short Stop",
            linewidth=1.8,
        )

        # ====================================================
        # RAW STOPS
        # ====================================================

        if show_raw_stops:

            ax_price.plot(
                df.index,
                df["LongStopRaw"],
                label="Raw Long Stop",
                linestyle="--",
                linewidth=0.8,
            )

            ax_price.plot(
                df.index,
                df["ShortStopRaw"],
                label="Raw Short Stop",
                linestyle="--",
                linewidth=0.8,
            )

        # ====================================================
        # BUY SIGNALS
        # ====================================================

        if show_buy_sell:

            buy = df[
                df["BuySignal"]
            ]

            sell = df[
                df["SellSignal"]
            ]

            if not buy.empty:

                ax_price.scatter(
                    buy.index,
                    buy["LongStop"],
                    marker="^",
                    s=70,
                    label="BUY",
                    zorder=5,
                )

            if not sell.empty:

                ax_price.scatter(
                    sell.index,
                    sell["ShortStop"],
                    marker="v",
                    s=70,
                    label="SELL",
                    zorder=5,
                )

        # ====================================================
        # PRICE LABELS
        # ====================================================

        ax_price.set_title(
            "Chandelier Exit"
        )

        ax_price.set_ylabel(
            "Price"
        )

        ax_price.grid(
            True,
            alpha=0.25
        )

        ax_price.legend()

        # ====================================================
        # ATR PANEL
        # ====================================================

        if show_atr:

            ax_atr.plot(
                df.index,
                df["ATR"],
                label="ATR",
                linewidth=1.2,
            )

            ax_atr.set_ylabel(
                "ATR"
            )

            ax_atr.grid(
                True,
                alpha=0.25
            )

            ax_atr.legend()

        # ====================================================
        # FINAL LAYOUT
        # ====================================================

        timeframe_text = (
            f"{self.timeframe_seconds} seconds"
        )

        fig.suptitle(
            f"Chandelier Exit | "
            f"Timeframe: {timeframe_text} | "
            f"ATR Period: {self.atr_period} | "
            f"Multiplier: {self.atr_multiplier}"
        )

        plt.tight_layout()

        plt.show()


# ============================================================
# DEBUG / TABLE OUTPUT
# ============================================================

class ChandelierDebugger:
    """
    Prints the mathematical calculation so you can inspect
    what the algorithm is doing candle by candle.
    """

    def __init__(
        self,
        data: pd.DataFrame
    ):
        self.data = data

    def print_last(self, count: int = 20):

        columns = [
            "open",
            "high",
            "low",
            "close",
            "TR",
            "ATR",
            "ATR_Distance",
            "Highest",
            "Lowest",
            "LongStopRaw",
            "LongStop",
            "ShortStopRaw",
            "ShortStop",
            "Direction",
            "BuySignal",
            "SellSignal",
        ]

        available = [
            column
            for column in columns
            if column in self.data.columns
        ]

        result = self.data[
            available
        ].tail(count)

        pd.set_option(
            "display.max_columns",
            None
        )

        pd.set_option(
            "display.width",
            250
        )

        pd.set_option(
            "display.float_format",
            lambda value: f"{value:.6f}"
        )

        print()
        print("=" * 150)
        print("CHANDAELIER EXIT CALCULATION")
        print("=" * 150)

        print(result)

        print("=" * 150)


# ============================================================
# MAIN APPLICATION
# ============================================================

class ChandelierApplication:
    """
    Main application controller.

    This class connects:

        CSV
         ↓
        Ticks
         ↓
        Candles
         ↓
        Chandelier Exit
         ↓
        Debug
         ↓
        Plot
    """

    def __init__(self):

        self.csv_file = CSV_FILE
        self.timeframe_seconds = TIMEFRAME_SECONDS
        self.atr_period = ATR_PERIOD
        self.atr_multiplier = ATR_MULTIPLIER
        self.use_close = USE_CLOSE

    def run(self):

        print()
        print("=" * 70)
        print("CHANDELIER EXIT")
        print("=" * 70)

        print(
            f"CSV File       : {self.csv_file}"
        )

        print(
            f"Candle Period  : "
            f"{self.timeframe_seconds} seconds"
        )

        print(
            f"ATR Period     : "
            f"{self.atr_period}"
        )

        print(
            f"ATR Multiplier : "
            f"{self.atr_multiplier}"
        )

        print(
            f"Use Close      : "
            f"{self.use_close}"
        )

        print("=" * 70)

        # ====================================================
        # 1. LOAD TICKS
        # ====================================================

        loader = TickDataLoader(
            self.csv_file
        )

        ticks = loader.load()

        print(
            f"Loaded ticks   : {len(ticks)}"
        )

        # ====================================================
        # 2. BUILD CANDLES
        # ====================================================

        candle_builder = CandleBuilder(
            self.timeframe_seconds
        )

        candles = candle_builder.build(
            ticks
        )

        print(
            f"Created candles: {len(candles)}"
        )

        # ====================================================
        # 3. CHANDELIER EXIT
        # ====================================================

        chandelier = ChandelierExit(
            period=self.atr_period,
            multiplier=self.atr_multiplier,
            use_close=self.use_close,
        )

        result = chandelier.calculate(
            candles
        )

        df = result.data

        # ====================================================
        # 4. DEBUG OUTPUT
        # ====================================================

        debugger = ChandelierDebugger(
            df
        )

        debugger.print_last(
            count=20
        )

        # ====================================================
        # 5. PLOT
        # ====================================================

        plotter = ChandelierPlotter(
            data=df,
            timeframe_seconds=self.timeframe_seconds,
            atr_period=self.atr_period,
            atr_multiplier=self.atr_multiplier,
        )

        plotter.plot(
            show_buy_sell=SHOW_BUY_SELL,
            show_raw_stops=SHOW_RAW_STOPS,
            show_atr=SHOW_ATR,
            last_n=PLOT_LAST_N,
        )


# ============================================================
# PROGRAM ENTRY POINT
# ============================================================

def main():

    application = ChandelierApplication()

    try:

        application.run()

    except FileNotFoundError as error:

        print(
            f"\nERROR: {error}"
        )

    except Exception as error:

        print(
            f"\nERROR: {error}"
        )

        raise


if __name__ == "__main__":
    main()