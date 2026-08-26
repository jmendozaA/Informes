import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la página
st.set_page_config(page_title="Reporte de Sedes", layout="wide")

# --- INICIO ENCABEZADO CON IMÁGENES ---
# Ajustamos las columnas a [1.5, 4, 1.5] para dar más espacio a los laterales
col_img1, col_tit, col_img2 = st.columns([1.5, 4, 1.5])

with col_img1:
    st.image("logo1.png", width=550) 

with col_tit:
    # Usamos HTML para centrar el texto y controlar el tamaño exacto de la fuente
    st.markdown(
        "<h2 style='text-align: center; font-size: 32px; margin-top: 20px;'>Reporte del proceso de Admisión Docente 2026</h2>", 
        unsafe_allow_html=True
    )

with col_img2:
    st.image("logo2.png", width=550)

# (Opcional) También podemos justificar el texto descriptivo para que se vea más ordenado
st.markdown(
    "<p style='text-align: justify; font-size: 16px;'>El presente reporte muestra los datos del proceso de admisión de cuanto a las clases participativas desarrolladas y monitoreadas en la gestión 2026-2 (Actualizado al 21 de Agosto del 2026).</p>", 
    unsafe_allow_html=True
)
# --- FIN ENCABEZADO CON IMÁGENES ---

# --- NUEVO: DEFINICIÓN DE PALETA DE COLORES INSTITUCIONALES ---
COLOR_GUINDO = '#860942'
COLOR_PLOMO_OSCURO = '#807f7f'
COLOR_PLOMO_CLARO = '#d8d2d4'

# Paleta discreta para gráficos con varias categorías (Pastel, Sede, Rendimiento)
colores_institucionales = [COLOR_GUINDO, COLOR_PLOMO_OSCURO, COLOR_PLOMO_CLARO, '#5C062D', '#A1A0A0', '#B0135B']

# Escala continua para mapas de calor o gráficos ordenados (Carreras)
escala_continua = [COLOR_PLOMO_CLARO, COLOR_PLOMO_OSCURO, COLOR_GUINDO]
# ---------------------------------------------------------------

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

# 3. Definimos un estilo CSS común para las tarjetas (COLORES ACTUALIZADOS)
tarjeta_css = f"""
    <style>
    div[data-testid="stMarkdownContainer"] .tarjeta-kpi {{
        background-color: #f8f9fa; 
        border: 1px solid {COLOR_PLOMO_CLARO}; 
        border-radius: 10px;       
        padding: 20px;             
        text-align: center;        
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05); 
    }}
    .kpi-titulo {{
        color: {COLOR_PLOMO_OSCURO}; /* Título en plomo oscuro */
        font-size: 12px;
        margin-bottom: 10px;
    }}
    .kpi-valor {{
        color: {COLOR_GUINDO}; /* Valor en Guindo */
        font-size: 32px;
        font-weight: bold;
    }}
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
            <div class="kpi-titulo">Puntaje promedio de Clases Participativas</div>
            <div class="kpi-valor">{promedio_clases_participativas} pts</div>
        </div>
    """, unsafe_allow_html=True)

