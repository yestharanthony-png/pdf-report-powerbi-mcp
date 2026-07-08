"""Small reusable helper functions."""

import re
import uuid
from datetime import datetime


def new_run_id() -> str:
    """Unique id used to namespace files/datasets generated for one request."""
    return uuid.uuid4().hex[:10]


def timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def slugify(text: str, max_len: int = 40) -> str:
    text = re.sub(r"[^a-zA-Z0-9\-_ ]", "", text).strip().lower()
    text = re.sub(r"\s+", "_", text)
    return text[:max_len] or "report"
