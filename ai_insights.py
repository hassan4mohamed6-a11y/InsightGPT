"""
ai_insights.py
Sends the data profile summary to the OpenAI API and asks for a
plain-English business report: key trends, anomalies, and
actionable recommendations.
"""

import os
from openai import OpenAI

SYSTEM_PROMPT = """You are a senior data analyst who writes clear, professional, \
business-friendly reports. You will be given a statistical profile of a dataset \
(not the raw rows). Based only on this profile, write a structured report with \
these sections:

1. Executive Summary (2-3 sentences)
2. Key Trends & Patterns (bullet points)
3. Notable Anomalies / Outliers (bullet points, or state "No significant anomalies detected" if none)
4. Actionable Recommendations (3-5 bullet points)

Rules:
- Be specific and reference actual column names and numbers from the profile.
- Do not invent data that isn't in the profile.
- Write for a non-technical business audience.
- Keep the total report under 400 words.
- Use plain section headers exactly as listed above, no markdown symbols like ### or **.
"""


def get_client(api_key: str = None) -> OpenAI:
    """
    Create an OpenAI client.
    If api_key is not passed explicitly, it falls back to the
    OPENAI_API_KEY environment variable.
    """
    key = api_key or os.getenv("OPENAI_API_KEY")
    if not key:
        raise ValueError(
            "No OpenAI API key found. Pass it directly or set the "
            "OPENAI_API_KEY environment variable."
        )
    return OpenAI(api_key=key)


def generate_insights(profile_text: str, api_key: str = None, model: str = "gpt-4.1-mini") -> str:
    """
    Send the profile text to the OpenAI API and return the generated
    business report as plain text.
    """
    client = get_client(api_key)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Here is the data profile:\n\n{profile_text}"},
        ],
        temperature=0.4,
    )

    return response.choices[0].message.content.strip()
