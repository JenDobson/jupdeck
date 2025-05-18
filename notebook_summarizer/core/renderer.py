# renderer.py
"""Render parsed notebook content into a PowerPoint presentation."""

import base64
import io
import re
from pathlib import Path
from typing import List

import pandas as pd
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE_TYPE
from pptx.enum.text import MSO_AUTO_SIZE
from pptx.util import Inches, Pt

from notebook_summarizer.core.models import ParsedCell


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

    def render_slides(self, cells: List[ParsedCell]) -> None:
        """
        Render a list of ParsedCell objects into a PowerPoint presentation.
        """
        # Type check: ensure cells is a list of ParsedCell instances
        if not isinstance(cells, list) or not all(isinstance(cell, ParsedCell) for cell in cells):
            raise TypeError(
                f"cells must be a list of ParsedCell instances, got {type(cells).__name__} with element types: "
                f"{[type(cell).__name__ for cell in cells] if isinstance(cells, list) else 'N/A'}"
            )
        for cell in cells:
            self._render_cell(cell)
        
        self.prs.save(self.output_path)

    def render_presentation(self, parsed_notebook: dict) -> None:
        """
        Render a parsed notebook dictionary into a PowerPoint presentation.
        Expects a dict with keys 'metadata' and 'cells'.
        """
        if not isinstance(parsed_notebook, dict):
            raise TypeError(f"parsed_notebook must be a dict, got {type(parsed_notebook).__name__}")
        parsed_cells = parsed_notebook.get("cells", [])
        if not isinstance(parsed_cells, list):
            raise TypeError(f"'cells' must be a list, got {type(parsed_cells).__name__}")
        self.render_slides(parsed_cells)
        self.prs.save(self.output_path)

    def _render_cell(self, cell: ParsedCell):
        slide = self.prs.slides.add_slide(self.slide_layout)
        
        title_shape = slide.shapes.title
        title_shape.text = cell.title if cell.title else ""
        
        left = Inches(1)
        top = Inches(1.5)
        width = Inches(9)
        height = Inches(5)

        # Render paragraphs
        paragraph_top = top
        paragraph_left = left
        paragraph_width = Inches(5)
        paragraph_height = Inches(3)
        for paragraph in cell.paragraphs:
            p = slide.shapes.add_textbox(
                paragraph_left, paragraph_top, paragraph_width, paragraph_height
                ).text_frame.paragraphs[0]
            p.text = paragraph
            p.font.size = Pt(14)
            p.space_after = Pt(14)
            paragraph_top = paragraph_top + Inches(0.5)  # Move down for next paragraph
    
        # Render bullets
        if cell.bullets:
            bullet_box = slide.shapes.add_textbox(
                paragraph_left, paragraph_top, paragraph_width, paragraph_height
            )
            text_frame = bullet_box.text_frame
            text_frame.word_wrap = True

            for i, bullet in enumerate(cell.bullets):
                if i == 0:
                    p = text_frame.paragraphs[0]  # Use the default paragraph
                else:
                    p = text_frame.add_paragraph()

                p.text = bullet
                p.level = 0  # Top-level bullet
                p.font.size = Pt(14)
                p.space_after = Pt(6)
                p.space_before = Pt(2)
                p.bullet = True
                
            paragraph_top += Inches(0.5)  # Move down to avoid overlap

        # Render code
        if cell.code:
            code_box = slide.shapes.add_textbox(
                paragraph_left, paragraph_top, paragraph_width, paragraph_height
            )
            text_frame = code_box.text_frame
            text_frame.word_wrap = True

            p = text_frame.paragraphs[0]
            p.text = cell.code
            p.font.size = Pt(12)
            p.font.name = "Courier New"
            p.font.bold = True
            p.space_after = Pt(6)
            p.space_before = Pt(2)
            p.bullet = False
            paragraph_top += Inches(0.5)
            
            fill = code_box.fill
            fill.solid()
            fill.fore_color.rgb = RGBColor(230, 230, 230)  # Light gray background

        
        # Render image(s) if present
        image_top = top
        image_left = left + width / 2
        image_width = Inches(5)
        image_height = Inches(3)
        for image in cell.images:
            if image.mime_type == "image/png" and image.data:
                image_data = base64.b64decode(image.data)
                image_stream = io.BytesIO(image_data)
                slide.shapes.add_picture(
                    image_stream, image_left, image_top, width=image_width, height=image_height
                )
                image_top = image_top + Inches(0.5)  # Move down for next image

        if cell.table:
            self._render_table_to_slide(slide, cell.table, cell.index)

    def _render_table_to_slide(self, slide, table_data: list, cell_index: int = 0):


        if not table_data or not isinstance(table_data, list):
            return  # nothing to render

        headers = list(table_data[0].keys())
        n_rows = len(table_data)
        n_cols = len(headers)

        is_large = n_rows > 10 or n_cols > 6
        link_file = None

        # Limit number of table_data shown if large
        max_display_rows = 10 if is_large else n_rows
        display_rows = table_data[:max_display_rows]

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

        # Data table_data
        for row_idx, row in enumerate(display_rows):
            for col_idx, header in enumerate(headers):
                table_shape.cell(row_idx + 1, col_idx).text = str(row.get(header, ""))

        if is_large:
            table_idx = len([s for s in slide.shapes if s.shape_type == MSO_SHAPE_TYPE.TABLE])
            
            link_file = f"cell_{cell_index}_table_{table_idx}.xlsx"
            xlsx_path = self.output_path.with_name(link_file)

            textbox = slide.shapes.add_textbox(Inches(0.5), Inches(0.5), Inches(9), Inches(0.5))
            text_frame = textbox.text_frame
            text_frame.text = f"⚠️ Table truncated. See full data in '{link_file}'"
            text_frame.paragraphs[0].font.size = Pt(12)
            text_frame.auto_size = MSO_AUTO_SIZE.SHAPE_TO_FIT_TEXT

            df = pd.DataFrame(table_data)

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
    renderer.render_presentation(parsed_notebook)
