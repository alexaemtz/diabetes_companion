import streamlit as st
from PIL import Image
import google.generativeai as genai
import re
import pandas as pd

# --- API KEY ---
my_api_key = st.secrets["GEMINI_API_KEY"]

if not my_api_key:
    st.error("Por favor, configura la clave API de Google en las variables de entorno.")
else:
    genai.configure(api_key=my_api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")

    def input_image_details(image_upload):
        if image_upload is not None:
            bytes_data = image_upload.getvalue()
            image_parts = [{"mime_type": image_upload.type, "data": bytes_data}]
            return image_parts
        else:
            raise FileNotFoundError("No ha seleccionado una imagen.")

    def get_gemini_response(user_input, image, prompt):
        try:
            response = model.generate_content([user_input, image[0], prompt])
            return response
        except Exception as e:
            return f"Error al obtener la respuesta de Gemini: {e}"
        
    with open("css/style.css" ) as css:
        st.markdown( f'<style>{css.read()}</style>' , unsafe_allow_html= True)

    st.title("🍵 Contador de carbohidratos")
    st.write(
        """¡Bienvenido su contador de carbohidratos! Este proyecto le será de utilidad para calcular el número de carbohidratos contenidos en una comida. 
        Utilice el botón 'Browse files' para seleccionar una imagen. No es necesario que ingrese una descripción de lo deseado, el sistema lo hará por usted.
        El sistema utilizará inteligencia artificial para determinar el contenido nutrimental de la misma."""
    )

    user_input = st.text_input(
        "Ingrese una descripción de lo deseado:",
        placeholder="Ejemplo: Dime las calorías contenidas en este plato de ensalada.",
        key="user_input",
    )
    image_upload = st.file_uploader("Suba una imagen", type=["png", "jpg", "jpeg"])
    image = ""
    if image_upload is not None:
        image = Image.open(image_upload)
        st.image(image, caption="Imagen cargada", use_container_width=True)
    submit = st.button("Escanear la comida")

    input_prompt = input_prompt = """
You are a competent nutritionist/dietitian. Your current task is to identify types of foods in the provided image.
The system must be able to detect and accurately label the various types of foods shown in the image, stating their names.
Additionally, you must extract nutritional information and categorize each food (for example: fruits, vegetables, cereals, legumes, meats, etc.) according to the foods detected in the image.
You should also provide an approximate quantity in grams for each identified food item.
Also include nutritional information such as the amount of calories, carbohydrates, sugars, proteins, fats (broken down into saturated and unsaturated), fiber, vitamins, minerals, sodium, cholesterol, etc.
Also indicate whether the food is suitable for diabetics, and whether it is rich in nutrients or not.

**Provide the result in Spanish**, in a table with the following structure:

| Tipo de Alimento | Cantidad (g) | Calorías | Colesterol | Carbohidratos | Azúcares | Proteínas | Grasas Saturadas | Grasas Insaturadas | Fibra | Vitaminas | Minerales | Sodio | Apto para diabéticos | Rico en nutrientes |
|------------------|--------------|----------|------------|----------------|----------|-----------|------------------|---------------------|--------|-----------|-----------|--------|----------------------|--------------------|
| Alimento 1       | 100          | 100      | 30         | 80             | 50       | 20        | 30               | 90                  | 40     | 50        | 60        | 70     | Sí                   | No                 |
| Alimento 2       | 200          | 200      | 10         | 100            | 80       | 40        | 60               | 28                  | 80     | 100       | 120       | 140    | No                   | Sí                 |
"""

    if submit:
        with st.spinner("Escaneando la comida..."):
            try:
                image_data = input_image_details(image_upload)
                response = get_gemini_response(input_prompt, image_data, user_input)

                # Extraer la tabla de la respuesta
                text_response = response.text
                table_match = re.search(r"\| Tipo de Alimento.*\|", text_response, re.DOTALL)

                if table_match:
                    table_text = table_match.group(0)
                    lines = table_text.strip().split("\n")
                    headers = [h.strip() for h in lines[0].strip("|").split("|")]
                    data = []
                    for line in lines[2:]:
                        row = [r.strip() for r in line.strip("|").split("|")]
                        data.append(dict(zip(headers, row)))

                    st.subheader("Información Nutricional:")
                    st.dataframe(data, use_container_width=True)
                else:
                    st.subheader("Resultados obtenidos: ")
                    st.write(response.text)

            except Exception as e:
                st.error(f"Ocurrió un error: {e}")