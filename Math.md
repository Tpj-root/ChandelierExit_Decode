**True Range → ATR → Highest/Lowest → ATR multiplier → trailing stops → direction state.**

If you understand those five pieces, you can build your own function without copying the TradingView code.


---

# 1. First remove all the visual/alert code

The TradingView script looks large, but the **mathematical core is actually small**.

Ignore these for now:

```text
plot()
plotshape()
fill()
color
alertcondition()
showLabels
highlightState
awaitBarConfirmation
```

They are UI/alert functionality.

The important mathematical section is:

```text
length
mult
useClose

atr = mult × ATR(length)

longStop
longStopPrev
longStop trailing rule

shortStop
shortStopPrev
shortStop trailing rule

dir
```

So our learning target is:

```text
OHLC candles
     ↓
True Range
     ↓
ATR
     ↓
ATR × Multiplier
     ↓
Highest / Lowest
     ↓
Long Stop / Short Stop
     ↓
Trailing logic
     ↓
Direction
     ↓
Buy / Sell
```

---

# 2. The three inputs

The original code has:

```pine
length = 22
mult = 3.0
useClose = true
```

### `length`

Number of candles used for the calculation.

```text
length = 22
```

means:

> Look at the latest 22 candles.

It is used for both:

* ATR
* highest/lowest calculation

---

### `mult`

ATR multiplier:

```text
mult = 3.0
```

Meaning:

```text
ATR × 3
```

The larger the multiplier, the farther the stop is from price.

For example:

```text
ATR = 10

ATR × 2 = 20
ATR × 3 = 30
ATR × 4 = 40
```

---

### `useClose`

This changes what "extreme" means.

If:

```text
useClose = true
```

then:

```text
highest = highest CLOSE
lowest  = lowest CLOSE
```

If:

```text
useClose = false
```

then:

```text
highest = highest HIGH
lowest  = lowest LOW
```

This is an important detail.

---

# 3. First mathematical building block: True Range

Before calculating ATR, we need **True Range (TR)**.

For a candle:

```text
High
Low
Close
Previous Close
```

True Range is:

$$
TR = \max
\begin{cases}
High-Low \\
|High-PreviousClose| \\
|Low-PreviousClose|
\end{cases}
$$

In simple words:

> TR measures the effective price movement of one candle, including gaps from the previous close.

---

## Example

Suppose:

```text
Previous Close = 100
High           = 110
Low            = 95
```

Calculate:

```text
High - Low
= 110 - 95
= 15
```

Next:

```text
|High - Previous Close|
= |110 - 100|
= 10
```

Next:

```text
|Low - Previous Close|
= |95 - 100|
= 5
```

Therefore:

```text
TR = max(15, 10, 5)

TR = 15
```

---

# 4. Why does ATR exist?

ATR means:

> **Average True Range**

It tells us approximately how much the market has been moving.

If:

```text
ATR = 2
```

the market has relatively small movement.

If:

```text
ATR = 20
```

the market has much larger movement.

Chandelier Exit uses this volatility measurement to place the stop.

---

# 5. ATR mathematics

TradingView's:

```pine
ta.atr(length)
```

is based on:

```text
True Range
+
Wilder's moving average (RMA)
```

Conceptually:

### Initial ATR

For the first complete `length` observations:

$$
ATR = \frac{TR_1+TR_2+\cdots+TR_n}{n}
$$

Then subsequent ATR values use Wilder smoothing:

$$
ATR_t =
\frac{ATR_{t-1}(n-1)+TR_t}{n}
$$

or equivalently:

$$
ATR_t =
ATR_{t-1}+\frac{TR_t-ATR_{t-1}}{n}
$$

That second form is especially useful for implementing your own function.

---

# 6. Now the important Chandelier calculation

TradingView does:

```pine
atr = mult * ta.atr(length)
```

Don't mentally call this just "ATR".

It is actually:

$$
D = ATR \times Multiplier
$$

Let's call it:

```text
distance
```

For example:

```text
ATR = 7

Multiplier = 3

Distance = 7 × 3
         = 21
```

This `21` is the distance used to place the stop.

---

# 7. Long Stop

The code:

```pine
longStop =
    highest(close, length) - atr
```

Remember that `atr` already means:

```text
ATR × multiplier
```

So mathematically:

