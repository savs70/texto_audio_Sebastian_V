import io
import streamlit as st
from gtts import gTTS

# ============================
# CONFIGURACIÓN DE LA INTERFAZ
# ============================
st.set_page_config(
    page_title="Convertidor de texto a MP3 de Sebastián V.",
    page_icon="🎧",
    layout="centered",
)

st.title("🎧 Convertidor de texto a MP3 de Sebastián V.")
st.write("Convierte texto en audio MP3 con soporte para **narraciones** o **conversaciones con varios acentos**.")


# ============================
# IDIOMAS DISPONIBLES (NARRACIÓN)
# ============================
IDIOMAS = {
    "Español (es)": "es",
    "Inglés (en)": "en",
    "Mandarín (zh-CN)": "zh-cn",
    "Coreano (ko)": "ko",
    "Francés (fr)": "fr",
    "Portugués (pt)": "pt",
    "Alemán (de)": "de",
    "Italiano (it)": "it",
}

# ============================
# IDIOMAS / ACENTOS PARA CONVERSACIÓN
# ============================
IDIOMAS_CONVERSACION = {
    "Español - España": "es",
    "Español - México": "es-mx",
    "Español - Colombia": "es-co",
    # Google usa 'es-us' como variante rioplatense (suena argentino)
    "Español - Argentina": "es-us",
    "Español - Perú": "es-pe",
    "Español - Venezuela": "es-ve",
    "Inglés - USA": "en",
    "Inglés - UK": "en-uk",
    "Inglés - Australia": "en-au",
    "Coreano": "ko",
    "Mandarín (China)": "zh-cn",
    "Francés": "fr",
    "Italiano": "it",
    "Portugués (Brasil)": "pt-br",
}


# ============================
# FUNCIÓN gTTS (GENÉRICA)
# ============================
def generar_audio_gtts(texto: str, lang: str) -> bytes:
    """Genera audio MP3 usando gTTS y lo devuelve en bytes."""
    tts = gTTS(text=texto, lang=lang)
    buf = io.BytesIO()
    tts.write_to_fp(buf)
    buf.seek(0)
    return buf.read()


# ============================
# FUNCIONES PARA CONVERSACIÓN
# ============================
def parse_dialogue(text: str):
    """
    Parsea un diálogo en formato:
    Personaje: texto...
    Devuelve:
      - lista de personajes únicos
      - lista de segmentos (personaje, texto)
    """
    personajes = []
    segmentos = []

    for linea in text.splitlines():
        linea = linea.strip()
        if not linea:
            continue

        if ":" in linea:
            nombre, contenido = linea.split(":", 1)
            nombre = nombre.strip()
            contenido = contenido.strip()
        else:
            nombre = "Narrador"
            contenido = linea

        if not contenido:
            continue

        if nombre not in personajes:
            personajes.append(nombre)

        segmentos.append((nombre, contenido))

    return personajes, segmentos


def generar_linea_gtts(texto: str, lang: str) -> bytes:
    """Genera una línea de diálogo en MP3 usando gTTS."""
    tts = gTTS(text=texto, lang=lang)
    buf = io.BytesIO()
    tts.write_to_fp(buf)
    buf.seek(0)
    return buf.read()


def concatenar_mp3(lista_mp3) -> bytes:
    """
    Concatena múltiples chunks MP3.
    gTTS genera MP3 válidos; concatenarlos así suele funcionar bien
    para uso simple (no es edición profesional, pero sirve perfecto
    para diálogos educativos).
    """
    final = b""
    for mp3 in lista_mp3:
        final += mp3
    return final


# ============================
# SELECCIÓN DE MODO
# ============================
modo = st.radio(
    "¿Qué deseas hacer?",
    ["Narración", "Conversación"],
    horizontal=True
)

st.markdown("---")


