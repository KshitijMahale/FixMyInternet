from fastapi import APIRouter
from backend.models.result_model import PingTestResponse
from backend.diagnostics.ping_test import run_ping_test
from backend.diagnostics.dns_test import run_dns_test
from backend.models.result_model import DNSTestResponse
from backend.analysis.root_cause_engine import analyze_network
from backend.diagnostics.packet_loss import run_packet_loss_test
from backend.models.result_model import PacketLossResponse
from backend.diagnostics.speed_test import run_speed_test
from backend.models.result_model import SpeedTestResponse

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

@router.get("/speed-test", response_model=SpeedTestResponse)
def speed_test():
    return run_speed_test()

@router.get("/packet-loss", response_model=PacketLossResponse)
def packet_loss():
    return run_packet_loss_test()

@router.get("/full-analysis")
def full_analysis():
    ping_results = run_ping_test()
    dns_results = run_dns_test()
    packet_loss = run_packet_loss_test()
    speed = run_speed_test()

    analysis = analyze_network(
        ping_results,
        dns_results,
        packet_loss
    )

    return {
        "speed": speed,
        "ping": ping_results,
        "dns": dns_results,
        "packet_loss": packet_loss,
        "analysis": analysis
    }