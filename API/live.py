#!/usr/bin/env python3

"""
LIVE DERIV CHANDELIER EXIT

Architecture:

    Deriv WebSocket
          |
          v
      TickBuffer
          |
          v
      CandleBuilder
          |
          v
     True Range
          |
          v
      ATR / RMA
          |
          v
   Chandelier Exit
          |
          v
    Direction State
          |
          v
    BUY / SELL
          |
          v
    Live Matplotlib


IMPORTANT:
    This program is MONITORING / ANALYSIS only.
    It does NOT place trades.
"""

import json
import os
import time
import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from collections import deque

import numpy as np
import pandas as pd
import requests
import websocket

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.animation import FuncAnimation


# ============================================================
# USER CONFIGURATION
# ============================================================

APP_ID = os.getenv(
    "DERIV_APP_ID_PY",
    "YOUR_APP_ID"
)

AUTH_TOKEN = os.getenv(
    "DERIV_API_TOKEN_PY",
    "YOUR_AUTH_TOKEN"
)

ACCOUNT_ID = os.getenv(
    "DERIV_ACCOUNT_ID",
    "YOUR_ACCOUNT_ID"
)

SYMBOL = "frxXAUUSD"


# ------------------------------------------------------------
# CANDLE SETTINGS
# ------------------------------------------------------------

# 60 = 1 minute
#
# Change:
#
# 15  = 15 seconds
# 30  = 30 seconds
# 60  = 1 minute
# 120 = 2 minutes
# 300 = 5 minutes
#
TIMEFRAME_SECONDS = 60


# ------------------------------------------------------------
# CHANDELIER EXIT SETTINGS
# ------------------------------------------------------------

ATR_PERIOD = 22

ATR_MULTIPLIER = 3.0

# TradingView:
#
# true  -> highest/lowest CLOSE
# false -> highest HIGH / lowest LOW
#
USE_CLOSE = True


# ------------------------------------------------------------
# GRAPH SETTINGS
# ------------------------------------------------------------

# Number of candles shown on graph
MAX_CANDLES_ON_GRAPH = 150

# Number of historical ticks requested for warm-up
HISTORY_TICKS = 1000

# Update graph every this many milliseconds
GRAPH_UPDATE_MS = 500


# ============================================================
# DATA CLASSES
# ============================================================

@dataclass
class Tick:
    """
    One market tick.
    """

    epoch: int
    price: float
    symbol: str


@dataclass
class Candle:
    """
    One OHLC candle.
    """

    timestamp: pd.Timestamp
    open: float
    high: float
    low: float
    close: float
    tick_count: int = 0


# ============================================================
# DERIV CLIENT
# ============================================================

