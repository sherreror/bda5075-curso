"""
Generador de datos NF2 (RA2) — caso GAMING: "el motor predictivo".

Genera, de forma determinista (seed fijo):
  - eventos.parquet : tabla grande de eventos de juego (para procesamiento distribuido)
  - regiones.csv    : tabla de dimensión, una fila por región del mundo (para el join)
  - stream_in/      : varios ficheros que simulan micro-batches para streaming

Reutilizable por caso: el "tema" se define en CONFIG_CASO; la estructura
(tabla de hechos grande + dimensión + micro-batches) se mantiene constante.

Uso (desde la carpeta del núcleo, nf2/):
    python datos/generar_datos.py --salida datos/raw
"""
import argparse, os, shutil
import numpy as np
import pandas as pd

SEED = 42
N_EVENTOS = 600_000
N_REGIONES = 40
N_STREAM_FILES = 6
N_POR_STREAM = 5_000

# Nombres fijos (no consumen aleatoriedad: el contrato no depende de ellos).
REGIONES_GAMING = [
    "Bosque de Alba", "Cañon Rojo", "Puerto Sirena", "Cumbre Helada",
    "Llanura de Ceniza", "Ruinas de Kael", "Bahia Turquesa", "Paso del Lobo",
    "Cripta Sumergida", "Meseta Ambar", "Selva Umbria", "Faro Olvidado",
    "Dunas de Sal", "Valle Espejo", "Fortaleza Negra", "Isla Tormenta",
    "Jardin Colgante", "Mina Profunda", "Estepa Gris", "Arrecife Coral",
    "Templo del Eco", "Glaciar Partido", "Bosque Petrificado", "Ciudad Hundida",
    "Paramo Violeta", "Torre Vigia", "Delta Salvaje", "Cantera Vieja",
    "Puente Roto", "Lago Nebuloso", "Colinas Doradas", "Foso Escarlata",
    "Bastion Norte", "Caverna Azul", "Pradera Alta", "Astillero Muerto",
    "Sendero Blanco", "Volcan Durmiente", "Marisma Lenta", "Atalaya Sur",
]

CONFIG_CASO = {
    "gaming": {
        "tipos": ["combate", "exploracion", "social"],
        "umbral_critico": 90.0,   # valor por encima del cual el evento es "crítico"
        "dim_nombre": "nombre_region",
    },
}


def generar(caso, salida):
    cfg = CONFIG_CASO[caso]
    np.random.seed(SEED)
    if os.path.exists(salida):
        shutil.rmtree(salida)
    os.makedirs(f"{salida}/stream_in", exist_ok=True)

    tipos = cfg["tipos"]
    ts = pd.date_range("2025-03-01", periods=N_EVENTOS, freq="s")

    # -------- Tabla de hechos (grande) --------
    eventos = pd.DataFrame({
        "id_evento": np.arange(N_EVENTOS),
        "id_jugador": np.random.randint(1, 201, N_EVENTOS),
        "id_region": np.random.randint(1, N_REGIONES + 1, N_EVENTOS),
        "timestamp": ts.astype(str),
        "tipo": np.random.choice(tipos, N_EVENTOS, p=[0.45, 0.35, 0.20]),
        "valor": np.round(np.random.gamma(shape=3.0, scale=20.0, size=N_EVENTOS), 2),
    })
    eventos.to_parquet(f"{salida}/eventos.parquet", index=False)

    # -------- Dimensión: regiones --------
    # OJO al orden: los nombres son una lista fija y NO consumen aleatoriedad,
    # así que `continente` recibe exactamente el mismo tramo de np.random que
    # antes. Cambiar los nombres no mueve ningún valor del contrato.
    regiones = pd.DataFrame({
        "id_region": np.arange(1, N_REGIONES + 1),
        cfg["dim_nombre"]: REGIONES_GAMING[:N_REGIONES],
        "continente": np.random.randint(1, 6, N_REGIONES),
    })
    regiones.to_csv(f"{salida}/regiones.csv", index=False)

    # -------- Micro-batches para streaming --------
    for i in range(N_STREAM_FILES):
        b = pd.DataFrame({
            "id_evento": np.arange(i * N_POR_STREAM, (i + 1) * N_POR_STREAM),
            "id_region": np.random.randint(1, N_REGIONES + 1, N_POR_STREAM),
            "tipo": np.random.choice(tipos, N_POR_STREAM, p=[0.45, 0.35, 0.20]),
            "valor": np.round(np.random.gamma(3.0, 20.0, N_POR_STREAM), 2),
        })
        b.to_parquet(f"{salida}/stream_in/batch_{i:02d}.parquet", index=False)

    print(f"[OK] Caso '{caso}': eventos.parquet={N_EVENTOS}, regiones.csv={N_REGIONES}, "
          f"stream_in={N_STREAM_FILES}x{N_POR_STREAM}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--caso", default="gaming", choices=sorted(CONFIG_CASO))
    ap.add_argument("--salida", required=True,
                    help="ruta de salida; desde nf2/ usa: --salida datos/raw")
    a = ap.parse_args()
    generar(a.caso, a.salida)
