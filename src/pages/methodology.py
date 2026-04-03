from pathlib import Path
import streamlit as st

st.set_page_config(page_title="Methodology", layout="wide")

TITLE = "AI-Generated Semantic Scaffolding for Learner Comprehension"
SUBTITLE = "Methodology, conceptual framework, pipeline design, implementation tradeoffs, and figures."

METHOD_TEXT = r'''# AI-Generated Semantic Scaffolding for Learner Comprehension

**Rex VanHorn**  
Institute for Artificial Intelligence  
University of Georgia, Athens, Georgia, USA  
**ORCID:** 0000-0002-3792-427  
**Email:** rex.vanhorn@uga.edu  

---

## Abstract

Operationalizing concepts from multiple research traditions, this project presents the design and implementation of a learning-facilitation application built around a fully automated content-generation pipeline and an interactive Streamlit web interface.

The central concept of the system is **semantic scaffolding**: a structured approach toward full comprehension in which learners ascend a staircase of progressively richer meaning. Instead of presenting learners with either simplified texts or original texts in isolation, the system generates a continuum of materials that guide the learner progressively from basic understanding toward full interpretation.

This project focuses primarily on foreign language learning as a demonstration domain, but also includes literary and technical examples to demonstrate the robustness and generality of the approach. The system takes a difficult source text and regenerates it at four progressively richer levels, such that a learner with only basic understanding can begin at the lowest level and move upward toward comprehension of the source.

To accomplish this, the project integrates text generation, image generation, text-to-speech, database orchestration, and a learner-facing web interface. Multiple local and frontier models were tested in order to identify workable tradeoffs among cost, speed, structure, and quality for large-scale generation.

---

## Contributions

This project makes three primary contributions.

### 1. Semantic Scaffolding as a Computational Framework

The project introduces **semantic scaffolding** as a computational approach to learning support. Semantic scaffolding describes a structured process in which complex texts are transformed into a sequence of intermediate representations that progressively build meaning.

Rather than simply presenting learners with texts in isolation, the system generates multiple graded levels of interpretation that guide learners from elementary comprehension toward full understanding of the source material.

### 2. A Scalable Automated Pipeline

The project develops a scalable automated pipeline for generating semantic scaffolding artifacts. The pipeline integrates:

- large language models,
- diffusion-based image generation systems,
- text-to-speech technologies,
- validation and orchestration logic,
- and a structured SQLite-backed storage system.

Generated artifacts include:

- graded text
- one-line summaries
- paragraph summaries
- vocabulary explanations
- teaching notes
- quizzes
- audio narration
- illustrative images

### 3. An Interactive Learning Application

The project implements an interactive Streamlit application that operationalizes the semantic scaffolding framework. The learner can navigate between graded levels, explore vocabulary, listen to audio, view images, read teaching notes, and complete comprehension quizzes.

Together, these contributions demonstrate how modern generative AI systems can be integrated into a coherent architecture that supports scalable, multimodal learning environments based on progressive semantic understanding.

---

## Related Work

This project draws from several adjacent traditions of prior work, including:

- text simplification,
- readability control,
- instructional scaffolding,
- multimedia learning,
- intelligent tutoring systems,
- and AI-supported educational environments.

### Text Simplification and Readability Control

One of the clearest antecedents to this project is the literature on **text simplification**, which aims to reduce linguistic complexity while preserving meaning.

A key insight from this literature is that simplification is not merely lexical shortening. It can also involve conceptual unpacking, summarization, and pedagogically meaningful restructuring.

This project extends simplification beyond the production of a single easier version of a text. Instead, it generates a **continuum of staged representations** aligned approximately to CEFR levels.

### Instructional Scaffolding and Progressive Comprehension

Pedagogically, this project is grounded in the concept of **scaffolding**, in which learners receive temporary support structures that help them understand beyond their current independent ability.

Traditional scaffolding usually depends on human-authored materials or live instructional intervention. This project attempts to automate the production of scaffold steps at scale.

In this sense, the system is not just a simplifier — it is a **scaffold generator**.

### Multimedia Learning

The project also draws on the literature on **multimedia learning**, particularly the idea that learners often understand material more deeply when verbal and visual channels reinforce one another.

Accordingly, the system combines:

- graded text
- summaries
- vocabulary
- audio narration
- images
- quizzes

into a unified multimodal learning experience.

### Intelligent Tutoring Systems and AI-Supported Learning

This project also connects to the tradition of **intelligent tutoring systems (ITS)** and, more recently, **LLM-enhanced educational tools**.

However, unlike many systems centered around conversational tutoring or reactive Q&A, this project emphasizes **pre-generated pedagogical artifacts** that can be explored interactively and at low cost.

This is a different design philosophy:
- less reactive tutoring,
- more proactive learning environment construction.

### LLMs for Accessibility and Comprehension Support

A related line of work explores the use of LLMs to improve accessibility and reader comprehension of difficult material.

This project extends that idea by arguing that AI-generated intermediate representations should not be isolated interventions, but part of a structured pathway toward fuller understanding.

---

## Conceptual Framework: Semantic Scaffolding

The central concept underlying this project is **semantic scaffolding**, a structured approach to learning in which understanding is achieved incrementally through a sequence of intermediate representations.

### Definition

**Semantic scaffolding** is the computational generation of staged intermediate representations that progressively restore semantic density, lexical specificity, stylistic nuance, and contextual support between novice comprehension and source-text understanding.

In this framework:

- the learner begins with a simplified representation that conveys the core semantic content,
- subsequent levels restore additional linguistic complexity and conceptual depth,
- and the learner ultimately arrives at the original source material.

This process is reinforced through multiple modalities, not text alone.

### Generated Artifacts

For each passage or chapter, the system can generate:

- rewritten graded text
- one-sentence summary
- one-paragraph summary
- vocabulary list
- searchable vocabulary support
- teaching notes
- comprehension quiz
- MP3 narration
- illustrative image

### CEFR as a Learning Ladder

The project uses the **Common European Framework of Reference for Languages (CEFR)** as a practical guide for structuring progressive levels of comprehension.

| App Level | CEFR Approximation | Learning Purpose |
|---|---|---|
| Level 1 | A1 | Elementary to basic: core meaning of the text |
| Level 2 | A2 | Advanced beginner: slightly richer sentences |
| Level 3 | B1 | Beginning intermediate: more natural language |
| Level 4 | B2 | Advanced intermediate: near-original complexity |
| Source | C1–C2 | Original source text |

This framework is not treated as a formal certification system, but as a useful pedagogical ladder.

---

## Example: Shakespeare as a Semantic Ladder

To illustrate semantic scaffolding, consider Shakespeare’s line:

> “All the world’s a stage,  
> And all the men and women merely players.”

The system can generate a staged progression such as:

| Level | Example | Conceptual Layer | Style |
|---|---|---|---|
| A1 | Everyone does things in the world. | Literal core meaning | Literal |
| A2 | The world is like a big stage. People are like actors who play different roles in life. | Semantic core + explanation | Explanatory |
| B1 | The whole world is like a stage, and every person is like an actor who performs different roles during life. | Conceptual metaphor | Conceptual |
| B2 | The world is a stage where men and women perform their roles, acting out the different parts of life. | Stylistic enrichment | Literary |
| Original | All the world's a stage, And all the men and women merely players. | Full rhetorical expression | Poetic |

This illustrates the pathway:

**fact → explanation → conceptual metaphor → literary metaphor → literature**

---

## System Overview

The system follows a modular pipeline architecture designed to transform source texts into structured pedagogical artifacts.

### High-Level Flow

```text
Source Content
    ↓
LLM Generation
    ↓
Graded Text
Summaries
Vocabulary
Teaching Notes
Quizzes
    ↓
Audio Generation
    ↓
Image Generation
    ↓
Interactive Learning App
```

### Pipeline Goals

The pipeline was designed to:

- automate the generation of semantic scaffolding artifacts,
- operate at scale across large corpora,
- coordinate storage and generation processes,
- and support learner interaction through a web interface.

---

## Corpus Design

This project evaluates the pipeline using three major source domains:

### 1. Biblical Texts

Biblical texts served as the primary development corpus because they offer:

- large public-domain multilingual datasets,
- strong structural regularity,
- natural segmentation,
- alignment across translations,
- and a rich historical visual tradition.

### 2. Shakespearean Drama

Shakespearean drama was used to test whether the framework could adapt to literary style, rhetorical density, and older forms of English.

### 3. Technical Writing

Technical writing was used to demonstrate that the framework is not limited to religious or literary material, but can also support structured access to difficult expository content.

Together, these corpora support the broader claim that semantic scaffolding is **domain-flexible**.

---

## Models and Technologies

The project experimented with a range of local and frontier models.

### Text Generation

Used for:

- graded text
- summaries
- vocabulary
- teaching notes
- quizzes

Models explored included:

- Qwen family models
- Gemini models
- Claude models
- Llama models
- GPT-4.1 / GPT-5 family models

### Image Generation

Used for chapter-level illustrations.

Models explored included:

- Stable Diffusion XL
- FLUX Schnell
- Gemini image generation
- OpenAI GPT Image

### Audio Generation

Used for MP3 narration of graded text.

Technologies included:

- Edge TTS
- Internet Archive hosting

### Web Application

The learner-facing application was built with:

- Python
- Streamlit
- SQLite

---

## Learner Application

The learner interacts with the artifacts through a Streamlit-based web interface.

### Learner Features

The application allows learners to:

- choose a language and source text,
- select a CEFR-aligned difficulty level,
- read graded text,
- view summaries,
- listen to audio narration,
- study vocabulary,
- view teaching notes,
- complete quizzes,
- and view illustrative images.

The interface is designed to make the scaffold visible and explorable rather than hiding the learning process behind a single output.

---

## Free Pipeline vs Paid Pipeline

A major practical concern in this project was **scalability**.

### Free Pipeline

The free pipeline used a mixture of:

- local models,
- free-tier frontier APIs,
- and manual or semi-automated orchestration.

Advantages:
- minimal direct cost
- useful for experimentation
- academically sufficient in many cases

Disadvantages:
- slow throughput
- rate limits
- weaker consistency
- more structural failures

### Paid Pipeline

The paid pipeline used OpenAI API infrastructure for structured generation.

Advantages:
- faster generation
- stronger schema compliance
- higher reliability
- easier parallelization

Disadvantages:
- real API cost at scale
- image moderation failures in some chapters
- continued need for validation and repair logic

The practical result is that the project evolved into a **hybrid engineering exercise** in quality, throughput, and cost control.

---

## Image Generation

Image generation was treated as an important part of the multimodal scaffold.

The project experimented with:

- **Stable Diffusion XL (SDXL)** for local generation,
- **FLUX Schnell** for batch-style generation,
- **Gemini image generation**,
- and **OpenAI GPT Image** for high-quality chapter illustrations.

### Design Philosophy

The image system was designed to generate **one representative scene per chapter**, not a full visual retelling.

Images were intended to:

- reinforce learner comprehension,
- provide visual anchoring,
- and create a more immersive pedagogical environment.

### Observed Tradeoffs

#### Stable Diffusion XL
- lower semantic control
- more variable output
- useful but often fragile

#### FLUX Schnell
- more coherent scene control
- stronger prompt interpretation
- better consistency

#### GPT Image / Gemini
- often strongest semantic understanding
- easier one-shot chapter scene generation
- but vulnerable to moderation blocks and API cost

---

## Impact on the UGA Community

This system has practical applications for the University of Georgia community.

Potential uses include:

- helping language learners gradually approach difficult texts,
- supporting students who struggle with dense academic reading,
- generating scaffolded course materials,
- and eventually integrating into learning management systems such as **Brightspace / eLC**.

The broader educational value is that the system can act like an AI-generated, multimodal **study edition** of difficult material.

---

## Limitations

Despite promising results, several limitations remain.

### Current limitations include:

- output quality still depends heavily on the underlying models,
- prompt brittleness across languages,
- occasional JSON/schema failures,
- imperfect quiz distractor generation,
- moderation failures during image generation,
- and cost/time tradeoffs at scale.

The project demonstrates **viability**, not completion.

That is the honest and correct framing.

---

## Conclusion

This project demonstrates that modern generative AI systems can be orchestrated into a coherent pipeline that transforms difficult source texts into structured learning environments.

Its central contribution is not merely simplification, nor merely multimodal generation, nor merely app development.

Its contribution is the integration of these elements into one framework:

## **Semantic Scaffolding**

That framework provides a practical and extensible model for helping learners move from limited understanding toward meaningful comprehension through staged, multimodal support.

---

## References

- León-Paredes, G. A., Alba-Narváez, L. A., & Paltin-Guzmán, K. D. (2025). *NOVA: A Retrieval-Augmented Generation Assistant in Spanish for Parallel Computing Education with Large Language Models*. Applied Sciences, 15(15), 8175.
- Mayer, R. E. (2002). *Multimedia learning*. In *Psychology of Learning and Motivation* (Vol. 41, pp. 85–139). Academic Press.
- Rahman, M. M., Irbaz, M. S., North, K., Williams, M. S., Zampieri, M., & Lybarger, K. (2024). *Health text simplification: An annotated corpus for digestive cancer education and novel strategies for reinforcement learning*. Journal of Biomedical Informatics, 158, 104727.
- Rossetti, A., & Van Waes, L. (2022). *It's not just a phase: Investigating text simplification in a second language from a process and product perspective*. Frontiers in Artificial Intelligence, 5, 983008.
- Siddharthan, A. (2014). *A survey of research on text simplification*. ITL - International Journal of Applied Linguistics, 165(2), 259–298.
- Zhang, X., & Lu, X. (2025). *Aligning linguistic complexity with the difficulty of English texts for L2 learners based on CEFR levels*. Studies in Second Language Acquisition, 1–28.
'''


