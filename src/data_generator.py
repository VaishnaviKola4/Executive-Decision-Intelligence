"""
Synthetic Enterprise Dataset Generator for Executive Decision Intelligence.
Generates multi-department operational KPIs, financial outcomes, external factors,
and historical performance data spanning monthly periods.
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple, Optional
import os

class EnterpriseDataGenerator:
    """
    Generates realistic, synchronized operational and financial datasets
    featuring structural macro trends, seasonal fluctuations, marketing elasticity,
    supply chain shocks, and departmental performance variations.
    """

    def __init__(self, seed: int = 42):
        np.random.seed(seed)
        self.seed = seed

    def generate(self, n_months: int = 36, start_date: str = "2023-01-01") -> pd.DataFrame:
        """
        Generates monthly business performance data.
        
        Args:
            n_months: Number of monthly periods to generate (e.g. 36 = 3 years).
            start_date: Start date for the timeline (YYYY-MM-DD).
            
        Returns:
            pd.DataFrame containing operational KPIs, financials, budgets, and external factors.
        """
        date_range = pd.date_range(start=start_date, periods=n_months, freq="MS")
        df = pd.DataFrame({"date": date_range})
        df["period_index"] = np.arange(n_months)
        df["month_of_year"] = df["date"].dt.month
        df["year"] = df["date"].dt.year
        df["quarter"] = "Q" + df["date"].dt.quarter.astype(str)

        # -------------------------------------------------------------
        # 1. External Factors & Market Context
        # -------------------------------------------------------------
        # Seasonality: Strong peak in Q4 (Holiday shopping: Nov/Dec), mid-year lift (June/July)
        seasonality = np.sin((df["month_of_year"] - 1) * (2 * np.pi / 12) - 1.5) * 0.12
        # Q4 boost specifically
        q4_boost = np.where(df["month_of_year"].isin([11, 12]), 0.18, 0.0)
        
        # Macro Economic Index (Baseline 100, cyclical fluctuation with mild inflationary pressure)
        macro_trend = 100 + np.linspace(-2, 8, n_months) + np.sin(np.linspace(0, 3 * np.pi, n_months)) * 3.5
        df["macro_economic_index"] = np.round(macro_trend, 2)
        
        # Market Competitive Pressure (Scale 1-10)
        df["competitive_pressure_index"] = np.round(
            5.0 + 1.2 * np.sin(np.linspace(0.5, 4.0, n_months)) + np.random.normal(0, 0.2, n_months), 2
        )

        # Supply Chain Disruption Index (0-100, baseline 15, with acute shock in month 18-21)
        sc_disruption = 15.0 + np.random.normal(0, 3, n_months)
        if n_months >= 22:
            sc_disruption[18:22] += 32.0  # Acute global logistics / port congestion shock
        df["supply_chain_disruption_index"] = np.round(np.clip(sc_disruption, 5, 95), 1)

        # -------------------------------------------------------------
        # 2. Operational KPIs by Department
        # -------------------------------------------------------------
        
        # Marketing: Expenditure ($k)
        base_marketing = 180 + df["period_index"] * 3.0 + (seasonality + q4_boost) * 80
        marketing_spend = base_marketing + np.random.normal(0, 8, n_months)
        # Targeted marketing campaign push at month 10-13 and month 28-30
        if n_months >= 14:
            marketing_spend[10:14] += 35
        if n_months >= 31:
            marketing_spend[28:31] += 45
        df["marketing_spend_k"] = np.round(np.clip(marketing_spend, 100, 450), 2)

        # Customer Acquisition Cost (CAC in $)
        # CAC goes up if competitive pressure increases and marketing efficiency drops
        cac = 120 + df["competitive_pressure_index"] * 8.5 - (seasonality * 15) + np.random.normal(0, 4, n_months)
        df["customer_acquisition_cost"] = np.round(np.clip(cac, 80, 250), 2)

        # New Customers Acquired
        # Driven by marketing spend / CAC with diminishing returns
        new_cust = (df["marketing_spend_k"] * 1000) / (df["customer_acquisition_cost"] * 1.1)
        df["new_customers_acquired"] = np.round(new_cust + np.random.normal(0, 25, n_months)).astype(int)

        # Sales Performance: Active B2B / Enterprise Accounts & Conversion Rate (%)
        base_conv_rate = 3.2 + (seasonality * 1.5) - (df["competitive_pressure_index"] * 0.1)
        df["sales_conversion_rate_pct"] = np.round(np.clip(base_conv_rate + np.random.normal(0, 0.15, n_months), 1.5, 6.0), 2)
        
        # Sales Pipeline Value ($k)
        df["sales_pipeline_k"] = np.round(df["marketing_spend_k"] * 14.5 + np.random.normal(0, 100, n_months), 2)

        # HR / People: Employee Productivity Score (Index 70-130) & Headcount
        base_headcount = 120 + (df["period_index"] * 1.8).astype(int)
        df["employee_headcount"] = base_headcount
        
        # Attrition in mid periods due to restructuring
        emp_productivity = 100.0 + (df["period_index"] * 0.4) - (df["supply_chain_disruption_index"] * 0.15)
        if n_months >= 20:
            emp_productivity[16:20] -= 12.0 # Restructuring dip
        df["employee_productivity_index"] = np.round(np.clip(emp_productivity + np.random.normal(0, 2.5, n_months), 70, 130), 1)

        # Operations & Supply Chain: Inventory Turnover & Delivery Efficiency (%)
        base_deliv_eff = 95.0 - (df["supply_chain_disruption_index"] * 0.28)
        df["on_time_delivery_rate_pct"] = np.round(np.clip(base_deliv_eff + np.random.normal(0, 1.2, n_months), 65, 99.5), 1)
        
        # Inventory Holding (Units in thousands) and Inventory Turnover Ratio
        inv_turnover = 6.2 - (df["supply_chain_disruption_index"] * 0.035) + np.random.normal(0, 0.2, n_months)
        df["inventory_turnover_ratio"] = np.round(np.clip(inv_turnover, 2.5, 8.5), 2)
        df["warehouse_capacity_utilization_pct"] = np.round(
            np.clip(75 + (seasonality * 40) + (df["supply_chain_disruption_index"] * 0.15) + np.random.normal(0, 2, n_months), 50, 99), 1
        )

        # -------------------------------------------------------------
        # 3. Financial Outcomes (Bridging Operational Drivers)
        # -------------------------------------------------------------
        
        # Revenue ($k): Formed by existing base customers + new customer spend + seasonality + sales efficiency
        base_mrr = 1200 + df["period_index"] * 28.0
        revenue_k = base_mrr * (1 + seasonality + q4_boost) + (df["new_customers_acquired"] * 0.45)
        # Supply chain delivery failures trigger refunds and missed shipments
        delivery_penalty = np.where(df["on_time_delivery_rate_pct"] < 88.0, (88.0 - df["on_time_delivery_rate_pct"]) * 14.0, 0)
        revenue_k -= delivery_penalty
        df["revenue_k"] = np.round(revenue_k + np.random.normal(0, 20, n_months), 2)

        # Cost of Goods Sold (COGS $k): Influenced by sales volume and supply chain disruption costs
        cogs_ratio = 0.42 + (df["supply_chain_disruption_index"] * 0.0018)
        cogs_k = df["revenue_k"] * cogs_ratio + np.random.normal(0, 15, n_months)
        df["cogs_k"] = np.round(cogs_k, 2)
        df["gross_profit_k"] = np.round(df["revenue_k"] - df["cogs_k"], 2)
        df["gross_margin_pct"] = np.round((df["gross_profit_k"] / df["revenue_k"]) * 100, 2)

        # Operating Expenses (OpEx $k): Marketing Spend + Payroll + Logistics Overhead
        payroll_k = df["employee_headcount"] * 5.8
        logistics_overhead_k = 45 + (100 - df["on_time_delivery_rate_pct"]) * 1.8
        general_admin_k = 65 + df["period_index"] * 0.8
        opex_k = df["marketing_spend_k"] + payroll_k + logistics_overhead_k + general_admin_k
        df["opex_k"] = np.round(opex_k + np.random.normal(0, 12, n_months), 2)

        # Operating Income (EBITDA $k) & Operating Margin (%)
        df["operating_profit_k"] = np.round(df["gross_profit_k"] - df["opex_k"], 2)
        df["operating_margin_pct"] = np.round((df["operating_profit_k"] / df["revenue_k"]) * 100, 2)

        # Net Cash Flow ($k): Operating Profit adjusted for working capital changes
        wc_change = (df["inventory_turnover_ratio"] - 5.0) * 18.0
        df["net_cash_flow_k"] = np.round(df["operating_profit_k"] * 0.82 + wc_change + np.random.normal(0, 15, n_months), 2)

        # Customer Lifetime Value (CLV in $) & Return on Investment (ROI in %)
        df["customer_lifetime_value"] = np.round(
            (df["gross_margin_pct"] / 100.0) * 1850 * (df["on_time_delivery_rate_pct"] / 90.0) + np.random.normal(0, 20, n_months), 2
        )
        # Marketing ROI (%) = ((Gross Profit attributable to new sales - Marketing Spend) / Marketing Spend) * 100
        mktg_roi = (((df["new_customers_acquired"] * 0.45 * (df["gross_margin_pct"] / 100.0) * 1000) - (df["marketing_spend_k"] * 1000)) / (df["marketing_spend_k"] * 1000)) * 100
        df["marketing_roi_pct"] = np.round(np.clip(mktg_roi, -20, 250), 2)

        # -------------------------------------------------------------
        # 4. Budget Targets & Budget vs Actual Performance
        # -------------------------------------------------------------
        # Target Revenue: modeled as planned budget with standard 8% annual growth target
        budget_revenue_k = 1250 + df["period_index"] * 30.0 + (seasonality + q4_boost) * 150
        df["budget_revenue_k"] = np.round(budget_revenue_k, 2)
        df["revenue_variance_k"] = np.round(df["revenue_k"] - df["budget_revenue_k"], 2)
        df["revenue_budget_attainment_pct"] = np.round((df["revenue_k"] / df["budget_revenue_k"]) * 100, 2)

        # Target Operating Profit
        budget_operating_profit_k = budget_revenue_k * 0.22
        df["budget_operating_profit_k"] = np.round(budget_operating_profit_k, 2)
        df["profit_variance_k"] = np.round(df["operating_profit_k"] - df["budget_operating_profit_k"], 2)
        df["profit_budget_attainment_pct"] = np.round((df["operating_profit_k"] / df["budget_operating_profit_k"]) * 100, 2)

        # Period-over-period changes (MoM % and YoY %)
        df["revenue_mom_change_pct"] = np.round(df["revenue_k"].pct_change() * 100, 2).fillna(0.0)
        df["operating_profit_mom_change_pct"] = np.round(df["operating_profit_k"].pct_change() * 100, 2).fillna(0.0)
        df["gross_margin_mom_change_pct"] = np.round(df["gross_margin_pct"].diff(), 2).fillna(0.0)

        # Year-over-Year (12 months lag)
        df["revenue_yoy_growth_pct"] = np.round(df["revenue_k"].pct_change(12) * 100, 2).fillna(0.0)
        df["operating_profit_yoy_growth_pct"] = np.round(df["operating_profit_k"].pct_change(12) * 100, 2).fillna(0.0)

        return df

    def save_to_csv(self, df: pd.DataFrame, file_path: str) -> str:
        """Saves generated dataset to disk."""
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        df.to_csv(file_path, index=False)
        return file_path


if __name__ == "__main__":
    generator = EnterpriseDataGenerator(seed=42)
    dataset = generator.generate(n_months=36)
    out_file = os.path.join(os.path.dirname(__file__), "..", "data", "enterprise_kpi_dataset.csv")
    generator.save_to_csv(dataset, out_file)
    print(f"Generated enterprise dataset successfully: {out_file} ({dataset.shape[0]} rows, {dataset.shape[1]} columns)")
