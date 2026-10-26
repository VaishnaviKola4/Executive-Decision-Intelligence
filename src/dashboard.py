"""
Executive Decision Intelligence Interactive C-Suite Dashboard.
Built with Streamlit and Plotly.
Visualizes cross-departmental KPIs, operational-to-financial bridges,
elasticity coefficients, anomaly flags, and interactive LLM executive inquiry.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
import sys

# Ensure root directory is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.pipeline import DecisionIntelligenceSystem
from src.kpi_registry import KPI_REGISTRY, get_kpis_by_department

st.set_page_config(
    page_title="Executive Decision Intelligence System",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 15px;
        border-left: 5px solid #1f77b4;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .headline-box {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        padding: 18px 24px;
        border-radius: 8px;
        margin-bottom: 20px;
    }
    .insight-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .badge-pos {
        background-color: #d4edda;
        color: #155724;
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .badge-neg {
        background-color: #f8d7da;
        color: #721c24;
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Sidebar Controls
# ---------------------------------------------------------
st.sidebar.image("https://img.icons8.com/fluency/96/combo-chart.png", width=64)
st.sidebar.title("Decision Intelligence")
st.sidebar.caption("Bridging Operational Performance & Financial Outcomes")

data_source = st.sidebar.radio(
    "Data Source",
    ["Synthetic Enterprise Benchmark (36 Months)", "Upload Custom CSV/Excel"]
)

api_key = st.sidebar.text_input("OpenAI API Key (Optional)", type="password", help="Leave blank to use internal deterministic grounded engine.")

# Target Financial Outcome
target_kpi = st.sidebar.selectbox(
    "Target Financial Outcome",
    ["operating_profit_k", "revenue_k", "gross_margin_pct", "net_cash_flow_k"],
    format_func=lambda x: KPI_REGISTRY.get(x).name if x in KPI_REGISTRY else x
)

# Initialize System
@st.cache_resource
def get_system(data_path=None, key=None):
    return DecisionIntelligenceSystem(data_path=data_path, api_key=key)

if data_source == "Upload Custom CSV/Excel":
    uploaded_file = st.sidebar.file_uploader("Upload Enterprise Performance Data", type=["csv", "xlsx"])
    if uploaded_file is not None:
        temp_path = os.path.join("data", "uploaded_data.csv")
        os.makedirs("data", exist_ok=True)
        if uploaded_file.name.endswith(".csv"):
            df_upload = pd.read_csv(uploaded_file)
            df_upload.to_csv(temp_path, index=False)
        else:
            df_upload = pd.read_excel(uploaded_file)
            df_upload.to_csv(temp_path, index=False)
        system = DecisionIntelligenceSystem(data_path=temp_path, api_key=api_key)
    else:
        st.info("Please upload a CSV file with historical operational & financial KPIs, or switch to Benchmark.")
        system = get_system(key=api_key)
else:
    system = get_system(key=api_key)

# Execute Full Intelligence Pipeline
with st.spinner("Analyzing cross-departmental KPIs and computing driver elasticity..."):
    results = system.run_full_intelligence_cycle(target_kpi=target_kpi)

summary = results["summary_kpis"]
drivers = results["drivers"]
briefing = results["executive_briefing"]
variance = results["variance"]
anomalies = results["anomalies"]
df = system.df

# ---------------------------------------------------------
# Header Banner
# ---------------------------------------------------------
st.markdown(f"""
<div class="headline-box">
    <h3 style="margin:0; font-size:1.4rem;">Executive Intelligence Briefing — {variance.get('period', 'Latest')}</h3>
    <p style="margin:6px 0 0 0; opacity:0.95; font-size:1.05rem;">{briefing['executive_headline']}</p>
    <div style="margin-top:8px; font-size:0.85rem; opacity:0.8;">Mode: {briefing.get('engine_mode', 'Active')} | Target Metric: {KPI_REGISTRY[target_kpi].name}</div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Executive KPI Scorecard
# ---------------------------------------------------------
st.subheader("Executive KPI Scorecard")
cols = st.columns(5)

kpi_cards = [
    ("revenue_k", "Gross Revenue", "$", "k"),
    ("operating_profit_k", "Operating Profit", "$", "k"),
    ("operating_margin_pct", "Operating Margin", "", "%"),
    ("net_cash_flow_k", "Net Cash Flow", "$", "k"),
    ("customer_acquisition_cost", "CAC", "$", "")
]

for col, (kid, label, prefix, suffix) in zip(cols, kpi_cards):
    item = summary.get(kid, {})
    val = item.get("current", 0)
    change = item.get("pct_change", 0)
    is_imp = item.get("is_improving", True)
    delta_str = f"{'+' if change >= 0 else ''}{change}% MoM"
    
    col.metric(
        label=label,
        value=f"{prefix}{val:,.1f}{suffix}",
        delta=delta_str,
        delta_color="normal" if is_imp else "inverse"
    )

