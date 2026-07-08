import pandas as pd


class ValidationService:

    @staticmethod
    def analyze(df: pd.DataFrame):

        report = {

            "rows": df.shape[0],

            "columns": df.shape[1],

            "column_names": list(df.columns),

            "missing_values": df.isnull().sum().sum(),

            "duplicate_rows": df.duplicated().sum(),

            "data_types": {
                col: str(dtype)
                for col, dtype in df.dtypes.items()
            },

            "numeric_columns": list(
                df.select_dtypes(include="number").columns
            ),

            "text_columns": list(
                df.select_dtypes(include="object").columns
            )

        }

        return report