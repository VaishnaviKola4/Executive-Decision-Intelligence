"""
Pipeline Orchestrator for Executive Decision Intelligence.
Coordinates data ingestion, diagnostic computations, driver attribution,
anomaly detection, and LLM-grounded executive briefing generation.
"""

import os
import pandas as pd
from typing import Dict, Any, Optional

from src.data_generator import EnterpriseDataGenerator
from src.kpi_registry import KPI_REGISTRY
from src.diagnostic_engine import DiagnosticEngine
from src.llm_engine import LLMReasoningEngine

class DecisionIntelligenceSystem:
    """
    Main entrypoint orchestrating data diagnostics and executive insight generation.
    """

    def __init__(self, data_path: Optional[str] = None, api_key: Optional[str] = None):
        self.data_path = data_path
        self.api_key = api_key
        self.df: Optional[pd.DataFrame] = None
        self.diagnostic_engine: Optional[DiagnosticEngine] = None
        self.llm_engine = LLMReasoningEngine(api_key=api_key)

        if data_path and os.path.exists(data_path):
            self.load_data(data_path)
        else:
            self.initialize_default_data()

    def initialize_default_data(self, n_months: int = 36) -> pd.DataFrame:
        """Generates synthetic enterprise performance data if no file provided."""
        generator = EnterpriseDataGenerator(seed=42)
        self.df = generator.generate(n_months=n_months)
        self.diagnostic_engine = DiagnosticEngine(self.df)
        return self.df

    def load_data(self, file_path: str) -> pd.DataFrame:
        """Loads and prepares external dataset."""
        if file_path.endswith(".csv"):
            self.df = pd.read_csv(file_path)
        elif file_path.endswith((".xls", ".xlsx")):
            self.df = pd.read_excel(file_path)
        else:
            raise ValueError("Supported file formats: CSV or Excel.")

        self.diagnostic_engine = DiagnosticEngine(self.df)
        return self.df

    def run_full_intelligence_cycle(self, period_idx: int = -1, target_kpi: str = "operating_profit_k") -> Dict[str, Any]:
        """
        Executes end-to-end intelligence cycle:
        1. Snapshot & MoM/YoY Variance
        2. Driver Attribution (Ridge Regression standardized coefficients)
        3. Statistical Correlation Matrix
        4. Outlier & Anomaly Detection
        5. Budget Waterfall Variance
        6. LLM Grounded Executive Briefing & Recommendations
        """
        if self.diagnostic_engine is None or self.df is None:
            raise ValueError("No data loaded. Call load_data() or initialize_default_data().")

        # 1. Summary KPIs
        summary_kpis = self.diagnostic_engine.compute_summary_kpis(period_idx=period_idx)

        # 2. Driver Attribution
        drivers = self.diagnostic_engine.estimate_driver_elasticity_and_impact(target_kpi=target_kpi)

        # 3. Correlation Analysis
        correlations = self.diagnostic_engine.analyze_driver_correlations(target_kpi=target_kpi)

        # 4. Anomaly Detection
        anomalies = self.diagnostic_engine.detect_anomalies(kpi_id=target_kpi)

        # 5. Budget Variance
        variance = self.diagnostic_engine.decompose_profit_variance(period_idx=period_idx)

        # 6. LLM Briefing
        briefing = self.llm_engine.generate_executive_briefing(
            summary_kpis=summary_kpis,
            drivers=drivers,
            variance=variance,
            anomalies=anomalies
        )

        return {
            "summary_kpis": summary_kpis,
            "drivers": drivers,
            "correlations": correlations.to_dict(orient="records"),
            "anomalies": anomalies,
            "variance": variance,
            "executive_briefing": briefing
        }

    def ask(self, query: str) -> Dict[str, Any]:
        """
        Interactively answers executive queries using the latest diagnostic state.
        """
        context = self.run_full_intelligence_cycle()
        return self.llm_engine.answer_executive_query(query, context)
