# Demo de la VC3 · NF3 — caso Smart City

> **Esto no se entrega y no se corrige.** Es el material de la videoconferencia del NF3.
> Tu actividad evaluable audita **reportes anti-cheat de un juego** (`nf3/`). Aquí puedes
> ejecutar, romper y experimentar sin consecuencias.

## Qué hay aquí

La videoconferencia parte de **un** hecho —*"una alerta de calidad del aire nos costó dinero;
¿era de verdad?"*— y audita la fiabilidad en tres frentes, que son las tres ideas del núcleo:

| Frente | La pregunta | Herramienta | Ítem de teoría en el Campus |
|---|---|---|---|
| 1 | ¿Llegaron los datos enteros? | `_SUCCESS` + checksums SHA-256 | 3.4 · Volumen e integridad |
| 2 | ¿El umbral era honesto? | media ± 3σ → limpiar primero → mediana + MAD | 3.2 · El engaño de la media |
| 3 | ¿La tabla cumple su promesa? | tests de dbt sobre DuckDB | 3.6 · Calidad como código: dbt |

## Cómo ejecutarlo

Desde la **raíz del repositorio**:

```bash
python demo/nf3_smartcity/preparar_demo.py     # genera raw/ y los seeds de dbt (~2 s)
# abre demo/nf3_smartcity/VC3_demo_smartcity.ipynb y ejecútalo de arriba a abajo
```

El cuaderno ejecuta `dbt seed`, `dbt run` y `dbt test` por ti desde una celda. **dbt y DuckDB
ya vienen en el devcontainer del curso** (los usa la actividad del NF3): no hay que instalar
nada ni levantar ningún servidor. DuckDB es un fichero local.

Si quieres correr dbt a mano, desde `demo/nf3_smartcity/dbt_calidad/`:

```bash
DBT_PROFILES_DIR=. dbt seed && DBT_PROFILES_DIR=. dbt run && DBT_PROFILES_DIR=. dbt test
```

## Qué deberías ver

Todos los números son **deterministas**: salen iguales en cualquier máquina.

| Frente | Resultado |
|---|---|
| 1 | `part-2.csv` **pesa lo mismo** que cuando se firmó (911 bytes) y **su checksum no cuadra** |
| 2 | media ± 3σ detecta **0 de 40** atascos; mediana + MAD, **40 de 40**. En el barrido, la media pasa de 15/15 a **0/25** |
| 3 | `dbt test`: **1 PASS, 5 FAIL** (1 · 176 · 60 · 12 · 30) y `ERROR=5` |

## El proyecto dbt

`dbt_calidad/` es un proyecto dbt **mínimo y real**:
- `models/schema.yml`: los **cuatro tests genéricos** de serie (`unique`, `not_null`,
  `accepted_values` y `relationships`).
- `tests/aqi_en_rango.sql`: un test **singular** (SQL a medida) para el rango del índice de
  calidad del aire.
- `seeds/`: lo genera `preparar_demo.py`. `alertas_raw.csv` (la tabla con fallos inyectados) y
  `distritos.csv` (el catálogo oficial al que apunta `relationships`).
- `profiles.yml`: apunta a DuckDB, un fichero local (`calidad.duckdb`), sin servidor.

## Para experimentar

- Cambia el número de atascos en `preparar_demo.py` y mira cuándo se cae la media.
- Cambia un carácter de un `part-*.csv` a mano y vuelve a ejecutar el frente 1.
- Añade `Puerto` a `distritos.csv` y mira qué pasa con el test `relationships`.
- Pon `severity: warn` en uno de los tests y mira cómo cambia la última línea de `dbt test`.

---

### Reglas de esta carpeta *(nota para el equipo docente)*

1. **La demo no toca el `devcontainer`.** Usa dbt y DuckDB, que ya están.
2. **La demo no escribe fuera de `demo/`.** `raw/`, los seeds generados y los artefactos de dbt
   (`target/`, `calidad.duckdb`, `logs/`) no se versionan. Lo que se versiona es el
   **esqueleto** del proyecto dbt (yml, sql), no sus datos ni su salida.
3. **La demo no revela la solución de la actividad.** Las columnas son de Smart City (`aqi`,
   `distrito`). La estructura del `schema.yml` coincide con la de la Parte C porque el
   enunciado de la actividad la dicta; la columna y los recuentos del alumno son otros.
