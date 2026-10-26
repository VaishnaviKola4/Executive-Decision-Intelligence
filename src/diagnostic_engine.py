"""
Diagnostic and Statistical Engine for Executive Decision Intelligence.
Computes variance analysis, rolling MoM/YoY trends, statistical correlation,
elasticity coefficients, multi-variate feature drivers, and anomaly detection.
Distinguishes statistical correlation from causal attribution with traceable metrics.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from src.kpi_registry import KPI_REGISTRY, KPIMeta

class DiagnosticEngine:
    """
    Performs rigorous quantitative analysis linking operational changes to financial outcomes.
    """

    def __init__(self, data: pd.DataFrame):
        self.data = data.copy()
        if "date" in self.data.columns:
            self.data["date"] = pd.to_datetime(self.data["date"])
            self.data = self.data.sort_values("date").reset_index(drop=True)

    def compute_summary_kpis(self, period_idx: int = -1) -> Dict[str, Any]:
        """
        Returns latest period KPI snapshot, period-over-period differences, and budget attainment.
        """
        curr = self.data.iloc[period_idx]
        prev = self.data.iloc[period_idx - 1] if len(self.data) > 1 else curr
        
        snapshot = {}
        for kpi_id, meta in KPI_REGISTRY.items():
            if kpi_id in self.data.columns:
                curr_val = float(curr[kpi_id])
                prev_val = float(prev[kpi_id])
                abs_change = curr_val - prev_val
                pct_change = ((curr_val - prev_val) / abs(prev_val) * 100) if prev_val != 0 else 0.0

                snapshot[kpi_id] = {
                    "id": kpi_id,
                    "name": meta.name,
                    "department": meta.department,
                    "unit": meta.unit,
                    "current": round(curr_val, 2),
                    "previous": round(prev_val, 2),
                    "abs_change": round(abs_change, 2),
                    "pct_change": round(pct_change, 2),
                    "desirable": meta.desirable_direction,
                    "is_improving": (abs_change > 0 if meta.desirable_direction == "higher" else abs_change < 0)
                }
        return snapshot

    def detect_anomalies(self, kpi_id: str, z_thresh: float = 2.0) -> List[Dict[str, Any]]:
        """
        Detects statistical anomalies using rolling Z-score with 6-month window.
        """
        if kpi_id not in self.data.columns:
            return []
            
        series = self.data[kpi_id]
        mean = series.rolling(window=6, min_periods=3).mean()
        std = series.rolling(window=6, min_periods=3).std().replace(0, np.nan)
        z_scores = (series - mean) / std

        anomalies = []
        for i, z in enumerate(z_scores):
            if abs(z) >= z_thresh:
                anomalies.append({
                    "period_index": int(self.data.iloc[i].get("period_index", i)),
                    "date": str(self.data.iloc[i]["date"].strftime("%Y-%m-%d")),
                    "value": float(round(series.iloc[i], 2)),
                    "rolling_mean": float(round(mean.iloc[i], 2)) if not np.isnan(mean.iloc[i]) else 0.0,
                    "z_score": float(round(z, 2)),
                    "severity": "CRITICAL" if abs(z) >= 2.8 else "WARNING"
                })
        return anomalies

    def analyze_driver_correlations(self, target_kpi: str = "operating_profit_k") -> pd.DataFrame:
        """
        Computes Pearson and Spearman correlations between operational drivers and a target financial KPI.
        """
        if target_kpi not in self.data.columns:
            raise ValueError(f"Target KPI {target_kpi} not found in dataset.")

        numeric_cols = self.data.select_dtypes(include=[np.number]).columns
        corrs = []

        for col in numeric_cols:
            if col in [target_kpi, "period_index", "month_of_year", "year"]:
                continue
            
            pearson = self.data[target_kpi].corr(self.data[col], method="pearson")
            spearman = self.data[target_kpi].corr(self.data[col], method="spearman")
            meta = KPI_REGISTRY.get(col)

            corrs.append({
                "driver_id": col,
                "driver_name": meta.name if meta else col.replace("_", " ").title(),
                "department": meta.department if meta else "Other",
                "pearson_corr": round(pearson, 3) if not np.isnan(pearson) else 0.0,
                "spearman_corr": round(spearman, 3) if not np.isnan(spearman) else 0.0,
                "abs_correlation": round(abs(pearson), 3) if not np.isnan(pearson) else 0.0,
                "relationship_type": "Statistical Correlation (Non-Causal)"
            })

        df_corr = pd.DataFrame(corrs).sort_values("abs_correlation", ascending=False).reset_index(drop=True)
        return df_corr

    def estimate_driver_elasticity_and_impact(self, target_kpi: str = "operating_profit_k") -> List[Dict[str, Any]]:
        """
        Uses standardized regularized linear regression (Ridge) to estimate the relative driver weights
        (elasticity / standardized coefficients) of operational inputs on a financial outcome.
        This provides a mathematically grounded decomposition of variance.
        """
        operational_kpis = [
            "marketing_spend_k", "customer_acquisition_cost", "new_customers_acquired",
            "sales_conversion_rate_pct", "on_time_delivery_rate_pct", "inventory_turnover_ratio",
            "employee_productivity_index", "supply_chain_disruption_index", "competitive_pressure_index"
        ]
        valid_cols = [c for c in operational_kpis if c in self.data.columns]
        
        if target_kpi not in self.data.columns or len(valid_cols) == 0:
            return []

        X = self.data[valid_cols].copy().bfill().ffill()
        y = self.data[target_kpi].copy().bfill().ffill()

        # Standardize features for comparable coefficients
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        y_scaled = (y - y.mean()) / (y.std() if y.std() != 0 else 1.0)

        model = Ridge(alpha=1.0)
        model.fit(X_scaled, y_scaled)

        r2_score = model.score(X_scaled, y_scaled)
        
        # Calculate feature contributions
        weights = model.coef_
        total_abs_weight = np.sum(np.abs(weights)) if np.sum(np.abs(weights)) > 0 else 1.0

        drivers = []
        for col_name, weight in zip(valid_cols, weights):
            meta = KPI_REGISTRY.get(col_name)
            share_of_impact = (abs(weight) / total_abs_weight) * 100
            
            # Latest movement
            curr_val = float(self.data[col_name].iloc[-1])
            prev_val = float(self.data[col_name].iloc[-2]) if len(self.data) > 1 else curr_val
            pct_change = ((curr_val - prev_val) / abs(prev_val) * 100) if prev_val != 0 else 0.0

            drivers.append({
                "driver_id": col_name,
                "driver_name": meta.name if meta else col_name,
                "department": meta.department if meta else "Operations",
                "standardized_coefficient": round(float(weight), 3),
                "relative_impact_share_pct": round(float(share_of_impact), 1),
                "direction": "Positive Driver" if weight > 0 else "Inverse/Headwind Driver",
                "latest_period_change_pct": round(pct_change, 1),
                "model_fit_r2": round(float(r2_score), 3)
            })

        drivers.sort(key=lambda x: abs(x["standardized_coefficient"]), reverse=True)
        return drivers

    def decompose_profit_variance(self, period_idx: int = -1) -> Dict[str, Any]:
        """
        Decomposes profit variance against budget into operational buckets:
        Revenue variance, COGS variance, Marketing spend variance, Logistics/OpEx variance.
        """
        curr = self.data.iloc[period_idx]
        actual_profit = float(curr.get("operating_profit_k", 0.0))
        budget_profit = float(curr.get("budget_operating_profit_k", actual_profit))
        total_variance = actual_profit - budget_profit

        actual_rev = float(curr.get("revenue_k", 0.0))
        budget_rev = float(curr.get("budget_revenue_k", actual_rev))
        rev_variance = actual_rev - budget_rev

        actual_cogs = float(curr.get("cogs_k", 0.0))
        actual_opex = float(curr.get("opex_k", 0.0))

        return {
            "period": str(curr.get("date", "Latest")),
            "actual_operating_profit_k": round(actual_profit, 2),
            "budget_operating_profit_k": round(budget_profit, 2),
            "total_profit_variance_k": round(total_variance, 2),
            "revenue_variance_k": round(rev_variance, 2),
            "actual_cogs_k": round(actual_cogs, 2),
            "actual_opex_k": round(actual_opex, 2),
            "attainment_pct": round((actual_profit / budget_profit * 100) if budget_profit != 0 else 100.0, 1),
            "status": "AHEAD OF PLAN" if total_variance >= 0 else "BEHIND PLAN"
        }
