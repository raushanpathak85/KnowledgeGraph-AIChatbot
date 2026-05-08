from typing import Optional, Dict, Any
from pydantic import BaseModel


class ReportIngestRequest(BaseModel):
    title: str
    content: str
    source_url: Optional[str] = None
    author: Optional[str] = None
    sector: Optional[str] = None
    published_date: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None