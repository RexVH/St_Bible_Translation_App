from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

import streamlit as st


# -----------------------------
# Chat state + helpers (logic)
# -----------------------------
CHAT_ENABLED_DEFAULT = False  # placeholder for now (wire this to your LLM later)


@dataclass(frozen=True)
class ChatScopeKey:
    """A stable per-chapter scope for chat history."""
    bible_id: int
    level: str
    book_id: int
    chapter: int

    def as_str(self) -> str:
        return f"chat:{self.bible_id}:{self.level}:{self.book_id}:{self.chapter}"


def _safe_tr(t: Callable, ss: Dict[str, Any], key: str, default: str) -> str:
    """
    Calls your i18n `t(session_state, key)` but falls back if the key is missing
    (common behavior is returning the key itself).
    """
    try:
        out = t(ss, key)
        if not out or out == key:
            return default
        return out
    except Exception:
        return default


def get_chat_scope_key(ss: Dict[str, Any]) -> Optional[ChatScopeKey]:
    """
    Builds a scope key from active selection.
    Returns None if required state isn't ready.
    """
    try:
        bible_id = int(ss.get("active_bible_id"))
        level = str(ss.get("active_level"))
        book_id = int(ss.get("active_book_id"))
        chapter = int(ss.get("active_chapter"))
        if not bible_id or not level or not book_id or not chapter:
            return None
        return ChatScopeKey(bible_id=bible_id, level=level, book_id=book_id, chapter=chapter)
    except Exception:
        return None


def ensure_chat_state(scope: ChatScopeKey) -> str:
    """
    Ensures the per-scope message list exists.
    Returns the session_state key name holding the messages.
    """
    key = scope.as_str()
    if key not in st.session_state:
        st.session_state[key] = []  # list[dict(role, content, meta?)]
    return key


def add_chat_message(messages_key: str, role: str, content: str, meta: Optional[Dict[str, Any]] = None) -> None:
    if not content.strip():
        return
    st.session_state[messages_key].append(
        {"role": role, "content": content.strip(), "meta": meta or {}}
    )


def clear_chat(messages_key: str) -> None:
    st.session_state[messages_key] = []


def build_min_context_snippet(
    verses: Sequence[Dict[str, Any]],
    max_chars: int = 1800,
) -> str:
    """
    Small, cheap context snippet: verse-numbered plain text.
    This is what you'd hand to an LLM later.
    """
    chunks: List[str] = []
    for v in verses or []:
        n = v.get("verse_num") or v.get("verse") or v.get("n") or ""
        tx = v.get("text") or ""
        line = f"{n}. {tx}".strip()
        if line and line != ".":
            chunks.append(line)

    text = "\n".join(chunks).strip()
    if len(text) <= max_chars:
        return text

    # truncate from the end (keep the beginning, which tends to include the setup)
    return text[: max_chars - 20].rstrip() + "\n…"


# -----------------------------
# Streamlit UI (placeholder)
# -----------------------------
def render_chat_placeholder(
    t: Callable,
    book_name: str,
    chapter_num: int,
    verses: Sequence[Dict[str, Any]],
    vocab_json: Optional[Dict[str, Any]] = None,
    enabled: bool = CHAT_ENABLED_DEFAULT,
) -> None:
    ss = st.session_state

    # Localized title with safe fallback
    # Add later to i18n:
    # - en: "Chat (Coming soon…)"
    # - de: "Chat (Demnächst…)"
    title_default = "Chat (Coming soon…)"
    if str(ss.get("active_language", "")).lower().startswith("german"):
        title_default = "Chat (Demnächst…)"
    title = _safe_tr(t, ss, "chat_coming_soon", title_default)

    scope = get_chat_scope_key(ss)
    if scope is None:
        with st.expander(title, expanded=False):
            st.info("Chat will appear once a chapter is loaded.")
        return

    messages_key = ensure_chat_state(scope)

    with st.expander(title, expanded=False):
        # Top row: scope + controls
        left, right = st.columns([4, 1], vertical_alignment="center")
        with left:
            st.caption(f"{book_name} {chapter_num} • {ss.get('active_level','')}")
        with right:
            st.button(
                _safe_tr(t, ss, "clear", "Clear"),
                use_container_width=True,
                on_click=clear_chat,
                args=(messages_key,),
                key=f"{messages_key}:clear_btn",
                disabled=(len(st.session_state[messages_key]) == 0),
            )

        # Explain what it will do
        st.markdown(
            _safe_tr(
                t,
                ss,
                "chat_helper_text",
                "Ask questions about the chapter (meaning, grammar, vocabulary, or translation choices). "
                "This will be wired to an LLM soon.",
            )
        )

        # Render chat transcript (if any)
        for m in st.session_state[messages_key]:
            role = m.get("role", "assistant")
            content = m.get("content", "")
            with st.chat_message(role):
                st.write(content)

        # Placeholder input (disabled for now)
        placeholder = _safe_tr(t, ss, "chat_input_placeholder", "Type your question here…")
        st.chat_input(
            placeholder,
            key=f"{messages_key}:input",
            disabled=(not enabled),
        )

        # If disabled, show a gentle hint and an example of the context that would be provided
        if not enabled:
            st.info(
                _safe_tr(
                    t,
                    ss,
                    "chat_disabled_info",
                    "Chat is not enabled yet. This section is a placeholder UI (next step: connect to an LLM).",
                )
            )

        # Context preview (useful while you wire the model later)
        with st.expander(_safe_tr(t, ss, "chat_context_preview", "Context preview (for wiring the LLM)"), expanded=False):
            ctx = build_min_context_snippet(verses=verses, max_chars=1800)
            st.code(ctx or "(no verses loaded)", language="text")
