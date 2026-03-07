from fastapi import APIRouter
from backend.models.result_model import PingTestResponse
from backend.diagnostics.ping_test import run_ping_test
from backend.diagnostics.dns_test import run_dns_test
from backend.models.result_model import DNSTestResponse
from backend.analysis.root_cause_engine import analyze_network
from backend.diagnostics.packet_loss import run_packet_loss_test
from backend.models.result_model import PacketLossResponse

router = APIRouter(
    prefix="/diagnostics",
    tags=["Diagnostics"]
)

@router.get("/ping-test", response_model=PingTestResponse)
def ping_test():
    results = run_ping_test()

    return {
        "test": "latency",
        "results": results
    }

@router.get("/dns-test", response_model=DNSTestResponse)
def dns_test():
    results = run_dns_test()

    return {
        "test": "dns_resolution",
        "results": results
    }

@router.get("/speed-test")
def speed_test():
    return {
        "message": "Speed test endpoint coming soon"
    }

@router.get("/packet-loss", response_model=PacketLossResponse)
def packet_loss():
    return run_packet_loss_test()

@router.get("/full-analysis")
def full_analysis():
    ping_results = run_ping_test()
    dns_results = run_dns_test()
    analysis = analyze_network(
        ping_results,
        dns_results
    )

    return {
        "ping": ping_results,
        "dns": dns_results,
        "analysis": analysis
    }