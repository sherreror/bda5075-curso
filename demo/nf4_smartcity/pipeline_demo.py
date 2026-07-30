"""
Pipeline instrumentado de la DEMO de la VC4 · NF4 — caso SMART CITY.

El pipeline procesa eventos de la red de sensores de la ciudad y expone métricas
Prometheus (los tres pilares de observabilidad: throughput, errores, latencia,
y la estrella del núcleo: frescura del dato).

NO forma parte de la actividad evaluable (caso gaming). Es material de demo.

Estructura PARALELA a `NF4_rediseno_pipeline.py`:
  - mismos nombres de métrica y misma mecánica determinista,
  - dos modos: normal / incidente,
  - usable como servicio (expone /metrics) o como librería (lo usa el notebook).

Uso como SERVICIO (para abrir /metrics en el navegador, como la Spark UI del NF2):
    python demo/nf4_smartcity/pipeline_demo.py --modo normal --puerto 8000
    python demo/nf4_smartcity/pipeline_demo.py --modo incidente --puerto 8000

Uso como LIBRERÍA (lo hace el cuaderno):
    from pipeline_demo import procesar, latencias_demo
    reg = procesar("incidente")
"""

import argparse
import time

from prometheus_client import (Counter, Gauge, Histogram, CollectorRegistry,
                               generate_latest, start_http_server)

N_EVENTOS = 10_000

# Dos perfiles. En 'incidente' los tres SLO revientan a la vez: es lo que
# permite enseñar que la degradación es simultánea, no de una sola métrica.
PERFIL = {
    "normal":    {"tasa_error": 0.01, "latencia": 0.05, "frescura_s": 5},
    "incidente": {"tasa_error": 0.30, "latencia": 0.80, "frescura_s": 300},
}


def procesar(modo: str, registry: CollectorRegistry | None = None) -> CollectorRegistry:
    """Procesa el stream de sensores y devuelve un registry Prometheus."""
    reg = registry or CollectorRegistry()
    p = PERFIL[modo]

    eventos = Counter("eventos_procesados_total", "Lecturas de sensor procesadas", registry=reg)
    errores = Counter("errores_total", "Errores de procesamiento", registry=reg)
    latencia = Histogram("latencia_procesamiento_segundos", "Latencia por lectura",
                         buckets=(0.05, 0.1, 0.25, 0.5, 1.0, 2.5), registry=reg)
    frescura = Gauge("datos_frescura_segundos", "Segundos desde la última lectura válida",
                     registry=reg)
    cola = Gauge("cola_pendiente", "Lecturas en cola", registry=reg)

    cada = int(round(1 / p["tasa_error"]))   # 1 de cada N falla -> determinista
    for i in range(N_EVENTOS):
        eventos.inc()
        latencia.observe(p["latencia"])
        if i % cada == 0:
            errores.inc()

    frescura.set(p["frescura_s"])
    cola.set(0 if modo == "normal" else 1200)
    return reg


def latencias_demo() -> list[float]:
    """Las 10 latencias del ejemplo canónico de la teoría (§4.2, percentiles).
    Nueve peticiones rápidas y una lenta: la media cumple el SLO, el p95 no."""
    return [0.05, 0.05, 0.06, 0.05, 0.07, 0.05, 0.06, 0.05, 0.05, 4.00]


def metricas_texto(reg: CollectorRegistry) -> str:
    return generate_latest(reg).decode()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--modo", choices=["normal", "incidente"], default="normal")
    ap.add_argument("--puerto", type=int, default=8000)
    args = ap.parse_args()

    reg = procesar(args.modo)
    start_http_server(args.puerto, registry=reg)
    print(f"[pipeline demo] modo={args.modo}  ->  http://localhost:{args.puerto}/metrics")
    print("Ctrl+C para parar.  (En Codespaces, abre el puerto en la pestaña 'Ports'.)")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[pipeline demo] parado.")
