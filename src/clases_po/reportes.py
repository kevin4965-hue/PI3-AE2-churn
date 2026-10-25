"""Generación de reportes de DataFrames."""
from __future__ import annotations  # permite escribir tipos como "dict | None" en Python 3.9

from datetime import datetime  # para poner la fecha y hora en el reporte
from pathlib import Path  # para manejar rutas de archivos

import pandas as pd  # para trabajar con tablas (DataFrame)


class Reportes:
    """Imprime y guarda un resumen legible de un DataFrame.

    Args:
        origen: Diccionario opcional con el origen de los datos (por ejemplo,
            el resultado de ``HFDatasetLoader.info()``): dataset, config,
            split y si se usó una muestra. Se escribe al inicio del reporte.
    """

    def __init__(self, origen: dict | None = None) -> None:
        # Si no nos dan el origen, usamos un diccionario vacío.
        self.origen = origen or {}

    def generar_reporte(self, df: pd.DataFrame) -> str:
        """Genera el contenido textual del reporte."""
        # Verificamos que realmente nos pasen un DataFrame.
        self._validar_dataframe(df)

        # Armamos el reporte línea por línea.
        lineas = [
            "RESUMEN DEL DATAFRAME",
            "=" * 60,
            f"Generado: {datetime.now():%Y-%m-%d %H:%M:%S}",
            "",
            # De dónde salieron los datos.
            "Origen de los datos:",
            f"- Dataset (Hugging Face): {self.origen.get('dataset', 'no indicado')}",
            f"- Configuración: {self.origen.get('config') or 'por defecto'}",
            f"- Split: {self.origen.get('split', 'no indicado')}",
            f"- Muestra: {self.origen.get('muestra', 'no indicado')}",
            "",
            # Tamaño de la tabla.
            "Dimensiones:",
            f"- Filas: {len(df)}",
            f"- Columnas: {len(df.columns)}",
            f"- Filas duplicadas: {int(df.duplicated().sum())}",
            "",
            # Una fila por columna: tipo de dato, nulos y valores distintos.
            "Columnas, tipos y valores nulos:",
            self._tabla_columnas(df),
        ]

        # Si hay columnas numéricas, agregamos sus estadísticas básicas.
        numericas = df.select_dtypes(include="number")
        if not numericas.empty:
            lineas += [
                "",
                "Estadísticas de las columnas numéricas:",
                numericas.describe().round(3).to_string(),
            ]

        # Unimos todas las líneas en un solo texto.
        return "\n".join(lineas) + "\n"

    def imprimir_reporte(self, df: pd.DataFrame) -> None:
        """Imprime en la consola el reporte del DataFrame."""
        print(self.generar_reporte(df), end="")

    def guardar_reporte(self, df: pd.DataFrame, ruta: str | Path) -> Path:
        """Guarda el reporte en UTF-8, creando la carpeta si no existe, y devuelve su ruta.

        Si el archivo ya existe, se sobrescribe (se regenera en cada ejecución).
        """
        path = Path(ruta)
        # Creamos la carpeta de destino si no existe.
        path.parent.mkdir(parents=True, exist_ok=True)
        # Escribimos el reporte; encoding="utf-8" conserva tildes y ñ.
        path.write_text(self.generar_reporte(df), encoding="utf-8")
        return path

    @staticmethod
    def _tabla_columnas(df: pd.DataFrame) -> str:
        """Arma una tabla de texto con el tipo, los nulos y los valores únicos de cada columna."""
        tabla = pd.DataFrame({
            "tipo": df.dtypes.astype(str),      # tipo de dato de la columna
            "nulos": df.isna().sum(),           # cuántos valores vacíos tiene
            "valores_unicos": df.nunique(),     # cuántos valores distintos tiene
        })
        return tabla.rename_axis("columna").to_string()

    @staticmethod
    def _validar_dataframe(df: pd.DataFrame) -> None:
        """Lanza un error si lo recibido no es un DataFrame."""
        if not isinstance(df, pd.DataFrame):
            raise TypeError("df debe ser un pandas.DataFrame.")
