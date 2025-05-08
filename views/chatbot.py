import streamlit as st
import google.generativeai as genai

my_api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=my_api_key)

model = genai.GenerativeModel("gemini-2.0-flash")

st.title("🧘 Chatbot para tu Bienestar y Diabetes")
st.subheader("Cuida tu salud física y emocional. ¡Pregunta sobre el manejo de la diabetes y recibe consejos para sentirte mejor!")
st.write("""Este chatbot utiliza inteligencia artificial para ofrecerte información y sugerencias para el manejo de la diabetes, con un enfoque en tu bienestar general.
            Recuerda que esta herramienta no reemplaza la consulta con profesionales de la salud.""")

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Hola, soy tu asistente virtual para temas relacionados con la diabetes. ¿En qué puedo ayudarte hoy?"}]

for message in st.session_state["messages"]:
    with st.chat_message(message["role"], avatar="🤖"):
        st.markdown(message["content"], unsafe_allow_html=True)
        
mood = st.selectbox("¿Cómo te sientes el día de hoy?", ["Neutro", "Animado", "Preocupado", "Desmotivado", "Feliz", "Triste", "Frustado", "Molesto", "Aburrido", "Enfadado"],
                    index=0, 
                    key="mood_selector")

prompt = st.chat_input("Escriba su pregunta o solicitud aquí...")

if prompt:
    st.session_state["messages"].append({"role": "user", "content": f"{prompt} Mi estado de ánimo actual es {mood}"})
    with st.chat_message("user", avatar="😃"):
        st.markdown(prompt, unsafe_allow_html=True)
        
    # Prompt
    modified_promp = f"""{prompt}. Considerando que soy un paciente diabético y actualmente me siento {mood}, 
    ¿qué consejos me puedes dar para manejar mi diabetes y promover mi bienestar general? 
    Por favor, enfócate en estrategias prácticas y considera mi estado emocional actual."""

    # Iniciar el chat con el historial actual
    chat = model.start_chat(history=[{"role": m["role"], "parts": [m["content"]]} for m in st.session_state["messages"][:-1]])

    # Enviar el nuevo mensaje del usuario
    response = chat.send_message(modified_promp)
    response_text = response.text

    st.session_state["messages"].append({"role": "assistant", "content": response_text})
    with st.chat_message("assistant", avatar="🤖"):
        st.markdown(response_text, unsafe_allow_html=True)