"""
DEMO en directo de la VC3 · NF3 — caso SMART CITY ("auditar las alertas").

Prepara los datos y el proyecto dbt de la videoconferencia. EJECUTAR UNA VEZ,
ANTES de la sesión:

    python demo/nf3_smartcity/preparar_demo.py

Nada de esto forma parte de la actividad evaluable (caso gaming). Es material de
demostración: el alumno puede ejecutarlo, romperlo y experimentar. No se entrega.

Estructura PARALELA a la actividad del NF3 (integridad con _SUCCESS + checksums,
baseline media vs mediana/MAD, calidad con dbt), con distinto tema para que el
patrón se vea pero la solución no se copie. IMPORTANTE: aquí las columnas SON
coherentes con Smart City (no hay fuga de nombres); el caso es el de demostración.

LA HISTORIA
-----------
"Una alerta de calidad del aire ha activado el protocolo de emergencia y ha
costado dinero. Antes de fiarnos de la siguiente, vamos a auditarla." Tres
frentes: ¿llegaron enteros los ficheros? ¿el umbral que disparó la alarma era
honesto? ¿la tabla de alertas cumple lo que promete?
"""

import hashlib
import json
import os
import shutil

import numpy as np
import pandas as pd

SEED = 7
BASE = os.path.dirname(os.path.abspath(__file__))
RAW = f"{BASE}/raw"
DIST = f"{RAW}/dist_ok"          # directorio "bueno": con _SUCCESS
INCOMP = f"{RAW}/dist_incompleto"  # directorio "malo": sin _SUCCESS

rng = np.random.default_rng(SEED)


def limpiar():
    shutil.rmtree(RAW, ignore_errors=True)
    os.makedirs(DIST, exist_ok=True)
    os.makedirs(INCOMP, exist_ok=True)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for bloque in iter(lambda: f.read(8192), b""):
            h.update(bloque)
    return h.hexdigest()


def frente_integridad():
    """Dos directorios distribuidos + un manifiesto de metadatos (sha256 + bytes).
    Uno está entero y declarado (_SUCCESS); el otro, ni completo ni declarado.
    Y un fichero del bueno se corrompe DESPUÉS de firmar el manifiesto."""
    manifiesto = {}

    # Directorio bueno: 4 particiones + _SUCCESS
    for i in range(4):
        p = f"{DIST}/part-{i}.csv"
        pd.DataFrame({"id": range(i * 100, (i + 1) * 100),
                      "lectura": np.round(rng.uniform(20, 60, 100), 1)}).to_csv(p, index=False)
        # Metadatos de cada pieza: su huella y su tamaño (como hace el log de Delta)
        manifiesto[f"part-{i}.csv"] = {"sha256": sha256(p), "bytes": os.path.getsize(p)}
    open(f"{DIST}/_SUCCESS", "w").close()  # el sello: "el job terminó entero"

    # Guardamos el manifiesto ANTES de corromper
    json.dump(manifiesto, open(f"{RAW}/manifiesto.json", "w"), indent=2)

    # Y AHORA corrompemos una partición SIN cambiar su tamaño: un solo dígito de
    # una lectura cambia (bit rot). El control de tamaño no lo ve; el checksum sí.
    p = f"{DIST}/part-2.csv"
    datos = bytearray(open(p, "rb").read())
    i = datos.index(b"\n") + 1            # primera fila de datos
    i = datos.index(b",", i) + 1          # primer carácter de la lectura
    datos[i] = ord(str((int(chr(datos[i])) + 1) % 10))   # p. ej. 45.3 -> 55.3
    open(p, "wb").write(bytes(datos))

    # Directorio incompleto: solo 2 particiones y SIN _SUCCESS
    for i in range(2):
        pd.DataFrame({"id": range(i * 100, (i + 1) * 100),
                      "lectura": np.round(rng.uniform(20, 60, 100), 1)}
                     ).to_csv(f"{INCOMP}/part-{i}.csv", index=False)
    # (a propósito: no se escribe _SUCCESS)


def frente_baseline():
    """Un sensor de velocidad de tráfico con atascos. La media se deja engañar;
    la mediana/MAD no. Calibrado para que salgan más anomalías con el robusto."""
    # 200 lecturas normales (~45 km/h) y 40 atascos severos (~8 km/h).
    # 40 basta para inflar σ tanto que media±3σ deja de detectarlos (enmascaramiento
    # total), mientras mediana/MAD los caza todos. Es el efecto que pide §3.2.
    normales = rng.normal(45, 4, 200)
    atascos = rng.normal(8, 2, 40)
    x = np.concatenate([normales, atascos])
    rng.shuffle(x)
    pd.DataFrame({"velocidad": np.round(x, 1)}).to_csv(f"{RAW}/sensor_velocidad.csv", index=False)


def frente_calidad_dbt():
    """La tabla stg_alertas: con nulos, duplicados, categorías inválidas y
    valores fuera de rango. Es el seed del proyecto dbt."""
    N = 1000
    df = pd.DataFrame({
        "id_alerta": list(range(N - 30)) + list(range(30)),   # 30 duplicados
        "severidad": rng.choice(["baja", "media", "alta", "critica"], N),
        "aqi": np.round(rng.uniform(0, 600, N), 1),            # índice calidad aire; algunos > 500
        "distrito": rng.choice(["Centro", "Ensanche", "Norte", "Sur"], N),
    })
    df.loc[rng.choice(N, 60, replace=False), "severidad"] = None          # 60 nulos
    df.loc[rng.choice(N, 2, replace=False), "severidad"] = "URGENTISIMA"  # 2 filas, 1 valor inválido
    # Datos fantasma (integridad referencial): alertas de un distrito que NO existe
    # en el catálogo. Va al final para no alterar los números anteriores.
    df.loc[rng.choice(N, 12, replace=False), "distrito"] = "Puerto"       # 12 fantasmas
    os.makedirs(f"{BASE}/dbt_calidad/seeds", exist_ok=True)
    df.to_csv(f"{BASE}/dbt_calidad/seeds/alertas_raw.csv", index=False)
    # El catálogo oficial de distritos (la tabla a la que apunta la alerta)
    pd.DataFrame({"distrito": ["Centro", "Ensanche", "Norte", "Sur"]}).to_csv(
        f"{BASE}/dbt_calidad/seeds/distritos.csv", index=False)
    return df


if __name__ == "__main__":
    limpiar()
    frente_integridad()
    frente_baseline()
    df = frente_calidad_dbt()
    print("[1/3] Integridad : dist_ok/ (4 partes + _SUCCESS, 1 corrupta SIN cambiar de tamaño)"
          " + dist_incompleto/ (2 partes, sin _SUCCESS)")
    print("[2/3] Baseline   : sensor_velocidad.csv (200 normales + 40 atascos)")
    print(f"[3/3] Calidad dbt: alertas_raw.csv ({len(df)} filas: 60 nulos, 30 ids duplicados, "
          f"~fuera de rango, 1 categoría inválida, 12 distritos fantasma) + distritos.csv")
    print("\n[OK] Demo lista.")
    print("      El proyecto dbt está en demo/nf3_smartcity/dbt_calidad/")
    print("      >> Ejecuta el cuaderno una vez para verificar y anota tus números.")
