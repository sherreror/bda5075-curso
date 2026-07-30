"""
DEMO en directo de la VC2 · NF2 — caso SMART CITY ("el motor de la ciudad").

Prepara los datos de la videoconferencia. EJECUTAR UNA VEZ, ANTES de la sesión:

    python demo/nf2_smartcity/preparar_demo.py

Nada de esto forma parte de la actividad evaluable (caso gaming). Es material de
demostración: el alumno puede ejecutarlo, romperlo y experimentar. No se entrega.

Estructura PARALELA a `NF2_rediseno_generar_datos.py` (tabla de hechos grande +
dimensión para el join + micro-batches para streaming), con distinto tema y
distinta escala, para que el patrón se vea pero la solución no se pueda copiar.

LA HISTORIA QUE SOSTIENEN ESTOS DATOS
-------------------------------------
"El panel de tráfico de la ciudad tardaba 40 minutos en actualizarse. Vamos a
arreglarlo." El dato tiene una anomalia real escondida: en la hora punta de la
manana, una via concreta se satura muy por encima de su media -> se ve con una
funcion de ventana, no con una media global. Esa es la carga util de la demo.
"""

import json
import os
import shutil

import numpy as np
import pandas as pd

SEED = 7  # distinto del 42 de la actividad: son datos distintos, a propósito
BASE = os.path.dirname(os.path.abspath(__file__))
RAW = f"{BASE}/raw"

N_MEDICIONES = 2_000_000    # tabla de hechos grande (para que el shuffle se note)
N_VIAS = 40                 # dimensión para el join
N_STREAM_FILES = 6          # micro-batches de streaming
N_POR_STREAM = 5_000

TIPOS = ["trafico", "aire", "ruido"]

rng = np.random.default_rng(SEED)


def limpiar():
    shutil.rmtree(RAW, ignore_errors=True)
    os.makedirs(f"{RAW}/stream_in", exist_ok=True)


def tabla_de_hechos():
    """2 M de mediciones de sensores urbanos. La tabla que se procesa distribuido."""
    ts = pd.date_range("2025-03-01", periods=N_MEDICIONES, freq="s")
    id_via = rng.integers(1, N_VIAS + 1, N_MEDICIONES)
    hora = ts.hour.values
    tipo = rng.choice(TIPOS, N_MEDICIONES, p=[0.45, 0.35, 0.20])

    # Señal base + una anomalía real: la vía 7, en la hora punta (8 h), se dispara.
    valor = rng.gamma(shape=3.0, scale=20.0, size=N_MEDICIONES)
    anomalia = (id_via == 7) & (hora == 8) & (tipo == "trafico")
    valor = np.where(anomalia, valor * 2.4, valor)

    df = pd.DataFrame({
        "id_medicion": np.arange(N_MEDICIONES),
        "id_via": id_via,
        "hora": hora,
        "timestamp": ts.astype(str),
        "tipo": tipo,
        "valor": np.round(valor, 2),
    })
    df.to_parquet(f"{RAW}/mediciones.parquet", index=False)
    return len(df)


def dimension_vias():
    """Tabla de dimensión pequeña: id_via -> distrito. Para el join."""
    distritos = ["Centro", "Ensanche", "Norte", "Sur", "Litoral"]
    vias = pd.DataFrame({
        "id_via": np.arange(1, N_VIAS + 1),
        "nombre_via": [f"Via-{i:03d}" for i in range(1, N_VIAS + 1)],
        "distrito": rng.choice(distritos, N_VIAS),
    })
    vias.to_csv(f"{RAW}/vias.csv", index=False)
    return len(vias)


def micro_batches():
    """Ficheros que llegan de uno en uno: la 'tabla infinita' del streaming."""
    for i in range(N_STREAM_FILES):
        lote = pd.DataFrame({
            "id_medicion": np.arange(i * N_POR_STREAM, (i + 1) * N_POR_STREAM),
            "id_via": rng.integers(1, N_VIAS + 1, N_POR_STREAM),
            "hora": rng.integers(0, 24, N_POR_STREAM),
            "timestamp": pd.Timestamp("2025-03-02") .isoformat(),
            "tipo": rng.choice(TIPOS, N_POR_STREAM, p=[0.45, 0.35, 0.20]),
            "valor": np.round(rng.gamma(3.0, 20.0, N_POR_STREAM), 2),
        })
        lote.to_json(f"{RAW}/stream_in/lote_{i}.json", orient="records", lines=True)
    return N_STREAM_FILES * N_POR_STREAM


def mb(path):
    return os.path.getsize(path) / 1024 ** 2


if __name__ == "__main__":
    limpiar()
    n1 = tabla_de_hechos()
    n2 = dimension_vias()
    n3 = micro_batches()
    print(f"[1/3] raw/mediciones.parquet  {n1:>9,} filas  ({mb(f'{RAW}/mediciones.parquet'):.1f} MB)")
    print(f"[2/3] raw/vias.csv            {n2:>9,} filas  (dimensión para el join)")
    print(f"[3/3] raw/stream_in/          {N_STREAM_FILES} ficheros x {N_POR_STREAM:,}  ({n3:,} filas)")
    print("\n[OK] Demo lista.")
    print("      >> Ejecuta el cuaderno una vez y anota TUS tiempos en el guion.")
