# src/components/quiz.py
from __future__ import annotations

import json
import random
from typing import Any, Callable, Dict, List

import streamlit as st


def _safe_parse_quiz_json(raw: Any) -> List[Dict[str, Any]]:
    """
    Accepts:
      - None
      - already-parsed list[dict]
      - dict with "questions"
      - JSON string
    Returns list of question dicts (possibly empty).
    """
    if raw is None:
        return []

    if isinstance(raw, list):
        return [q for q in raw if isinstance(q, dict)]

    if isinstance(raw, dict):
        qs = raw.get("questions")
        if isinstance(qs, list):
            return [q for q in qs if isinstance(q, dict)]
        return []

    if isinstance(raw, str):
        s = raw.strip()
        if not s:
            return []
        try:
            obj = json.loads(s)
        except Exception:
            return []
        return _safe_parse_quiz_json(obj)

    return []


def _quiz_signature(book_name: str, chapter_num: int) -> str:
    """
    A "chapter session" signature. Includes active selection to ensure reset
    when user changes any of these.
    """
    ss = st.session_state
    return "|".join(
        [
            str(ss.get("active_language")),
            str(ss.get("active_bible_id")),
            str(ss.get("active_level")),
            str(ss.get("active_book_id")),
            str(ss.get("active_chapter")),
            str(book_name),
            str(chapter_num),
        ]
    )


def _ensure_quiz_state(sig: str, questions: List[Dict[str, Any]]) -> None:
    ss = st.session_state

    # Initialize container keys if missing
    ss.setdefault("quiz_sig", None)
    ss.setdefault("quiz_questions", [])
    ss.setdefault("quiz_index", 0)
    ss.setdefault("quiz_correct", 0)
    ss.setdefault("quiz_incorrect", 0)

    # Per-question toggles / last choice
    ss.setdefault("quiz_last_choice", None)
    ss.setdefault("quiz_last_was_correct", None)
    ss.setdefault("quiz_show_hint", False)
    ss.setdefault("quiz_show_explanation", False)

    # Reset when chapter selection changes OR question set changes materially
    if ss.quiz_sig != sig or not isinstance(ss.quiz_questions, list):
        ss.quiz_sig = sig
        ss.quiz_questions = questions
        ss.quiz_index = 0
        ss.quiz_correct = 0
        ss.quiz_incorrect = 0
        ss.quiz_last_choice = None
        ss.quiz_last_was_correct = None
        ss.quiz_show_hint = False
        ss.quiz_show_explanation = False
        return

    # If quiz exists but the question list length changed (e.g., DB updated),
    # keep progress but clamp safely.
    if isinstance(ss.quiz_questions, list) and len(ss.quiz_questions) != len(questions):
        ss.quiz_questions = questions
        if ss.quiz_index >= len(questions):
            ss.quiz_index = max(0, len(questions) - 1)
        ss.quiz_last_choice = None
        ss.quiz_last_was_correct = None
        ss.quiz_show_hint = False
        ss.quiz_show_explanation = False


def _deterministic_shuffle(items: List[str], seed: str) -> List[str]:
    r = random.Random(seed)
    items = list(items)
    r.shuffle(items)
    return items


def _answers_for_question(q: Dict[str, Any], seed: str) -> List[str]:
    correct = q.get("correct_answer", "")
    distractors = q.get("distractor_answers") or []
    answers = [a for a in [correct, *distractors] if isinstance(a, str) and a.strip()]
    # Dedup while preserving original relative order first, then shuffle deterministically
    seen = set()
    deduped = []
    for a in answers:
        if a not in seen:
            seen.add(a)
            deduped.append(a)
    return _deterministic_shuffle(deduped, seed=seed)


def _reset_per_question_flags() -> None:
    ss = st.session_state
    ss.quiz_last_choice = None
    ss.quiz_last_was_correct = None
    ss.quiz_show_hint = False
    ss.quiz_show_explanation = False


def _go_next_question() -> None:
    ss = st.session_state
    if ss.quiz_index < len(ss.quiz_questions) - 1:
        ss.quiz_index += 1
        _reset_per_question_flags()
    else:
        _reset_per_question_flags()


def _restart_quiz() -> None:
    ss = st.session_state
    ss.quiz_index = 0
    ss.quiz_correct = 0
    ss.quiz_incorrect = 0
    _reset_per_question_flags()


