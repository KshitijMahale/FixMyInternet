import ping3
from typing import Dict
import logging

logger = logging.getLogger(__name__)

class PacketLossTest:
    def __init__(self):
        self.target = "1.1.1.1"
        self.count = 20
        ping3.EXCEPTIONS = True
    
    def run_test(self) -> Dict:
        """Test for packet loss"""
        packets_sent = 0
        packets_received = 0
        latencies = []
        
        for i in range(self.count):
            packets_sent += 1
            try:
                result = ping3.ping(self.target, timeout=2)
                if result is not None:
                    packets_received += 1
                    latencies.append(result * 1000)  # Convert to ms
            except Exception as e:
                logger.debug(f"Packet {i+1} lost: {str(e)}")
        
        packets_lost = packets_sent - packets_received
        packet_loss_percent = round((packets_lost / packets_sent) * 100, 1) if packets_sent > 0 else 100
        
        return {
            'packets_sent': packets_sent,
            'packets_received': packets_received,
            'packets_lost': packets_lost,
            'packet_loss_percent': packet_loss_percent,
            'average_latency': round(sum(latencies) / len(latencies), 2) if latencies else None
        }
