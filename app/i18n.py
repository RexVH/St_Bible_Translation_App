# app/i18n.py

UI_STRINGS = {
    "English": {
        "load": "Load",
        "selection": "Selection",
        "language": "Language",
        "bible": "Bible",
        "level": "Level",
        "book": "Book",
        "chapter": "Chapter",
        "reference": "Reference",
        "contact_dev": "Contact the developer",
        "view_image": "View image",
        "download_mp3": "Download MP3",
        "audio_speed": "Speed",
        "nav_prev": "Back",
        "nav_next": "Next",
        "show_verses": "Show verse numbers",
        "highlight_vocab": "Highlight vocabulary",
        "key_words": "Key words",
        "vocabulary": "Vocabulary",
        "quiz": "Quiz",
        "hint": "Hint",
        "explanation": "Explanation",
        "chat_soon": "Chat (Coming soon...)",
    },
    "German": {
        "load": "Laden",
        "selection": "Auswahl",
        "language": "Sprache",
        "bible": "Bibel",
        "level": "Niveau",
        "book": "Buch",
        "chapter": "Kapitel",
        "reference": "Nachschlagen",
        "contact_dev": "Entwickler kontaktieren",
        "view_image": "Bild ansehen",
        "download_mp3": "MP3 herunterladen",
        "audio_speed": "Tempo",
        "nav_prev": "Zurück",
        "nav_next": "Weiter",
        "show_verses": "Versnummern anzeigen",
        "highlight_vocab": "Vokabeln markieren",
        "key_words": "Schlüsselwörter",
        "vocabulary": "Wortschatz",
        "quiz": "Quiz",
        "hint": "Hinweis",
        "explanation": "Erklärung",
        "chat_soon": "Chat (Demnächst...)",
    },
}


def t(state, key: str) -> str:
    lang = state.get("active_language", "English")
    return UI_STRINGS.get(lang, UI_STRINGS["English"]).get(key, key)
