"""
Prepara el escenario de INTEGRIDAD (RA3.3/3.4) — se ejecuta una vez en el setup.

Replica el contrato de un sistema de ficheros distribuido (Hadoop/Spark):
  - Escribe la salida en varios "part files".
  - El "servidor"/coordinador calcula una SUMA DE VERIFICACIÓN (sha256) por fichero
    ANTES de dar el resultado por válido (RA3.4) y la guarda en manifiesto.json.
  - Escribe el marcador _SUCCESS solo cuando el job termina bien (RA3.4).
Y simula dos fallos que el alumno deberá detectar:
  - Un directorio SIN _SUCCESS (job incompleto).
  - Un fichero CORRUPTO (su checksum ya no coincide con el manifiesto) (RA3.3).
"""
import hashlib, json, os, shutil
import numpy as np, pandas as pd
import pyarrow as pa, pyarrow.parquet as pq

DIST = "almacen/alertas_dist"
INCOMP = "almacen/alertas_incompletas"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    df = pd.read_parquet("datos/raw/alertas.parquet")
    if os.path.exists("almacen"):
        shutil.rmtree("almacen")
    os.makedirs(DIST, exist_ok=True)

    # 1) Escribir 4 "part files" (como haría un job distribuido)
    bordes = np.linspace(0, len(df), 5, dtype=int)
    for i in range(4):
        trozo = df.iloc[bordes[i]:bordes[i+1]]
        pq.write_table(pa.Table.from_pandas(trozo, preserve_index=False),
                       f"{DIST}/part-{i:05d}.parquet")

    # 2) El coordinador calcula la suma de verificación de cada fichero (RA3.4)
    manifiesto = {f: sha256(f"{DIST}/{f}") for f in sorted(os.listdir(DIST))
                  if f.endswith(".parquet")}
    json.dump(manifiesto, open(f"{DIST}/manifiesto.json", "w"), indent=2)

    # 3) Marcador _SUCCESS: el job terminó correctamente (RA3.4)
    open(f"{DIST}/_SUCCESS", "w").close()

    # 4) Sabotaje A: directorio gemelo SIN _SUCCESS (job incompleto)
    shutil.copytree(DIST, INCOMP)
    os.remove(f"{INCOMP}/_SUCCESS")

    # 5) Sabotaje B: corromper exactamente 1 fichero de part en DIST
    objetivo = f"{DIST}/part-00002.parquet"
    with open(objetivo, "r+b") as f:
        f.seek(100); f.write(b"\x00\x00\x00\x00")   # altera bytes -> checksum cambia

    print(f"[OK] Escenario listo: {len(manifiesto)} ficheros, _SUCCESS en {DIST}, "
          f"1 corrupto, directorio incompleto en {INCOMP}")


if __name__ == "__main__":
    main()
