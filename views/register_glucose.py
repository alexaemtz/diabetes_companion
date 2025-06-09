import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import pytz
import firebase_utils
from firebase_utils import init_firebase
from firebase_admin import firestore
import plotly.express as px
import numpy as np # Para calcular el coeficiente de variación

# Importar para generar PDF (se abordará más adelante)
# from reportlab.lib.pagesizes import letter
# from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
# from reportlab.lib.styles import getSampleStyleSheet
# from reportlab.lib import colors
# import io

with open("css/style.css") as css:
    st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)

firebase = init_firebase()
db = firebase["db"]
auth = firebase["auth"]

st.title(":blue[App Azul - ¡Bienvenido!]")
st.header("¡Bienvenido a su App Azul!", divider="rainbow")
st.write("Esta aplicación le será de ayuda para el monitoreo y control de su diabetes.")

st.subheader("Registro")
st.write("Cree el registro de glucosa.")

with st.container():
    zona_local = pytz.timezone("America/Mexico_City")
    hora_local = datetime.now(zona_local)

    fecha = st.date_input("Fecha:", hora_local)
    hora = st.time_input("Hora:", hora_local)
    
    # MODIFICACIÓN: Usar selectbox para tiempo_medicion para una mejor categorización
    opciones_tiempo_medicion = [
        "En ayunas",
        "Antes del desayuno",
        "Después del desayuno",
        "Antes del almuerzo",
        "Después del almuerzo",
        "Antes de la cena",
        "Después de la cena",
        "Antes de dormir",
        "Otro"
    ]
    tiempo_medicion_seleccionado = st.selectbox("Tiempo de la medición:", opciones_tiempo_medicion)

    tiempo_medicion_texto_libre = ""
    if tiempo_medicion_seleccionado == "Otro":
        tiempo_medicion_texto_libre = st.text_input("Especifique el tiempo de la medición:",
                                                    placeholder="Ejemplo: 30 minutos antes de hacer ejercicio.")
        tiempo_medicion_a_guardar = tiempo_medicion_texto_libre
    else:
        tiempo_medicion_a_guardar = tiempo_medicion_seleccionado

    glucosa = st.number_input("Glucosa marcada (mg/dL):",
                                     placeholder="Ejemplo: 100", min_value=1) # Añadido min_value

save_button = st.button("Guardar")

if save_button:
    if 'user' in st.session_state and 'uid' in st.session_state['user']:
        user_uid = st.session_state['user']['uid']
        try:
            doc_ref = db.collection("lecturas_glucosa").document()
            doc_ref.set({
                "uid_usuario": user_uid,
                "fecha": fecha.strftime("%Y-%m-%d"),
                "hora": hora.strftime("%H:%M:%S"),
                "tiempo_medicion": tiempo_medicion_a_guardar, # Usar el valor correcto
                "glucosa": glucosa,
            })
            st.success("¡Medición guardada exitosamente!")
        except Exception as e:
            st.error(f"Ocurrió un error: {e}")
    else:
        st.info("No se ha detectado ningún usuario. Por favor, inicie sesión.")

st.subheader("Historial de glucosa")
mediciones_df = None

