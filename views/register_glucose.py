import streamlit as st
from datetime import datetime
import pytz
import firebase_utils
from firebase_utils import init_firebase

with open("css/style.css" ) as css:
    st.markdown( f'<style>{css.read()}</style>' , unsafe_allow_html= True)

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

  fecha =st.date_input("Fecha:",hora_local)
  hora = st.time_input("Hora:",hora_local)
  tiempo_medicion = st.text_input("Tiempo de la medición:",
                                  placeholder="Ejemplo: 10 minutos antes de la comida.")
  glucosa = st.number_input("Glucosa marcada (mg/dL):", 
                            placeholder="Ejemplo: 100")
  
guardar =st.button("Guardar")
if guardar:
  try:
    doc_ref = db.collection("lecturas_glucosa").document()
    doc_ref.set({
      "fecha": fecha.strftime("%Y-%m-%d"),
      "hora": hora.strftime("%H:%M:%S"),
      "tiempo_medicion" : tiempo_medicion,
      "glucosa" : glucosa,
    })
    st.success("¡Gracias por registrar su glucosa!")
  except Exception as e:
    st.error(f"Ocurrió un error: {e}")