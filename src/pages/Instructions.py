import streamlit as st

st.set_page_config(page_title="Instructions", layout="wide")

st.title("How to Use the Bible Translation App")
st.caption("Use the tabs to view the same guidance in English, Deutsch, or Espanol.")

english_text = """
### Getting Started
1. Open the sidebar and choose your **Language**.
2. Choose a **Bible/Translation**.
3. Select a **Level** (A1, A2, B1, B2, or Source).
4. Select a **Book** and **Chapter**.
5. Click **Load** to display the selected chapter content.

### Main Artifacts and Features
- **Graded Text**: The chapter text is adapted to your selected level.
- **Image**: Each chapter can include an illustration and a larger image view.
- **Audio MP3**: Listen to chapter audio directly in the app with speed controls.
- **Downloadable MP3**: Download chapter audio for offline listening.
- **Vocab Strip**: A quick strip of key vocabulary appears near the top.
- **Vocabulary Words**: Open the Vocabulary section to browse/search words, meanings, and examples.
- **Teacher's Notes**: Teaching notes appear with the verses to support instruction.
- **Quiz**: Review comprehension with the built-in quiz for the chapter.

### Navigation Tips
- Use **Prev** and **Next** to move chapter-by-chapter.
- Change active **Book** and **Chapter** from the main navigation row.
- Toggle options like showing verse numbers and highlighting vocabulary.

### Coming Soon
- **Interactive chat is coming soon** to support guided learning and Q&A.
"""

german_text = """
### Erste Schritte
1. Öffnen Sie die Seitenleiste und wählen Sie Ihre **Sprache**.
2. Wählen Sie eine **Bibel/Übersetzung**.
3. Wählen Sie ein **Niveau** (A1, A2, B1, B2 oder Quelle).
4. Wählen Sie ein **Buch** und ein **Kapitel**.
5. Klicken Sie auf **Load**, um den ausgewählten Kapitelinhalt anzuzeigen.

### Hauptinhalte und Funktionen
- **Graded Text**: Der Kapiteltext ist an das gewählte Niveau angepasst.
- **Image**: Jedes Kapitel kann eine Illustration und eine größere Bildansicht enthalten.
- **Audio MP3**: Hören Sie Kapitel-Audio direkt in der App mit Geschwindigkeitssteuerung.
- **Downloadable MP3**: Laden Sie Kapitel-Audio zum Offline-Hören herunter.
- **Vocab Strip**: Ein kurzer Streifen mit Schlüsselvokabular erscheint im oberen Bereich.
- **Vocabulary Words**: Öffnen Sie den Vokabelbereich, um Wörter, Bedeutungen und Beispiele zu durchsuchen.
- **Teacher's Notes**: Unterrichtsnotizen erscheinen bei den Versen zur Unterstützung.
- **Quiz**: Überprüfen Sie das Verständnis mit dem integrierten Kapitel-Quiz.

### Navigationstipps
- Nutzen Sie **Prev** und **Next**, um kapitelweise vor- oder zurückzugehen.
- Ändern Sie **Buch** und **Kapitel** in der Hauptnavigationszeile.
- Schalten Sie Optionen wie Versnummern und Vokabelhervorhebung ein oder aus.

### Demnächst
- **Interaktiver Chat kommt bald** zur Unterstützung von begleitetem Lernen und Fragen.
"""

spanish_text = """
### Primeros pasos
1. Abra la barra lateral y elija su **Idioma**.
2. Elija una **Biblia/Traducción**.
3. Seleccione un **Nivel** (A1, A2, B1, B2 o Fuente).
4. Seleccione un **Libro** y un **Capítulo**.
5. Haga clic en **Load** para mostrar el contenido del capítulo seleccionado.

### Artefactos principales y funciones
- **Graded Text**: El texto del capítulo está adaptado al nivel seleccionado.
- **Image**: Cada capítulo puede incluir una ilustración y una vista ampliada de la imagen.
- **Audio MP3**: Escuche el audio del capítulo directamente en la app con control de velocidad.
- **Downloadable MP3**: Descargue el audio del capítulo para escucharlo sin conexión.
- **Vocab Strip**: Una tira rápida de vocabulario clave aparece cerca de la parte superior.
- **Vocabulary Words**: Abra la sección de vocabulario para explorar/buscar palabras, significados y ejemplos.
- **Teacher's Notes**: Las notas del docente aparecen con los versículos para apoyar la enseñanza.
- **Quiz**: Revise la comprensión con el cuestionario integrado del capítulo.

### Consejos de navegación
- Use **Prev** y **Next** para moverse capítulo por capítulo.
- Cambie **Libro** y **Capítulo** desde la fila de navegación principal.
- Active o desactive opciones como mostrar números de versículos y resaltar vocabulario.

### Próximamente
- **El chat interactivo llegará pronto** para apoyar el aprendizaje guiado y preguntas y respuestas.
"""

tab_en, tab_de, tab_es = st.tabs(["English", "Deutsch", "Espanol"])

with tab_en:
    st.markdown(english_text)

with tab_de:
    st.markdown(german_text)

with tab_es:
    st.markdown(spanish_text)