class DerivClient:
    """
    Handles:

        REST OTP
        WebSocket connection
        Tick subscription
        Historical tick request
    """

    BASE_URL = "https://api.derivws.com"

    def __init__(
        self,
        app_id: str,
        auth_token: str,
        account_id: str,
    ):

        self.app_id = app_id
        self.auth_token = auth_token
        self.account_id = account_id

        self.ws = None

        self.running = False

        # Callback for every received tick
        self.tick_callback = None

        # Callback for historical data
        self.history_callback = None

    # --------------------------------------------------------
    # OTP
    # --------------------------------------------------------

    def get_socket_url(self) -> str:

        url = (
            f"{self.BASE_URL}"
            f"/trading/v1/options/accounts/"
            f"{self.account_id}/otp"
        )

        headers = {
            "Deriv-App-ID": self.app_id,
            "Authorization": (
                f"Bearer {self.auth_token}"
            ),
        }

        response = requests.post(
            url,
            headers=headers,
            timeout=10,
        )

        response.raise_for_status()

        data = response.json()

        if "error" in data:

            raise RuntimeError(
                f"Deriv API Error: {data['error']}"
            )

        if "errors" in data:

            raise RuntimeError(
                f"Deriv API Error: {data['errors']}"
            )

        return data["data"]["url"]

    # --------------------------------------------------------
    # CONNECT
    # --------------------------------------------------------

    def connect(self):

        socket_url = self.get_socket_url()

        print()
        print("Socket URL received")
        print("Connecting to Deriv...")

        self.ws = websocket.create_connection(
            socket_url,
            timeout=10,
        )

        self.running = True

        print("Connected!")

    # --------------------------------------------------------
    # REQUEST HISTORICAL TICKS
    # --------------------------------------------------------

    def request_history(
        self,
        symbol: str,
        count: int,
    ):

        request = {
            "ticks_history": symbol,
            "count": count,
            "end": "latest",
            "style": "ticks",
        }

        self.ws.send(
            json.dumps(request)
        )

        print(
            f"Requested {count} historical ticks"
        )

    # --------------------------------------------------------
    # SUBSCRIBE
    # --------------------------------------------------------

    def subscribe_ticks(
        self,
        symbol: str,
    ):

        request = {
            "ticks": symbol,
            "subscribe": 1,
        }

        self.ws.send(
            json.dumps(request)
        )

        print(
            f"Subscribed: {symbol}"
        )

    # --------------------------------------------------------
    # SET CALLBACKS
    # --------------------------------------------------------

    def set_tick_callback(
        self,
        callback,
    ):

        self.tick_callback = callback

    def set_history_callback(
        self,
        callback,
    ):

        self.history_callback = callback

    # --------------------------------------------------------
    # RECEIVE LOOP
    # --------------------------------------------------------

    def receive_loop(self):

        while self.running:

            try:

                message = self.ws.recv()

                if not message:
                    continue

                data = json.loads(
                    message
                )

                msg_type = data.get(
                    "msg_type"
                )

                # --------------------------------------------
                # LIVE TICK
                # --------------------------------------------

                if msg_type == "tick":

                    tick_data = data.get(
                        "tick"
                    )

                    if not tick_data:
                        continue

                    tick = Tick(
                        epoch=int(
                            tick_data["epoch"]
                        ),
                        price=float(
                            tick_data["quote"]
                        ),
                        symbol=tick_data.get(
                            "symbol",
                            SYMBOL
                        ),
                    )

                    if self.tick_callback:

                        self.tick_callback(
                            tick
                        )

                # --------------------------------------------
                # HISTORICAL DATA
                # --------------------------------------------

                elif msg_type == "history":

                    if self.history_callback:

                        self.history_callback(
                            data
                        )

                # --------------------------------------------
                # ERROR
                # --------------------------------------------

                elif msg_type == "error":

                    print(
                        "\nDeriv error:"
                    )

                    print(
                        json.dumps(
                            data,
                            indent=2
                        )
                    )

            except websocket.WebSocketTimeoutException:

                continue

            except websocket.WebSocketConnectionClosedException:

                print(
                    "\nWebSocket connection closed."
                )

                self.running = False

            except Exception as error:

                print(
                    f"\nWebSocket error: {error}"
                )

                self.running = False

    # --------------------------------------------------------
    # CLOSE
    # --------------------------------------------------------

    def close(self):

        self.running = False

        if self.ws:

            try:
                self.ws.close()
            except Exception:
                pass

            self.ws = None

        print(
            "\nDisconnected."
        )


# ============================================================
# CANDLE BUILDER
# ============================================================

