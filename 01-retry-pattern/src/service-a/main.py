import time
from pathlib import Path

import requests
import yaml
from fastapi import FastAPI, HTTPException

app = FastAPI(title="Retry Pattern - Service A")

BASE_DIR = Path(__file__).resolve().parents[2]
CONFIG_PATH = BASE_DIR / "config" / "retry-config.yml"

with CONFIG_PATH.open("r", encoding="utf-8") as config_file:
    config = yaml.safe_load(config_file)

retry_config = config["retry"]
MAX_ATTEMPTS = retry_config["max_attempts"]
INITIAL_DELAY = retry_config["backoff"]["initial_delay_seconds"]
BACKOFF_MULTIPLIER = retry_config["backoff"]["multiplier"]

SERVICE_B_URL = "http://127.0.0.1:8001/unstable"

@app.get("/execute")
def execute_with_retry():
    delay = INITIAL_DELAY

    for attempt in range(1, MAX_ATTEMPTS + 1):
        print(f"[Service A] Intento {attempt}/{MAX_ATTEMPTS}")

        try:
            response = requests.get(SERVICE_B_URL, timeout=5)

            if response.status_code == 200:
                print("[Service A] Operacion completada correctamente")
                return {
                    "status": "success",
                    "attempts": attempt,
                    "service_b_response": response.json()
                }

            if response.status_code not in (502, 503, 504):
                response.raise_for_status()

            print(f"[Service A] Error temporal: HTTP {response.status_code}")

        except requests.Timeout:
            print("[Service A] Tiempo de espera agotado")
        except requests.ConnectionError:
            print("[Service A] No se pudo conectar con Service B")

        if attempt < MAX_ATTEMPTS:
            print(f"[Service A] Esperando {delay} segundos antes del siguiente intento")
            time.sleep(delay)
            delay *= BACKOFF_MULTIPLIER

    print("[Service A] Se agotaron los intentos")
    raise HTTPException(status_code=503, detail="No fue posible completar la operacion")
