# app/app.py
import streamlit as st

from app.state import init_state, apply_load, go_next_chapter, go_prev_chapter
from app.i18n import t

st.set_page_config(layout="wide")
init_state()

from app.state import (
    init_state,
    apply_load,
    go_next_chapter,
    go_prev_chapter,
    on_draft_language_change,
    on_draft_bible_level_book_change,
    on_draft_book_change,
)
from app.i18n import t
from app import db_repo

st.set_page_config(layout="wide")
init_state()

db_path = st.session_state.db_path

# --- SIDEBAR ---
with st.sidebar:
    st.header(t(st.session_state, "selection"))

    # Language
    languages = db_repo.get_languages(db_path)
    st.selectbox(
        t(st.session_state, "language"),
        languages,
        key="draft_language",
        on_change=on_draft_language_change,
    )

    # Bible (filtered by language)
    bibles = db_repo.get_bibles_for_language(db_path, st.session_state.draft_language)
    bible_options = {f'{b["name"]} ({b.get("code","")})'.strip(): int(b["id"]) for b in bibles}
    if not bible_options:
        st.warning("No bibles available for this language in the DB.")
        st.session_state.draft_bible_id = None
    else:
        # pick index based on current draft_bible_id
        labels = list(bible_options.keys())
        ids = list(bible_options.values())
        cur_id = st.session_state.draft_bible_id
        if cur_id not in ids:
            st.session_state.draft_bible_id = ids[0]
            cur_id = ids[0]
        idx = ids.index(cur_id)

        st.selectbox(
            t(st.session_state, "bible"),
            labels,
            index=idx,
            key="_draft_bible_label",
            on_change=on_draft_bible_level_book_change,
        )
        # map label -> id into the real state key
        st.session_state.draft_bible_id = bible_options[st.session_state._draft_bible_label]

    # Level
    st.selectbox(
        t(st.session_state, "level"),
        ["A1", "A2", "B1", "B2", "Source"],
        key="draft_level",
        on_change=on_draft_bible_level_book_change,
    )

    # Book (localized names from DB)
    books = db_repo.get_books_for_language(db_path, st.session_state.draft_language)
    book_options = {b["name"]: int(b["id"]) for b in books}  # name already localized
    if not book_options:
        st.warning("No books found for this language in the DB.")
        st.session_state.draft_book_id = 1
    else:
        book_labels = list(book_options.keys())
        book_ids = list(book_options.values())
        cur_book = int(st.session_state.draft_book_id)
        if cur_book not in book_ids:
            st.session_state.draft_book_id = book_ids[0]
            cur_book = book_ids[0]
        book_idx = book_ids.index(cur_book)

        st.selectbox(
            t(st.session_state, "book"),
            book_labels,
            index=book_idx,
            key="_draft_book_label",
            on_change=on_draft_book_change,
        )
        st.session_state.draft_book_id = book_options[st.session_state._draft_book_label]

    # Chapter (depends on bible/level/book)
    if st.session_state.draft_bible_id is None:
        st.session_state.draft_chapter = 1
        st.selectbox(t(st.session_state, "chapter"), [1], key="draft_chapter", disabled=True)
    else:
        chapters = db_repo.get_available_chapters(
            db_path,
            int(st.session_state.draft_bible_id),
            st.session_state.draft_level,
            int(st.session_state.draft_book_id),
        )
        if not chapters:
            chapters = [1]
        # clamp draft_chapter in case upstream changed
        st.session_state.draft_chapter = db_repo.clamp_to_available_chapter(
            chapters, int(st.session_state.draft_chapter)
        )
        chap_idx = chapters.index(int(st.session_state.draft_chapter))
        st.selectbox(
            t(st.session_state, "chapter"),
            chapters,
            index=chap_idx,
            key="draft_chapter",
        )

    # Load button (commits draft -> active, and triggers UI language switch)
    if st.button(t(st.session_state, "load")):
        apply_load()
        st.rerun()

    st.divider()

    # Reference section (placeholder links for now)
    st.subheader(t(st.session_state, "reference"))
    if st.session_state.active_language == "German":
        st.link_button("Duden", "https://www.duden.de/")
        st.link_button("Wiktionary", "https://de.wiktionary.org/")
    else:
        st.link_button("Merriam-Webster", "https://www.merriam-webster.com/")
        st.link_button("Wiktionary", "https://en.wiktionary.org/")

    st.link_button(t(st.session_state, "contact_dev"), "mailto:rex@ninefourecho.com")

# --- MAIN ---
st.title(
    f"{st.session_state.active_language} · "
    f"{st.session_state.active_level} · "
    f"Book {st.session_state.active_book_id}, "
    f"Chapter {st.session_state.active_chapter}"
)

col1, col2, col3 = st.columns([1, 3, 1])

with col1:
    st.button(t(st.session_state, "nav_prev"), on_click=go_prev_chapter)

with col3:
    st.button(t(st.session_state, "nav_next"), on_click=go_next_chapter)

st.checkbox(
    t(st.session_state, "show_verses"),
    key="show_verse_numbers",
)
st.checkbox(
    t(st.session_state, "highlight_vocab"),
    key="highlight_vocab",
)

st.info("UI skeleton running. Ready to wire DB + components.")