def image_or_placeholder(title: str, path: str | None = None, caption: str | None = None):
    if path and Path(path).exists():
        st.image(path, width="stretch", caption=caption or title)
    else:
        st.info(
            f"{title}: add an image path here later with st.image(...)."
        )


with st.sidebar:
    st.header("Methodology")
    st.page_link("app.py", label="Back to App", icon="↩️")
    st.download_button(
        label="Download Markdown",
        data=METHOD_TEXT,
        file_name="semantic_scaffolding_methodology.md",
        mime="text/markdown",
        use_container_width=True,
    )
    st.markdown("---")
    st.markdown("**Jump to section**")
    st.caption("Use the tabs in the main area for navigation.")

st.title(TITLE)
st.caption(SUBTITLE)

hero1, hero2, hero3 = st.columns(3)
hero1.metric("Primary Idea", "Semantic scaffolding")
hero2.metric("Core Modes", "Text · Audio · Image · Quiz")
hero3.metric("Primary UI", "Streamlit")

st.info(
    "This page is a Streamlit-native methodology view. It keeps the full paper available, "
    "but also breaks the content into sections that are easier to browse in-app."
)

overview_tab, paper_tab, pipeline_tab, figures_tab, appendix_tab = st.tabs(
    ["Overview", "Paper", "Pipeline", "Figures", "Appendices"]
)

