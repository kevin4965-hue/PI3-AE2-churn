"""Aplicación de Streamlit: abandono de clientes de una compañía de telecomunicaciones (AE4).

Ejecutar desde la raíz del proyecto:
    streamlit run AE4/app/streamlit_app.py
"""
import inspect
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ---------------------------------------------------------------------------
# Rutas: la app vive en AE4/app; la raíz del proyecto está dos carpetas arriba.
# ---------------------------------------------------------------------------
APP = Path(__file__).resolve().parent
ROOT = APP.parents[1]
sys.path.insert(0, str(ROOT / "src"))   # para importar tabla_abandono
sys.path.insert(0, str(APP))            # para importar los textos compartidos

import contenido as C  # noqa: E402  (se importa después de ajustar sys.path)
from clases_po import tabla_abandono  # noqa: E402

DATASET = ROOT / "AE3" / "datos" / "churn_preparado.csv"
TABLAS = ROOT / "AE3" / "resultados" / "tablas"
REPO = "https://github.com/kevin4965-hue/PI3-AE2-churn"

st.set_page_config(page_title="Abandono de clientes · PI3", page_icon="📉", layout="wide")


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------
def fmt(valor, decimales=2):
    """Número en formato español: 26.54 -> '26,54'. Los enteros sin decimales."""
    if decimales == 0:
        return f"{int(round(valor))}"
    return f"{valor:.{decimales}f}".replace(".", ",")


@st.cache_data
def cargar_datos():
    """Lee el dataset preparado y las tablas de resultados exportadas en AE3."""
    df = pd.read_csv(DATASET, encoding="utf-8-sig")
    # El CSV no guarda el orden de las categorías: lo restablecemos.
    df["tipo_contrato"] = pd.Categorical(df["tipo_contrato"], ["Mes a mes", "Un año", "Dos años"], ordered=True)
    orden_antig = sorted(df["rango_antiguedad"].unique(), key=lambda x: int(x.split("-")[0]))
    df["rango_antiguedad"] = pd.Categorical(df["rango_antiguedad"], orden_antig, ordered=True)
    df["rango_cargo_mensual"] = pd.Categorical(df["rango_cargo_mensual"],
                                               sorted(df["rango_cargo_mensual"].unique()), ordered=True)
    tablas = {f.stem: pd.read_csv(f, encoding="utf-8-sig") for f in sorted(TABLAS.glob("*.csv"))}
    return df, tablas


@st.cache_data
def verificar(df, tablas):
    """Recalcula las tablas desde el dataset y las compara con los CSV de AE3. Devuelve la lista de diferencias."""
    pruebas = {
        "P2_abandono_por_contrato": ["tipo_contrato"],
        "P3_abandono_por_antiguedad": ["rango_antiguedad"],
        "P4a_abandono_por_cargo_mensual": ["rango_cargo_mensual"],
        "P5a_abandono_por_metodo_pago": ["metodo_pago"],
        "P5b_abandono_por_internet": ["servicio_internet"],
        "P6_ranking_segmentos": ["tipo_contrato", "servicio_internet"],
    }
    errores = []
    for nombre, claves in pruebas.items():
        nueva = tabla_abandono(df, claves if len(claves) > 1 else claves[0])
        a = nueva.astype({c: str for c in claves}).sort_values(claves).reset_index(drop=True)
        b = tablas[nombre].astype({c: str for c in claves}).sort_values(claves).reset_index(drop=True)
        for col in a.columns:
            if col not in claves and (a[col] - b[col]).abs().max() >= 0.01:
                errores.append(f"{nombre}: {col}")
    if abs(tablas["P1_resumen_general"].loc[0, "tasa_abandono_pct"] - df["abandono_num"].mean() * 100) >= 0.01:
        errores.append("P1_resumen_general")
    return errores


