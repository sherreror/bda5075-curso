# Demo de la VC2 · NF2 — caso Smart City

> **Esto no se entrega y no se corrige.** Es el material de la videoconferencia del NF2.
> Tu actividad evaluable es la del caso **gaming** (`nf2/`). Aquí puedes ejecutar, romper y
> experimentar sin consecuencias.

## Qué hay aquí

La videoconferencia arranca de **un** encargo —*"el panel de tráfico tarda 40 minutos, vamos a
arreglarlo"*— y de ahí salen las seis propiedades del cómputo distribuido:

| Acto | La idea | Teoría |
|---|---|---|
| 2 | Pereza: transformación vs acción | §2.1 |
| 3 | Linaje: tolerancia a fallos sin copiar | §2.2 |
| 4 | Shuffle: la unidad de coste | §2.3 |
| 5 | Función de ventana: 1 shuffle en vez de 2 | §2.3 |
| 6 | Batch y streaming, el mismo código | §2.5 |
| 7 | ¿De verdad necesitas Spark? DuckDB | §2.6 |

## Cómo ejecutarlo

Desde la **raíz del repositorio**:

```bash
python demo/nf2_smartcity/preparar_demo.py     # genera raw/ (~5 s)
# abre demo/nf2_smartcity/VC2_demo_smartcity.ipynb y ejecútalo de arriba a abajo
```

**Todo funciona con lo que ya trae el devcontainer del curso** (PySpark y DuckDB los usan la
actividad del NF2 y la del NF3). No hay que instalar nada.

**La Spark UI** (puerto 4040) se abre sola al arrancar la sesión; en Codespaces aparece en la
pestaña *Ports*. Es parte de la demo: ahí se ven los *stages* y los *shuffles*.

## La anomalía escondida (para que sepas qué estás mirando)

Los datos llevan una señal real: la **vía 7**, en la **hora punta de la mañana**, se satura al
doble de lo normal. El truco pedagógico es que **la media diaria por vía la esconde** (sale
~64 frente a ~60, casi nada) y **solo una función de ventana por `(vía, hora)` la saca a la
luz** (144 a las 8 h). Es el argumento del ACTO 5 hecho carne.
