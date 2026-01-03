# app/components/text.py
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

import streamlit as st


# ----------------------------
# Styling
# ----------------------------

_TEXT_CSS = """
<style>
.bible-text { line-height: 1.75; font-size: 1.03rem; }
.verse-row { display: flex; gap: 0.55rem; align-items: flex-start; padding: 0.15rem 0; }
.verse-num { width: 2.3rem; text-align: right; opacity: 0.65; user-select: none; }
.verse-body { flex: 1; }
.vocab-hl {
  font-weight: 700;
  text-decoration: underline;
  text-underline-offset: 0.18em;
}
.note-chip { opacity: 0.9; font-size: 0.95rem; }
.note-block p { margin: 0.35rem 0; }
.note-label { opacity: 0.7; font-size: 0.85rem; margin-top: 0.35rem; }
</style>
"""


# ----------------------------
# Helpers
# ----------------------------

def _escape_html(s: str) -> str:
    # Minimal escaping for safe HTML rendering via st.markdown(unsafe_allow_html=True)
    return (
        s.replace("&", "&amp;")
         .replace("<", "&lt;")
         .replace(">", "&gt;")
         .replace('"', "&quot;")
         .replace("'", "&#39;")
    )


def _extract_headwords(vocab_json: Optional[Mapping[str, Any]]) -> List[str]:
    """
    Expected vocab_json shape (flexible):
      - {"items": [{"headword": "...", ...}, ...]}
      - [{"headword": "..."}]
      - {"vocab": [{"headword": "..."}]}
    Returns unique headwords in a stable order.
    """
    if not vocab_json:
        return []

    candidates: List[Any] = []
    if isinstance(vocab_json, list):
        candidates = vocab_json
    elif isinstance(vocab_json, dict):
        for key in ("items", "vocab", "words", "entries"):
            if key in vocab_json and isinstance(vocab_json[key], list):
                candidates = vocab_json[key]
                break

    headwords: List[str] = []
    seen = set()
    for item in candidates:
        if isinstance(item, dict):
            hw = item.get("headword") or item.get("lemma") or item.get("word")
        else:
            hw = None
        if isinstance(hw, str):
            hw = hw.strip()
            if hw and hw.lower() not in seen:
                seen.add(hw.lower())
                headwords.append(hw)

    return headwords


@st.cache_data(show_spinner=False)
def _compile_vocab_pattern(headwords: Tuple[str, ...]) -> Optional[re.Pattern]:
    """
    Whole-word matching, case-insensitive, Unicode-aware.
    Sort longest-first to avoid weird overlaps when words share boundaries.
    """
    if not headwords:
        return None

    words = [w.strip() for w in headwords if w and w.strip()]
    if not words:
        return None

    # Longest first helps if you have e.g. "Gott" and "Gottes" (though \b blocks many overlaps)
    words = sorted(set(words), key=len, reverse=True)
    escaped = [re.escape(w) for w in words]

    # Whole-word match:
    # \b is Unicode-aware for letters/digits/underscore; good enough for v1.
    pattern = r"\b(" + "|".join(escaped) + r")\b"
    return re.compile(pattern, flags=re.IGNORECASE | re.UNICODE)


def _highlight_vocab_html(text: str, pat: Optional[re.Pattern]) -> str:
    """
    Returns HTML string (escaped + <span> wrappers).
    """
    safe = _escape_html(text)
    if not pat:
        return safe

    # We need to run regex on the *original* text for indices; but we also need HTML escaping.
    # Simple approach: do regex substitution on original, escaping matched/non-matched chunks manually.
    out_parts: List[str] = []
    last = 0
    for m in pat.finditer(text):
        start, end = m.span()
        if start > last:
            out_parts.append(_escape_html(text[last:start]))
        out_parts.append(f'<span class="vocab-hl">{_escape_html(text[start:end])}</span>')
        last = end
    if last < len(text):
        out_parts.append(_escape_html(text[last:]))

    return "".join(out_parts)


def _get_verse_num(v: Mapping[str, Any]) -> Optional[int]:
    for key in ("verse", "verse_num", "verse_number", "v"):
        val = v.get(key)
        if isinstance(val, int):
            return val
        if isinstance(val, str) and val.isdigit():
            return int(val)
    return None


def _get_verse_text(v: Mapping[str, Any]) -> str:
    for key in ("text", "verse_text", "content"):
        val = v.get(key)
        if isinstance(val, str):
            return val
    return ""