def estilo(fig, alto=380):
    """Estilo común de los gráficos: fondo limpio, cuadrícula suave y tooltips."""
    fig.update_layout(
        height=alto, margin=dict(l=10, r=10, t=50, b=10), plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)", font=dict(family="Arial", size=13), hoverlabel=dict(font_size=13),
        legend=dict(orientation="h", yanchor="bottom", y=1.0, xanchor="right", x=1, title=None),
        title=dict(x=0, xanchor="left", font=dict(size=16)),
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="rgba(128,128,128,0.18)")
    return fig


def barras_tasa(tabla, columna, titulo, etiqueta, horizontal=False, alto=None):
    """Barras de tasa de abandono por grupo, con la tasa general como línea de referencia."""
    t = tabla.copy()
    if not horizontal:
        # Etiquetas largas en dos líneas: "Q1 Bajo (18.25-35.50)" -> "Q1 Bajo<br>(18.25-35.50)".
        t[columna] = t[columna].astype(str).str.replace(" (", "<br>(", regex=False)
    t["texto"] = t["tasa_abandono_pct"].map(lambda v: f"{fmt(v)} %")
    datos_hover = {"clientes": True, "abandonos": True, "participacion_abandonos_pct": ":.2f",
                   "ingreso_mensual_perdido": ":.2f", "texto": False}
    etiquetas = {columna: etiqueta, "tasa_abandono_pct": "Tasa de abandono (%)", "clientes": "Clientes",
                 "abandonos": "Abandonos", "participacion_abandonos_pct": "Part. en abandonos (%)",
                 "ingreso_mensual_perdido": "Ingreso mensual perdido"}
    if horizontal:
        fig = px.bar(t, y=columna, x="tasa_abandono_pct", orientation="h", text="texto", title=titulo,
                     hover_data=datos_hover, labels=etiquetas, color_discrete_sequence=[C.AZUL])
        fig.add_vline(x=C.TASA_GENERAL, line_dash="dash", line_color=C.GRIS)
        fig.update_yaxes(categoryorder="array", categoryarray=list(t[columna])[::-1], title=etiqueta)
        fig.update_xaxes(range=[0, t["tasa_abandono_pct"].max() * 1.35], title="Tasa de abandono (%)", showgrid=True,
                         gridcolor="rgba(128,128,128,0.18)")
    else:
        fig = px.bar(t, x=columna, y="tasa_abandono_pct", text="texto", title=titulo, hover_data=datos_hover,
                     labels=etiquetas, color_discrete_sequence=[C.AZUL])
        fig.add_hline(y=C.TASA_GENERAL, line_dash="dash", line_color=C.GRIS)
        fig.update_yaxes(range=[0, t["tasa_abandono_pct"].max() * 1.2], title="Tasa de abandono (%)")
        fig.update_xaxes(title=etiqueta)
    # Entrada de leyenda para la línea de referencia (la línea en sí no aparece en la leyenda).
    fig.add_trace(go.Scatter(x=[None], y=[None], mode="lines", line=dict(color=C.GRIS, dash="dash"),
                             name=f"Tasa general {fmt(C.TASA_GENERAL)} %"))
    fig.update_traces(textposition="outside", cliponaxis=False, selector=dict(type="bar"), width=0.6)
    fig.update_layout(showlegend=True)
    if alto is None:
        alto = 420 if horizontal and len(t) > 5 else 380
    return estilo(fig, alto)


# Streamlit 1.52+ usa width="stretch"; las versiones anteriores, use_container_width=True.
ANCHO_PLOTLY = ({"width": "stretch"} if "width" in inspect.signature(st.plotly_chart).parameters
                else {"use_container_width": True})


def grafico(fig, key=None):
    """Muestra un gráfico de Plotly ocupando todo el ancho disponible."""
    st.plotly_chart(fig, key=key, **ANCHO_PLOTLY)


def ficha_metricas(clave):
    """Muestra cómo se calcula cada métrica de la pregunta y en qué unidad se expresa."""
    with st.expander("📐 Métricas: cálculo y unidad"):
        st.dataframe(pd.DataFrame(C.PREGUNTAS[clave]["metricas"], columns=["Métrica", "Cálculo", "Unidad"]),
                     hide_index=True)


