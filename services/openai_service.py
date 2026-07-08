import json
import os

from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()


class OpenAIService:

    def __init__(self):

        self.client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        )

        self.model_name = os.getenv("AZURE_OPENAI_DEPLOYMENT")

    # -------------------------------------------------------
    # Generate Executive Summary
    # -------------------------------------------------------

    def generate_summary(
        self,
        dataframe,
        report_title,
    ):

        prompt = f"""
You are a professional Business Intelligence Analyst.

Report Title:
{report_title}

Dataset:

{dataframe.to_csv(index=False)}

Generate:

1. Executive Summary

2. Business Insights

3. Recommendations

Return the response in Markdown.
"""

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert business analyst."
                },
                {
                    "role": "user",
                    "content": prompt
                },
            ],
            temperature=0.3,
        )

        return response.choices[0].message.content

    # -------------------------------------------------------
    # Suggest Dashboard Items
    # -------------------------------------------------------

    def suggest_dashboard_items(
        self,
        dataframe,
    ):
        """
        Analyze the dataset and suggest useful dashboard items.

        Returns

        [
            "Total Revenue",
            "Revenue by Region",
            "Monthly Revenue Trend",
            ...
        ]
        """

        columns = dataframe.columns.tolist()

        dtypes = {
            column: str(dtype)
            for column, dtype in dataframe.dtypes.items()
        }

        prompt = f"""
You are an expert Power BI Dashboard Designer.

Dataset Columns:

{columns}

Column Data Types:

{dtypes}

Your task:

Analyze the dataset and suggest the BEST dashboard items.

Rules

1. Use ONLY available columns.

2. Never invent columns.

3. Suggest 8 to 12 dashboard items.

4. Include

- KPI metrics
- Trends
- Comparisons
- Distributions
- Top/Bottom analysis
- Correlations (if possible)

5. Make suggestions suitable for THIS dataset only.

6. Return ONLY JSON.

Example

[
    "Total Revenue",
    "Average Revenue",
    "Revenue by Region",
    "Revenue Trend",
    "Region Distribution",
    "Top Customers",
    "Profit Distribution",
    "Revenue vs Profit"
]
"""

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert BI dashboard planner. "
                        "Return ONLY JSON."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0,
        )

        content = self._clean_json(
            response.choices[0].message.content
        )

        return json.loads(content)

    # -------------------------------------------------------
    # Generate Chart Plan
    # -------------------------------------------------------

    def generate_chart_plan(
        self,
        dataframe,
        dashboard_items,
    ):
        """
        Convert dashboard items into chart specifications.
        """

        columns = dataframe.columns.tolist()

        dtypes = {
            column: str(dtype)
            for column, dtype in dataframe.dtypes.items()
        }

        prompt = f"""
You are an expert Power BI Dashboard Designer.

Dataset Columns

{columns}

Column Types

{dtypes}

Dashboard Items

{dashboard_items}

For EACH dashboard item choose the best visualization.

Supported chart types

- bar
- column
- line
- pie
- scatter
- kpi

Rules

1. Use ONLY dataset columns.

2. Never invent columns.

3. Every object must contain

chart_type

x

y

title

4. KPI

x = null

y = numeric column

5. Pie

y = null

6. Scatter

Both x and y must be numeric.

7. Skip impossible dashboard items.

8. Return ONLY JSON.

Example

[
    {{
        "chart_type":"bar",
        "x":"Region",
        "y":"Revenue",
        "title":"Revenue by Region"
    }},
    {{
        "chart_type":"line",
        "x":"Month",
        "y":"Revenue",
        "title":"Monthly Revenue Trend"
    }},
    {{
        "chart_type":"pie",
        "x":"Region",
        "y":null,
        "title":"Region Distribution"
    }},
    {{
        "chart_type":"kpi",
        "x":null,
        "y":"Revenue",
        "title":"Total Revenue"
    }}
]
"""

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert BI dashboard planner. "
                        "Return ONLY JSON."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0,
        )

        content = self._clean_json(
            response.choices[0].message.content
        )

        return json.loads(content)

    # -------------------------------------------------------
    # Helper
    # -------------------------------------------------------

    def _clean_json(
        self,
        text,
    ):

        text = text.strip()

        if text.startswith("```json"):
            text = text.replace("```json", "")

        if text.startswith("```"):
            text = text.replace("```", "")

        return text.strip()
