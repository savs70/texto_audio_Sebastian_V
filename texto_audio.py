import io
import asyncio
from typing import List, Tuple, Dict

import streamlit as st
import edge_tts

# ===== Voces disponibles (puedes ampliar esta lista) =====
VOICE_OPTIONS = {
    # -----------------------
    # ESPAÑOL - España
    # -----------------------
    "Español (España) - Elvira (♀)": "es-ES-ElviraNeural",
    "Español (España) - Álvaro (♂)": "es-ES-AlvaroNeural",
    "Español (España) - Laia (♀)": "es-ES-LaiaNeural",
    "Español (España) - Tomás (♂)": "es-ES-TomasNeural",

    # -----------------------
    # ESPAÑOL - México
    # -----------------------
    "Español (México) - Dalia (♀)": "es-MX-DaliaNeural",
    "Español (México) - Cecilia (♀)": "es-MX-CeciliaNeural",
    "Español (México) - Jorge (♂)": "es-MX-JorgeNeural",
    "Español (México) - Lucas (♂)": "es-MX-LucasNeural",

    # -----------------------
    # ESPAÑOL - Argentina
    # -----------------------
    "Español (Argentina) - Elena (♀)": "es-AR-ElenaNeural",
    "Español (Argentina) - Tomás (♂)": "es-AR-TomasNeural",

    # -----------------------
    # ESPAÑOL - Colombia
    # -----------------------
    "Español (Colombia) - Salomé (♀)": "es-CO-SalomeNeural",
    "Español (Colombia) - Gonzalo (♂)": "es-CO-GonzaloNeural",

    # -----------------------
    # ESPAÑOL - Chile
    # -----------------------
    "Español (Chile) - Catalina (♀)": "es-CL-CatalinaNeural",
    "Español (Chile) - Lorenzo (♂)": "es-CL-LorenzoNeural",

    # -----------------------
    # ESPAÑOL - Perú
    # -----------------------
    "Español (Perú) - Camila (♀)": "es-PE-CamilaNeural",
    "Español (Perú) - Lorenzo (♂)": "es-PE-LorenzoNeural",

    # -----------------------
    # COREANO
    # -----------------------
    "Coreano - Sun-Hi (♀)": "ko-KR-SunHiNeural",
    "Coreano - In-Joon (♂)": "ko-KR-InJoonNeural",
    "Coreano - Ji-Min (♀)": "ko-KR-JiMinNeural",
    "Coreano - Seo-Yeon (♀)": "ko-KR-SeoYeonNeural",
    "Coreano - Bong-Hyeon (♂)": "ko-KR-BongHyeonNeural",

    # -----------------------
    # INGLÉS (ejemplos)
    # -----------------------
    "Inglés (EE.UU.) - Aria (♀)": "en-US-AriaNeural",
    "Inglés (EE.UU.) - Guy (♂)": "en-US-GuyNeural",

     # -----------------------
    # MANDARÍN - China (zh-CN)
    # -----------------------
    "Mandarín (China) - Xiaoxiao (♀)": "zh-CN-XiaoxiaoNeural",
    "Mandarín (China) - Xiaoyi (♀)": "zh-CN-XiaoyiNeural",
    "Mandarín (China) - Xiaoshuang (♀, niña)": "zh-CN-XiaoshuangNeural",
    "Mandarín (China) - Xiaozhen (♀, narradora)": "zh-CN-XiaozhenNeural",
    "Mandarín (China) - Yunxi (♂)": "zh-CN-YunxiNeural",
    "Mandarín (China) - Yunye (♂, maduro)": "zh-CN-YunyeNeural",
    "Mandarín (China) - Yunyang (♂, joven)": "zh-CN-YunyangNeural",

    # -----------------------
    # MANDARÍN - Taiwán (zh-TW)
    # -----------------------
    "Mandarín (Taiwán) - HsiaoChen (♀)": "zh-TW-HsiaoChenNeural",
    "Mandarín (Taiwán) - HsiaoYu (♀)": "zh-TW-HsiaoYuNeural",
    "Mandarín (Taiwán) - YunJhe (♂)": "zh-TW-YunJheNeural",
}

