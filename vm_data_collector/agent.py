import socket
import platform
import requests
import time
import os


MASTER_SERVER_URL = os.environ.get("HOST_URL", "http://127.0.0.1:5000/host")
INTERVAL_SECONDS = 10  # 10 minutes

def collect_system_info():
    return {
        "hostname": socket.gethostname(),
        "os_name": platform.system(),
        "os_release": platform.release(),
        "architecture": platform.machine()
    }

def send_data(payload):
    try:
        response = requests.post(
            MASTER_SERVER_URL,
            json=payload,
            timeout=5
        )
        response.raise_for_status()
        print("Heartbeat sent")
    except requests.exceptions.RequestException as e:
        print(f"Send failed: {e}")

def main():
    while True:
        payload = collect_system_info()
        send_data(payload)
        time.sleep(INTERVAL_SECONDS)

if __name__ == "__main__":
    main()
