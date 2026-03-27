# src/state.py

import os
import streamlit as st
import db_repo
from components.catalog import build_catalog

LEVELS = ["A1", "A2", "B1", "B2", "src"]


def _preferred_default_language(langs: list[str]) -> str:
    return "en" if "en" in langs else langs[0]

def _ensure_defaults():
    catalog = build_catalog(data_dir())

    langs = list(catalog.keys())
    if not langs:
        # no dbs found; keep app from crashing
        st.session_state.draft_language = "en"
        st.session_state.draft_level = "A1"
        st.session_state.draft_book_id = 1
        st.session_state.draft_chapter = 1
        return

    # --- Draft language ---
    if st.session_state.get("draft_language") not in langs:
        st.session_state.draft_language = _preferred_default_language(langs)

    # --- Draft translation (label) ---
    translations = catalog.get(st.session_state.draft_language, [])
    labels = [t["label"] for t in translations]
    if not labels:
        # language exists but no translations; defensive
        st.session_state.draft_translation_label = None
        return

    if st.session_state.get("draft_translation_label") not in labels:
        st.session_state.draft_translation_label = labels[0]

    # --- Resolve db_path from selected translation ---
    selected = next(t for t in translations if t["label"] == st.session_state.draft_translation_label)
    st.session_state.db_path = selected["db_path"]

    # --- Bible id inside this DB (usually 1 bible) ---
    # Recommended: add a db_repo helper for this (see below)
    st.session_state.draft_bible_id = db_repo.get_default_bible_id_for_db(st.session_state.db_path)

    # --- Level ---
    if st.session_state.get("draft_level") not in LEVELS:
        st.session_state.draft_level = "A1"

    # --- Books ---
    books = db_repo.get_books_for_language(st.session_state.db_path, st.session_state.draft_language)
    book_ids = [int(b["id"]) for b in books]
    default_book_id = book_ids[0] if book_ids else 1
    if st.session_state.get("draft_book_id") not in book_ids:
        st.session_state.draft_book_id = default_book_id

    # --- Chapters ---
    bible_id = st.session_state.draft_bible_id
    if bible_id is None:
        st.session_state.draft_chapter = 1
    else:
        chapters = db_repo.get_available_chapters(
            st.session_state.db_path,
            int(bible_id),
            st.session_state.draft_level,
            int(st.session_state.draft_book_id),
        )
        desired = int(st.session_state.get("draft_chapter", 1))
        st.session_state.draft_chapter = db_repo.clamp_to_available_chapter(chapters, desired)

    # --- Active defaults ---
    st.session_state.setdefault("active_language", st.session_state.draft_language)
    st.session_state.setdefault("active_translation_label", st.session_state.draft_translation_label)
    st.session_state.setdefault("active_db_path", st.session_state.db_path)
    st.session_state.setdefault("active_bible_id", st.session_state.draft_bible_id)
    st.session_state.setdefault("active_level", st.session_state.draft_level)
    st.session_state.setdefault("active_book_id", st.session_state.draft_book_id)
    st.session_state.setdefault("active_chapter", st.session_state.draft_chapter)

    st.session_state.setdefault("show_verse_numbers", True)
    st.session_state.setdefault("highlight_vocab", False)
    st.session_state.setdefault("audio_speed", 1.0)
    st.session_state.setdefault("quiz_key", None)
    st.session_state.setdefault("quiz_questions", [])
    st.session_state.setdefault("quiz_index", 0)
    st.session_state.setdefault("quiz_correct", 0)
    st.session_state.setdefault("quiz_incorrect", 0)
    st.session_state.setdefault("quiz_show_hint", False)
    st.session_state.setdefault("quiz_show_explanation", False)
    st.session_state.setdefault("quiz_last_choice", None)
    st.session_state.setdefault("quiz_last_was_correct", None)
    st.session_state.setdefault("feedback_key", None)
    st.session_state.setdefault("feedback_vote", None)
    st.session_state.setdefault("feedback_comment", "")
    st.session_state.setdefault("feedback_submitted", False)

