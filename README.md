
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

- [x] Parse notebook structure and outputs
- [x] Generate PowerPoint slide decks
- [ ] Embed output graphics in slides
- [ ] Convert markdown to bullet points
- [ ] Move prose and notes to speaker notes
- [ ] Optional PDF rendering
- [ ] Group slides by sections / headings
- [ ] Add unique cell IDs for database referencing
- [ ] Store notebook-level metadata (author, kernel, timestamps)
- [ ] Normalize parsed schema for chatbot-ready knowledge indexing
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
