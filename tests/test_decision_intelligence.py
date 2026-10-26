"""
Unit and Integration Tests for Executive Decision Intelligence System.
Verifies data generation, diagnostic computations, LLM briefings, Q&A, and evaluations.
"""

import pytest
import pandas as pd
import numpy as np

from src.data_generator import EnterpriseDataGenerator
from src.kpi_registry import KPI_REGISTRY
from src.diagnostic_engine import DiagnosticEngine
from src.llm_engine import LLMReasoningEngine
from src.pipeline import DecisionIntelligenceSystem
from eval.evaluation_harness import DecisionIntelligenceEvaluator

def test_data_generator_shape_and_columns():
    gen = EnterpriseDataGenerator(seed=123)
    df = gen.generate(n_months=24)
    assert len(df) == 24
    # Check essential operational and financial columns
    assert "revenue_k" in df.columns
    assert "operating_profit_k" in df.columns
    assert "marketing_spend_k" in df.columns
    assert "customer_acquisition_cost" in df.columns
    assert "on_time_delivery_rate_pct" in df.columns
    assert "supply_chain_disruption_index" in df.columns

def test_kpi_registry_integrity():
    for kpi_id, meta in KPI_REGISTRY.items():
        assert meta.id == kpi_id
        assert meta.department in ["Finance", "Marketing", "Sales", "Operations", "Human Resources", "External"]
        assert meta.desirable_direction in ["higher", "lower"]

def test_diagnostic_engine_computations():
    gen = EnterpriseDataGenerator(seed=42)
    df = gen.generate(n_months=36)
    engine = DiagnosticEngine(df)

    # 1. Summary KPIs
    summary = engine.compute_summary_kpis()
    assert "revenue_k" in summary
    assert "operating_profit_k" in summary
    assert isinstance(summary["revenue_k"]["current"], float)

    # 2. Driver Attribution
    drivers = engine.estimate_driver_elasticity_and_impact("operating_profit_k")
    assert len(drivers) > 0
    assert "standardized_coefficient" in drivers[0]
    assert "relative_impact_share_pct" in drivers[0]

    # 3. Correlation
    corrs = engine.analyze_driver_correlations("operating_profit_k")
    assert not corrs.empty
    assert "pearson_corr" in corrs.columns

    # 4. Variance Decomposition
    var = engine.decompose_profit_variance()
    assert "actual_operating_profit_k" in var
    assert "budget_operating_profit_k" in var

def test_llm_reasoning_engine_deterministic():
    gen = EnterpriseDataGenerator(seed=42)
    df = gen.generate(n_months=36)
    engine = DiagnosticEngine(df)

    summary = engine.compute_summary_kpis()
    drivers = engine.estimate_driver_elasticity_and_impact("operating_profit_k")
    variance = engine.decompose_profit_variance()
    anomalies = engine.detect_anomalies("operating_profit_k")

    llm = LLMReasoningEngine()
    briefing = llm.generate_executive_briefing(summary, drivers, variance, anomalies)

    assert "executive_headline" in briefing
    assert len(briefing["core_insights"]) >= 3
    assert len(briefing["actionable_recommendations"]) >= 3
    for ins in briefing["core_insights"]:
        assert "evidence" in ins
        assert "statistical_basis" in ins
        assert "causality_note" in ins

def test_pipeline_ask_query():
    system = DecisionIntelligenceSystem()
    ans = system.ask("What is driving profitability down?")
    assert "answer" in ans
    assert "supporting_metrics" in ans
    assert len(ans["supporting_metrics"]) > 0

def test_evaluation_harness_benchmarks():
    system = DecisionIntelligenceSystem()
    evaluator = DecisionIntelligenceEvaluator(system)
    report = evaluator.run_evaluation_suite()

    metrics = report["evaluation_metrics"]
    assert metrics["Accuracy"]["score"] >= 0.95
    assert metrics["Precision"]["score"] >= 0.80
    assert metrics["Recall"]["score"] >= 0.75
    assert metrics["F1 Score"]["score"] >= 0.80
    assert metrics["Insight Grounding"]["score"] >= 0.90
    assert metrics["Recommendation Quality"]["score"] >= 0.85
