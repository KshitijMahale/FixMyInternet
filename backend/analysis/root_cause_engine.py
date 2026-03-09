def calculate_health_score(ping_results, dns_results, packet_loss):
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
            score -= 25
        elif avg_dns > 100:
            score -= 15
        elif avg_dns > 60:
            score -= 5

    # Packet loss evaluation 
    loss = packet_loss["packet_loss_percent"]
    if loss > 10:
        score -= 40
    elif loss > 5:
        score -= 25
    elif loss > 2:
        score -= 10
    return max(score, 0)


def detect_problem(ping_results, dns_results, packet_loss, speed):
    valid_pings = [v for v in ping_results.values() if v is not None]
    valid_dns = [v for v in dns_results.values() if v is not None]

    avg_ping = sum(valid_pings) / len(valid_pings) if valid_pings else None
    avg_dns = sum(valid_dns) / len(valid_dns) if valid_dns else None

    packet_loss_percent = packet_loss["packet_loss_percent"]
    download_speed = speed.get("download_mbps")

    # ---- Packet Loss ----
    if packet_loss_percent > 5:
        return {
            "diagnosis": "Packet loss detected",
            "explanation": (
                "Your network dropped several packets during testing. "
                "Packet loss can cause lag in games, buffering, and unstable calls."
            ),
            "recommendation": (
                "Move closer to your router or try using an Ethernet connection."
            )
        }

    # ---- Slow DNS ----
    if avg_dns and avg_dns > 120:
        return {
            "diagnosis": "Slow DNS resolution detected",
            "explanation": (
                "Your DNS server is taking longer than usual to resolve domain names. "
                "This can delay website loading."
            ),
            "recommendation": (
                "Switch your DNS to Cloudflare (1.1.1.1) or Google (8.8.8.8)."
            )
        }

    # ---- High Latency ----
    if avg_ping and avg_ping > 120:
        return {
            "diagnosis": "High network latency detected",
            "explanation": (
                "Your network latency is higher than normal. "
                "This may cause lag in games or video calls."
            ),
            "recommendation": (
                "Check your WiFi signal strength or try using a wired connection."
            )
        }

    # ---- Low Speed ----
    if download_speed and download_speed < 5:
        return {
            "diagnosis": "Low download speed detected",
            "explanation": (
                "Your internet download speed is very low compared to normal broadband speeds."
            ),
            "recommendation": (
                "Restart your router or check with your internet provider."
            )
        }

    # ---- Possible ISP congestion ----
    if avg_ping and avg_ping > 80 and packet_loss_percent < 1:
        return {
            "diagnosis": "Possible ISP congestion",
            "explanation": (
                "Latency is higher than normal but there is no packet loss. "
                "This could indicate congestion in your ISP network."
            ),
            "recommendation": (
                "Try testing again later or contact your ISP."
            )
        }

    # ---- WiFi instability ----
    if packet_loss_percent > 1 and packet_loss_percent <= 5:
        return {
            "diagnosis": "Possible WiFi instability",
            "explanation": (
                "A small amount of packet loss was detected which may indicate weak WiFi signal."
            ),
            "recommendation": (
                "Move closer to the router or switch to a wired connection."
            )
        }
    
    if detect_latency_instability(ping_results):
        return {
            "diagnosis": "Unstable network detected",
            "explanation": (
                "Your latency fluctuates significantly which suggests "
                "WiFi interference or network instability."
            ),
            "recommendation": (
                "Move closer to your router or use a wired Ethernet connection."
            )
        }

    # ---- Default ----
    return {
        "diagnosis": "Connection healthy",
        "explanation": (
            "Your internet connection appears stable based on speed, latency, DNS performance, "
            "and packet loss."
        ),
        "recommendation": "No action required."
    }


def analyze_network(ping_results, dns_results, packet_loss, speed):

    health_score = calculate_health_score(
        ping_results,
        dns_results,
        packet_loss
    )

    result = detect_problem(
        ping_results,
        dns_results,
        packet_loss,
        speed
    )

    return {
        "health_score": health_score,
        "diagnosis": result["diagnosis"],
        "explanation": result["explanation"],
        "recommendation": result["recommendation"]
    }

def detect_latency_instability(ping_results):
    latencies = []

    for server in ping_results.values():
        if server:
            latencies.append(server["max"] - server["min"])

    if not latencies:
        return False

    avg_variation = sum(latencies) / len(latencies)
    return avg_variation > 80