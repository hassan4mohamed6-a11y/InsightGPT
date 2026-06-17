# 📊 InsightGPT — AI-Powered Data Analysis Assistant

InsightGPT lets you upload any CSV file and instantly get:
- Automated data profiling (missing values, types, stats, correlations, outliers)
- Auto-generated visualizations (histograms, bar charts, correlation heatmap)
- An AI-written business report explaining trends, anomalies, and recommendations — powered by the OpenAI API
- A downloadable Word report with all insights and charts embedded

---

## Demo Flow

1. Upload a CSV file
2. View an automatic data profile and key metrics
3. Browse auto-generated charts
4. Click "Generate AI Report" to get a plain-English analysis from GPT
5. Export everything as a polished Word document

---

## Tech Stack

| Component | Tool |
|---|---|
| UI | Streamlit |
| Data processing | Pandas, NumPy |
| Visualization | Matplotlib, Seaborn |
| AI insights | OpenAI API (GPT-4.1-mini) |
| Report export | python-docx |

---

## Project Structure

```
insightgpt/
├── app.py                # Main Streamlit application
├── data_profiler.py       # Dataset profiling logic (stats, missing values, correlations, outliers)
├── chart_generator.py     # Automatic chart generation
├── ai_insights.py          # OpenAI API integration for report generation
├── report_exporter.py     # Word (.docx) report builder
├── requirements.txt
└── .env.example
```

---

## Setup

1. Clone the repository and install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Add your OpenAI API key. Either:
   - Create a `.env` file based on `.env.example`, or
   - Paste it directly into the sidebar when running the app

3. Run the app:
   ```bash
   streamlit run app.py
   ```

4. Open `http://localhost:8501` in your browser

---

## How It Works

1. **Profiling** — `data_profiler.py` scans the uploaded dataframe for shape, types, missing values, numeric statistics, categorical distributions, strong correlations (|r| ≥ 0.5), and outliers (IQR method).
2. **Visualization** — `chart_generator.py` automatically builds histograms for numeric columns, bar charts for categorical columns, and a correlation heatmap.
3. **AI Insights** — `ai_insights.py` converts the profile into a compact text summary and sends it to the OpenAI API with a system prompt instructing the model to write a structured business report (Executive Summary, Key Trends, Anomalies, Recommendations).
4. **Export** — `report_exporter.py` parses the AI's report into sections and assembles a Word document with the dataset overview, insights, and embedded charts.

---

## Notes

- Your OpenAI API key is only used for the current session and is never stored or logged.
- Designed to work with any well-formed CSV — sales data, survey results, operational metrics, etc.

---

## License

This project was created for educational and portfolio purposes.
