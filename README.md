# PI3 — Proyecto integrador: abandono de clientes (churn)

Proyecto integrador de Analítica de Datos.
**Proyecto:** caracterización del abandono de clientes en una compañía de telecomunicaciones ficticia
según tipo de contrato, antigüedad y facturación.

| Etapa | Carpeta | Contenido |
|---|---|---|
| AE2 · Ideación, diseño y documentación de la necesidad | [`AE2/`](AE2/) | Necesidad, diseño, carga y descripción básica del dataset |
| AE3 · Transformación y enriquecimiento de datos | [`AE3/`](AE3/) | Limpieza, variables derivadas, respuestas a las preguntas y tablas exportadas |
| AE4 · Métricas y visualización de datos | [`AE4/`](AE4/) | Aplicación de Streamlit, gráficos, métricas e informe final en PDF |

**Aplicación de Streamlit:** [pi3-abandono-clientes.streamlit.app](https://pi3-abandono-clientes.streamlit.app/) ·
**Informe final (PDF):** [`AE4/documento/Informe_Final_PI3_Abandono_Clientes.pdf`](AE4/documento/Informe_Final_PI3_Abandono_Clientes.pdf)

## AE4 · Métricas y visualización

### Aplicación de Streamlit

La aplicación [`AE4/app/streamlit_app.py`](AE4/app/streamlit_app.py) presenta el proyecto en estas secciones:

| Sección | Contenido |
|---|---|
| Inicio | Necesidad, pregunta de análisis, preguntas de negocio, dataset, indicadores generales y verificación de cifras |
| Respuestas en resumen | Las 6 preguntas en una sola página: gráfico + respuesta sencilla de cada una |
| P1 a P6 | Respuesta «En pocas palabras», indicadores, gráficos interactivos, cálculo y unidad de cada métrica, respuesta, decisión que apoya, limitación y tabla de datos |
| Explorador de segmentos | Filtros por contrato, internet, método de pago y antigüedad; métricas recalculadas en vivo |
| Conclusiones | Conclusiones, recomendaciones y limitaciones |

**Datos que usa:** `AE3/datos/churn_preparado.csv` y las tablas de `AE3/resultados/tablas/`. Al abrirse, la app recalcula
las tablas desde el dataset y comprueba que coinciden con los CSV (mensaje «Cifras verificadas»). Los textos de cada
pregunta están en [`AE4/app/contenido.py`](AE4/app/contenido.py), que comparten la app, el notebook y el informe.

**Ejecutar localmente** (desde la raíz del repositorio, con las dependencias instaladas):

```bash
streamlit run AE4/app/streamlit_app.py
```

Se abre en http://localhost:8501.

### Métricas y gráficos

| Pregunta | Métrica principal (unidad) | Gráfico |
|---|---|---|
| P1 | Tasa de abandono (%) e ingreso mensual perdido (unidades monetarias/mes) | Barras 100 % apiladas: clientes vs. ingreso |
| P2 | Tasa de abandono por tipo de contrato (%) | Barras con la tasa general como referencia |
| P3 | Tasa de abandono por rango de antigüedad (%) | Barras por tramos de 12 meses |
| P4 | Tasa por cuartil de cargo (%) y cargo mensual (unidades monetarias/mes) | Barras + diagrama de caja |
| P5 | Tasa por método de pago y por servicio de internet (%) | Barras horizontales y verticales |
| P6 | Tasa y participación por segmento contrato × internet (%) | Ranking en barras horizontales |

El notebook [`AE4/notebooks/AE4_metricas_visualizacion.ipynb`](AE4/notebooks/AE4_metricas_visualizacion.ipynb) verifica
las cifras, exporta [`AE4/resultados/metricas_por_pregunta.csv`](AE4/resultados/metricas_por_pregunta.csv) y genera los
gráficos del informe en [`AE4/resultados/graficos/`](AE4/resultados/graficos/).

### Publicación en Streamlit Community Cloud

1. Entrar a https://share.streamlit.io con la cuenta de GitHub.
2. **Create app → Deploy a public app from GitHub**.
3. Repositorio `kevin4965-hue/PI3-AE2-churn`, rama `main`, archivo principal `AE4/app/streamlit_app.py`.
4. En **Advanced settings**, elegir Python 3.12 y desplegar. Las dependencias se instalan desde `requirements.txt`.

## Necesidad

**Escenario hipotético:** el equipo de retención de clientes de una compañía de telecomunicaciones necesita
saber qué perfiles de cliente concentran las cancelaciones del servicio, para orientar sus campañas de fidelización.

**Pregunta de análisis (AE2):** ¿cómo varía la proporción de clientes que abandonaron el servicio según el tipo
de contrato, la antigüedad, el cargo mensual, el método de pago y el tipo de servicio de internet?

## Dataset

| Campo | Valor |
|---|---|
| Identificador | `scikit-learn/churn-prediction` |
| Enlace | https://huggingface.co/datasets/scikit-learn/churn-prediction |
| Split | `train` (único disponible), configuración por defecto, **sin muestreo** |
| Tamaño original | 7 043 filas × 21 columnas (una fila = un cliente) |
| Licencia | CC-BY-4.0 (permite redistribuir citando la fuente) |
| Procedencia | IBM Sample Datasets. Compañía de telecomunicaciones **ficticia** (datos no reales) |
| Fecha de consulta | 25 de octubre de 2026 |

Los datos originales se descargan desde Hugging Face al ejecutar los notebooks; el dataset es público y no requiere token.
El dataset **preparado** de la AE3 sí se publica en el repositorio. La licencia CC-BY-4.0 lo permite citando la fuente.

## AE3 · Transformación y enriquecimiento

### Preguntas de negocio abordadas

La pregunta de AE2 se desglosó en seis preguntas, una por cada componente del diseño inicial:

| # | Pregunta | Tabla de resultados |
|---|---|---|
| P1 | ¿Qué proporción de clientes abandonó y cuánto ingreso mensual representa? | `P1_resumen_general.csv` |
| P2 | ¿Cómo varía el abandono según el tipo de contrato? | `P2_abandono_por_contrato.csv` |
| P3 | ¿Cómo varía el abandono según la antigüedad del cliente? | `P3_abandono_por_antiguedad.csv` |
| P4 | ¿Se diferencian en sus cargos los clientes que abandonan? | `P4a_abandono_por_cargo_mensual.csv`, `P4b_comparacion_cargos.csv` |
| P5 | ¿Hay diferencias según el método de pago y el servicio de internet? | `P5a_abandono_por_metodo_pago.csv`, `P5b_abandono_por_internet.csv` |
| P6 | ¿Qué segmentos (contrato × internet) concentran el abandono? | `P6_ranking_segmentos.csv` |

**Hallazgo principal:** el 26,54 % de los clientes abandonó (30,50 % del ingreso mensual). El abandono se concentra en
contratos mes a mes (42,71 %), clientes del primer año (47,44 %), fibra óptica (41,89 %) y pago con cheque electrónico
(45,29 %). El segmento «Mes a mes | Fibra óptica» reúne el 62,17 % de los abandonos.

### Transformaciones

| Paso | Transformación | Registros afectados |
|---|---|---|
| 3.1 | `TotalCharges` convertido de texto a número | 7 043 |
| 3.2 | 11 `TotalCharges` vacíos (clientes con 0 meses) reemplazados por 0 y marcados en `cargo_total_imputado` | 11 |
| 3.3 | Control de nulos, duplicados (fila, ID y atributos) y espacios: sin problemas; 22 perfiles idénticos con distinto ID se conservan | 0 |
| 3.4 | Control de coherencia entre servicios y entre cargo total y mensual: sin incoherencias | 0 |
| 3.5 | Columnas en español (`snake_case`); Sí/No; «Sin servicio» unificado; contrato, internet y pago traducidos; contrato ordenado | 7 043 |
| 3.6 | Se elimina `genero` (no responde ninguna pregunta); se conservan todos los registros | 0 |

### Enriquecimiento (variables nuevas)

| Variable | Regla |
|---|---|
| `abandono_num` | 1 si abandonó, 0 si no |
| `rango_antiguedad` | Tramos de 12 meses (0–12 … 61–72) |
| `rango_cargo_mensual` | Cuartiles del cargo mensual (Q1 a Q4) |
| `num_servicios_adicionales` | Cantidad de servicios adicionales contratados (0–6) |
| `pago_automatico` | Sí si paga con transferencia o tarjeta automática |
| `ingreso_mensual_perdido` | Cargo mensual del cliente si abandonó; 0 si no |
| `segmento` | `tipo_contrato` + `servicio_internet` |

### Rutas de los resultados

| Archivo | Ruta |
|---|---|
| Dataset preparado (7 043 × 28) | [`AE3/datos/churn_preparado.csv`](AE3/datos/churn_preparado.csv) |
| Tablas de resultados (P1–P6) y bitácora | [`AE3/resultados/tablas/`](AE3/resultados/tablas/) |
| Resumen descriptivo del DataFrame final | [`AE3/resultados/resumen_dataframe_final.txt`](AE3/resultados/resumen_dataframe_final.txt) |
| Notebook ejecutado | [`AE3/notebooks/AE3_transformacion_churn.ipynb`](AE3/notebooks/AE3_transformacion_churn.ipynb) |
| Documento actualizado | [`AE3/documento/AE3_Transformacion_Enriquecimiento_Churn.docx`](AE3/documento/AE3_Transformacion_Enriquecimiento_Churn.docx) |

Los CSV se guardan en UTF-8 con BOM (`utf-8-sig`) para que Excel muestre bien las tildes.

## Estructura de archivos

```
├── .github/workflows/
│   └── ejecutar-ae2.yml                      # GitHub Action: ejecuta los notebooks de AE2 y AE3
├── AE2/
│   ├── documento/AE2_Necesidad_Diseno_Churn.docx
│   ├── notebooks/AE2_exploracion_churn.ipynb
│   └── resultados/resumen_dataframe.txt
├── AE3/
│   ├── datos/churn_preparado.csv             # dataset transformado y enriquecido
│   ├── documento/AE3_Transformacion_Enriquecimiento_Churn.docx
│   ├── notebooks/AE3_transformacion_churn.ipynb
│   └── resultados/
│       ├── resumen_dataframe_final.txt       # resumen .txt del DataFrame final
│       └── tablas/                           # P1–P6 y bitácora de transformaciones (.csv)
├── AE4/
│   ├── app/
│   │   ├── streamlit_app.py                  # aplicación de Streamlit
│   │   └── contenido.py                      # textos compartidos: preguntas, métricas, respuestas
│   ├── documento/
│   │   ├── Informe_Final_PI3_Abandono_Clientes.docx
│   │   └── Informe_Final_PI3_Abandono_Clientes.pdf   # informe completo del proyecto
│   ├── notebooks/AE4_metricas_visualizacion.ipynb
│   └── resultados/
│       ├── graficos/                         # gráficos PNG del informe
│       └── metricas_por_pregunta.csv
├── src/
│   └── clases_po/
│       ├── __init__.py
│       ├── hf_loader.py                      # clase HFDatasetLoader: obtiene el DataFrame
│       ├── indicadores.py                    # función tabla_abandono: tasas por grupo
│       └── reportes.py                       # clase Reportes: genera los resúmenes .txt
├── requirements.txt
└── README.md
```

## Pasos de ejecución

1. Clonar el repositorio y entrar a la carpeta.
2. Crear y activar un entorno virtual e instalar las dependencias.

   **Windows (PowerShell):**

   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

   **Linux / macOS / Codespaces (Bash):**

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. Ejecutar los notebooks en orden: todas las celdas de cada uno con **Kernel → Restart & Run All**.

   ```bash
   jupyter notebook AE2/notebooks/AE2_exploracion_churn.ipynb
   jupyter notebook AE3/notebooks/AE3_transformacion_churn.ipynb
   jupyter notebook AE4/notebooks/AE4_metricas_visualizacion.ipynb
   ```

   O desde la terminal, sin abrir Jupyter:

   ```bash
   jupyter nbconvert --to notebook --execute --inplace AE2/notebooks/AE2_exploracion_churn.ipynb
   jupyter nbconvert --to notebook --execute --inplace AE3/notebooks/AE3_transformacion_churn.ipynb
   jupyter nbconvert --to notebook --execute --inplace AE4/notebooks/AE4_metricas_visualizacion.ipynb
   ```

4. El notebook de AE3 regenera en cada ejecución el dataset preparado, las tablas `.csv` y
   `resumen_dataframe_final.txt`. También comprueba que los totales y porcentajes sean consistentes y que los
   archivos exportados coincidan con lo calculado.
5. Abrir la aplicación: `streamlit run AE4/app/streamlit_app.py`.

El GitHub Action (`.github/workflows/ejecutar-ae2.yml`) ejecuta los notebooks de AE2 y AE3 en cada `push` a `main`.

## Uso de las clases

```python
import sys
sys.path.insert(0, "src")

from clases_po import HFDatasetLoader, Reportes, tabla_abandono

loader = HFDatasetLoader("scikit-learn/churn-prediction", split="train")
df = loader.load()

Reportes(origen=loader.info()).guardar_reporte(df, "AE2/resultados/resumen_dataframe.txt")
# Con un DataFrame preparado (columnas abandono_num y cargo_mensual):
# tabla_abandono(df_preparado, "tipo_contrato")
```

Para un dataset privado, inicia sesión con `hf auth login`. `HFDatasetLoader` usará esa sesión automáticamente.
No escribas tokens en el código ni los subas a GitHub.