$$
LongStop_{raw}
=
HighestClose_n-(ATR_n\times Multiplier)
$$

For the default settings:

$$
LongStop_{raw}
=
HighestClose_{22}-(ATR_{22}\times3)
$$

This means:

> Find the highest price in the lookback window, then move downward by 3 ATR.

---

# 8. Short Stop

The code:

```pine
shortStop =
    lowest(close, length) + atr
```

Therefore:

$$
ShortStop_{raw}
=
LowestClose_n+(ATR_n\times Multiplier)
$$

With defaults:

$$
ShortStop_{raw}
=
LowestClose_{22}+(ATR_{22}\times3)
$$

Meaning:

> Find the lowest price and move upward by 3 ATR.

---

# 9. Visualize the idea

Imagine price moving upward:

```text
Price
  |
120|                 Price
   |                /
110|              /
   |            /
100|          /
   |        /
 90|------ Long Stop
   |
```

The long stop sits below the market.

For a short trend:

```text
Price
  |
120|------ Short Stop
   |       \
110|        \
   |         \
100|          \
   |           \
 90|            Price
```

The short stop sits above the market.

---

# 10. But there is an important second calculation

This is where Chandelier Exit becomes a **trailing stop**.

Look at:

```pine
longStopPrev = nz(longStop[1], longStop)
```

`[1]` means:

> Previous candle's value.

So:

```text
longStop[1]
```

means:

```text
previous Long Stop
```

Then:

```pine
longStop :=
    close[1] > longStopPrev
    ? math.max(longStop, longStopPrev)
    : longStop
```

This is extremely important.

It says:

```text
IF previous close > previous long stop

    new long stop =
        MAX(current calculated stop,
            previous long stop)

ELSE

    new long stop =
        current calculated stop
```

---

# 11. Why MAX?

Suppose:

```text
Previous Long Stop = 86
Current calculated Long Stop = 83
```

And previous close is above the previous stop.

Then:

```text
max(83, 86)
= 86
```

The stop **doesn't move backward**.

It stays at:

```text
86
```

That's the trailing behavior.

If instead:

```text
Previous Long Stop = 86
Current calculated Long Stop = 90
```

then:

```text
max(90, 86)
= 90
```

So the stop moves upward.

Therefore, during the long state:

```text
Long Stop can move UP
or remain the same

but should not move DOWN
```

That is one of the most important things to understand.

---

# 12. Short stop does the opposite

The code:

```pine
shortStop :=
    close[1] < shortStopPrev
    ? math.min(shortStop, shortStopPrev)
    : shortStop
```

If previous close is below previous short stop:

```text
new short stop =
    MIN(current short stop,
        previous short stop)
```

Therefore, during the short state:

```text
Short Stop can move DOWN
or remain the same

but should not move UP
```

So:

```text
LONG:
    MAX()

SHORT:
    MIN()
```

Very important.

---

# 13. Direction calculation

Now we have the stops.

TradingView:

```pine
var int dir = 1

dir :=
    close > shortStopPrev ? 1 :
    close < longStopPrev ? -1 :
    dir
```

There are three possibilities.

### Condition 1

```text
Close > Previous Short Stop
```

Then:

```text
dir = +1
```

Meaning:

```text
LONG / bullish state
```

---

### Condition 2

```text
Close < Previous Long Stop
```

Then:

```text
dir = -1
```

Meaning:

```text
SHORT / bearish state
```

---

### Condition 3

Neither condition happens.

Then:

```text
dir = dir
```

Meaning:

> Keep the previous direction.

This is a **state machine**.

---

# 14. Chandelier Exit is actually a state machine

This is a beautiful thing to recognize.

It isn't simply:

```text
price > something → BUY
price < something → SELL
```

It has memory.

```text
Previous Direction
        ↓
Previous Stops
        ↓
Current Price
        ↓
New Direction
        ↓
New State
```

The variable:

```pine
var int dir = 1
```

stores state between candles.

You can think:

```text
+1 = LONG STATE
-1 = SHORT STATE
```

---

# 15. Buy signal

TradingView:

```pine
buySignal = dir == 1 and dir[1] == -1
```

Mathematically:

```text
Current direction = +1
AND
Previous direction = -1
```

Therefore:

```text
-1 → +1
```

is a BUY signal.

---

# 16. Sell signal

