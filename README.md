# 🩺 Planificador Integral para Personas con Diabetes Tipo 2

**Versión:** 1.0  
**Desarrollador:** Alexa Shettel Escalante Martínez / @alexaemtz
**Tecnologías:** Python · Streamlit · Gemini API · Pandas · Firebase · Plotly

---

## 📋 Descripción

Esta aplicación web está diseñada para brindar **apoyo diario y personalizado** a personas con **diabetes tipo 2**, combinando herramientas de seguimiento de salud, nutrición, educación y bienestar emocional. Utiliza **inteligencia artificial (Gemini)** para proporcionar recomendaciones prácticas, análisis de datos de glucosa y planes de comida personalizados.

> ⚕️ *Más que un planificador de comidas, es un acompañante digital para el autocuidado de la diabetes.*

---

## 🚀 Funcionalidades Principales

### 🔐 Autenticación de Usuarios
- Registro e inicio de sesión seguros
- Base de datos de usuarios con almacenamiento personalizado

### 📈 Registro y Análisis de Glucosa
- Ingreso manual de valores de glucosa
- Análisis estadístico automático:
  - **Media y mediana**
  - Clasificación de valores: **hipoglucemia, normoglucemia e hiperglucemia**
  - Evaluación por periodos: **diaria**, **semanal** y **mensual**
- Consejos prácticos para mantener los valores en un rango saludable

### 🍽️ Planificador de Comidas Personalizado
- Generación de menús semanales adaptados a:
  - Preferencias personales
  - Necesidades nutricionales para diabetes tipo 2
- Exportación del plan alimenticio en **PDF con formato profesional**

### 🧠 Chatbot Inteligente
- Interacción conversacional con un chatbot que:
  - Responde preguntas sobre diabetes, nutrición y estilo de vida
  - **Adapta sus respuestas según tu estado de ánimo**
  - Usa **Gemini API** para empatía y conocimiento actualizado

### 🧾 Información Nutricional con Visión por Computadora
- Subida de imágenes de alimentos
- Reconocimiento de alimentos mediante **API de Gemini**
- Despliegue automático de su contenido nutricional estimado

🔑 No olvides configurar tus claves de API para Gemini y Firebase en un archivo .env.

---

## 🛠️ Tecnologías Utilizadas

| Herramienta          | Descripción                                |
|----------------------|--------------------------------------------|
| **Python**           | Lenguaje principal del backend             |
| **Streamlit**        | Framework para construir la interfaz web   |
| **Firebase**         | Autenticación de usuarios y base de datos  |
| **Gemini API**       | IA para generación de texto e imágenes     |
| **Pandas**           | Generación de documentos con los planes    |
| **Plotly**           | Visualización de gráficos históricos       |

---

## 📦 Instalación Local (Desarrolladores)

```bash
git clone https://github.com/tuusuario/diabetes-app.git
cd diabetes-app
pip install -r requirements.txt
streamlit run app.py
```
---

diabetes-app/  
├── streamlit_app.py              # Punto de entrada principal de la app  
├── requirements.txt              # Dependencias del proyecto  
├── login.py                      # Lógica de inicio de sesión  
├── register.py                   # Lógica de registro de usuario  
├── firebase_utils.py             # Funciones auxiliares para Firebase  
├── .gitignore                    # Archivos y carpetas ignoradas por Git  
│  
├── views/                        # Módulos funcionales de la interfaz  
│   ├── chatbot.py                # Chatbot con IA según estado de ánimo  
│   ├── detection.py             # Análisis de glucosa (media, mediana, etc.)  
│   ├── main.py                   # Vista principal tras el login  
│   ├── nutrition.py              # Reconocimiento de alimentos con Gemini  
│   └── register_glucose.py       # Registro manual de valores de glucosa  
│  
├── css/  
│   └── style.css                 # Estilos personalizados para la interfaz  
│  
└── .streamlit/                   # Configuración de Streamlit  
    ├── config.toml               # Configuración de tema y layout  
    └── secrets.toml              # Credenciales privadas (ignorado por Git)  

---

## 📍 Estado Actual y Futuras Funciones
Estado actual:
- 🟢 Funcionalidades principales completas y funcionales
- 🟡 Validación inicial con usuarios cercanos (familiares y amistades)

---

## ❤️ Contribuciones
¿Te gustaría contribuir? Toda ayuda es bienvenida. Puedes abrir un pull request o contactar a alemrtnz@proton.me.

---

## ⚠️ Descargo de Responsabilidad
Esta aplicación es una herramienta complementaria para el manejo de la diabetes tipo 2 y no reemplaza el asesoramiento médico profesional. Consulta siempre con tu equipo de salud antes de realizar cambios importantes en tu dieta o tratamiento.

---

## 📄 Licencia
MIT License. Consulta el archivo LICENSE para más información.