def _render_teaching_notes_popover(notes: Sequence[Mapping[str, Any]]) -> None:
    """
    Option A: a single 📝 popover at verse_start containing all notes that start there.
    """
    # Streamlit >= 1.32-ish has st.popover. If not, fallback to st.expander.
    popover_fn = getattr(st, "popover", None)

    label = "📝"
    if callable(popover_fn):
        with st.popover(label, use_container_width=False):
            st.markdown('<div class="note-block">', unsafe_allow_html=True)
            for i, n in enumerate(notes, start=1):
                primary_change = (n.get("primary_change") or "").strip()
                note = (n.get("note") or "").strip()
                rq = (n.get("reflection_question") or "").strip()

                if len(notes) > 1:
                    st.markdown(f"**Note {i}**")

                if primary_change:
                    st.markdown(f'<div class="note-label">Primary change</div>', unsafe_allow_html=True)
                    st.markdown(primary_change)

                if note:
                    st.markdown(f'<div class="note-label">Teaching note</div>', unsafe_allow_html=True)
                    st.markdown(note)

                if rq:
                    st.markdown(f'<div class="note-label">Reflection question</div>', unsafe_allow_html=True)
                    st.markdown(rq)

                if i < len(notes):
                    st.divider()
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        # Fallback (older Streamlit)
        with st.expander("📝 Teaching notes", expanded=False):
            for i, n in enumerate(notes, start=1):
                primary_change = (n.get("primary_change") or "").strip()
                note = (n.get("note") or "").strip()
                rq = (n.get("reflection_question") or "").strip()

                if len(notes) > 1:
                    st.markdown(f"**Note {i}**")

                if primary_change:
                    st.caption("Primary change")
                    st.write(primary_change)
                if note:
                    st.caption("Teaching note")
                    st.write(note)
                if rq:
                    st.caption("Reflection question")
                    st.write(rq)
                if i < len(notes):
                    st.divider()


# ----------------------------
# Public API
# ----------------------------

def render_text_block(
    *,
    verses: Sequence[Mapping[str, Any]],
    vocab_json: Optional[Mapping[str, Any]] = None,
    notes_by_verse_start: Optional[Mapping[int, Sequence[Mapping[str, Any]]]] = None,
    show_verse_numbers: bool = True,
    highlight_vocab: bool = False,
) -> None:
    """
    Verse-by-verse renderer with:
      - show/hide verse numbers
      - basic whole-word vocab highlighting
      - 📝 teaching notes popover at verse_start (Option A)

    notes_by_verse_start should look like:
      { 2: [note_obj, ...], 7: [note_obj, ...] }
    """
    st.markdown(_TEXT_CSS, unsafe_allow_html=True)
    st.markdown('<div class="bible-text">', unsafe_allow_html=True)

    headwords = tuple(_extract_headwords(vocab_json))
    pat = _compile_vocab_pattern(headwords) if highlight_vocab else None
    notes_by_verse_start = notes_by_verse_start or {}

    for v in verses:
        vn = _get_verse_num(v)
        vt = _get_verse_text(v)

        # Render row with optional verse number + body
        left = ""
        if show_verse_numbers and vn is not None:
            left = f'<div class="verse-num">{vn}</div>'
        else:
            left = '<div class="verse-num"></div>'  # keeps alignment consistent

        # Optional 📝 at verse start
        notes_here = []
        if vn is not None and vn in notes_by_verse_start:
            notes_here = list(notes_by_verse_start.get(vn, []))

        # Render the verse body HTML (with optional highlighting)
        body_html = _highlight_vocab_html(vt, pat) if highlight_vocab else _escape_html(vt)

        # Layout: number column + body + (popover button inline before verse text)
        # We can’t place popover inside raw HTML reliably, so we use Streamlit columns.
        if notes_here:
            c_num, c_icon, c_body = st.columns([0.10, 0.06, 0.84], gap="small")
            with c_num:
                if show_verse_numbers and vn is not None:
                    st.markdown(f'<div class="verse-num">{vn}</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="verse-num"></div>', unsafe_allow_html=True)
            with c_icon:
                _render_teaching_notes_popover(notes_here)
            with c_body:
                st.markdown(f'<div class="verse-body">{body_html}</div>', unsafe_allow_html=True)
        else:
            c_num, c_body = st.columns([0.10, 0.90], gap="small")
            with c_num:
                if show_verse_numbers and vn is not None:
                    st.markdown(f'<div class="verse-num">{vn}</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="verse-num"></div>', unsafe_allow_html=True)
            with c_body:
                st.markdown(f'<div class="verse-body">{body_html}</div>', unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
