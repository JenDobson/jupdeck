from nbformat.v4 import new_code_cell, new_markdown_cell
from pptx import Presentation

from notebook_summarizer.core.parser import parse_code_cell, parse_markdown_cell
from notebook_summarizer.core.renderer import PowerPointRenderer


def test_can_render_slide_from_markdown(tmp_path):
    cell = new_markdown_cell("# Slide Title\n\nThis is a paragraph with some explanation.")
    parsed = parse_markdown_cell(cell, index=0)

    output_file = tmp_path / "markdown_slide.pptx"
    renderer = PowerPointRenderer(output_file)
    renderer.render({"cells": [parsed], "metadata": {}})

    prs = Presentation(output_file)
    assert len(prs.slides) == 1
    assert "Slide Title" in prs.slides[0].shapes.title.text

def test_can_render_slide_from_code_cell(tmp_path):
    cell = new_code_cell("x = 1 + 1")
    cell["outputs"] = []
    parsed = parse_code_cell(cell, index=0)

    output_file = tmp_path / "code_slide.pptx"
    renderer = PowerPointRenderer(output_file)
    renderer.render({"cells": [parsed], "metadata": {}})

    prs = Presentation(output_file)
    assert len(prs.slides) == 1
    shape_texts = [s.text for s in prs.slides[0].shapes if hasattr(s, "text")]
    assert any("x = 1 + 1" in text for text in shape_texts)
