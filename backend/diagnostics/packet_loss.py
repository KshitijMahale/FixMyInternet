from ping3 import ping

def run_packet_loss_test(host="1.1.1.1", attempts=20):
    sent = attempts
    received = 0

    for _ in range(attempts):
        try:
            response = ping(host, timeout=2)
            if response is not None:
                received += 1

        except Exception:
            pass

    lost = sent - received
    loss_percent = (lost / sent) * 100

    return {
        "packets_sent": sent,
        "packets_received": received,
        "packets_lost": lost,
        "packet_loss_percent": round(loss_percent, 2)
    }