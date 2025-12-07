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
st.write("Convierte texto en audio MP3 con soporte para narraciones o conversaciones.")


# ============================
# IDIOMAS DISPONIBLES (gTTS)
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
# SELECCIÓN DE MODO
# ============================
modo = st.radio(
    "¿Qué deseas hacer?",
    ["Narración", "Conversación"],
    horizontal=True
)

st.markdown("---")

# ============================
# FUNCIÓN gTTS
# ============================
def generar_audio_gtts(texto: str, lang: str) -> bytes:
    """Genera audio MP3 usando gTTS y lo devuelve en bytes."""
    tts = gTTS(text=texto, lang=lang)
    buf = io.BytesIO()
    tts.write_to_fp(buf)
    buf.seek(0)
    return buf.read()


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

    idioma = st.selectbox("Idioma del audio:", list(IDIOMAS.keys()))
    nombre_archivo = st.text_input("Nombre del archivo (sin .mp3):", "audio_narracion")

    col1, col2 = st.columns(2)
    btn_previa = col1.button("🔊 Previsualizar")
    btn_descargar = col2.button("⬇️ Generar y descargar")

    if btn_previa or btn_descargar:
        if not texto.strip():
            st.error("❌ El texto está vacío.")
        else:
            lang_code = IDIOMAS[idioma]

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
# MODO: CONVERSACIÓN
# ============================
elif modo == "Conversación":
    st.subheader("🎭 Modo Conversación")

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

    st.info("⚠️ Nota: gTTS solo permite **una voz**, así que el diálogo se narrará completo como un texto continuo.")

    idioma = st.selectbox("Idioma del audio:", list(IDIOMAS.keys()), key="idioma_conv")
    nombre_archivo = st.text_input("Nombre del archivo (sin .mp3):", "dialogo_generado")

    col1, col2 = st.columns(2)
    btn_previa_conv = col1.button("🔊 Previsualizar diálogo")
    btn_descargar_conv = col2.button("⬇️ Generar y descargar diálogo")

    if btn_previa_conv or btn_descargar_conv:
        if not texto_conv.strip():
            st.error("❌ El diálogo está vacío.")
        else:
            lang_code = IDIOMAS[idioma]

            # Conversación → texto unificado
            texto_final = texto_conv

            try:
                audio_bytes = generar_audio_gtts(texto_final, lang_code)
                buffer = io.BytesIO(audio_bytes)

                st.success("✅ Diálogo convertido a audio.")
                st.audio(buffer, format="audio/mp3")

                if btn_descargar_conv:
                    st.download_button(
                        "⬇️ Descargar MP3",
                        data=audio_bytes,
                        file_name=f"{nombre_archivo}.mp3",
                        mime="audio/mpeg",
                    )

            except Exception as e:
                st.error(f"❌ Error al generar el audio del diálogo: {e}")

st.markdown("---")
st.markdown(
    "<div style='text-align: right; color: gray;'>Hecho por Sebastian V.</div>",
    unsafe_allow_html=True
)
