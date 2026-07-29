import numpy as np

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt


# ========================
# MATHEMATICAL FUNCTIONS
# ========================

def simulate_vasicek(r0, a, b, sigma, T, dt, num_paths):
    """
    Simulates interest rate paths using the Vasicek (Ornstein-Uhlenbeck) model
    via the Euler-Maruyama numerical method.
    """
    num_steps = int(T / dt)
    time_grid = np.linspace(0, T, num_steps)

    rates = np.zeros((num_steps, num_paths))
    rates[0, :] = r0

    # Pre-compute random shocks (vectorized for speed)
    Z = np.random.standard_normal((num_steps - 1, num_paths))

    # Euler-Maruyama integration loop
    for t in range(1, num_steps):
        drift = a * (b - rates[t - 1, :]) * dt
        diffusion = sigma * np.sqrt(dt) * Z[t - 1, :]
        rates[t, :] = rates[t - 1, :] + drift + diffusion

    return rates, time_grid


def calculate_npv(cash_flows, periods, discount_rate):
    """Calculates Net Present Value of a cash flow array."""
    discount_factors = 1 / ((1 + discount_rate) ** periods)
    return np.sum(cash_flows * discount_factors)


if __name__ == "__main__":

    # Ensuring the same "random" path is simulated every time code is run
    np.random.seed(42)

    # =====================
    # VASICEK SDE SIMULATION
    # =====================
    print("Starting IRRBB Validation Model...\n")
    print("--- PART A: SIMULATING YIELD CURVE (VASICEK) ---")

    R0 = 0.05  # Current rate is 5%
    A = 0.85  # Mean reversion speed
    B = 0.03  # Long-term average is 3%
    SIGMA = 0.015  # 1.5% annual volatility
    T_YEARS = 5.0  # 5-year horizon
    DT = 1 / 252.0  # Daily time steps
    NUM_PATHS = 1000

    rates_sim, t_grid = simulate_vasicek(R0, A, B, SIGMA, T_YEARS, DT, NUM_PATHS)
    print(f"Successfully generated {NUM_PATHS} interest rate paths over {T_YEARS} years.")


    # Script pauses here - CLOSE CHART WINDOW TO CONTINUE
    plt.figure(figsize=(10, 6))
    plt.plot(t_grid, rates_sim[:, :50], alpha=0.3, color='blue', linewidth=1)
    plt.axhline(B, color='red', linestyle='--', linewidth=2, label='Long-term Mean (3%)')
    plt.title('Vasicek Interest Rate Simulation (First 50 Paths)')
    plt.xlabel('Years')
    plt.ylabel('Interest Rate')
    plt.legend()
    plt.grid(True)
    print(">> Close the Vasicek chart window to calculate NII...")
    plt.show()

    # ==========================================
    # TRANSIENT SHOCK - NET INTEREST INCOME (NII)
    # ==========================================
    print("\n--- PART B: ALM BALANCE SHEET (1-YEAR NII PROJECTION) ---")

    ASSET_BALANCE = 100_000_000  # $100M fixed assets
    ASSET_FIXED_RATE = 0.05  # 5% fixed yield
    LIABILITY_BALANCE = 80_000_000  # $80M floating liabilities

    # Calculate Asset Income (Constant)
    asset_income = ASSET_BALANCE * ASSET_FIXED_RATE

    # Calculate Liability Expense (Variable based on Year 1 of Vasicek paths)
    average_path_rates_1Y = np.mean(rates_sim[:252, :], axis=0)
    liability_expense_paths = LIABILITY_BALANCE * average_path_rates_1Y

    # Calculate NII outcomes
    nii_paths = asset_income - liability_expense_paths
    expected_nii = np.mean(nii_paths)
    best_case_nii = np.max(nii_paths)
    worst_case_nii_99 = np.percentile(nii_paths, 1)  # 99% Value at Risk

    print(f"Asset Yield (Fixed):          ${asset_income:,.2f}")
    print(f"Expected NII:                 ${expected_nii:,.2f}")
    print(f"Best Case NII (Rates drop):   ${best_case_nii:,.2f}")
    print(f"99% Worst Case NII (Spike):   ${worst_case_nii_99:,.2f}")

    # Script pauses here - CLOSE CHART WINDOW TO FINISH EVE CALCULATION
    plt.figure(figsize=(8, 5))
    plt.hist(nii_paths, bins=50, color='skyblue', edgecolor='black')
    plt.axvline(expected_nii, color='blue', linestyle='dashed', linewidth=2, label='Expected NII')
    plt.axvline(worst_case_nii_99, color='red', linestyle='dashed', linewidth=2, label='99% Worst Case (VaR)')
    plt.title('Distribution of 1-Year Net Interest Income')
    plt.xlabel('Net Interest Income ($)')
    plt.ylabel('Frequency')
    plt.legend()
    print(">> Close the NII histogram window to calculate EVE...")
    plt.show()

    # ==========================================
    # STEADY STATE - ECONOMIC VALUE OF EQUITY (EVE)
    # ==========================================
    print("\n--- PART C: ALM BALANCE SHEET (EVE SENSITIVITY SHOCK) ---")

    # Generate Cash Flow Schedules
    # Assets: $100M, 10-year bullet loan, 5% annual coupon
    asset_principal = 100_000_000
    asset_rate = 0.05
    asset_years = 10

    cf_assets = np.full(asset_years, asset_principal * asset_rate)
    cf_assets[-1] += asset_principal
    asset_periods = np.arange(1, asset_years + 1)

    # Liabilities: $80M, 1-year duration, 3% rate
    liability_principal = 80_000_000
    liability_rate = 0.03

    cf_liabilities = np.array([liability_principal * (1 + liability_rate)])
    liability_periods = np.array([1])

    # Regulatory Shock Scenarios
    baseline_discount_rate = 0.04  # Market yield curve is currently flat at 4%
    shock_bps = 0.02  # Regulators mandate a +200 basis point (2%) shock
    shocked_discount_rate = baseline_discount_rate + shock_bps

    # Baseline EVE
    npv_assets_base = calculate_npv(cf_assets, asset_periods, baseline_discount_rate)
    npv_liab_base = calculate_npv(cf_liabilities, liability_periods, baseline_discount_rate)
    eve_base = npv_assets_base - npv_liab_base

    # Shocked EVE (+200 bps)
    npv_assets_shock = calculate_npv(cf_assets, asset_periods, shocked_discount_rate)
    npv_liab_shock = calculate_npv(cf_liabilities, liability_periods, shocked_discount_rate)
    eve_shock = npv_assets_shock - npv_liab_shock

    #  Financial Impact
    eve_destruction = eve_base - eve_shock
    percent_loss = eve_destruction / eve_base

    print(f"Baseline EVE (Equity):        ${eve_base:,.0f}")
    print(f"Shocked EVE (+200 bps):       ${eve_shock:,.0f}")
    print("-" * 45)
    print(f"EVE Destruction (Loss):       ${eve_destruction:,.0f} (-{percent_loss:.1%})")
    print("\nModel Execution Complete.")