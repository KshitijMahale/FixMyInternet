from ping3 import ping


def run_ping_test():
    targets = {
        "google_dns": "8.8.8.8",
        "cloudflare": "1.1.1.1",
        "google_dns_backup": "8.8.4.4",
        "quad9": "9.9.9.9"
    }

    results = {}

    for name, host in targets.items():
        samples = []

        for _ in range(5):
            latency = ping(host, timeout=2)
            if latency is not None:
                samples.append(latency * 1000)

        if samples:
            avg_latency = sum(samples) / len(samples)
            min_latency = min(samples)
            max_latency = max(samples)

            results[name] = {
                "avg": round(avg_latency, 2),
                "min": round(min_latency, 2),
                "max": round(max_latency, 2),
                "samples": len(samples)
            }

        else:
            results[name] = None
    return results