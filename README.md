\# Interest Rate Risk in the Banking Book (IRRBB) Model Validation



\*\*Objective:\*\*  

An independent quantitative validation of a bank's Asset-Liability Management (ALM) framework. This project models the impact of stochastic interest rate shocks on a duration-mismatched balance sheet, calculating both the transient shock to Net Interest Income (NII) and the long-term destruction of the Economic Value of Equity (EVE).



> \*\*🔗 \[Read the full Model Validation Document (PDF)](docs/IRRBB-MVD.pdf)\*\*



\## 📊 Project Overview



This repository evaluates interest rate risk using numerical methods and stochastic differential equations (SDEs). It bridges theoretical rate simulations with concrete balance-sheet dollar impacts, complying with regulatory requirements for stress-testing interest rate sensitivity (+200 bps shocks).



\*\*Core Technologies:\*\* `Python 3.10` | `numpy` | `pandas` | `matplotlib` | `scipy`



\## 🧠 Methodology



1\.  \*\*Stochastic Rate Simulation (The Vasicek Model):\*\* 

&#x20;   \*   Modeled the yield curve using the Vasicek mean-reverting stochastic differential equation:  

&#x20;       $dr\_t = a(b - r\_t)dt + \\sigma dW\_t$

&#x20;   \*   Solved the SDE using an Euler-Maruyama numerical scheme to generate 1,000 Monte Carlo forward-rate paths. (Note: This mathematical framework mirrors the Ornstein-Uhlenbeck process used to model physical state changes in closed thermodynamic systems).

2\.  \*\*Transient Risk (NII):\*\* 

&#x20;   \*   Pushed the 1,000 simulated rate paths through a mock balance sheet ($100M fixed assets, $80M floating liabilities).

&#x20;   \*   Calculated the 12-month Value at Risk (VaR) at the 99th percentile for Net Interest Income.

3\.  \*\*Steady-State Risk (EVE):\*\* 

&#x20;   \*   Applied a regulatory +200 bps parallel shock to the yield curve.

&#x20;   \*   Calculated the exact Net Present Value (NPV) of all future asset and liability cash flows to quantify the structural equity destruction caused by duration mismatch.



\## 🔍 Key Validation Findings



The formal validation audit identified several critical model limitations that require governance overlays:

\*   \*\*Convexity Limitations in EVE:\*\* Simple duration-based models assume a linear price-yield relationship. By calculating exact discounted cash flows, the validation proved that massive rate shocks (+400 bps) introduce convexity errors, causing standard linear models to understate equity destruction.

\*   \*\*Deposit Beta Absence:\*\* The baseline NII model assumes a 1.0 correlation between market rates and liability repricing. In reality, retail deposit betas are historically sluggish (\~0.4 to 0.6). Without a deposit beta assumption, the model over-predicts NII margin compression in rising-rate environments.

\*   \*\*Boundary Conditions:\*\* The Vasicek simulation allows for negative interest rates. While theoretically sound under recent European monetary policy, it requires hard-coded zero-floors for standard US retail banking validations.



