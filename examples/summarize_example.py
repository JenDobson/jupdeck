"""Example usage of the notebook summarizer API."""
from notebook_summarizer.core import parser, summarizer, exporter

notebook_path = "../notebooks/demo_notebook.ipynb"
cells = parser.extract_notebook_content(notebook_path)
summary = summarizer.summarize_content(cells)
exporter.export_to_html(summary, "summary.html")
