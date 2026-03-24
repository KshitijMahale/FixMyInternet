import logging
import statistics
from typing import Dict, List, Optional

import ping3

logger = logging.getLogger(__name__)


class PingTest:
    def __init__(self) -> None:
        self.targets = ["8.8.8.8", "1.1.1.1", "8.8.4.4", "9.9.9.9"]
        self.pings_per_target = 5
        ping3.EXCEPTIONS = False

    def run_test(self) -> Dict:
        all_latencies: List[float] = []
        targets_result: Dict[str, Dict] = {}

        for target in self.targets:
            target_data = self._ping_target(target, self.pings_per_target)
            targets_result[target] = target_data
            all_latencies.extend(target_data["latencies_ms"])

        return {
            "targets": targets_result,
            "summary": self._build_summary(all_latencies),
        }

    def _ping_target(self, target: str, count: int) -> Dict:
        latencies: List[float] = []

        for _ in range(count):
            try:
                response_seconds = ping3.ping(target, timeout=2)
                if response_seconds is not None:
                    latencies.append(round(response_seconds * 1000, 2))
            except Exception as exc:
                logger.warning("Ping failed for %s: %s", target, exc)

        sent = count
        received = len(latencies)
        return {
            "attempts": sent,
            "successful_pings": received,
            "latencies_ms": latencies,
            "average_latency_ms": self._mean(latencies),
            "minimum_latency_ms": round(min(latencies), 2) if latencies else None,
            "maximum_latency_ms": round(max(latencies), 2) if latencies else None,
            "variance_ms2": self._variance(latencies),
            "packet_loss_percent": round(((sent - received) / sent) * 100, 2) if sent else None,
        }

    def _build_summary(self, latencies: List[float]) -> Dict:
        if not latencies:
            return {
                "average_latency_ms": None,
                "minimum_latency_ms": None,
                "maximum_latency_ms": None,
                "variance_ms2": None,
                "jitter_ms": None,
                "error": "No successful ICMP responses.",
            }

        min_latency = round(min(latencies), 2)
        max_latency = round(max(latencies), 2)
        return {
            "average_latency_ms": self._mean(latencies),
            "minimum_latency_ms": min_latency,
            "maximum_latency_ms": max_latency,
            "variance_ms2": self._variance(latencies),
            "jitter_ms": round(max_latency - min_latency, 2),
        }

    @staticmethod
    def _mean(values: List[float]) -> Optional[float]:
        if not values:
            return None
        return round(statistics.mean(values), 2)

    @staticmethod
    def _variance(values: List[float]) -> Optional[float]:
        if not values:
            return None
        if len(values) == 1:
            return 0.0
        return round(statistics.variance(values), 2)
