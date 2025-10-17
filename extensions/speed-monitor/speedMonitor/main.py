import argparse, time, signal
from kuksa_client.grpc import VSSClient
from speedMonitor.core import SpeedMonitor, Thresholds
from speedMonitor.io import AlertSink

def parse_args():
    p = argparse.ArgumentParser(description="Speed Anomaly Monitor (Phase 1 scaffold)")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=55556)
    p.add_argument("--max-speed", type=float, default=80.0)
    p.add_argument("--csv", default="alerts.csv")
    return p.parse_args()

def main():
    args = parse_args()
    mon  = SpeedMonitor(Thresholds(args.max_speed))
    sink = AlertSink(args.csv)

    c = VSSClient(args.host, args.port); c.connect()

    def on_update(resp):
        speed = resp["Vehicle.Speed"].value
        for a in mon.on_speed(speed):
            print(f"[ALERT] kind={a.kind} speed={a.speed:.2f} reason={a.reason}", flush=True)
    
    c.subscribe_current_values(["Vehicle.Speed"], on_update)
    print("Subscribed. Ctrl+C to exit.")

    running = True
    def _stop(*_): 
        nonlocal running; running = False
    signal.signal(signal.SIGINT, _stop)
    signal.signal(signal.SIGTERM, _stop)

    try:
        while running:
            time.sleep(0.2)
    finally:
        sink.close()

if __name__ == "__main__":
    main()
