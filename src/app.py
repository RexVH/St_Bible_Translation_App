# app/app.py
import streamlit as st
st.set_page_config(layout="wide")

from state import (
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
from i18n import t
import db_repo
from components.image import banner_with_overlay
from components.audio import render_audio_player
from components.vocab import render_key_words_strip, render_vocab_section
from components.text import render_text_block

init_state()

db_path = st.session_state.db_path

# --- SIDEBAR ---
with st.sidebar:
    st.header(t(st.session_state, "selection"))
    # --- Language ---
    languages = db_repo.get_languages(db_path)
    if not languages:
        st.error("No languages available.")
        st.stop()

    if st.session_state.get("draft_language") not in languages:
        st.session_state.draft_language = languages[0]

    st.selectbox(
        t(st.session_state, "language"),
        languages,
        key="draft_language",
        on_change=on_draft_language_change,
    )

    # --- Bible ---
    bibles = db_repo.get_bibles_for_language(db_path, st.session_state.draft_language)
    bible_id_to_label = {int(b["id"]): f'{b["name"]} ({b.get("code","")})'.strip() for b in bibles}
    bible_ids = list(bible_id_to_label.keys())

    if not bible_ids:
        st.warning("No bibles available for this language.")
        st.session_state.draft_bible_id = None
    else:
        if st.session_state.get("draft_bible_id") not in bible_ids:
            st.session_state.draft_bible_id = bible_ids[0]

        st.selectbox(
            t(st.session_state, "bible"),
            bible_ids,
            key="draft_bible_id",
            format_func=lambda i: bible_id_to_label.get(i, str(i)),
        )

    # --- Level ---
    LEVELS = ["A1", "A2", "B1", "B2", "Source"]
    if st.session_state.get("draft_level") not in LEVELS:
        st.session_state.draft_level = "A1"
    st.selectbox(t(st.session_state, "level"), LEVELS, key="draft_level")

    # --- Book ---
    books = db_repo.get_books_for_language(db_path, st.session_state.draft_language)
    book_id_to_label = {int(b["id"]): b["name"] for b in books}
    book_ids = list(book_id_to_label.keys()) or [1]

    if st.session_state.get("draft_book_id") not in book_ids:
        st.session_state.draft_book_id = book_ids[0]

    st.selectbox(
        t(st.session_state, "book"),
        book_ids,
        key="draft_book_id",
        format_func=lambda i: book_id_to_label.get(i, str(i)),
    )

    # --- Chapter ---
    if st.session_state.draft_bible_id is None:
        chapters = [1]
    else:
        chapters = db_repo.get_available_chapters(
            db_path,
            int(st.session_state.draft_bible_id),
            st.session_state.draft_level,
            int(st.session_state.draft_book_id),
        ) or [1]

    cur_ch = int(st.session_state.get("draft_chapter", 1))
    if cur_ch not in chapters:
        st.session_state.draft_chapter = chapters[0]

    st.selectbox(
        t(st.session_state, "chapter"),
        chapters,
        key="draft_chapter",
        on_change=apply_load,
    )

    if st.button(t(st.session_state, "load"), key="load_btn"):
        apply_load()

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
    one_line = meta.get("summary_one_line") or ""

    img_url = meta.get("image_url")
    if img_url:
        html_text = banner_with_overlay(
            image_ref=img_url,
            title=f"{book_name} {chapter_num}",
            subtitle=one_line,
            banner_height_px=260,
        )
        import streamlit.components.v1 as comp
        comp.html(html_text, height=280)

    if st.button(t(st.session_state, "view_image")):
        @st.dialog(f"{book_name} {chapter_num}")
        def _dlg():
            st.image(img_url, width='stretch', caption="Right-click to open in a new tab or window.")
        _dlg()

    para = meta.get("summary_paragraph") or ""
    if para.strip():
        st.write(para)
else:
    st.warning("No chapter metadata found for this selection (yet).")

st.divider()  # audio player

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

with nav2:
    books = db_repo.get_books_for_language(db_path, st.session_state.active_language)
    active_book_id_to_label = {int(b["id"]): b["name"] for b in books}

    if not active_book_id_to_label:
        st.selectbox(t(st.session_state, "book"), [book_name], disabled=True)
    else:
        active_book_ids = list(active_book_id_to_label.keys())
        cur = st.session_state.get("active_book_id")
        if cur not in active_book_ids:
            st.session_state.active_book_id = active_book_ids[0]

        st.selectbox(
            t(st.session_state, "book"),
            active_book_ids,
            key="active_book_id",
            format_func=lambda i: active_book_id_to_label.get(i, str(i)),
            on_change=on_active_book_change,
        )

with nav3:
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

    st.session_state.setdefault("active_chapter", chapters[0])

    if st.session_state.active_chapter not in chapters:
        st.session_state.active_chapter = db_repo.clamp_to_available_chapter(
            chapters, st.session_state.active_chapter
        )

    st.selectbox(
        t(st.session_state, "chapter"),
        chapters,
        key="active_chapter",
        on_change=on_active_chapter_change,
    )

with nav4:
    st.button(t(st.session_state, "nav_next"), on_click=go_next_chapter)

st.divider()

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

st.divider()  # ---- End Vocab preview

# --- START Controls (reader controls above text)
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
    db_path=st.session_state.db_path,
    bible_id=st.session_state.active_bible_id,
    book_id=st.session_state.active_book_id,
    chapter=st.session_state.active_chapter,
    level=st.session_state.active_level,
)

teaching_notes = db_repo.get_teaching_notes(
    db_path=st.session_state.db_path,
    bible_id=st.session_state.active_bible_id,
    book_id=st.session_state.active_book_id,
    chapter=st.session_state.active_chapter,
    level=st.session_state.active_level,
)

notes_by_verse_start = db_repo.group_teaching_notes_by_verse_start(teaching_notes)

# --- Render verses (and notes / highlighting)
render_text_block(
    verses=verses,
    vocab_json=vocab_json,
    notes_by_verse_start=notes_by_verse_start,
    show_verse_numbers=show_verse_numbers,
    highlight_vocab=highlight_vocab,
)

# ✅ Vocabulary section AFTER the verse display (now shows lemma + pos + example)
st.divider()
with st.expander(t(st.session_state, "vocabulary"), expanded=False):
    render_vocab_section(
        vocab_json=vocab_json,
        title=t(st.session_state, "vocabulary"),
        enable_search=True,
        columns=3,
        state_key_query="vocab_query",
    )

st.info("How does this look now now?")