# ============================
# MODO: NARRACIÓN
# ============================
if modo == "Narración":
    st.subheader("📖 Modo Narración")

    texto = st.text_area(
        "Texto a convertir:",
        height=250,
        placeholder="Escribe aquí el texto que deseas convertir a audio…"
    )

    idioma_label = st.selectbox("Idioma del audio:", list(IDIOMAS.keys()))
    lang_code = IDIOMAS[idioma_label]

    nombre_archivo = st.text_input("Nombre del archivo (sin .mp3):", "audio_narracion")

    col1, col2 = st.columns(2)
    btn_previa = col1.button("🔊 Previsualizar narración")
    btn_descargar = col2.button("⬇️ Generar y descargar narración")

    if btn_previa or btn_descargar:
        if not texto.strip():
            st.error("❌ El texto está vacío.")
        else:
            try:
                audio_bytes = generar_audio_gtts(texto, lang_code)
                buffer = io.BytesIO(audio_bytes)

                st.success("✅ Audio generado correctamente.")
                st.audio(buffer, format="audio/mp3")

                if btn_descargar:
                    st.download_button(
                        "⬇️ Descargar MP3",
                        data=audio_bytes,
                        file_name=f"{nombre_archivo}.mp3",
                        mime="audio/mpeg",
                    )

            except Exception as e:
                st.error(f"❌ Error al generar el audio: {e}")


# ============================
# MODO: CONVERSACIÓN MULTI-ACENTO
# ============================
elif modo == "Conversación":
    st.subheader("🎭 Modo Conversación (múltiples acentos con gTTS)")

    st.write(
        "**Formato recomendado:**\n"
        "`Personaje: diálogo...`\n\n"
        "Ejemplo:\n"
        "Profe: Hola, ¿cómo están hoy?\n"
        "Alumno: Muy bien, profe.\n"
        "Narrador: La clase empieza con energía."
    )

    texto_conv = st.text_area(
        "Escribe el diálogo aquí:",
        height=260
    )

    personajes, segmentos = [], []
    if texto_conv.strip():
        personajes, segmentos = parse_dialogue(texto_conv)

    if personajes:
        st.markdown("### 🎙️ Voces / acentos por personaje")
        for p in personajes:
            st.selectbox(
                f"Voz/acento para «{p}»:",
                list(IDIOMAS_CONVERSACION.keys()),
                key=f"voz_{p}"
            )
    else:
        st.info("Escribe el diálogo arriba para detectar personajes y elegir sus acentos.")

    nombre_archivo_conv = st.text_input(
        "Nombre del archivo (sin .mp3):",
        "dialogo_multivoces"
    )

    col1, col2 = st.columns(2)
    btn_prev = col1.button("🔊 Previsualizar diálogo multivoces")
    btn_down = col2.button("⬇️ Generar y descargar MP3 multivoces")

    if btn_prev or btn_down:
        if not texto_conv.strip():
            st.error("❌ El diálogo está vacío.")
        elif not segmentos:
            st.error("❌ No se encontraron líneas válidas en el diálogo.")
        else:
            try:
                # Generar MP3 por línea usando el acento de cada personaje
                audios = []
                for personaje, frase in segmentos:
                    voz_label = st.session_state.get(f"voz_{personaje}")
                    if not voz_label:
                        # Por si acaso, usa español de España por defecto
                        voz_label = "Español - España"
                    lang = IDIOMAS_CONVERSACION[voz_label]

                    texto_linea = f"{personaje}: {frase}"
                    mp3_linea = generar_linea_gtts(texto_linea, lang)
                    audios.append(mp3_linea)

                audio_final = concatenar_mp3(audios)
                buffer = io.BytesIO(audio_final)

                st.success("✅ ¡Diálogo generado con múltiples acentos!")
                st.audio(buffer, format="audio/mp3")

                if btn_down:
                    st.download_button(
                        "⬇️ Descargar MP3 multivoces",
                        data=audio_final,
                        file_name=f"{nombre_archivo_conv}.mp3",
                        mime="audio/mpeg",
                    )

            except Exception as e:
                st.error(f"❌ Error al generar el audio del diálogo: {e}")

st.markdown("---")
st.markdown(
    "<div style='text-align: right; color: gray;'>Hecho por Sebastian V.</div>",
    unsafe_allow_html=True
)
