from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Optional, Sequence

import streamlit as st

from .emailer import send_feedback_email

@dataclass(frozen=True)
class FeedbackScopeKey:
    bible_id: int
    level: str
    book_id: int
    chapter: int

    def as_str(self) -> str:
        return f"feedback:{self.bible_id}:{self.level}:{self.book_id}:{self.chapter}"


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


def _get_scope(ss: Dict[str, Any]) -> Optional[FeedbackScopeKey]:
    try:
        return FeedbackScopeKey(
            bible_id=int(ss.get("active_bible_id")),
            level=str(ss.get("active_level")),
            book_id=int(ss.get("active_book_id")),
            chapter=int(ss.get("active_chapter")),
        )
    except Exception:
        return None


def _build_verse_preview(verses: Sequence[Dict[str, Any]], max_chars: int = 900) -> str:
    """Small excerpt so your email has a hint of what they saw without being huge."""
    if not verses:
        return ""
    lines = []
    for v in verses:
        n = v.get("verse_num") or v.get("verse") or v.get("n") or ""
        tx = (v.get("text") or "").strip()
        if not tx:
            continue
        lines.append(f"{n}. {tx}".strip())
    text = "\n".join(lines).strip()
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 20].rstrip() + "\n…"


def _cooldown_ok(scope_key: str, seconds: int = 30) -> bool:
    ts_key = f"{scope_key}:last_sent_ts"
    last = st.session_state.get(ts_key)
    if not last:
        return True
    try:
        return (datetime.now(timezone.utc).timestamp() - float(last)) >= seconds
    except Exception:
        return True


def _mark_sent(scope_key: str) -> None:
    st.session_state[f"{scope_key}:last_sent_ts"] = datetime.now(timezone.utc).timestamp()


def render_feedback_footer(
    t: Callable,
    book_name: str,
    chapter_num: int,
    bible_name: str,
    level: str,
    verses: Sequence[Dict[str, Any]],
) -> None:
    
    with st.expander("Feedback - coming soon",False):
        ss = st.session_state

        scope = _get_scope(ss)
        if scope is None:
            st.info("Feedback will appear once a chapter is loaded.")
            return

        scope_key = scope.as_str()

        # --- Localized strings (with good defaults) ---
        title = _safe_tr(t, ss, "feedback_title", "Chapter feedback -- Coming Soon")
        thumbs_up_label = _safe_tr(t, ss, "thumbs_up", "Thumbs up")
        thumbs_down_label = _safe_tr(t, ss, "thumbs_down", "Thumbs down")
        optional_comment = _safe_tr(t, ss, "optional_comment", "Optional comment")
        comment_ph = _safe_tr(
            t,
            ss,
            "feedback_comment_placeholder",
            "Tell me what worked or what felt confusing…",
        )
        send_btn = _safe_tr(t, ss, "send_feedback", "Send feedback")
        email_dev = _safe_tr(t, ss, "email_developer", "Email developer")
        thanks = _safe_tr(t, ss, "feedback_thanks", "Thanks — your feedback was sent!")

        # Footer text
        copyright_text = _safe_tr(
            t,
            ss,
            "copyright_text",
            "Copyright Rex VanHorn 2026. \n Attribution: Biblical texts and supporting content were derived from public sources and are provided for educational purposes.",
        )
        public_domain_notice = _safe_tr(
            t,
            ss,
            "public_domain_notice",
            "Public domain notice: All translations (e.g., inc. ASV) are in the public domain.",
        )

        # --- UI: feedback form (no DB) ---
        st.subheader(title)

        # Simple anti-spam honeypot (hidden-ish). Bots often fill it; humans won’t.
        # If it’s filled, we silently ignore send.
        hp_key = f"{scope_key}:hp"

        with st.form(key=f"{scope_key}:form", clear_on_submit=False):
            c1, c2, c3 = st.columns([1, 1, 2])

            with c1:
                choice = st.radio(
                    label=_safe_tr(t, ss, "feedback_vote_label", "Rating"),
                    options=[thumbs_up_label, thumbs_down_label],
                    horizontal=True,
                    key=f"{scope_key}:vote",
                )

            with c2:
                st.text_input(
                    label="test",
                    value=ss.get(hp_key, ""),
                    key=hp_key,
                    label_visibility="collapsed",
                    placeholder="(leave blank)",
                    help="",
                )

            with c3:
                comment = st.text_area(
                    label=optional_comment,
                    placeholder=comment_ph,
                    key=f"{scope_key}:comment",
                    height=110,
                )

            # Disable if cooldown hasn’t passed
            can_send = _cooldown_ok(scope_key, seconds=30)
            submitted = st.form_submit_button(send_btn, use_container_width=True, disabled=(not can_send))

        if submitted:
            # If honeypot filled, treat as spam and do nothing visible.
            if (ss.get(hp_key) or "").strip():
                st.stop()

            vote = "up" if choice == thumbs_up_label else "down"

            # Extra context
            quiz_correct = ss.get("quiz_correct")
            quiz_incorrect = ss.get("quiz_incorrect")

            verse_preview = _build_verse_preview(verses, max_chars=900)

            subject = f"[Bible App Feedback] {book_name} {chapter_num} ({level}) — {vote.upper()}"
            body = "\n".join(
                [
                    "New chapter feedback",
                    "",
                    f"Vote: {vote}",
                    f"Language: {ss.get('active_language', '')}",
                    f"Bible: {bible_name}",
                    f"Level: {level}",
                    f"Book/Chapter: {book_name} {chapter_num}",
                    f"BibleId/BookId/Chapter: {ss.get('active_bible_id')}/{ss.get('active_book_id')}/{ss.get('active_chapter')}",
                    f"Quiz: correct={quiz_correct} incorrect={quiz_incorrect}",
                    "",
                    "Comment:",
                    (comment or "").strip() or "(none)",
                    "",
                    "Verse preview:",
                    verse_preview or "(no verses loaded)",
                    "",
                    "Timestamp (UTC): " + datetime.now(timezone.utc).isoformat(timespec="seconds"),
                ]
            )

            try:
                send_feedback_email(subject=subject, body=body)
                _mark_sent(scope_key)
                st.success(thanks)
            except Exception as e:
                st.error(
                    "Could not send feedback email. "
                    "Check API keys (SENDGRID_API_KEY / FEEDBACK_TO_EMAIL / FEEDBACK_FROM_EMAIL)."
                )
                st.exception(e)

        # Developer email link (simple mailto)
        st.link_button(email_dev, "mailto:rex@ninefourecho.com")

        # --- Footer / copyright ---
        st.divider()
        st.caption(copyright_text)
        st.caption(public_domain_notice)
