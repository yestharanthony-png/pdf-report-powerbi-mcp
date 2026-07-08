import os
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


class ChartService:

    @staticmethod
    def generate(
        df: pd.DataFrame,
        chart_plan: list,
        run_id: str,
    ):

        chart_folder = Path(f"generated/charts/{run_id}")
        chart_folder.mkdir(parents=True, exist_ok=True)

        chart_paths = []

        for index, chart in enumerate(chart_plan):

            try:

                chart_type = chart["chart_type"].lower()

                x = chart.get("x")
                y = chart.get("y")
                title = chart.get("title", f"Chart {index+1}")

                filename = f"{chart_type}_{index+1}.png"
                filepath = chart_folder / filename

                plt.figure(figsize=(8, 5))

                # ---------------- BAR ----------------

                if chart_type == "bar":

                    grouped = (
                        df.groupby(x)[y]
                        .sum()
                        .sort_values(ascending=False)
                    )

                    grouped.plot(kind="bar")

                # ---------------- COLUMN ----------------

                elif chart_type == "column":

                    grouped = (
                        df.groupby(x)[y]
                        .sum()
                    )

                    grouped.plot(kind="bar")

                # ---------------- LINE ----------------

                elif chart_type == "line":

                    grouped = (
                        df.groupby(x)[y]
                        .sum()
                    )

                    grouped.plot(kind="line", marker="o")

                # ---------------- PIE ----------------

                elif chart_type == "pie":

                    grouped = (
                        df.groupby(x)
                        .size()
                    )

                    grouped.plot(
                        kind="pie",
                        autopct="%1.1f%%"
                    )

                    plt.ylabel("")

                # ---------------- SCATTER ----------------

                elif chart_type == "scatter":

                    plt.scatter(df[x], df[y])

                    plt.xlabel(x)
                    plt.ylabel(y)

                # ---------------- HISTOGRAM ----------------

                elif chart_type == "histogram":

                    df[x].plot(kind="hist", bins=15)

                # ---------------- KPI ----------------

                elif chart_type == "kpi":

                    plt.text(
                        0.5,
                        0.5,
                        f"{title}\n\n{df[y].sum():,.2f}",
                        fontsize=20,
                        ha="center",
                        va="center",
                    )

                    plt.axis("off")

                else:

                    print(f"Skipping unsupported chart: {chart_type}")

                    plt.close()

                    continue

                plt.title(title)

                plt.tight_layout()

                plt.savefig(filepath)

                plt.close()

                chart_paths.append(str(filepath))

            except Exception as e:

                print(f"Chart generation failed: {e}")

                plt.close()

        return chart_paths