def respuesta(clave):
    """Respuesta, decisión que apoya y limitación de la pregunta."""
    p = C.PREGUNTAS[clave]
    st.markdown(f"**Respuesta.** {p['respuesta']}")
    col1, col2 = st.columns(2)
    col1.success(f"**Decisión que apoya:** {p['decision']}", icon="✅")
    col2.warning(f"**Limitación:** {p['limitacion']}", icon="⚠️")


def ver_tabla(tabla, nombre_csv):
    """Tabla de datos del gráfico (para leer los valores exactos)."""
    with st.expander(f"🔢 Ver tabla de datos ({nombre_csv}.csv)"):
        st.dataframe(tabla, hide_index=True, width="stretch")


def encabezado(clave):
    p = C.PREGUNTAS[clave]
    st.header(f"{clave}. {p['titulo']}")
    st.markdown(f"#### {p['pregunta']}")
    # Respuesta sencilla, antes del detalle.
    st.info(f"**En pocas palabras:** {p['respuesta_corta']}", icon="💡")


def grafico_p1(p1, alto=300, titulo="Quienes abandonan pesan más en el ingreso que en la cantidad de clientes"):
    """Barras 100 % apiladas: la misma división (permanece / abandonó) medida en clientes y en ingreso."""
    datos = pd.DataFrame({
        "Medida": ["Clientes", "Clientes", "Ingreso mensual", "Ingreso mensual"],
        "Grupo": ["Permanece", "Abandonó", "Permanece", "Abandonó"],
        "Porcentaje": [100 - p1["tasa_abandono_pct"], p1["tasa_abandono_pct"],
                       100 - p1["ingreso_perdido_pct"], p1["ingreso_perdido_pct"]],
    })
    datos["texto"] = datos["Porcentaje"].map(lambda v: f"{fmt(v)} %")
    fig = px.bar(datos, y="Medida", x="Porcentaje", color="Grupo", orientation="h", text="texto",
                 title=titulo,
                 color_discrete_map={"Permanece": C.AZUL, "Abandonó": C.NARANJA},
                 labels={"Porcentaje": "Porcentaje del total (%)", "Medida": ""},
                 hover_data={"texto": False, "Porcentaje": ":.2f"})
    fig.update_traces(marker_line_color="white", marker_line_width=2, insidetextanchor="middle")
    fig.update_xaxes(range=[0, 100])
    return estilo(fig, alto)


def tabla_p2(tablas):
    """Tabla P2 en el orden lógico del contrato (de menor a mayor compromiso)."""
    t = tablas["P2_abandono_por_contrato"].copy()
    t["tipo_contrato"] = pd.Categorical(t["tipo_contrato"], ["Mes a mes", "Un año", "Dos años"], ordered=True)
    return t.sort_values("tipo_contrato")


def tabla_p3(tablas):
    """Tabla P3 ordenada por antigüedad (0-12, 13-24, ...)."""
    t = tablas["P3_abandono_por_antiguedad"].copy()
    t["orden"] = t["rango_antiguedad"].str.split("-").str[0].astype(int)
    return t.sort_values("orden").drop(columns="orden")


def tabla_p6(tablas):
    """Tabla P6 con una columna 'segmento' (contrato | internet)."""
    t = tablas["P6_ranking_segmentos"].copy()
    t["segmento"] = t["tipo_contrato"] + " | " + t["servicio_internet"]
    return t


