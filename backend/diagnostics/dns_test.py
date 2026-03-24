import logging
import statistics
import time
from typing import Dict, List, Optional

import dns.resolver

logger = logging.getLogger(__name__)


class DNSTest:
    def __init__(self) -> None:
        self.servers = ["1.1.1.1", "8.8.8.8", "9.9.9.9"]
        self.queries_per_server = 3
        self.domain = "google.com"

    def run_test(self) -> Dict:
        server_results: Dict[str, Dict] = {}
        all_query_times: List[float] = []
        best_server: Optional[str] = None
        best_latency: Optional[float] = None

        for server in self.servers:
            result = self._test_server(server)
            server_results[server] = result
            all_query_times.extend(result["query_times_ms"])

            average_latency = result["average_latency_ms"]
            if average_latency is not None and (best_latency is None or average_latency < best_latency):
                best_latency = average_latency
                best_server = server

        return {
            "servers": server_results,
            "summary": {
                "average_latency_ms": round(statistics.mean(all_query_times), 2) if all_query_times else None,
                "minimum_latency_ms": round(min(all_query_times), 2) if all_query_times else None,
                "maximum_latency_ms": round(max(all_query_times), 2) if all_query_times else None,
                "fastest_server": best_server,
            },
        }

    def _test_server(self, server: str) -> Dict:
        resolver = dns.resolver.Resolver(configure=False)
        resolver.nameservers = [server]
        resolver.timeout = 2
        resolver.lifetime = 2

        times: List[float] = []
        failures = 0

        for _ in range(self.queries_per_server):
            try:
                start = time.perf_counter()
                resolver.resolve(self.domain, "A")
                elapsed_ms = (time.perf_counter() - start) * 1000
                times.append(round(elapsed_ms, 2))
            except Exception as exc:
                logger.warning("DNS query failed for %s using %s: %s", self.domain, server, exc)
                failures += 1

        average_latency = round(statistics.mean(times), 2) if times else None
        return {
            "queries": self.queries_per_server,
            "successful_queries": len(times),
            "failed_queries": failures,
            "query_times_ms": times,
            "average_latency_ms": average_latency,
        }
