"""Indicadores de abandono de clientes por grupo."""
from __future__ import annotations  # permite escribir tipos como "list | None" en Python 3.9

import pandas as pd  # para trabajar con tablas (DataFrame)


def tabla_abandono(
    df: pd.DataFrame,
    grupo: str | list[str],
    col_abandono: str = "abandono_num",
    col_cargo: str = "cargo_mensual",
) -> pd.DataFrame:
    """Resume el abandono de clientes por uno o varios grupos.

    Args:
        df: DataFrame preparado; debe tener una columna 0/1 de abandono y el cargo mensual.
        grupo: Columna (o lista de columnas) por la que se agrupa, por ejemplo "tipo_contrato".
        col_abandono: Columna con 1 si el cliente abandonó y 0 si permaneció.
        col_cargo: Columna con el cargo mensual del cliente.

    Returns:
        Una fila por grupo con estas columnas:
        clientes, abandonos, tasa_abandono_pct, participacion_clientes_pct,
        participacion_abandonos_pct, cargo_mensual_promedio,
        ingreso_mensual_perdido y participacion_ingreso_perdido_pct.
    """
    # Cargo mensual solo de los clientes que abandonaron (0 para los que siguen).
    perdido = df[col_cargo].where(df[col_abandono] == 1, 0)

    # Agrupamos y calculamos los conteos y sumas básicas.
    # observed=True: solo muestra las combinaciones de grupos que existen en los datos.
    tabla = (
        df.assign(_perdido=perdido)
        .groupby(grupo, observed=True)
        .agg(
            clientes=(col_abandono, "size"),           # cuántos clientes hay en el grupo
            abandonos=(col_abandono, "sum"),           # cuántos abandonaron (suma de unos)
            cargo_mensual_promedio=(col_cargo, "mean"),
            ingreso_mensual_perdido=("_perdido", "sum"),
        )
    )

    # Porcentajes: tasa dentro del grupo y participación sobre el total.
    tabla["tasa_abandono_pct"] = tabla["abandonos"] / tabla["clientes"] * 100
    tabla["participacion_clientes_pct"] = tabla["clientes"] / tabla["clientes"].sum() * 100
    tabla["participacion_abandonos_pct"] = tabla["abandonos"] / tabla["abandonos"].sum() * 100
    tabla["participacion_ingreso_perdido_pct"] = (
        tabla["ingreso_mensual_perdido"] / tabla["ingreso_mensual_perdido"].sum() * 100
    )

    # Ordenamos las columnas y redondeamos a 2 decimales para presentar.
    columnas = [
        "clientes", "abandonos", "tasa_abandono_pct", "participacion_clientes_pct",
        "participacion_abandonos_pct", "cargo_mensual_promedio",
        "ingreso_mensual_perdido", "participacion_ingreso_perdido_pct",
    ]
    return tabla[columnas].round(2).reset_index()