class LiveCandleBuilder:
    """
    Converts ticks into fixed-time OHLC candles.

    Example for 60 seconds:

        10:45:00 -> 10:45:59
        10:46:00 -> 10:46:59
        10:47:00 -> 10:47:59
    """

    def __init__(
        self,
        timeframe_seconds: int,
    ):

        self.timeframe_seconds = (
            timeframe_seconds
        )

        self.current_candle = None

        self.completed_candles = []

    # --------------------------------------------------------
    # GET CANDLE START
    # --------------------------------------------------------

    def candle_start(
        self,
        epoch: int,
    ) -> int:

        return (
            epoch
            // self.timeframe_seconds
        ) * self.timeframe_seconds

    # --------------------------------------------------------
    # PROCESS TICK
    # --------------------------------------------------------

    def process_tick(
        self,
        tick: Tick,
    ):

        start_epoch = self.candle_start(
            tick.epoch
        )

        timestamp = pd.to_datetime(
            start_epoch,
            unit="s",
            utc=True,
        )

        # --------------------------------------------
        # No current candle
        # --------------------------------------------

        if self.current_candle is None:

            self.current_candle = Candle(
                timestamp=timestamp,
                open=tick.price,
                high=tick.price,
                low=tick.price,
                close=tick.price,
                tick_count=1,
            )

            return None

        current_epoch = int(
            self.current_candle.timestamp.timestamp()
        )

        # --------------------------------------------
        # Same candle
        # --------------------------------------------

        if start_epoch == current_epoch:

            self.current_candle.high = max(
                self.current_candle.high,
                tick.price,
            )

            self.current_candle.low = min(
                self.current_candle.low,
                tick.price,
            )

            self.current_candle.close = (
                tick.price
            )

            self.current_candle.tick_count += 1

            return None

        # --------------------------------------------
        # New candle started
        # --------------------------------------------

        completed = self.current_candle

        self.completed_candles.append(
            completed
        )

        self.current_candle = Candle(
            timestamp=timestamp,
            open=tick.price,
            high=tick.price,
            low=tick.price,
            close=tick.price,
            tick_count=1,
        )

        return completed

    # --------------------------------------------------------
    # ADD HISTORICAL CANDLES
    # --------------------------------------------------------

    def load_candles(
        self,
        candles,
    ):

        self.completed_candles = list(
            candles
        )


# ============================================================
# TRUE RANGE
# ============================================================

class TrueRangeCalculator:

    def calculate(
        self,
        candles: pd.DataFrame,
    ) -> pd.Series:

        high = candles["high"]
        low = candles["low"]
        close = candles["close"]

        previous_close = (
            close.shift(1)
        )

        a = high - low

        b = (
            high - previous_close
        ).abs()

        c = (
            low - previous_close
        ).abs()

        tr = pd.concat(
            [a, b, c],
            axis=1,
        ).max(axis=1)

        # First candle
        tr.iloc[0] = (
            high.iloc[0]
            - low.iloc[0]
        )

        return tr


# ============================================================
# ATR
# ============================================================

class ATRCalculator:
    """
    Wilder's RMA.

    Initial:

        ATR = SUM(TR) / N

    Afterwards:

        ATR =
            Previous ATR +
            (Current TR - Previous ATR) / N
    """

    def __init__(
        self,
        period: int,
    ):

        self.period = period

    def calculate(
        self,
        tr: pd.Series,
    ) -> pd.Series:

        values = tr.to_numpy(
            dtype=float
        )

        result = np.full(
            len(values),
            np.nan,
        )

        n = self.period

        if len(values) < n:
            return pd.Series(
                result,
                index=tr.index,
            )

        # Initial ATR
        result[n - 1] = np.mean(
            values[:n]
        )

        # Wilder RMA
        for i in range(
            n,
            len(values)
        ):

            result[i] = (
                result[i - 1]
                +
                (
                    values[i]
                    - result[i - 1]
                )
                / n
            )

        return pd.Series(
            result,
            index=tr.index,
            name="ATR",
        )


# ============================================================
# CHANDELIER EXIT
# ============================================================

