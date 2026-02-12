from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class SheetJobRecord:
    job_id: str
    date_scraped: str
    source: str
    scraped_at_utc: str
    title: str
    company: Optional[str]
    location: Optional[str]
    posted: Optional[str]
    job_url: str
    apply_url: Optional[str] = None
    description: Optional[str] = None
    snipit: Optional[str] = None
    processed: Optional[str] = None