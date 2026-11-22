"""Textos del proyecto: necesidad, preguntas, métricas, respuestas y conclusiones.

Se guardan en un solo lugar para que la aplicación de Streamlit, el notebook de AE4
y el documento final digan exactamente lo mismo.
"""

# Colores de los gráficos (paleta validada para personas con daltonismo).
AZUL = "#2a78d6"      # métrica principal / clientes que permanecen
NARANJA = "#eb6834"   # clientes que abandonaron
GRIS = "#8a8984"      # líneas de referencia (promedio general)

TASA_GENERAL = 26.54  # % de abandono de todo el dataset (P1), usada como referencia en los gráficos

DATASET = {
    "nombre": "Telco Customer Churn",
    "id": "scikit-learn/churn-prediction",
    "enlace": "https://huggingface.co/datasets/scikit-learn/churn-prediction",
    "split": "train (completo, sin muestreo)",
    "licencia": "CC-BY-4.0",
    "procedencia": "IBM Sample Datasets; compañía de telecomunicaciones ficticia",
    "tamano_original": "7043 clientes × 21 columnas",
    "tamano_preparado": "7043 clientes × 28 columnas (AE3)",
}

NECESIDAD = (
    "El equipo de retención de clientes de una compañía de telecomunicaciones necesita saber qué perfiles de "
    "cliente concentran las cancelaciones del servicio, para orientar sus campañas de fidelización. "
    "Es un escenario hipotético: los datos son de una compañía ficticia."
)

PREGUNTA_GENERAL = (
    "¿Cómo varía la proporción de clientes que abandonaron el servicio según el tipo de contrato, la antigüedad, "
    "el cargo mensual, el método de pago y el tipo de servicio de internet?"
)

