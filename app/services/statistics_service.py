import pandas as pd


class StatisticsService:

    @staticmethod
    def generate_statistics(df: pd.DataFrame):

        report = {}

        report["numeric_summary"] = {}

        numeric_columns = df.select_dtypes(include="number").columns

        for column in numeric_columns:

            report["numeric_summary"][column] = {

                "sum": round(df[column].sum(), 2),

                "mean": round(df[column].mean(), 2),

                "max": round(df[column].max(), 2),

                "min": round(df[column].min(), 2),

                "median": round(df[column].median(), 2),

                "std": round(df[column].std(), 2)

            }

        return report