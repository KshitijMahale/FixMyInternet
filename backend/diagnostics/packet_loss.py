from typing import Dict

import ping3


class PacketLossTest:
    def __init__(self) -> None:
        self.target = "1.1.1.1"
        self.count = 20
        ping3.EXCEPTIONS = False

    def run_test(self) -> Dict:
        packets_sent = self.count
        packets_received = 0

        for _ in range(self.count):
            response = ping3.ping(self.target, timeout=2)
            if response is not None:
                packets_received += 1

        packets_lost = packets_sent - packets_received
        packet_loss_percent = round((packets_lost / packets_sent) * 100, 2) if packets_sent else 100.0

        return {
            "target": self.target,
            "packets_sent": packets_sent,
            "packets_received": packets_received,
            "packets_lost": packets_lost,
            "packet_loss_percent": packet_loss_percent,
        }
