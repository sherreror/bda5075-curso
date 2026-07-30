# Demo de la VC4 · NF4 — caso Smart City

> **Esto no se entrega y no se corrige.** Es el material de la videoconferencia del NF4.
> Tu actividad evaluable instrumenta **el servidor de un juego** (`nf4/`). Aquí monitorizamos una
> red de sensores. Puedes ejecutar, romper y experimentar sin consecuencias.

## Qué hay aquí

La videoconferencia parte de una paradoja —*"el pipeline salió en verde y los datos son
basura"*— y construye la maquinaria para no volver a fiarse del verde:

| Acto | La idea | Teoría |
|---|---|---|
| 0 | NF3 (tests) vs NF4 (monitores): "¿llegó **todo**?" | §4.0, §4.6 |
| 1 | Instrumentar: Counter, Gauge, Histogram | §4.2 |
| 2 | La media miente: el SLO es p95, no media | §4.2 |
| 3 | El SLO como código: `expr`, `for`, `severity` | §4.4, §4.5 |
| 4 | **La alerta del silencio**: `up`, `absent()` | §4.5 |
| 5 | Observabilidad como código (sin capturas) | §4.6 |

## Cómo ejecutarlo

Desde la **raíz del repositorio**:

```bash
python demo/nf4_smartcity/preparar_demo.py     # genera raw/ (~1 s)
# abre demo/nf4_smartcity/VC4_demo_smartcity.ipynb y ejecútalo de arriba a abajo
```

**No hace falta Docker, Prometheus ni Grafana.** Todo el stack que importa corre en Python:
`prometheus_client` (que ya viene en el devcontainer del curso) instrumenta y expone `/metrics`;
el SLO se evalúa en Python; las alertas se validan con PyYAML. En un CI real, ese último paso
sería `promtool check rules alertas.yml` — se menciona en la demo, no se ejecuta.

### Ver `/metrics` en vivo (opcional, para el directo)

```bash
python demo/nf4_smartcity/pipeline_demo.py --modo normal --puerto 8000
# en Codespaces, abre el puerto 8000 en la pestaña "Ports"
```

Es el equivalente a la Spark UI del NF2: ver el endpoint que Prometheus scrapearía.

## Ficheros

| | |
|---|---|
| `preparar_demo.py` | Genera `raw/lote_hoy.csv` (el lote "verde y roto": 47 de 50 sensores). |
| `pipeline_demo.py` | El pipeline instrumentado. Usable como servicio (`/metrics`) o librería. |
| `VC4_demo_smartcity.ipynb` | El cuaderno de la sesión. |
| `observabilidad/alertas.yml` | Las 4 reglas como código, incluida la del silencio. |
| `observabilidad/torre_control.json` | El dashboard como código (4 paneles). |

## Por qué esta demo no levanta Grafana

**A propósito.** Lo que se enseña y se evalúa en el NF4 es **observabilidad como código**:
`alertas.yml` y `torre_control.json` son ficheros de texto, versionables y revisables, y eso es
lo que importa. Clicar en una interfaz no se evalúa en ninguna parte.

En la demo verás las métricas reales que expone el pipeline y cómo se leen; Grafana solo las
**dibuja**. Si el dashboard no se te llega a ver, no has perdido nada evaluable.

> **Estos dos ficheros te van a servir en tu actividad.** `observabilidad/alertas.yml` tiene
> **4 reglas resueltas** y `observabilidad/torre_control.json` **4 paneles resueltos**, sobre el
> caso Smart City. Tu actividad del NF4 te pide lo mismo con las métricas del servidor de juego:
> **son el ejemplo del que copiar la estructura**, no la solución de tu entrega.
