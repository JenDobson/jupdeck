
# 📘 Notebook Summarizer

**Convert Jupyter notebooks into clean, client-friendly PowerPoint presentations — automatically.**

---

## 🚀 What It Does

This tool transforms `.ipynb` notebooks into structured `.pptx` presentations.

- 📄 **Markdown cells** become slides with formatted text
- 🧠 **Code cells** appear as readable blocks (graphics support coming soon)
- 📊 **Output cells** will soon be replaced with charts and images

Ideal for:
- Technical consultants
- Data scientists
- Instructors
- Teams presenting notebook work to non-technical stakeholders

---

## 📸 Example Output

```
notebook.ipynb  →  notebook_summary.pptx
```

Slides are created 1:1 with each notebook cell:
- Markdown → Slide title & bullets
- Code → Slide body (or image preview, coming soon)
- Outputs → (Planned: embedded figures or tables)

---

## ⚙️ How to Use It

1. Clone the repo and install dependencies:

```bash
poetry install --with dev
```

2. Run the end-to-end tool:

```bash
poetry run python scripts/build_report.py path/to/notebook.ipynb output.pptx
```

---

## 🛣️ Roadmap

## Notebook Summarizer MVP Roadmap

This roadmap outlines the phased development plan for the Notebook Summarizer tool. The goal is to build a system that transforms Jupyter Notebooks into professional PowerPoint presentations, supporting data science reporting, executive summaries, and technical documentation.

### MVP-1: Core Technology Proof (Est. 56 hrs)

**Goal**: Prove core functionality—parse notebooks, summarize code, and render a working PowerPoint output with embedded graphics.

**Features**:
- [x] Parse notebook structure and outputs (code, markdown, output cells)
- [x] Generate PowerPoint slide decks (`.pptx`)
- [x] Embed output graphics (e.g., plots, images) into slides
- [ ] Embed output tables into slides
- [ ] Summarize code cells using LLM into bullet points
- [ ] Store basic notebook-level metadata (author, kernel, timestamps)
- [ ] (Optional) Export to PDF via PowerPoint

---

### MVP-2: Differentiation Layer (Est. 60 hrs)

**Goal**: Add features that differentiate the product from notebook-to-slide tools like Mercury, RISE, and Quarto.

**Features**:
- [ ] Templated intro/outro slides (e.g., executive summary, conclusions)
- [ ] Slide layout/styling themes (corporate, academic, dark mode)
- [ ] Slide format validation (e.g., image resolution, text overflow)
- [ ] Normalize parsed output schema for chatbot-ready indexing
- [ ] Export speaker notes as script/briefing document
- [ ] UX toggle: “executive mode” (hide raw code, emphasize presentation)

---

### MVP-Pro: Polish & Scale (Est. 70 hrs)

**Goal**: Add polish, user experience enhancements, and early ecosystem integrations to support broader adoption and reusability.

**Features**:
- [ ] Optional voiceover notes per slide (text-to-speech or speaker script sync)
- [ ] Themed animations and transitions (PowerPoint-level polish)
- [ ] Automated metrics (slide count, section coverage, etc.)
- [ ] Drag-and-drop custom slide ordering (UI or slide map file)
- [ ] Preset corporate themes (e.g., with logo, custom footer, fonts)
- [ ] Export leads to CRM or newsletter integration

---

**Total Estimated Time**: ~186 hrs across all phases  
**Cadence**: ~15 hrs/week over 3–4 months
---

## 💡 Why?

Jupyter notebooks are fantastic for exploratory work — but hard to present clearly. This tool turns notebook narratives into shareable reports for clients, collaborators, and classrooms.

---

## 🧪 Development & Testing

```bash
poetry run pytest         # Run test suite
poetry run pre-commit run --all-files  # Run linters and formatters
```

---

## 📄 License

MIT License — you are free to use, share, and modify. (See `LICENSE` file)
