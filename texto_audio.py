import io
from gtts import gTTS
import streamlit as st

# ===== Configuración de idiomas y acentos =====
OPCIONES_IDIOMA = {
    "Español (México)": ("es", "com.mx"),
    "Español (España)": ("es", "es"),
    "Español (Estados Unidos)": ("es", "com"),
    
    "Inglés (EE.UU.)": ("en", "com"),
    "Inglés (Reino Unido)": ("en", "co.uk"),
    
    "Francés": ("fr", "fr"),
    "Portugués (Brasil)": ("pt", "com.br"),
    "Italiano": ("it", "it"),
    "Alemán": ("de", "de"),
    
    "Holandés": ("nl", "nl"),
    "Sueco": ("sv", "se"),
    "Noruego": ("no", "no"),
    "Danés": ("da", "dk"),
    "Finlandés": ("fi", "fi"),
    
    "Coreano": ("ko", "co.kr"),
    "Japonés": ("ja", "co.jp"),
    "Chino (Simplificado)": ("zh-CN", "com"),
    "Chino (Tradicional)": ("zh-TW", "com"),
    
    "Ruso": ("ru", "ru"),
    "Árabe": ("ar", "sa"),
    "Hindi": ("hi", "co.in"),
}

st.set_page_config(
    page_title="Convertidor de texto a MP3 de Sebastian V.",
    page_icon="🎧",
    layout="centered"
)

st.title("🎧 Convertidor de texto a MP3 de Sebastian V.")
st.write("Pega tu texto, elige idioma y escucha o descarga tu audio en MP3.")

# ===== Entrada de texto =====
texto = st.text_area(
    "Texto a convertir",
    height=250,
    placeholder="Pega aquí tu texto…"
)

# ===== Controles =====
col1, col2 = st.columns(2)
with col1:
    idioma_label = st.selectbox("Idioma / acento", list(OPCIONES_IDIOMA.keys()))
with col2:
    velocidad_lenta = st.checkbox("Voz lenta", value=False)

nombre_base = st.text_input("Nombre del archivo (sin .mp3)", value="audio_generado")

st.markdown("---")

# ===== Botones =====
colA, colB = st.columns(2)
boton_previa = colA.button("🔊 Previsualizar")
boton_generar = colB.button("⚙️ Generar audio")

# ===== Acción: PREVISUALIZAR =====
if boton_previa:
    if not texto.strip():
        st.error("❌ El cuadro de texto está vacío.")
    else:
        lang_code, tld = OPCIONES_IDIOMA[idioma_label]

        try:
            buffer = io.BytesIO()
            tts = gTTS(text=texto, lang=lang_code, tld=tld, slow=velocidad_lenta)
            tts.write_to_fp(buffer)
            buffer.seek(0)

            st.info("🔊 **Previsualización generada** (sin descarga):")
            st.audio(buffer, format="audio/mp3")
            st.caption("Usa los controles del reproductor para play/pausa y barra de progreso.")

        except Exception as e:
            st.error(f"❌ Error al previsualizar: {e}")

# ===== Acción: GENERAR AUDIO + DESCARGA =====
if boton_generar:
    if not texto.strip():
        st.error("❌ El cuadro de texto está vacío.")
    else:
        lang_code, tld = OPCIONES_IDIOMA[idioma_label]

        try:
            buffer = io.BytesIO()
            tts = gTTS(text=texto, lang=lang_code, tld=tld, slow=velocidad_lenta)
            tts.write_to_fp(buffer)
            buffer.seek(0)

            st.success("✅ Audio generado con éxito.")
            st.audio(buffer, format="audio/mp3")
            st.caption("Puedes escucharlo o descargarlo abajo.")

            buffer.seek(0)
            nombre_archivo = f"{nombre_base or 'audio_generado'}.mp3"
            
            st.download_button(
                "⬇️ Descargar MP3",
                data=buffer,
                file_name=nombre_archivo,
                mime="audio/mpeg"
            )

        except Exception as e:
            st.error(f"❌ Error al generar el audio: {e}")

st.markdown("---")
st.markdown(
    "<div style='text-align: right; color: gray;'>Hecho por Sebastian V.</div>",
    unsafe_allow_html=True
)