class ChandelierExit:

    def __init__(
        self,
        period: int = 22,
        multiplier: float = 3.0,
        use_close: bool = True,
    ):

        self.period = period
        self.multiplier = multiplier
        self.use_close = use_close

    def calculate(
        self,
        candles: pd.DataFrame,
    ) -> pd.DataFrame:

        df = candles.copy()

        if len(df) == 0:
            return df

        # ====================================================
        # TRUE RANGE
        # ====================================================

        tr_calculator = (
            TrueRangeCalculator()
        )

        df["TR"] = (
            tr_calculator.calculate(df)
        )

        # ====================================================
        # ATR
        # ====================================================

        atr_calculator = (
            ATRCalculator(
                self.period
            )
        )

        df["ATR"] = (
            atr_calculator.calculate(
                df["TR"]
            )
        )

        # ====================================================
        # ATR DISTANCE
        # ====================================================

        df["ATR_Distance"] = (
            df["ATR"]
            * self.multiplier
        )

        # ====================================================
        # EXTREMUM
        # ====================================================

        if self.use_close:

            highest_source = (
                df["close"]
            )

            lowest_source = (
                df["close"]
            )

        else:

            highest_source = (
                df["high"]
            )

            lowest_source = (
                df["low"]
            )

        df["Highest"] = (
            highest_source
            .rolling(
                self.period
            )
            .max()
        )

        df["Lowest"] = (
            lowest_source
            .rolling(
                self.period
            )
            .min()
        )

        # ====================================================
        # RAW STOPS
        # ====================================================

        df["LongStopRaw"] = (
            df["Highest"]
            - df["ATR_Distance"]
        )

        df["ShortStopRaw"] = (
            df["Lowest"]
            + df["ATR_Distance"]
        )

        # ====================================================
        # TRAILING STOPS
        # ====================================================

        long_stop = np.full(
            len(df),
            np.nan,
        )

        short_stop = np.full(
            len(df),
            np.nan,
        )

        closes = (
            df["close"]
            .to_numpy(
                dtype=float
            )
        )

        raw_long = (
            df["LongStopRaw"]
            .to_numpy(
                dtype=float
            )
        )

        raw_short = (
            df["ShortStopRaw"]
            .to_numpy(
                dtype=float
            )
        )

        for i in range(len(df)):

            if np.isnan(
                raw_long[i]
            ):

                continue

            if i == 0:

                long_stop[i] = (
                    raw_long[i]
                )

                short_stop[i] = (
                    raw_short[i]
                )

                continue

            previous_long = (
                long_stop[i - 1]
            )

            previous_short = (
                short_stop[i - 1]
            )

            if np.isnan(
                previous_long
            ):

                long_stop[i] = (
                    raw_long[i]
                )

                short_stop[i] = (
                    raw_short[i]
                )

                continue

            # --------------------------------------------
            # LONG STOP
            # --------------------------------------------

            if (
                closes[i - 1]
                > previous_long
            ):

                long_stop[i] = max(
                    raw_long[i],
                    previous_long,
                )

            else:

                long_stop[i] = (
                    raw_long[i]
                )

            # --------------------------------------------
            # SHORT STOP
            # --------------------------------------------

            if (
                closes[i - 1]
                < previous_short
            ):

                short_stop[i] = min(
                    raw_short[i],
                    previous_short,
                )

            else:

                short_stop[i] = (
                    raw_short[i]
                )

        df["LongStop"] = (
            long_stop
        )

        df["ShortStop"] = (
            short_stop
        )

        # ====================================================
        # DIRECTION STATE MACHINE
        # ====================================================

        direction = np.full(
            len(df),
            np.nan,
        )

        current_direction = 1

        for i in range(len(df)):

            if i == 0:

                direction[i] = (
                    current_direction
                )

                continue

            previous_long = (
                long_stop[i - 1]
            )

            previous_short = (
                short_stop[i - 1]
            )

            if (
                np.isnan(
                    previous_long
                )
                or
                np.isnan(
                    previous_short
                )
            ):

                direction[i] = (
                    current_direction
                )

                continue

            # TradingView:
            #
            # close > shortStopPrev ? 1 :
            # close < longStopPrev ? -1 :
            # dir

            if (
                closes[i]
                > previous_short
            ):

                current_direction = 1

            elif (
                closes[i]
                < previous_long
            ):

                current_direction = -1

            direction[i] = (
                current_direction
            )

        df["Direction"] = (
            direction
        )

        # ====================================================
        # SIGNALS
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

        return df


# ============================================================
# LIVE DATA ENGINE
# ============================================================

