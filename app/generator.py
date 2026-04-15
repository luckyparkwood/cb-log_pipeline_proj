import random
import time
from datetime import datetime, timezone
import requests

API_URL = "http://127.0.0.1:8000/logs"

SERVICES = ["auth-service", "billing-service", "search-service"]
LEVELS = ["INFO", "INFO", "INFO", "ERROR"]


def make_log():
    service = random.choice(SERVICES)
    level = random.choice(LEVELS)

    latency = random.randint(50, 250)

    if service == "billing-service" and random.random() < 0.2:
        latency = random.randint(600, 1200)

    if service == "auth-service" and random.random() < 0.2:
        level = "ERROR"

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": service,
        "host": "agent-1",
        "level": level,
        "message": f"Simulated log from {service}",
        "latency_ms": latency
    }


def main():
    while True:
        log = make_log()
        response = requests.post(API_URL, json=log)
        print(response.status_code, log)
        time.sleep(1)


if __name__ == "__main__":
    main()