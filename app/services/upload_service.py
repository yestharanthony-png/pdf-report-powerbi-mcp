import pandas as pd


class UploadService:

    @staticmethod
    def read_file(file_path: str):

        if file_path.endswith(".csv"):
            return pd.read_csv(file_path)

        elif file_path.endswith(".xlsx"):
            return pd.read_excel(file_path)

        else:
            raise Exception("Unsupported File")