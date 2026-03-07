from ping3 import ping


def run_ping_test():
    targets = {
        "google_dns": "8.8.8.8",
        "cloudflare": "1.1.1.1",
        "google_dns_backup": "8.8.4.4",
        "quad9": "9.9.9.9"
        # "amazon": "amazon.com" #ping blocked
    }

    results = {}

    for name, host in targets.items():
        latencies = []
        try:
            for _ in range(3): # send 3 ping attempts
                latency = ping(host, timeout=2)

                if latency is not None:
                    latencies.append(latency * 1000)  # convert to ms

            if latencies:
                avg_latency = sum(latencies) / len(latencies)
                results[name] = round(avg_latency, 2)
            else:
                results[name] = None

        except Exception:
            results[name] = None
    return results