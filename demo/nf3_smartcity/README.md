# Demo de la VC3 · NF3 — caso Smart City

> **Esto no se entrega y no se corrige.** Es el material de la videoconferencia del NF3.
> Tu actividad evaluable audita **reportes anti-cheat de un juego** (`nf3/`). Aquí puedes
> ejecutar, romper y experimentar sin consecuencias.

## Qué hay aquí

La videoconferencia parte de **un** hecho —*"una alerta de calidad del aire nos costó dinero;
¿era de verdad?"*— y audita la fiabilidad en tres frentes, que son las tres ideas del núcleo:

| Frente | La pregunta | Herramienta | Teoría |
|---|---|---|---|
| 1 | ¿Llegaron los datos enteros? | `_SUCCESS` + checksums SHA-256 | §3.4 |
| 2 | ¿El umbral era honesto? | mediana + MAD (robustos) | §3.2 |
| 3 | ¿La tabla cumple su promesa? | tests de dbt sobre DuckDB | §3.6 |

## Cómo ejecutarlo

Desde la **raíz del repositorio**:

```bash
python demo/nf3_smartcity/preparar_demo.py     # genera raw/ y el seed de dbt (~2 s)
# abre demo/nf3_smartcity/VC3_demo_smartcity.ipynb y ejecútalo de arriba a abajo
```

El notebook ejecuta `dbt seed`, `dbt run` y `dbt test` por ti desde una celda. **dbt y DuckDB
ya vienen en el devcontainer del curso** (los usa la actividad del NF3): no hay que instalar
nada, no hay servidor que levantar. DuckDB es un fichero local.

Si quieres correr dbt a mano, desde `demo/nf3_smartcity/dbt_calidad/`:

```bash
DBT_PROFILES_DIR=. dbt seed && DBT_PROFILES_DIR=. dbt run && DBT_PROFILES_DIR=. dbt test
```

## El proyecto dbt

`dbt_calidad/` es un proyecto dbt **mínimo y real**:
- `models/schema.yml` — los tests **genéricos** (unique, not_null, accepted_values).
- `tests/aqi_en_rango.sql` — un test **singular** (SQL a medida) para el rango del índice de
  calidad del aire.
- `profiles.yml` — apunta a DuckDB, un fichero local (`calidad.duckdb`), sin servidor.

`dbt test` devuelve el patrón que el alumno verá en su actividad: **1 PASS, 4 FAIL** con el
recuento de filas malas por test.