class LiveChandelierEngine:
    """
    Connects:

        Tick
          ↓
        Candle
          ↓
        Chandelier
    """

    def __init__(
        self,
        timeframe_seconds: int,
        atr_period: int,
        atr_multiplier: float,
        use_close: bool,
    ):

        self.candle_builder = (
            LiveCandleBuilder(
                timeframe_seconds
            )
        )

        self.chandelier = (
            ChandelierExit(
                period=atr_period,
                multiplier=atr_multiplier,
                use_close=use_close,
            )
        )

        self.lock = threading.Lock()

        self.df = pd.DataFrame()

        self.last_tick = None

        self.last_completed_candle = None

        self.current_signal = "NONE"

    # --------------------------------------------------------
    # LOAD HISTORICAL CANDLES
    # --------------------------------------------------------

    def load_history(
        self,
        candles,
    ):

        with self.lock:

            self.candle_builder.load_candles(
                candles
            )

            self.recalculate()

    # --------------------------------------------------------
    # TICK
    # --------------------------------------------------------

    def on_tick(
        self,
        tick: Tick,
    ):

        with self.lock:

            self.last_tick = tick

            completed = (
                self.candle_builder
                .process_tick(tick)
            )

            if completed is not None:

                self.last_completed_candle = (
                    completed
                )

                self.recalculate()

    # --------------------------------------------------------
    # BUILD DATAFRAME
    # --------------------------------------------------------

    def build_dataframe(
        self,
    ) -> pd.DataFrame:

        candles = (
            self.candle_builder
            .completed_candles
        )

        # Add current unfinished candle
        if (
            self.candle_builder
            .current_candle
            is not None
        ):

            candles = (
                candles
                + [
                    self.candle_builder
                    .current_candle
                ]
            )

        if not candles:

            return pd.DataFrame()

        rows = []

        for candle in candles:

            rows.append(
                {
                    "timestamp": candle.timestamp,
                    "open": candle.open,
                    "high": candle.high,
                    "low": candle.low,
                    "close": candle.close,
                    "tick_count": (
                        candle.tick_count
                    ),
                }
            )

        df = pd.DataFrame(
            rows
        )

        df = df.set_index(
            "timestamp"
        )

        return df

    # --------------------------------------------------------
    # RECALCULATE
    # --------------------------------------------------------

    def recalculate(self):

        candles = (
            self.build_dataframe()
        )

        if candles.empty:
            return

        self.df = (
            self.chandelier
            .calculate(candles)
        )

        # --------------------------------------------
        # Detect newest signal
        # --------------------------------------------

        if len(self.df) >= 2:

            latest = self.df.iloc[-1]

            if latest["BuySignal"]:

                self.current_signal = (
                    "BUY"
                )

                print()
                print(
                    "========== BUY =========="
                )

                print(
                    f"Price: "
                    f"{latest['close']:.3f}"
                )

                print(
                    f"Long Stop: "
                    f"{latest['LongStop']:.3f}"
                )

                print(
                    "========================="
                )

            elif latest["SellSignal"]:

                self.current_signal = (
                    "SELL"
                )

                print()
                print(
                    "========= SELL =========="
                )

                print(
                    f"Price: "
                    f"{latest['close']:.3f}"
                )

                print(
                    f"Short Stop: "
                    f"{latest['ShortStop']:.3f}"
                )

                print(
                    "========================"
                )

    # --------------------------------------------------------
    # GET DATA
    # --------------------------------------------------------

    def get_dataframe(self):

        with self.lock:

            return self.df.copy()

    # --------------------------------------------------------
    # GET CURRENT TICK
    # --------------------------------------------------------

    def get_current_tick(self):

        with self.lock:

            return self.last_tick

    # --------------------------------------------------------
    # CURRENT CANDLE
    # --------------------------------------------------------

    def get_current_candle(self):

        with self.lock:

            return (
                self.candle_builder
                .current_candle
            )


# ============================================================
# HISTORICAL DATA CONVERTER
# ============================================================

