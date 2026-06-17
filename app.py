"""
app.py
InsightGPT — AI-Powered Data Analysis Assistant

Upload a CSV, get automatic data profiling, auto-generated charts,
and an AI-written business report explaining trends, anomalies,
and recommendations — powered by the OpenAI API.

Run with:
    streamlit run app.py
"""

import os
import tempfile
import streamlit as st
import pandas as pd
from dotenv import load_dotenv

from data_profiler import profile_dataframe, profile_to_text
from chart_generator import generate_charts
from ai_insights import generate_insights
from report_exporter import build_report

load_dotenv()

st.set_page_config(page_title="InsightGPT", page_icon="📊", layout="wide")

# ---------- Sidebar ----------
st.sidebar.title("📊 InsightGPT")
st.sidebar.markdown("AI-Powered Data Analysis Assistant")
st.sidebar.divider()

api_key_input = st.sidebar.text_input(
    "OpenAI API Key",
    type="password",
    value=os.getenv("OPENAI_API_KEY", ""),
    help="Your key is only used for this session and is never stored.",
)

model_choice = st.sidebar.selectbox(
    "Model",
    ["gpt-4.1-mini", "gpt-4.1", "gpt-4o-mini"],
    index=0,
)

st.sidebar.divider()
st.sidebar.caption("Built with Python, Streamlit, Pandas, and the OpenAI API.")

# ---------- Main ----------
st.title("📊 InsightGPT — AI Data Analysis Assistant")
st.markdown(
    "Upload a CSV file to automatically profile your data, generate visualizations, "
    "and receive an AI-written business report with trends, anomalies, and recommendations."
)

uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
    except Exception as e:
        st.error(f"Could not read this CSV file: {e}")
        st.stop()

    st.success(f"Loaded **{uploaded_file.name}** — {df.shape[0]} rows, {df.shape[1]} columns")

    with st.expander("Preview data", expanded=True):
        st.dataframe(df.head(20), use_container_width=True)

    # ---------- Profiling ----------
    with st.spinner("Profiling your data..."):
        profile = profile_dataframe(df)
        profile_text = profile_to_text(profile)

    col1, col2, col3 = st.columns(3)
    col1.metric("Rows", profile["shape"]["rows"])
    col2.metric("Columns", profile["shape"]["columns"])
    col3.metric("Missing Fields", sum(v["count"] for v in profile["missing"].values()))

    with st.expander("View full data profile"):
        st.text(profile_text)

    # ---------- Charts ----------
    st.subheader("📈 Visualizations")
    chart_dir = tempfile.mkdtemp()
    with st.spinner("Generating charts..."):
        chart_paths = generate_charts(df, profile, chart_dir)

    if chart_paths:
        chart_cols = st.columns(2)
        for i, chart in enumerate(chart_paths):
            with chart_cols[i % 2]:
                st.image(chart["path"], caption=chart["title"], use_container_width=True)
    else:
        st.info("No charts could be generated — the dataset may not have enough numeric or categorical columns.")

    # ---------- AI Insights ----------
    st.subheader("🤖 AI-Generated Insights")

    if st.button("Generate AI Report", type="primary"):
        if not api_key_input:
            st.error("Please enter your OpenAI API key in the sidebar first.")
        else:
            with st.spinner("Asking AI to analyze your data..."):
                try:
                    insights_text = generate_insights(
                        profile_text, api_key=api_key_input, model=model_choice
                    )
                    st.session_state["insights_text"] = insights_text
                except Exception as e:
                    st.error(f"Error generating insights: {e}")

    if "insights_text" in st.session_state:
        st.markdown(st.session_state["insights_text"])

        st.divider()
        st.subheader("📄 Export Report")

        if st.button("Build Word Report"):
            with st.spinner("Building your report..."):
                output_path = os.path.join(tempfile.mkdtemp(), "InsightGPT_Report.docx")
                build_report(
                    output_path=output_path,
                    dataset_name=uploaded_file.name,
                    profile=profile,
                    insights_text=st.session_state["insights_text"],
                    chart_paths=chart_paths,
                )
                with open(output_path, "rb") as f:
                    st.download_button(
                        "⬇️ Download Word Report",
                        data=f.read(),
                        file_name="InsightGPT_Report.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    )
else:
    st.info("👆 Upload a CSV file to get started.")