def render_quiz_section(
    quiz_json: Any,
    t: Callable[[Any, str], str],
    book_name: str,
    chapter_num: int,
) -> None:
    """
    Renders the quiz UI:
      - one question at a time
      - progress indicator
      - tracks correct/incorrect for this chapter session
      - Hint -> shows reference verse
      - Explanation -> shows explanation text
    """
    questions = _safe_parse_quiz_json(quiz_json)
    sig = _quiz_signature(book_name, chapter_num)
    _ensure_quiz_state(sig, questions)

    ss = st.session_state

    if not ss.quiz_questions:
        st.subheader(t(ss, "quiz"))
        st.info(t(ss, "no_quiz_available"))
        return

    total = len(ss.quiz_questions)

    # Completion screen (index uses sentinel == total)
    if ss.quiz_index >= total:
        st.subheader(t(ss, "quiz"))
        st.caption(t(ss, "quiz_complete"))
        st.write(f"{t(ss, 'correct')}: {int(ss.quiz_correct)}")
        st.write(f"{t(ss, 'incorrect')}: {int(ss.quiz_incorrect)}")

        denom = max(1, int(ss.quiz_correct) + int(ss.quiz_incorrect))
        pct = int(round((int(ss.quiz_correct) / denom) * 100))
        st.caption(f"{t(ss, 'score')}: {pct}%")

        if st.button(t(ss, "restart_quiz"), key="quiz_restart_done"):
            _restart_quiz()
            st.rerun()
        return

    # Normal question view
    q = ss.quiz_questions[ss.quiz_index]
    at_last = ss.quiz_index >= total - 1

    # --- Header line: "Quiz" (big) + "Question x of y" (small) on same line
    h1, h2, h3 = st.columns([2, 2, 2], vertical_alignment="bottom")
    with h1:
        st.markdown(f"### {t(ss, 'quiz')}")
    with h2:
        st.caption(f"{t(ss, 'question')} {ss.quiz_index + 1} {t(ss, 'of')} {total}")
    with h3:
        st.write(t(ss, "correct:"), int(ss.quiz_correct), t(ss, "incorrect"), int(ss.quiz_incorrect))

    # Question text
    q_text = q.get("question_text") or ""
    if q_text.strip():
        st.markdown(f"**{q_text}**")
    else:
        st.warning(t(ss, "quiz_question_missing_text"))

    # --- Answers (horizontal row)
    answers = _answers_for_question(q, seed=f"{sig}|q{ss.quiz_index}")
    if not answers:
        st.warning(t(ss, "quiz_no_answers"))
        return

    # IMPORTANT: compute answered AFTER handling click, so feedback appears on first click
    answered_now = ss.quiz_last_choice is not None
    clicked_this_run = False

    cols = st.columns(len(answers))
    correct_answer =(q.get("correct_answer") or "")
    for a, c in zip(answers, cols):
        with c:
            if st.button(
                a,
                disabled=answered_now,
                use_container_width=True,
                key=f"quiz_answer_{ss.quiz_index}_{hash(a)}",
            ):
                ss.quiz_last_choice = a
                correct = (a == correct_answer)
                ss.quiz_last_was_correct = correct
                if correct:
                    ss.quiz_correct += 1
                else:
                    ss.quiz_incorrect += 1

                answered_now = True
                clicked_this_run = True

    # If they clicked an answer, we don't need a rerun; we already set answered_now=True
    # (Feedback + Next enabled immediately in the same run.)

    # Feedback after answering
    if answered_now:
        if ss.quiz_last_was_correct:
            st.success("Yay! You chose the correct answer. Click next_question to continue.")
        else:
            st.error(f"Sorry. The correct answer was '{correct_answer}'.  Click next_question to continue. ")

    # Hint / Explanation buttons
    b1, b2, _, b3, b4 = st.columns([1, 1, 4, 1, 1])

    with b1:
        if st.button(t(ss, "hint"), key=f"quiz_hint_{ss.quiz_index}"):
            ss.quiz_show_hint = True

    with b2:
        if st.button(t(ss, "explanation"), key=f"quiz_expl_{ss.quiz_index}"):
            ss.quiz_show_explanation = True

    # Reveals
    if ss.quiz_show_hint:
        ref = q.get("reference_verse")
        bo_vs = ref.split(':')
        if isinstance(ref, str) and ref.strip():
            st.caption(f"{t(ss, 'reference_verse')}  -  {book_name} {chapter_num}:{bo_vs[1]}")
        else:
            st.caption(f"{t(ss, 'reference_verse')}: —")

    if ss.quiz_show_explanation:
        expl = q.get("explanation") or ""
        if str(expl).strip():
            st.info(expl)
        else:
            st.caption(t(ss, "no_explanation_available"))

    with b3:
        if st.button(t(ss, "restart_quiz"), key="quiz_restart"):
            _restart_quiz()
            st.rerun()

    with b4:
        next_label = t(ss, "finish") if (answered_now and at_last) else t(ss, "next_question")
        if st.button(next_label, disabled=not answered_now, type="primary", key=f"quiz_next_{ss.quiz_index}"):
            if at_last:
                ss.quiz_index = total  # sentinel -> completion screen
                _reset_per_question_flags()
            else:
                _go_next_question()
            st.rerun()
