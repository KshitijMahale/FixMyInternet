from fastapi import APIRouter

router = APIRouter(
    prefix="/diagnostics",
    tags=["Diagnostics"]
)

@router.get("/ping-test")
def ping_test():
    return {
        "message": "Ping test endpoint coming soon"
    }

@router.get("/dns-test")
def dns_test():
    return {
        "message": "DNS test endpoint coming soon"
    }

@router.get("/speed-test")
def speed_test():
    return {
        "message": "Speed test endpoint coming soon"
    }

@router.get("/packet-loss")
def packet_loss():
    return {
        "message": "Packet loss test endpoint coming soon"
    }