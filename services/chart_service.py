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

        output_folder = Path("generated/charts") / run_id
        output_folder.mkdir(parents=True, exist_ok=True)

        chart_paths = []

        for index, item in enumerate(chart_plan):

            chart_type = item.get("chart_type", "").lower()
            x = item.get("x")
            y = item.get("y")
            title = item.get("title", f"Chart {index + 1}")

            filepath = output_folder / f"chart_{index + 1}.png"

            # -------------------------
            # Validate columns
            # -------------------------

            if x and x not in df.columns:
                print(f"Skipping '{title}' - x column '{x}' not found.")
                continue

            if y and y not in df.columns:
                print(f"Skipping '{title}' - y column '{y}' not found.")
                continue

            plt.figure(figsize=(10, 6))

            try:

                # -------------------------
                # BAR
                # -------------------------
                if chart_type == "bar":

                    data = df[[x, y]].dropna()

                    grouped = (
                        data.groupby(x)[y]
                        .sum()
                        .sort_values(ascending=False)
                    )

                    grouped.plot(kind="bar")

                # -------------------------
                # COLUMN
                # -------------------------
                elif chart_type == "column":

                    data = df[[x, y]].dropna()

                    grouped = (
                        data.groupby(x)[y]
                        .sum()
                    )

                    grouped.plot(kind="bar")

                # -------------------------
                # LINE
                # -------------------------
                elif chart_type == "line":

                    data = df[[x, y]].dropna()

                    grouped = (
                        data.groupby(x)[y]
                        .sum()
                    )

                    grouped.plot(kind="line")

                # -------------------------
                # PIE
                # -------------------------
                elif chart_type == "pie":

                    counts = (
                        df[x]
                        .dropna()
                        .value_counts()
                    )

                    counts.plot(
                        kind="pie",
                        autopct="%1.1f%%",
                    )

                    plt.ylabel("")

                # -------------------------
                # SCATTER
                # -------------------------
                elif chart_type == "scatter":

                    if x is None or y is None:
                        continue

                    data = df[[x, y]].dropna()

                    data.plot(
                        kind="scatter",
                        x=x,
                        y=y,
                    )

                # -------------------------
                # KPI
                # -------------------------
                elif chart_type == "kpi":

                    if y is None:
                        continue

                    title_lower = title.lower()

                    if "count" in title_lower:
                        value = len(df)

                    elif "average" in title_lower:
                        value = df[y].mean()

                    elif "min" in title_lower:
                        value = df[y].min()

                    elif "max" in title_lower:
                        value = df[y].max()

                    elif "sum" in title_lower or "total" in title_lower:
                        value = df[y].sum()

                    else:
                        value = df[y].sum()

                    plt.axis("off")

                    plt.text(
                        0.5,
                        0.60,
                        f"{value:,.2f}",
                        fontsize=32,
                        ha="center",
                        weight="bold",
                    )

                    plt.text(
                        0.5,
                        0.35,
                        title,
                        fontsize=16,
                        ha="center",
                    )

                else:
                    print(f"Unsupported chart type: {chart_type}")
                    continue

                plt.title(title)
                plt.tight_layout()
                plt.savefig(filepath, dpi=300)
                plt.close()

                chart_paths.append(str(filepath))

            except Exception as exc:

                print(f"Error generating '{title}': {exc}")

                plt.close()

        return chart_paths