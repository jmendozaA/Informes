import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la página
st.set_page_config(page_title="Reporte de Sedes", layout="wide")

st.title("📊 Reporte del proceso de Admisión Docente 2026")
st.markdown("El presente reporte muestra los datos del proceso de admisión de cuanto a las clases participativas desarrolladas y monitoreadas en la gestión 2026-2")

# Función para cargar y preparar los datos
@st.cache_data
def load_data():
    # Leer el archivo Excel
    df = pd.read_excel("Tabla_BD_v01.xlsx")
    
    # Asegurar el formato datetime de la fecha de visita
    if 'FechaVisita' in df.columns:
        df['FechaVisita'] = pd.to_datetime(df['FechaVisita'])
        
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Error al cargar el archivo 'Tabla_BD_v01.xlsx'. Asegúrese de que el archivo esté en la misma carpeta que este script. Detalle: {e}")
    st.stop()

# --- INICIO DE TARJETAS DE MÉTRICAS (KPIs) ---
st.markdown("### Resumen General del Proceso")

# 1. Cálculos matemáticos usando pandas
total_clases = len(df)
promedio_puntaje_total = round(df['Puntuacion Total'].mean(), 2)
promedio_clases_participativas = round(df['PuntajeProm'].mean(), 2)

# 2. Creación de 3 columnas
kpi1, kpi2, kpi3 = st.columns(3)

# 3. Definimos un estilo CSS común para las tarjetas
tarjeta_css = """
    <style>
    div[data-testid="stMarkdownContainer"] .tarjeta-kpi {
        background-color: #f8f9fa; /* Color de fondo claro */
        border: 1px solid #dee2e6; /* Borde sutil */
        border-radius: 10px;       /* Bordes curvos */
        padding: 20px;             /* Espacio interno */
        text-align: center;        /* Texto centrado */
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05); /* Sombra ligera 3D */
    }
    .kpi-titulo {
        color: #6c757d;
        font-size: 16px;
        margin-bottom: 10px;
    }
    .kpi-valor {
        color: #1f77b4; /* Color azul para destacar el número */
        font-size: 32px;
        font-weight: bold;
    }
    </style>
"""

# Inyectamos el CSS en la página
st.markdown(tarjeta_css, unsafe_allow_html=True)

# 4. Asignación de los valores usando HTML (Ahora invertidos)
with kpi1:
    st.markdown(f"""
        <div class="tarjeta-kpi">
            <div class="kpi-titulo">Total Clases Evaluadas</div>
            <div class="kpi-valor">{total_clases}</div>
        </div>
    """, unsafe_allow_html=True)

with kpi2:
    st.markdown(f"""
        <div class="tarjeta-kpi">
            <div class="kpi-titulo">Puntaje Promedio Clases Participativas</div>
            <div class="kpi-valor">{promedio_clases_participativas} pts</div>
        </div>
    """, unsafe_allow_html=True)

