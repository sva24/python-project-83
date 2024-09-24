from dataclasses import dataclass
from typing import Optional


@dataclass
class Url:
    name: str
    created_at: Optional[str] = None
    id: Optional[int] = None
    url_id: Optional[int] = None
    status_code: Optional[int] = None
    h1: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    last_checked: Optional[str] = None
