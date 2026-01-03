# Session State Spec (UI v1) — Streamlit Bible Language App

**Goal:** deterministic behavior across Streamlit reruns  
**Principle:** UI language and content update only when **Load** commits draft → active state

---

## 1) Terminology

### Draft vs Active
- **Draft selections**: sidebar widget values
- **Active selection**: what drives all main-page queries and UI language

UI language always follows **active_language**, never draft_language.

---

## 2) Initialization

- `initialized: bool`
  - default: `False`

- `db_path: str`
  - default: `"multi_bibles.db"`

---

## 3) Draft Sidebar State (no immediate effect)

- `draft_language: str`
  - default: `"English"`
- `draft_bible_id: int`
- `draft_level: str`
- `draft_book_id: int`
  - default: `1`
- `draft_chapter: int`
  - default: `1`

Changing these does NOT affect:
- main content
- UI language
- quiz state

---

## 4) Active Selection State (authoritative)

- `active_language: str`
- `active_bible_id: int`
- `active_level: str`
- `active_book_id: int`
- `active_chapter: int`

### UI Language Rule (NEW — v1)
- All UI labels, buttons, and instructions are derived from:
  - `active_language`
- Example:
  - `active_language = "German"` → UI renders in German

---

## 5) Reading Toggles (persist across navigation)

- `show_verse_numbers: bool`
  - default: `True`
- `highlight_vocab: bool`
  - default: `False`

---

## 6) Audio State (persist across navigation)

- `audio_speed: float`
  - default: `1.0`
  - allowed:
    - `0.75 | 0.80 | 0.90 | 1.0 | 1.25 | 1.5`

---

## 7) Quiz State (resets on context change)

- `quiz_key: str`
  - format: `{bible_id}:{level}:{book_id}:{chapter}`

- `quiz_questions: list[dict]`
- `quiz_index: int`
- `quiz_correct: int`
- `quiz_incorrect: int`

- Per-question flags:
  - `quiz_show_hint: bool`
  - `quiz_show_explanation: bool`
  - `quiz_last_choice: str|None`
  - `quiz_last_was_correct: bool|None`

---

## 8) Feedback State

- `feedback_key: str`
- `feedback_vote: int|None`
- `feedback_comment: str`
- `feedback_submitted: bool`

---

## 9) Cached Derived Data

- `cached_vocab_key: str|None`
- `cached_vocab: Any|None`

- `cached_notes_key: str|None`
- `cached_notes_by_verse_start: dict[int, list[dict]]|None`

---

## 10) Event Flow Rules (UPDATED)

### Load Button
On **Load**:
1. Copy all draft values → active values
2. Set `active_language`
3. UI language updates immediately
4. Reset quiz + feedback state
5. Refresh cached vocab and notes

---

### Back / Next Navigation
- Update `active_chapter`
- KEEP:
  - UI language
  - toggles
  - audio_speed
- RESET:
  - quiz state
  - feedback state

---

### Level Change
- Update `active_level`
- KEEP:
  - active_language
  - book/chapter
  - toggles
  - audio_speed
- RESET quiz + feedback

---

### Language / Bible Change
- Occurs via sidebar + Load
- Resets:
  - book/chapter (unless explicitly selected)
  - quiz
  - feedback
- Updates:
  - UI language
  - all content

---

## 11) Invariants

- UI language always matches `active_language`
- UI never switches language mid-rerun
- All visible text must come from either:
  - DB content (already localized), or
  - UI string dictionary keyed by `active_language`
