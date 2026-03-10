import ping3
from typing import Dict
import logging
import httpx
import time

logger = logging.getLogger(__name__)

class PacketLossTest:
    def __init__(self):
        self.target = "1.1.1.1"
        self.count = 20
        ping3.EXCEPTIONS = True
    
    def run_test(self) -> Dict:
        """Test packet loss using HTTP fallback if ICMP blocked"""

        packets_sent = self.count
        packets_received = 0

        for _ in range(self.count):
            try:
                start = time.time()
                httpx.get("https://www.google.com", timeout=3)
                packets_received += 1
            except:
                pass

        packets_lost = packets_sent - packets_received

        packet_loss_percent = round(
            (packets_lost / packets_sent) * 100, 1
        ) if packets_sent > 0 else 100

        return {
            "packets_sent": packets_sent,
            "packets_received": packets_received,
            "packets_lost": packets_lost,
            "packet_loss_percent": packet_loss_percent,
            "method": "http_fallback"
        }