# ===== Configuración general de la app =====
st.set_page_config(
    page_title="Convertidor de texto a MP3 de Sebastian V.",
    page_icon="🎧",
    layout="centered",
)

st.title("🎧 Convertidor de texto a MP3 de Sebastian V.")
st.write("Elige si quieres generar **una narración** o **una conversación con varias voces**.")


# ===== Funciones comunes =====
async def synthesize_edge_tts(text: str, voice_name: str, velocidad: str) -> bytes:
    """Genera audio MP3 en memoria usando edge-tts."""
    # rate: +0% normal, -20% más lento
    if velocidad == "Lenta":
        rate = "-20%"
    else:
        rate = "+0%"

    communicate = edge_tts.Communicate(text=text, voice=voice_name, rate=rate)

    audio_bytes = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_bytes += chunk["data"]

    return audio_bytes


def generar_audio_simple(texto: str, voz_label: str, velocidad: str) -> bytes:
    """Genera audio MP3 para narración simple (una voz)."""
    voice_name = VOICE_OPTIONS[voz_label]
    return asyncio.run(synthesize_edge_tts(texto, voice_name, velocidad))


def parse_dialogue(text: str) -> Tuple[List[str], List[Tuple[str, str]]]:
    """
    Devuelve:
      - lista de personajes únicos
      - lista de segmentos (personaje, texto)
    Formato esperado por línea: 'Nombre: texto...'
    Si una línea no tiene ':', se asigna al 'Narrador'.
    """
    speakers: List[str] = []
    segments: List[Tuple[str, str]] = []

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        if ":" in line:
            name, content = line.split(":", 1)
            name = name.strip()
            content = content.strip()
            if not content:
                continue
        else:
            name = "Narrador"
            content = line

        if name not in speakers:
            speakers.append(name)
        segments.append((name, content))

    return speakers, segments


def generate_full_dialogue_audio(
    segments: List[Tuple[str, str]],
    speakers: List[str],
    velocidad: str,
) -> bytes:
    """
    Genera el audio completo del diálogo concatenando las réplicas
    de cada personaje con su voz correspondiente.
    """
    # Mapear cada speaker a su voz (voice_name real)
    speaker_to_voice: Dict[str, str] = {}
    for speaker in speakers:
        voice_label = st.session_state.get(f"voice_{speaker}")
        if not voice_label:
            # por si acaso, asignamos una voz por defecto
            voice_label = list(VOICE_OPTIONS.keys())[0]
        speaker_to_voice[speaker] = VOICE_OPTIONS[voice_label]

    # Concatenar audios de cada intervención
    final_audio = b""
    for speaker, text in segments:
        voice_name = speaker_to_voice.get(
            speaker, VOICE_OPTIONS[list(VOICE_OPTIONS.keys())[0]]
        )
        audio_bytes = asyncio.run(synthesize_edge_tts(text, voice_name, velocidad))
        final_audio += audio_bytes

    return final_audio


# ===== Selector de modo =====
modo = st.radio(
    "¿Qué deseas hacer?",
    ["Narración", "Conversación"],
    horizontal=True,
)

st.markdown("---")

