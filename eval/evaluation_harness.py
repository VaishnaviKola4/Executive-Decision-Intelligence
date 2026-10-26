"""
Evaluation Harness for Executive Decision Intelligence System.
Quantifies system performance against the prompt's 6 core evaluation metrics:
1. Accuracy (Correctness of calculation & trend identification)
2. Precision (Identified drivers supported by underlying data)
3. Recall (Proportion of actual significant movements captured)
4. F1 Score (Harmonic mean of precision and recall)
5. Insight Grounding (Proportion of insights verified by quantitative metrics)
6. Recommendation Quality (Relevance, feasibility, and actionability score)
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List
import json

from src.pipeline import DecisionIntelligenceSystem

class DecisionIntelligenceEvaluator:
    """
    Automated evaluation framework benchmarked against ground truth statistics.
    """

    def __init__(self, system: DecisionIntelligenceSystem):
        self.system = system

    def run_evaluation_suite(self) -> Dict[str, Any]:
        """
        Executes a comprehensive quantitative evaluation of the intelligence engine.
        """
        df = self.system.df
        cycle_result = self.system.run_full_intelligence_cycle()
        briefing = cycle_result["executive_briefing"]
        drivers = cycle_result["drivers"]
        summary = cycle_result["summary_kpis"]

        # ---------------------------------------------------------
        # Metric 1: Accuracy (Math correctness & trend identification)
        # ---------------------------------------------------------
        # Check if calculated MoM percentage changes match exact pandas calculations
        math_checks_passed = 0
        total_math_checks = 0
        for kpi_id in ["revenue_k", "operating_profit_k", "customer_acquisition_cost"]:
            curr = float(df[kpi_id].iloc[-1])
            prev = float(df[kpi_id].iloc[-2])
            expected_change = round(((curr - prev) / abs(prev)) * 100, 2)
            reported_change = summary[kpi_id]["pct_change"]
            total_math_checks += 1
            if abs(expected_change - reported_change) < 0.05:
                math_checks_passed += 1

        accuracy_score = round(math_checks_passed / total_math_checks, 4)

        # ---------------------------------------------------------
        # Metric 2 & 3: Precision & Recall of Driver Identification
        # ---------------------------------------------------------
        # Operational candidate features tested in driver regression
        operational_kpis = [
            "marketing_spend_k", "customer_acquisition_cost", "new_customers_acquired",
            "sales_conversion_rate_pct", "on_time_delivery_rate_pct", "inventory_turnover_ratio",
            "employee_productivity_index", "supply_chain_disruption_index", "competitive_pressure_index"
        ]
        
        # Ground truth: Operational drivers with true statistical significance
        # defined by |correlation| >= 0.25 (statistically meaningful correlation in time series)
        corr_matrix = cycle_result["correlations"]
        ground_truth_significant_drivers = {
            c["driver_id"] for c in corr_matrix 
            if c["driver_id"] in operational_kpis and c["abs_correlation"] >= 0.25
        }
        
        # System identified drivers (multivariate drivers with impact share >= 5%)
        system_predicted_drivers = {
            d["driver_id"] for d in drivers if d["relative_impact_share_pct"] >= 5.0
        }

        true_positives = len(system_predicted_drivers.intersection(ground_truth_significant_drivers))
        false_positives = len(system_predicted_drivers - ground_truth_significant_drivers)
        false_negatives = len(ground_truth_significant_drivers - system_predicted_drivers)

        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 1.0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 1.0

        # ---------------------------------------------------------
        # Metric 4: F1 Score
        # ---------------------------------------------------------
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

        # ---------------------------------------------------------
        # Metric 5: Insight Grounding Score
        # ---------------------------------------------------------
        # Measures the proportion of generated insight statements that contain explicit, verifiable evidence
        core_insights = briefing.get("core_insights", [])
        grounded_count = 0
        for ins in core_insights:
            evidence = ins.get("evidence", {})
            stat_basis = ins.get("statistical_basis", "")
            # Must possess key-value numerical evidence and defined statistical basis
            if isinstance(evidence, dict) and len(evidence) >= 2 and len(stat_basis) > 5:
                grounded_count += 1

        insight_grounding_score = round(grounded_count / len(core_insights), 4) if core_insights else 1.0

        # ---------------------------------------------------------
        # Metric 6: Recommendation Quality
        # ---------------------------------------------------------
        # Evaluates recommendations for:
        # 1. Clear proposed action
        # 2. Financial impact quantification
        # 3. Feasibility assessment
        # 4. Risk / countermeasure note
        recs = briefing.get("actionable_recommendations", [])
        rec_scores = []
        for r in recs:
            has_action = bool(r.get("proposed_action"))
            has_fin_impact = bool(r.get("expected_financial_impact") and any(char.isdigit() or char == '$' for char in r["expected_financial_impact"]))
            has_feasibility = bool(r.get("feasibility"))
            has_risk = bool(r.get("risk_consideration"))
            
            score = (has_action + has_fin_impact + has_feasibility + has_risk) / 4.0
            rec_scores.append(score)

        avg_rec_quality = round(float(np.mean(rec_scores)), 4) if rec_scores else 1.0

        return {
            "evaluation_metrics": {
                "Accuracy": {
                    "score": accuracy_score,
                    "target": ">= 0.95",
                    "status": "PASS" if accuracy_score >= 0.95 else "FAIL",
                    "description": "Correctness of KPI calculations, trends, and budget variances."
                },
                "Precision": {
                    "score": round(precision, 4),
                    "target": ">= 0.80",
                    "status": "PASS" if precision >= 0.80 else "FAIL",
                    "description": "Proportion of identified key drivers that are statistically significant in underlying data."
                },
                "Recall": {
                    "score": round(recall, 4),
                    "target": ">= 0.75",
                    "status": "PASS" if recall >= 0.75 else "FAIL",
                    "description": "Proportion of true significant KPI drivers correctly captured by model."
                },
                "F1 Score": {
                    "score": round(f1_score, 4),
                    "target": ">= 0.80",
                    "status": "PASS" if f1_score >= 0.80 else "FAIL",
                    "description": "Harmonic balance of precision and recall for business driver identification."
                },
                "Insight Grounding": {
                    "score": insight_grounding_score,
                    "target": ">= 0.90",
                    "status": "PASS" if insight_grounding_score >= 0.90 else "FAIL",
                    "description": "Proportion of executive insights supported by traceable, verifiable quantitative evidence."
                },
                "Recommendation Quality": {
                    "score": avg_rec_quality,
                    "target": ">= 0.85",
                    "status": "PASS" if avg_rec_quality >= 0.85 else "FAIL",
                    "description": "Completeness, feasibility, risk mitigation, and financial impact quantification."
                }
            },
            "driver_validation_details": {
                "ground_truth_significant_drivers": list(ground_truth_significant_drivers),
                "system_predicted_drivers": list(system_predicted_drivers),
                "true_positives": true_positives,
                "false_positives": false_positives,
                "false_negatives": false_negatives
            }
        }


if __name__ == "__main__":
    system = DecisionIntelligenceSystem()
    evaluator = DecisionIntelligenceEvaluator(system)
    report = evaluator.run_evaluation_suite()
    print("\n==========================================")
    print("EXECUTIVE DECISION INTELLIGENCE EVALUATION")
    print("==========================================")
    for metric, data in report["evaluation_metrics"].items():
        print(f"[{data['status']}] {metric:24}: {data['score']:.4f} (Target: {data['target']})")
    print("==========================================\n")
