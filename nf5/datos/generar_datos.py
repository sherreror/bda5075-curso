"""
Generador NF5 (RA5) — caso GAMING: "convertir datos en acción".

Tres dominios que el alumno combinará en un Data Mart (RA5.1/5.4):
  - eventos.parquet  : partidas por modo de juego (tipo, valor, region)
  - alertas.parquet  : reportes anti-cheat (severidad, region)
  - regiones.csv     : dimensión: las regiones del mundo del juego, agrupadas
                       en 5 macrorregiones (columna `region`, 1..5)

Determinista (seed fijo) -> KPIs del Data Mart reproducibles.
"""
import argparse, os, shutil
import numpy as np, pandas as pd

SEED = 42
N_EVENTOS = 200_000
N_ALERTAS = 12_000
N_REGIONES = 40
TIPOS = ["combate", "exploracion", "social"]
SEV = ["baja", "media", "alta", "critica"]

# Las mismas 40 zonas del mundo de juego que usa el NF2: es el mismo estudio y el
# mismo mapa a lo largo del módulo. Lista fija: NO consume aleatoriedad, así que
# `region` recibe exactamente el mismo tramo de np.random y el contrato no se mueve.
NOMBRES_REGION = [
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


def generar(caso, salida):
    np.random.seed(SEED)
    if os.path.exists(salida):
        shutil.rmtree(salida)
    os.makedirs(salida, exist_ok=True)

    # Dimensión: zonas del mapa agrupadas en 5 macrorregiones (region 1..5)
    regiones = pd.DataFrame({
        "id_zona": np.arange(1, N_REGIONES + 1),
        "nombre_zona": NOMBRES_REGION[:N_REGIONES],
        "region": np.random.randint(1, 6, N_REGIONES),
    })
    regiones.to_csv(f"{salida}/regiones.csv", index=False)

    # Hechos: eventos operacionales
    eventos = pd.DataFrame({
        "id_evento": np.arange(N_EVENTOS),
        "id_zona": np.random.randint(1, N_REGIONES + 1, N_EVENTOS),
        "timestamp": pd.date_range("2025-05-01", periods=N_EVENTOS, freq="s").astype(str),
        "tipo": np.random.choice(TIPOS, N_EVENTOS, p=[0.45, 0.35, 0.20]),
        "valor": np.round(np.random.gamma(3.0, 20.0, N_EVENTOS), 2),
    })
    eventos.to_parquet(f"{salida}/eventos.parquet", index=False)

    # Hechos: alertas (reportes anti-cheat) — las críticas se concentran en una región
    id_zona_al = np.random.randint(1, N_REGIONES + 1, N_ALERTAS)
    # sesgo: las zonas de la región 3 generan más críticas (es el hallazgo a descubrir)
    region_de_zona = dict(zip(regiones.id_zona, regiones.region))
    p_critica = np.array([0.25 if region_de_zona[z] == 3 else 0.08 for z in id_zona_al])
    es_critica = np.random.random(N_ALERTAS) < p_critica
    severidad = np.where(es_critica, "critica",
                         np.random.choice(["baja", "media", "alta"], N_ALERTAS))
    alertas = pd.DataFrame({
        "id_alerta": np.arange(N_ALERTAS),
        "id_zona": id_zona_al,
        "timestamp": pd.date_range("2025-05-01", periods=N_ALERTAS, freq="min").astype(str),
        "severidad": severidad,
    })
    alertas.to_parquet(f"{salida}/alertas.parquet", index=False)

    print(f"[OK] Caso '{caso}': eventos={N_EVENTOS}, alertas={N_ALERTAS}, zonas={N_REGIONES}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--caso", default="gaming", choices=["gaming"])
    ap.add_argument("--salida", required=True,
                    help="ruta de salida; desde nf5/ usa: --salida datos/raw")
    a = ap.parse_args()
    generar(a.caso, a.salida)
