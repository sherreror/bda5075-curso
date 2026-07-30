# Big Data Aplicado (5075) — Repositorio del curso

Entorno único reproducible en **GitHub Codespaces**. No instalas nada: Java, Spark,
dbt, DuckDB, Delta Lake y Prometheus/Grafana ya vienen configurados.

## 📅 Calendario
Cada núcleo formativo (NF) **se habilita en el Campus Virtual en su fecha**. Trabaja
siempre el NF que esté **abierto**: allí tienes la misión, la teoría, el cuestionario y
la **tarea de entrega** con su fecha límite. Este repositorio es solo tu **entorno**.

## Cómo empezar

> ⚠️ **No abras un Codespace sobre este repositorio.** Aquí no puedes escribir: no podrías
> guardar tu trabajo. Primero crea **tu propia copia privada** (paso 1).

**1. Crea tu copia privada del repositorio — una sola vez en todo el módulo.**

Inicia sesión en GitHub y, en esta misma página, pulsa el botón verde **`Use this template`**
→ **`Create a new repository`**. Rellena así:

| Campo | Qué pones |
|---|---|
| **Owner** | Tu propia cuenta (ya sale seleccionada). |
| **Repository name** | `bda5075-apellido` — p. ej. `bda5075-garcia`. Sin espacios ni acentos. |
| **Visibility** | **`Private`** ← obligatorio. |
| **Include all branches** | Desmarcado. |

**No hagas `Fork`:** el fork de un repositorio público es siempre público y no se puede
privatizar. Tu actividad es evaluable: tiene que quedar en privado.

**2. Abre el Codespace sobre TU copia.**

Desde tu repositorio (comprueba que arriba pone `tu-usuario/bda5075-...`):
*Code → Codespaces → Create codespace on main*. La primera vez tarda unos minutos; verás
**"Entorno OK · PySpark ..."** cuando esté listo.

**3. Sitúate en la carpeta del núcleo** abierto y trabaja siempre desde ahí:

```bash
cd nf1                                   # (nf1 … nf5, según el núcleo abierto)
python datos/generar_datos.py --salida datos/raw
# abre actividad/NF1_actividad.ipynb y complétalo, ejecutando todas las celdas de arriba abajo
```

La **última celda** genera tu `resultados.json`.

> **Si al abrir el `.ipynb` te pide elegir kernel:** arriba a la derecha pulsa
> **`Seleccionar el kernel`** → **`Entornos de Python…`** → el que dice **`Python 3.12.x`**
> (ruta `/usr/local/bin/python`). Ese es el del curso, el que trae Spark, dbt y Delta.
> No elijas `/usr/bin/python3` ni ningún entorno "base": no tienen las librerías instaladas
> y te dará `ModuleNotFoundError`. Normalmente lo selecciona solo.

**4. Al terminar cada sesión, haz commit y push.**

Panel **Source Control** (`Ctrl+Shift+G`) → escribe un mensaje → **Commit** → **Sync Changes**.
Equivale a `git add -A && git commit -m "..." && git push`. No tienes que configurar
credenciales: el Codespace ya viene conectado a tu repositorio.

Tu repositorio guarda tu **código** (el notebook, `schema.yml`, `alertas.yml`). **No** guarda
`datos/raw/`, `resultados.json`, `datamart/`, `almacen/` ni `entrega/`: están en el
`.gitignore` a propósito porque se regeneran ejecutando tu notebook. Por eso el push **no
sustituye** a descargarte los archivos que entregas.

> NF4 usa Docker y NF2/NF5 usan Spark. Cada actividad indica sus pasos concretos al inicio.

---

## 📤 ENTREGA — léelo con atención (afecta a tu nota)

**Dónde.** Solo en la **tarea del Campus Virtual** del NF correspondiente. No se aceptan
entregas por correo ni por GitHub.

**Qué entregar (NF1).** DOS archivos:
1. El notebook **completado**: `NF1_actividad.ipynb`
2. El **`resultados.json`** que genera la última celda

*(Otros núcleos piden archivos adicionales; se indica en cada tarea.)*

**Nombre de los archivos — OBLIGATORIO.** Renómbralos con tus **Apellidos_Nombre_NF**:
- `Apellidos_Nombre_NF1.ipynb`  ·  `Apellidos_Nombre_NF1.json`

Reglas: solo **letras y guiones bajos**; **sin espacios, sin acentos y sin ñ**
(`Nunez`, no `Núñez`). Ejemplo: `Garcia_Lopez_Ana_NF1.ipynb`.

**Tu nombre dentro del notebook.** En la última celda, escribe tus *Apellidos, Nombre*
en la variable `ALUMNO`. **El notebook no generará el `resultados.json` si no lo haces.**

**No lo toques.** No modifiques la última celda ni las claves del `resultados.json`:
entrégalo **tal cual** lo genera el notebook.

### ⚠️ Penalizaciones (se aplican de forma estricta)
- **Fuera de plazo:** según la normativa del módulo.
- **Nombre de archivo o formato incorrecto:** −10 % de la nota de la actividad.
- **Falta el notebook** (solo el JSON): **0 en la parte automática**.
- **`resultados.json` alterado a mano:** tu notebook **se re-ejecuta**; si tu código no lo
  genera, **0 en la parte automática**.

> Pegar un `resultados.json` que tu código no produce **no sirve**: se detecta al re-ejecutar.

---

## 💶 Coste
Con el límite de gasto en 0 € y sin método de pago, Codespaces **se detiene** al agotar la
cuota gratuita; nunca te cobra. Tu cuenta gratuita cubre también repositorios privados.
**Para y borra tu Codespace al terminar** (pestaña *Codespaces*) — borrarlo solo es seguro si
antes has hecho **push** y has descargado lo que entregas. No lo abras hasta que vayas a
trabajar el NF.

## Recordatorio
Sigue las **reglas exactas** de cada fase. Si un autochequeo te avisa (p. ej. "quedan
nulos"), corrígelo **antes** de entregar.

---
### ⚙️ Caso activo este semestre: **GAMING** (plataforma de juego online)
