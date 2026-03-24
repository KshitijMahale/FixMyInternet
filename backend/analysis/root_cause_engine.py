from typing import Any, Dict, List, Optional, Tuple


class RootCauseAnalyzer:
    def analyze(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        latency = self._pick_number(
            test_results,
            ["latency", "summary", "average_latency_ms"],
            ["latency", "summary", "average"],
        )
        min_latency = self._pick_number(
            test_results,
            ["latency", "summary", "minimum_latency_ms"],
            ["latency", "summary", "minimum"],
        )
        max_latency = self._pick_number(
            test_results,
            ["latency", "summary", "maximum_latency_ms"],
            ["latency", "summary", "maximum"],
        )
        dns = self._pick_number(
            test_results,
            ["dns", "summary", "average_latency_ms"],
            ["dns", "summary", "average"],
        )
        packet_loss = self._pick_number(test_results, ["packet_loss", "packet_loss_percent"])
        download_speed = self._pick_number(test_results, ["speed", "download_mbps"])

        jitter = None
        if min_latency is not None and max_latency is not None:
            jitter = round(max_latency - min_latency, 2)

        health_score = self._calculate_health_score(latency, dns, packet_loss)
        diagnosis, explanation, recommendation, issues = self._diagnose(
            latency=latency,
            dns=dns,
            packet_loss=packet_loss,
            download_speed=download_speed,
            jitter=jitter,
        )

        return {
            "health_score": health_score,
            "diagnosis": diagnosis,
            "explanation": explanation,
            "recommendation": recommendation,
            "issues_detected": issues,
            "jitter_ms": jitter,
        }

    def _calculate_health_score(
        self,
        latency: Optional[float],
        dns: Optional[float],
        packet_loss: Optional[float],
    ) -> int:
        score = 100

        if latency is not None:
            if latency > 150:
                score -= 30
            elif latency >= 80:
                score -= 15
            elif latency >= 50:
                score -= 5

        if dns is not None:
            if dns > 200:
                score -= 25
            elif dns >= 100:
                score -= 15
            elif dns >= 60:
                score -= 5

        if packet_loss is not None:
            if packet_loss > 10:
                score -= 40
            elif packet_loss >= 5:
                score -= 25
            elif packet_loss >= 2:
                score -= 10

        return max(0, score)

    def _diagnose(
        self,
        latency: Optional[float],
        dns: Optional[float],
        packet_loss: Optional[float],
        download_speed: Optional[float],
        jitter: Optional[float],
    ) -> Tuple[str, str, str, List[str]]:
        issues: List[Dict[str, str]] = []

        if dns is not None and dns > 120:
            issues.append(
                {
                    "diagnosis": "Slow DNS server detected",
                    "explanation": "Your DNS server is taking longer than normal to resolve domain names.",
                    "recommendation": "Switch DNS to Cloudflare (1.1.1.1) or Google (8.8.8.8).",
                    "severity": "medium",
                }
            )

        if latency is not None and latency > 120:
            issues.append(
                {
                    "diagnosis": "High network latency",
                    "explanation": "High latency may cause lag in gaming and video calls.",
                    "recommendation": "Check WiFi signal or use Ethernet.",
                    "severity": "high",
                }
            )

        if packet_loss is not None and packet_loss > 5:
            issues.append(
                {
                    "diagnosis": "Packet loss detected",
                    "explanation": "Your network dropped packets during testing.",
                    "recommendation": "Move closer to router or use wired connection.",
                    "severity": "critical",
                }
            )

        if download_speed is not None and download_speed < 5:
            issues.append(
                {
                    "diagnosis": "Low internet speed",
                    "explanation": "Your measured download speed is below 5 Mbps, which can affect basic browsing and streaming.",
                    "recommendation": "Restart router or contact ISP.",
                    "severity": "high",
                }
            )

        if latency is not None and latency > 80 and (packet_loss is not None and packet_loss < 1):
            issues.append(
                {
                    "diagnosis": "Possible ISP congestion",
                    "explanation": "High latency without packet loss often indicates ISP network congestion.",
                    "recommendation": "Test again later or contact your ISP.",
                    "severity": "medium",
                }
            )

        if jitter is not None and jitter > 80:
            issues.append(
                {
                    "diagnosis": "Unstable WiFi connection",
                    "explanation": "Large latency fluctuations indicate wireless interference.",
                    "recommendation": "Move closer to router or switch to Ethernet.",
                    "severity": "high",
                }
            )

        if not issues:
            return (
                "Connection looks healthy",
                "No major internet stability or quality problems were detected during this diagnostic run.",
                "If you still feel slowness, run the test again at a different time and compare trends.",
                [],
            )

        severity_rank = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        primary = max(issues, key=lambda issue: severity_rank.get(issue["severity"], 0))
        issue_names = [issue["diagnosis"] for issue in issues]
        return (
            primary["diagnosis"],
            primary["explanation"],
            primary["recommendation"],
            issue_names,
        )

    @staticmethod
    def _pick_number(source: Dict[str, Any], *paths: List[str]) -> Optional[float]:
        for path in paths:
            value: Any = source
            for key in path:
                if not isinstance(value, dict) or key not in value:
                    value = None
                    break
                value = value[key]
            if isinstance(value, (int, float)):
                return float(value)
        return None