st.markdown("---")

# ---------------------------------------------------------
# Main Tabs
# ---------------------------------------------------------
tab_briefing, tab_drivers, tab_correlations, tab_waterfall, tab_chat, tab_evaluation = st.tabs([
    "Briefing & Action Plan",
    "Operational Drivers & Elasticity",
    "Correlation Matrix",
    "Budget vs Actual Waterfall",
    "Executive Q&A Query",
    "System Evaluation Suite"
])

# ---------------------------------------------------------
# TAB 1: Briefing & Action Plan
# ---------------------------------------------------------
with tab_briefing:
    col_left, col_right = st.columns([1.1, 0.9])
    
    with col_left:
        st.subheader("Core Evidence-Based Insights")
        for ins in briefing.get("core_insights", []):
            with st.container():
                st.markdown(f"#### {ins['topic']}")
                st.write(ins["observation"])
                
                # Render verified evidence table
                ev_df = pd.DataFrame(list(ins["evidence"].items()), columns=["Metric / Dimension", "Observed Value"])
                st.dataframe(ev_df, hide_index=True, use_container_width=True)
                
                c1, c2 = st.columns(2)
                c1.caption(f"**Methodology:** {ins.get('statistical_basis')}")
                c2.caption(f"**Causality Distinction:** {ins.get('causality_note')}")
                st.markdown("<hr style='margin:10px 0;'>", unsafe_allow_html=True)

    with col_right:
        st.subheader("Ranked Strategic Recommendations")
        for rec in briefing.get("actionable_recommendations", []):
            with st.expander(f"#{rec['rank']} {rec['title']} ({rec['department']})", expanded=(rec['rank'] == 1)):
                st.markdown(f"**Rationale:** {rec['rationale']}")
                st.markdown(f"**Proposed Action:** {rec['proposed_action']}")
                st.info(f"**Expected Financial Impact:** {rec['expected_financial_impact']}")
                
                c_f, c_r = st.columns(2)
                c_f.markdown(f"**Feasibility:** {rec['feasibility']}")
                c_r.markdown(f"**Risk Consideration:** {rec['risk_consideration']}")

# ---------------------------------------------------------
# TAB 2: Operational Drivers & Elasticity
# ---------------------------------------------------------
with tab_drivers:
    st.subheader(f"Relative Operational Drivers of {KPI_REGISTRY[target_kpi].name}")
    st.caption("Standardized Ridge Regression coefficients decomposing which operational changes account for financial variance.")

    if drivers:
        driver_df = pd.DataFrame(drivers)
        
        # Horizontal Bar Chart of Standardized Coefficients
        fig_drivers = px.bar(
            driver_df,
            x="standardized_coefficient",
            y="driver_name",
            orientation="h",
            color="standardized_coefficient",
            color_continuous_scale="RdBu_r",
            text="standardized_coefficient",
            title=f"Standardized Impact Elasticity on {KPI_REGISTRY[target_kpi].name}",
            labels={"standardized_coefficient": "Standardized Impact Coefficient", "driver_name": "Operational KPI"}
        )
        fig_drivers.update_layout(yaxis=dict(autorange="reversed"), height=420)
        st.plotly_chart(fig_drivers, use_container_width=True)

        st.dataframe(
            driver_df[["driver_name", "department", "standardized_coefficient", "relative_impact_share_pct", "direction", "latest_period_change_pct"]],
            column_config={
                "driver_name": "Operational Driver",
                "department": "Department",
                "standardized_coefficient": st.column_config.NumberColumn("Std. Coeff", format="%.3f"),
                "relative_impact_share_pct": st.column_config.NumberColumn("Relative Impact Share (%)", format="%.1f%%"),
                "direction": "Impact Direction",
                "latest_period_change_pct": st.column_config.NumberColumn("Latest MoM Change (%)", format="%.1f%%")
            },
            hide_index=True,
            use_container_width=True
        )

# ---------------------------------------------------------
# TAB 3: Correlation Matrix
# ---------------------------------------------------------
with tab_correlations:
    st.subheader("Statistical Correlation Explorer")
    st.caption("Pearson and Spearman correlation coefficients. Note: Correlation measures statistical association, not confirmed causation.")

    corr_df = pd.DataFrame(results["correlations"])
    
    col_c1, col_c2 = st.columns([1.2, 0.8])
    with col_c1:
        st.dataframe(
            corr_df[["driver_name", "department", "pearson_corr", "spearman_corr", "relationship_type"]],
            column_config={
                "driver_name": "Metric",
                "department": "Department",
                "pearson_corr": st.column_config.NumberColumn("Pearson (Linear)", format="%.3f"),
                "spearman_corr": st.column_config.NumberColumn("Spearman (Rank)", format="%.3f"),
                "relationship_type": "Classification"
            },
            hide_index=True,
            use_container_width=True
        )

    with col_c2:
        top_corr = corr_df.head(6)
        fig_corr = px.bar(
            top_corr,
            x="abs_correlation",
            y="driver_name",
            orientation="h",
            title="Top Absolute Correlated Metrics",
            labels={"abs_correlation": "|Correlation|", "driver_name": "Metric"}
        )
        fig_corr.update_layout(yaxis=dict(autorange="reversed"), height=380)
        st.plotly_chart(fig_corr, use_container_width=True)

