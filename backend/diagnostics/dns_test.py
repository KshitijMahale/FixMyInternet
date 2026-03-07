import dns.resolver
import time


def measure_dns_latency(dns_server, domain="google.com"):
    resolver = dns.resolver.Resolver()
    resolver.nameservers = [dns_server]
    resolver.timeout = 1
    resolver.lifetime = 1

    try:
        start = time.perf_counter()
        resolver.resolve(domain, "A")
        end = time.perf_counter()
        latency = (end - start) * 1000
        return round(latency, 2)

    except Exception:
        return None


def run_dns_test():
    dns_servers = {
        "cloudflare": "1.1.1.1",
        "google": "8.8.8.8",
        "google_backup": "8.8.4.4",
        "quad9": "9.9.9.9"
    }

    results = {}

    for name, server in dns_servers.items():
        results[name] = measure_dns_latency(server)

    return results