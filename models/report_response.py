"""Response returned by the MCP tool to the client/agent."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class ReportResponse(BaseModel):
    status: str
    executive_summary: str
    insights: List[str]
    recommendations: List[str]
    pdf_path: str
    powerbi_dashboard_url: Optional[str] = None
    powerbi_dataset_id: Optional[str] = None
    data_preview: List[Dict[str, Any]] = []
    message: str