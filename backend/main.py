import asyncio
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from analysis.root_cause_engine import RootCauseAnalyzer
from diagnostics.dns_test import DNSTest
from diagnostics.packet_loss import PacketLossTest
from diagnostics.ping_test import PingTest
from diagnostics.speed_test import SpeedTestDiagnostic

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="FixMyInternet API",
    description="Network diagnostics with intelligent root-cause analysis.",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class NetworkDiagnostics:
    def __init__(self) -> None:
        self.ping_test = PingTest()
        self.dns_test = DNSTest()
        self.packet_loss_test = PacketLossTest()
        self.speed_test = SpeedTestDiagnostic()
        self.analyzer = RootCauseAnalyzer()

    async def _run_safely(
        self,
        test_name: str,
        test_fn: Callable[[], Dict[str, Any]],
        timeout_seconds: float = 35.0,
    ) -> Dict[str, Any]:
        try:
            logger.info("Running %s", test_name)
            return await asyncio.wait_for(asyncio.to_thread(test_fn), timeout=timeout_seconds)
        except asyncio.TimeoutError:
            logger.warning("%s timed out after %ss", test_name, timeout_seconds)
            return {"error": f"{test_name} timed out"}
        except Exception as exc:
            logger.exception("%s failed", test_name)
            return {"error": f"{test_name} failed: {exc}"}

    async def run_full_analysis(self) -> Dict[str, Any]:
        latency_task = self._run_safely("latency test", self.ping_test.run_test, timeout_seconds=20.0)
        dns_task = self._run_safely("dns test", self.dns_test.run_test, timeout_seconds=20.0)
        packet_loss_task = self._run_safely("packet loss test", self.packet_loss_test.run_test, timeout_seconds=20.0)
        speed_task = self._run_safely("speed test", self.speed_test.run_test, timeout_seconds=45.0)

        latency, dns, packet_loss, speed = await asyncio.gather(
            latency_task,
            dns_task,
            packet_loss_task,
            speed_task,
        )

        diagnostics_result = {
            "speed": speed,
            "latency": latency,
            "dns": dns,
            "packet_loss": packet_loss,
        }
        diagnostics_result["analysis"] = self.analyzer.analyze(diagnostics_result)
        diagnostics_result["timestamp"] = datetime.now(timezone.utc).isoformat()
        return diagnostics_result


diagnostics = NetworkDiagnostics()

project_root = Path(__file__).resolve().parent.parent
frontend_root = project_root / "frontend"
if (frontend_root / "js").exists():
    app.mount("/js", StaticFiles(directory=frontend_root / "js"), name="js")
if (frontend_root / "css").exists():
    app.mount("/css", StaticFiles(directory=frontend_root / "css"), name="css")


@app.get("/")
async def frontend_index() -> Any:
    index_path = frontend_root / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {
        "message": "FixMyInternet API is running.",
        "frontend": "Not found at /frontend/index.html",
    }


@app.get("/health")
async def health_check() -> Dict[str, str]:
    return {"status": "healthy"}


@app.get("/diagnostics/full-analysis")
async def full_analysis() -> Dict[str, Any]:
    return await diagnostics.run_full_analysis()