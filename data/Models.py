# data/models.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class AggResult:
    ip: str
    port: int
    service: Optional[str] = None
    location: Optional[str] = None
    asn: Optional[str] = None
    banner: Optional[str] = None
    domain: Optional[str] = None
    date: Optional[str] = None
    extra: Optional[str] = None
    isUnseen: Optional[bool] = None