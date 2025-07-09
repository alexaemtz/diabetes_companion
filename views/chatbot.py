import streamlit as st
import google.generativeai as genai
import pandas as pd
import numpy as np

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

my_api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=my_api_key)

model = genai.GenerativeModel("gemini-2.0-flash")

# ------------- Load and prepare the knowledge database -------------
@st.cache_resource
def load_knowledge_database():
    database = pd.read_csv("database.csv")
    embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    database['embedding'] = database['text'].apply(lambda x: embedding_model.encode(x))
    return database, embedding_model

knowledge_database, embeding_model = load_knowledge_database()

# --------------- Search for context in the database ---------------
def search_database(query, database, modelo, top_k=3):
    query_embedding = modelo.encode(query)
    similarities = cosine_similarity([query_embedding], list(database['embedding']))[0]
    top_indices = np.argsort(similarities)[-top_k:][::-1]
    return database.iloc[top_indices]
    
# --------------- User Interface ---------------------------    
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
        
    # Buscar contexto en la base de datos
    context_database = search_database(prompt, knowledge_database, embeding_model, top_k=3)
    context_text = "\n".join(f"- {row}" for row in context_database['text'])
        
    # Prompt enriquecido con RAG
    modified_promp = f"""
    Eres un asistente experto en diabetes. Usa el siguiente contexto médico validado para responder con mayor precisión.
    Procura otorgar respuestas cortas y precisas, sin ambigüedades ni redundancias. Máximo 200 palabras.
    
    Contexto:
    {context_text}
    
    Pregunta del usuario:
    {prompt}
    
    Considera que soy un paciente diabético y actualmente me siento {mood}, 
    ¿qué consejos me puedes dar para manejar mi diabetes y promover mi bienestar general? 
    Enfócate en estrategias prácticas para promover mi bienestar general, incluyendo recomendaciones ajustadas a mi estado emocional actual. 
    """

    # Iniciar el chat con el historial actual
    chat = model.start_chat(history=[{"role": m["role"], "parts": [m["content"]]} for m in st.session_state["messages"][:-1]])

    # Enviar el nuevo mensaje del usuario
    response = chat.send_message(modified_promp)
    response_text = response.text
    
    # Mostrar respuesta al usuario
    st.session_state["messages"].append({"role": "assistant", "content": response_text})
    with st.chat_message("assistant", avatar="🤖"):
        st.markdown(response_text, unsafe_allow_html=True)