# ---------------------------------------------------------
# TAB 4: Budget vs Actual Waterfall
# ---------------------------------------------------------
with tab_waterfall:
    st.subheader("Budget vs Actual Performance Waterfall")
    v = results["variance"]

    col_v1, col_v2, col_v3 = st.columns(3)
    col_v1.metric("Actual Operating Profit", f"${v['actual_operating_profit_k']:,.1f}k")
    col_v2.metric("Target Budget Profit", f"${v['budget_operating_profit_k']:,.1f}k")
    col_v3.metric("Plan Attainment", f"{v['attainment_pct']}%", delta=f"${v['total_profit_variance_k']:,.1f}k", delta_color="normal" if v['total_profit_variance_k'] >= 0 else "inverse")

    # Time series of Revenue & Profit vs Budget
    fig_ts = go.Figure()
    fig_ts.add_trace(go.Scatter(x=df["date"], y=df["revenue_k"], name="Actual Revenue ($k)", line=dict(color="#1f77b4", width=3)))
    fig_ts.add_trace(go.Scatter(x=df["date"], y=df["budget_revenue_k"], name="Budget Revenue ($k)", line=dict(color="#1f77b4", dash="dash")))
    fig_ts.add_trace(go.Scatter(x=df["date"], y=df["operating_profit_k"], name="Actual Profit ($k)", line=dict(color="#2ca02c", width=3)))
    fig_ts.add_trace(go.Scatter(x=df["date"], y=df["budget_operating_profit_k"], name="Budget Profit ($k)", line=dict(color="#2ca02c", dash="dash")))
    
    fig_ts.update_layout(title="Historical Trajectory: Actuals vs Plan Targets", xaxis_title="Timeline", yaxis_title="USD ($k)", height=400)
    st.plotly_chart(fig_ts, use_container_width=True)

# ---------------------------------------------------------
# TAB 5: Interactive Executive Q&A
# ---------------------------------------------------------
with tab_chat:
    st.subheader("Executive Decision Inquiry Assistant")
    st.caption("Ask natural language business questions. Every response is grounded on empirical metrics and driver decompositions.")

    sample_queries = [
        "What are the primary contributors to declining profitability?",
        "How is marketing expenditure and CAC influencing our margins?",
        "What is the impact of supply chain delivery performance on revenue?"
    ]
    
    selected_sample = st.selectbox("Sample Executive Questions:", ["-- Select a question or type below --"] + sample_queries)
    user_query = st.text_input("Enter your business query:", value=selected_sample if selected_sample != "-- Select a question or type below --" else "")

    if st.button("Generate Executive Analysis", type="primary"):
        if user_query.strip():
            with st.spinner("Analyzing operational relationships and generating evidence-grounded response..."):
                ans_obj = system.ask(user_query)
                st.markdown(ans_obj["answer"])
                
                st.markdown("##### Supporting Quantitative Evidence:")
                st.json(ans_obj["supporting_metrics"])
                st.caption(f"Traceability Note: {ans_obj['distinction_note']}")
        else:
            st.warning("Please enter a question.")

# ---------------------------------------------------------
# TAB 6: System Evaluation Suite
# ---------------------------------------------------------
with tab_evaluation:
    st.subheader("System Performance & Quantitative Evaluation")
    st.caption("Automated benchmarking against ground-truth statistical standards.")

    from eval.evaluation_harness import DecisionIntelligenceEvaluator
    evaluator = DecisionIntelligenceEvaluator(system)
    eval_report = evaluator.run_evaluation_suite()

    cols_e = st.columns(3)
    metrics_items = list(eval_report["evaluation_metrics"].items())
    
    for i, (m_name, m_data) in enumerate(metrics_items):
        target_col = cols_e[i % 3]
        target_col.metric(
            label=f"{m_name} ({m_data['status']})",
            value=f"{m_data['score']:.4f}",
            delta=f"Target: {m_data['target']}",
            delta_color="normal" if m_data["status"] == "PASS" else "inverse"
        )
        target_col.caption(m_data["description"])

    st.markdown("#### Driver Identification Confusion Matrix:")
    details = eval_report["driver_validation_details"]
    st.write(f"- **True Positives (Significant Drivers Captured):** {details['true_positives']}")
    st.write(f"- **False Positives (Erroneously Flagged Non-Drivers):** {details['false_positives']}")
    st.write(f"- **False Negatives (Missed True Significant Drivers):** {details['false_negatives']}")
