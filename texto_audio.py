import streamlit as st
import edge_tts
import asyncio
import io
import re

st.set_page_config(page_title="Convertidor de Texto a MP3 – Sebastián V.", layout="centered")

st.title("🎧 Convertidor de Texto a MP3 – Sebastián V.")
st.write("Convierte texto a voz usando Edge-TTS directamente desde esta app.")

# -------------------------
# VOCES DISPONIBLES
# -------------------------
VOCES = {
    "Español (España) – Elvira": "es-ES-ElviraNeural",
    "Español (España) – Álvaro": "es-ES-AlvaroNeural",
    "Español (México) – Dalia": "es-MX-DaliaNeural",
    "Español (México) – Jorge": "es-MX-JorgeNeural",
    "Coreano – SunHi": "ko-KR-SunHiNeural",
    "Coreano – InJoon": "ko-KR-InJoonNeural",
    "Chino – Xiaoxiao": "zh-CN-XiaoxiaoNeural",
    "Chino – Xiaoyi": "zh-CN-XiaoyiNeural",
}

# -------------------------
# MODO DE USO
# -------------------------
modo = st.radio("Selecciona el modo:", ["Narración", "Conversación"])

# -------------------------
# INTERFAZ PARA NARRACIÓN
# -------------------------
if modo == "Narración":

    texto = st.text_area(
        "Escribe o pega tu texto:",
        height=250,
        placeholder="Ingresa tu texto aquí…"
    )

    voz = st.selectbox("Selecciona la voz:", list(VOCES.keys()))
    rate = st.slider("Velocidad", -50, 50, 0, format="%d%%")
    volume = st.slider("Volumen", -50, 50, 0, format="%d%%")

    if st.button("🎧 Generar audio"):
        if not texto.strip():
            st.error("El texto está vacío.")
        else:
            with st.spinner("Generando audio…"):

                async def generar():
                    communicate = edge_tts.Communicate(
                        text=texto,
                        voice=VOCES[voz],
                        rate=f"{rate}%",
                        volume=f"{volume}%"
                    )
                    audio = io.BytesIO()
                    async for chunk in communicate.stream():
                        if chunk["type"] == "audio":
                            audio.write(chunk["data"])
                    audio.seek(0)
                    return audio

                audio = asyncio.run(generar())

                st.audio(audio, format="audio/mp3")
                st.success("¡Audio generado!")

# -------------------------
# INTERFAZ PARA CONVERSACIÓN
# -------------------------
else:

    st.markdown("### 💬 Escribe un diálogo usando este formato:")
    st.markdown("""
    Escribe cada línea así:

    **Nombre: texto**

    Ejemplo:
    - Profe: Hola, ¿cómo están?
    - Alumno: Estamos bien, profe.
    - Narrador: La clase se anima.
    """)

    texto = st.text_area(
        "Diálogo:",
        height=280,
        placeholder="Profe: Hoy veremos el pretérito imperfecto...\nAlumno: ¿También listening?\nNarrador: La clase se anima..."
    )

    # VOCES POR PERSONA
    st.subheader("Asignar voces")

    personas = sorted(set(re.findall(r"^([^:]+):", texto, flags=re.MULTILINE)))

    asignaciones = {}

    for p in personas:
        asignaciones[p] = st.selectbox(
            f"Voz para **{p}**:",
            list(VOCES.keys()),
            key=f"voz_{p}"
        )

    rate = st.slider("Velocidad", -50, 50, 0, format="%d%%", key="rate_conv")
    volume = st.slider("Volumen", -50, 50, 0, format="%d%%", key="vol_conv")

    if st.button("🎧 Generar conversación"):
        if not texto.strip():
            st.error("El texto está vacío.")
        elif len(personas) == 0:
            st.error("No se detectaron nombres. Usa el formato: Nombre: texto")
        else:
            st.info("Generando conversación… puede tardar unos segundos.")

            partes = re.findall(r"^([^:]+):\s*(.+)", texto, flags=re.MULTILINE)

            async def generar_dialogo():
                audio_total = io.BytesIO()

                for nombre, frase in partes:
                    voz_persona = VOCES[asignaciones[nombre]]

                    # Los audios NO incluyen el nombre, solo la frase
                    communicate = edge_tts.Communicate(
                        text=frase,
                        voice=voz_persona,
                        rate=f"{rate}%",
                        volume=f"{volume}%"
                    )

                    async for chunk in communicate.stream():
                        if chunk["type"] == "audio":
                            audio_total.write(chunk["data"])

                audio_total.seek(0)
                return audio_total

            audio_final = asyncio.run(generar_dialogo())

            st.audio(audio_final, format="audio/mp3")
            st.success("¡Conversación generada!")

st.markdown("---")
st.markdown("App creada con ❤️ por **Sebastián V.**")


