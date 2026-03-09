import dns.resolver
import time
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class DNSTest:
    def __init__(self):
        self.dns_servers = {
            "1.1.1.1": "Cloudflare",
            "8.8.8.8": "Google",
            "9.9.9.9": "Quad9"
        }
        self.test_domains = [
            "google.com",
            "cloudflare.com",
            "github.com"
        ]
    
    def run_test(self) -> Dict:
        """Test DNS resolution performance"""
        results = {
            'servers': {},
            'summary': {}
        }
        
        all_times = []
        
        for server_ip, server_name in self.dns_servers.items():
            server_results = self._test_dns_server(server_ip)
            results['servers'][server_ip] = server_results
            
            if server_results.get('times'):
                all_times.extend(server_results['times'])
        
        # Calculate summary
        if all_times:
            results['summary'] = {
                'average': round(sum(all_times) / len(all_times), 2),
                'minimum': round(min(all_times), 2),
                'maximum': round(max(all_times), 2),
                'fastest_server': min(results['servers'].items(), key=lambda x: x[1].get('average', float('inf')))[0]
            }
        else:
            results['summary'] = {
                'average': round(sum(all_times) / len(all_times), 2),
                'minimum': round(min(all_times), 2),
                'maximum': round(max(all_times), 2),
                'fastest_server': f"{self.dns_servers.get(fastest)} ({fastest})"
            }
        
        return results
    
    def _test_dns_server(self, server: str, queries: int = 3) -> Dict:
        """Test a single DNS server"""
        resolver = dns.resolver.Resolver()
        resolver.nameservers = [server]
        resolver.timeout = 2
        resolver.lifetime = 2
        
        times = []
        errors = 0
        
        for domain in self.test_domains[:queries]:
            try:
                start = time.time()
                resolver.resolve(domain, 'A')
                elapsed = (time.time() - start) * 1000  # Convert to ms
                times.append(elapsed)
            except Exception as e:
                logger.error(f"DNS resolution error for {domain} using {server}: {str(e)}")
                errors += 1
        
        if times:
            return {
                'times': times,
                'average': round(sum(times) / len(times), 2),
                'minimum': round(min(times), 2),
                'maximum': round(max(times), 2),
                'success_rate': round(((len(times) / (len(times) + errors)) * 100), 1)
            }
        else:
            return {
                'times': [],
                'average': None,
                'minimum': None,
                'maximum': None,
                'success_rate': 0.0,
                'error': 'All queries failed'
            }