class HistoryConverter:
    """
    Converts Deriv ticks_history response into candles.
    """

    def __init__(
        self,
        timeframe_seconds: int,
    ):

        self.timeframe_seconds = (
            timeframe_seconds
        )

    def convert(
        self,
        data,
    ):

        history = data.get(
            "history"
        )

        if not history:

            return []

        prices = history.get(
            "prices",
            []
        )

        times = history.get(
            "times",
            []
        )

        if not prices or not times:

            return []

        ticks = []

        for epoch, price in zip(
            times,
            prices
        ):

            ticks.append(
                Tick(
                    epoch=int(epoch),
                    price=float(price),
                    symbol=SYMBOL,
                )
            )

        builder = (
            LiveCandleBuilder(
                self.timeframe_seconds
            )
        )

        for tick in ticks:

            builder.process_tick(
                tick
            )

        return builder.completed_candles


# ============================================================
# LIVE PLOTTER
# ============================================================

class LivePlotter:
    """
    Matplotlib live graph.
    """

    def __init__(
        self,
        engine: LiveChandelierEngine,
        symbol: str,
    ):

        self.engine = engine
        self.symbol = symbol

        self.fig = None
        self.ax = None

    # --------------------------------------------------------
    # CREATE GRAPH
    # --------------------------------------------------------

    def create(self):

        plt.style.use(
            "dark_background"
        )

        self.fig, self.ax = plt.subplots(
            figsize=(15, 8)
        )

        self.fig.canvas.manager.set_window_title(
            "Live Chandelier Exit"
        )

        self.ax.set_title(
            f"{self.symbol} - "
            "Live Chandelier Exit"
        )

        self.ax.set_xlabel(
            "Time"
        )

        self.ax.set_ylabel(
            "Price"
        )

        self.ax.grid(
            True,
            alpha=0.15
        )

        self.fig.tight_layout()

    # --------------------------------------------------------
    # UPDATE
    # --------------------------------------------------------

    def update(
        self,
        frame,
    ):

        df = (
            self.engine
            .get_dataframe()
        )

        if df.empty:

            return

        # --------------------------------------------
        # Last N candles
        # --------------------------------------------

        df = df.tail(
            MAX_CANDLES_ON_GRAPH
        )

        self.ax.clear()

        # --------------------------------------------
        # Close
        # --------------------------------------------

        self.ax.plot(
            df.index,
            df["close"],
            color="white",
            linewidth=1.5,
            label="Price",
        )

        # --------------------------------------------
        # Long Stop
        # --------------------------------------------

        long_stop = (
            df["LongStop"]
            .where(
                df["Direction"] == 1
            )
        )

        self.ax.plot(
            df.index,
            long_stop,
            color="#00ff66",
            linewidth=2.0,
            label="Long Stop",
        )

        # --------------------------------------------
        # Short Stop
        # --------------------------------------------

        short_stop = (
            df["ShortStop"]
            .where(
                df["Direction"] == -1
            )
        )

        self.ax.plot(
            df.index,
            short_stop,
            color="#ff3355",
            linewidth=2.0,
            label="Short Stop",
        )

        # --------------------------------------------
        # BUY
        # --------------------------------------------

        buys = df[
            df["BuySignal"]
        ]

        if not buys.empty:

            self.ax.scatter(
                buys.index,
                buys["LongStop"],
                color="#00ff66",
                marker="^",
                s=120,
                zorder=10,
                label="BUY",
            )

        # --------------------------------------------
        # SELL
        # --------------------------------------------

        sells = df[
            df["SellSignal"]
        ]

        if not sells.empty:

            self.ax.scatter(
                sells.index,
                sells["ShortStop"],
                color="#ff3355",
                marker="v",
                s=120,
                zorder=10,
                label="SELL",
            )

        # --------------------------------------------
        # Current tick
        # --------------------------------------------

        tick = (
            self.engine
            .get_current_tick()
        )

        if tick:

            current_price = (
                tick.price
            )

            self.ax.axhline(
                current_price,
                color="#00bfff",
                linestyle="--",
                linewidth=1,
                alpha=0.7,
            )

            # Current price label
            self.ax.text(
                0.99,
                0.95,
                f"PRICE  {current_price:.3f}",
                transform=self.ax.transAxes,
                ha="right",
                va="top",
                fontsize=13,
                color="#00bfff",
                fontweight="bold",
            )

        # --------------------------------------------
        # Latest calculation
        # --------------------------------------------

        latest = df.iloc[-1]

        direction = latest.get(
            "Direction"
        )

        atr = latest.get(
            "ATR"
        )

        long_value = latest.get(
            "LongStop"
        )

        short_value = latest.get(
            "ShortStop"
        )

        # --------------------------------------------
        # Direction text
        # --------------------------------------------

        if direction == 1:

            direction_text = (
                "LONG / BULLISH"
            )

            direction_color = (
                "#00ff66"
            )

        elif direction == -1:

            direction_text = (
                "SHORT / BEARISH"
            )

            direction_color = (
                "#ff3355"
            )

        else:

            direction_text = "WAIT"

            direction_color = "white"

        # --------------------------------------------
        # Information panel
        # --------------------------------------------

        info = (
            f"SYMBOL     : {self.symbol}\n"
            f"DIRECTION  : {direction_text}\n"
            f"ATR        : "
            f"{atr:.4f}\n"
            f"LONG STOP  : "
            f"{long_value:.4f}\n"
            f"SHORT STOP : "
            f"{short_value:.4f}\n"
            f"TIMEFRAME  : "
            f"{TIMEFRAME_SECONDS}s\n"
            f"ATR PERIOD : "
            f"{ATR_PERIOD}\n"
            f"MULTIPLIER : "
            f"{ATR_MULTIPLIER}"
        )

        self.ax.text(
            0.02,
            0.97,
            info,
            transform=self.ax.transAxes,
            ha="left",
            va="top",
            fontsize=10,
            color=direction_color,
            family="monospace",
            bbox={
                "boxstyle": "round",
                "facecolor": "#111111",
                "alpha": 0.85,
                "edgecolor": direction_color,
            },
        )

        # --------------------------------------------
        # Title
        # --------------------------------------------

        current_time = datetime.now(
            timezone.utc
        ).strftime(
            "%H:%M:%S UTC"
        )

        self.ax.set_title(
            f"{self.symbol} | "
            f"LIVE CHANDELIER EXIT | "
            f"{current_time}",
            fontsize=15,
            fontweight="bold",
        )

        self.ax.set_xlabel(
            "Candle Time"
        )

        self.ax.set_ylabel(
            "Price"
        )

        self.ax.grid(
            True,
            alpha=0.15
        )

        self.ax.legend(
            loc="upper left"
        )

        self.ax.xaxis.set_major_formatter(
            mdates.DateFormatter(
                "%H:%M:%S"
            )
        )

        self.fig.autofmt_xdate()

        self.fig.tight_layout()


