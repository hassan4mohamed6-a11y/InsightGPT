"""
chart_generator.py
Generates a set of standard exploratory charts from a dataframe profile:
- histograms for numeric columns
- bar charts for top categorical columns
- a correlation heatmap (if 2+ numeric columns)

Each chart is returned as a matplotlib Figure so the Streamlit app
can render it, and also saved to disk so it can be embedded in the
exported Word report.
"""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

sns.set_theme(style="whitegrid")

MAX_NUMERIC_CHARTS = 6
MAX_CATEGORICAL_CHARTS = 4


def generate_charts(df: pd.DataFrame, profile: dict, output_dir: str) -> list:
    """
    Generate charts and save them as PNG files.
    Returns a list of dicts: {"title": str, "path": str}
    """
    os.makedirs(output_dir, exist_ok=True)
    chart_paths = []

    numeric_cols = profile["numeric_columns"][:MAX_NUMERIC_CHARTS]
    categorical_cols = profile["categorical_columns"][:MAX_CATEGORICAL_CHARTS]

    # Histograms for numeric columns
    for col in numeric_cols:
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.histplot(df[col].dropna(), kde=True, ax=ax, color="#1A5276")
        ax.set_title(f"Distribution of {col}")
        ax.set_xlabel(col)
        ax.set_ylabel("Frequency")
        fig.tight_layout()

        path = os.path.join(output_dir, f"hist_{col}.png")
        fig.savefig(path, dpi=150)
        plt.close(fig)
        chart_paths.append({"title": f"Distribution of {col}", "path": path})

    # Bar charts for categorical columns
    for col in categorical_cols:
        top_values = df[col].value_counts().head(10)
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.barplot(x=top_values.values, y=top_values.index.astype(str), ax=ax, color="#2E86C1")
        ax.set_title(f"Top values in {col}")
        ax.set_xlabel("Count")
        ax.set_ylabel(col)
        fig.tight_layout()

        path = os.path.join(output_dir, f"bar_{col}.png")
        fig.savefig(path, dpi=150)
        plt.close(fig)
        chart_paths.append({"title": f"Top values in {col}", "path": path})

    # Correlation heatmap
    if len(profile["numeric_columns"]) >= 2:
        corr = df[profile["numeric_columns"]].corr(numeric_only=True)
        fig, ax = plt.subplots(figsize=(6, 5))
        sns.heatmap(corr, annot=True, fmt=".2f", cmap="Blues", ax=ax, cbar=True)
        ax.set_title("Correlation Heatmap")
        fig.tight_layout()

        path = os.path.join(output_dir, "correlation_heatmap.png")
        fig.savefig(path, dpi=150)
        plt.close(fig)
        chart_paths.append({"title": "Correlation Heatmap", "path": path})

    return chart_paths