with overview_tab:
    left, right = st.columns([1.2, 1])
    with left:
        st.subheader("What this project does")
        st.markdown(
            """
This system turns difficult source texts into a **learning staircase**.

Instead of giving learners only a simplified version or only the original, the pipeline generates a sequence of intermediate representations that progressively reveal meaning, vocabulary, nuance, and style.

The goal is not merely simplification. The goal is **guided ascent toward comprehension**.
            """
        )
        with st.expander("Read the abstract", expanded=True):
            abstract = METHOD_TEXT.split("## Contributions")[0]
            st.markdown(abstract)
    with right:
        st.subheader("At a glance")
        st.markdown(
            """
- **Conceptual contribution:** semantic scaffolding
- **Pipeline outputs:** graded text, summaries, vocab, notes, quiz, audio, images
- **Target use case:** language learning first, broader comprehension support second
- **Source domains:** biblical text, Shakespeare, technical writing
- **Delivery surface:** interactive Streamlit application
            """
        )
        st.code(
            """Source Text
  -> Graded Levels
  -> Summaries / Vocab / Notes / Quiz
  -> Audio / Images
  -> Streamlit Learning App""",
            language="text",
        )

with paper_tab:
    st.subheader("Full Paper")
    with st.expander("Show full paper", expanded=True):
        st.markdown(METHOD_TEXT)

