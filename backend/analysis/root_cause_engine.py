def calculate_health_score(ping_results, dns_results):
    score = 100

    # Ping evaluation 
    valid_pings = [v for v in ping_results.values() if v is not None]

    if valid_pings:
        avg_ping = sum(valid_pings) / len(valid_pings)
        if avg_ping > 150:
            score -= 30
        elif avg_ping > 80:
            score -= 15
        elif avg_ping > 50:
            score -= 5

    # DNS evaluation 
    valid_dns = [v for v in dns_results.values() if v is not None]

    if valid_dns:
        avg_dns = sum(valid_dns) / len(valid_dns)
        if avg_dns > 200:
            score -= 30
        elif avg_dns > 100:
            score -= 15
        elif avg_dns > 60:
            score -= 5

    return max(score, 0)


def detect_problem(ping_results, dns_results):
    valid_dns = [v for v in dns_results.values() if v is not None]

    if valid_dns:
        avg_dns = sum(valid_dns) / len(valid_dns)
        if avg_dns > 120:
            return (
                "Slow DNS resolution detected",
                "Switch DNS to Cloudflare (1.1.1.1)"
            )

    valid_pings = [v for v in ping_results.values() if v is not None]

    if valid_pings:
        avg_ping = sum(valid_pings) / len(valid_pings)
        if avg_ping > 120:
            return (
                "High network latency detected",
                "Check WiFi signal or contact ISP"
            )

    return ("Connection healthy", "No action required")


def analyze_network(ping_results, dns_results):
    health_score = calculate_health_score(ping_results, dns_results)
    diagnosis, recommendation = detect_problem(
        ping_results,
        dns_results
    )

    return {
        "health_score": health_score,
        "diagnosis": diagnosis,
        "recommendation": recommendation
    }