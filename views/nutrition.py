import streamlit as st
import google.generativeai as genai
from firebase_utils import init_firebase

my_api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=my_api_key)

model = genai.GenerativeModel("gemini-2.0-flash")

firebase = init_firebase()
db = firebase["db"]

st.title("Asistente virtual para nutrición")
st.subheader("Este asistente virtual le ayudará a obtener sugerencias de alimentos y nutrición para su dieta, de acuerdo a sus necesides y preferencias.")

dietary_restrictions = st.multiselect("Restricciones dietéticas", ["Sin gluten", "Sin lácteos", "Vegetariano", "Vegano", "Paleo", "Otras (especificar)"], placeholder="Seleccione una opción")
other_restrictions = st.text_area("Otras restricciones dietéticas (si aplica)")
allergies = st.text_area("¿Tiene alguna alergia o alergias? Si no, deje este campo en blanco.")
type_of_food = st.multiselect("Tipo de comida preferida", ["Italiana", "Mexicana", "Americana", "Asiática", "Mediterránea", "Otras (especificar)"], placeholder="Seleccione una opción")
another_type_of_food = st.text_area("Otro tipo de comida preferida (si aplica)")
food_to_include = st.text_area("¿Qué tipo de alimentos le gustaría que incluyera este asistente virtual?", placeholder="""Puede incluir alimentos específicos, como frutas o verduras,
                                o especificar una categoría de alimentos, como salsa, ensalada, etc. Si no tiene ninguna preferencia, deje este campo en blanco.""")
portion_size = st.text_area("¿Tiene alguna preferencia de tamaño de porción? Si no, deje este campo en blanco.")
glucose_reading = st.number_input("¿Cuál fue su última lectura de glucosa (en mg/dL)? Este dato puede ayudar a personalizar mejor su sugerencia.", value=100)
activity_level = st.selectbox("¿Cuál es su nivel de actividad física?", ["Sedentario", "Ligero", "Moderado", "Intenso"])
food_at_day = st.number_input("¿Cuántas comidas diarias le gustaría que le diera este asistente virtual?", value=1)
glucose_objective = st.text_input("Opcional: ¿Hasta que valor le gustaría controlar su glucosa?", placeholder="Ejemplo: 80 mg/dL")

sugerencias = st.button("Generar sugerencias")

if sugerencias:
    prompt = f"""Eres un asistente virtual para nutrición. Genera un plan de comidas personalizado para el paciente con diabetes. Considera la siguiente información:
    Restricciones dietéticas: {', '.join(dietary_restrictions) + (f', {other_restrictions}' if other_restrictions else '')}
    Alergias: {allergies if allergies else 'Ninguna'}
    Tipo de comida: {', '.join(type_of_food) + (f', {another_type_of_food}' if another_type_of_food else '')}
    Alimentos a incluir: {food_to_include if food_to_include else 'No proporcionado'}    
    Historial reciente de glucosa: {glucose_reading if glucose_reading else 'No proporcionado'}
    Nivel de actividad física: {activity_level}
    Número de comidas al día: {food_at_day}
    Objetivos de rango de glucosa: {glucose_objective if glucose_objective else 'No especificado'}
    
    El plan de comidas debe ser saludable, equilibrado y adaptado a las restricciones dietéticas, preferencias alimentarias, alimentos a incluir, 
    tamaños de porción de los alimentos,nivel de actividad física, historial de glucosa y objetivos de rango de glucosa.
    El plan debe incluir una variedad de alimentos. Debe ser adecuado para controlar los niveles de glucosa en un paciente diabético.
    Incluye ideas de recetas específicas y considera las porciones adecuadas. Trata de solo dar las recetas. No des explicaciones complejas. 
    Limita la respuesta a menos de 30 líneas de texto. El plan de comidas debe cubrir una semana, sin repetir sugerencias.
    
    Procura ofrecer sugerencias económicas y fáciles de conseguir. Los precios deben estar en MXN y no incluir descuentos. 
    
    Formato de salida sugerido:
    **Día [Número]:**
    
    * **Desayuno:** [Nombre del plato] - [Descripción breve] - [Precio aproximado]
    * **Media Mañana:** [Nombre del snack] - [Descripción breve] - [Precio aproximado]
    * **Almuerzo:** [Nombre del plato] - [Descripción breve] - [Precio aproximado]
    * **Media Tarde:** [Nombre del snack] - [Descripción breve] - [Precio aproximado]
    * **Cena:** [Nombre del plato] - [Descripción breve] - [Precio aproximado]
    """
    
    try:
        response = model.generate_content(prompt)
        st.subheader("Plan de comidas sugerido:")
        st.markdown(response.text)
        # st.subheader("Recomendaciones Nutricionales Adicionales:")
        # prompt_recomendaciones = f"""
        # Considerando las restricciones y preferencias del paciente diabético con la siguiente información:
        # Restricciones dietéticas: {', '.join(dietary_restrictions) + (f', {other_restrictions}' if other_restrictions else '')}
        # Preferencias alimentarias: {', '.join(type_of_food) + (f', {another_type_of_food}' if another_type_of_food else '')}
        # Limita la respuesta menos 10 líneas de texto.
        # """
        # response_recomendaciones = model.generate_content(prompt_recomendaciones)
        # st.markdown(response_recomendaciones.text)
    except Exception as e:
        st.error(f"Ocurrió un error al generar la sugerencia: {e}")