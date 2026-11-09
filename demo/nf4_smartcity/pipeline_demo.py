"""
Pipeline instrumentado de la DEMO de la VC4 · NF4 — caso SMART CITY.

El pipeline procesa lecturas de la red de sensores de la ciudad y expone métricas
Prometheus: throughput, errores, latencia y la estrella del núcleo, la frescura del dato.

NO forma parte de la actividad evaluable (caso gaming). Es material de demo.

Mismos NOMBRES de métrica y misma mecánica que el pipeline de la actividad, pero con
CIFRAS PROPIAS (otro perfil normal/incidente), para que la demo no enseñe los valores que
comprueba la corrección automática.

Uso como SERVICIO (para abrir /metrics en el navegador, como la Spark UI del NF2):
    python demo/nf4_smartcity/pipeline_demo.py --modo normal --puerto 8000
    python demo/nf4_smartcity/pipeline_demo.py --modo incidente --puerto 8000
  En modo servicio el pipeline SIGUE TRABAJANDO: cada segundo procesa otro lote, así que
  al recargar /metrics ves los Counters subir. (El pipeline de la actividad, en cambio,
  procesa una vez y se queda quieto: lo explica la teoría, §4.7.)

Uso como LIBRERÍA (lo hace el cuaderno; resultado determinista):
    from pipeline_demo import procesar, latencias_demo
    reg = procesar("incidente")
"""

import argparse
import time

from prometheus_client import (Counter, Gauge, Histogram, CollectorRegistry,
                               generate_latest, start_http_server)

N_EVENTOS = 10_000
LOTE_SERVICIO = 200          # lecturas por segundo en modo servicio

# Dos perfiles. En 'incidente' los tres SLO revientan a la vez.
#   normal    -> error 2 %,  latencia 0,04 s, frescura 8 s    (todo dentro del SLO)
#   incidente -> error 25 %, latencia 0,9 s,  frescura 240 s  (los tres fuera)
PERFIL = {
    "normal":    {"tasa_error": 0.02, "latencia": 0.04, "frescura_s": 8,   "cola": 0},
    "incidente": {"tasa_error": 0.25, "latencia": 0.90, "frescura_s": 240, "cola": 900},
}


def _instrumentos(reg: CollectorRegistry) -> dict:
    return {
        "eventos": Counter("eventos_procesados_total", "Lecturas de sensor procesadas", registry=reg),
        "errores": Counter("errores_total", "Errores de procesamiento", registry=reg),
        "latencia": Histogram("latencia_procesamiento_segundos", "Latencia por lectura",
                              buckets=(0.05, 0.1, 0.25, 0.5, 1.0, 2.5), registry=reg),
        "frescura": Gauge("datos_frescura_segundos", "Segundos desde la última lectura válida",
                          registry=reg),
        "cola": Gauge("cola_pendiente", "Lecturas en cola", registry=reg),
    }


def _procesar_lote(m: dict, p: dict, n: int, inicio: int = 0) -> None:
    cada = int(round(1 / p["tasa_error"]))   # 1 de cada N falla -> determinista
    for i in range(inicio, inicio + n):
        m["eventos"].inc()
        m["latencia"].observe(p["latencia"])
        if i % cada == 0:
            m["errores"].inc()
    m["frescura"].set(p["frescura_s"])
    m["cola"].set(p["cola"])


def procesar(modo: str, registry: CollectorRegistry | None = None) -> CollectorRegistry:
    """Procesa N_EVENTOS lecturas y devuelve un registry Prometheus (determinista)."""
    reg = registry or CollectorRegistry()
    _procesar_lote(_instrumentos(reg), PERFIL[modo], N_EVENTOS)
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

    reg = CollectorRegistry()
    m = _instrumentos(reg)
    p = PERFIL[args.modo]
    _procesar_lote(m, p, N_EVENTOS)
    start_http_server(args.puerto, registry=reg)
    print(f"[pipeline demo] modo={args.modo}  ->  http://localhost:{args.puerto}/metrics", flush=True)
    print("Recarga la página: los Counters suben. Ctrl+C para parar.", flush=True)
    print("(En Codespaces, abre el puerto en la pestaña 'Ports'.)", flush=True)
    hechos = N_EVENTOS
    try:
        while True:
            time.sleep(1)
            _procesar_lote(m, p, LOTE_SERVICIO, inicio=hechos)
            hechos += LOTE_SERVICIO
    except KeyboardInterrupt:
        print("\n[pipeline demo] parado.")
