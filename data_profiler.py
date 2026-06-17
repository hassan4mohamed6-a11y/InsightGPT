"""
data_profiler.py
Handles automatic profiling of an uploaded dataframe:
- basic stats
- missing values
- data types
- correlations
- simple outlier flags

This module produces a single dictionary ("profile") that is later
converted into a compact text summary for the LLM, and also used
directly to drive the charts.
"""

import pandas as pd
import numpy as np


def profile_dataframe(df: pd.DataFrame) -> dict:
    """Generate a structured profile of the dataframe."""

    profile = {}

    profile["shape"] = {"rows": df.shape[0], "columns": df.shape[1]}
    profile["columns"] = list(df.columns)

    # Data types
    profile["dtypes"] = {col: str(dtype) for col, dtype in df.dtypes.items()}

    # Missing values
    missing = df.isnull().sum()
    missing_pct = (missing / len(df) * 100).round(2)
    profile["missing"] = {
        col: {"count": int(missing[col]), "pct": float(missing_pct[col])}
        for col in df.columns
        if missing[col] > 0
    }

    # Numeric summary
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    profile["numeric_columns"] = numeric_cols

    numeric_summary = {}
    for col in numeric_cols:
        series = df[col].dropna()
        if len(series) == 0:
            continue
        numeric_summary[col] = {
            "mean": float(series.mean()),
            "median": float(series.median()),
            "std": float(series.std()),
            "min": float(series.min()),
            "max": float(series.max()),
        }
    profile["numeric_summary"] = numeric_summary

    # Categorical summary
    categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    profile["categorical_columns"] = categorical_cols

    categorical_summary = {}
    for col in categorical_cols:
        top_values = df[col].value_counts().head(5).to_dict()
        categorical_summary[col] = {
            "unique_count": int(df[col].nunique()),
            "top_values": {str(k): int(v) for k, v in top_values.items()},
        }
    profile["categorical_summary"] = categorical_summary

    # Correlations (numeric only)
    if len(numeric_cols) >= 2:
        corr_matrix = df[numeric_cols].corr(numeric_only=True)
        strong_pairs = []
        for i, col_a in enumerate(numeric_cols):
            for col_b in numeric_cols[i + 1:]:
                corr_val = corr_matrix.loc[col_a, col_b]
                if pd.notna(corr_val) and abs(corr_val) >= 0.5:
                    strong_pairs.append(
                        {"pair": [col_a, col_b], "correlation": round(float(corr_val), 3)}
                    )
        profile["strong_correlations"] = sorted(
            strong_pairs, key=lambda x: abs(x["correlation"]), reverse=True
        )
    else:
        profile["strong_correlations"] = []

    # Simple outlier flags using IQR method
    outliers = {}
    for col in numeric_cols:
        series = df[col].dropna()
        if len(series) < 4:
            continue
        q1, q3 = series.quantile(0.25), series.quantile(0.75)
        iqr = q3 - q1
        lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        outlier_count = int(((series < lower) | (series > upper)).sum())
        if outlier_count > 0:
            outliers[col] = outlier_count
    profile["outliers"] = outliers

    return profile


def profile_to_text(profile: dict) -> str:
    """Convert the structured profile into a compact text block for the LLM prompt."""

    lines = []
    lines.append(f"Dataset shape: {profile['shape']['rows']} rows, {profile['shape']['columns']} columns")
    lines.append(f"Columns: {', '.join(profile['columns'])}")

    if profile["missing"]:
        lines.append("\nMissing values:")
        for col, info in profile["missing"].items():
            lines.append(f"- {col}: {info['count']} missing ({info['pct']}%)")

    if profile["numeric_summary"]:
        lines.append("\nNumeric column statistics:")
        for col, stats in profile["numeric_summary"].items():
            lines.append(
                f"- {col}: mean={stats['mean']:.2f}, median={stats['median']:.2f}, "
                f"std={stats['std']:.2f}, min={stats['min']:.2f}, max={stats['max']:.2f}"
            )

    if profile["categorical_summary"]:
        lines.append("\nCategorical column summaries:")
        for col, info in profile["categorical_summary"].items():
            top_str = ", ".join(f"{k} ({v})" for k, v in info["top_values"].items())
            lines.append(f"- {col}: {info['unique_count']} unique values, top: {top_str}")

    if profile["strong_correlations"]:
        lines.append("\nStrong correlations (|r| >= 0.5):")
        for item in profile["strong_correlations"]:
            lines.append(f"- {item['pair'][0]} vs {item['pair'][1]}: r = {item['correlation']}")

    if profile["outliers"]:
        lines.append("\nPotential outliers (IQR method):")
        for col, count in profile["outliers"].items():
            lines.append(f"- {col}: {count} potential outlier(s)")

    return "\n".join(lines)