def init_state():
    # Build catalog once per rerun (cached in build_catalog)
    catalog = build_catalog(data_dir())

    langs = list(catalog.keys())
    if not langs:
        st.error("No Bible .db files found in /data.")
        st.stop()

    # Ensure baseline keys exist before _ensure_defaults runs
    st.session_state.setdefault("draft_language", _preferred_default_language(langs))

    # Pick a default translation label for that language
    translations = catalog.get(st.session_state.draft_language, [])
    if not translations:
        st.session_state.draft_language = _preferred_default_language(langs)
        translations = catalog[st.session_state.draft_language]

    st.session_state.setdefault("draft_translation_label", translations[0]["label"])

    # Resolve db_path immediately from defaults
    selected = next(t for t in translations if t["label"] == st.session_state.draft_translation_label)
    st.session_state["db_path"] = selected["db_path"]

    if st.session_state.get("initialized"):
        _ensure_defaults()
        return

    st.session_state.initialized = True

    # Draft defaults (sidebar)
    st.session_state.draft_level = "A1"
    st.session_state.draft_book_id = 1
    st.session_state.draft_chapter = 1

    # Bible id inside this DB
    st.session_state.draft_bible_id = db_repo.get_default_bible_id_for_db(st.session_state.db_path)

    # Active starts from draft
    st.session_state.active_language = st.session_state.draft_language
    st.session_state.active_translation_label = st.session_state.draft_translation_label
    st.session_state.active_db_path = st.session_state.db_path
    st.session_state.active_bible_id = st.session_state.draft_bible_id
    st.session_state.active_level = st.session_state.draft_level
    st.session_state.active_book_id = st.session_state.draft_book_id
    st.session_state.active_chapter = st.session_state.draft_chapter

    st.session_state.show_verse_numbers = True
    st.session_state.highlight_vocab = False
    st.session_state.audio_speed = 1.0

    reset_quiz()
    reset_feedback()


def data_dir() -> str:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, "..", "data")

def on_draft_language_change():
    catalog = build_catalog(data_dir())
    lang = st.session_state.draft_language
    translations = catalog.get(lang, [])
    if not translations:
        return
    st.session_state.draft_translation_label = translations[0]["label"]
    on_draft_translation_change()

def on_draft_translation_change():
    catalog = build_catalog(data_dir())

    lang = st.session_state.get("draft_language")
    translations = catalog.get(lang, [])
    if not translations:
        return

    label = st.session_state.get("draft_translation_label")
    labels = [t["label"] for t in translations]
    if label not in labels:
        label = labels[0]
        st.session_state.draft_translation_label = label

    selected = next(t for t in translations if t["label"] == label)
    new_db_path = selected["db_path"]

    if st.session_state.get("db_path") == new_db_path:
        return

    st.session_state.db_path = new_db_path
    ...

    # Get the bible_id inside this split DB (usually 1 bible row)
    # Use your split-db helper (recommended)
    bible_id = db_repo.get_default_bible_id_for_db(new_db_path)
    st.session_state.draft_bible_id = bible_id

    # Reset book/chapter to valid defaults for this DB
    books = db_repo.get_books_for_language(new_db_path, lang)
    if books:
        st.session_state.draft_book_id = int(books[0]["id"])
    else:
        st.session_state.draft_book_id = 1

    st.session_state.draft_chapter = 1

    # Now clamp chapter based on available chapters for the selected level/book
    # (This uses your existing logic if you have it)
    if "on_draft_bible_level_book_change" in globals():
        on_draft_bible_level_book_change()
    else:
        # Minimal fallback clamp if you don't have that helper in state.py
        if bible_id is not None:
            chapters = db_repo.get_available_chapters(
                new_db_path,
                int(bible_id),
                st.session_state.get("draft_level", "A1"),
                int(st.session_state.draft_book_id),
            )
            if chapters:
                st.session_state.draft_chapter = int(chapters[0])

