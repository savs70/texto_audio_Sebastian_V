# ============================
# FUNCIONES PARA CONVERSACIÓN MULTI-VOZ
# ============================

IDIOMAS_CONVERSACION = {
    "Español - España": "es",
    "Español - México": "es-mx",
    "Español - Colombia": "es-co",
    "Español - Argentina": "es-us",   # Google usa 'es-us' para acento rioplatense
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

def parse_dialogue(text: str):
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

        if nombre not in personajes:
            personajes.append(nombre)

        segmentos.append((nombre, contenido))
    return personajes, segmentos


def generar_linea_gtts(texto, lang):
    tts = gTTS(text=texto, lang=lang)
    buf = io.BytesIO()
    tts.write_to_fp(buf)
    buf.seek(0)
    return buf.read()


def concatenar_mp3(lista_mp3):
    """Concatena múltiples bytes MP3 en un solo archivo."""
    final = b""
    for mp3 in lista_mp3:
        final += mp3
    return final


# ============================
# SECCIÓN COMPLETA DE CONVERSACIÓN
# ============================

elif modo == "Conversación":
    st.subheader("🎭 Modo Conversación (múltiples voces/accentos con gTTS)")

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

    if texto_conv.strip():
        personajes, segmentos = parse_dialogue(texto_conv)

        st.markdown("### 🎙️ Voces/Acentos por personaje")
        voz_por_personaje = {}
        for p in personajes:
            voz_por_personaje[p] = st.selectbox(
                f"Voz para «{p}»:",
                list(IDIOMAS_CONVERSACION.keys()),
                key=f"voz_{p}"
            )
    else:
        personajes, segmentos = [], []

    nombre_archivo_conv = st.text_input(
        "Nombre del archivo (sin .mp3):",
        "dialogo_multivoces"
    )

    col1, col2 = st.columns(2)
    btn_prev = col1.button("🔊 Previsualizar diálogo multivoces")
    btn_down = col2.button("⬇️ Generar y descargar MP3")

    if btn_prev or btn_down:
        if not texto_conv.strip():
            st.error("❌ El diálogo está vacío.")
        else:
            audios = []
            for personaje, frase in segmentos:
                lang = IDIOMAS_CONVERSACION[ st.session_state[f"voz_{personaje}"] ]
                mp3_linea = generar_linea_gtts(f"{personaje}: {frase}", lang)
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
