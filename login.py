import streamlit as st
from firebase_admin import auth
from firebase_utils import init_firebase

firebase = init_firebase()
db = firebase["db"]

def login():
    st.write("Si no tiene una cuenta, por favor, regístrese.")
    email = st.text_input("Correo electrónico", key="login_email")
    password = st.text_input("Contraseña", type="password", placeholder="••••••••", key="login_password")
    login_button = st.button("Iniciar sesión", key="login_button")
    register_button = st.button("Registrarse", key="register_button_login")
    login_error_message = st.sidebar.empty()

    if register_button:
        st.session_state['show_register_form'] = True
        st.rerun()

    if login_button:
        try:
            user = auth.get_user_by_email(email)
            #user_role = get_user_role(user.uid)
            st.session_state['user'] = {"uid": user.uid, "email": user.email}
            st.session_state['logged_in'] = True
            st.success(f"¡Bienvenido, {email}!")       
            st.rerun()
            return True
        except auth.UserNotFoundError:
            login_error_message.error("Usuario no encontrado. ¿Desea registrarse?")
        except Exception as e:
            login_error_message.error(f"❌Error al iniciar sesión: {e}")
    return False

def logout():
    if st.sidebar.button("Cerrar sesión", key="logout_button"):
        if 'user' in st.session_state:
            del st.session_state['user']
        if 'logged_in' in st.session_state:
            st.session_state['logged_in'] = False
        if 'role' in st.session_state:
            del st.session_state['role']
        st.session_state['show_register_form'] = False
        st.rerun()
        
"""def get_user_role(uid):
    try:
        user_doc = db.collection("users").document(uid).get()
        if user_doc.exists:
            data = user_doc.to_dict()
            role = data.get("role", None)
            return role
        else:
            return None
    except Exception as e:
        st.error(f"Error al obtener el rol del usuario: {e}")
        return None

def get_user_uid(uid):
    try:
        user_doc = db.collection("pacientes").document(uid).get()
        if user_doc.exists:
            data = user_doc.to_dict()
            return data.get("uid", None)
        else:
            return None
    except Exception as e:
        st.error(f"Error al obtener el UID del paciente: {e}")
        return None"""
