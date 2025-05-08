import streamlit as st

with open("css/style.css" ) as css:
    st.markdown( f'<style>{css.read()}</style>' , unsafe_allow_html= True)

st.title(":blue[App Azul - ¡Bienvenido!]")
st.header("¡Bienvenido a su App Azul!", divider="rainbow")
st.write("Esta aplicación le será de ayuda para el monitoreo y control de su diabetes.")
st.write("Para comenzar, seleccione una opción de la barra de navegación, por favor.")
