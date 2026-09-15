# ChandelierExit_Decode



## 🔎 Information Gathering

Before writing any code, the first step is to understand **how Chandelier Exit actually works**.

> **Goal:** Go from **Zero → Understanding → Mathematics → Implementation → Hero**.

### 1. Start With the Original Source

The first reference is the original Chandelier Exit implementation by **everget** on TradingView.

* **First version:** March 7, 2019
* **Current source:** Updated July 28, 2025

TradingView source:
[https://www.tradingview.com/script/AqXxNS7j-Chandelier-Exit-everget/](https://www.tradingview.com/script/AqXxNS7j-Chandelier-Exit-everget/)

### 2. Collect Only a Few Sources

There may be hundreds of articles, videos, indicators, and implementations available online.

**Don't collect everything.**

For the initial research, choose only **3–5 strong sources**.

For example:

1. Original TradingView source
2. One alternative implementation
3. One reliable explanation of the mathematics
4. One reference for ATR
5. One reference for practical trading interpretation

Another useful implementation is:

**Advanced Chandelier Exit with S/R [Alpha Extract]**

[https://www.tradingview.com/script/9X7UPWIx-Advanced-Chandelier-Exit-with-S-R-Alpha-Extract/](https://www.tradingview.com/script/9X7UPWIx-Advanced-Chandelier-Exit-with-S-R-Alpha-Extract/)

* Published: October 10, 2025

### 3. Why Limit the Sources?

Too much information can create an **information loop**:

```text
More Sources
     ↓
More Information
     ↓
More Questions
     ↓
Search for More Sources
     ↓
More Information
     ↓
Repeat...
```

At some point, collecting information stops being research and becomes a distraction.

So the rule for this project is:

> **Collect enough information to understand the subject — not enough information to become stuck researching it.**

### 4. What Do We Need to Discover?

Before implementing Chandelier Exit, we only need to answer a few fundamental questions:

```text
What is Chandelier Exit?
        ↓
What inputs does it use?
        ↓
What mathematical formulas does it use?
        ↓
What is ATR?
        ↓
How is Highest High / Lowest Low calculated?
        ↓
How does the ATR multiplier affect the result?
        ↓
How are Long and Short levels calculated?
        ↓
When does the trend direction change?
        ↓
How does the calculation move from candle to candle?
```

Once these questions are understood, **stop gathering information and start calculating.**

### 5. Research Principle

> **Information Gathering ≠ Information Collecting**

The purpose of research is not to collect the maximum amount of information.

The purpose is to collect the **minimum useful information required to build a correct mental model**.

For this Chandelier Exit study:

**3–5 good sources → understand the formulas → calculate by hand → verify against TradingView → implement in code.**






### InformationGathering_URL

```
Sourcecode is
https://www.tradingview.com/script/AqXxNS7j-Chandelier-Exit-everget/
Updated Jul 28, 2025

Advanced Chandelier Exit with S/R [Alpha Extract]
https://www.tradingview.com/script/9X7UPWIx-Advanced-Chandelier-Exit-with-S-R-Alpha-Extract/
Oct 10, 2025



### WEBPAGE

https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-overlays/chandelier-exit
https://corporatefinanceinstitute.com/resources/equities/chandelier-exit/
https://github.com/WoolenWang/fmz_strategies/blob/master/Chandelier-Exit.md


### API
https://github.com/QuantGeekDev/StockWolf-Chandelier-Exit/

### VIDEO
https://www.youtube.com/watch?v=mWSX8yxMQMw&t=37


### CODE
https://github.com/NJiHin/TA_Chandelier
https://github.com/Wendigooor/tradingview_scripts/blob/main/Chandelier_Exit
https://github.com/WoolenWang/fmz_strategies/blob/master/Chandelier-Exit.md
https://github.com/hasnocool/tradingview-pine-scripts/tree/main
https://gist.github.com/jericbas/115662754636d6401a7589776bf2a84e
https://github.com/botradingblog1/python-algorithmic-trading/blob/main/strategies/Crypto%20Chandelier%20Exit.ipynb
https://github.com/SSonagi/Chandelier-Exit-Python

### EXTRA
https://rdrr.io/github/pverspeelt/Quantfunctions/man/chandelier.html
https://rdrr.io/github/pverspeelt/Quantfunctions/src/R/protective_stops.R
https://doc.stocksharp.com/en/api-examples/0614_Chandelier_Exit_With_200_EMA_Filter

```




