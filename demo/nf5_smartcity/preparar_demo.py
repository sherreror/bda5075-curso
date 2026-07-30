"""
DEMO en directo de la VC5 · NF5 — caso SMART CITY ("del dato a la decisión").

Prepara los datos de la videoconferencia. EJECUTAR UNA VEZ, ANTES de la sesión:

    python demo/nf5_smartcity/preparar_demo.py

Nada de esto forma parte de la actividad evaluable (caso gaming). Es material de
demostración: el alumno puede ejecutarlo, romperlo y experimentar. No se entrega.

Estructura PARALELA a `NF5_rediseno_generar_datos.py` (tabla de hechos grande de
eventos + alertas + dimensión de zonas), con distinto tema, distinta escala y
—crucial— una zona problemática DISTINTA de la del caso gaming, para que el
salto observación->decisión se enseñe sin revelar el insight evaluable.

LA HISTORIA
-----------
El alcalde entra y pregunta: "¿Dónde pongo el presupuesto de calidad del aire el
año que viene?". Hay 2 años de datos. La respuesta correcta NO es la zona con más
alertas en bruto (esa es el Centro, que además tiene todo el tráfico): es la que
tiene más alertas DE LO QUE SU actividad explica. En la demo esa zona es el
LITORAL (poca actividad, tasa de alerta alta -> algo estructural, no circulación).
"""

import os
import shutil

import numpy as np
import pandas as pd

SEED = 7
BASE = os.path.dirname(os.path.abspath(__file__))
RAW = f"{BASE}/raw"

N_EVENTOS = 2_000_000
N_ZONAS = 5

# Reparto de actividad (eventos) por zona. El Centro concentra el tráfico.
PESO_EVENTOS = {1: 0.34, 2: 0.14, 3: 0.24, 4: 0.20, 5: 0.08}   # zona 5 = Litoral: poca actividad
# Tasa de alerta por zona. El Litoral tiene tasa ALTA pese a poca actividad:
# es el patrón que la cifra bruta esconde y el análisis por tasa revela.
TASA_ALERTA = {1: 0.006, 2: 0.006, 3: 0.006, 4: 0.006, 5: 0.028}
NOMBRES = {1: "Centro", 2: "Ensanche", 3: "Norte", 4: "Sur", 5: "Litoral"}
TIPOS = ["trafico", "industrial", "domestico"]

rng = np.random.default_rng(SEED)


def limpiar():
    shutil.rmtree(RAW, ignore_errors=True)
    os.makedirs(RAW, exist_ok=True)


def generar_eventos():
    zonas = np.arange(1, N_ZONAS + 1)
    p = np.array([PESO_EVENTOS[z] for z in zonas])
    df = pd.DataFrame({
        "id_evento": np.arange(N_EVENTOS),
        "id_zona": rng.choice(zonas, N_EVENTOS, p=p),
        "tipo": rng.choice(TIPOS, N_EVENTOS),
        "valor": np.round(rng.gamma(3, 20, N_EVENTOS), 2),
    })
    df.to_parquet(f"{RAW}/eventos.parquet", index=False)
    return df


def generar_alertas(eventos):
    tasa = eventos["id_zona"].map(TASA_ALERTA).values
    dispara = rng.random(len(eventos)) < tasa
    al = eventos[dispara].copy()
    al["severidad"] = rng.choice(["baja", "media", "critica"], len(al), p=[0.5, 0.35, 0.15])
    al = al[["id_evento", "id_zona", "severidad"]].reset_index(drop=True)
    al.to_parquet(f"{RAW}/alertas.parquet", index=False)
    return al


def generar_zonas():
    z = pd.DataFrame({
        "id_zona": np.arange(1, N_ZONAS + 1),
        "nombre": [NOMBRES[i] for i in range(1, N_ZONAS + 1)],
        "poblacion": rng.integers(20_000, 200_000, N_ZONAS),
    })
    z.to_csv(f"{RAW}/zonas.csv", index=False)
    return z


if __name__ == "__main__":
    limpiar()
    ev = generar_eventos()
    al = generar_alertas(ev)
    z = generar_zonas()

    print(f"[1/3] raw/eventos.parquet  {len(ev):>9,} filas")
    print(f"[2/3] raw/alertas.parquet  {len(al):>9,} filas")
    print(f"[3/3] raw/zonas.csv        {len(z):>9} filas")
    print()
    por_zona = ev.groupby("id_zona").size().to_dict()
    al_zona = al.groupby("id_zona").size().to_dict()
    print("      [pista docente] eventos por zona:", por_zona)
    print("      [pista docente] alertas por zona:", al_zona)
    print("      [pista docente] la zona con más alertas EN BRUTO no es la más problemática por TASA.")
    print("\n[OK] Demo lista. El data mart lo construye el cuaderno en directo.")