```pine
sellSignal = dir == -1 and dir[1] == 1
```

Therefore:

```text
+1 → -1
```

is a SELL signal.

---

# 17. Now let's solve one complete example by hand

Let's deliberately use:

```text
length = 3
multiplier = 3
useClose = true
```

I am using `3` instead of `22` only because calculating 22 candles by hand would be unnecessarily large.

The **algorithm is exactly the same**.

---

## Candle data

We'll use:

| Candle | High | Low | Close |
| -----: | ---: | --: | ----: |
|      1 |  105 |  98 |   103 |
|      2 |  108 | 101 |   106 |
|      3 |  110 | 104 |   105 |
|      4 |  112 | 103 |   109 |
|      5 |   85 |  78 |    80 |

We'll calculate candles 1 → 5.

---

# 18. Candle 1 — True Range

No previous close exists, so use:

$$
TR_1=High-Low
$$

Therefore:

$$
TR_1=105-98=7
$$

```text
TR1 = 7
```

---

# 19. Candle 2 — True Range

Previous close:

```text
103
```

Current:

```text
High = 108
Low  = 101
```

Calculate:

```text
High - Low
= 108 - 101
= 7
```

```text
|High - Previous Close|
= |108 - 103|
= 5
```

```text
|Low - Previous Close|
= |101 - 103|
= 2
```

Therefore:

$$
TR_2=max(7,5,2)
$$

```text
TR2 = 7
```

---

# 20. Candle 3 — True Range

Previous close:

```text
106
```

Current:

```text
High = 110
Low  = 104
```

Calculate:

```text
110 - 104 = 6

|110 - 106| = 4

|104 - 106| = 2
```

Therefore:

```text
TR3 = max(6,4,2)

TR3 = 6
```

---

# 21. First ATR

Our length is:

```text
3
```

So after three TR values:

```text
TR1 = 7
TR2 = 7
TR3 = 6
```

Initial ATR:

$$
ATR_3=\frac{7+7+6}{3}
$$

$$
ATR_3=\frac{20}{3}
$$

$$
ATR_3=6.6667
$$

So:

```text
ATR3 = 6.6667
```

---

# 22. Apply multiplier

Multiplier:

```text
3
```

Therefore:

$$
Distance=6.6667\times3
$$

$$
Distance=20
$$

So:

```text
ATR distance = 20
```

---

# 23. Candle 3 Long Stop

`useClose = true`.

Look at the last 3 closes:

```text
103
106
105
```

Highest:

```text
106
```

Therefore:

$$
LongStopRaw=106-20
$$

```text
LongStopRaw = 86
```

---

# 24. Candle 3 Short Stop

Lowest close:

```text
min(103,106,105)
= 103
```

Therefore:

$$
ShortStopRaw=103+20
$$

```text
ShortStopRaw = 123
```

So at candle 3:

```text
Long Stop  = 86
Short Stop = 123
```

And initially:

```text
dir = +1
```

---

# 25. Candle 4 — calculate TR

Candle 4:

```text
High = 112
Low  = 103
Close = 109

Previous Close = 105
```

Calculate:

```text
112 - 103 = 9

|112 - 105| = 7

|103 - 105| = 2
```

Therefore:

$$
TR_4=max(9,7,2)
$$

```text
TR4 = 9
```

---

# 26. Candle 4 — ATR

We use Wilder's RMA:

$$
ATR_4=
\frac{ATR_3(3-1)+TR_4}{3}
$$

Substitute:

$$
ATR_4=
\frac{6.6667\times2+9}{3}
$$

$$
ATR_4=
\frac{13.3334+9}{3}
$$

$$
ATR_4=
\frac{22.3334}{3}
$$

$$
ATR_4\approx7.4445
$$

So:

```text
ATR4 ≈ 7.4444
```

---

# 27. Apply multiplier

$$
7.4444\times3
$$

```text
Distance ≈ 22.3333
```

---

# 28. Candle 4 raw Long Stop

Last 3 closes:

```text
Candle 2 = 106
Candle 3 = 105
Candle 4 = 109
```

Highest:

```text
109
```

Therefore:

$$
LongStopRaw=109-22.3333
$$

$$
LongStopRaw=86.6667
$$

---

# 29. Now the trailing logic

Previous long stop:

```text
86
```

Previous close:

```text
105
```

