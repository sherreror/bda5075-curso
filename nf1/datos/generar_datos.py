"""
Generador NF1 — caso GAMING: "la memoria de las partidas" de un juego online.

Tres fuentes con tres problemas de calidad distintos. Determinista (seed fijo):
a todo el alumnado le salen exactamente los mismos datos.

  sesiones.csv        id_jugador, ping_ms [métrica: nulos + outliers],
                      fps [numérico guardado como texto, con centinela "sin_dato"],
                      latitud/longitud [geolocalización aproximada del jugador,
                      la que usa el emparejador para asignar servidor regional]
  partidas.json       JSON anidado -> datos.mapa [categoría sin estandarizar],
                      datos.jugadores, ubicacion.lat/lon [zona del servidor]
  matchmaking.parquet mmr [numérico guardado como texto]
"""
import argparse, json, os, random
import numpy as np, pandas as pd

SEED = 42
N_SESIONES = 8000
N_PARTIDAS = 3000
N_MATCH = 5000
N_NULOS_PING = 400        # nulos en la métrica (ping_ms)
N_NULOS_FPS = 250         # nulos de texto en fps ('sin_dato')
N_OUTLIERS = 120          # outliers de ping (rango)

MAPAS_SUCIOS = ["Forest", "FOREST", "forest", "Bosque", "BOSQUE",
                "Desert", "DESERT", "Desierto", "Snow", "nieve"]
MAPA_CANONICO = {"forest": "bosque", "bosque": "bosque",
                 "desert": "desierto", "desierto": "desierto",
                 "snow": "nieve", "nieve": "nieve"}


def generar(salida):
    random.seed(SEED); np.random.seed(SEED)
    os.makedirs(salida, exist_ok=True)
    ts = pd.date_range("2025-01-01", periods=N_SESIONES, freq="h")

    # Fuente 1: sesiones.csv (tabular sucio)
    df = pd.DataFrame({
        "id_jugador": np.random.randint(1, 51, N_SESIONES),
        "timestamp": ts.astype(str),
        "ping_ms": np.round(np.random.uniform(10, 180, N_SESIONES), 2),
        "fps": np.round(np.random.uniform(24, 144, N_SESIONES), 1).astype(str),  # texto a propósito
        "latitud": np.round(np.random.uniform(40.38, 40.48, N_SESIONES), 5),
        "longitud": np.round(np.random.uniform(-3.75, -3.65, N_SESIONES), 5),
    })
    idx_nulos = np.random.choice(N_SESIONES, N_NULOS_PING, replace=False)
    df.loc[idx_nulos, "ping_ms"] = np.nan
    idx_out = np.random.choice(np.setdiff1d(np.arange(N_SESIONES), idx_nulos),
                               N_OUTLIERS, replace=False)
    df.loc[idx_out, "ping_ms"] = np.random.choice([-50, 999, 1500], N_OUTLIERS)
    idx_fps = np.random.choice(N_SESIONES, N_NULOS_FPS, replace=False)
    df.loc[idx_fps, "fps"] = "sin_dato"
    df.to_csv(f"{salida}/sesiones.csv", index=False)

    # Fuente 2: partidas.json (anidado, categorías sucias)
    registros = []
    for i in range(N_PARTIDAS):
        registros.append({
            "id_partida": i,
            "timestamp": str(ts[i % N_SESIONES]),
            "ubicacion": {"lat": float(np.round(np.random.uniform(40.38, 40.48), 5)),
                          "lon": float(np.round(np.random.uniform(-3.75, -3.65), 5))},
            "datos": {"mapa": random.choice(MAPAS_SUCIOS),
                      "jugadores": int(np.random.randint(2, 11))},
        })
    json.dump(registros, open(f"{salida}/partidas.json", "w", encoding="utf-8"),
              ensure_ascii=False)

    # Fuente 3: matchmaking.parquet (mmr como texto)
    df_extra = pd.DataFrame({
        "id_jugador": np.random.randint(1, 51, N_MATCH),
        "timestamp": pd.date_range("2025-01-01", periods=N_MATCH, freq="min").astype(str),
        "mmr": np.round(np.random.uniform(800, 2400, N_MATCH), 0).astype(str),
    })
    df_extra.to_parquet(f"{salida}/matchmaking.parquet", index=False)

    print(f"[OK] Caso gaming: sesiones.csv={N_SESIONES}, partidas.json={N_PARTIDAS}, "
          f"matchmaking.parquet={N_MATCH}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--salida", required=True,
                    help="ruta de salida; desde nf1/ usa: --salida datos/raw")
    generar(ap.parse_args().salida)