# ============================================================
# APPLICATION
# ============================================================

class ChandelierLiveApplication:

    def __init__(self):

        self.client = DerivClient(
            app_id=APP_ID,
            auth_token=AUTH_TOKEN,
            account_id=ACCOUNT_ID,
        )

        self.engine = (
            LiveChandelierEngine(
                timeframe_seconds=(
                    TIMEFRAME_SECONDS
                ),
                atr_period=(
                    ATR_PERIOD
                ),
                atr_multiplier=(
                    ATR_MULTIPLIER
                ),
                use_close=(
                    USE_CLOSE
                ),
            )
        )

        self.history_converter = (
            HistoryConverter(
                TIMEFRAME_SECONDS
            )
        )

        self.plotter = (
            LivePlotter(
                self.engine,
                SYMBOL,
            )
        )

        self.receiver_thread = None

    # --------------------------------------------------------
    # LIVE TICK
    # --------------------------------------------------------

    def on_tick(
        self,
        tick: Tick,
    ):

        self.engine.on_tick(
            tick
        )

        # --------------------------------------------
        # Terminal live display
        # --------------------------------------------

        candle = (
            self.engine
            .get_current_candle()
        )

        if candle:

            now = datetime.fromtimestamp(
                tick.epoch,
                tz=timezone.utc,
            )

            print(
                f"\r"
                f"{now.strftime('%H:%M:%S')} "
                f"{SYMBOL} "
                f"PRICE={tick.price:.3f} "
                f"CANDLE="
                f"O:{candle.open:.3f} "
                f"H:{candle.high:.3f} "
                f"L:{candle.low:.3f} "
                f"C:{candle.close:.3f} "
                f"TICKS:{candle.tick_count}",
                end="",
                flush=True,
            )

    # --------------------------------------------------------
    # HISTORY
    # --------------------------------------------------------

    def on_history(
        self,
        data,
    ):

        try:

            candles = (
                self.history_converter
                .convert(data)
            )

            if candles:

                print(
                    f"\nHistorical candles: "
                    f"{len(candles)}"
                )

                self.engine.load_history(
                    candles
                )

            else:

                print(
                    "\nNo historical candles."
                )

        except Exception as error:

            print(
                f"\nHistory error: {error}"
            )

    # --------------------------------------------------------
    # START
    # --------------------------------------------------------

    def start(self):

        print()
        print("=" * 75)
        print(
            "LIVE CHANDELIER EXIT MONITOR"
        )
        print("=" * 75)

        print(
            f"Symbol          : {SYMBOL}"
        )

        print(
            f"Timeframe       : "
            f"{TIMEFRAME_SECONDS} seconds"
        )

        print(
            f"ATR Period      : "
            f"{ATR_PERIOD}"
        )

        print(
            f"ATR Multiplier  : "
            f"{ATR_MULTIPLIER}"
        )

        print(
            f"Use Close       : "
            f"{USE_CLOSE}"
        )

        print("=" * 75)

        # ----------------------------------------------------
        # Connect
        # ----------------------------------------------------

        self.client.set_tick_callback(
            self.on_tick
        )

        self.client.set_history_callback(
            self.on_history
        )

        self.client.connect()

        # ----------------------------------------------------
        # Historical warm-up
        # ----------------------------------------------------

        self.client.request_history(
            SYMBOL,
            HISTORY_TICKS,
        )

        # ----------------------------------------------------
        # Subscribe live
        # ----------------------------------------------------

        self.client.subscribe_ticks(
            SYMBOL
        )

        # ----------------------------------------------------
        # Receiver thread
        # ----------------------------------------------------

        self.receiver_thread = (
            threading.Thread(
                target=(
                    self.client
                    .receive_loop
                ),
                daemon=True,
            )
        )

        self.receiver_thread.start()

        print()
        print(
            "Live monitor running..."
        )

        print(
            "Press Ctrl+C to stop."
        )

        # ----------------------------------------------------
        # Plot
        # ----------------------------------------------------

        self.plotter.create()

        animation = FuncAnimation(
            self.plotter.fig,
            self.plotter.update,
            interval=GRAPH_UPDATE_MS,
            cache_frame_data=False,
        )

        # Keep reference alive
        self.animation = animation

        try:

            plt.show()

        except KeyboardInterrupt:

            pass

        finally:

            self.stop()

    # --------------------------------------------------------
    # STOP
    # --------------------------------------------------------

    def stop(self):

        print(
            "\nStopping..."
        )

        self.client.close()


# ============================================================
# MAIN
# ============================================================

def main():

    if (
        APP_ID == "YOUR_APP_ID"
        or
        AUTH_TOKEN == "YOUR_AUTH_TOKEN"
        or
        ACCOUNT_ID == "YOUR_ACCOUNT_ID"
    ):

        print()
        print(
            "ERROR: Configure your Deriv credentials."
        )

        print()
        print(
            "Recommended:"
        )

        print(
            "export DERIV_APP_ID='your_app_id'"
        )

        print(
            "export DERIV_AUTH_TOKEN='your_token'"
        )

        print(
            "export DERIV_ACCOUNT_ID='your_account_id'"
        )

        return

    application = (
        ChandelierLiveApplication()
    )

    try:

        application.start()

    except KeyboardInterrupt:

        print(
            "\nStopped by user."
        )

        application.stop()

    except Exception as error:

        print(
            f"\nFatal error: {error}"
        )

        application.stop()


if __name__ == "__main__":

    main()