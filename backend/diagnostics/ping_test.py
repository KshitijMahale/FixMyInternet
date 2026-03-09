import ping3
import statistics
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class PingTest:
    def __init__(self):
        self.targets = [
            "8.8.8.8",    # Google DNS
            "1.1.1.1",    # Cloudflare DNS
            "8.8.4.4",    # Google DNS Secondary
            "9.9.9.9"     # Quad9 DNS
        ]
        ping3.EXCEPTIONS = True
    
    def run_test(self) -> Dict:
        """Run ping test to multiple targets"""
        results = {
            'targets': {},
            'summary': {}
        }
        
        all_latencies = []
        
        for target in self.targets:
            target_results = self._ping_target(target)
            results['targets'][target] = target_results
            
            if target_results['latencies']:
                all_latencies.extend(target_results['latencies'])
        
        # Calculate overall summary
        if all_latencies:
            results['summary'] = {
                'average': round(statistics.mean(all_latencies), 2),
                'minimum': round(min(all_latencies), 2),
                'maximum': round(max(all_latencies), 2),
                'variance': round(statistics.variance(all_latencies) if len(all_latencies) > 1 else 0, 2),
                'jitter': round(max(all_latencies) - min(all_latencies), 2)
            }
        else:
            results['summary'] = {
                'average': None,
                'minimum': None,
                'maximum': None,
                'variance': None,
                'jitter': None,
                'error': 'No ping responses received'
            }
        
        return results
    
    def _ping_target(self, target: str, count: int = 5) -> Dict:
        """Ping a single target multiple times"""
        latencies = []
        errors = 0
        
        for _ in range(count):
            try:
                result = ping3.ping(target, timeout=2)
                if result is not None:
                    # Convert to milliseconds
                    latencies.append(result * 1000)
                else:
                    errors += 1
            except Exception as e:
                logger.error(f"Ping error for {target}: {str(e)}")
                errors += 1
        
        if latencies:
            return {
                'latencies': latencies,
                'average': round(statistics.mean(latencies), 2),
                'minimum': round(min(latencies), 2),
                'maximum': round(max(latencies), 2),
                'packet_loss': round((errors / count) * 100, 1)
            }
        else:
            return {
                'latencies': [],
                'average': None,
                'minimum': None,
                'maximum': None,
                'packet_loss': 100.0,
                'error': 'All pings failed'
            }
