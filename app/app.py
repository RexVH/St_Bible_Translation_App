# app/app.py
import streamlit as st

from app.state import (
    init_state,
    apply_load,
    go_next_chapter,
    go_prev_chapter,
    on_draft_language_change,
    on_draft_bible_level_book_change,
    on_draft_book_change,
    on_active_book_change,
    on_active_chapter_change,
)

from app.i18n import t
from app import db_repo
from app.components.audio import render_audio_player
from app.components.vocab import render_key_words_strip
from app.components.text import render_text_block


DEV = False

def _apply_active_book_label(book_options: dict):
    """
    Maps the selected label to active_book_id and triggers on_active_book_change().
    """
    label = st.session_state.get("_active_book_label")
    if label in book_options:
        st.session_state.active_book_id = int(book_options[label])
    on_active_book_change()

def _apply_draft_bible_label(bible_options: dict):
    label = st.session_state.get("_draft_bible_label")
    if label in bible_options:
        st.session_state.draft_bible_id = int(bible_options[label])
    on_draft_bible_level_book_change()


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

        # Ensure the label key is aligned to the current bible id
        st.session_state["_draft_bible_label"] = labels[idx]

        st.selectbox(
            t(st.session_state, "bible"),
            labels,
            index=idx,
            key="_draft_bible_label",
            on_change=lambda: _apply_draft_bible_label(bible_options),
        )

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

        st.session_state["_active_book_label"] = book_labels[book_idx]

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
db_path = st.session_state.db_path

# Resolve display names from DB (localized where applicable)
if st.session_state.active_bible_id is None:
    st.error("No Bible is available for the current language selection. Choose a different language in the sidebar.")
    st.stop()

bible_name = db_repo.get_bible_display_name(db_path, int(st.session_state.active_bible_id)) if st.session_state.active_bible_id else "—"
book_name = db_repo.get_book_name(db_path, st.session_state.active_language, int(st.session_state.active_book_id)) or f"Book {st.session_state.active_book_id}"
chapter_num = int(st.session_state.active_chapter)

# Orientation header (localized by content + UI strings)
st.markdown(f"## {book_name} {chapter_num} — {bible_name} — {st.session_state.active_level}")

# Hero block (DB-driven, safe if missing)
meta = None
if st.session_state.active_bible_id is not None:
    meta = db_repo.get_chapter_meta(
        db_path,
        int(st.session_state.active_bible_id),
        st.session_state.active_level,
        int(st.session_state.active_book_id),
        int(st.session_state.active_chapter),
    )

if meta:
    # One-line summary as headline
    one_line = meta.get("summary_one_line") or ""
    if one_line.strip():
        st.markdown(f"### {one_line}")

    # Image (if present)
    img_url = meta.get("image_url")
    if img_url:
        c_img, c_btn = st.columns([6, 1])
        with c_img:
            st.image(img_url, use_container_width=True)  # height control later
        with c_btn:
            if st.button(t(st.session_state, "view_image")):
                # Streamlit dialog/modal supported in recent versions
                try:
                    with st.dialog(one_line or f"{book_name} {chapter_num}"):
                        st.image(img_url, use_container_width=True)
                except Exception:
                    st.info("Modal not available in this Streamlit version.")
    # Summary paragraph always visible
    para = meta.get("summary_paragraph") or ""
    if para.strip():
        st.write(para)

else:
    st.warning("No chapter metadata found for this selection (yet).")

# --- AUDIO BLOCK ---
audio_url = meta.get("audio_url") if meta else None
render_audio_player(
    audio_url=audio_url,
    speed_key="audio_speed",
    label=t(st.session_state, "audio"),
    speed_label=t(st.session_state, "audio_speed"),
    download_label=t(st.session_state, "download_mp3"),
)

st.divider()

# Navigation + quick settings row
nav1, nav2, nav3, nav4 = st.columns([1, 3, 3, 1])

with nav1:
    st.button(t(st.session_state, "nav_prev"), on_click=go_prev_chapter)