Condition:

```text
105 > 86
```

TRUE.

Therefore:

$$
LongStop=max(86.6667,86)
$$

Result:

```text
LongStop = 86.6667
```

Excellent.

The stop moved:

```text
86
 ↓
86.6667
```

It moved upward.

---

# 30. Candle 4 Short Stop

Last 3 closes:

```text
106
105
109
```

Lowest:

```text
105
```

Therefore:

$$
ShortStopRaw=105+22.3333
$$

$$
ShortStopRaw=127.3333
$$

Previous short stop:

```text
123
```

Previous close:

```text
105
```

Condition:

```text
105 < 123
```

TRUE.

Therefore:

$$
ShortStop=min(127.3333,123)
$$

Result:

```text
ShortStop = 123
```

Notice:

```text
123
↓
123
```

It did not move upward.

That's the trailing logic.

---

# 31. Candle 4 — Direction

Previous short stop:

```text
123
```

Current close:

```text
109
```

Check:

```text
109 > 123 ?
```

NO.

Then:

```text
109 < previous long stop 86 ?
```

NO.

Therefore:

```text
dir = previous dir
```

Previous direction:

```text
+1
```

So:

```text
dir = +1
```

Still LONG.

---

# 32. Now candle 5 — dramatic movement

Candle 5:

```text
High = 85
Low  = 78
Close = 80

Previous Close = 109
```

TR:

```text
85 - 78 = 7

|85 - 109| = 24

|78 - 109| = 31
```

Therefore:

$$
TR_5=max(7,24,31)
$$

```text
TR5 = 31
```

This is a very important example.

Why is TR 31 instead of 7?

Because price moved far away from the previous close.

---

# 33. Candle 5 ATR

Previous ATR:

```text
7.4444
```

Current TR:

```text
31
```

Using Wilder smoothing:

$$
ATR_5=
\frac{7.4444\times2+31}{3}
$$

$$
ATR_5=
\frac{14.8888+31}{3}
$$

$$
ATR_5=
\frac{45.8888}{3}
$$

$$
ATR_5\approx15.2963
$$

So:

```text
ATR5 ≈ 15.2963
```

---

# 34. Multiplier

$$
15.2963\times3
$$

```text
Distance ≈ 45.8889
```

---

# 35. Candle 5 Long Stop

Last 3 closes:

```text
105
109
80
```

Highest:

```text
109
```

Therefore:

$$
LongStopRaw=109-45.8889
$$

$$
LongStopRaw=63.1111
$$

Now previous long stop:

```text
86.6667
```

Previous close:

```text
109
```

Check:

```text
109 > 86.6667
```

TRUE.

Therefore:

$$
LongStop=max(63.1111,86.6667)
$$

Result:

```text
LongStop = 86.6667
```

This is VERY important.

The raw calculation wanted to move the stop down:

```text
86.6667 → 63.1111
```

But the trailing logic prevented that.

The actual stop remains:

```text
86.6667
```

---

# 36. Candle 5 Short Stop

Last 3 closes:

```text
105
109
80
```

Lowest:

```text
80
```

Therefore:

$$
ShortStopRaw=80+45.8889
$$

$$
ShortStopRaw=125.8889
$$

Previous short stop:

```text
123
```

Previous close:

```text
109
```

Check:

```text
109 < 123
```

TRUE.

Therefore:

$$
ShortStop=min(125.8889,123)
$$

Result:

```text
ShortStop = 123
```

---

# 37. Now the important direction calculation

Current close:

```text
80
```

Previous long stop:

```text
86.6667
```

Check:

```text
80 < 86.6667
```

TRUE.

Therefore:

```text
dir = -1
```

Direction changed:

```text
Previous = +1
Current  = -1
```

Therefore:

```text
SELL SIGNAL
```

because:

$$
+1\rightarrow-1
$$

---

# 38. Our complete hand calculation

The important result is:

| Candle | TR |     ATR | Long Stop | Short Stop | Direction |
| -----: | -: | ------: | --------: | ---------: | --------: |
|      1 |  7 |       — |         — |          — |        +1 |
|      2 |  7 |       — |         — |          — |        +1 |
|      3 |  6 |  6.6667 |   86.0000 |   123.0000 |        +1 |
|      4 |  9 |  7.4444 |   86.6667 |   123.0000 |        +1 |
|      5 | 31 | 15.2963 |   86.6667 |   123.0000 |    **-1** |

