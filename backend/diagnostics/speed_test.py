import logging
from typing import Dict

import speedtest

logger = logging.getLogger(__name__)


class SpeedTestDiagnostic:
    def run_test(self) -> Dict:
        try:
            tester = speedtest.Speedtest(secure=True)
            tester.get_best_server()
            download_mbps = tester.download() / 1_000_000
            upload_mbps = tester.upload() / 1_000_000

            return {
                "download_mbps": round(download_mbps, 2),
                "upload_mbps": round(upload_mbps, 2),
            }
        except Exception as exc:
            logger.warning("Speed test failed: %s", exc)
            return {
                "download_mbps": None,
                "upload_mbps": None,
                "error": "Speed test failed.",
            }