with kpi3:
    st.markdown(f"""
        <div class="tarjeta-kpi">
            <div class="kpi-titulo">Puntaje Total Promedio</div>
            <div class="kpi-valor">{promedio_puntaje_total} pts</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br><hr>", unsafe_allow_html=True) # Salto de línea extra y separador
# --- FIN DE TARJETAS DE MÉTRICAS ---


# 1. Distribución total de las transacciones por sede
st.header("1. Distribución Total de Clases participativas por Sede")

# Agrupar los datos
sede_counts = df['Sede'].value_counts().reset_index()
sede_counts.columns = ['Sede', 'Cantidad']

# --- NUEVO: Calcular porcentajes y etiquetas ---
# Calculamos el total general sumando todas las cantidades
total_general = sede_counts['Cantidad'].sum()

# Calculamos el porcentaje matemático
sede_counts['Porcentaje'] = (sede_counts['Cantidad'] / total_general) * 100

# Creamos una columna de texto uniendo la cantidad y el porcentaje formateado a 1 decimal
sede_counts['Etiqueta'] = sede_counts.apply(lambda x: f"{x['Cantidad']} ({x['Porcentaje']:.1f}%)", axis=1)
# -----------------------------------------------

# Crear el gráfico
fig_total_sede = px.bar(
    sede_counts, 
    x='Sede', 
    y='Cantidad', 
    color='Sede', 
    text='Etiqueta', # Usamos nuestra nueva columna en lugar de text_auto=True
    color_discrete_sequence=px.colors.qualitative.Pastel
)

# Forzar a que el texto se adapte bien dentro o fuera de la barra
fig_total_sede.update_traces(textposition='auto', textfont_size=13)

# Mejorar el diseño del layout
fig_total_sede.update_layout(
    title={
        'text': "TOTAL DE CLASES PARTICIPATIVAS POR SEDE",
        'x': 0.5,           
        'xanchor': 'center' 
    },
    yaxis_title="Cantidad de Clases",
    xaxis_title="Sede",
    showlegend=False # Ocultar leyenda (opcional, limpia el gráfico ya que el eje X tiene los nombres)
)

st.plotly_chart(fig_total_sede, use_container_width=True)

# 1.1 Expander de interpretación general
with st.expander("💡 Interpretación"):
    # Extraemos los datos de la sede principal (la primera fila, índice 0)
    sede_mayor_nombre = sede_counts.iloc[0]['Sede']
    sede_mayor_cantidad = sede_counts.iloc[0]['Cantidad']
    sede_mayor_porcentaje = sede_counts.iloc[0]['Porcentaje']
    
    st.info(
        f"Este gráfico muestra el volumen total a nivel nacional. "
        f"La sede con mayor participación en general es **{sede_mayor_nombre}** con "
        f"**{sede_mayor_cantidad}** clases registradas, lo que representa el "
        f"**{sede_mayor_porcentaje:.1f}%** del esfuerzo total de evaluación."
    )

st.markdown("---")

# 2. Menú desplegable para seleccionar la Sede
st.header("2. Análisis Detallado por Sede")
sedes_disponibles = sorted(df['Sede'].dropna().unique().tolist())
sede_seleccionada = st.selectbox("Seleccione una Sede para ver sus gráficos específicos:", sedes_disponibles)

# Filtrar el dataframe por la sede seleccionada
df_sede = df[df['Sede'] == sede_seleccionada]

st.subheader(f"Resultados para la sede: {sede_seleccionada}")

# --- INICIO DE KPIs ESPECÍFICOS POR SEDE ---
# 1. Cálculos matemáticos usando df_sede (datos filtrados)
total_clases_sede = len(df_sede)
promedio_clases_participativas_sede = round(df_sede['PuntajeProm'].mean(), 2)
promedio_puntaje_total_sede = round(df_sede['Puntuacion Total'].mean(), 2)

# 2. Creación de 3 columnas para los KPIs de la sede
kpi_sede1, kpi_sede2, kpi_sede3 = st.columns(3)

# (Nota: No es necesario volver a definir el CSS porque ya está inyectado arriba)

# 3. Asignación de los valores de la sede usando HTML
with kpi_sede1:
    st.markdown(f"""
        <div class="tarjeta-kpi">
            <div class="kpi-titulo">Total Clases (Sede)</div>
            <div class="kpi-valor">{total_clases_sede}</div>
        </div>
    """, unsafe_allow_html=True)

with kpi_sede2:
    st.markdown(f"""
        <div class="tarjeta-kpi">
            <div class="kpi-titulo">Promedio Clases Part. (Sede)</div>
            <div class="kpi-valor">{promedio_clases_participativas_sede} pts</div>
        </div>
    """, unsafe_allow_html=True)

with kpi_sede3:
    st.markdown(f"""
        <div class="tarjeta-kpi">
            <div class="kpi-titulo">Puntaje Total Promedio (Sede)</div>
            <div class="kpi-valor">{promedio_puntaje_total_sede} pts</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True) # Pequeño espacio antes de los gráficos
# --- FIN DE KPIs ESPECÍFICOS POR SEDE ---

# Crear dos columnas para mostrar los gráficos de forma organizada
col1, col2 = st.columns(2)

