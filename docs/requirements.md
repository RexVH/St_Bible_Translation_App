# 📘 Streamlit Bible Language App  
## UI v1 Requirements Specification

**Version:** v1  
**Scope:** ASV (English) and TextBibel (German), CEFR A1–B2 + Source  
**Primary goal:** Reading-first Bible + language-learning experience with full language immersion  
**Out of scope (v1):** Chat backend, user accounts, cross-session tracking

---

## 0. App Overview

- Single-page **Streamlit application**
- Layout:
  - **Sidebar:** user selection + references
  - **Main page:** chapter experience (image → audio → reading → study → quiz)
- **UI language always follows the active learning language** (immersion-first design)

---

## 1. Sidebar Requirements

### 1.1 Selection Panel
Required widgets (labels localized to UI language):

- **Language selector**
  - v1 options: `English`, `German`
  - Controls the **target learning language**
  - UI language updates only after clicking **Load**

- **Bible selector**
  - Filtered by language
  - v1:
    - English → ASV
    - German → TextBibel

- **Level selector**
  - Options: `A1`, `A2`, `B1`, `B2`, `Source`

- **Book selector** (optional)
  - Default: `Genesis` (`book_id = 1`)
  - Book names come from DB and are already localized

- **Chapter selector** (optional)
  - Default: `1`

- **Load button**
  - Label localized (e.g., `Load`, `Laden`)
  - Applies all selections to the main page
  - Triggers UI language switch to match active learning language

---

### 1.2 Reference Section
- Dictionary lookup links (external, localized labels):
  - German (e.g., Duden / Wiktionary)
  - English (e.g., Merriam-Webster / Wiktionary)
- “Contact developer” link (localized label)

---

## 2. Main Page Layout (Top → Bottom)

### A. Hero Block
- **Chapter orientation header**
  - Example:
    - English: `Genesis 1 — ASV — A1`
    - German: `1. Mose 1 — TextBibel — A1`

- **Banner image**
  - Source: `graded_chapter_meta.image_url`
  - Display height: ~260px
  - Button: localized **View image** (modal/dialog)

- **One-line summary**
  - Source: `graded_chapter_meta.summary_one_line`
  - Displayed as headline text (already localized via DB)

- **Summary paragraph**
  - Source: `graded_chapter_meta.summary_paragraph`
  - Always visible (max ~3 sentences)

---

### B. Audio Block
- **Audio player**
  - Source: `graded_chapter_meta.audio_url`

- **Playback speed controls**
  - Options:
    - `0.75x`, `0.80x`, `0.90x`, `1.0x`, `1.25x`, `1.5x`
  - Labels localized

- **Download MP3**
  - Localized label
  - Direct download using same `audio_url`

---

### C. Navigation + Quick Settings
- **Navigation row**
  - Localized buttons:
    - Back / Zurück
    - Next / Weiter
  - Book dropdown
  - Chapter dropdown

- **Quick toggles** (localized labels)
  - Show verse numbers
  - Highlight vocab headwords

---

### D. Key Words Preview (Before Text)
- Display **first 10 headwords** from `chapter_vocab.vocab_json`
- Render as **pills/chips**
- Interaction:
  - **Hover:** one-line gloss tooltip (localized via DB)
  - **Click/tap:** reveal same gloss (popover or inline)
- No ranking logic in v1

---

### E. Reading Block (Main Text)
- Display selected chapter text:
  - Graded (CEFR levels) **or**
  - Source text
- All text sourced from DB and already localized

- Verse rendering:
  - Verse numbers ON → numbered verse lines
  - Verse numbers OFF → verses separated by spacing
  - No artificial paragraph creation

#### Teaching Notes — REQUIRED (Option A)
- Data source: chapter-level teaching notes JSON (already localized)
- For each verse `v`:
  - If any note where `verse_start == v`, show 📝 icon
  - Clicking icon opens localized popover containing:
    - `primary_change`
    - `note`
    - `reflection_question`
- Notes spanning multiple verses appear only at `verse_start`

---

### F. Vocabulary (After Text)
- **Expander** titled with localized label (e.g., `Vocabulary`, `Wortschatz`)
- Displays full vocab list from `chapter_vocab.vocab_json`
- Optional v1 enhancement:
  - Search/filter box (localized placeholder text)

---

### G. Quiz Section
- Data source: `graded_chapter_meta.quiz_json` (localized)

Behavior:
- One question at a time
- Progress indicator (localized format)
- Track **correct** and **incorrect** counts per chapter session
- Buttons (localized):
  - Hint → reveals reference verse
  - Explanation → reveals explanation text

---

### H. Chat Placeholder
- Collapsed expander
- Localized title (e.g., “Chat (Coming soon…)”, “Chat (Demnächst…)”)

---

### I. Feedback + Footer
- **Chapter feedback**
  - Thumbs up / down (localized labels)
  - Optional comment field (localized placeholder)
  - Email developer link

- **Copyright/footer**
  - Static text
  - Public domain notice (localized)

---

## 3. UI Language Rules (NEW — v1)

- UI language is **fully localized**
- UI language always follows **active_language**
- UI language updates:
  - **Only when Load is clicked**
  - Never during draft sidebar changes (prevents flicker)
- No UI-language override in v1

---

## 4. Explicitly Out of Scope (v1)
- User accounts or progress persistence
- Cross-chapter quiz tracking
- Chat / LLM backend
- Advanced dictionary APIs
- Side-by-side text comparison
- UI language override
