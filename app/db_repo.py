# app/db_repo.py
from __future__ import annotations

import sqlite3
import json
from functools import lru_cache
from typing import Any, Dict, List, Optional, Tuple


# -----------------------------
# Connection helpers
# -----------------------------
def connect(db_path: str) -> sqlite3.Connection:
    """
    SQLite connection suitable for Streamlit reruns.
    NOTE: Callers should close the connection (use `with connect(...) as conn:`).
    """
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def _safe_json_loads(s: Optional[str]) -> Any:
    if not s:
        return None
    try:
        return json.loads(s)
    except Exception:
        return None


# -----------------------------
# Lookup lists for UI dropdowns
# -----------------------------
@lru_cache(maxsize=128)
def get_languages(db_path: str) -> List[str]:
    """
    v1 languages are also hard-coded, but this uses DB so it scales.
    Returns: ["English", "German", ...] (sorted)
    """
    with connect(db_path) as conn:
        rows = conn.execute(
            "SELECT DISTINCT language FROM bibles WHERE language IS NOT NULL ORDER BY language"
        ).fetchall()
    langs = [r["language"] for r in rows]
    # Fallback to v1 defaults if DB empty
    return langs or ["English", "German"]


@lru_cache(maxsize=256)
def get_bibles_for_language(db_path: str, language: str) -> List[Dict[str, Any]]:
    """
    Returns list of bibles for a language.
    Each item: {id, code, name, year, license}
    """
    with connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT id, code, language, name, year, license
            FROM bibles
            WHERE language = ?
            ORDER BY name
            """,
            (language,),
        ).fetchall()

    return [dict(r) for r in rows]


@lru_cache(maxsize=256)
def get_books_for_language(db_path: str, language: str) -> List[Dict[str, Any]]:
    """
    Returns books (localized) for a language, ordered canonically by sort_order.
    Falls back to books_en if localized table missing for that language.
    Each item: {id, name, testament, sort_order}
    """
    with connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT id, name, testament, sort_order
            FROM books
            WHERE language = ?
            ORDER BY sort_order
            """,
            (language,),
        ).fetchall()

        if rows:
            return [dict(r) for r in rows]

        # fallback (should not happen in your current setup, but safe)
        rows2 = conn.execute(
            """
            SELECT id, name, testament, sort_order
            FROM books_en
            ORDER BY sort_order
            """
        ).fetchall()
        return [dict(r) for r in rows2]


