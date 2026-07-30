"""
DEMO en directo de la VC1 · NF1 — caso SMART CITY.

Prepara los datos de la videoconferencia. EJECUTAR UNA VEZ, ANTES de la sesión:

    python demo/nf1_smartcity/preparar_demo.py

Nada de esto forma parte de la actividad evaluable (caso gaming). Es material de
demostración: el alumno puede ejecutarlo, romperlo y experimentar. No se entrega.

Estructura deliberadamente PARALELA a `NF1_rediseno_generar_datos.py` (CSV tabular
sucio + JSON anidado + fichero extra), con distinto tema, distintas columnas y
distintos umbrales: el patrón se ve, la solución no se copia.

LA HISTORIA QUE SOSTIENEN ESTOS DATOS
-------------------------------------
Movilidad pregunta: "¿tenemos un problema de NO2 en el Ensanche?".
  · raw/sensores.csv    -> lo que llega del sensor: sucio. Con esto NO se puede responder.
  · bench/lecturas.*    -> el histórico acumulado (1 M de lecturas), ya limpio.
Hay señal REAL escondida dentro: el Ensanche está peor, y su exceso se concentra en
dos franjas horarias. Esa es la respuesta del final de la VC (observación -> insight).
"""

import json
import os
import shutil

import numpy as np
import pandas as pd

SEED = 7  # distinto del 42 de la actividad: son datos distintos, a propósito
BASE = os.path.dirname(os.path.abspath(__file__))
RAW, BENCH, PROC = f"{BASE}/raw", f"{BASE}/bench", f"{BASE}/proc"

N_LECTURAS = 5_000        # Demo A: pequeño, para mirarlo a ojo
N_BENCH = 1_000_000       # Demo B: grande, PRE-escrito (en directo solo se lee)
N_ESTACIONES = 50         # Demo D

# Señal: NO2 base por estación (ug/m3). El Ensanche está peor. Esto es lo que hay
# que poder ver al final... y lo que el dato sucio impide ver al principio.
BASE_NO2 = {"centro": 42.0, "ensanche": 63.0, "norte": 28.0, "sur": 35.0}
# Picos de trafico: entrada y salida. El exceso del Ensanche vive aqui.
PICOS = {7: 12.0, 8: 22.0, 9: 14.0, 18: 10.0, 19: 20.0, 20: 12.0}

rng = np.random.default_rng(SEED)


def limpiar():
    for d in (RAW, BENCH, PROC):
        shutil.rmtree(d, ignore_errors=True)
        os.makedirs(d, exist_ok=True)


def fuente_1_sensores():
    """CSV tabular sucio: la cara del problema (Demo A)."""
    # Cuatro estaciones reales escritas de once formas distintas
    variantes = {"centro": ["Centro", "centro ", "CENTRO", " Centro"],
                 "ensanche": ["Ensanche", "ensanche", "ENSANCHE"],
                 "norte": ["Norte", "norte "],
                 "sur": ["Sur", "sur"]}

    canonico = rng.choice(list(BASE_NO2), N_LECTURAS)
    ts = pd.date_range("2025-01-01", periods=N_LECTURAS, freq="h")

    no2 = np.array([BASE_NO2[c] for c in canonico])
    no2 = no2 + np.array([PICOS.get(h, 0.0) for h in ts.hour])
    no2 = np.round(no2 + rng.normal(0, 6, N_LECTURAS), 1)

    df = pd.DataFrame({
        "id_lectura": np.arange(N_LECTURAS),
        "timestamp": ts.astype(str),
        "estacion": [rng.choice(variantes[c]) for c in canonico],
        "no2": no2,
        "ruido_db": np.round(rng.uniform(35.0, 85.0, N_LECTURAS), 1).astype(str),
    })

    # (a) Huecos: el sensor no reporto
    df.loc[rng.choice(N_LECTURAS, 300, replace=False), "no2"] = np.nan
    # (b) Sensor averiado: valor imposible que dispara la media -> punchline de la Demo A
    df.loc[rng.choice(N_LECTURAS, 60, replace=False), "no2"] = 9999.0
    # (c) Centinela de texto: envenena el TIPO de la columna entera
    df.loc[rng.choice(N_LECTURAS, 150, replace=False), "ruido_db"] = "ERROR"

    df.to_csv(f"{RAW}/sensores.csv", index=False)
    return len(df)


def fuente_2_meteorologia():
    """JSON anidado, tal cual lo devolveria una API (Demo D)."""
    api = [{
        "id_estacion": int(i),
        "nombre": f"EST-{i:03d}",
        "ubicacion": {"lat": round(float(rng.uniform(41.36, 41.42)), 5),
                      "lon": round(float(rng.uniform(2.12, 2.20)), 5)},
        "medida": {"temp": round(float(rng.uniform(5.0, 32.0)), 1),
                   "humedad": int(rng.integers(30, 95)),
                   "viento_kmh": round(float(rng.uniform(0.0, 45.0)), 1)},
    } for i in range(N_ESTACIONES)]

    with open(f"{RAW}/meteorologia.json", "w", encoding="utf-8") as f:
        json.dump(api, f, ensure_ascii=False, indent=2)
    return len(api)


def fuente_3_historico():
    """1 M de filas YA escritas a disco: en directo solo se lee (Demos B y C)."""
    ts = pd.date_range("2024-01-01", periods=N_BENCH, freq="s")
    estacion = rng.choice(list(BASE_NO2), N_BENCH)

    no2 = np.array([BASE_NO2[e] for e in estacion])
    no2 = no2 + np.array([PICOS.get(h, 0.0) for h in ts.hour])
    no2 = np.round(no2 + rng.normal(0, 6, N_BENCH), 2)

    big = pd.DataFrame({
        "id_lectura": np.arange(N_BENCH),
        "timestamp": ts.astype(str),
        "estacion": estacion,
        "no2": no2,
        "ruido_db": np.round(rng.uniform(35.0, 85.0, N_BENCH), 2),
        "temp": np.round(rng.uniform(0.0, 40.0, N_BENCH), 2),
    })
    big.to_csv(f"{BENCH}/lecturas.csv", index=False)
    big.to_parquet(f"{BENCH}/lecturas.parquet", index=False)
    return len(big)


def mb(path):
    return os.path.getsize(path) / 1024 ** 2


if __name__ == "__main__":
    limpiar()
    n1 = fuente_1_sensores()
    n2 = fuente_2_meteorologia()
    print(f"[1/3] raw/sensores.csv        {n1:>9,} filas sucias        (Demo A)")
    print(f"[2/3] raw/meteorologia.json   {n2:>9,} documentos anidados (Demo D)")
    print(f"[3/3] bench/  escribiendo {N_BENCH:,} filas... (justo lo que NO hacemos en directo)")
    fuente_3_historico()

    print("\n[OK] Demo lista.")
    print(f"      bench/lecturas.csv      {mb(f'{BENCH}/lecturas.csv'):>8.1f} MB")
    print(f"      bench/lecturas.parquet  {mb(f'{BENCH}/lecturas.parquet'):>8.1f} MB")
    print("      proc/                     vacio (lo llena la Demo C, en directo)")
    print("\n      >> Ejecuta el notebook una vez y anota los tiempos en el guion.")