with kpi3:
    st.markdown(f"""
        <div class="tarjeta-kpi">
            <div class="kpi-titulo">Puntaje promedio Final</div>
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

# Calcular porcentajes y etiquetas
total_general = sede_counts['Cantidad'].sum()
sede_counts['Porcentaje'] = (sede_counts['Cantidad'] / total_general) * 100
sede_counts['Etiqueta'] = sede_counts.apply(lambda x: f"{x['Cantidad']} ({x['Porcentaje']:.1f}%)", axis=1)

# Crear el gráfico
fig_total_sede = px.bar(
    sede_counts, 
    x='Sede', 
    y='Cantidad', 
    color='Sede', 
    text='Etiqueta', 
    color_discrete_sequence=colores_institucionales # Paleta institucional aplicada
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

# 3. Asignación de los valores de la sede usando HTML
with kpi_sede1:
    st.markdown(f"""
        <div class="tarjeta-kpi">
            <div class="kpi-titulo">Total Clases Participativas</div>
            <div class="kpi-valor">{total_clases_sede}</div>
        </div>
    """, unsafe_allow_html=True)

with kpi_sede2:
    st.markdown(f"""
        <div class="tarjeta-kpi">
            <div class="kpi-titulo">Puntaje promedio de Clases Participativas</div>
            <div class="kpi-valor">{promedio_clases_participativas_sede} pts</div>
        </div>
    """, unsafe_allow_html=True)

with kpi_sede3:
    st.markdown(f"""
        <div class="tarjeta-kpi">
            <div class="kpi-titulo">Puntaje promedio Final</div>
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
    mes_counts = df_sede_mes.groupby(['Num_Mes', 'Mes_Texto']).size().reset_index(name='Cantidad')
    mes_counts = mes_counts.sort_values('Num_Mes') 
    
    # 4. Dibujar el gráfico de barras verticales
    fig_fechas = px.bar(
        mes_counts, 
        x='Mes_Texto', 
        y='Cantidad',
        text_auto=True, 
        color_discrete_sequence=[COLOR_GUINDO] # Aplicando el color principal
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
        mes_mayor = mes_counts.loc[mes_counts['Cantidad'].idxmax()]['Mes_Texto'] if not mes_counts.empty else "N/A"
        texto_interpretacion = f"En la sede **{sede_seleccionada}**, el gráfico de barras evidencia la carga mensual de evaluaciones. El mes de **{mes_mayor}** registra la mayor cantidad acumulada de clases participativas del periodo analizado."
        
        if 'Agosto' in mes_counts['Mes_Texto'].values:
            clases_agosto = mes_counts.loc[mes_counts['Mes_Texto'] == 'Agosto', 'Cantidad'].values[0]
            df_agosto = df_sede_mes[df_sede_mes['Mes_Texto'] == 'Agosto']
            carreras_agosto_counts = df_agosto['Carrera_T'].value_counts()
            lista_carreras = [f"{carrera} ({cantidad})" for carrera, cantidad in carreras_agosto_counts.items()]
            texto_carreras = ", ".join(lista_carreras)
            texto_interpretacion += f" También se resalta que en el mes de Agosto se tienen **{clases_agosto}** clases, lo que significa que todavía se han desarrollado evaluaciones una vez que han comenzado las clases de la gestión 2026-2. Las carreras que solicitaron estas clases fueron: **{texto_carreras}**."
        
        st.write(texto_interpretacion)

    # B. Distribución del máximo grado académico (Gráfico de pastel)
    grado_counts = df_sede['Máximo Grado Academico'].value_counts().reset_index()
    grado_counts.columns = ['Grado Académico', 'Cantidad']
    fig_grado = px.pie(
        grado_counts, 
        names='Grado Académico', 
        values='Cantidad', 
        hole=0.4,
        color_discrete_sequence=colores_institucionales # Aplicando paleta institucional
    )

    fig_grado.update_layout(
        title={
            'text': "DISTRIBUCIÓN DE ACUERDO AL GRADO ACADÉMICO",
            'x': 0.5,           
            'xanchor': 'center' 
        }
    )

    st.plotly_chart(fig_grado, use_container_width=True) 

    # 5. Expander de interpretación para Grado Académico
    with st.expander("💡 Ver interpretación de Grado Académico"):
        st.write(f"Detalle de las carreras que cuentan con postulantes de nivel posgrado en la sede **{sede_seleccionada}**:")
        df_posgrado = df_sede[~df_sede['Máximo Grado Academico'].str.contains('Licenciatura', case=False, na=False)]
        if df_posgrado.empty:
            st.write("- *No se registraron postulantes con grado de Maestría, Doctorado o Especialidad en esta sede.*")
        else:
            grados_presentes = df_posgrado['Máximo Grado Academico'].dropna().unique()
            for grado in sorted(grados_presentes):
                datos_grado = df_posgrado[df_posgrado['Máximo Grado Academico'] == grado]
                conteos_carreras = datos_grado['Carrera_T'].value_counts()
                lista_carreras_formateada = [f"{carrera} ({cantidad})" for carrera, cantidad in conteos_carreras.items()]
                lista_carreras_txt = ", ".join(lista_carreras_formateada)
                st.write(f"- **{grado}**: {lista_carreras_txt}")

    # E. Distribución de la puntuación total (Histograma)
    fig_total = px.histogram(
        df_sede, 
        x='Puntuacion Total', 
        nbins=15, 
        title="Distribución de Puntuación Total",
        marginal="box", 
        color_discrete_sequence=[COLOR_PLOMO_OSCURO] # Aplicando color secundario
    )

    fig_total.update_layout(
        title={
            'text': "DISTRIBUCIÓN DE LA PUNTUACIÓN TOTAL",
            'x': 0.5,           
            'xanchor': 'center' 
        }
    )

    st.plotly_chart(fig_total, use_container_width=True)

# 5. Expander de interpretación de Puntuación Total
    with st.expander("💡 Interpretación"):
        st.write(f"La puntuación total promedio en esta sede es de **{promedio_puntaje_total_sede} pts**.")
        
        st.markdown("📌 **Análisis de Reprobados (Menor a 60 pts):**")
        nota_aprobacion = 60
        df_reprobados = df_sede[df_sede['Puntuacion Total'] < nota_aprobacion]
        total_reprobados = len(df_reprobados)
        
        # --- NUEVO: Cálculo del total de evaluados y porcentaje ---
        total_evaluados = len(df_sede['Puntuacion Total'].dropna()) 
        
        if total_reprobados > 0:
            porcentaje_reprobados = (total_reprobados / total_evaluados) * 100 if total_evaluados > 0 else 0
            
            conteo_carreras_reprobados = df_reprobados['Carrera_T'].value_counts()
            lista_rep = [f"{carrera} ({cantidad})" for carrera, cantidad in conteo_carreras_reprobados.items()]
            texto_reprobados = ", ".join(lista_rep)
            
            # --- MODIFICADO: Agregamos el porcentaje al texto de st.warning ---
            st.warning(f"Se identificaron **{total_reprobados}** postulante(s) (**{porcentaje_reprobados:.1f}%** del total) que no alcanzaron la nota mínima de aprobación. Pertenecen a las siguientes carreras: **{texto_reprobados}**.")
        else:
            st.success("✔️ En esta sede, no existen postulantes reprobados bajo la puntuación total (todos obtuvieron 60 pts o más).")
            
        st.markdown("📊 **Concentración Principal de Calificaciones:**")
        if len(df_sede['Puntuacion Total'].dropna()) > 1:
            # --- NUEVO: Calculamos el total de evaluados válidos para el porcentaje ---
            total_evaluados = len(df_sede['Puntuacion Total'].dropna())
            
            rangos = pd.cut(df_sede['Puntuacion Total'], bins=10)
            rango_moda = rangos.mode()[0]
            df_rango_frecuente = df_sede[df_sede['Puntuacion Total'].between(rango_moda.left, rango_moda.right)]
            
            total_en_rango = len(df_rango_frecuente)
            # --- NUEVO: Cálculo del porcentaje del rango modal ---
            porcentaje_rango = (total_en_rango / total_evaluados) * 100
            
            conteo_carreras_rango = df_rango_frecuente['Carrera_T'].value_counts()
            lista_ran = [f"{carrera} ({cantidad})" for carrera, cantidad in conteo_carreras_rango.items()]
            texto_rango = ", ".join(lista_ran)
            
            # --- MODIFICADO: Agregamos el porcentaje al texto de st.info ---
            st.info(f"La mayor concentración de calificaciones agrupa a **{total_en_rango} postulantes** (**{porcentaje_rango:.1f}%** del total), quienes obtuvieron notas que oscilan entre **{rango_moda.left:.1f} y {rango_moda.right:.1f} pts**. Las áreas que lograron ubicarse en esta franja mayoritaria son: **{texto_rango}**.")
        else:
            st.write("No hay datos suficientes para calcular rangos de frecuencia.")


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
        color_continuous_scale=escala_continua # Degradado entre colores institucionales
    )

    fig_carreras.update_layout(
        title={
            'text': "DISTRIBUCIÓN DE EJECUCIÓN POR CARRERA",
            'x': 0.5,           
            'xanchor': 'center' 
        }
    )

    fig_carreras.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_carreras, use_container_width=True)

    # 5. Expander de interpretación para Carreras (Acumulado 80%)
    with st.expander("💡 Interpretación"):
        carrera_counts = carrera_counts.sort_values('Cantidad', ascending=False)
        total_clases_sede = carrera_counts['Cantidad'].sum()
        carrera_counts['Porcentaje'] = (carrera_counts['Cantidad'] / total_clases_sede) * 100
        carrera_counts['Acumulado'] = carrera_counts['Porcentaje'].cumsum()
        
        st.write(f"En la sede **{sede_seleccionada}**, alrededor del 80% del esfuerzo de evaluación se concentró en el siguiente grupo principal de carreras:")
        
        for index, row in carrera_counts.iterrows():
            nombre_carrera = row['Carrera']
            cantidad = row['Cantidad']
            porcentaje = row['Porcentaje']
            acumulado = row['Acumulado']
            
            st.write(f"- **{nombre_carrera}**: {cantidad} clases ({porcentaje:.1f}%)")
            if acumulado >= 80:
                break
    
    # F. Rendimiento promedio según Grado Académico (Gráfico de Barras)
    df_rendimiento = df_sede.groupby('Máximo Grado Academico')['PuntajeProm'].mean().reset_index()
    df_rendimiento.columns = ['Grado Académico', 'Puntaje Promedio']
    df_rendimiento['Puntaje Promedio'] = df_rendimiento['Puntaje Promedio'].round(2)
    df_rendimiento = df_rendimiento.sort_values('Puntaje Promedio', ascending=False)
    
    fig_rendimiento = px.bar(
        df_rendimiento,
        x='Grado Académico',
        y='Puntaje Promedio',
        text='Puntaje Promedio', 
        color='Grado Académico',
        color_discrete_sequence=colores_institucionales # Paleta institucional aplicada
    )

    fig_rendimiento.update_layout(
        title={
            'text': "RENDIMIENTO PROMEDIO<br>POR GRADO ACADÉMICO",
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis_title="Grado Académico",
        yaxis_title="Puntaje Promedio (Clases Part.)",
        showlegend=False 
    )

    st.plotly_chart(fig_rendimiento, use_container_width=True)
    
    # 4. Expander de interpretación de rendimiento
    with st.expander("💡 Ver interpretación de Calidad vs. Título"):
        if not df_rendimiento.empty:
            mejor_grado = df_rendimiento.iloc[0]['Grado Académico']
            mejor_puntaje = df_rendimiento.iloc[0]['Puntaje Promedio']
            
            st.write(f"En la sede **{sede_seleccionada}**, este análisis cruza el perfil profesional con el desempeño real en aula.")
            st.write(f"Los postulantes con nivel de **{mejor_grado}** demostraron el mejor desempeño pedagógico, obteniendo una calificación promedio de **{mejor_puntaje} pts** en sus clases participativas.")
            
            if 'Licenciatura' in df_rendimiento['Grado Académico'].values:
                puntaje_licenciatura = df_rendimiento.loc[df_rendimiento['Grado Académico'] == 'Licenciatura', 'Puntaje Promedio'].values[0]
                
                if mejor_grado != 'Licenciatura':
                    diferencia = round(mejor_puntaje - puntaje_licenciatura, 2)
                    st.success(f"📈 **Dato clave:** El grado de {mejor_grado} supera al de Licenciatura por una diferencia de {diferencia} puntos en promedio, lo que sugiere que el nivel de posgrado aporta un valor pedagógico medible en esta sede.")
                else:
                    st.warning(f"⚠️ **Dato clave:** Los postulantes con Licenciatura obtuvieron el promedio más alto. Esto indica que exigir niveles de posgrado en esta sede no necesariamente ha garantizado una mejor clase participativa.")
        else:
            st.write("No hay datos suficientes para calcular el rendimiento en esta sede.")


    # C. Distribución del puntaje obtenido en PuntajeProm (Histograma)
    fig_prom = px.histogram(
        df_sede, 
        x='PuntajeProm', 
        nbins=15, 
        marginal="box", 
        color_discrete_sequence=[COLOR_GUINDO] # Aplicando el color principal
    )

    fig_prom.update_layout(
        title={
            'text': "DISTRIBUCIÓN DEL PUNTAJE OBTENIDO<br>EN LAS CLASES PARTICIPATIVAS",
            'x': 0.5,           
            'xanchor': 'center' 
        }
    )

    st.plotly_chart(fig_prom, use_container_width=True)

# 5. Expander de interpretación para Clases Participativas (PuntajeProm)
    with st.expander("💡 Interpretación"):
        st.write(f"El puntaje promedio específico de la práctica docente en esta sede es de **{promedio_clases_participativas_sede} pts** (sobre un máximo de 50).")
        
        st.markdown("📊 **Tendencia General del Desempeño:**")
        if len(df_sede['PuntajeProm'].dropna()) > 1:
            # --- NUEVO: Calculamos el total de evaluados válidos para el porcentaje ---
            total_evaluados_prom = len(df_sede['PuntajeProm'].dropna())
            
            rangos_prom = pd.cut(df_sede['PuntajeProm'], bins=10)
            rango_moda_prom = rangos_prom.mode()[0]
            df_rango_prom = df_sede[df_sede['PuntajeProm'].between(rango_moda_prom.left, rango_moda_prom.right)]
            
            total_rango_prom = len(df_rango_prom)
            # --- NUEVO: Cálculo del porcentaje del rango modal ---
            porcentaje_rango_prom = (total_rango_prom / total_evaluados_prom) * 100
            
            conteo_carreras_prom = df_rango_prom['Carrera_T'].value_counts().head(5)
            lista_ran_prom = [f"{carrera} ({cantidad})" for carrera, cantidad in conteo_carreras_prom.items()]
            texto_rango_prom = ", ".join(lista_ran_prom)
            
            # --- MODIFICADO: Agregamos el porcentaje al texto de st.info ---
            st.info(f"El grueso de los postulantes (**{total_rango_prom}** en total, que representa el **{porcentaje_rango_prom:.1f}%**) demostró un nivel pedagógico que se agrupa entre los **{rango_moda_prom.left:.1f} y {rango_moda_prom.right:.1f} pts**. Las carreras más representativas con este nivel promedio son: **{texto_rango_prom}**.")
        
        st.markdown("🌟 **Desempeño Sobresaliente (45 pts o más):**")
        df_excelencia = df_sede[df_sede['PuntajeProm'] >= 45]
        total_excelencia = len(df_excelencia)
        
        if total_excelencia > 0:
            total_evaluados_prom = len(df_sede['PuntajeProm'].dropna())
            porcentaje_exc = (total_excelencia / total_evaluados_prom) * 100 if total_evaluados_prom > 0 else 0
            conteo_excelencia = df_excelencia['Carrera_T'].value_counts()
            lista_exc = [f"{carrera} ({cantidad})" for carrera, cantidad in conteo_excelencia.items()]
            texto_exc = ", ".join(lista_exc)
            
            st.success(f"Se identificaron **{total_excelencia}** clase(s) (**{porcentaje_exc:.1f}%** del total) con calificación de excelencia (45 puntos o más sobre 50). Estos talentos destacados pertenecen a las áreas de: **{texto_exc}**.")
        else:
            st.write("- *En esta sede no se registraron clases participativas con nivel de excelencia (45 pts o más).*")