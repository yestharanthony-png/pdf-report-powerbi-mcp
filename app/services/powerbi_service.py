"""
Real Power BI integration:
  1) Push dataset creation + row streaming (client credentials / MSAL)
  2) Report export-to-image (requires Premium capacity), used to embed
     a live dashboard screenshot into the generated PDF.

Workflow assumption: you build the report/visuals ONCE manually in
Power BI (on top of the pushed dataset), save it with a known name,
and this service finds that report by name and exports its first page
as a PNG each time a new report is generated.
"""

import os
import time
from typing import Any, Dict, Optional

import msal
import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()

_AUTHORITY_TEMPLATE = "https://login.microsoftonline.com/{tenant_id}"
_SCOPE = ["https://analysis.windows.net/powerbi/api/.default"]
_API_BASE = "https://api.powerbi.com/v1.0/myorg"


class PowerBIAuthError(RuntimeError):
    """Raised when token acquisition fails (e.g. consent not granted)."""


class PowerBIAPIError(RuntimeError):
    """Raised when a Power BI REST API call fails."""


def _pandas_dtype_to_powerbi(dtype) -> str:
    kind = dtype.kind
    if kind in ("i", "u"):
        return "Int64"
    if kind == "f":
        return "Double"
    if kind == "b":
        return "bool"
    if kind == "M":
        return "DateTime"
    return "string"


def _slugify(text: str, max_len: int = 60) -> str:
    import re
    text = re.sub(r"[^a-zA-Z0-9\-_ ]", "", text).strip().lower()
    text = re.sub(r"\s+", "_", text)
    return text[:max_len] or "report"


