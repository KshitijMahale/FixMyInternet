from typing import Any, Dict, List, Optional


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

        health_score = self._calculate_health_score(latency, dns, packet_loss, download_speed, jitter)

        latency_status = self._classify_latency(latency)
        jitter_status = self._classify_jitter(jitter)
        dns_status = self._classify_dns(dns)
        packet_loss_status = self._classify_packet_loss(packet_loss)
        speed_status = self._classify_speed(download_speed)

        diagnosis_result = self._diagnose(
            latency=latency,
            dns=dns,
            packet_loss=packet_loss,
            download_speed=download_speed,
            jitter=jitter,
            latency_status=latency_status,
            jitter_status=jitter_status,
            dns_status=dns_status,
            packet_loss_status=packet_loss_status,
            speed_status=speed_status,
        )
        health_label = self._health_label(health_score)

        metrics = {
            "speed": {
                "label": "Download Speed",
                "value": download_speed,
                "unit": "Mbps",
                "rating": speed_status,
                "meaning": self._speed_meaning(speed_status),
                "impact": self._speed_impact(speed_status),
            },
            "latency": {
                "label": "Latency",
                "value": latency,
                "unit": "ms",
                "rating": latency_status,
                "meaning": "Low latency means your connection responds quickly. High latency can cause lag.",
                "impact": self._latency_impact(latency_status),
            },
            "stability": {
                "label": "Stability (Jitter)",
                "value": jitter,
                "unit": "ms",
                "rating": jitter_status,
                "meaning": "High jitter means your connection fluctuates and may cause lag.",
                "impact": self._jitter_impact(jitter_status),
            },
            "dns": {
                "label": "DNS Response",
                "value": dns,
                "unit": "ms",
                "rating": dns_status,
                "meaning": "DNS controls how quickly website names are translated into addresses.",
                "impact": self._dns_impact(dns_status),
            },
            "packet_loss": {
                "label": "Packet Loss",
                "value": packet_loss,
                "unit": "%",
                "rating": packet_loss_status,
                "meaning": "Packet loss means some network data never reaches its destination.",
                "impact": self._packet_loss_impact(packet_loss_status),
            },
        }

        fastest_dns_ip = self._pick_text(test_results, ["dns", "summary", "fastest_server"])
        fastest_dns_name = self._dns_provider_name(fastest_dns_ip)

        checklist = self._healthy_checklist(
            latency=latency,
            packet_loss=packet_loss,
            dns=dns,
            download_speed=download_speed,
        )

        return {
            "health_score": health_score,
            "health_label": health_label,
            "connection_summary": diagnosis_result["connection_summary"],
            "diagnosis": diagnosis_result["diagnosis"],
            "explanation": diagnosis_result["explanation"],
            "recommendation": diagnosis_result["recommendation"],
            "suggestions": diagnosis_result["suggestions"],
            "issues_detected": diagnosis_result["issues_detected"],
            "is_healthy": diagnosis_result["is_healthy"],
            "checklist": checklist,
            "metrics": metrics,
            "dns_provider": {
                "ip": fastest_dns_ip,
                "name": fastest_dns_name,
                "display": f"{fastest_dns_name} ({fastest_dns_ip})" if fastest_dns_ip else "Unknown",
            },
            "jitter_ms": jitter,
        }

    def _calculate_health_score(
        self,
        latency: Optional[float],
        dns: Optional[float],
        packet_loss: Optional[float],
        speed: Optional[float],
        jitter: Optional[float],
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
            if packet_loss > 5:
                score -= 40
            elif packet_loss >= 3:
                score -= 25
            elif packet_loss >= 1:
                score -= 10

        if speed is not None:
            if speed < 5:
                score -= 30
            elif speed < 25:
                score -= 15
            elif speed < 100:
                score -= 5

        if jitter is not None:
            if jitter > 50:
                score -= 20
            elif jitter >= 20:
                score -= 10
            elif jitter >= 5:
                score -= 3

        return max(0, score)

    def _diagnose(
        self,
        latency: Optional[float],
        dns: Optional[float],
        packet_loss: Optional[float],
        download_speed: Optional[float],
        jitter: Optional[float],
        latency_status: str,
        jitter_status: str,
        dns_status: str,
        packet_loss_status: str,
        speed_status: str,
    ) -> Dict[str, Any]:
        issues: List[Dict[str, str]] = []

        if packet_loss is not None and packet_loss > 0:
            severity = "critical" if packet_loss > 5 else ("high" if packet_loss >= 3 else "medium")
            issues.append(
                {
                    "diagnosis": "Packet loss detected",
                    "explanation": "Your network is losing data packets, which causes instability, buffering, call drops, and gaming lag.",
                    "recommendation": "Move closer to your router, restart your router, and retest.",
                    "severity": severity,
                }
            )

        if latency is not None and latency > 150:
            issues.append(
                {
                    "diagnosis": "High latency detected",
                    "explanation": "Your connection has high delay, which may cause lag in calls, games, and remote work tools.",
                    "recommendation": "Check WiFi signal quality and switch to Ethernet if possible.",
                    "severity": "high",
                }
            )

        if jitter is not None and jitter > 50:
            issues.append(
                {
                    "diagnosis": "WiFi instability detected",
                    "explanation": "Your connection fluctuates significantly, indicating unstable WiFi conditions.",
                    "recommendation": "Move closer to the router and reduce interference from nearby devices.",
                    "severity": "high",
                }
            )

        if dns is not None and dns > 100:
            issues.append(
                {
                    "diagnosis": "Slow DNS resolution",
                    "explanation": "Your DNS server is slow in resolving websites, which can delay page loads.",
                    "recommendation": "Switch DNS to Cloudflare (1.1.1.1) for faster lookups.",
                    "severity": "medium",
                }
            )

        if download_speed is not None and download_speed < 25:
            issues.append(
                {
                    "diagnosis": "Low download speed",
                    "explanation": "Your download speed is lower than expected for smooth streaming and larger downloads.",
                    "recommendation": "Restart your router and contact your ISP if low speeds continue.",
                    "severity": "high" if download_speed < 5 else "medium",
                }
            )

        if latency is not None and latency > 80 and (packet_loss is not None and packet_loss <= 1):
            issues.append(
                {
                    "diagnosis": "Possible ISP congestion",
                    "explanation": "Your latency is elevated while packet loss stays low, which often suggests ISP congestion.",
                    "recommendation": "Run tests at different times and share results with your ISP.",
                    "severity": "medium",
                }
            )

        is_healthy = (
            latency_status in {"Excellent", "Good"}
            and jitter_status in {"Very stable", "Stable"}
            and dns_status in {"Fast", "Normal"}
            and packet_loss_status in {"Perfect", "Acceptable"}
            and speed_status in {"Good", "Very fast"}
        )

        if is_healthy and not issues:
            return {
                "is_healthy": True,
                "connection_summary": "Your internet connection is fast, stable, and reliable.",
                "diagnosis": "Your internet connection is performing very well.",
                "explanation": "You have low latency, no meaningful packet loss, fast DNS response, and strong speed for daily use.",
                "recommendation": "No urgent action needed. Keep your router firmware updated and retest periodically.",
                "suggestions": [
                    "No immediate fixes needed.",
                    "Keep router firmware updated.",
                    "Retest at different times to track consistency.",
                ],
                "issues_detected": [],
            }

        if not issues:
            return {
                "is_healthy": False,
                "connection_summary": "Your internet connection is usable but has room for improvement.",
                "diagnosis": "Moderate connection quality",
                "explanation": "Some metrics are not ideal, which may cause occasional slowdowns under load.",
                "recommendation": "Retest over Ethernet and compare with WiFi to isolate local interference.",
                "suggestions": [
                    "Retest closer to your router.",
                    "Try a wired Ethernet test for comparison.",
                ],
                "issues_detected": [],
            }

        severity_rank = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        primary = max(issues, key=lambda issue: severity_rank.get(issue["severity"], 0))

        suggestions = self._build_suggestions(issues)

        return {
            "is_healthy": False,
            "connection_summary": self._connection_summary_from_status(
                speed_status, latency_status, jitter_status, dns_status, packet_loss_status
            ),
            "diagnosis": primary["diagnosis"],
            "explanation": primary["explanation"],
            "recommendation": primary["recommendation"],
            "suggestions": suggestions,
            "issues_detected": [issue["diagnosis"] for issue in issues],
        }

    def _build_suggestions(self, issues: List[Dict[str, str]]) -> List[str]:
        suggestions: List[str] = []
        issue_names = {issue["diagnosis"] for issue in issues}

        if "Packet loss detected" in issue_names:
            suggestions.extend(
                [
                    "Move closer to your WiFi router and remove nearby interference.",
                    "Restart your router and modem.",
                    "Use Ethernet for calls, gaming, or critical work.",
                ]
            )

        if "High latency detected" in issue_names:
            suggestions.extend(
                [
                    "Check WiFi signal quality in your current room.",
                    "Switch to Ethernet to reduce lag.",
                ]
            )

        if "WiFi instability detected" in issue_names:
            suggestions.extend(
                [
                    "Reduce interference from Bluetooth devices and microwave ovens.",
                    "Use 5 GHz WiFi when close to the router.",
                ]
            )

        if "Slow DNS resolution" in issue_names:
            suggestions.extend(
                [
                    "Switch DNS to Cloudflare (1.1.1.1).",
                    "As backup, try Google DNS (8.8.8.8).",
                ]
            )

        if "Low download speed" in issue_names:
            suggestions.extend(
                [
                    "Restart your router and run another speed test.",
                    "Pause background downloads on other devices.",
                    "Contact your ISP if speeds remain below your plan.",
                ]
            )

        if "Possible ISP congestion" in issue_names:
            suggestions.extend(
                [
                    "Run tests during off-peak hours and compare results.",
                    "Share peak-hour latency screenshots with your ISP.",
                ]
            )

        # Keep order while removing duplicates.
        unique_suggestions: List[str] = []
        for item in suggestions:
            if item not in unique_suggestions:
                unique_suggestions.append(item)

        return unique_suggestions

    @staticmethod
    def _classify_latency(value: Optional[float]) -> str:
        if value is None:
            return "Unknown"
        if value < 40:
            return "Excellent"
        if value <= 80:
            return "Good"
        if value <= 150:
            return "Moderate"
        return "Poor"

    @staticmethod
    def _classify_jitter(value: Optional[float]) -> str:
        if value is None:
            return "Unknown"
        if value < 5:
            return "Very stable"
        if value <= 20:
            return "Stable"
        if value <= 50:
            return "Unstable"
        return "Highly unstable"

    @staticmethod
    def _classify_dns(value: Optional[float]) -> str:
        if value is None:
            return "Unknown"
        if value < 40:
            return "Fast"
        if value <= 100:
            return "Normal"
        return "Slow"

    @staticmethod
    def _classify_packet_loss(value: Optional[float]) -> str:
        if value is None:
            return "Unknown"
        if value == 0:
            return "Perfect"
        if value <= 2:
            return "Acceptable"
        if value <= 5:
            return "Problematic"
        return "Severe issue"

    @staticmethod
    def _classify_speed(value: Optional[float]) -> str:
        if value is None:
            return "Unknown"
        if value < 5:
            return "Very slow"
        if value < 25:
            return "Basic usage"
        if value <= 100:
            return "Good"
        return "Very fast"

    @staticmethod
    def _health_label(score: int) -> str:
        if score >= 90:
            return "Excellent"
        if score >= 75:
            return "Good"
        if score >= 55:
            return "Moderate"
        if score >= 35:
            return "Poor"
        return "Severe issues"

    @staticmethod
    def _dns_provider_name(ip: Optional[str]) -> str:
        mapping = {
            "1.1.1.1": "Cloudflare",
            "8.8.8.8": "Google DNS",
            "9.9.9.9": "Quad9",
        }
        if not ip:
            return "Unknown"
        return mapping.get(ip, "Custom DNS")

    @staticmethod
    def _speed_meaning(status: str) -> str:
        return {
            "Very slow": "This speed struggles with most modern internet tasks.",
            "Basic usage": "This speed is suitable for browsing and light streaming.",
            "Good": "This speed supports streaming, video calls, and most home usage.",
            "Very fast": "This speed is excellent for 4K streaming, gaming, and large downloads.",
        }.get(status, "Speed data is unavailable.")

    @staticmethod
    def _speed_impact(status: str) -> str:
        return {
            "Very slow": "Web pages may load slowly, and streaming can buffer often.",
            "Basic usage": "Browsing is fine, but heavy streaming or multiple users may feel slow.",
            "Good": "Most online activities should feel smooth for regular households.",
            "Very fast": "High-demand activities should run smoothly with multiple connected devices.",
        }.get(status, "Speed impact cannot be determined right now.")

    @staticmethod
    def _latency_impact(status: str) -> str:
        return {
            "Excellent": "Real-time activities like gaming and calls should feel responsive.",
            "Good": "Most online tasks should feel smooth with minimal delay.",
            "Moderate": "You may notice delay in calls or fast-paced games.",
            "Poor": "Lag is likely during games, calls, and remote work sessions.",
        }.get(status, "Latency impact cannot be determined right now.")

    @staticmethod
    def _jitter_impact(status: str) -> str:
        return {
            "Very stable": "Connection timing is consistent.",
            "Stable": "Connection is mostly consistent for calls and streaming.",
            "Unstable": "You may see occasional lag spikes and call quality drops.",
            "Highly unstable": "Frequent lag spikes and stutter are likely.",
        }.get(status, "Stability impact cannot be determined right now.")

    @staticmethod
    def _dns_impact(status: str) -> str:
        return {
            "Fast": "Websites should start loading quickly.",
            "Normal": "Website lookup time is within normal range.",
            "Slow": "New websites may take longer to start loading.",
        }.get(status, "DNS impact cannot be determined right now.")

    @staticmethod
    def _packet_loss_impact(status: str) -> str:
        return {
            "Perfect": "No data loss detected. Your connection is stable.",
            "Acceptable": "Minor data loss may happen but usually remains unnoticeable.",
            "Problematic": "Data loss may cause buffering, call drops, and gaming lag.",
            "Severe issue": "Heavy data loss will cause visible instability and interruptions.",
        }.get(status, "Packet loss impact cannot be determined right now.")

    def _healthy_checklist(
        self,
        latency: Optional[float],
        packet_loss: Optional[float],
        dns: Optional[float],
        download_speed: Optional[float],
    ) -> List[Dict[str, Any]]:
        return [
            {
                "label": "Low latency",
                "ok": latency is not None and latency < 40,
                "value": latency,
            },
            {
                "label": "No packet loss",
                "ok": packet_loss is not None and packet_loss == 0,
                "value": packet_loss,
            },
            {
                "label": "Fast DNS",
                "ok": dns is not None and dns < 40,
                "value": dns,
            },
            {
                "label": "Good speed",
                "ok": download_speed is not None and download_speed >= 25,
                "value": download_speed,
            },
        ]

    @staticmethod
    def _connection_summary_from_status(
        speed_status: str,
        latency_status: str,
        jitter_status: str,
        dns_status: str,
        packet_loss_status: str,
    ) -> str:
        if packet_loss_status in {"Problematic", "Severe issue"}:
            return "Your connection is unstable due to data loss."
        if latency_status == "Poor" or jitter_status == "Highly unstable":
            return "Your connection is currently unstable and may feel laggy."
        if speed_status in {"Very slow", "Basic usage"}:
            return "Your connection is stable enough for basic tasks, but speed is limited."
        if dns_status == "Slow":
            return "Your connection quality is fair, but website loading may feel delayed."
        return "Your internet connection is mostly stable with minor issues to optimize."

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

    @staticmethod
    def _pick_text(source: Dict[str, Any], path: List[str]) -> Optional[str]:
        value: Any = source
        for key in path:
            if not isinstance(value, dict) or key not in value:
                return None
            value = value[key]
        if isinstance(value, str):
            return value
        return None
