# app/state.py
import os, streamlit as st
from app import db_repo


def init_state():
    if st.session_state.get("initialized"):
        return

    st.session_state.initialized = True
    st.session_state.db_path = os.getenv(
    "BIBLE_DB_PATH", "data/multi_bibles.db"
        )
    
    # Draft (sidebar)
    st.session_state.draft_language = "English"
    st.session_state.draft_bible_id = None
    st.session_state.draft_level = "A1"
    st.session_state.draft_book_id = 1
    st.session_state.draft_chapter = 1

    # Active (main view)
    st.session_state.active_language = "English"
    st.session_state.active_bible_id = None
    st.session_state.active_level = "A1"
    st.session_state.active_book_id = 1
    st.session_state.active_chapter = 1

    # Reading toggles
    st.session_state.show_verse_numbers = True
    st.session_state.highlight_vocab = False

    # Audio
    st.session_state.audio_speed = 1.0
    st.session_state.kw_selected = None


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


def apply_load():
    st.session_state.active_language = st.session_state.draft_language
    st.session_state.active_bible_id = st.session_state.draft_bible_id
    st.session_state.active_level = st.session_state.draft_level
    st.session_state.active_book_id = st.session_state.draft_book_id
    st.session_state.active_chapter = st.session_state.draft_chapter

    reset_quiz()
    reset_feedback()


def go_next_chapter():
    """Next chapter within available chapters for the active (bible, level, book)."""
    db_path = st.session_state.db_path
    bible_id = st.session_state.active_bible_id
    level = st.session_state.active_level
    book_id = st.session_state.active_book_id

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
        # else: do nothing (end of book)

    reset_quiz()
    reset_feedback()


def go_prev_chapter():
    """Previous chapter within available chapters for the active (bible, level, book)."""
    db_path = st.session_state.db_path
    bible_id = st.session_state.active_bible_id
    level = st.session_state.active_level
    book_id = st.session_state.active_book_id

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
        # else: do nothing (start of book)

    reset_quiz()
    reset_feedback()

def on_active_book_change():
    """When active book changes via header dropdown, clamp chapter and reset quiz/feedback."""
    db_path = st.session_state.db_path
    bible_id = st.session_state.active_bible_id
    level = st.session_state.active_level
    book_id = st.session_state.active_book_id

    chapters = db_repo.get_available_chapters(db_path, int(bible_id), level, int(book_id))
    st.session_state.active_chapter = db_repo.clamp_to_available_chapter(chapters, int(st.session_state.active_chapter))

    reset_quiz()
    reset_feedback()


def on_active_chapter_change():
    """When active chapter changes via header dropdown, reset quiz/feedback."""
    reset_quiz()
    reset_feedback()