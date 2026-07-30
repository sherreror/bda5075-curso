# Demo de la VC5 · NF5 — caso Smart City

> **Esto no se entrega y no se corrige.** Es el material de la videoconferencia del NF5.
> Tu actividad evaluable es el informe estratégico de **un juego online** (`nf5/`). Aquí lo
> hacemos de una ciudad. Puedes ejecutar, romper y experimentar sin consecuencias.

## Qué hay aquí

La videoconferencia parte de una pregunta del alcalde —*"¿dónde pongo el presupuesto?"*— y
recorre el camino del dato a la decisión, tropezando con una lección en cada paso:

| Acto | La idea | Teoría |
|---|---|---|
| 1 | El data lake crudo mata el dashboard (y el análisis) | §5.3 |
| 2 | El Data Mart: hecho + dimensión + grano. 2M → 5 filas | §5.3 |
| 3 | El mismo dato, dos gráficos: el eje truncado miente | §5.5 |
| 4 | Observación → insight → decisión (la comparación) | §5.6 |
| 5 | La herramienta es lo fácil; el pensamiento es lo tuyo | §5.7 |

## Cómo ejecutarlo

Desde la **raíz del repositorio**:

```bash
python demo/nf5_smartcity/preparar_demo.py     # genera raw/ (~3 s)
# abre demo/nf5_smartcity/VC5_demo_smartcity.ipynb y ejecútalo de arriba a abajo
```

**No hace falta Power BI ni Tableau.** Todo corre en Python (pandas, DuckDB, matplotlib), ya en
el devcontainer del curso. La demo **construye el data mart** (`data_mart/fact_zona.csv`) —el
fichero que cargarías en la herramienta de BI— y **muestra el razonamiento en código**. Montar el
dashboard en la herramienta es la parte fácil (10 min) y se hace fuera de esta demo.

## Neutral entre herramientas, a propósito

La demo **no se decanta** por Power BI ni por Tableau: el `fact_zona.csv` de 5 filas sirve para
ambas. El ACTO 5 resume la elección (Power BI solo Windows; Tableau Public gratis y multiplataforma
pero **publica el trabajo en internet**) sin imponer. En su actividad el alumno elige una.

## La señal escondida (para que sepas qué estás mirando)

Los datos llevan un patrón **contraintuitivo y distinto del caso gaming**: el **Litoral** tiene
poca actividad (8 %) pero una tasa de alerta altísima (2,76 %, frente al 0,61 % del Centro, que
tiene 4× más tráfico). En bruto, Litoral y Centro parecen problemas parecidos; **solo la
comparación por tasa revela** que el Litoral es estructural. Es el ACTO 4 hecho dato: la
observación (número bruto) no basta; el insight nace de elegir contra qué comparar.
