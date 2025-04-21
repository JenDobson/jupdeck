# renderer.py
"""Render parsed notebook content into a PowerPoint presentation."""

import base64
import io
from pathlib import Path
from typing import Any, Dict

from pptx import Presentation
from pptx.util import Inches, Pt


class PowerPointRenderer:
    def __init__(self, output_path: Path):
        self.output_path = output_path
        self.prs = Presentation()
        self._set_default_layout()

    def _set_default_layout(self):
        # Use blank layout for full control
        self.slide_layout = self.prs.slide_layouts[5]  # Title Only

    def render(self, parsed: Dict[str, Any]):
        for i, cell in enumerate(parsed["cells"]):
            self._render_cell(i, cell)
        self.prs.save(self.output_path)

    def _render_cell(self, index: int, cell: Dict[str, Any]):
        slide = self.prs.slides.add_slide(self.slide_layout)
        title_shape = slide.shapes.title
        title_shape.text = f"Cell {index + 1} ({cell['type']})"

        left = Inches(1)
        top = Inches(1.5)
        width = Inches(8)
        height = Inches(5)

        content = cell.get("source", "")
        if isinstance(content, list):
            content = "".join(content)

        textbox = slide.shapes.add_textbox(left, top, width, height)
        text_frame = textbox.text_frame
        text_frame.word_wrap = True
        p = text_frame.paragraphs[0]
        p.text = content
        p.font.size = Pt(14)

        # Render image(s) if present
        for image in cell.get("images", []):
            if image.get("mime_type") == "image/png" and image.get("data"):
                image_data = base64.b64decode(image["data"])
                image_stream = io.BytesIO(image_data)
                slide.shapes.add_picture(
                    image_stream, left, top + Inches(2.5), width=Inches(4), height=Inches(3)
                )


if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Render notebook to PowerPoint")
    parser.add_argument("input_json", type=Path, help="Path to parsed notebook JSON")
    parser.add_argument("output_pptx", type=Path, help="Path to output PowerPoint file")
    args = parser.parse_args()

    with open(args.input_json, "r", encoding="utf-8") as f:
        parsed_notebook = json.load(f)

    renderer = PowerPointRenderer(args.output_pptx)
    renderer.render(parsed_notebook)
