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

El **ACTO 4** (MongoDB) es opcional. `pymongo` ya viene en el entorno del curso; lo único que
hace falta es levantar el servidor con Docker:

```bash
docker run -d --name mongo-demo -p 27017:27017 mongo:7
# al terminar:
docker stop mongo-demo && docker rm mongo-demo
```

Si no lo levantas, el resto del cuaderno funciona igual: solo fallarán esas tres celdas.

## Ficheros

| | |
|---|---|
| `preparar_demo.py` | Genera los datos. `raw/` (sucio, 5.000 filas), `bench/` (1 M de filas ya escritas en CSV y Parquet), `proc/` (vacío, lo llena el ACTO 3). |
| `VC1_demo_smartcity.ipynb` | El cuaderno de la sesión. |
| `requirements-demo.txt` | `pymongo`, para el ACTO 4. Ya está en el entorno del curso; el fichero se conserva por si se ejecuta la demo fuera de él. |

`raw/`, `bench/` y `proc/` están en el `.gitignore`: no se versionan (el CSV pesa ~50 MB) y se
regeneran en segundos.

---

### Reglas de esta carpeta *(nota para el equipo docente)*

1. **La demo no toca el `devcontainer`.** Nunca. Si necesitara una dependencia que el entorno
   no trae, iría en `requirements-demo.txt`. El entorno que ejecuta y corrige las actividades
   evaluables se queda intacto: sin rebuild, sin riesgo, sin Codespaces divergentes. *(Hoy no
   hace falta nada extra: el entorno del curso ya fija `pymongo==4.10.1` para el NF1.)*
2. **La demo no escribe fuera de `demo/`.** Sus datos viven aquí y están *gitignored*.
3. **La demo no revela la solución de la actividad.** Caso distinto, columnas distintas,
   umbrales distintos. Y las fases evaluables de limpieza **no se resuelven en pantalla**:
   solo se enseña el diagnóstico y el error típico.