# Una entrada por pregunta de negocio.
PREGUNTAS = {
    "P1": {
        "titulo": "Magnitud del abandono",
        "pregunta": "¿Qué proporción de clientes abandonó y cuánto ingreso mensual representa?",
        "respuesta_corta": "Uno de cada cuatro clientes se fue (26,54 %), y esos clientes representaban el 30,50 % del ingreso mensual.",
        "metricas": [
            ("Tasa de abandono", "abandonos ÷ clientes × 100", "%"),
            ("Ingreso mensual perdido", "suma del cargo mensual de los clientes que abandonaron", "unidades monetarias / mes"),
            ("Participación del ingreso perdido", "ingreso mensual perdido ÷ ingreso mensual total × 100", "%"),
        ],
        "respuesta": (
            "1869 de 7043 clientes abandonaron el servicio en el último mes: una tasa del 26,54 %, cerca de uno de "
            "cada cuatro clientes. Esos clientes pagaban 139130,85 al mes, el 30,50 % del ingreso mensual. El ingreso "
            "perdido pesa más que la proporción de clientes, porque se van, en promedio, clientes con cargos más altos."
        ),
        "decision": "Dimensionar el problema y fijar una línea base para medir el efecto de las campañas de retención.",
        "limitacion": "Es una foto de un solo mes: sin fechas no se sabe si la tasa sube o baja con el tiempo.",
    },
    "P2": {
        "titulo": "Tipo de contrato",
        "pregunta": "¿Cómo varía el abandono según el tipo de contrato?",
        "respuesta_corta": "Los clientes con contrato mes a mes son los que más se van: 42,71 %, frente a solo 2,83 % con contrato de dos años.",
        "metricas": [
            ("Tasa de abandono por contrato", "abandonos del contrato ÷ clientes del contrato × 100", "%"),
            ("Participación en los abandonos", "abandonos del contrato ÷ total de abandonos × 100", "%"),
        ],
        "respuesta": (
            "El contrato mes a mes concentra el abandono: su tasa es del 42,71 %, frente al 11,27 % del contrato a "
            "un año y el 2,83 % del de dos años. Son el 55,02 % de los clientes, pero aportan el 88,55 % de los "
            "abandonos y el 86,86 % del ingreso perdido."
        ),
        "decision": "Priorizar ofertas para migrar a los clientes mes a mes hacia contratos de uno o dos años.",
        "limitacion": (
            "Es una asociación, no una causa: los clientes más fieles pueden ser justamente los que eligen contratos largos."
        ),
    },
    "P3": {
        "titulo": "Antigüedad",
        "pregunta": "¿Cómo varía el abandono según la antigüedad del cliente?",
        "respuesta_corta": "Los clientes nuevos se van mucho más: 47,44 % en el primer año y solo 6,61 % después de cinco años.",
        "metricas": [
            ("Tasa de abandono por rango de antigüedad", "abandonos del rango ÷ clientes del rango × 100", "%"),
            ("Participación en los abandonos", "abandonos del rango ÷ total de abandonos × 100", "%"),
        ],
        "respuesta": (
            "El abandono baja a medida que aumenta la antigüedad: 47,44 % en el primer año, 28,71 % en el segundo y "
            "6,61 % entre los clientes de 61 a 72 meses. Los clientes del primer año son el 31,04 % del total, pero "
            "aportan el 55,48 % de los abandonos."
        ),
        "decision": "Concentrar acciones de bienvenida y acompañamiento en los primeros 12 meses del cliente.",
        "limitacion": "La antigüedad se mide al momento del corte; no se sigue a un mismo grupo de clientes en el tiempo.",
    },
    "P4": {
        "titulo": "Cargos",
        "pregunta": "¿Se diferencian en sus cargos los clientes que abandonan?",
        "respuesta_corta": "Sí: los que se van pagan más cada mes (74,44 en promedio, frente a 61,27 de los que se quedan).",
        "metricas": [
            ("Tasa de abandono por cuartil de cargo mensual", "abandonos del cuartil ÷ clientes del cuartil × 100", "%"),
            ("Cargo mensual promedio y mediana", "promedio y mediana de cargo_mensual por grupo", "unidades monetarias / mes"),
            ("Participación en el ingreso perdido", "ingreso perdido del cuartil ÷ ingreso perdido total × 100", "%"),
        ],
        "respuesta": (
            "Sí. Quienes abandonaron pagan más cada mes: promedio de 74,44 (mediana 79,65), frente a 61,27 (mediana "
            "64,43) de quienes permanecen. La tasa sube del 11,24 % en el cuartil bajo al 37,51 % en el medio-alto y "
            "al 32,88 % en el alto; esos dos cuartiles suman el 79,34 % del ingreso perdido. Su cargo total acumulado "
            "es menor porque llevan menos tiempo como clientes (mediana de 10 meses frente a 38)."
        ),
        "decision": "Revisar la propuesta de valor de los planes de cargo medio-alto y alto, donde se pierde más ingreso.",
        "limitacion": (
            "Mide facturación, no rentabilidad: sin costos no se puede decir qué clientes son más rentables. "
            "La moneda no está documentada."
        ),
    },
    "P5": {
        "titulo": "Método de pago e internet",
        "pregunta": "¿Hay diferencias según el método de pago y el servicio de internet?",
        "respuesta_corta": "Se van más los que pagan con cheque electrónico (45,29 %) y los que tienen fibra óptica (41,89 %).",
        "metricas": [
            ("Tasa de abandono por método de pago", "abandonos del método ÷ clientes del método × 100", "%"),
            ("Tasa de abandono por servicio de internet", "abandonos del servicio ÷ clientes del servicio × 100", "%"),
        ],
        "respuesta": (
            "El cheque electrónico tiene la tasa más alta (45,29 %) y aporta el 57,30 % de los abandonos; los pagos "
            "automáticos están muy por debajo (transferencia 16,71 %, tarjeta 15,24 %). En internet, la fibra óptica "
            "alcanza el 41,89 %, frente al 18,96 % de DSL y el 7,40 % sin internet, y aporta el 82,15 % del ingreso "
            "perdido."
        ),
        "decision": "Promover el pago automático y revisar la experiencia de los clientes de fibra óptica.",
        "limitacion": "El dataset no registra por qué abandonan (precio, calidad, competencia); requeriría encuestas o reclamos.",
    },
    "P6": {
        "titulo": "Segmentos prioritarios",
        "pregunta": "¿Qué segmentos (contrato × internet) concentran el abandono?",
        "respuesta_corta": "El grupo más crítico es «Mes a mes | Fibra óptica»: se fue más de la mitad (54,61 %) y concentra el 62,17 % de los abandonos.",
        "metricas": [
            ("Tasa de abandono por segmento", "abandonos del segmento ÷ clientes del segmento × 100", "%"),
            ("Participación en abandonos e ingreso perdido", "valor del segmento ÷ total × 100", "%"),
        ],
        "respuesta": (
            "El segmento «Mes a mes | Fibra óptica» encabeza el ranking: tasa del 54,61 %, el 30,21 % de los clientes, "
            "el 62,17 % de los abandonos y el 72,22 % del ingreso perdido. Le sigue «Mes a mes | DSL» (32,22 %). Los "
            "segmentos con contrato de dos años están por debajo del 8 %."
        ),
        "decision": "Lanzar una campaña piloto en «Mes a mes | Fibra óptica», que reúne casi dos tercios de los abandonos.",
        "limitacion": "Los segmentos pequeños (por ejemplo, «Dos años | Sin internet», 5 abandonos) tienen tasas poco estables.",
    },
}

CONCLUSIONES = [
    "El 26,54 % de los clientes abandonó el servicio y se llevó el 30,50 % del ingreso mensual.",
    "El abandono se concentra en clientes con contrato mes a mes (42,71 %), en su primer año (47,44 %), con fibra "
    "óptica (41,89 %), pago por cheque electrónico (45,29 %) y cargos mensuales medio-altos o altos.",
    "Un solo segmento, «Mes a mes | Fibra óptica», reúne el 62,17 % de los abandonos y el 72,22 % del ingreso perdido.",
]

RECOMENDACIONES = [
    "Campaña piloto de migración a contrato anual en el segmento «Mes a mes | Fibra óptica».",
    "Programa de acompañamiento durante los primeros 12 meses del cliente.",
    "Incentivos para pasar del cheque electrónico al pago automático.",
    "Revisar precio y calidad percibida de la fibra óptica con encuestas a clientes que cancelan.",
    "Repetir la medición mensualmente con la tasa de 26,54 % como línea base.",
]

LIMITACIONES = [
    "Los datos son de una compañía ficticia (IBM Sample Datasets): los resultados describen este dataset, no una empresa real.",
    "El análisis es descriptivo: muestra asociaciones, no causas.",
    "No hay fechas: no se pueden estudiar tendencias ni estacionalidad.",
    "No hay costos: el ingreso perdido mide facturación, no rentabilidad; la moneda no está documentada.",
    "Los segmentos pequeños tienen tasas poco estables.",
]
