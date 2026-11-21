from fastapi import FastAPI, Response

app = FastAPI(title="Retry Pattern - Service B")

request_count = 0

@app.get("/unstable")
def unstable_service(response: Response):
    global request_count
    request_count += 1

    print(f"[Service B] Solicitud #{request_count}")

    if request_count <= 2:
        print("[Service B] Respuesta: 503 Service Unavailable")
        response.status_code = 503
        return {"status": "error", "message": "Servicio temporalmente no disponible", "attempt": request_count}

    print("[Service B] Respuesta: 200 OK")
    return {"status": "success", "message": "Servicio disponible", "attempt": request_count}