# Active book dropdown (localized names)
books = db_repo.get_books_for_language(db_path, st.session_state.active_language)
book_options = {b["name"]: int(b["id"]) for b in books}
book_labels = list(book_options.keys())
book_ids = list(book_options.values())

# Guard: if active_book_id not valid, clamp to first
cur_book = int(st.session_state.active_book_id)
if book_ids and cur_book not in book_ids:
    st.session_state.active_book_id = book_ids[0]
    cur_book = book_ids[0]

with nav2:
    if book_labels:
        book_idx = book_ids.index(cur_book)
        st.selectbox(
            t(st.session_state, "book"),
            book_labels,
            index=book_idx,
            key="_active_book_label",
            on_change=lambda: _apply_active_book_label(book_options),
        )
    else:
        st.selectbox(t(st.session_state, "book"), [book_name], disabled=True)

# Active chapter dropdown depends on active selection
chapters = []
if st.session_state.active_bible_id is not None:
    chapters = db_repo.get_available_chapters(
        db_path,
        int(st.session_state.active_bible_id),
        st.session_state.active_level,
        int(st.session_state.active_book_id),
    )
if not chapters:
    chapters = [1]

# Clamp active chapter to available list
st.session_state.active_chapter = db_repo.clamp_to_available_chapter(chapters, int(st.session_state.active_chapter))
cur_ch = int(st.session_state.active_chapter)

with nav3:
    chap_idx = chapters.index(cur_ch)
    st.selectbox(
        t(st.session_state, "chapter"),
        chapters,
        index=chap_idx,
        key="active_chapter",
        on_change=on_active_chapter_change,
    )

with nav4:
    st.button(t(st.session_state, "nav_next"), on_click=go_next_chapter)

# Quick toggles
tog1, tog2 = st.columns([1, 1])
with tog1:
    st.checkbox(t(st.session_state, "show_verses"), key="show_verse_numbers")
with tog2:
    st.checkbox(t(st.session_state, "highlight_vocab"), key="highlight_vocab")

st.divider()
if DEV:
    st.info("Header + hero are now DB-driven...")

# --- VOCAB DISPLAY AND KEY WORDS STRIP (first 10) ---
vocab_json = db_repo.get_vocab_json(
    db_path,
    int(st.session_state.active_bible_id),
    st.session_state.active_level,
    int(st.session_state.active_book_id),
    int(st.session_state.active_chapter),
)

render_key_words_strip(
    vocab_json=vocab_json,
    title=t(st.session_state, "key_words"),
    limit=10,
    per_row=5,
    state_key_selected="kw_selected",
)

st.divider() # ---- End Vocab

# --- START Controls (wherever you’re keeping reader controls; v1 can live above the text)
show_verse_numbers = st.toggle(
    t(st.session_state, "show_verse_numbers"),
    value=st.session_state.get("show_verse_numbers", True),
    key="show_verse_numbers",
)

highlight_vocab = st.toggle(
    t(st.session_state, "highlight_vocab"),
    value=st.session_state.get("highlight_vocab", False),
    key="highlight_vocab",
)

# --- Data fetch
verses = db_repo.get_verses(
    bible_id=st.session_state.active_bible_id,
    book_id=st.session_state.active_book_id,
    chapter=st.session_state.active_chapter,
    level=st.session_state.active_level,
)

vocab_json = db_repo.get_vocab_json(
    bible_id=st.session_state.active_bible_id,
    book_id=st.session_state.active_book_id,
    chapter=st.session_state.active_chapter,
    level=st.session_state.active_level,
)

teaching_notes = db_repo.get_teaching_notes(
    bible_id=st.session_state.active_bible_id,
    book_id=st.session_state.active_book_id,
    chapter=st.session_state.active_chapter,
    level=st.session_state.active_level,
)

notes_by_verse_start = db_repo.group_teaching_notes_by_verse_start(teaching_notes)

# --- Render
render_text_block(
    verses=verses,
    vocab_json=vocab_json,
    notes_by_verse_start=notes_by_verse_start,
    show_verse_numbers=show_verse_numbers,
    highlight_vocab=highlight_vocab,
)


