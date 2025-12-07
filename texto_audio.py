import io
from gtts import gTTS
import streamlit as st

# ============================
# CONFIGURACIÓN DE LA PÁGINA
# ============================
st.set_page_config(
    page_title="Convertidor de texto a MP3 de Sebastián V.",
    page_icon="🎧",
    layout="centered",
)

st.title("🎧 Convertidor de texto a MP3 de Sebastián V.")
st.write(
    "Convierte texto en audio MP3. "
    "Puedes usarlo como narrador o para practicar diálogos."
)

# ============================
# VOCES / IDIOMAS DISPONIBLES
# ============================

VOICE_OPTIONS = {
    # Español: mismo idioma (es), distinto acento con tld
    "Español (España)": {"lang": "es", "tld": "es"},
    "Español (México)": {"lang": "es", "tld": "com.mx"},
    "Español (Argentina)": {"lang": "es", "tld": "com.ar"},
    "Español (Colombia)": {"lang": "es", "tld": "com.co"},

    # Otros idiomas
    "Inglés (EE.UU.)": {"lang": "en", "tld": "com"},
    "Coreano": {"lang": "ko", "tld": "co.kr"},
    "Mandarín (China)": {"lang": "zh-CN", "tld": "com"},
}


def generar_audio_gtts(texto: str, lang: str, tld: str) -> bytes:
    """Genera audio MP3 usando gTTS y devuelve los bytes."""
    tts = gTTS(text=texto, lang=lang, tld=tld)
    buffer = io.BytesIO()
    tts.write_to_fp(buffer)
    buffer.seek(0)
    return buffer.read()


def parse_dialog(text: str, incluir_nombres: bool = False) -> str:
    """
    Convierte un diálogo tipo:
        Profe: Hola
        Alumno: Bien

    - incluir_nombres=True  -> "Profe: Hola. Alumno: Bien."
    - incluir_nombres=False -> "Hola. Bien."
    """
    fragmentos = []

    for linea in text.splitlines():
        linea = linea.strip()
        if not linea:
            continue

        if ":" in linea:
            nombre, contenido = linea.split(":", 1)
            nombre = nombre.strip()
            contenido = contenido.strip()
            if not contenido:
                continue

            if incluir_nombres:
                fragmentos.append(f"{nombre}: {contenido}")
            else:
                fragmentos.append(contenido)
        else:
            # Línea sin nombre (por ejemplo narrador sin etiqueta)
            fragmentos.append(linea)

    # Unimos con puntos para provocar pequeñas pausas
    return ". ".join(fragmentos)


# ============================
# SELECCIÓN DE MODO
# ============================

modo = st.radio(
    "¿Qué deseas hacer?",
    ["Narración", "Conversación"],
    horizontal=True,
)

st.markdown("---")

# ============================
# SELECCIÓN DE VOZ (ACENTO)
# ============================

voz_label = st.selectbox(
    "Selecciona la voz (acento / idioma):",
    list(VOICE_OPTIONS.keys()),
)
voz_cfg = VOICE_OPTIONS[voz_label]
lang = voz_cfg["lang"]
tld = voz_cfg["tld"]

st.markdown("---")

# ============================
# MODO NARRACIÓN
# ============================

if modo == "Narración":
    st.subheader("📖 Modo Narración")

    texto = st.text_area(
        "Escribe el texto que quieres convertir a audio:",
        height=260,
        placeholder="Escribe aquí tu texto para convertirlo en narración…",
    )

    nombre_archivo = st.text_input(
        "Nombre del archivo (sin .mp3):",
        "narracion_sebastian_v",
        key="nombre_narracion",
    )

    col1, col2 = st.columns(2)
    btn_previa = col1.button("🔊 Previsualizar narración", key="btn_previa_narracion")
    btn_desc = col2.button(
        "⬇️ Generar y descargar MP3", key="btn_descargar_narracion"
    )

    if btn_previa or btn_desc:
        if not texto.strip():
            st.error("❌ El texto está vacío.")
        else:
            try:
                audio_bytes = generar_audio_gtts(texto, lang=lang, tld=tld)
                st.success("✅ Audio generado correctamente.")
                st.audio(audio_bytes, format="audio/mp3")

                if btn_desc:
                    st.download_button(
                        "⬇️ Descargar MP3",
                        data=audio_bytes,
                        file_name=f"{nombre_archivo}.mp3",
                        mime="audio/mpeg",
                        key="download_narracion",
                    )
            except Exception as e:
                st.error(f"❌ Error al generar el audio: {e}")

# ============================
# MODO CONVERSACIÓN
# ============================

else:
    st.subheader("🎭 Modo Conversación")

    st.markdown(
        "Escribe un diálogo usando el formato "
        "`Nombre: texto` en cada línea.  \n"
        "La voz leerá **solo las frases**, **sin decir los nombres**.  \n\n"
        "Ejemplo: `Profe: Hola, ¿cómo están hoy?`   "
        "`Alumno: Estamos bien, profe.`   "
        "`Narrador: La clase se anima.`"
    )

    ejemplo_dialogo = (
        "María: Exacto. Por eso hoy son tan importantes. "
        "Los usamos para estudiar, trabajar, viajar… para casi todo.\n\n"
        "Fernando: Aunque también tienen desventajas, ¿no?\n\n"
        "María: Sí, claro. La gente se distrae mucho con el móvil "
        "y algunos modelos son muy caros. Pero si lo usamos bien, "
        "es una herramienta súper útil.\n\n"
        "Fernando: Totalmente de acuerdo. El móvil cambió nuestra vida."
    )

    texto_dialogo = st.text_area(
        "Diálogo",
        height=260,
        placeholder=ejemplo_dialogo,
        key="dialogo_textarea",
    )

    nombre_archivo_d = st.text_input(
        "Nombre del archivo (sin .mp3):",
        "dialogo_sebastian_v",
        key="nombre_dialogo",
    )

    col1, col2 = st.columns(2)
    btn_previa_d = col1.button("🔊 Previsualizar diálogo", key="btn_previa_dialogo")
    btn_desc_d = col2.button(
        "⬇️ Generar y descargar MP3 del diálogo",
        key="btn_descargar_dialogo",
    )

    if btn_previa_d or btn_desc_d:
        if not texto_dialogo.strip():
            st.error("❌ El diálogo está vacío.")
        else:
            try:
                # NO leemos los nombres de los participantes
                texto_procesado = parse_dialog(texto_dialogo, incluir_nombres=False)

                if not texto_procesado.strip():
                    st.error("❌ No se encontraron líneas válidas en el diálogo.")
                else:
                    audio_bytes = generar_audio_gtts(
                        texto_procesado, lang=lang, tld=tld
                    )
                    st.success("✅ Audio del diálogo generado correctamente.")
                    st.audio(audio_bytes, format="audio/mp3")

                    if btn_desc_d:
                        st.download_button(
                            "⬇️ Descargar MP3 del diálogo",
                            data=audio_bytes,
                            file_name=f"{nombre_archivo_d}.mp3",
                            mime="audio/mpeg",
                            key="download_dialogo",
                        )
            except Exception as e:
                st.error(f"❌ Error al generar el audio del diálogo: {e}")

# ============================
# PIE DE PÁGINA
# ============================

st.markdown("---")
st.markdown(
    "<div style='text-align: right; color: gray; font-size: 0.9rem;'>"
    "Hecho por Sebastian V."
    "</div>",
    unsafe_allow_html=True,
)

