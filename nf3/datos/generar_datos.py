"""
Generador NF3 (RA3) — caso GAMING: "auditando los reportes anti-cheat".

Genera de forma determinista:
  - alertas.parquet : reportes anti-cheat con PROBLEMAS DE CALIDAD plantados (para dbt)
  - lecturas.csv    : serie de medidas de un jugador con outliers (baseline anti-enmascaramiento)

Conteos plantados (deterministas) — los detectarán los tests del alumno:
  nulos en severidad        = 60
  severidad inválida        = 40 filas, con solo 2 VALORES distintos ("ALTA", "x").
                                 OJO: accepted_values es un test AGRUPADO y reporta 2, no 40.
  puntuacion_sospecha fuera de rango = 50   (<0 o >500)
  id_alerta duplicado       = 30   (valores que aparecen 2 veces)
"""
import argparse, os, shutil
import numpy as np, pandas as pd

SEED = 42
N = 5000
N_NULL_SEV, N_BAD_SEV, N_RANGE, N_DUP = 60, 40, 50, 30
SEV_OK = ["baja", "media", "alta", "critica"]
SEV_BAD = ["ALTA", "x"]


def generar(caso, salida):
    np.random.seed(SEED)
    if os.path.exists(salida):
        shutil.rmtree(salida)
    os.makedirs(salida, exist_ok=True)

    df = pd.DataFrame({
        "id_alerta": np.arange(1, N + 1),
        "id_jugador": np.random.randint(1, 201, N),
        "timestamp": pd.date_range("2025-04-01", periods=N, freq="min").astype(str),
        "severidad": np.random.choice(SEV_OK, N),
        "puntuacion_sospecha": np.round(np.random.uniform(10, 180, N), 2),
        "confianza": np.round(np.random.uniform(0.5, 1.0, N), 3),
    })
    # Plantar problemas en posiciones deterministas y DISJUNTAS
    pool = np.random.permutation(N)
    a = 0
    i_null = pool[a:a+N_NULL_SEV]; a += N_NULL_SEV
    i_bad = pool[a:a+N_BAD_SEV]; a += N_BAD_SEV
    i_rng = pool[a:a+N_RANGE]; a += N_RANGE
    i_orig = pool[a:a+N_DUP]; a += N_DUP          # ids "originales" (intactos)
    i_dup = pool[a:a+N_DUP]; a += N_DUP           # reciben los ids originales -> 30 valores duplicados
    df.loc[i_null, "severidad"] = None
    df.loc[i_bad, "severidad"] = np.random.choice(SEV_BAD, N_BAD_SEV)
    df.loc[i_rng, "puntuacion_sospecha"] = np.random.choice([-7.0, 999.0, 1500.0], N_RANGE)
    df.loc[i_dup, "id_alerta"] = df.loc[i_orig, "id_alerta"].values
    df.to_parquet(f"{salida}/alertas.parquet", index=False)

    # -------- Escenario baseline anti-enmascaramiento --------
    # 990 lecturas normales ~ N(50,4); 5 picos extremos (600) que inflan media/std
    # y enmascaran; 5 anomalías moderadas (88) que solo el método robusto detecta.
    base = np.round(np.random.normal(50, 4, 990), 2)
    lecturas = np.concatenate([base, np.full(5, 600.0), np.full(5, 88.0)])
    pd.DataFrame({"id_jugador": 7, "lectura": lecturas}).to_csv(f"{salida}/lecturas.csv", index=False)

    print(f"[OK] Caso '{caso}': alertas.parquet={N} (nulos={N_NULL_SEV}, sev_invalida={N_BAD_SEV}, "
          f"rango={N_RANGE}, dup={N_DUP}); lecturas.csv={len(lecturas)}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--caso", default="gaming", choices=["gaming"])
    ap.add_argument("--salida", required=True,
                    help="ruta de salida; desde nf3/ usa: --salida datos/raw")
    a = ap.parse_args()
    generar(a.caso, a.salida)