with pipeline_tab:
    st.subheader("System and pipeline")
    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            st.markdown("### Pipeline goals")
            st.markdown(
                """
- Automate semantic scaffolding artifact generation
- Operate across large corpora
- Preserve structured outputs through validation
- Support multimodal learning in one interface
                """
            )
        with st.container(border=True):
            st.markdown("### Core artifacts")
            st.markdown(
                """
- Graded text
- One-line summary
- Paragraph summary
- Vocabulary list
- Teaching notes
- Quiz
- Audio narration
- Chapter illustration
                """
            )
    with c2:
        with st.container(border=True):
            st.markdown("### Model families explored")
            st.markdown(
                """
- Qwen
- Gemini
- Claude
- Llama
- GPT-4.1 / GPT-5 family
- SDXL
- FLUX
- GPT Image
                """
            )
        with st.container(border=True):
            st.markdown("### Engineering tradeoffs")
            st.markdown(
                """
- Free pipeline: cheaper, slower, less reliable
- Paid pipeline: faster, better structure, real cost
- Images: high value, but moderation and consistency issues remain
- Validation: essential for production-like behavior
                """
            )
    st.divider()
    with st.expander("Corpus design", expanded=False):
        st.markdown(
            """
The project uses three main source domains:

1. **Biblical texts** for multilingual alignment and strong segmentation
2. **Shakespeare** for literary and stylistic difficulty
3. **Technical writing** for expository complexity and generalization
            """
        )
    with st.expander("Free vs paid pipeline", expanded=False):
        st.markdown(
            """
### Free pipeline
Useful for experimentation and broad generation, but slowed heavily by throttling, weaker structure, and reliability issues.

### Paid pipeline
Better schema adherence, faster throughput, and more practical orchestration, but introduces direct API cost and moderation edge cases.
            """
        )
    with st.expander("Limitations", expanded=False):
        st.markdown(
            """
- Model-dependent quality
- Prompt brittleness across languages
- JSON/schema failures
- Imperfect distractors in quizzes
- Image moderation failures
- Cost and runtime constraints at scale
            """
        )

