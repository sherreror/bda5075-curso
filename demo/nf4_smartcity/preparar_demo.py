"""
DEMO en directo de la VC4 · NF4 — caso SMART CITY ("el pipeline verde y roto").

Prepara los datos de la videoconferencia. EJECUTAR UNA VEZ, ANTES de la sesión:

    python demo/nf4_smartcity/preparar_demo.py

Nada de esto forma parte de la actividad evaluable (caso gaming). Es material de
demostración: el alumno puede ejecutarlo, romperlo y experimentar. No se entrega.

LA HISTORIA
-----------
El pipeline de anoche salió SUCCESS. En verde. Con su _SUCCESS y todo. Y esta
mañana los datos son basura: 47 de los 50 sensores reportan; 3 llevan horas
mudos. El job "terminó bien" porque procesó lo que le llegó — pero le llegó de
47, no de 50. Ningún control del NF3 lo detecta: lo que llegó es válido. Solo un
MONITOR de VOLUMEN (¿llegó TODO?) o de conteo de entidades lo caza. Esa es la
diferencia NF3 (tests) vs NF4 (monitores) hecha dato.
"""

import json
import os
import shutil

import numpy as np
import pandas as pd

SEED = 7
BASE = os.path.dirname(os.path.abspath(__file__))
RAW = f"{BASE}/raw"

N_SENSORES_ESPERADOS = 50
N_SENSORES_MUDOS = 3            # los que "se callaron" -> nadie lo nota por umbral
HORAS = 24

rng = np.random.default_rng(SEED)


def limpiar():
    shutil.rmtree(RAW, ignore_errors=True)
    os.makedirs(RAW, exist_ok=True)


def lote_de_hoy():
    """El lote que el pipeline procesó 'con éxito'. Faltan 3 sensores enteros,
    pero lo que hay es perfectamente válido: pasa todos los tests del NF3."""
    reportan = list(range(N_SENSORES_ESPERADOS - N_SENSORES_MUDOS))  # 0..46
    filas = []
    for s in reportan:
        for h in range(HORAS):
            filas.append({"id_sensor": s, "hora": h,
                          "lectura": round(float(rng.uniform(20, 60)), 1)})
    df = pd.DataFrame(filas)
    df.to_csv(f"{RAW}/lote_hoy.csv", index=False)

    # El histórico dice cuántos sensores REPORTAN un día normal: 50.
    manifiesto = {"sensores_esperados": N_SENSORES_ESPERADOS,
                  "sensores_hoy": df["id_sensor"].nunique(),
                  "filas_hoy": len(df),
                  "filas_dia_normal": N_SENSORES_ESPERADOS * HORAS}
    json.dump(manifiesto, open(f"{RAW}/manifiesto.json", "w"), indent=2)
    return df, manifiesto


if __name__ == "__main__":
    limpiar()
    df, m = lote_de_hoy()
    print(f"[1/1] raw/lote_hoy.csv  {len(df):>6,} filas  "
          f"({m['sensores_hoy']} sensores de {m['sensores_esperados']} esperados)")
    print()
    print("      El lote 'salió SUCCESS' y todo lo que contiene es VÁLIDO...")
    print(f"      ...pero faltan {N_SENSORES_ESPERADOS - m['sensores_hoy']} sensores enteros.")
    print(f"      filas hoy: {m['filas_hoy']:,}  |  un día normal: {m['filas_dia_normal']:,}")
    print("\n[OK] Demo lista. Ejecuta el cuaderno para ver el pipeline verde y roto.")
