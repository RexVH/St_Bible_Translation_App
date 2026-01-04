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
      - Your schema dict: {"schema_version":..., "meta":..., "vocab":[...], ...}
      - list[dict]
      - dict with list under common keys
    """
    if not vocab_json:
        return []

    if isinstance(vocab_json, list):
        return [x for x in vocab_json if isinstance(x, dict)]

    if isinstance(vocab_json, dict):
        # Your actual schema uses "vocab"
        val = vocab_json.get("vocab")
        if isinstance(val, list):
            return [x for x in val if isinstance(x, dict)]

        # Fallback keys
        for key in ("entries", "items", "words", "word_list", "data"):
            val = vocab_json.get(key)
            if isinstance(val, list):
                return [x for x in val if isinstance(x, dict)]

    return []


def _extract_vocab_fields(entry: Dict[str, Any]) -> Dict[str, Optional[str]]:
    """
    Extract fields from one vocab entry:
      - headword
      - lemma
      - pos
      - gloss_simple (fallbacks)
      - example.text
    """
    headword = None
    for k in ("headword", "word", "term", "lemma"):
        v = entry.get(k)
        if isinstance(v, str) and v.strip():
            headword = v.strip()
            break

    lemma = entry.get("lemma")
    if isinstance(lemma, str):
        lemma = lemma.strip()
        if not lemma:
            lemma = None
    else:
        lemma = None

    pos = entry.get("pos")
    if isinstance(pos, str):
        pos = pos.strip()
        if not pos:
            pos = None
    else:
        pos = None

    gloss = None
    for k in ("gloss_simple", "gloss", "definition", "meaning", "translation", "sense"):
        v = entry.get(k)
        if isinstance(v, str) and v.strip():
            gloss = v.strip()
            break

    # Sometimes gloss is nested
    if gloss is None:
        for k in ("definitions", "meanings", "translations"):
            v = entry.get(k)
            if isinstance(v, list) and v:
                for item in v:
                    if isinstance(item, str) and item.strip():
                        gloss = item.strip()
                        break
                    if isinstance(item, dict):
                        for kk in ("gloss", "definition", "meaning", "translation", "text"):
                            vv = item.get(kk)
                            if isinstance(vv, str) and vv.strip():
                                gloss = vv.strip()
                                break
                    if gloss:
                        break
            if gloss:
                break

    # Example text
    example = None
    ex = entry.get("example")
    if isinstance(ex, dict):
        txt = ex.get("text")
        if isinstance(txt, str) and txt.strip():
            example = txt.strip()
    elif isinstance(ex, str) and ex.strip():
        example = ex.strip()

    return {
        "headword": headword,
        "lemma": lemma,
        "pos": pos,
        "gloss": gloss,
        "example": example,
    }


def _popover_vocab_details(data: Dict[str, Optional[str]]) -> None:
    """
    Popover body: gloss, lemma (if different), POS, example.
    """
    hw = data.get("headword") or ""
    lemma = data.get("lemma")
    pos = data.get("pos")
    gloss = data.get("gloss")
    example = data.get("example")

    if gloss and gloss.strip():
        st.markdown(f"**{gloss.strip()}**")
    else:
        st.caption("No gloss available.")

    # Lemma only if present + different (avoids noise like make/make)
    if lemma and lemma.strip() and lemma.strip().lower() != hw.strip().lower():
        st.markdown(f"- **Lemma:** {lemma.strip()}")

    if pos and pos.strip():
        st.markdown(f"- **PoS:** {pos.strip()}")

    if example and example.strip():
        st.markdown(f"_Example:_ {example.strip()}")


def render_key_words_strip(
    *,
    vocab_json: Any,
    title: str,
    limit: int = 10,
    per_row: int = 5,
    state_key_selected: str = "kw_selected",
) -> None:
    """
    Renders the first N key words as pill-like buttons (popover).
    """
    entries = _extract_entries(vocab_json)

    words: List[Dict[str, Optional[str]]] = []
    for e in entries:
        data = _extract_vocab_fields(e)
        if not data.get("headword"):
            continue
        words.append(data)
        if len(words) >= limit:
            break

    if not words:
        return

    st.markdown(f"**{title}**")

    # Initialize selected state (kept for compatibility with your earlier approach)
    if state_key_selected not in st.session_state:
        st.session_state[state_key_selected] = None

    # Render in rows
    for i in range(0, len(words), per_row):
        row = words[i : i + per_row]
        cols = st.columns(len(row))
        for data, c in zip(row, cols):
            hw = data.get("headword") or ""
            pos = data.get("pos") or ""
            label = f"{hw} ({pos})" if pos else hw

            with c:
                with st.popover(label, use_container_width=True):
                    _popover_vocab_details(data)


def render_vocab_section(
    *,
    vocab_json: Any,
    title: str,
    enable_search: bool = True,
    columns: int = 3,
    state_key_query: str = "vocab_query",
) -> None:
    """
    Full vocab display intended for AFTER the verses.
    Compact grid + popovers, optional search.
    Popover shows: gloss + lemma + pos + example
    """
    entries = _extract_entries(vocab_json)
    if not entries:
        st.caption("No vocabulary found.")
        return

    rows: List[Dict[str, Optional[str]]] = []
    for e in entries:
        data = _extract_vocab_fields(e)
        if not data.get("headword"):
            continue
        rows.append(data)

    if not rows:
        st.caption("No vocabulary found.")
        return

    # Optional search
    q = ""
    if enable_search:
        if state_key_query not in st.session_state:
            st.session_state[state_key_query] = ""
        q = (
            st.text_input(
                "",
                key=state_key_query,
                placeholder=title + "…",
                label_visibility="collapsed",
            )
            .strip()
            .lower()
        )

    if q:
        filtered: List[Dict[str, Optional[str]]] = []
        for d in rows:
            hay = " ".join(
                [
                    d.get("headword") or "",
                    d.get("lemma") or "",
                    d.get("pos") or "",
                    d.get("gloss") or "",
                    d.get("example") or "",
                ]
            ).lower()
            if q in hay:
                filtered.append(d)
        rows = filtered

    if not rows:
        st.caption("No matches.")
        return

    # Grid
    columns = max(1, int(columns))
    cols = st.columns(columns)

    for idx, data in enumerate(rows):
        hw = data.get("headword") or ""
        pos = data.get("pos") or ""
        label = f"{hw} ({pos})" if pos else hw

        with cols[idx % columns]:
            with st.popover(label, use_container_width=True):
                _popover_vocab_details(data)