def on_draft_bible_level_book_change():
    db_path = st.session_state.db_path
    bible_id = st.session_state.draft_bible_id
    level = st.session_state.draft_level
    book_id = st.session_state.draft_book_id

    # Guard: don’t query until bible_id exists
    if bible_id is None:
        st.session_state.draft_chapter = 1
        return

    chapters = db_repo.get_available_chapters(db_path, int(bible_id), level, int(book_id))
    # Guard: if no chapters, keep it at 1
    if not chapters:
        st.session_state.draft_chapter = 1
        return

    st.session_state.draft_chapter = db_repo.clamp_to_available_chapter(
        chapters, int(st.session_state.draft_chapter)
    )


def on_draft_book_change():
    on_draft_bible_level_book_change()


def apply_load():
    st.session_state.active_language = st.session_state.draft_language
    st.session_state.active_translation_label = st.session_state.draft_translation_label
    st.session_state.active_db_path = st.session_state.db_path
    st.session_state.active_bible_id = st.session_state.draft_bible_id
    st.session_state.active_level = st.session_state.draft_level
    st.session_state.active_book_id = st.session_state.draft_book_id
    st.session_state.active_chapter = st.session_state.draft_chapter

    reset_quiz()
    reset_feedback()


def go_next_chapter():
    db_path = st.session_state.active_db_path
    bible_id = st.session_state.active_bible_id
    level = st.session_state.active_level
    book_id = st.session_state.active_book_id

    # Guard: if not ready, do nothing (prevents crash)
    if bible_id is None:
        return

    chapters = db_repo.get_available_chapters(db_path, int(bible_id), level, int(book_id))
    if not chapters:
        return

    cur = int(st.session_state.active_chapter)
    if cur not in chapters:
        st.session_state.active_chapter = chapters[0]
    else:
        idx = chapters.index(cur)
        if idx < len(chapters) - 1:
            st.session_state.active_chapter = chapters[idx + 1]

    reset_quiz()
    reset_feedback()


def go_prev_chapter():
    db_path = st.session_state.active_db_path
    bible_id = st.session_state.active_bible_id
    level = st.session_state.active_level
    book_id = st.session_state.active_book_id

    if bible_id is None:
        return

    chapters = db_repo.get_available_chapters(db_path, int(bible_id), level, int(book_id))
    if not chapters:
        return

    cur = int(st.session_state.active_chapter)
    if cur not in chapters:
        st.session_state.active_chapter = chapters[0]
    else:
        idx = chapters.index(cur)
        if idx > 0:
            st.session_state.active_chapter = chapters[idx - 1]

    reset_quiz()
    reset_feedback()


def on_active_book_change():
    db_path = st.session_state.active_db_path
    bible_id = st.session_state.active_bible_id
    level = st.session_state.active_level
    book_id = st.session_state.active_book_id

    if bible_id is None:
        st.session_state.active_chapter = 1
        reset_quiz()
        reset_feedback()
        return

    chapters = db_repo.get_available_chapters(db_path, int(bible_id), level, int(book_id))
    if not chapters:
        st.session_state.active_chapter = 1
    else:
        st.session_state.active_chapter = db_repo.clamp_to_available_chapter(
            chapters, int(st.session_state.active_chapter)
        )

    reset_quiz()
    reset_feedback()


def on_active_chapter_change():
    reset_quiz()
    reset_feedback()


def quiz_key():
    return f"{st.session_state.active_bible_id}:{st.session_state.active_level}:" \
           f"{st.session_state.active_book_id}:{st.session_state.active_chapter}"


def reset_quiz():
    st.session_state.quiz_key = None
    st.session_state.quiz_questions = []
    st.session_state.quiz_index = 0
    st.session_state.quiz_correct = 0
    st.session_state.quiz_incorrect = 0
    st.session_state.quiz_show_hint = False
    st.session_state.quiz_show_explanation = False
    st.session_state.quiz_last_choice = None
    st.session_state.quiz_last_was_correct = None


def reset_feedback():
    st.session_state.feedback_key = None
    st.session_state.feedback_vote = None
    st.session_state.feedback_comment = ""
    st.session_state.feedback_submitted = False
