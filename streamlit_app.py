import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth
from login import login, logout
from register import register

with open("css/style.css" ) as css:
    st.markdown( f'<style>{css.read()}</style>' , unsafe_allow_html= True)
    
# ---- STATE INITIALIZATION ----
if 'user' not in st.session_state:
    st.session_state['user'] = None
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'show_register_form' not in st.session_state:
    st.session_state['show_register_form'] = False

# ---- AUTHENTICATION ----
if not st.session_state['logged_in']:
    if st.session_state['show_register_form']:
        st.subheader("Registro de nuevo usuario.")
        register()
        if st.button("Volver al inicio de sesión", key="back_to_login"):
            st.session_state['show_register_form'] = False
            st.rerun()
    else:
        st.subheader("Usuario no autenticado. Por favor, inicie sesión o cree una cuenta.")
        login_sucessful = login()
        
else:
    # --- PAGE SETUP ---
    main_page = st.Page("views/main.py",
                        title="Inicio",
                        icon="🏠",)

    register_glucose_page = st.Page("views/register_glucose.py", 
                            title="Registro", 
                            icon="📑",)

    counter_page = st.Page("views/detection.py", 
                        title="Cálculo de carbohidratos", 
                        icon="📷",)

    nutrition_page = st.Page("views/nutrition.py", 
                            title="Nutrición", 
                            icon="🥗",)

    wellness_page = st.Page("views/chatbot.py", 
                            title="Wellness", 
                            icon="🤖",)

    # --- NAVIGATION SETUP [WITH SECTIONS] ----
    pg = st.navigation({
        "Inicio" : [main_page],
        "Registro de glucosa" : [register_glucose_page],
        "Monitoreo" : [counter_page],
        "Plan de alimentación" : [nutrition_page],
        "Wellness" : [wellness_page],
    })
    
    pg.run()
    
st.sidebar.text("Made with ❤️")