with figures_tab:
    st.subheader("Figures and screenshots")
    st.caption("Screenshots and examples showing pipeline outputs, app interface, and example artifacts.")

    st.markdown("### Figure 1 — App interface")
    image_or_placeholder("App interface screenshot", path="src/assets/figure1.png", caption="Figure 1. Example of the learning interface, designed for a beginner learner of German, showing the language selection (de = Deutsch), image, graded summaries, audio options and vocabulary words for the text.")
    st.markdown("### Figure 2 — App Interface - Shakespeare example")
    image_or_placeholder("Shakespeare screenshot", path="src/assets/figure2.png", caption="Figure 2. Screenshot of the application user interface, selecting Shakespeare's A Comedy of Errors at CEFR Level A1, showing the banner image, summaries, audio controls, act/scene or book/chapter navigation, and the top of the vocab list.")
    st.markdown("### Figure 3 — App Interface - Shakespeare example with vocab and text")
    image_or_placeholder("Shakespeare screenshot", path="src/assets/figure3.png", caption="Figure 3. Screenshot of the application user interface, selecting Shakespeare's A Comedy of Errors in Act 1, Scene 1 at CEFR Level A1, showing the act/scene or book/chapter navigation, the vocab list and content, text options, teachers' notes (buttons) and the start of the graded text.")
    st.markdown("### Figure 4 — App Interface - Shakespeare example with vocab and text")
    image_or_placeholder("Shakespeare screenshot", path="src/assets/figure4.png", caption="Figure 4. Screenshot of the application user interface, selecting Shakespeare's A Comedy of Errors at CEFR Level A1, showing the vocabulary strip, text options, a teachers' note explaining the simplification and a reflection question, and the start of the graded text.")
    
    st.markdown("### Figure 5 — App Interface - Shakespeare example with quiz")
    image_or_placeholder("Shakespeare screenshot", path="src/assets/figure5.png", caption="Figure 5. Screenshot of the application user interface, selecting Shakespeare's A Comedy of Errors at CEFR Level B1, showing the bottom of the graded text, the quiz section (including scoreboard), and a potential new feature - a chat interface where learners can interact with an LLM but only in the selected language, at the selected level, and about the text and/or grammatical or linguistic attributes.")
    
    st.markdown("### Figure 6 — Image Generation Example (ChatGPT)")
    image_or_placeholder("Shakespeare screenshot", path="src/assets/figure6.png", caption="Figure 6. Screenshot from the application user interface, displaying the complete image (from which the banner image is derived). This image is hosted on ImageKit.io's free tier, was generated using Stable Diffusion XL on an Nvidia 4090 GPU, and illustrates the creation event described in Genesis 1, derived from the simplified text of the ASV's AI graded text.")
    
    st.markdown("### Figure 7 — Image Generation Example (Gemini)")
    image_or_placeholder("Shakespeare screenshot", path="src/assets/figure7.png", caption="Figure 7. Screenshot from the application user interface, displaying the complete image (from which the banner image is derived), though this image specifically generated for the German Textbibel text in classic German artistic flair, inspired by famous German artist Albrecht Dürer's wood engraving style. This image is also hosted on ImageKit.io's free tier, was generated by ChatGPT 5.2, similarly illustrating the creation event described in 1 Moses 1 (Genesis 1), derived from the simplified text of the Textbibel's AI graded text.")
    
    st.markdown("### Figure 8 — Image Generation Example (ChatGPT Image 1.5)")
    image_or_placeholder("Shakespeare screenshot", path="src/assets/figure8.png", caption="Figure 8. Screenshot from the application user interface, displaying the complete image (from which the banner image is derived), though this image specifically generated for the Reina Valera (Spanish) biblical text in classic Mesoamerican/Mexican artistic flair, inspired by famous Mexican artist power couple, Diego Rivera and Frida Kahlo. This image was generated by OpenAI's gpt-image-1.5 model, via API) and similarly illustrates the creation event described in Génesis 1 (Genesis chapter 1), derived from the simplified text of the Reina Valera AI graded text, from the perspective of indigenous inhabitants of ancient Mexico.")
    
    st.markdown("### Figure 9 — Image Generation Example (Stable Diffusion XL)")
    image_or_placeholder("Shakespeare screenshot", path="src/assets/figure9.png", caption="Figure 9. This image shows the quality of the Stable Diffusion XL model, which is free, but requires approximately 5 minutes to generate a single image on a GeForce 4090 GPU.")

    st.markdown("### Figure 10 — Image Generation Example (FLUX Schnell)")
    image_or_placeholder("Shakespeare screenshot", path="src/assets/figure10.png", caption="Figure 10. This image shows the quality of the FLUX.Schnell model, which is free, but also requires approximately 5 minutes to generate a single image on Kaggle GPUs.")