# ---------------------------------------------------------------------------
# Páginas
# ---------------------------------------------------------------------------
def pagina_inicio(df, tablas, errores):
    st.title("📉 ¿Qué clientes abandonan el servicio?")
    st.caption("Proyecto integrador · Analítica de Datos · Institución Universitaria Digital de Antioquia")

    p1 = tablas["P1_resumen_general"].iloc[0]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Clientes analizados", fmt(p1["clientes"], 0))
    c2.metric("Abandonaron en el último mes", fmt(p1["abandonos"], 0))
    c3.metric("Tasa de abandono", f"{fmt(p1['tasa_abandono_pct'])} %")
    c4.metric("Ingreso mensual perdido", f"{fmt(p1['ingreso_perdido_pct'])} %",
              help="Suma del cargo mensual de quienes abandonaron ÷ ingreso mensual total.")

    st.subheader("Necesidad")
    st.write(C.NECESIDAD)
    st.subheader("Pregunta de análisis")
    st.info(C.PREGUNTA_GENERAL)

    st.subheader("Preguntas de negocio")
    st.dataframe(pd.DataFrame([(k, p["pregunta"]) for k, p in C.PREGUNTAS.items()], columns=["#", "Pregunta"]),
                 hide_index=True, width="stretch")

    st.subheader("Dataset")
    d = C.DATASET
    st.markdown(
        f"- **{d['nombre']}** · [`{d['id']}`]({d['enlace']}) en Hugging Face, split `{d['split']}`\n"
        f"- Licencia {d['licencia']} · {d['procedencia']}\n"
        f"- Original: {d['tamano_original']} · Preparado: {d['tamano_preparado']}\n"
        f"- Cada fila es **un cliente**. La app lee `AE3/datos/churn_preparado.csv` y las tablas de "
        f"`AE3/resultados/tablas/`."
    )
    if errores:
        st.error("Las tablas no coinciden con el dataset: " + ", ".join(errores))
    else:
        st.success("Cifras verificadas: las tablas de la AE3 coinciden con un nuevo cálculo desde el dataset preparado.",
                   icon="✔️")


def pagina_p1(df, tablas):
    encabezado("P1")
    p1 = tablas["P1_resumen_general"].iloc[0]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Tasa de abandono", f"{fmt(p1['tasa_abandono_pct'])} %")
    c2.metric("Clientes que abandonaron", fmt(p1["abandonos"], 0), help=f"de {fmt(p1['clientes'], 0)} clientes")
    c3.metric("Ingreso mensual perdido", fmt(p1["ingreso_mensual_perdido"]), help="Unidades monetarias por mes")
    c4.metric("% del ingreso mensual", f"{fmt(p1['ingreso_perdido_pct'])} %")

    grafico(grafico_p1(p1))
    ficha_metricas("P1")
    respuesta("P1")
    ver_tabla(tablas["P1_resumen_general"], "P1_resumen_general")


def pagina_p2(df, tablas):
    encabezado("P2")
    t = tabla_p2(tablas)
    mm = t[t["tipo_contrato"] == "Mes a mes"].iloc[0]
    c1, c2, c3 = st.columns(3)
    c1.metric("Tasa en contrato mes a mes", f"{fmt(mm['tasa_abandono_pct'])} %",
              delta=f"{fmt(mm['tasa_abandono_pct'] - C.TASA_GENERAL)} pp vs. general", delta_color="inverse")
    c2.metric("Participación en los abandonos", f"{fmt(mm['participacion_abandonos_pct'])} %")
    c3.metric("Participación en el ingreso perdido", f"{fmt(mm['participacion_ingreso_perdido_pct'])} %")
    grafico(barras_tasa(t, "tipo_contrato", "Tasa de abandono por tipo de contrato", "Tipo de contrato"))
    ficha_metricas("P2")
    respuesta("P2")
    ver_tabla(t, "P2_abandono_por_contrato")


def pagina_p3(df, tablas):
    encabezado("P3")
    t = tabla_p3(tablas)
    primero, ultimo = t.iloc[0], t.iloc[-1]
    c1, c2, c3 = st.columns(3)
    c1.metric("Tasa en el primer año", f"{fmt(primero['tasa_abandono_pct'])} %")
    c2.metric("Tasa con 61-72 meses", f"{fmt(ultimo['tasa_abandono_pct'])} %")
    c3.metric("Abandonos del primer año", f"{fmt(primero['participacion_abandonos_pct'])} %",
              help="Participación del primer año en el total de abandonos")
    grafico(barras_tasa(t, "rango_antiguedad", "Tasa de abandono por antigüedad del cliente",
                                "Antigüedad (meses)"))
    ficha_metricas("P3")
    respuesta("P3")
    ver_tabla(t, "P3_abandono_por_antiguedad")