# Función de análisis (mejorada)
def analizar_glucosa_profundo(df_glucosa, tipo_reporte):
    """
    Realiza un análisis más profundo de los valores de glucosa para un médico.
    """
    if df_glucosa.empty:
        return "No hay datos de glucosa para analizar en este período."

    analisis_markdown = f"### Análisis de Glucosa - Reporte {tipo_reporte}\n\n"
    analisis_markdown += "---"
    analisis_markdown += f"\n\n**Período del reporte:** Del {df_glucosa['fecha'].min()} al {df_glucosa['fecha'].max()}\n"
    analisis_markdown += f"**Número de registros:** {len(df_glucosa)} mediciones.\n\n"

    # 1. Métricas básicas
    promedio_glucosa = df_glucosa["glucosa"].mean()
    mediana_glucosa = df_glucosa["glucosa"].median()
    max_glucosa = df_glucosa["glucosa"].max()
    min_glucosa = df_glucosa["glucosa"].min()
    
    analisis_markdown += f"#### Resumen de Glucosa\n"
    analisis_markdown += f"- **Promedio General:** **{promedio_glucosa:.2f} mg/dL**\n"
    analisis_markdown += f"- **Mediana General:** **{mediana_glucosa:.2f} mg/dL**\n"
    analisis_markdown += f"- **Glucosa Más Alta:** **{max_glucosa} mg/dL**\n"
    analisis_markdown += f"- **Glucosa Más Baja:** **{min_glucosa} mg/dL**\n\n"

    # 2. Variabilidad Glucémica (Coeficiente de Variación)
    std_dev_glucosa = df_glucosa["glucosa"].std()
    # Evitar división por cero si el promedio es 0 (aunque con glucosa no debería pasar)
    cv_glucosa = (std_dev_glucosa / promedio_glucosa) * 100 if promedio_glucosa != 0 else 0
    
    analisis_markdown += f"#### Variabilidad Glucémica\n"
    analisis_markdown += f"- **Desviación Estándar:** {std_dev_glucosa:.2f} mg/dL\n"
    analisis_markdown += f"- **Coeficiente de Variación (CV):** **{cv_glucosa:.2f}%**\n"
    
    if cv_glucosa < 36:
        analisis_markdown += "  *(Indicador de baja variabilidad, generalmente deseable)*\n"
    elif 36 <= cv_glucosa <= 60:
        analisis_markdown += "  *(Indicador de variabilidad moderada, puede requerir atención)*\n"
    else:
        analisis_markdown += "  *(Indicador de alta variabilidad, se recomienda revisión médica para buscar patrones)*\n"
    analisis_markdown += "\n"

    # 3. Frecuencia de hipo/hiperglucemias
    # Rangos objetivo personalizables si se implementa una interfaz para el médico
    rango_hipoglucemia = 70
    rango_hiperglucemia = 180 # Considerado alto para muchos pacientes
    rango_optimo_min = 80
    rango_optimo_max = 140 # Un rango más estricto para "óptimo"

    lecturas_hipo = df_glucosa[df_glucosa["glucosa"] < rango_hipoglucemia]
    lecturas_hiper = df_glucosa[df_glucosa["glucosa"] > rango_hiperglucemia]
    lecturas_en_rango_optimo = df_glucosa[(df_glucosa["glucosa"] >= rango_optimo_min) & (df_glucosa["glucosa"] <= rango_optimo_max)]

    analisis_markdown += f"#### Cumplimiento de Rangos Objetivo\n"
    analisis_markdown += f"- **Lecturas en Hipoglucemia (< {rango_hipoglucemia} mg/dL):** **{len(lecturas_hipo)}** veces ({len(lecturas_hipo)/len(df_glucosa)*100:.2f}%)\n"
    if not lecturas_hipo.empty:
        analisis_markdown += f"  - Valores: {', '.join(map(str, lecturas_hipo['glucosa'].tolist()))}\n"
    
    analisis_markdown += f"- **Lecturas en Hiperglucemia (> {rango_hiperglucemia} mg/dL):** **{len(lecturas_hiper)}** veces ({len(lecturas_hiper)/len(df_glucosa)*100:.2f}%)\n"
    if not lecturas_hiper.empty:
        analisis_markdown += f"  - Valores: {', '.join(map(str, lecturas_hiper['glucosa'].tolist()))}\n"

    analisis_markdown += f"- **Lecturas en Rango Óptimo ({rango_optimo_min}-{rango_optimo_max} mg/dL):** **{len(lecturas_en_rango_optimo)}** veces ({len(lecturas_en_rango_optimo)/len(df_glucosa)*100:.2f}%)\n\n"

    # 4. Promedio por período del día y patrones
    analisis_markdown += f"#### Análisis por Período del Día y Patrones\n"
    
    # Categorizar las mediciones
    def categorizar_tiempo_medicion(tiempo_str):
        tiempo_str_lower = tiempo_str.lower()
        if "ayunas" in tiempo_str_lower:
            return "En ayunas"
        elif "desayuno" in tiempo_str_lower and "antes" in tiempo_str_lower:
            return "Antes del desayuno"
        elif "desayuno" in tiempo_str_lower and "después" in tiempo_str_lower:
            return "Después del desayuno"
        elif "almuerzo" in tiempo_str_lower and "antes" in tiempo_str_lower:
            return "Antes del almuerzo"
        elif "almuerzo" in tiempo_str_lower and "después" in tiempo_str_lower:
            return "Después del almuerzo"
        elif "cena" in tiempo_str_lower and "antes" in tiempo_str_lower:
            return "Antes de la cena"
        elif "cena" in tiempo_str_lower and "después" in tiempo_str_lower:
            return "Después de la cena"
        elif "dormir" in tiempo_str_lower:
            return "Antes de dormir"
        else:
            return "Otros momentos"
    
    df_glucosa['periodo_dia'] = df_glucosa['tiempo_medicion'].apply(categorizar_tiempo_medicion)
    
    promedio_por_periodo = df_glucosa.groupby('periodo_dia')['glucosa'].mean().reset_index()
    promedio_por_periodo.columns = ['Período del Día', 'Glucosa Promedio (mg/dL)']
    
    if not promedio_por_periodo.empty:
        analisis_markdown += "##### Glucosa Promedio por Período:\n"
        analisis_markdown += promedio_por_periodo.to_markdown(index=False) # Tabla Markdown
        analisis_markdown += "\n\n"

    # Identificación de patrones (simplificada)
    analisis_markdown += "##### Observaciones de Patrones:\n"
    
    # Patrón de picos post-desayuno
    desayuno_df = df_glucosa[df_glucosa['periodo_dia'] == 'Después del desayuno']
    if not desayuno_df.empty and desayuno_df['glucosa'].mean() > 180: # Umbral para pico post-desayuno
        analisis_markdown += "- **Picos Post-desayuno:** El promedio de glucosa después del desayuno es **{:.2f} mg/dL**, lo que sugiere picos consistentes. Se recomienda revisar la composición del desayuno o la medicación pre-desayuno.\n".format(desayuno_df['glucosa'].mean())
    
    # Patrón de ayunas elevadas
    ayunas_df = df_glucosa[df_glucosa['periodo_dia'] == 'En ayunas']
    if not ayunas_df.empty and ayunas_df['glucosa'].mean() > 130: # Umbral para ayunas elevadas
        analisis_markdown += "- **Glucosa en Ayunas Elevada:** El promedio de glucosa en ayunas es **{:.2f} mg/dL**. Esto podría indicar un efecto del amanecer o una dosis insuficiente de medicación basal.\n".format(ayunas_df['glucosa'].mean())
    
    if (desayuno_df.empty or desayuno_df['glucosa'].mean() <= 180) and \
       (ayunas_df.empty or ayunas_df['glucosa'].mean() <= 130):
        analisis_markdown += "- No se observan patrones claros de picos post-desayuno o glucosa en ayunas elevada en este período."
    analisis_markdown += "\n\n"

    analisis_markdown += "---"
    analisis_markdown += "\n**Nota Importante para el Profesional de la Salud:** Este análisis es una herramienta de apoyo y no sustituye la evaluación clínica completa del paciente. Utilice esta información en conjunto con su juicio profesional y otros datos del paciente para tomar decisiones sobre el tratamiento."
    
    return analisis_markdown

