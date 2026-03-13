# src/app.py
import json
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
    on_draft_translation_change
)
from i18n import t
import db_repo
from state import data_dir
from components.image import banner_with_overlay
from components.audio import render_audio_player
from components.vocab import render_key_words_strip, render_vocab_section
from components.text import render_text_block
from components.quiz import render_quiz_section 
from components.chat import render_chat_placeholder
from components.feedback import render_feedback_footer
from components.catalog import build_catalog, get_language_display_name

init_state()

# --- SIDEBAR ---
with st.sidebar:
    st.info(t(st.session_state, "startup_instruction"))
    st.header(t(st.session_state, "selection"))
    # --- Language ---
    catalog = build_catalog(data_dir())

    languages = list(catalog.keys())
    if not languages:
        st.error("No .db files found in /data or no valid bibles inside them.")
        st.stop()

    # Draft language
    if st.session_state.get("draft_language") not in languages:
        st.session_state.draft_language = "en" if "en" in languages else languages[0]

    st.selectbox(
        t(st.session_state, "language"),
        languages,
        key="draft_language",
        format_func=get_language_display_name,
        on_change=on_draft_language_change,
    )

    # Translation (sets db_path)
    translations = catalog.get(st.session_state.draft_language, [])
    if not translations:
        st.warning("No translations available for this language.")
        st.stop()

    labels = [t["label"] for t in translations]

    # store the selection by label (or by db_path; either works)
    if st.session_state.get("draft_translation_label") not in labels:
        st.session_state.draft_translation_label = labels[0]

    st.selectbox(
        t(st.session_state, "bible"),   # reuse existing label key
        labels,
        key="draft_translation_label",
        on_change=on_draft_translation_change
    )

    # Resolve selected db_path
    selected = next(x for x in translations if x["label"] == st.session_state.draft_translation_label)
    st.session_state.db_path = selected["db_path"]
    db_path = st.session_state.db_path

    st.session_state.draft_bible_id = db_repo.get_default_bible_id_for_db(db_path)
    if st.session_state.draft_bible_id is None:
        st.warning("No bible row found in this database.")
        st.stop()

    # --- Level ---
    LEVELS = ["A1", "A2", "B1", "B2", "src"]
    if st.session_state.get("draft_level") not in LEVELS:
        st.session_state.draft_level = "A1"
    st.selectbox(
        t(st.session_state, "level"),
        LEVELS,
        key="draft_level",
        format_func=lambda level: "Source" if level == "src" else level,
        on_change=on_draft_bible_level_book_change,
    )

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
        on_change=on_draft_book_change,
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

    st.link_button("Instructions 🤔", "./Instructions")

    # Reference section (placeholder links for now)
    st.subheader(t(st.session_state, "reference"))
    if st.session_state.active_language == "de":
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
nav1, nav2, nav3, nav4 = st.columns([1, 3, 3, 1], vertical_alignment="center")

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

# --- VOCAB DISPLAY AND KEY WORDS STRIP (first 10); prefer vocab_json stored on graded_chapter_meta (new schema)
vocab_json = (meta.get("vocab_json") if meta else None)

# ✅ Decode SQLite TEXT -> dict
if isinstance(vocab_json, (bytes, bytearray)):
    vocab_json = vocab_json.decode("utf-8", errors="replace")

if isinstance(vocab_json, str):
    vocab_json = vocab_json.strip()
    if vocab_json:
        try:
            vocab_json = json.loads(vocab_json)
        except json.JSONDecodeError:
            print("Failed to decode vocab_json as JSON:", vocab_json)
            vocab_json = None
    else:
        vocab_json = None

# Fallback to legacy table lookup if you still have it in some DBs
if not vocab_json:
    try:
        vocab_json = db_repo.get_vocab_json(
            db_path,
            int(st.session_state.active_bible_id),
            st.session_state.active_level,
            int(st.session_state.active_book_id),
            int(st.session_state.active_chapter),
        )
    except Exception:
        vocab_json = None

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
    key="show_verse_numbers",
)

highlight_vocab = st.toggle(
    t(st.session_state, "highlight_vocab"),
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

st.divider()

# --- ✅ QUIZ SECTION ---
quiz_json = meta.get("quiz_json") if meta else None
render_quiz_section(
    quiz_json=quiz_json,
    t=t,
    book_name=book_name,
    chapter_num=chapter_num,
)

# --- ✅ H. CHAT PLACEHOLDER (collapsed) ---
st.divider()
render_chat_placeholder(
    t=t,
    book_name=book_name,
    chapter_num=chapter_num,
    verses=verses,
    vocab_json=vocab_json,
)

# --- ✅ I. FEEDBACK + FOOTER ---
st.divider()
render_feedback_footer(
    t=t,
    book_name=book_name,
    chapter_num=chapter_num,
    bible_name=bible_name,
    level=st.session_state.active_level,
    verses=verses,
)
