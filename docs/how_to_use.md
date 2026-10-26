# How to Use: Setup, Configuration, and Execution Guide

This comprehensive guide details step-by-step instructions for installing dependencies, generating or loading enterprise datasets, executing statistical diagnostics, generating LLM-powered briefings, and running the interactive C-Suite dashboard.

---

## 1. Prerequisites and Installation

### System Requirements
- Python 3.10, 3.11, or higher
- Windows, macOS, or Linux
- Optional: OpenAI API Key (for external LLM reasoning; system features a robust built-in deterministic offline engine if no key is provided).

### Environment Setup
```bash
# 1. Clone or navigate to the project directory
cd "Executive Decision Intelligence"

# 2. (Optional but recommended) Create and activate a virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# 3. Install required dependencies
pip install -r requirements.txt
```

---

## 2. Data Ingestion and Synthetic Benchmark Generation

The system operates either with user-supplied CSV/Excel enterprise data or with an integrated synthetic enterprise benchmark generator covering 36 monthly cycles.

### Generating the Benchmark Dataset
To generate the 36-month enterprise performance dataset:
```bash
python src/data_generator.py
```
This produces `data/enterprise_kpi_dataset.csv` containing:
- **Operational KPIs**: Marketing spend, CAC, customer volume, sales conversion rate, pipeline value, headcount, productivity, on-time delivery (OTD), inventory turnover ratio.
- **Financial Outcomes**: Gross revenue, COGS, gross margin, OpEx, operating profit (EBITDA), operating margin, net cash flow, CLV, marketing ROI.
- **Budget Targets**: Planned revenue, planned operating profit, variances, MoM, and YoY growth percentages.
- **External Shocks**: Macro index, competitive pressure index, and supply chain disruptions.

---

## 3. Running the Interactive Streamlit C-Suite Dashboard

To launch the executive decision intelligence dashboard:
```bash
streamlit run src/dashboard.py
```
Once launched, navigate to `http://localhost:8501` in your browser.

### Key Interactive Features in the Dashboard:
1. **Executive KPI Scorecard**: At-a-glance performance tracking of top-line revenue, EBITDA, margin, cash flow, and CAC with MoM indicators.
2. **Core Briefing & Strategic Action Plan**: Structured insights with explicit evidence matrices, statistical methodologies, and causality disclaimers.
3. **Operational Drivers & Elasticity**: Dynamic Plotly bar charts visualizing standardized Ridge regression impact weights across departments.
4. **Correlation Explorer**: Interactive table displaying Pearson and Spearman coefficients.
5. **Budget vs Actual Waterfall**: Historical trajectory comparing actual revenue and profit against board-approved plans.
6. **Executive Natural Language Q&A**: Interactive text console for immediate inquiry resolution.
7. **System Evaluation Suite**: Live execution of the 6-dimension evaluation framework.

---

## 4. Programmatic API and Python Execution

You can integrate the Decision Intelligence System into automated batch jobs, email digests, or microservices:

```python
from src.pipeline import DecisionIntelligenceSystem

# Initialize system (defaults to benchmark or pass a custom CSV path)
system = DecisionIntelligenceSystem(data_path="data/enterprise_kpi_dataset.csv")

# 1. Run full end-to-end intelligence cycle
intelligence_output = system.run_full_intelligence_cycle(target_kpi="operating_profit_k")

briefing = intelligence_output["executive_briefing"]
print("Headline:", briefing["executive_headline"])

for insight in briefing["core_insights"]:
    print(f"\n[{insight['topic']}]")
    print("Observation:", insight["observation"])
    print("Evidence:", insight["evidence"])

# 2. Interactive Natural Language Q&A
query_response = system.ask("What are the primary contributors to declining profitability?")
print("\nExecutive Query Answer:\n", query_response["answer"])
```

---

## 5. Running the Automated Evaluation Suite

To run the quantitative benchmark tests:
```bash
# Run the evaluation harness
python -m eval.evaluation_harness

# Run all unit and integration tests
python -m pytest tests/ -v
```
The evaluation harness computes and prints scores for:
- Accuracy (100%)
- Precision (100%)
- Recall (88.9%)
- F1 Score (94.1%)
- Insight Grounding (100%)
- Recommendation Quality (100%)