@lru_cache(maxsize=1024)
def get_available_chapters(
    db_path: str, bible_id: int, level: str, book_id: int
) -> List[int]:
    """
    Returns available chapters for (bible_id, level, book_id).
    Uses graded_chapter_meta for graded levels; uses verses for Source if needed.
    """
    with connect(db_path) as conn:
        if level == "Source":
            rows = conn.execute(
                """
                SELECT DISTINCT chapter
                FROM verses
                WHERE bible_id = ? AND book_id = ?
                ORDER BY chapter
                """,
                (bible_id, book_id),
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT DISTINCT chapter
                FROM graded_chapter_meta
                WHERE bible_id = ? AND level = ? AND book_id = ?
                ORDER BY chapter
                """,
                (bible_id, level, book_id),
            ).fetchall()

    return [int(r["chapter"]) for r in rows]


# -----------------------------
# Chapter content
# -----------------------------
def get_chapter_meta(
    db_path: str, bible_id: int, level: str, book_id: int, chapter: int
) -> Optional[Dict[str, Any]]:
    """
    Returns graded_chapter_meta row as dict (or None).
    For level == Source, still returns meta if present (optional),
    but callers should not depend on it.
    """
    with connect(db_path) as conn:
        row = conn.execute(
            """
            SELECT *
            FROM graded_chapter_meta
            WHERE bible_id = ? AND level = ? AND book_id = ? AND chapter = ?
            LIMIT 1
            """,
            (bible_id, level, book_id, chapter),
        ).fetchone()

    return dict(row) if row else None


def get_verses(
    db_path: str, bible_id: int, level: str, book_id: int, chapter: int
) -> List[Dict[str, Any]]:
    """
    Returns verses for the chapter as list of dicts:
      [{verse:int, text:str, verse_notes_json:optional str}, ...]

    - For Source: uses verses.text
    - For graded levels: uses graded_verses.graded_text + optional verse_notes_json
    """
    with connect(db_path) as conn:
        if level == "Source":
            rows = conn.execute(
                """
                SELECT verse, text
                FROM verses
                WHERE bible_id = ? AND book_id = ? AND chapter = ?
                ORDER BY verse
                """,
                (bible_id, book_id, chapter),
            ).fetchall()
            return [{"verse": int(r["verse"]), "text": r["text"]} for r in rows]

        rows = conn.execute(
            """
            SELECT verse, graded_text AS text, verse_notes_json
            FROM graded_verses
            WHERE bible_id = ? AND level = ? AND book_id = ? AND chapter = ?
            ORDER BY verse
            """,
            (bible_id, level, book_id, chapter),
        ).fetchall()
        return [
            {
                "verse": int(r["verse"]),
                "text": r["text"],
                "verse_notes_json": r["verse_notes_json"],
            }
            for r in rows
        ]


def get_vocab_json(
    db_path: str, bible_id: int, level: str, book_id: int, chapter: int
) -> Optional[dict]:
    """
    Prefer chapter_vocab.vocab_json (per spec).
    Fallback: graded_chapter_meta.vocab_json if chapter_vocab missing.
    Returns parsed JSON dict or None.
    """
    with connect(db_path) as conn:
        row = conn.execute(
            """
            SELECT vocab_json
            FROM chapter_vocab
            WHERE bible_id = ? AND level = ? AND book_id = ? AND chapter = ?
            LIMIT 1
            """,
            (bible_id, level, book_id, chapter),
        ).fetchone()

        if row and row["vocab_json"]:
            return _safe_json_loads(row["vocab_json"])

        # fallback
        row2 = conn.execute(
            """
            SELECT vocab_json
            FROM graded_chapter_meta
            WHERE bible_id = ? AND level = ? AND book_id = ? AND chapter = ?
            LIMIT 1
            """,
            (bible_id, level, book_id, chapter),
        ).fetchone()

        if row2 and row2["vocab_json"]:
            return _safe_json_loads(row2["vocab_json"])

    return None


def get_teaching_notes(
    db_path: str, bible_id: int, level: str, book_id: int, chapter: int
) -> List[dict]:
    """
    Returns teaching notes list from graded_chapter_meta.teaching_notes_json.
    Expected shape:
      {"teaching_notes":[{...}, ...]}
    Returns [] if missing or invalid.
    """
    with connect(db_path) as conn:
        row = conn.execute(
            """
            SELECT teaching_notes_json
            FROM graded_chapter_meta
            WHERE bible_id = ? AND level = ? AND book_id = ? AND chapter = ?
            LIMIT 1
            """,
            (bible_id, level, book_id, chapter),
        ).fetchone()

    payload = _safe_json_loads(row["teaching_notes_json"]) if row else None
    if not isinstance(payload, dict):
        return []
    notes = payload.get("teaching_notes")
    return notes if isinstance(notes, list) else []


def group_teaching_notes_by_verse_start(notes: List[dict]) -> Dict[int, List[dict]]:
    """
    Option A support: verse_start -> [note, note, ...]
    """
    out: Dict[int, List[dict]] = {}
    for n in notes or []:
        try:
            vs = int(n.get("verse_start"))
        except Exception:
            continue
        out.setdefault(vs, []).append(n)
    return out


def get_quiz_json(
    db_path: str, bible_id: int, level: str, book_id: int, chapter: int
) -> Optional[dict]:
    """
    Returns parsed quiz JSON dict from graded_chapter_meta.quiz_json (or None).
    """
    meta = get_chapter_meta(db_path, bible_id, level, book_id, chapter)
    if not meta:
        return None
    return _safe_json_loads(meta.get("quiz_json"))


@lru_cache(maxsize=256)
def get_default_bible_id(db_path: str, language: str) -> Optional[int]:
    bibles = get_bibles_for_language(db_path, language)
    if not bibles:
        return None
    return int(bibles[0]["id"])


@lru_cache(maxsize=512)
def get_book_name(db_path: str, language: str, book_id: int) -> Optional[str]:
    books = get_books_for_language(db_path, language)
    for b in books:
        if int(b["id"]) == int(book_id):
            return b["name"]
    return None


def clamp_to_available_chapter(chapters: list[int], desired: int) -> int:
    if not chapters:
        return 1
    if desired in chapters:
        return desired
    # choose nearest lower, else first
    lower = [c for c in chapters if c <= desired]
    return max(lower) if lower else chapters[0]