def pagina_p4(df, tablas):
    encabezado("P4")
    t = tablas["P4a_abandono_por_cargo_mensual"]
    comp = tablas["P4b_comparacion_cargos"].set_index("abandono")
    c1, c2, c3 = st.columns(3)
    c1.metric("Cargo mensual promedio · abandonó", fmt(comp.loc["Sí", "cargo_mensual_promedio"]),
              delta=fmt(comp.loc["Sí", "cargo_mensual_promedio"] - comp.loc["No", "cargo_mensual_promedio"]),
              delta_color="off", help="Diferencia frente a quienes permanecen (unidades monetarias/mes)")
    c2.metric("Cargo mensual promedio · permanece", fmt(comp.loc["No", "cargo_mensual_promedio"]))
    c3.metric("Ingreso perdido en Q3 + Q4", f"{fmt(t['participacion_ingreso_perdido_pct'].iloc[2:].sum())} %")

    izq, der = st.columns(2)
    with izq:
        grafico(barras_tasa(t, "rango_cargo_mensual", "Tasa de abandono por cuartil de cargo mensual",
                                    "Cuartil de cargo mensual (unidades monetarias/mes)"))
    with der:
        fig = px.box(df, x="cargo_mensual", y="abandono", color="abandono", orientation="h",
                     category_orders={"abandono": ["Sí", "No"]},
                     color_discrete_map={"No": C.AZUL, "Sí": C.NARANJA},
                     labels={"cargo_mensual": "Cargo mensual (unidades monetarias/mes)", "abandono": "¿Abandonó?"},
                     title="Distribución del cargo mensual según abandono")
        fig.update_layout(showlegend=False)
        grafico(estilo(fig))
    ficha_metricas("P4")
    respuesta("P4")
    ver_tabla(t, "P4a_abandono_por_cargo_mensual")
    ver_tabla(tablas["P4b_comparacion_cargos"], "P4b_comparacion_cargos")


def pagina_p5(df, tablas):
    encabezado("P5")
    pago = tablas["P5a_abandono_por_metodo_pago"]
    internet = tablas["P5b_abandono_por_internet"]
    auto = tabla_abandono(df, "pago_automatico").set_index("pago_automatico")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Tasa · cheque electrónico", f"{fmt(pago.iloc[0]['tasa_abandono_pct'])} %")
    c2.metric("Tasa · pago automático", f"{fmt(auto.loc['Sí', 'tasa_abandono_pct'])} %")
    c3.metric("Tasa · pago no automático", f"{fmt(auto.loc['No', 'tasa_abandono_pct'])} %")
    c4.metric("Tasa · fibra óptica", f"{fmt(internet.iloc[0]['tasa_abandono_pct'])} %")
    izq, der = st.columns(2)
    with izq:
        grafico(barras_tasa(pago, "metodo_pago", "Tasa de abandono por método de pago", "Método de pago",
                                    horizontal=True))
    with der:
        grafico(barras_tasa(internet, "servicio_internet", "Tasa de abandono por servicio de internet",
                                    "Servicio de internet"))
    ficha_metricas("P5")
    respuesta("P5")
    ver_tabla(pago, "P5a_abandono_por_metodo_pago")
    ver_tabla(internet, "P5b_abandono_por_internet")


