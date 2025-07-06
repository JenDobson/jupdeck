
# JupDeck Roadmap

This roadmap outlines the phased development plan for the JupDeck tool. The goal is to build a system that transforms Jupyter Notebooks into professional PowerPoint presentations, supporting data science reporting, executive summaries, and technical documentation.

### 1: Baseline Slide Generator

**Goal**: Prove core functionality: parse notebooks and render working PowerPoint output with embedded graphics.

**Features**:
- [x] Parse notebook markdown structure and code cell outputs
- [x] Generate PowerPoint slide decks (`.pptx`)
- [x] Embed output graphics (e.g., plots, images, tables) into slides with generic/simple formatting
- [x] PyPI and GitHub releases with versioning

**Notes**:
"User in the loop" for clean up of formated slides necessary

---
### 2:  Notebook Slide Directives

**Goal**: Interpret slide layout directives from Jupyter notebooks

**Features**:
- [] Rudimentary directives can be embedded as html-comments in markdown cells
- [] Directives control simple formatting, e.g. "New Slide", "Hide Tables"

---
### 3: Improved Layouts

**Goal**: Automatically Adapt Slide Layouts

**Features**:
- [] 3 different content slide layouts offered plus intro / ending layouts
- [] Layout rules encoded in reusable config file
- [] During slide rendering, best layout for slide chosen based on contents
- [] Format validation during rendering (e.g. image resolution, text overflow)

---
### 4: Custom Theming and Templates
**Goal**: Use Custom Styling Templates and Themes

**Features**:
- [] Choose between 3 custom styling templates (e.g. dark mode, corporate, academic)
- [] Add user-defined templates

---
### 5: Custom Content Filtering
**Goal**: Generate different decks depending on audience

**Features**:
- [] Directives mark content for different rendering scenarios (e.g. technical vs. non-technical, internal vs. external)  
- [] Command-line flag controls rendering scenario and generates appropriate deck (e.g. `jupdeck input.ipynb --theme internal --no-code`)
- [] Reusable configuration profiles (YAML) 
---
### 6: VS Code Plugin
**Goal**: Notebook rendering from VS Code
- [] Plugin allows notebook rendering from VS Code interface
- [] Plugin provides suggestions during notebook editing

---

### 7: Basic LLM Editing Support

**Goal**: Use LLMs for editing support
**Features**:
- [] Summarize markdown into concise, audience-appropriate bullets
- [] Align slide tone with target audience (e.g. "executive-friendly", "technical peer review")
---
### 8: LLM Slide Enhancement
- [] Integrate conversational interface to notebook
- [] Auto-suggest slide titles and bullets from raw code/markdown
- [] Validate presentation claims against content: "This model seems to be overfit", "This chart does not support the title claim"
---
### 9: Team Collaboration & Workflow Integration

**Goal**: Support real-world enterprise workflows

- [] GitHub Actions to auto-render slides from notebooks on PR merge
- [] Enable shared template libraries across teams
- [] Add comments/annotations for reviewer workflows
