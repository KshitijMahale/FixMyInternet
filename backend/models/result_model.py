from pydantic import BaseModel
from typing import Dict, Optional


class PingTestResponse(BaseModel):
    test: str
    results: Dict[str, Optional[float]]

class DNSTestResponse(BaseModel):
    test: str
    results: Dict[str, Optional[float]]

class PacketLossResponse(BaseModel):
    packets_sent: int
    packets_received: int
    packets_lost: int
    packet_loss_percent: float