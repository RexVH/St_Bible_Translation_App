# app/components/vocab.py
from __future__ import annotations

import streamlit as st
from typing import Any, Dict, List, Optional, Tuple


def _truncate_one_line(s: str, max_len: int = 90) -> str:
    s = (s or "").strip().replace("\n", " ")
    if len(s) <= max_len:
        return s
    return s[: max_len - 1].rstrip() + "…"


def _extract_entries(vocab_json: Any) -> List[Dict[str, Any]]:
    """
    Attempts to normalize vocab_json into a list of entry dicts.
    Supports:
      - list[dict]
      - dict with list under common keys
    """
    if not vocab_json:
        return []

    if isinstance(vocab_json, list):
        return [x for x in vocab_json if isinstance(x, dict)]

    if isinstance(vocab_json, dict):
        for key in ("vocab", "entries", "items", "words", "word_list", "data"):
            val = vocab_json.get(key)
            if isinstance(val, list):
                return [x for x in val if isinstance(x, dict)]

    return []


def _get_headword_and_gloss(entry: Dict[str, Any]) -> Tuple[Optional[str], Optional[str]]:
    """
    Attempts to extract a headword + gloss from a vocab entry.
    """
    headword = None
    for k in ("headword", "word", "lemma", "term"):
        v = entry.get(k)
        if isinstance(v, str) and v.strip():
            headword = v.strip()
            break

    gloss = None
    for k in ("gloss", "definition", "meaning", "translation", "sense"):
        v = entry.get(k)
        if isinstance(v, str) and v.strip():
            gloss = v.strip()
            break

    # Sometimes gloss is nested
    if gloss is None:
        for k in ("definitions", "meanings", "translations"):
            v = entry.get(k)
            if isinstance(v, list) and v:
                # use first string-ish
                for item in v:
                    if isinstance(item, str) and item.strip():
                        gloss = item.strip()
                        break
                    if isinstance(item, dict):
                        for kk in ("gloss", "definition", "meaning", "translation"):
                            vv = item.get(kk)
                            if isinstance(vv, str) and vv.strip():
                                gloss = vv.strip()
                                break
                    if gloss:
                        break
            if gloss:
                break

    return headword, gloss


def render_key_words_strip(
    *,
    vocab_json: Any,
    title: str,
    limit: int = 10,
    per_row: int = 5,
    state_key_selected: str = "kw_selected",
) -> None:
    """
    Renders the first N key words as pill-like buttons.
    - Hover tooltip: uses Streamlit `help=...`
    - Click/tap reveal: shows the selected word's gloss under the strip
    """
    entries = _extract_entries(vocab_json)

    words: List[Tuple[str, str]] = []
    for e in entries:
        hw, gloss = _get_headword_and_gloss(e)
        if not hw:
            continue
        gloss = gloss or ""
        words.append((hw, gloss))
        if len(words) >= limit:
            break

    if not words:
        return

    st.markdown(f"**{title}**")

    # Initialize selected state
    if state_key_selected not in st.session_state:
        st.session_state[state_key_selected] = None

    # Render in rows
    for i in range(0, len(words), per_row):
        row = words[i : i + per_row]
        cols = st.columns(len(row))
        for (hw, gloss), c in zip(row, cols):
            with c:
                # Use button with help tooltip to simulate "hover gloss"
                tooltip = _truncate_one_line(gloss) if gloss else None
                clicked = st.button(
                    hw,
                    key=f"kw_{i}_{hw}",
                    help=tooltip,
                    use_container_width=True,
                )
                if clicked:
                    # Toggle selection
                    if st.session_state[state_key_selected] == hw:
                        st.session_state[state_key_selected] = None
                    else:
                        st.session_state[state_key_selected] = hw

    # Click/tap reveal for mobile (and also useful on desktop)
    selected = st.session_state.get(state_key_selected)
    if selected:
        # find gloss
        gloss = ""
        for hw, g in words:
            if hw == selected:
                gloss = g or ""
                break

        if gloss.strip():
            st.caption(f"**{selected}** — {_truncate_one_line(gloss, 220)}")
        else:
            st.caption(f"**{selected}**")
