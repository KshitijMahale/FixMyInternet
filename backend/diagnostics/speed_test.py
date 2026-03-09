import speedtest
from typing import Dict
import logging

logger = logging.getLogger(__name__)

class SpeedTestDiagnostic:
    def __init__(self):
        self.st = None
    
    def run_test(self) -> Dict:
        try:
            logger.info("Initializing speed test...")
            self.st = speedtest.Speedtest()

            logger.info("Getting best server...")
            try:
                self.st.get_best_server()
            except Exception:
                return {
                    "download_mbps": None,
                    "upload_mbps": None,
                    "ping": None,
                    "error": "Unable to select speed test server"
                }

            logger.info("Testing download speed...")
            download_speed = self.st.download() / 1_000_000

            logger.info("Testing upload speed...")
            upload_speed = self.st.upload() / 1_000_000

            return {
                "download_mbps": round(download_speed, 2),
                "upload_mbps": round(upload_speed, 2),
                "ping": round(self.st.results.ping, 2),
                "server": self.st.results.server.get("sponsor", "Unknown"),
                "server_location": f"{self.st.results.server.get('name','')} - {self.st.results.server.get('country','')}"
            }

        except Exception as e:
            logger.error(f"Speed test error: {str(e)}")
            return {
                "download_mbps": None,
                "upload_mbps": None,
                "ping": None,
                "error": "Speed test failed or timed out"
            }