def pagina_p6(df, tablas):
    encabezado("P6")
    t = tabla_p6(tablas)
    top = t.iloc[0]
    c1, c2, c3 = st.columns(3)
    c1.metric(f"Tasa · {top['segmento']}", f"{fmt(top['tasa_abandono_pct'])} %")
    c2.metric("Participación en los abandonos", f"{fmt(top['participacion_abandonos_pct'])} %")
    c3.metric("Participación en el ingreso perdido", f"{fmt(top['participacion_ingreso_perdido_pct'])} %")

    medida = st.radio("Ordenar y mostrar por:", ["Tasa de abandono", "Participación en los abandonos",
                                                  "Participación en el ingreso perdido"], horizontal=True)
    if medida == "Tasa de abandono":
        grafico(barras_tasa(t, "segmento", "Ranking de segmentos por tasa de abandono",
                                    "Segmento (contrato | internet)", horizontal=True))
    else:
        col = "participacion_abandonos_pct" if medida == "Participación en los abandonos" else \
            "participacion_ingreso_perdido_pct"
        orden = t.sort_values(col, ascending=False)
        orden["texto"] = orden[col].map(lambda v: f"{fmt(v)} %")
        fig = px.bar(orden, y="segmento", x=col, orientation="h", text="texto", title=f"{medida} por segmento",
                     labels={col: f"{medida} (%)", "segmento": "Segmento (contrato | internet)"},
                     hover_data={"clientes": True, "abandonos": True, "texto": False},
                     color_discrete_sequence=[C.NARANJA])
        fig.update_yaxes(categoryorder="array", categoryarray=list(orden["segmento"])[::-1])
        fig.update_xaxes(range=[0, orden[col].max() * 1.2], showgrid=True, gridcolor="rgba(128,128,128,0.18)")
        fig.update_traces(textposition="outside", cliponaxis=False, width=0.6)
        grafico(estilo(fig, 420))
    ficha_metricas("P6")
    respuesta("P6")
    ver_tabla(t.drop(columns="segmento"), "P6_ranking_segmentos")


def pagina_respuestas(df, tablas):
    """Todas las preguntas en una sola página: gráfico + respuesta sencilla."""
    st.title("✅ Respuestas en resumen")
    st.write("Cada pregunta de negocio con su gráfico y una respuesta sencilla. "
             "El detalle (métricas, decisión y limitaciones) está en la sección de cada pregunta.")

    p1 = tablas["P1_resumen_general"].iloc[0]
    pago = tablas["P5a_abandono_por_metodo_pago"]
    internet = tablas["P5b_abandono_por_internet"]
    # Gráfico (o gráficos) de cada pregunta, en versión compacta.
    graficos = {
        "P1": [("", grafico_p1(p1, alto=260, titulo="Clientes e ingreso según abandono"))],
        "P2": [("", barras_tasa(tabla_p2(tablas), "tipo_contrato", "Tasa de abandono por tipo de contrato",
                                "Tipo de contrato", alto=330))],
        "P3": [("", barras_tasa(tabla_p3(tablas), "rango_antiguedad", "Tasa de abandono por antigüedad",
                                "Antigüedad (meses)", alto=330))],
        "P4": [("", barras_tasa(tablas["P4a_abandono_por_cargo_mensual"], "rango_cargo_mensual",
                                "Tasa de abandono por cuartil de cargo mensual",
                                "Cuartil de cargo mensual (unidades monetarias/mes)", alto=350))],
        "P5": [("Método de pago", barras_tasa(pago, "metodo_pago", "Tasa de abandono por método de pago",
                                              "Método de pago", horizontal=True, alto=330)),
               ("Servicio de internet", barras_tasa(internet, "servicio_internet",
                                                    "Tasa de abandono por servicio de internet",
                                                    "Servicio de internet", alto=330))],
        "P6": [("", barras_tasa(tabla_p6(tablas), "segmento", "Ranking de segmentos por tasa de abandono",
                                "Segmento (contrato | internet)", horizontal=True, alto=400))],
    }

    for clave, p in C.PREGUNTAS.items():
        with st.container(border=True):
            st.subheader(f"{clave}. {p['pregunta']}")
            izquierda, derecha = st.columns([3, 2], gap="large")
            with izquierda:
                lista = graficos[clave]
                if len(lista) == 1:
                    grafico(lista[0][1], key=f"resumen_{clave}")
                else:
                    # Si la pregunta tiene dos gráficos, se muestran en pestañas.
                    pestanas = st.tabs([nombre for nombre, _ in lista])
                    for i, (pestana, (_, fig)) in enumerate(zip(pestanas, lista)):
                        with pestana:
                            grafico(fig, key=f"resumen_{clave}_{i}")
            with derecha:
                st.markdown("**Respuesta**")
                st.markdown(f"##### {p['respuesta_corta']}")
                st.caption(f"💼 {p['decision']}")
    st.caption("Línea gris punteada: tasa general de abandono (26,54 %). Pasa el cursor sobre las barras para ver el detalle.")


