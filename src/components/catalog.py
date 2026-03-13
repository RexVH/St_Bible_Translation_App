# catalog.py
from __future__ import annotations

import glob
import os
import sqlite3
from typing import Dict, List, TypedDict

import streamlit as st


LANGUAGE_DISPLAY_NAMES = {
    "en": "English",
    "de": "Deutsch",
    "es": "Español",
    "fr": "Français",
    "it": "Italiano",
    "pt": "Português",
}

class TranslationEntry(TypedDict):
    label: str
    db_path: str
    code: str
    name: str
    language: str


def _safe_fetchone(cur, sql: str):
    try:
        return cur.execute(sql).fetchone()
    except Exception:
        return None


def get_language_display_name(language_code: str) -> str:
    """
    Convert a language code into a user-facing label for the language selector.
    Falls back to the original DB value when unknown.
    """
    if not language_code:
        return ""
    return LANGUAGE_DISPLAY_NAMES.get(language_code, language_code)


@st.cache_data(show_spinner=False)
def build_catalog(db_dir: str = "/data") -> Dict[str, List[TranslationEntry]]:
    """
    Scans the given directory for .db files, reads their metadata, and builds a catalog of available Bible translations.
    Returns:
      {
        "English": [{"label": "ASV (ASV)", "db_path": "/data/asv.db", ...}],
        "German":  [{"label": "Textbibel (TEXTBIBEL)", "db_path": "/data/textbibel.db", ...}],
      }
    Cached so it won't rescan on every rerun.
    """
    paths = sorted(glob.glob(os.path.join(db_dir, "*.db")))

    # Include mtimes in the cached function's dependency graph:
    # (Streamlit cache key includes args + function body; mtimes aren't automatic.)
    _mtimes = tuple((p, os.path.getmtime(p)) for p in paths)

    catalog: Dict[str, List[TranslationEntry]] = {}

    for p, _ in _mtimes:
        try:
            con = sqlite3.connect(p)
            con.row_factory = sqlite3.Row
            cur = con.cursor()

            bible_row = _safe_fetchone(cur, "SELECT name, language, code FROM bibles LIMIT 1")

            if not bible_row:
                continue

            language = str(bible_row["language"])
            name = str(bible_row["name"])
            code = str(bible_row["code"] or "")
            label = f"{name} ({code})".strip()

            entry: TranslationEntry = {
                "label": label,
                "db_path": p,
                "code": code,
                "name": name,
                "language": language,
            }
            catalog.setdefault(language, []).append(entry)

        except Exception:
            # optionally log/collect errors
            continue
        finally:
            try:
                con.close()
            except Exception:
                pass

    # sort for stable UI
    for language in list(catalog.keys()):
        catalog[language] = sorted(catalog[language], key=lambda e: e["label"].lower())

    return dict(sorted(catalog.items(), key=lambda kv: kv[0].lower()))