with col1:

    # A. Distribución de las fechas de visita (Gráfico de Barras por Mes)
    
    df_sede_mes = df_sede.copy()
    
    # 1. Extraer el número del mes (1 a 12)
    df_sede_mes['Num_Mes'] = df_sede_mes['FechaVisita'].dt.month
    
    # 2. Diccionario para traducir el número del mes a texto en español
    meses_espanol = {
        1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
        5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
        9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
    }
    df_sede_mes['Mes_Texto'] = df_sede_mes['Num_Mes'].map(meses_espanol)
    
    # 3. Contar la cantidad de registros por mes
    # Agrupamos también por 'Num_Mes' para poder ordenar cronológicamente
    mes_counts = df_sede_mes.groupby(['Num_Mes', 'Mes_Texto']).size().reset_index(name='Cantidad')
    mes_counts = mes_counts.sort_values('Num_Mes') # Ordenar de Enero a Diciembre
    
    # 4. Dibujar el gráfico de barras verticales
    fig_fechas = px.bar(
        mes_counts, 
        x='Mes_Texto', 
        y='Cantidad',
        text_auto=True, # Muestra el número sobre cada barra
        color_discrete_sequence=['#F6CF71'] # Un color naranja/dorado para diferenciar
    )

    fig_fechas.update_layout(
        title={
            'text': "DISTRIBUCIÓN DE CLASES PARTICIPATIVAS POR MES",
            'x': 0.5,           
            'xanchor': 'center' 
        },
        xaxis_title="Mes",
        yaxis_title="Cantidad de Clases"
    )

    st.plotly_chart(fig_fechas, use_container_width=True)
    
    # 5. Expander de interpretación (Con desglose de carreras para Agosto)
    with st.expander("💡 Interpretación"):
        # 5.1 Encontrar el mes con mayor cantidad
        mes_mayor = mes_counts.loc[mes_counts['Cantidad'].idxmax()]['Mes_Texto'] if not mes_counts.empty else "N/A"
        
        # 5.2 Construir el texto base
        texto_interpretacion = f"En la sede **{sede_seleccionada}**, el gráfico de barras evidencia la carga mensual de evaluaciones. El mes de **{mes_mayor}** registra la mayor cantidad acumulada de clases participativas del periodo analizado."
        
        # 5.3 Lógica condicional para el mes de Agosto
        if 'Agosto' in mes_counts['Mes_Texto'].values:
            # Extraemos la cantidad exacta de clases que hubo en Agosto
            clases_agosto = mes_counts.loc[mes_counts['Mes_Texto'] == 'Agosto', 'Cantidad'].values[0]
            
            # --- NUEVO: Extraer carreras de Agosto ---
            # Filtramos los datos para quedarnos solo con los registros de Agosto
            df_agosto = df_sede_mes[df_sede_mes['Mes_Texto'] == 'Agosto']
            
            # Contamos cuántas clases tuvo cada carrera ese mes
            carreras_agosto_counts = df_agosto['Carrera_T'].value_counts()
            
            # Convertimos esos datos en un texto legible (ej: "Derecho (3), Medicina (1)")
            lista_carreras = [f"{carrera} ({cantidad})" for carrera, cantidad in carreras_agosto_counts.items()]
            texto_carreras = ", ".join(lista_carreras)
            
            # Añadimos el texto extra y el desglose al párrafo principal
            texto_interpretacion += f" También se resalta que en el mes de Agosto se tienen **{clases_agosto}** clases, lo que significa que todavía se han desarrollado evaluaciones una vez que han comenzado las clases de la gestión 2026-2. Las carreras que solicitaron estas clases fueron: **{texto_carreras}**."
        
        # 5.4 Mostrar el texto final en la pantalla
        st.write(texto_interpretacion)

    # B. Distribución del máximo grado académico (Gráfico de pastel)
    grado_counts = df_sede['Máximo Grado Academico'].value_counts().reset_index()
    grado_counts.columns = ['Grado Académico', 'Cantidad']
    fig_grado = px.pie(
        grado_counts, 
        names='Grado Académico', 
        values='Cantidad', 
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Set3
    )

    fig_grado.update_layout(
        title={
            'text': "DISTRIBUCIÓN DE ACUERDO AL GRADO ACADÉMICO",
            'x': 0.5,           # Posición horizontal (50%)
            'xanchor': 'center' # El centro del texto se alinea con la posición x
        }
    )

    # Se elige gráfico de dona (pastel) al ser pocas categorías (proporciones)
    st.plotly_chart(fig_grado, use_container_width=True) 

    # E. Distribución de la puntuación total (Histograma)
    fig_total = px.histogram(
        df_sede, 
        x='Puntuacion Total', 
        nbins=15, 
        title="Distribución de Puntuación Total",
        marginal="box", 
        color_discrete_sequence=['#109618']
    )

    fig_total.update_layout(
        title={
            'text': "DISTRIBUCIÓN DE LA PUNTUACIÓN TOTAL",
            'x': 0.5,           # Posición horizontal (50%)
            'xanchor': 'center' # El centro del texto se alinea con la posición x
        }
    )

    # Al igual que PuntajeProm, el histograma muestra la concentración de calificaciones
    st.plotly_chart(fig_total, use_container_width=True)
    

