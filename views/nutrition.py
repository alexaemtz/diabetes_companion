import streamlit as st
import google.generativeai as genai
from firebase_utils import init_firebase
import re

# Configuración de la API de Gemini
my_api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=my_api_key)
model = genai.GenerativeModel("gemini-2.0-flash")

# Inicializar Firebase
firebase = init_firebase()
db = firebase["db"]

# Interfaz de usuario
st.title("Asistente virtual para nutrición")
st.subheader("Este asistente virtual le ayudará a obtener sugerencias de alimentos y nutrición para su dieta, de acuerdo a sus necesidades y preferencias.")

# Entradas del usuario
dietary_restrictions = st.multiselect("Restricciones dietéticas", ["Sin gluten", "Sin lácteos", "Vegetariano", "Vegano", "Paleo", "Otras (especificar)"], placeholder="Seleccione una opción")
other_restrictions = st.text_area("Otras restricciones dietéticas (si aplica)")
allergies = st.text_area("¿Tiene alguna alergia o alergias? Si no, deje este campo en blanco.")
type_of_food = st.multiselect("Tipo de comida preferida", ["Italiana", "Mexicana", "Americana", "Asiática", "Mediterránea", "Otras (especificar)"], placeholder="Seleccione una opción")
another_type_of_food = st.text_area("Otro tipo de comida preferida (si aplica)")
food_to_include = st.text_area("¿Qué tipo de alimentos le gustaría que incluyera este asistente virtual? Puede incluir alimentos específicos o categorías de alimentos. Si no, deje este campo en blanco.")
portion_size = st.text_area("¿Tiene alguna preferencia de tamaño de porción? Si no, deje este campo en blanco.")
glucose_reading = st.number_input("¿Cuál fue su última lectura de glucosa (en mg/dL)? Este dato puede ayudar a personalizar mejor su sugerencia.", value=100)
activity_level = st.selectbox("¿Cuál es su nivel de actividad física?", ["Sedentario", "Ligero", "Moderado", "Intenso"])
food_at_day = st.number_input("¿Cuántas comidas diarias le gustaría que le diera este asistente virtual?", value=1)
glucose_objective = st.text_input("Opcional: ¿Hasta qué valor le gustaría controlar su glucosa?", placeholder="Ejemplo: 80 mg/dL")

sugerencias = st.button("Generar sugerencias")

if sugerencias:
    prompt = f"""Eres un asistente virtual para nutrición. Genera un plan de comidas personalizado para el paciente con diabetes. Considera la siguiente información:
    Restricciones dietéticas: {', '.join(dietary_restrictions) + (f', {other_restrictions}' if other_restrictions else '')}
    Alergias: {allergies if allergies else 'Ninguna'}
    Tipo de comida: {', '.join(type_of_food) + (f', {another_type_of_food}' if another_type_of_food else '')}
    Alimentos a incluir: {food_to_include if food_to_include else 'No proporcionado'}
    Porciones de alimentos: {portion_size if portion_size else 'No proporcionado'}
    Historial reciente de glucosa: {glucose_reading if glucose_reading else 'No proporcionado'}
    Nivel de actividad física: {activity_level}
    Número de comidas al día: {food_at_day}
    Objetivos de rango de glucosa: {glucose_objective if glucose_objective else 'No especificado'}
    
    El plan de comidas debe ser saludable, equilibrado y adaptado a las restricciones dietéticas, preferencias alimentarias, alimentos a incluir, 
    tamaños de porción de los alimentos, nivel de actividad física, historial de glucosa y objetivos de rango de glucosa.
    El plan debe incluir una variedad de alimentos. Debe ser adecuado para controlar los niveles de glucosa en un paciente diabético.
    Incluye ideas de recetas específicas y considera las porciones adecuadas. Trata de solo dar las recetas. No des explicaciones complejas. 
    Limita la respuesta a menos de 40 líneas de texto. El plan de comidas debe cubrir una semana, sin repetir sugerencias.
    
    Procura ofrecer sugerencias económicas y fáciles de conseguir. Los precios deben estar en MXN y no incluir descuentos. 
    No olvides dar la receta de preparación de cada plato en la columna sugerida.
    
    Formato de salida sugerido:
    Día [ Número ]
    
    | Comida        | Nombre del plato               | Receta de preparación                                    | Precio  |
    |---------------|--------------------------------|----------------------------------------------------------|---------|
    | Desayuno      | Huevo revuelto con espinacas   | Bate los huevos con sal, sofríe espinacas y mezcla todo. | $25     |
    | Media mañana  | Fresas con nueces              | Lava las fresas, corta y mezcla con yogurt y nueces.     | $30     |
    | Almuerzo      | Sopa de lentejas               | Cocina lentejas con verduras y condimentos.              | $35     |
    | Media tarde   | Palito de zanahoria            | Pela y corta zanahorias, acompaña con hummus casero.     | $20     |
    | Cena          | Pechuga de pollo a la plancha  | Sazona y cocina la pechuga en sartén caliente.           | $40     |
    """

    try:
        response = model.generate_content(prompt)
        text_response = response.text

        # Regex flexible para separar los días (Día 1, Día: 2, Día [3], etc.)
        day_split_regex = r"(Día\s*[\[:#-]?\s*\d+\s*[\]]?)"
        parts = re.split(day_split_regex, text_response)

        day_titles = []
        days = []

        for i in range(1, len(parts), 2):
            day_titles.append(parts[i].strip())
            days.append(parts[i + 1].strip())

        if not day_titles or not days:
            st.warning("No se encontraron días con formato esperado.")
        else:
            st.subheader("Planes diarios de comida sugeridos:")
            for i, (title, day_content) in enumerate(zip(day_titles, days), 1):
                st.markdown(f"### {title}")

                # Buscar la tabla dentro del contenido del día
                table_match = re.search(r"\|.*\|.*\|.*\|.*\|\n(\|.*\|\n)+", day_content)
                if table_match:
                    table_text = table_match.group(0)
                    lines = table_text.strip().split("\n")
                    headers = [h.strip() for h in lines[0].strip("|").split("|")]
                    data = []
                    for line in lines[2:]:  # Saltar encabezado y línea de separación
                        row = [r.strip() for r in line.strip("|").split("|")]
                        if len(row) == len(headers):
                            data.append(dict(zip(headers, row)))
                    st.dataframe(data, use_container_width=True)
                else:
                    st.info("No se encontró una tabla estructurada en este día.")
    except Exception as e:
        st.error(f"Ocurrió un error al generar la sugerencia: {e}")