At candle 5:

```text
Close = 80

Previous Long Stop = 86.6667

80 < 86.6667

        ↓

Direction = -1

        ↓

+1 → -1

        ↓

SELL
```

---

# 39. The whole mathematical algorithm

Now we can reduce the entire TradingView indicator to this:

### Step 1 — True Range

$$
TR_t =
max(
H_t-L_t,
|H_t-C_{t-1}|,
|L_t-C_{t-1}|
)
$$

### Step 2 — ATR

Initial:

$$
ATR=\frac{\sum TR}{n}
$$

After that:

$$
ATR_t=
ATR_{t-1}+
\frac{TR_t-ATR_{t-1}}{n}
$$

### Step 3 — Distance

$$
D_t=ATR_t\times M
$$

### Step 4 — Raw Long Stop

With `useClose=true`:

$$
L_t=
Highest(C,n)-D_t
$$

With `useClose=false`:

$$
L_t=
Highest(H,n)-D_t
$$

### Step 5 — Trail Long Stop

$$
L_t=
\begin{cases}
max(L_t,L_{t-1}) & C_{t-1}>L_{t-1}\\
L_t & otherwise
\end{cases}
$$

### Step 6 — Raw Short Stop

With `useClose=true`:

$$
S_t=
Lowest(C,n)+D_t
$$

With `useClose=false`:

$$
S_t=
Lowest(L,n)+D_t
$$

### Step 7 — Trail Short Stop

First calculate the raw short stop:

$$
S_t^{raw} = L_t + ATR_t \times M
$$

Then trail the short stop:

$$
S_t =
\begin{cases}
\min(S_t^{raw}, S_{t-1}) & \text{if } C_{t-1} < S_{t-1} \\
S_t^{raw} & \text{otherwise}
\end{cases}
$$

### Step 8 — Direction

$$
Direction_t =
\begin{cases}
+1 & \text{if } C_t > S_{t-1} \\
-1 & \text{if } C_t < L_{t-1} \\
Direction_{t-1} & \text{otherwise}
\end{cases}
$$


### Step 9 — Signals

BUY:

$$
Direction_{t-1}=-1
\land
Direction_t=+1
$$

SELL:

$$
Direction_{t-1}=+1
\land
Direction_t=-1
$$

---

# 40. Your own function should NOT start with one giant function

Since your goal is **"I want to solve it in my hands"**, I strongly recommend you build it as small mathematical functions.

Think:

```text
ChandelierExit
│
├── true_range()
│
├── atr()
│
├── highest()
│
├── lowest()
│
├── calculate_long_stop()
│
├── calculate_short_stop()
│
├── update_direction()
│
└── generate_signal()
```

This is much better than asking AI:

> "Convert this entire Pine Script into C++."

That would give you code, but you would not necessarily understand the algorithm.

Instead, you can build it one mathematical piece at a time.

---

# 41. The most important learning exercise

Before writing your C++ function, make a spreadsheet or notebook with:

```text
Candle
High
Low
Close
Previous Close
TR
ATR
Highest Close
Lowest Close
ATR × Mult
Raw Long
Final Long
Raw Short
Final Short
Previous Long
Previous Short
Direction
Signal
```

Then manually calculate **10–20 candles**.

For example:

```text
                 Candle
                   ↓
          ┌─────────────────┐
          │ H   L   C       │
          └────────┬────────┘
                   ↓
                 TR
                   ↓
                 ATR
                   ↓
              ATR × 3
             ↙         ↘
       Highest          Lowest
          ↓                ↓
    Long Stop         Short Stop
          ↓                ↓
       MAX()             MIN()
          ↘                ↙
             Direction
                 ↓
             BUY/SELL
```

Once you can calculate this manually, **your C++ implementation becomes almost mechanical**.

---

## One very important distinction

There are actually **three different things** in this indicator that are easy to confuse:

```text
1. Raw Long Stop
       ↓
2. Trailing/Final Long Stop
       ↓
3. Direction
```

For example, in our candle 5:

```text
Raw Long Stop
= 63.1111

Final Long Stop
= 86.6667

Direction
= -1
```

Those are **not the same number or concept**.
Understanding this distinction is the key to understanding the TradingView code.

