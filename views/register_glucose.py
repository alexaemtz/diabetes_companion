import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import firebase_utils
from firebase_utils import init_firebase
from firebase_admin import firestore
import plotly.express as px

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
    tiempo_medicion = st.text_input("Tiempo de la medición:",
                                    placeholder="Ejemplo: 10 minutos antes de la comida.")
    glucosa = st.number_input("Glucosa marcada (mg/dL):",
                                placeholder="Ejemplo: 100")

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
                "tiempo_medicion": tiempo_medicion,
                "glucosa": glucosa,
            })
            st.success("¡Medición guardada exitosamente!")
        except Exception as e:
            st.error(f"Ocurrió un error: {e}")
    else:
        st.info("No se ha detectado ningún usuario. Por favor, inicie sesión.")

st.subheader("Historial de glucosa")
mediciones_df = None

if 'user' in st.session_state and 'uid' in st.session_state['user']:
    user_uid = st.session_state['user']['uid']
    try:
        lecturas_ref = db.collection("lecturas_glucosa").where("uid_usuario", "==", user_uid).order_by("fecha", direction=firestore.Query.DESCENDING).order_by("hora", direction=firestore.Query.DESCENDING)
        lecturas = lecturas_ref.get()

        data = []
        for lectura in lecturas:
            data.append(lectura.to_dict())

        if data:
            mediciones_df = pd.DataFrame(data)
            mediciones_df = mediciones_df.drop(columns=["uid_usuario"])
            mediciones_df['datetime'] = pd.to_datetime(mediciones_df["fecha"] + " " + mediciones_df["hora"])
            st.dataframe(mediciones_df)
            fig = px.line(mediciones_df, x="datetime", y="glucosa", title="Gráfica del historial de glucosa", markers=True, text="glucosa")
            fig.update_traces(line=dict(color='#e377c2', width=3), marker=dict(size=8), textposition="top center")
            fig.update_layout(xaxis_title="Fecha y hora", yaxis_title="Glucosa (mg/dL)", xaxis=dict(showgrid=True), yaxis=dict(showgrid=True), hovermode="x unified")
            st.plotly_chart(fig)
        else:
            st.info("No se encontraron registros de glucosa para este usuario.")

    except Exception as e:
        st.error(f"Ocurrió un error al cargar el historial: {e}")
else:
    st.info("Por favor, inicie sesión para ver su historial de glucosa.")