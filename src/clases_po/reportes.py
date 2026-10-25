"""Generación de reportes de DataFrames."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd


class Reportes:
    """Imprime y guarda un resumen legible de un DataFrame.

    Args:
        origen: Diccionario opcional con el origen de los datos (por ejemplo,
            el resultado de ``HFDatasetLoader.info()``): dataset, config,
            split y si se usó una muestra. Se escribe al inicio del reporte.
    """

    def __init__(self, origen: dict | None = None) -> None:
        self.origen = origen or {}

    def generar_reporte(self, df: pd.DataFrame) -> str:
        """Genera el contenido textual del reporte."""
        self._validar_dataframe(df)
        lineas = [
            "RESUMEN DEL DATAFRAME",
            "=" * 60,
            f"Generado: {datetime.now():%Y-%m-%d %H:%M:%S}",
            "",
            "Origen de los datos:",
            f"- Dataset (Hugging Face): {self.origen.get('dataset', 'no indicado')}",
            f"- Configuración: {self.origen.get('config') or 'por defecto'}",
            f"- Split: {self.origen.get('split', 'no indicado')}",
            f"- Muestra: {self.origen.get('muestra', 'no indicado')}",
            "",
            "Dimensiones:",
            f"- Filas: {len(df)}",
            f"- Columnas: {len(df.columns)}",
            f"- Filas duplicadas: {int(df.duplicated().sum())}",
            "",
            "Columnas, tipos y valores nulos:",
            self._tabla_columnas(df),
        ]

        numericas = df.select_dtypes(include="number")
        if not numericas.empty:
            lineas += [
                "",
                "Estadísticas de las columnas numéricas:",
                numericas.describe().round(3).to_string(),
            ]

        return "\n".join(lineas) + "\n"

    def imprimir_reporte(self, df: pd.DataFrame) -> None:
        """Imprime en la consola el reporte del DataFrame."""
        print(self.generar_reporte(df), end="")

    def guardar_reporte(self, df: pd.DataFrame, ruta: str | Path) -> Path:
        """Guarda el reporte en UTF-8, creando la carpeta si no existe, y devuelve su ruta.

        Si el archivo ya existe, se sobrescribe (se regenera en cada ejecución).
        """
        path = Path(ruta)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.generar_reporte(df), encoding="utf-8")
        return path

    @staticmethod
    def _tabla_columnas(df: pd.DataFrame) -> str:
        tabla = pd.DataFrame({
            "tipo": df.dtypes.astype(str),
            "nulos": df.isna().sum(),
            "valores_unicos": df.nunique(),
        })
        return tabla.rename_axis("columna").to_string()

    @staticmethod
    def _validar_dataframe(df: pd.DataFrame) -> None:
        if not isinstance(df, pd.DataFrame):
            raise TypeError("df debe ser un pandas.DataFrame.")
