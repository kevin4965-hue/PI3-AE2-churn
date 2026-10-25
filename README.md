# PI3 — AE2: Ideación, diseño y documentación de la necesidad

Primera etapa del proyecto integrador de Analítica de Datos.
**Proyecto:** caracterización del abandono de clientes en una compañía de telecomunicaciones ficticia
según tipo de contrato, antigüedad y facturación.

## Propósito

Definir y documentar una necesidad de analítica descriptiva a partir de un dataset de Hugging Face,
y dejar listo el flujo técnico para obtener los datos, describirlos y generar un resumen automático en `.txt`.

## Necesidad

**Escenario hipotético:** el equipo de retención de clientes de una compañía de telecomunicaciones necesita
saber qué perfiles de cliente concentran las cancelaciones del servicio, para orientar sus campañas de fidelización.

**Pregunta de análisis:** ¿cómo varía la proporción de clientes que abandonaron el servicio (`Churn`) según el tipo
de contrato, la antigüedad, el cargo mensual, el método de pago y el tipo de servicio de internet?

El desarrollo completo (justificación, objetivos, marco teórico, ficha, diccionario, alcance y diseño) está en
[`AE2/documento/AE2_Necesidad_Diseno_Churn.docx`](AE2/documento/AE2_Necesidad_Diseno_Churn.docx).

## Dataset

| Campo | Valor |
|---|---|
| Identificador | `scikit-learn/churn-prediction` |
| Enlace | https://huggingface.co/datasets/scikit-learn/churn-prediction |
| Split | `train` (único disponible), configuración por defecto, **sin muestreo** |
| Tamaño | 7 043 filas × 21 columnas (una fila = un cliente) |
| Licencia | CC-BY-4.0 |
| Procedencia | IBM Sample Datasets. Compañía de telecomunicaciones **ficticia** (datos no reales) |
| Fecha de consulta | 25 de octubre de 2026 |

Los datos **no se guardan en el repositorio**: se descargan desde Hugging Face al ejecutar el notebook.
El dataset es público y no requiere token.

## Estructura de archivos

```
├── AE2/
│   ├── documento/
│   │   └── AE2_Necesidad_Diseno_Churn.docx   # documento de la necesidad y el diseño
│   ├── notebooks/
│   │   └── AE2_exploracion_churn.ipynb       # carga, descripción básica y resumen .txt
│   └── resultados/
│       └── resumen_dataframe.txt             # resumen generado automáticamente por el notebook
├── src/
│   └── clases_po/
│       ├── __init__.py
│       ├── hf_loader.py                      # clase HFDatasetLoader: obtiene el DataFrame
│       └── reportes.py                       # clase Reportes: genera el resumen .txt
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

3. Abrir el notebook y ejecutar todas las celdas en orden (**Kernel → Restart & Run All**):

   ```bash
   jupyter notebook AE2/notebooks/AE2_exploracion_churn.ipynb
   ```

4. Al terminar, el notebook crea (o regenera) `AE2/resultados/resumen_dataframe.txt` en UTF-8. La última celda
   comprueba que el archivo corresponde al DataFrame revisado.

También se puede ejecutar todo desde la terminal, sin abrir Jupyter:

```bash
jupyter nbconvert --to notebook --execute --inplace AE2/notebooks/AE2_exploracion_churn.ipynb
```

## Uso de las clases

```python
import sys
sys.path.insert(0, "src")

from clases_po import HFDatasetLoader, Reportes

loader = HFDatasetLoader("scikit-learn/churn-prediction", split="train")
df = loader.load()

Reportes(origen=loader.info()).guardar_reporte(df, "AE2/resultados/resumen_dataframe.txt")
```

Para un dataset privado, inicia sesión con `hf auth login`. `HFDatasetLoader` usará esa sesión automáticamente.
No escribas tokens en el código ni los subas a GitHub.
