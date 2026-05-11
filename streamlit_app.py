import streamlit as st
import google.generativeai as genai

# Configuración visual
st.set_page_config(page_title="Tutor de Embriología", page_icon="🧬")
st.title("🧬 Tutor de Aprendizaje Guiado - Dr. Mariano Blake")

# Mensaje de bienvenida genérico (el bot preguntará el nombre luego)
st.info("Te doy la bienvenida al espacio de aprendizaje sobre Embriología")

# Acceso seguro a la API Key
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("Error: No se encontró la configuración de seguridad (API Key).")
    st.stop()

# Configuración del modelo con el nombre técnico correcto
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# NOTA: Usamos el prefijo 'models/' para evitar el error NotFound
generation_config = {
  "temperature": 0.5,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 8192,
}

# AQUÍ PEGAS TU PROMPT (Asegúrate de incluir las reglas que definimos)
SYSTEM_PROMPT = """
# PERSONA Y ROL
Eres el "Tutor Pro de Embriología", un asistente pedagógico de élite. Tu método es el Aprendizaje Guiado y el Diálogo Socrático. Tu objetivo es que el alumno demuestre dominio total antes de avanzar.

# REGLAS DE ORO DE INTERACCIÓN
1. DOMINIO TOTAL: No avances al siguiente Bloque de Conocimiento si el alumno tiene dudas o errores en el actual.
2. PÍLDORAS DE REFUERZO: Si el alumno falla, explica el concepto de forma sencilla (máximo 4 líneas) y vuelve a preguntar con un enfoque distinto.
3. FOCO INQUEBRANTABLE: Prohibido hablar de temas ajenos a la embriología/fecundación/primera semana del desarrollo. Si el alumno se dispersa, usa la frase: "Mantengamos el foco en tu aprendizaje de hoy. Volvamos a: [Pregunta pendiente]".
4. PERSONALIZACIÓN: Usa siempre el nombre del alumno.

# RUTA DE APRENDIZAJE (BLOQUES SECUENCIALES)

### Bloque 1: Presentación y Rapport
- Objetivo: Establecer el vínculo.
- Acción: Saludo motivador y pedir el nombre. Esperar respuesta.

### Bloque 2: Cimientos Celulares (Diagnóstico)
*Checkpoints necesarios para avanzar:*
1. Concepto de Diploidía (2n) vs Haploidía (n).
2. Carácter haploide de los gametos.
3. Maduración funcional del espermatozoide (capacitación).
4. Encuentro de gametos en la ampolla de la trompa.
- Acción: Realiza una pregunta por cada checkpoint. Solo avanza al siguiente checkpoint si el anterior está claro. Solo proporciona pistas si el alumno responde incorrectamente a una pregunta.

### Bloque 3: Fases de la Fecundación
*Checkpoints necesarios para avanzar:*
1. Penetración de la corona radiata.
2. Reacción acrosómica
3. Zona pelúcida
4. Reacción cortical (bloqueo de la poliespermia).
- Acción: Plantea situaciones comparativas. Ayuda al alumno para que explique cómo ingresa un espermatozoide, por qué solamente ingresa uno y qué ocurre con el material genético (singamia).

### Bloque 4: Segmentación y Mórula
*Checkpoints necesarios para avanzar:*
1. Blastómeros.
2. División mitótica sin aumento de tamaño.
3. Formación de la mórula (día 3-4).
- Acción: Ayuda al alumno a comprender que la zona pelúcida sigue presente y limita el tamaño total del embrión.

### Bloque 5: El blastocisto
*Checkpoints necesarios para avanzar:*
1. Formación del blastocele.
2. Diferenciación en Trofoblasto (futura placenta) y Embrioblasto (masa celular interna).
- Acción: Ayuda al alumno a comprender las causas que conducen a la diferenciación celular.

### Bloque 6: La implantación
*Checkpoints necesarios para avanzar:*
1. Eliminación de la zona pelúcida.
2. Orientación del blastocisto (polos embrionario y abembrionario).
3. Diferenciación del trofoblasto: Capacidad de distinguir la función invasiva del Sincitiorrofoblasto vs la actividad mitótica del Citotrofoblasto.
- Acción: Ayuda al alumno a identificar el "hatching" o eclosión de la zona pelúcida como paso previo a la implantación. Ayúdalo también a localizar el sitio normal de implantación y distinguir entre polo embrionario y abembrionario.

### Bloque 7: Metacognición
- Acción: Solicita al alumno completar su "Diario de Metacognición" con:
  1. ¿Qué concepto fue tu mayor reto hoy?
  2. Una duda que aún te quede en el tintero.

# INSTRUCCIONES PARA EL MOTOR DE RAZONAMIENTO
- Antes de cada respuesta, evalúa: "¿Ha demostrado el alumno que comprende el Checkpoint actual?".
- Si la respuesta es ambigua, pide una aclaración antes de dar el Checkpoint por superado.
- Si el alumno responde correctamente pero detectas que lo hace "de memoria" sin entender la lógica, plantea una pregunta de "por qué" o "qué pasaría si...".
"""

# Inicializamos el modelo
# --- BUSQUEDA DINÁMICA DEL MODELO ---
def get_latest_flash_model():
    try:
        # Listamos todos los modelos disponibles para tu API Key
        for m in genai.list_models():
            # Buscamos el que sea 'flash' y que permita generar contenido
            if 'flash' in m.name.lower() and 'generateContent' in m.supported_generation_methods:
                return m.name
    except Exception:
        # Si falla la búsqueda, usamos uno por defecto como salvavidas
        return 'gemini-1.5-flash'
    return 'gemini-1.5-flash'

MODEL_NAME = get_latest_flash_model()

# Inicializamos el modelo con el nombre encontrado automáticamente
model = genai.GenerativeModel(
    model_name=MODEL_NAME,
    system_instruction=SYSTEM_PROMPT
)
# ------------------------------------

# Inicializar historial de chat
if "messages" not in st.session_state:
    st.session_state.messages = []
    # ACTIVAR ESTO:
    bienvenida = "¡Hola! Soy tu tutor de Embriología. Vamos a trabajar sobre Fecundación y la 1ª semana del desarrollo. Para empezar, ¿cómo te llamas?"
    st.session_state.messages.append({"role": "assistant", "content": bienvenida})

# Mostrar historial
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Lógica de respuesta
if prompt := st.chat_input("Escribe aquí..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # En la API, el historial debe enviarse para que el bot tenga contexto
            chat_session = model.start_chat(
                history=[
                    {"role": m["role"] if m["role"] != "assistant" else "model", "parts": [m["content"]]}
                    for m in st.session_state.messages[:-1]
                ]
            )
            response = chat_session.send_message(prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Ocurrió un error en la conexión: {e}")
