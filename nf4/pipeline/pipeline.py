"""
Pipeline del SERVIDOR DE JUEGO (NF4 / RA4) — caso gaming instrumentado con Prometheus.

- Procesa un stream determinista de eventos de juego.
- Expone métricas Prometheus (los 3 pilares de observabilidad se reflejan aquí
  como métricas + logs): throughput, errores, latencia, frescura del dato.
- Dos modos:
    normal    -> tasa de error ~1%, baja latencia, dato fresco
    incidente -> tasa de error ~33% (1 de cada 3), alta latencia, dato obsoleto (degradación)

Uso como servicio (para el stack Docker/Prometheus en Codespaces):
    python pipeline.py --modo incidente --puerto 8000
Uso como librería (lo hace la corrección):
    from pipeline import procesar; reg = procesar("incidente")
"""
import argparse, time
from prometheus_client import (Counter, Gauge, Histogram, CollectorRegistry,
                               generate_latest, start_http_server)

N_EVENTOS = 10_000
PERFIL = {
    "normal":    {"tasa_error": 0.01, "latencia": 0.05, "frescura_s": 5},
    "incidente": {"tasa_error": 0.30, "latencia": 0.80, "frescura_s": 300},
}


def procesar(modo: str, registry: CollectorRegistry | None = None) -> CollectorRegistry:
    """Procesa el stream y devuelve un registry Prometheus con las métricas."""
    reg = registry or CollectorRegistry()
    p = PERFIL[modo]

    eventos = Counter("eventos_procesados_total", "Eventos procesados", registry=reg)
    errores = Counter("errores_total", "Errores de procesamiento", registry=reg)
    latencia = Histogram("latencia_procesamiento_segundos", "Latencia por evento",
                         buckets=(0.05, 0.1, 0.25, 0.5, 1.0, 2.5), registry=reg)
    frescura = Gauge("datos_frescura_segundos", "Segundos desde el último dato válido", registry=reg)
    cola = Gauge("cola_pendiente", "Eventos en cola", registry=reg)

    # 1 de cada (1/tasa_error) eventos falla -> determinista
    cada = int(round(1 / p["tasa_error"]))
    for i in range(N_EVENTOS):
        eventos.inc()
        latencia.observe(p["latencia"])
        if i % cada == 0:
            errores.inc()
    frescura.set(p["frescura_s"])
    cola.set(0 if modo == "normal" else 1200)
    return reg


def metricas_texto(reg) -> str:
    return generate_latest(reg).decode()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--modo", choices=["normal", "incidente"], default="normal")
    ap.add_argument("--puerto", type=int, default=8000)
    a = ap.parse_args()
    # Servicio para Prometheus: expone /metrics en el puerto indicado
    reg = procesar(a.modo)
    start_http_server(a.puerto, registry=reg)
    print(f"[pipeline modo={a.modo}] métricas en http://localhost:{a.puerto}/metrics")
    while True:
        time.sleep(5)