class PowerBIService:
    """Handles auth, dataset push, and report export-to-image."""

    def __init__(self) -> None:
        self._client_id = os.getenv("POWERBI_CLIENT_ID")
        self._client_secret = os.getenv("POWERBI_CLIENT_SECRET")
        self._tenant_id = os.getenv("POWERBI_TENANT_ID")
        self._workspace_id = os.getenv("POWERBI_WORKSPACE_ID")

        missing = [
            name for name, val in [
                ("POWERBI_CLIENT_ID", self._client_id),
                ("POWERBI_CLIENT_SECRET", self._client_secret),
                ("POWERBI_TENANT_ID", self._tenant_id),
                ("POWERBI_WORKSPACE_ID", self._workspace_id),
            ] if not val
        ]
        if missing:
            raise PowerBIAuthError(f"Missing required env vars: {', '.join(missing)}")

        self._token: Optional[str] = None
        self._app = msal.ConfidentialClientApplication(
            client_id=self._client_id,
            client_credential=self._client_secret,
            authority=_AUTHORITY_TEMPLATE.format(tenant_id=self._tenant_id),
        )

    # ---------------------------------------------------------------
    # Auth
    # ---------------------------------------------------------------

    def authenticate(self) -> str:
        result = self._app.acquire_token_for_client(scopes=_SCOPE)
        if "access_token" not in result:
            error = result.get("error_description", result.get("error", "unknown error"))
            raise PowerBIAuthError(
                f"Failed to authenticate with Power BI. Details: {error}"
            )
        self._token = result["access_token"]
        return self._token

    def _headers(self) -> Dict[str, str]:
        if not self._token:
            self.authenticate()
        return {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
        }

    # ---------------------------------------------------------------
    # Push dataset (data ingestion)
    # ---------------------------------------------------------------

    def _build_table_schema(self, df: pd.DataFrame, table_name: str) -> Dict[str, Any]:
        columns = [
            {"name": str(col), "dataType": _pandas_dtype_to_powerbi(df[col].dtype)}
            for col in df.columns
        ]
        return {"name": table_name, "columns": columns}

    def ensure_dataset(self, df: pd.DataFrame, dataset_name: str) -> str:
        headers = self._headers()

        list_url = f"{_API_BASE}/groups/{self._workspace_id}/datasets"
        resp = requests.get(list_url, headers=headers, timeout=30)
        if resp.status_code == 200:
            for ds in resp.json().get("value", []):
                if ds.get("name") == dataset_name:
                    return ds["id"]

        table_name = "ReportData"
        payload = {
            "name": dataset_name,
            "defaultMode": "Push",
            "tables": [self._build_table_schema(df, table_name)],
        }
        create_url = f"{_API_BASE}/groups/{self._workspace_id}/datasets"
        resp = requests.post(create_url, headers=headers, json=payload, timeout=30)
        if resp.status_code not in (200, 201):
            raise PowerBIAPIError(f"Failed to create Power BI dataset: {resp.status_code} {resp.text}")
        return resp.json()["id"]

    def push_rows(self, df: pd.DataFrame, dataset_id: str, table_name: str = "ReportData", batch_size: int = 500) -> None:
        headers = self._headers()
        url = f"{_API_BASE}/groups/{self._workspace_id}/datasets/{dataset_id}/tables/{table_name}/rows"
        records = df.to_dict(orient="records")
        for start in range(0, len(records), batch_size):
            batch = records[start:start + batch_size]
            resp = requests.post(url, headers=headers, json={"rows": batch}, timeout=30)
            if resp.status_code not in (200, 201):
                raise PowerBIAPIError(f"Failed to push rows to Power BI: {resp.status_code} {resp.text}")

    def get_dashboard_url(self, dataset_id: str) -> str:
        return f"https://app.powerbi.com/groups/{self._workspace_id}/datasets/{dataset_id}/details"

    def publish(self, df: pd.DataFrame, report_title: str) -> Dict[str, str]:
        """Authenticate, ensure dataset exists, push rows, return dataset info."""
        self.authenticate()
        dataset_name = _slugify(report_title)
        dataset_id = self.ensure_dataset(df, dataset_name)
        self.push_rows(df, dataset_id)
        return {
            "dataset_id": dataset_id,
            "dashboard_url": self.get_dashboard_url(dataset_id),
        }

    # ---------------------------------------------------------------
    # Report lookup + export-to-image (requires Premium capacity)
    # ---------------------------------------------------------------

    def find_report_id_by_name(self, report_name: str) -> Optional[str]:
        """Find an existing Power BI report (built manually on the dataset) by name."""
        headers = self._headers()
        url = f"{_API_BASE}/groups/{self._workspace_id}/reports"
        resp = requests.get(url, headers=headers, timeout=30)
        if resp.status_code != 200:
            raise PowerBIAPIError(f"Failed to list reports: {resp.status_code} {resp.text}")

        for r in resp.json().get("value", []):
            if r.get("name") == report_name:
                return r["id"]
        return None

    def export_report_as_image(
        self,
        report_id: str,
        output_path: str,
        poll_interval_seconds: float = 2.0,
        timeout_seconds: float = 60.0,
    ) -> str:
        """
        Export the report's first page as a PNG using Power BI's
        Export-To API (Premium feature) and save it to output_path.
        Returns output_path on success.
        """
        headers = self._headers()
        start_url = f"{_API_BASE}/groups/{self._workspace_id}/reports/{report_id}/ExportTo"
        payload = {"format": "PNG"}

        resp = requests.post(start_url, headers=headers, json=payload, timeout=30)
        if resp.status_code not in (200, 202):
            raise PowerBIAPIError(f"Failed to start report export: {resp.status_code} {resp.text}")

        export_id = resp.json()["id"]
        status_url = f"{_API_BASE}/groups/{self._workspace_id}/reports/{report_id}/exports/{export_id}"

        elapsed = 0.0
        while elapsed < timeout_seconds:
            status_resp = requests.get(status_url, headers=headers, timeout=30)
            if status_resp.status_code != 200:
                raise PowerBIAPIError(f"Failed to poll export status: {status_resp.status_code} {status_resp.text}")

            status_data = status_resp.json()
            status = status_data.get("status")

            if status == "Succeeded":
                file_url = f"{status_url}/file"
                file_resp = requests.get(file_url, headers=self._headers(), timeout=60)
                if file_resp.status_code != 200:
                    raise PowerBIAPIError(f"Failed to download exported image: {file_resp.status_code}")
                with open(output_path, "wb") as f:
                    f.write(file_resp.content)
                return output_path

            if status == "Failed":
                raise PowerBIAPIError(f"Power BI export failed: {status_data}")

            time.sleep(poll_interval_seconds)
            elapsed += poll_interval_seconds

        raise PowerBIAPIError("Power BI export timed out.")

    def publish_and_export_screenshot(
        self,
        df: pd.DataFrame,
        report_title: str,
        output_path: str,
    ) -> Dict[str, Optional[str]]:
        """
        Full flow: push data, then (if a matching report already exists,
        built manually once in Power BI) export its screenshot as PNG.

        Returns dict with dataset_id, dashboard_url, and screenshot_path
        (screenshot_path is None if no matching report was found yet).
        """
        publish_result = self.publish(df, report_title)

        report_id = self.find_report_id_by_name(report_title)
        screenshot_path = None
        if report_id:
            screenshot_path = self.export_report_as_image(report_id, output_path)

        return {
            **publish_result,
            "screenshot_path": screenshot_path,
        }