with col2:
    # D. Distribución de las carreras (Gráfico de barras horizontales)
    carrera_counts = df_sede['Carrera_T'].value_counts().reset_index()
    carrera_counts.columns = ['Carrera', 'Cantidad']
    fig_carreras = px.bar(
        carrera_counts, 
        x='Cantidad', 
        y='Carrera', 
        orientation='h',
        title="Distribución de Carreras", 
        color='Cantidad',
        color_continuous_scale='Blues'
    )

    fig_carreras.update_layout(
        title={
            'text': "DISTRIBUCIÓN DE EJECUCIÓN POR CARRERA",
            'x': 0.5,           # Posición horizontal (50%)
            'xanchor': 'center' # El centro del texto se alinea con la posición x
        }
    )

    fig_carreras.update_layout(yaxis={'categoryorder':'total ascending'})
    # Gráfico de barras horizontales es el mejor para nombres largos de categorías (carreras)
    st.plotly_chart(fig_carreras, use_container_width=True)

    # 5. Expander de interpretación para Carreras (Acumulado 80%)
    with st.expander("💡 Interpretación"):
        # Asegurarnos de que los datos estén ordenados de mayor a menor
        carrera_counts = carrera_counts.sort_values('Cantidad', ascending=False)
        
        # Calcular el total de la sede y los porcentajes individuales
        total_clases_sede = carrera_counts['Cantidad'].sum()
        carrera_counts['Porcentaje'] = (carrera_counts['Cantidad'] / total_clases_sede) * 100
        
        # Calcular el porcentaje acumulado progresivo
        carrera_counts['Acumulado'] = carrera_counts['Porcentaje'].cumsum()
        
        # Redactamos el párrafo inicial
        st.write(f"En la sede **{sede_seleccionada}**, alrededor del 80% del esfuerzo de evaluación se concentró en el siguiente grupo principal de carreras:")
        
        # Recorremos la tabla para imprimir la lista
        for index, row in carrera_counts.iterrows():
            nombre_carrera = row['Carrera']
            cantidad = row['Cantidad']
            porcentaje = row['Porcentaje']
            acumulado = row['Acumulado']
            
            # Imprimir la carrera como viñeta
            st.write(f"- **{nombre_carrera}**: {cantidad} clases ({porcentaje:.1f}%)")
            
            # Detener el bucle en cuanto crucemos la barrera del 80%
            if acumulado >= 80:
                break
    
    # C. Distribución del puntaje obtenido en PuntajeProm (Histograma)
    fig_prom = px.histogram(
        df_sede, 
        x='PuntajeProm', 
        nbins=15, 
        marginal="box", # Añade un boxplot en la parte superior para ver atípicos
        color_discrete_sequence=['#3366CC']
    )

    fig_prom.update_layout(
        title={
            'text': "DISTRIBUCIÓN DEL PUNTAJE OBTENIDO EN LAS CLASES PARTICIPATIVAS",
            'x': 0.5,           # Posición horizontal (50%)
            'xanchor': 'center' # El centro del texto se alinea con la posición x
        }
    )

    # Se elige gráfico de dona (pastel) al ser pocas categorías (proporciones)
    st.plotly_chart(fig_prom, use_container_width=True)
