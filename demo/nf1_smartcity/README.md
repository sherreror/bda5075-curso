# Demo de la VC1 · NF1 — caso Smart City

> **Esto no se entrega y no se corrige.** Es el material de la videoconferencia del NF1.
> Tu actividad evaluable es la del caso **gaming** (`nf1/`). Aquí puedes ejecutar, romper y
> experimentar sin consecuencias: es para eso.

## Qué hay aquí

La videoconferencia responde a **una** pregunta —*"¿tenemos un problema de NO₂ en el
Ensanche?"*— y se estrella contra cuatro obstáculos por el camino. Cada obstáculo es un
concepto del núcleo:

| Acto | El obstáculo | Teoría |
|---|---|---|
| 1 | El dato crudo miente | §1.6 |
| 2 | A escala, el formato es dinero | §1.4 |
| 3 | Alguien machaca la tabla buena | §1.5 |
| 4 | La app quiere un dato, no un millón | §1.7 |
| 5 | Un número no es una decisión | §1.8 |

## Cómo ejecutarlo

Desde la **raíz del repositorio** (no desde esta carpeta):

```bash
# 1. Generar los datos (una sola vez, ~10 s)
python demo/nf1_smartcity/preparar_demo.py

# 2. Abrir el cuaderno y ejecutarlo de arriba a abajo
#    demo/nf1_smartcity/VC1_demo_smartcity.ipynb
```

El **ACTO 4** (MongoDB) es opcional y necesita dos cosas más:

```bash
pip install -r demo/nf1_smartcity/requirements-demo.txt
docker run -d --name mongo-demo -p 27017:27017 mongo:7
# al terminar:
docker stop mongo-demo && docker rm mongo-demo
```

Si no lo ejecutas, el resto del cuaderno funciona igual: solo fallarán esas tres celdas.

## Ficheros

| | |
|---|---|
| `preparar_demo.py` | Genera los datos. `raw/` (sucio, 5.000 filas), `bench/` (1 M de filas ya escritas en CSV y Parquet), `proc/` (vacío, lo llena el ACTO 3). |
| `VC1_demo_smartcity.ipynb` | El cuaderno de la sesión. |
| `requirements-demo.txt` | Solo `pymongo`, solo para el ACTO 4. |

`raw/`, `bench/` y `proc/` están en el `.gitignore`: no se versionan (el CSV pesa ~50 MB) y se
regeneran en segundos.
