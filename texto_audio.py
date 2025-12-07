import io
import re
import asyncio
import streamlit as st
import edge_tts

# ============================
# CONFIGURACIÓN DE LA PÁGINA
# ============================
st.set_page_config(
    page_title="Convertidor de texto a MP3 – Sebastián V.",
    page_icon="🎧",
    layout="centered",
)

st.title("🎧 Convertidor de texto a MP3 – Sebastián V.")
st.write("Convierte texto en audio MP3 usando Edge-TTS, sin backend separado.")

# ============================
# VOCES DISPONIBLES
# ============================
VOCES = {
    "Español (España) – Elvira": "es-ES-ElviraNeural",
    "Español (España) – Álvaro": "es-ES-AlvaroNeural",
    "Español (México) – Dalia": "es-MX-DaliaNeural",
    "Español (México) – Jorge": "es-MX-JorgeNeural",
    "Español (Argentina) – Elena": "es-AR-ElenaNeural",
    "Español (Colombia) – Salomé": "es-CO-SalomeNeural",
    "Coreano – SunHi": "ko-KR-SunHiNeural",
    "Coreano – InJoon": "ko-KR-InJoonNeural",
    "Chino – Xiaoxiao": "zh-CN-XiaoxiaoNeural",
    "Chino – Xiaoyi": "zh-CN-XiaoyiNeural",
}


def format_param(value: int) -> str:
    """
    Convierte un entero (por ejemplo 0, 10, -20)
    en el formato que Edge-TTS espera: +0%, +10%, -20%, etc.
    """
    return f"{'+' if value >= 0 else ''}{value}%"


# ============================
# FUNCIONES ASYNC
# ============================

async def generar_audio_simple(texto: str, voice: str, rate: int, volume: int,
                               progress_bar) -> io.BytesIO:
    """Genera audio para narración única."""
    rate_str = format_param(rate)
    volume_str = format_param(volume)

    communicate = edge_tts.Communicate(
        text=texto,
        voice=voice,
        rate=rate_str,
        volume=volume_str,
    )

    audio = io.BytesIO()
    step = 0

    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio.write(chunk["data"])
        # Barra de progreso "clásica"
        step = min(step + 5, 95)
        progress_bar.progress(step)

    progress_bar.progress(100)
    audio.seek(0)
    return audio


async def generar_audio_dialogo(partes, asignaciones, rate: int, volume: int,
                                progress_bar) -> io.BytesIO:
    """
    Genera audio concatenando cada intervención del diálogo.
    partes: lista de (nombre, frase)
    asignaciones: dict nombre -> voz_edge
    """
    rate_str = format_param(rate)
    volume_str = format_param(volume)

    audio_total = io.BytesIO()
    total_partes = len(partes)
    progreso = 0

    for idx, (nombre, frase) in enumerate(partes, start=1):
        voz_persona = asignaciones[nombre]

        communicate = edge_tts.Communicate(
            text=frase,
            voice=voz_persona,
            rate=rate_str,
            volume=volume_str,
        )

        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_total.write(chunk["data"])

        # Actualizamos progreso según el número de intervenciones completadas
        progreso = int(idx / total_partes * 95)
        progress_bar.progress(progreso)

    progress_bar.progress(100)
    audio_total.seek(0)
    return audio_total


# ============================
# INTERFAZ PRINCIPAL
# ============================

modo = st.radio("¿Qué deseas hacer?", ["Narración", "Conversación"], horizontal=True)
st.markdown("---")

# --------------------------
# NARRACIÓN
# --------------------------
if modo == "Narración":
    st.subheader("📖 Modo Narración")

    texto = st.text_area(
        "Escribe o pega tu texto:",
        height=260,
        placeholder="Escribe aquí tu texto para convertirlo en narración…",
    )

    voz_label = st.selectbox("Selecciona la voz:", list(VOCES.keys()))
    rate = st.slider("Velocidad", -50, 50, 0, format="%d%%", key="rate_narr")
    volume = st.slider("Volumen", -50, 50, 0, format="%d%%", key="vol_narr")

    if st.button("🎧 Generar narración"):
        if not texto.strip():
            st.error("❌ El texto está vacío.")
        else:
            progress_bar = st.progress(0)
            st.info("Generando audio…")

            audio_bytes = asyncio.run(
                generar_audio_simple(
                    texto=texto,
                    voice=VOCES[voz_label],
                    rate=rate,
                    volume=volume,
                    progress_bar=progress_bar,
                )
            )

            st.success("✅ Narración generada.")
            st.audio(audio_bytes, format="audio/mp3")
            st.download_button(
                "⬇️ Descargar MP3",
                data=audio_bytes,
                file_name="narracion_sebastian_v.mp3",
                mime="audio/mpeg",
            )

# --------------------------
# CONVERSACIÓN
# --------------------------
else:
    st.subheader("🎭 Modo Conversación")

    st.markdown(
        "Escribe un diálogo usando el formato **Nombre: texto** en cada línea.\n\n"
        "Ejemplo:\n"
        "`Profe: Hola, ¿cómo están hoy?`\n\n"
        "`Alumno: Estamos bien, profe.`\n\n"
        "`Narrador: La clase se anima.`\n\n"
        "👉 La voz **no leerá los nombres**, solo las frases."
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
        "Diálogo:",
        height=260,
        placeholder=ejemplo_dialogo,
    )

    # Detectar participantes
    personas = sorted(set(re.findall(r"^([^:]+):", texto_dialogo, flags=re.MULTILINE)))

    if personas:
        st.subheader("🎙 Voces por participante")
        asignaciones = {}
        for p in personas:
            asignaciones[p] = VOCES[st.selectbox(
                f"Voz para **{p}**:",
                list(VOCES.keys()),
                key=f"voz_{p}",
            )]
    else:
        asignaciones = {}

    rate_c = st.slider("Velocidad", -50, 50, 0, format="%d%%", key="rate_conv")
    volume_c = st.slider("Volumen", -50, 50, 0, format="%d%%", key="vol_conv")

    if st.button("🎧 Generar conversación"):
        if not texto_dialogo.strip():
            st.error("❌ El diálogo está vacío.")
        else:
            # Dividir en partes Nombre: frase
            partes = re.findall(r"^([^:]+):\s*(.+)", texto_dialogo, flags=re.MULTILINE)

            if not partes:
                st.error("❌ No se encontraron líneas con el formato `Nombre: texto`.")
            else:
                # Verificamos que todos tengan voz asignada
                nombres_detectados = {n for n, _ in partes}
                faltantes = [n for n in nombres_detectados if n not in asignaciones]
                if faltantes:
                    st.error(
                        "⚠️ Falta asignar voz a: " + ", ".join(faltantes)
                    )
                else:
                    progress_bar = st.progress(0)
                    st.info("Generando audio del diálogo…")

                    audio_final = asyncio.run(
                        generar_audio_dialogo(
                            partes=partes,
                            asignaciones=asignaciones,
                            rate=rate_c,
                            volume=volume_c,
                            progress_bar=progress_bar,
                        )
                    )

                    st.success("✅ Conversación generada.")
                    st.audio(audio_final, format="audio/mp3")
                    st.download_button(
                        "⬇️ Descargar MP3 del diálogo",
                        data=audio_final,
                        file_name="dialogo_sebastian_v.mp3",
                        mime="audio/mpeg",
                    )

# --------------------------
# PIE DE PÁGINA
# --------------------------
st.markdown("---")
st.markdown(
    "<div style='text-align:right; color:gray; font-size:0.9rem;'>Hecho por Sebastian V.</div>",
    unsafe_allow_html=True,
)
