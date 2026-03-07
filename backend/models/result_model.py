from pydantic import BaseModel
from typing import Dict, Optional


class PingTestResponse(BaseModel):
    test: str
    results: Dict[str, Optional[float]]

class DNSTestResponse(BaseModel):
    test: str
    results: Dict[str, Optional[float]]