if 'user' in st.session_state and 'uid' in st.session_state['user']:
    user_uid = st.session_state['user']['uid']
    try:
        lecturas_ref = db.collection("lecturas_glucosa") \
                             .where("uid_usuario", "==", user_uid) \
                             .order_by("fecha", direction=firestore.Query.DESCENDING) \
                             .order_by("hora", direction=firestore.Query.DESCENDING)
        lecturas = lecturas_ref.get()

        data = [doc.to_dict() for doc in lecturas]

        if data:
            mediciones_df = pd.DataFrame(data)
            mediciones_df['datetime'] = pd.to_datetime(mediciones_df["fecha"] + " " + mediciones_df["hora"])
            mediciones_df = mediciones_df.sort_values(by="datetime", ascending=False)
            mediciones_df = mediciones_df[["fecha", "hora", "glucosa", "tiempo_medicion", "datetime"]]
            
            st.dataframe(mediciones_df.drop(columns=["datetime"]))

            fig = px.line(mediciones_df, x="datetime", y="glucosa",
                          title="Gráfica del historial de glucosa", markers=True, text="glucosa")
            fig.update_traces(line=dict(color='#e377c2', width=3), marker=dict(size=8), textposition="top center")
            fig.update_layout(xaxis_title="Fecha y hora", yaxis_title="Glucosa (mg/dL)",
                              xaxis=dict(showgrid=True), yaxis=dict(showgrid=True), hovermode="x unified")
            st.plotly_chart(fig)

            # Sección del reporte
            st.subheader("📊 Generar reporte de glucosa")
            tipo_reporte = st.selectbox("Seleccione el tipo de reporte:", ["Diario", "Semanal", "Mensual"])
            generar = st.button("Generar reporte")

            if generar:
                hoy = datetime.now().date()

                if tipo_reporte == "Diario":
                    fecha_inicio = hoy
                elif tipo_reporte == "Semanal":
                    fecha_inicio = hoy - timedelta(days=7) # Usar timedelta para fechas
                elif tipo_reporte == "Mensual":
                    fecha_inicio = hoy - timedelta(days=30) # Usar timedelta para fechas

                reporte_df = mediciones_df[mediciones_df["datetime"].dt.date >= fecha_inicio]

                if not reporte_df.empty:
                    st.success(f"Mostrando reporte {tipo_reporte.lower()} con {len(reporte_df)} registros.")
                    st.dataframe(reporte_df.drop(columns=["datetime"]))

                    fig_reporte = px.line(reporte_df, x="datetime", y="glucosa",
                                          title=f"Gráfica del reporte {tipo_reporte.lower()}",
                                          markers=True, text="glucosa")
                    fig_reporte.update_traces(line=dict(color='#1f77b4', width=3),
                                              marker=dict(size=8), textposition="top center")
                    fig_reporte.update_layout(xaxis_title="Fecha y hora",
                                              yaxis_title="Glucosa (mg/dL)",
                                              hovermode="x unified")
                    st.plotly_chart(fig_reporte)

                    # **Aquí se integra el análisis profundo para el médico**
                    st.subheader("🔍 Análisis Profundo para el Médico")
                    analisis_medico = analizar_glucosa_profundo(reporte_df, tipo_reporte)
                    st.markdown(analisis_medico)

                    # Botón para generar PDF (desactivado por ahora, se implementará después)
                    # if st.button("Descargar Reporte PDF"):
                    #     pdf_buffer = generar_reporte_pdf(reporte_df, analisis_medico, tipo_reporte)
                    #     st.download_button(
                    #         label="Descargar PDF",
                    #         data=pdf_buffer,
                    #         file_name=f"Reporte_Glucosa_{tipo_reporte}_{hoy}.pdf",
                    #         mime="application/pdf"
                    #     )

                else:
                    st.warning(f"No se encontraron registros en el rango seleccionado para el reporte {tipo_reporte.lower()}.")
        else:
            st.info("No se encontraron registros de glucosa para este usuario.")
    except Exception as e:
        st.error(f"Ocurrió un error al cargar el historial: {e}")
else:
    st.info("Por favor, inicie sesión para ver su historial de glucosa.")
