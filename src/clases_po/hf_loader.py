"""Carga datasets de Hugging Face y, opcionalmente, los guarda en disco."""
from __future__ import annotations  # permite escribir tipos como "str | None" en Python 3.9

from pathlib import Path  # para manejar rutas de archivos

import pandas as pd  # para trabajar con tablas (DataFrame)
from datasets import load_dataset  # función de Hugging Face que descarga datasets


class HFDatasetLoader:
    """Descarga un dataset de Hugging Face y lo devuelve como DataFrame.

    Args:
        dataset_name: Identificador del dataset en Hugging Face, por ejemplo
            ``"scikit-learn/churn-prediction"``.
        config: Configuración del dataset, si tiene más de una.
        split: División que se desea cargar.
        token: Token de Hugging Face para datasets privados. Si no se indica,
            se usa la sesión guardada con ``hf auth login`` (si existe).
        cache_dir: Directorio de caché de Hugging Face.
        max_rows: Cantidad máxima de filas a cargar (muestra de las primeras filas).
        filename: Ruta opcional donde se guardará el DataFrame.
        file_type: Formato opcional de salida: ``csv``, ``json``, ``parquet``
            o ``xlsx``. Si no se indica, se infiere desde la extensión de ``filename``.
    """

    # Formatos en los que se puede guardar una copia de los datos.
    _SUPPORTED_FILE_TYPES = {"csv", "json", "parquet", "xlsx"}

    def __init__(
        self,
        dataset_name: str,
        config: str | None = None,
        split: str = "train",
        token: str | None = None,
        cache_dir: str | None = None,
        max_rows: int | None = None,
        filename: str | Path | None = None,
        file_type: str | None = None,
    ) -> None:
        # Guardamos los datos de configuración para usarlos al cargar.
        self.dataset_name = dataset_name
        self.config = config
        self.split = split
        self.token = token
        self.cache_dir = cache_dir
        self.max_rows = max_rows
        # Si nos dan un nombre de archivo, lo convertimos en ruta (Path).
        self.filename = Path(filename) if filename is not None else None
        self.file_type = self._normalize_file_type(file_type)
        # Aquí quedará el DataFrame cuando se llame a load().
        self.df: pd.DataFrame | None = None

        # Revisamos que los parámetros tengan sentido antes de descargar nada.
        if self.max_rows is not None and self.max_rows < 0:
            raise ValueError("max_rows debe ser mayor o igual que cero.")
        if self.file_type is not None and self.filename is None:
            raise ValueError("filename es obligatorio cuando se indica file_type.")

    def load(self) -> pd.DataFrame:
        """Descarga el dataset, lo guarda si se configuró una salida y retorna el DataFrame."""
        # 1. Descargamos el dataset desde Hugging Face.
        dataset = load_dataset(
            self.dataset_name,
            self.config,
            split=self.split,
            token=self.token,  # si es None, se usa la sesión de "hf auth login"
            cache_dir=self.cache_dir,
        )

        # 2. Si se pidió una muestra, nos quedamos solo con las primeras filas.
        if self.max_rows is not None:
            dataset = dataset.select(range(min(self.max_rows, len(dataset))))

        # 3. Convertimos el dataset de Hugging Face en un DataFrame de pandas.
        self.df = dataset.to_pandas()

        # 4. Si se indicó un archivo, guardamos una copia de los datos.
        if self.filename is not None:
            self._save(self.df)
        return self.df

    def info(self) -> dict:
        """Devuelve el origen y el tamaño del último DataFrame cargado."""
        # No se puede describir algo que todavía no se ha cargado.
        if self.df is None:
            raise RuntimeError("Llama a load() primero.")
        return {
            "dataset": self.dataset_name,
            "config": self.config,
            "split": self.split,
            # Indica si se cargó todo el split o solo una muestra.
            "muestra": (
                f"primeras {self.max_rows} filas" if self.max_rows is not None
                else "no (split completo)"
            ),
            "filas": len(self.df),
            "columnas": len(self.df.columns),
        }

    @classmethod
    def _normalize_file_type(cls, file_type: str | None) -> str | None:
        """Convierte el formato a minúsculas y sin punto: ".CSV" -> "csv"."""
        if not file_type:
            return None
        normalized = file_type.lower().lstrip(".")
        if normalized == "excel":  # aceptamos "excel" como sinónimo de "xlsx"
            normalized = "xlsx"
        if normalized not in cls._SUPPORTED_FILE_TYPES:
            supported = ", ".join(sorted(cls._SUPPORTED_FILE_TYPES))
            raise ValueError(f"Tipo de archivo no soportado: {file_type}. Use: {supported}.")
        return normalized

    def _save(self, df: pd.DataFrame) -> None:
        """Guarda el DataFrame en el formato indicado."""
        # Usamos el formato indicado o, si no hay, la extensión del archivo.
        file_type = self.file_type or self._normalize_file_type(self.filename.suffix)
        if file_type is None:
            raise ValueError(
                "No se pudo inferir el tipo de archivo. Indique file_type "
                "o use una extensión compatible en filename."
            )

        # Creamos la carpeta de destino si no existe.
        self.filename.parent.mkdir(parents=True, exist_ok=True)

        # index=False evita guardar el número de fila como una columna extra.
        if file_type == "csv":
            df.to_csv(self.filename, index=False)
        elif file_type == "json":
            df.to_json(self.filename, orient="records", force_ascii=False)
        elif file_type == "parquet":
            df.to_parquet(self.filename, index=False)
        elif file_type == "xlsx":
            df.to_excel(self.filename, index=False)
