# API & Interface Reference Guide

This document defines the interface specifications, classes, methods, data schemas, and UI components of the Executive Decision Intelligence (EDI) platform.

---

## 1. Core Classes & Methods

### `DecisionIntelligenceSystem`
`src.pipeline.DecisionIntelligenceSystem(data_path: Optional[str] = None, api_key: Optional[str] = None)`
The primary orchestrator class coordinating ingestion, diagnostics, and executive briefing synthesis.

#### Methods:
- `initialize_default_data(n_months: int = 36) -> pd.DataFrame`
  - Generates synthetic 36-month enterprise dataset and attaches diagnostic engine.
- `load_data(file_path: str) -> pd.DataFrame`
  - Loads an external CSV or Excel file containing operational and financial KPIs.
- `run_full_intelligence_cycle(period_idx: int = -1, target_kpi: str = "operating_profit_k") -> Dict[str, Any]`
  - Runs end-to-end diagnostic computations, anomaly detection, regression driver analysis, and executive synthesis.
  - Returns dictionary with keys: `summary_kpis`, `drivers`, `correlations`, `anomalies`, `variance`, `executive_briefing`.
- `ask(query: str) -> Dict[str, Any]`
  - Processes natural language executive questions and returns grounded narrative answers with citations.

---

### `DiagnosticEngine`
`src.diagnostic_engine.DiagnosticEngine(data: pd.DataFrame)`
Statistical computation engine linking operational KPIs to financial outcomes.

#### Methods:
- `compute_summary_kpis(period_idx: int = -1) -> Dict[str, Any]`
  - Calculates latest values, absolute changes, percentage changes, and direction of improvement for all registered KPIs.
- `detect_anomalies(kpi_id: str, z_thresh: float = 2.0) -> List[Dict[str, Any]]`
  - Computes rolling 6-month mean and standard deviation; flags periods where $|Z| \ge \text{z\_thresh}$.
- `analyze_driver_correlations(target_kpi: str = "operating_profit_k") -> pd.DataFrame`
  - Computes Pearson (linear) and Spearman (rank-order) correlation coefficients against target financial metric.
- `estimate_driver_elasticity_and_impact(target_kpi: str = "operating_profit_k") -> List[Dict[str, Any]]`
  - Fits standardized regularized Ridge regression to quantify the relative driver weights and impact share of operational features.
- `decompose_profit_variance(period_idx: int = -1) -> Dict[str, Any]`
  - Decomposes target profit variance into revenue variance, COGS, OpEx, and percentage plan attainment.

---

### `LLMReasoningEngine`
`src.llm_engine.LLMReasoningEngine(api_key: Optional[str] = None, model: str = "gpt-4o-mini")`
Synthesizes quantitative metrics, anomaly alerts, and regression weights into structured executive briefings.

#### Methods:
- `generate_executive_briefing(summary_kpis, drivers, variance, anomalies) -> Dict[str, Any]`
  - Generates comprehensive C-suite briefing. Automatically uses OpenAI if API key is present; otherwise utilizes internal deterministic grounded reasoning rules.
- `answer_executive_query(query: str, engine_context: Dict[str, Any]) -> Dict[str, Any]`
  - Returns grounded Q&A analysis for specific executive prompts.

---

## 2. Output Data Schemas

### Executive Briefing Schema
```json
{
  "engine_mode": "Deterministic Structured Intelligence Engine (Offline Validated)",
  "executive_headline": "Monthly Performance: Revenue reached $2,185.3k (+4.2% MoM) with Operating Profit at $392.4k (18.0% margin, +6.1% MoM).",
  "period": "2025-12-01",
  "core_insights": [
    {
      "topic": "Operational Driver Attribution",
      "observation": "Multivariate Ridge regression identifies primary positive tailwinds from [New Customers Acquired, Sales Conversion Rate] and key operational headwinds from [Supply Chain Disruption Index].",
      "evidence": {
        "Leading Positive Driver": "New Customers Acquired",
        "Leading Positive Impact Share": "19.4%",
        "Leading Negative Driver": "Supply Chain Disruption Index",
        "Leading Negative Impact Share": "18.0%"
      },
      "statistical_basis": "Standardized Ridge regression coefficients across operational feature space.",
      "causality_note": "Statistical correlation; represents predictive association rather than randomized causal trial."
    }
  ],
  "actionable_recommendations": [
    {
      "rank": 1,
      "title": "Reallocate Programmatic Ad Spend to High-Conversion Channels",
      "department": "Marketing & Sales",
      "rationale": "CAC is currently $142.5 with marketing ROI recorded at 68.2%.",
      "proposed_action": "Trim bottom 20% underperforming paid acquisition campaigns; redirect $25k to high-intent search.",
      "expected_financial_impact": "Projected 8-12% CAC reduction ($12k-$18k monthly savings).",
      "feasibility": "High (can be implemented within 7-14 business days).",
      "risk_consideration": "Monitor organic traffic floor to avoid top-funnel contraction."
    }
  ]
}
```

---

## 3. Web Dashboard Interface (Streamlit)

The interactive dashboard at `src/dashboard.py` exposes:
- **Sidebar Selector**: Toggle between synthetic benchmark dataset or user-uploaded CSV/Excel file; select target financial outcome (`operating_profit_k`, `revenue_k`, `gross_margin_pct`, `net_cash_flow_k`).
- **Tab 1: Briefing & Action Plan**: Visual narrative briefings and prioritized recommendations.
- **Tab 2: Operational Drivers & Elasticity**: Interactive horizontal bar charts showing standardized feature elasticity.
- **Tab 3: Correlation Explorer**: Filterable correlation table comparing Pearson and Spearman statistics.
- **Tab 4: Budget vs Actual Waterfall**: Interactive time series with dual actual and plan traces.
- **Tab 5: Executive Q&A Query**: Immediate response engine answering natural language management questions.
- **Tab 6: System Evaluation Suite**: Real-time evaluation scorecard with precision, recall, and grounding metrics.

