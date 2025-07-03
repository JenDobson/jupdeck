# 📘 JupDeck

**Convert Jupyter notebooks to Presentation-Ready Slide Decks.**

Ideal for:
- Technical consultants
- Data scientists
- Instructors
- Teams presenting notebook work to non-technical stakeholders
---

## What It Does

This tool transforms `.ipynb` notebooks into structured `.pptx` presentations.

- **Markdown Headers** become slide titles
- **Markdown Bullets** become slide bullets.
- **Plots and Tables** become slide graphics.
- **Markdown Text** becomes speaker notes.

---

## Quick Start

Pip install the package:
`pip install jupdeck`

Convert a notebook to slides:

`jupdeck convert examples/data/jupdeck_overview.ipyng outputs/output.pptx`

---

## Why?

Jupyter notebooks are fantastic for exploratory work — but hard to present clearly. This tool turns notebook narratives into shareable reports for clients, collaborators, and classrooms.

---

## Development & Testing

```bash
poetry run pytest         # Run test suite
poetry run pre-commit run --all-files  # Run linters and formatters
```

---

## Roadmap

See the [JupDeck Roadmap](./ROADMAP.md) for upcoming features and ideas.

---

## License

Apache License 2.0 — permissive for personal, educational, and commercial use. (See `LICENSE` file)
