# renderer.py
"""Render parsed notebook content into a PowerPoint presentation."""

import base64
import io
import re
from pathlib import Path
from typing import Any, Dict

import pandas as pd
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE
from pptx.enum.text import MSO_AUTO_SIZE
from pptx.util import Inches, Pt


def clean_title_line(line: str) -> str:
    """Strip # characters, normalize whitespace, and remove
    trailing punctuation from a title line."""
    line = re.sub(r"#", "", line)
    line = re.sub(r"\s+", " ", line).strip()
    line = re.sub(r"[:\.\-]+$", "", line)
    return line.strip()


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
            self._render_cell(cell)
        self.prs.save(self.output_path)

    def _render_cell(self, cell: Dict[str, Any]):
        slide = self.prs.slides.add_slide(self.slide_layout)
        title_shape = slide.shapes.title

        # Determine slide title
        title = ""
        if cell.type == "markdown":
            lines = cell.get("source", "").splitlines()
            if lines:
                title = clean_title_line(lines[0])

        elif cell.type == "code":
            lines = cell.code.splitlines()
            for line in lines:
                if line.strip().startswith("#"):
                    title = clean_title_line(line)
                    break  # use the first comment line only

        # Only set title if one was found
        if title:
            title_shape.text = title
        else:
            # Remove the placeholder if no title
            slide.shapes._spTree.remove(title_shape._element)

        left = Inches(1)
        top = Inches(1.5)
        width = Inches(8)
        height = Inches(5)

        content = cell.paragraphs + cell.bullets
        if isinstance(content, list):
            content = "".join(content)

        textbox = slide.shapes.add_textbox(left, top, width, height)
        text_frame = textbox.text_frame
        text_frame.word_wrap = True
        p = text_frame.paragraphs[0]
        p.text = content
        p.font.size = Pt(14)

        # Render image(s) if present
        for image in cell.images:
            if image.get("mime_type") == "image/png" and image.get("data"):
                image_data = base64.b64decode(image["data"])
                image_stream = io.BytesIO(image_data)
                slide.shapes.add_picture(
                    image_stream, left, top + Inches(2.5), width=Inches(4), height=Inches(3)
                )

        if cell.table:
            self._render_table_to_slide(slide, cell.table)

    def _render_table_to_slide(self, slide, cell: dict):
        rows = cell.get("data", [])

        if not rows or not isinstance(rows, list):
            return  # nothing to render

        headers = list(rows[0].keys())
        n_rows = len(rows)
        n_cols = len(headers)

        is_large = n_rows > 10 or n_cols > 6
        link_file = None

        # Limit number of rows shown if large
        max_display_rows = 10 if is_large else n_rows
        display_rows = rows[:max_display_rows]

        # Add table shape
        left = Inches(0.5)
        top = Inches(1.5)
        width = Inches(9)
        height = Inches(5)

        table_shape = slide.shapes.add_table(
            len(display_rows) + 1, n_cols, left, top, width, height
        ).table

        # Header row
        for col_idx, header in enumerate(headers):
            table_shape.cell(0, col_idx).text = str(header)

        # Data rows
        for row_idx, row in enumerate(display_rows):
            for col_idx, header in enumerate(headers):
                table_shape.cell(row_idx + 1, col_idx).text = str(row.get(header, ""))

        if is_large:
            table_idx = len([s for s in slide.shapes if s.shape_type == MSO_SHAPE_TYPE.TABLE])
            index = cell.get("index", 0)
            link_file = f"cell_{index}_table_{table_idx}.xlsx"
            xlsx_path = self.output_path.with_name(link_file)

            textbox = slide.shapes.add_textbox(Inches(0.5), Inches(0.5), Inches(9), Inches(0.5))
            text_frame = textbox.text_frame
            text_frame.text = f"⚠️ Table truncated. See full data in '{link_file}'"
            text_frame.paragraphs[0].font.size = Pt(12)
            text_frame.auto_size = MSO_AUTO_SIZE.SHAPE_TO_FIT_TEXT

            df = pd.DataFrame(rows)

            df.to_excel(xlsx_path, index=False)


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
