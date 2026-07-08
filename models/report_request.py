"""Structured representation of a parsed report request."""

from enum import Enum
from typing import List, Optional

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field


class ChartType(str, Enum):
    BAR = "bar"
    PIE = "pie"
    LINE = "line"
    SCATTER = "scatter"


class ChartSpec(BaseModel):
    chart_type: ChartType
    title: str
    x_column: Optional[str] = None
    y_column: Optional[str] = None


class ReportRequest(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    raw_prompt: str
    report_title: str = Field(default="Business Report")
    dataframe: pd.DataFrame
    charts: List[ChartSpec] = Field(default_factory=list)
    include_powerbi: bool = True
    include_pdf: bool = True
