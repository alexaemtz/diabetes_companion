import streamlit as st
from firebase_admin import auth
from firebase_utils import init_firebase

firebase = init_firebase()
db = firebase["db"]

def register():
    st.write("Si ya posee una cuenta, por favor, inicie sesión. De lo contrario, complete el siguiente formulario.")
    new_email = st.text_input("Correo electrónico", key="register_email")
    new_password = st.text_input("Contraseña", type="password", placeholder="••••••••", key="register_password")
    confirm_password = st.text_input("Confirmar contraseña", type="password", placeholder="••••••••", key="register_confirm_password")
    new_username = st.text_input("Nombre de usuario", key="register_username")
    register_button = st.button("Registrarse", key="register_button")

    if register_button:
        if not new_email or not new_password or not confirm_password or not new_username:
            st.error("❌ Por favor, rellene todos los campos.")
            return
        
        if new_password != confirm_password:
            st.error("Las contraseñas no coinciden.")
            return
        
        if len(new_password) < 8:
            st.error("La contraseña es demasiado corta. Debe contener al menos 8 caracteres.")
            return
        
        upper_case = any(c.isupper() for c in new_password)
        lower_case = any(c.islower() for c in new_password)
        number = any(c.isdigit() for c in new_password)
        special_char = any(c in "!@#$%^&*()_+-=[]{}|;':,./<>?" for c in new_password)
        
        if not (upper_case and lower_case and number and special_char):
            st.error("❌ La contraseña debe contener al menos una letra mayúscula, una letra minúscula, un número y un carácter especial.")
            return
        else:
            st.success("✔️ Contraseña válida.")
            
        try:
            user = auth.create_user(email=new_email, password=new_password)
            user_data = {"email": new_email, "username": new_username, "uid": user.uid}
            st.success("✔️ Su usuario se ha registrado correctamente.")
            db.collection("users").document(new_username).set(user_data)
        except auth.EmailAlreadyExistsError:
            st.error("❗ El correo electrónico ya está registrado.")
        except Exception as e:
            st.error(f"❌ Error al registrar el usuario: {e}")