def pagina_explorador(df, tablas):
    st.header("🔎 Explorador de segmentos")
    st.write("Filtra los clientes y observa cómo cambian las métricas. Se calculan en vivo desde el dataset preparado.")
    f1, f2, f3, f4 = st.columns(4)
    contratos = f1.multiselect("Tipo de contrato", list(df["tipo_contrato"].cat.categories),
                               default=list(df["tipo_contrato"].cat.categories))
    servicios = f2.multiselect("Servicio de internet", sorted(df["servicio_internet"].unique()),
                               default=sorted(df["servicio_internet"].unique()))
    pagos = f3.multiselect("Método de pago", sorted(df["metodo_pago"].unique()), default=sorted(df["metodo_pago"].unique()))
    meses = f4.slider("Antigüedad (meses)", 0, 72, (0, 72))

    filtro = df[df["tipo_contrato"].isin(contratos) & df["servicio_internet"].isin(servicios)
                & df["metodo_pago"].isin(pagos) & df["antiguedad_meses"].between(*meses)]
    if filtro.empty:
        st.warning("No hay clientes con esa combinación de filtros.")
        return
    tasa = filtro["abandono_num"].mean() * 100
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Clientes", fmt(len(filtro), 0), help=f"{fmt(len(filtro) / len(df) * 100)} % del total")
    c2.metric("Abandonos", fmt(filtro["abandono_num"].sum(), 0))
    c3.metric("Tasa de abandono", f"{fmt(tasa)} %", delta=f"{fmt(tasa - C.TASA_GENERAL)} pp vs. general",
              delta_color="inverse")
    c4.metric("Ingreso mensual perdido", fmt(filtro["ingreso_mensual_perdido"].sum()))
    if len(filtro) < 100:
        st.caption("⚠️ Menos de 100 clientes: la tasa puede ser poco estable.")
    grafico(barras_tasa(tabla_abandono(filtro, "rango_antiguedad"), "rango_antiguedad",
                                "Tasa de abandono por antigüedad (clientes filtrados)", "Antigüedad (meses)"))


def pagina_conclusiones(df, tablas):
    st.header("Conclusiones, recomendaciones y limitaciones")
    st.subheader("Conclusiones")
    for c in C.CONCLUSIONES:
        st.markdown(f"- {c}")
    st.subheader("Recomendaciones para el equipo de retención")
    for r in C.RECOMENDACIONES:
        st.markdown(f"- {r}")
    st.subheader("Limitaciones")
    for lim in C.LIMITACIONES:
        st.markdown(f"- {lim}")
    st.caption("Las recomendaciones se apoyan en asociaciones descriptivas; conviene validarlas con una campaña piloto.")


# ---------------------------------------------------------------------------
# Navegación
# ---------------------------------------------------------------------------
df, tablas = cargar_datos()
errores = verificar(df, tablas)

PAGINAS = {
    "Inicio": lambda: pagina_inicio(df, tablas, errores),
    "Respuestas en resumen": lambda: pagina_respuestas(df, tablas),
    **{f"{k}. {p['titulo']}": (lambda f=f: f(df, tablas)) for (k, p), f in zip(
        C.PREGUNTAS.items(), [pagina_p1, pagina_p2, pagina_p3, pagina_p4, pagina_p5, pagina_p6])},
    "Explorador de segmentos": lambda: pagina_explorador(df, tablas),
    "Conclusiones": lambda: pagina_conclusiones(df, tablas),
}

with st.sidebar:
    st.title("Abandono de clientes")
    eleccion = st.radio("Secciones", list(PAGINAS), label_visibility="collapsed")
    st.divider()
    st.caption(f"Dataset: [{C.DATASET['id']}]({C.DATASET['enlace']}) · compañía ficticia")
    st.caption(f"Código: [repositorio en GitHub]({REPO})")
    st.caption("Autor: Jose Quevin Ordoñez Sánchez")

PAGINAS[eleccion]()