with appendix_tab:
    st.subheader("Appendices")
    with st.expander("Appendix A — Example Prompt for Generating Vocab Lists (JSON)", expanded=False):
        st.code(
'''
def resolve_language_name(language: str) -> str:
    return {
        "de": "German",
        "es": "Spanish",
        "en": "English",
        "fr": "French",
    }.get(language, "the target language")

def build_vocab_prompt(
    *,
    level: str,
    language: str,
    graded_text: str
) -> tuple[str, str]:
    """Build system and user prompts for vocab extraction."""
    language_name = resolve_language_name(language)

    system_prompt = f"""
    You are a careful language teacher and data extractor.

    Output MUST be valid JSON that matches the provided JSON schema.
    No markdown, no commentary, no extra keys.

    Hard rules:
    - Only choose vocabulary that appears in the provided graded text.
    - No duplicate headwords. No duplicate forms_in_text across items.
    - If uncertain about lemma/part-of-speech/gloss, SKIP the item (do not guess).
    - Prefer lemmatized headwords (dictionary form):
    - verbs: infinitive
    - nouns: singular nominative (German nouns capitalized)
    - adjectives: positive base form
    - "forms_in_text" must be copied verbatim from the graded text; do not generate or guess additional conjugations. If you only find 1 form, output 1 form.
    - "gloss_simple" must be written in the target language only, simple learner-friendly wording.

    {LEVEL_PROFILES[level]}
    {LEVEL_ADDENDA[level]}
    """.strip()

    LEVEL_ITEM_COUNTS = {
        "A1": (8, 12),
        "A2": (10, 14),
        "B1": (12, 16),
        "B2": (14, 18),
    }

    min_items, max_items = LEVEL_ITEM_COUNTS.get(level, (12, 18))

    user_prompt = PROMPT_TEMPLATE_VOCAB.format(
        language_name=language_name,
        level=level,
        min_items=min_items,
        max_items=max_items,
        graded_block=graded_text,
)

    return system_prompt, user_prompt

PROMPT_TEMPLATE_VOCAB = """
You will receive one graded chapter in {language_name} at CEFR {level}.

Return JSON with one top-level key: "vocab".

Choose {min_items}-{max_items} vocabulary items that are:
- useful and slightly challenging for CEFR {level}
- learnable from context in THIS chapter
- not proper names (people/places), not pronouns, not numbers

Item requirements (each vocab entry):
- headword: lemma/dictionary form
- pos: one of: "noun", "verb", "adjective", "adverb", "expression"
- gloss_simple: a short, simple explanation in {language_name} ONLY
  - 6-14 words
  - do NOT translate into English
  - do NOT just restate the headword
- forms_in_text: list of the exact forms seen in the text (1-4 items)
- example: ONE short sentence in {language_name} that fits the chapter context
  - preferably copied/trimmed from the graded text (no verse numbers)

Selection guidance:
- Prefer content words (actions, emotions, relationships, moral/legal concepts, nature terms).
- Avoid ultra-basic words unless the chapter uses them in a special way.
- Avoid duplicate lemmas and near-synonyms unless clearly distinct.
- If the chapter is genealogy-heavy, focus on recurring verbs/nouns (e.g., “zeugen”, “leben”, “sterben”),
  and avoid listing many names.

Graded chapter text:
{graded_block}
""".strip()

LEVEL_PROFILES = {
    "A1": """
LEVEL STYLE (A1)
- Use very common everyday words.
- Use very short sentences (8-12 words).
- Prefer present/simple past. Avoid complex verb forms.
- Avoid abstract terms; use simple paraphrases.
- Use basic connectors.
""".strip(),

    "A2": """
LEVEL STYLE (A2)
- Use simple, clear language with mostly common words.
- Use simple past/present/future (will). Avoid heavy passive and conditionals.
- Avoid rare abstract terms; paraphrase when needed (e.g., “agreement with God” for “covenant”).
- Use basic connectors: and, but, so, then, after that, because.
""".strip(),

    "B1": """
LEVEL STYLE (B1)
- Do NOT write sequences of short, simple sentences when the ideas are closely related.
  Combine related ideas into natural B1 sentences using connectors or relative clauses.
- Use clear, natural language suitable for intermediate learners.
- Allow moderately complex sentences (aim ~12-18 words on average), but keep readability high.
- Use a wider set of connectors: because, although, however, therefore, while, so that, after, before.
- Prefer precise verbs/nouns over vague fillers:
  Avoid: “bad things”, “good way”, “special thing”, “changed their bodies”.
  Prefer: “violence”, “injustice”, “law”, “covenant/agreement”, “circumcised”, “responsibility”, “punishment”.
- You MAY use essential domain terms when central to meaning (e.g., covenant, altar, sacrifice, prophet, plague),
  but do not overuse them; keep wording simple around them.
- Keep tone neutral and factual; do not add moral commentary beyond what is stated.
- When a verse lists many similar objects, measurements, or repeated details
  (especially tools, materials, or numbers), you MAY summarize them
  in clear B1 language instead of listing every item.
- Preserve the main idea (e.g., destruction, removal, value), not every object name.
- Avoid long noun lists with more than 4 items.
- If the original verse contains a long list, group items using a general term
  (e.g., “many bronze objects used in the Temple”).
- Exact ancient measurements (cubits, fingers, weights) are NOT required at B1
  unless they are central to the meaning.
- You may replace them with approximate descriptions
  (e.g., “very tall,” “very thick,” “extremely heavy”).
  - When verses contain direct speech, preserve dialogue clearly using quotation marks.
- Keep reported speech simple and faithful; do not summarize speeches unless they are repetitive.
- For abstract theological actions (e.g., judgment, mercy, warning),
  prefer clear everyday phrasing used consistently throughout the chapter
  (e.g., “bring disaster,” “change his mind,” “show favor”).
- Do not alternate between many paraphrases for the same idea within one chapter.
- In legal or judgment contexts, use precise but simple terms
  (e.g., innocent, guilty, deserve, responsible).
- Avoid vague placeholders such as “things”, “stuff”, or “something”
  when a clearer noun is available in the original verse.
- Repetition is allowed when it reflects emphasis in the original text.
- Avoid repeating the same verb or phrase in more than two consecutive verses
  unless it is central to the message.
- Each verse SHOULD contain at least one sentence with a connector
  (e.g., because, although, so that, while, when, after)
  unless the verse is extremely short in the original.
- Before finalizing output, verify:
-- The language is clearly more complex than A2 but not academic.
-- Related ideas are usually joined into one sentence, not split.
-- Vocabulary includes some abstract nouns or precise verbs where appropriate.
""".strip(),
"B2": """
LEVEL STYLE (B2)
- Write fluent, connected prose that reflects educated adult reading,
  without becoming academic, literary, or interpretive.
- Sentences may be longer and more layered than B1
  (aim ~16-24 words on average), but must remain clear and well-structured.
- Combine multiple related ideas into a single sentence
  using subordination, contrast, or cause-effect relationships
  rather than splitting them across sentences.
- Use a broad and flexible range of connectors and discourse markers:
  although, however, therefore, nevertheless, meanwhile, whereas,
  as a result, in order that, even though, by contrast, in this way.
- Allow embedded clauses, participial phrases, and conditional structures,
  but avoid excessive nesting that would strain comprehension.
- Use precise and abstract vocabulary naturally:
  justice, authority, repentance, responsibility, consequence,
  covenant, judgment, mercy, corruption, restoration, obedience.
- Prefer exact verbs over descriptive phrases:
  Avoid: “made them suffer,” “did something wrong,” “turned away.”
  Prefer: “oppressed,” “transgressed,” “abandoned,” “withheld,” “declared.”
- Biblical and theological terms MAY be used freely when central
  (e.g., covenant, exile, judgment, prophet, sanctuary, sacrifice, anointed),
  but they must be embedded in clear explanatory language.
- Do NOT assume specialist theological knowledge;
  meaning should be recoverable from context.
- Maintain a neutral, analytical tone.
  Do not preach, moralize, or modernize motivations beyond the text.
- Interpretive clarification is allowed only when the text itself
  clearly implies cause, intention, or consequence.
- When verses contain long lists, repeated measurements, or ritual detail:
  - You MAY summarize efficiently while preserving purpose and function.
  - Preserve distinctions that matter (e.g., sacred vs common, clean vs unclean).
  - Exact measurements and object names may be omitted unless they are central.
- In narrative sections:
  - Vary sentence structure to reflect shifts in action, speech, or tension.
  - Use temporal markers (when, after, while, eventually) to guide flow.
- In legal, prophetic, or judgment contexts:
  - Use clear, formal vocabulary (guilty, innocent, accountable, sentence, decree).
  - Cause-effect relationships should be explicit rather than implied.
- Direct speech should be preserved where present,
  but may be lightly condensed if repetitive,
  provided tone, intent, and authority remain clear.
- Repetition should reflect rhetorical emphasis in the original text,
  not mechanical verse-by-verse paraphrasing.
- Avoid cycling through multiple synonyms for the same key concept
  within a short span unless the original text itself varies.
- Avoid vague placeholders (“things,” “stuff,” “actions,” “events”)
  when the original text specifies meaning or responsibility.
- Before finalizing output, verify:
  -- The language is clearly more advanced than B1 but not academic.
  -- Sentences often contain more than one clause with clear hierarchy.
  -- Abstract ideas are expressed precisely, not emotionally.
  -- The text reads smoothly when read aloud by an educated adult learner.
"""
}

LEVEL_ADDENDA = {
    "A1": """
A1 HARD CONSTRAINTS (must follow)
- Use ONLY very common everyday words.
- Keep sentences very short (aim 8-12 words).
- Prefer present or simple past; avoid complex verb forms.
- Avoid abstract or rare words (e.g., generation, covenant, dominion, righteousness, wickedness).
  Use simple paraphrases instead.
- If a verse is complex, split into 2-3 short sentences rather than one long sentence.
- Keep important names (e.g., Moses, Pharaoh, Egypt, Israel) as written.
""".strip(),

    "A2": """
A2 HARD CONSTRAINTS (must follow)
- Keep sentences short (10-15 words) and avoid long clause chains.
- Use only simple past / simple present / simple future (“will”).
  Avoid passive voice, perfect tenses, conditionals, and heavy subordination unless it's unavoidable.
- Use common, concrete vocabulary. Avoid abstract domain words such as:
  covenant, dominion, righteousness, wickedness, generation.
  If needed, paraphrase simply (e.g., “agreement with God” for “covenant”).
- Avoid idioms and metaphorical phrasing.
- Prefer verbs over abstract nouns (e.g., “nicht gehorchen” instead of “Ungehorsam”).
- Do NOT infer emotions/motivations unless explicitly stated in the verse.
  Example: If the text says "he wept", you may write "he cried".
  If the text does NOT state an emotion, do NOT add one.
- For name lists and genealogies, you MAY use shorter sentences (5-9 words)
  and simple list-style sentences to preserve accuracy.

""".strip(),
    "B1": """
B1 REMINDERS
- Combine closely related ideas; avoid choppy A2-style sentence sequences.
- Use intermediate connectors naturally; keep tone factual and neutral.
""".strip(),

    "B2": """
B2 REMINDERS
- Use fluent, well-structured prose; allow subordination without excessive nesting.
- Keep tone neutral; no preaching or extra interpretation.
""".strip(),
}
''',
            language="python",
        )
    with st.expander("Appendix B — Architecture Diagram", expanded=False):
        st.markdown("### Appendix B — System Architecture Diagram")
        image_or_placeholder("System Architecture Diagram", path="src/assets/appendixB.png", caption="")

    with st.expander("Appendix C — Prompt for ChatGPT and Gemini German Image Generation", expanded=False):
        st.markdown(
"""
***The following prompt was used to generate the images displayed in the German Bible's Genesis (ChatGPT) and Exodus (Gemini) books.***

You are a Renaissance print director and image creator describing, then creating, a 16th century German woodcut engraving image, in the style of Albrecht Dürer.
Your task is to produce a structured engraving specification and image for:
Book: Enter Bible Book Name
Chapter: Enter Chapter Number
ABSOLUTE RULES:
* Figures must have rigid carved anatomy typical of 16th century woodcuts.
* Clothing folds should be structured and engraved, not flowing painterly fabric.
* Landscape must be composed of repeated engraved line patterns, not atmospheric gradient.
* Select ONE single visually dramatic moment from the chapter.
* Depict only one frozen moment (no multiple scenes, no timeline blending).
* Describe only what is visible.
* Do NOT summarize the whole chapter.
* Do NOT explain theology or moral meaning.
* No modern elements.
* All clothing, architecture, and objects must appear medieval German / early 16th century.
* The engraving must be black ink on parchment.
* No color.
* No grayscale wash.
* Shading must be described as dense cross-hatching and engraved linework only.
* Composition must be landscape (640w x 512h orientation).
* Include a short banner title in traditional German script describing the event.
SCENE SELECTION LOGIC:
1. If the chapter contains a divine appearance or dream, depict that moment.
2. Else if it contains confrontation between two main figures, depict the moment of tension between them.
3. Else if it contains travel or wilderness, depict a solitary or small group journey scene.
4. Else depict the most visually dramatic covenant, blessing, or action scene.

Think through these elements:
TITLE_BANNER:
(Short phrase in early modern German tone summarizing the depicted event.)

SCENE_MOMENT:
(One sentence describing the frozen dramatic moment.)

FOREGROUND:
(Primary figure(s), posture, gesture, facial expression, emotional tension.)

MIDGROUND:
(Secondary figure(s) and their interaction.)

BACKGROUND:
(Minimal medieval architectural or landscape setting.)

LIGHTING_AND_SHADOW:
(Describe how contrast, shadow, and divine light are rendered through engraved line density and cross-hatching.)

ENGRAVING_STYLE:
16th century German woodcut engraving, Albrecht Dürer inspired, black ink on parchment, no color, no grayscale, dense cross-hatching, intricate linework, high contrast, sharp contours, Renaissance biblical illustration, landscape orientation 640w x 512h.

Please generate an image using these rules and elements for use in a German Bible.
"""
)

st.divider()
st.caption("Built for the Semantic Scaffolding project.")
