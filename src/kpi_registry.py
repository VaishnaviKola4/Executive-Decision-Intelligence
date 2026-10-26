"""
KPI Registry and Departmental Mapping for Executive Decision Intelligence.
Defines metadata, classification, units, targets, and expected relationship polarities.
"""

from typing import Dict, List, Any
from dataclasses import dataclass

@dataclass
class KPIMeta:
    id: str
    name: str
    department: str  # Marketing, Sales, Operations, HR, Finance, External
    category: str    # Operational, Financial, External, Governance
    unit: str        # $, %, index, count, ratio
    desirable_direction: str  # higher, lower
    description: str

KPI_REGISTRY: Dict[str, KPIMeta] = {
    # Financial KPIs
    "revenue_k": KPIMeta(
        id="revenue_k",
        name="Gross Revenue",
        department="Finance",
        category="Financial",
        unit="$k",
        desirable_direction="higher",
        description="Total top-line recognized monthly revenue in thousands of dollars."
    ),
    "cogs_k": KPIMeta(
        id="cogs_k",
        name="Cost of Goods Sold (COGS)",
        department="Finance",
        category="Financial",
        unit="$k",
        desirable_direction="lower",
        description="Direct operational costs to manufacture and deliver products."
    ),
    "gross_margin_pct": KPIMeta(
        id="gross_margin_pct",
        name="Gross Margin",
        department="Finance",
        category="Financial",
        unit="%",
        desirable_direction="higher",
        description="Gross profit as percentage of total revenue."
    ),
    "opex_k": KPIMeta(
        id="opex_k",
        name="Operating Expenses (OpEx)",
        department="Finance",
        category="Financial",
        unit="$k",
        desirable_direction="lower",
        description="Total departmental operating expenditure including marketing, payroll, and admin."
    ),
    "operating_profit_k": KPIMeta(
        id="operating_profit_k",
        name="Operating Profit (EBITDA)",
        department="Finance",
        category="Financial",
        unit="$k",
        desirable_direction="higher",
        description="Earnings before interest, taxes, depreciation, and amortization."
    ),
    "operating_margin_pct": KPIMeta(
        id="operating_margin_pct",
        name="Operating Margin",
        department="Finance",
        category="Financial",
        unit="%",
        desirable_direction="higher",
        description="Operating profit as a percentage of gross revenue."
    ),
    "net_cash_flow_k": KPIMeta(
        id="net_cash_flow_k",
        name="Net Free Cash Flow",
        department="Finance",
        category="Financial",
        unit="$k",
        desirable_direction="higher",
        description="Net cash generation after operating expenses and working capital adjustments."
    ),
    "customer_lifetime_value": KPIMeta(
        id="customer_lifetime_value",
        name="Customer Lifetime Value (CLV)",
        department="Marketing",
        category="Financial",
        unit="$",
        desirable_direction="higher",
        description="Projected net margin earned over the average customer relationship."
    ),
    "marketing_roi_pct": KPIMeta(
        id="marketing_roi_pct",
        name="Marketing ROI",
        department="Marketing",
        category="Financial",
        unit="%",
        desirable_direction="higher",
        description="Return on marketing expenditure computed against customer gross margin."
    ),

    # Operational - Marketing
    "marketing_spend_k": KPIMeta(
        id="marketing_spend_k",
        name="Marketing Spend",
        department="Marketing",
        category="Operational",
        unit="$k",
        desirable_direction="higher",
        description="Direct programmatic, search, and brand marketing outlay."
    ),
    "customer_acquisition_cost": KPIMeta(
        id="customer_acquisition_cost",
        name="Customer Acquisition Cost (CAC)",
        department="Marketing",
        category="Operational",
        unit="$",
        desirable_direction="lower",
        description="Cost to acquire a single paying customer."
    ),
    "new_customers_acquired": KPIMeta(
        id="new_customers_acquired",
        name="New Customers Acquired",
        department="Marketing",
        category="Operational",
        unit="count",
        desirable_direction="higher",
        description="Volume of newly converted customers in the period."
    ),

    # Operational - Sales
    "sales_conversion_rate_pct": KPIMeta(
        id="sales_conversion_rate_pct",
        name="Sales Conversion Rate",
        department="Sales",
        category="Operational",
        unit="%",
        desirable_direction="higher",
        description="Conversion percentage from qualified sales pipeline to booked revenue."
    ),
    "sales_pipeline_k": KPIMeta(
        id="sales_pipeline_k",
        name="Sales Pipeline Value",
        department="Sales",
        category="Operational",
        unit="$k",
        desirable_direction="higher",
        description="Aggregate value of active qualified deals in sales funnel."
    ),

    # Operational - Supply Chain & Operations
    "on_time_delivery_rate_pct": KPIMeta(
        id="on_time_delivery_rate_pct",
        name="On-Time Delivery Rate (OTD)",
        department="Operations",
        category="Operational",
        unit="%",
        desirable_direction="higher",
        description="Percentage of customer orders fulfilled and delivered on time without defects."
    ),
    "inventory_turnover_ratio": KPIMeta(
        id="inventory_turnover_ratio",
        name="Inventory Turnover Ratio",
        department="Operations",
        category="Operational",
        unit="ratio",
        desirable_direction="higher",
        description="Frequency at which inventory stock is sold and replenished per annum."
    ),
    "warehouse_capacity_utilization_pct": KPIMeta(
        id="warehouse_capacity_utilization_pct",
        name="Warehouse Capacity Utilization",
        department="Operations",
        category="Operational",
        unit="%",
        desirable_direction="higher",
        description="Percentage of operational distribution hub volume actively utilized."
    ),

    # Operational - People / HR
    "employee_headcount": KPIMeta(
        id="employee_headcount",
        name="Total Headcount",
        department="Human Resources",
        category="Operational",
        unit="count",
        desirable_direction="higher",
        description="Active full-time equivalent (FTE) headcount across all departments."
    ),
    "employee_productivity_index": KPIMeta(
        id="employee_productivity_index",
        name="Employee Productivity Index",
        department="Human Resources",
        category="Operational",
        unit="index",
        desirable_direction="higher",
        description="Composite departmental efficiency score (baseline 100)."
    ),

    # External & Macro
    "macro_economic_index": KPIMeta(
        id="macro_economic_index",
        name="Macro Economic Index",
        department="External",
        category="External",
        unit="index",
        desirable_direction="higher",
        description="Consumer sentiment and macroeconomic demand climate indicator."
    ),
    "competitive_pressure_index": KPIMeta(
        id="competitive_pressure_index",
        name="Competitive Pressure Index",
        department="External",
        category="External",
        unit="index",
        desirable_direction="lower",
        description="Market competitor pricing and ad spend aggression index (1-10)."
    ),
    "supply_chain_disruption_index": KPIMeta(
        id="supply_chain_disruption_index",
        name="Supply Chain Disruption Index",
        department="External",
        category="External",
        unit="index",
        desirable_direction="lower",
        description="External freight, logistics, and port disruption severity scale (0-100)."
    ),
}

def get_kpis_by_department(dept: str) -> List[KPIMeta]:
    return [meta for meta in KPI_REGISTRY.values() if meta.department.lower() == dept.lower()]

def get_kpis_by_category(category: str) -> List[KPIMeta]:
    return [meta for meta in KPI_REGISTRY.values() if meta.category.lower() == category.lower()]