# =========================
# MODO NARRACIÓN
# =========================
if modo == "Narración":
    st.subheader("📖 Modo narración (una sola voz)")

    texto = st.text_area(
        "Texto a convertir",
        height=250,
        placeholder="Pega aquí el texto que quieras narrar…",
        key="texto_narracion",
    )

    col1, col2 = st.columns(2)
    with col1:
        voz_label = st.selectbox(
            "Voz (idioma / género)", list(VOICE_OPTIONS.keys()), key="voz_narracion"
        )
    with col2:
        velocidad = st.selectbox("Velocidad", ["Normal", "Lenta"], key="vel_narracion")

    nombre_base = st.text_input(
        "Nombre del archivo (sin .mp3)", value="audio_narracion", key="nombre_narracion"
    )

    colA, colB = st.columns(2)
    boton_previa = colA.button("🔊 Previsualizar narración")
    boton_generar = colB.button("⚙️ Generar y descargar MP3")

    if boton_previa or boton_generar:
        if not texto.strip():
            st.error("❌ El cuadro de texto está vacío.")
        else:
            try:
                audio_bytes = generar_audio_simple(texto, voz_label, velocidad)
                buffer = io.BytesIO(audio_bytes)

                st.success("✅ Audio generado correctamente.")
                st.audio(buffer, format="audio/mp3")

                if boton_generar:
                    nombre_archivo = f"{nombre_base or 'audio_narracion'}.mp3"
                    st.download_button(
                        "⬇️ Descargar MP3",
                        data=audio_bytes,
                        file_name=nombre_archivo,
                        mime="audio/mpeg",
                    )

            except Exception as e:
                st.error(f"❌ Error al generar el audio (Edge TTS): {e}")


# =========================
# MODO CONVERSACIÓN
# =========================
elif modo == "Conversación":
    st.subheader("🎭 Modo conversación (múltiples voces)")

    st.write(
        "Escribe un diálogo usando el formato `Nombre: texto` en cada línea.\n"
        "Ejemplo:\n"
        "`Profe: Hola, ¿cómo están hoy?`\n"
        "`Alumno: Estamos bien, profe.`\n"
        "`Narrador: La clase se anima.`"
    )

    texto_conv = st.text_area(
        "Diálogo",
        height=260,
        placeholder=(
            "Profe: Hoy vamos a practicar el pretérito imperfecto.\n"
            "Alumno: Profe, ¿podemos hacer también listening?\n"
            "Narrador: La clase se anima.\n"
            "Profe: Claro, y luego usamos el convertidor de Sebastián."
        ),
        key="texto_conversacion",
    )

    speakers: List[str] = []
    segments: List[Tuple[str, str]] = []

    if texto_conv.strip():
        speakers, segments = parse_dialogue(texto_conv)

    if speakers:
        st.markdown("### Personajes detectados y sus voces")

        for speaker in speakers:
            st.selectbox(
                f"Voz para «{speaker}»",
                list(VOICE_OPTIONS.keys()),
                key=f"voice_{speaker}",
            )
    else:
        st.info("Escribe el diálogo arriba para detectar personajes y asignar voces.")

    nombre_base_conv = st.text_input(
        "Nombre del archivo (sin .mp3)",
        value="dialogo_generado",
        key="nombre_dialogo",
    )

    velocidad_conv = st.selectbox(
        "Velocidad global", ["Normal", "Lenta"], key="vel_dialogo"
    )

    col1, col2 = st.columns(2)
    boton_previa_conv = col1.button("🔊 Previsualizar diálogo completo")
    boton_descargar_conv = col2.button("⬇️ Generar y descargar MP3 del diálogo")

    if boton_previa_conv or boton_descargar_conv:
        if not texto_conv.strip():
            st.error("❌ El cuadro de texto está vacío.")
        elif not segments:
            st.error("❌ No se encontraron líneas válidas en el diálogo.")
        else:
            try:
                audio_bytes = generate_full_dialogue_audio(
                    segments, speakers, velocidad_conv
                )
                buffer = io.BytesIO(audio_bytes)

                st.success("✅ Audio del diálogo generado correctamente.")
                st.audio(buffer, format="audio/mp3")

                if boton_descargar_conv:
                    nombre_archivo = f"{nombre_base_conv or 'dialogo_generado'}.mp3"
                    st.download_button(
                        "⬇️ Descargar MP3 del diálogo",
                        data=audio_bytes,
                        file_name=nombre_archivo,
                        mime="audio/mpeg",
                    )
            except Exception as e:
                st.error(f"❌ Error al generar el audio del diálogo (Edge TTS): {e}")

st.markdown("---")
st.markdown(
    "<div style='text-align: right; color: gray;'>Hecho por Sebastian V.</div>",
    unsafe_allow_html=True,
)
