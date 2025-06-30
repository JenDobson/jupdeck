# parser.py
"""Functions to parse .ipynb files."""

import io
from pathlib import Path
from typing import Any, Dict, List

import mistune
import nbformat
import pandas as pd

from jupdeck.core.models import ImageData, ParsedCell


def load_notebook(notebook_path: Path) -> nbformat.NotebookNode:
    """Load a Jupyter notebook from a file path."""
    with notebook_path.open("r", encoding="utf-8") as f:
        return nbformat.read(f, as_version=4)

def parse_notebook(notebook_path: Path) -> Dict[str, Any]:
    """Full notebook parsing pipeline."""
    nb = load_notebook(notebook_path)
    cell_data = extract_cells(nb)
    return {"metadata": nb.metadata, "cells": cell_data}

def extract_cells(nb: nbformat.NotebookNode) -> List[ParsedCell]:
    """Parse all notebook cells into a list of ParsedCell objects."""
    parsed = []

    for cell in nb.cells:
        cell_type = cell.get("cell_type")

        if cell_type == "markdown":
            parsed_cell = parse_markdown_cell(cell)
        elif cell_type == "code":
            parsed_cell = parse_code_cell(cell)
        else:
            # Optionally skip or log unsupported cell types
            continue

        parsed.append(parsed_cell)
        
    return parsed



def parse_code_cell(cell) -> ParsedCell:
    outputs = cell.get("outputs", [])
    images = []
    table = None

    for output in outputs:
        if output.get("output_type") in ("display_data", "execute_result"):
            img_data = output.get("data", {}).get("image/png")
            if img_data:
                images.append(ImageData(mime_type="image/png", data=img_data))

            html = output.get("data", {}).get("text/html")
            if html and "<table" in html:
                try:
                    dfs = pd.read_html(io.StringIO(html))
                    if dfs:
                        table = dfs[0].to_dict(orient="records")
                except Exception:
                    pass  # Silently ignore if read_html fails

    return ParsedCell(
        type="code",
        code=cell.get("source", "").strip(),
        images=images,
        table=table,
        raw_outputs=outputs,
    )

def parse_markdown_cell(cell) -> ParsedCell:
    markdown = mistune.create_markdown(renderer="ast")
    ast = markdown(cell.source)

    title = None
    bullets = []
    paragraphs = []
    images = []

    for node in ast:
        if node["type"] == "heading" and node.get("attrs",{}).get("level") == 1 and not title:
            # Grab first H1 as title
            title = flatten_ast_as_text(node.get("children", []))
        elif node["type"] == "heading" and node.get("attrs",{}).get("level") != 1:
            paragraphs.append(flatten_ast_as_text(node.get("children", [])))
        elif node["type"] == "paragraph":
            for child in node.get("children", []):
                if child["type"] == "image":
                    url = child.get("attrs", {}).get("url", "")
                    if url and url.startswith("data:image/"):
                        try:
                            header, bytestring = url.split(",", 1)
                            images.append(
                                ImageData(mime_type="image/png", 
                                          data=bytestring))
                        except Exception:
                            pass  # skip images that cannot be decoded
            paragraphs.append(flatten_ast_as_text(node.get("children", [])))
        elif node["type"] == "list":
            for item in node.get("children", []):
                if item["type"] == "list_item":
                    bullets.append(flatten_ast_as_text(item.get("children", [])))
        

    return ParsedCell(
        type="markdown",
        title=title,
        bullets=bullets,
        paragraphs=paragraphs,
        images=images
    )

def flatten_ast_as_text(children):
    parts = []
    for child in children:
        ctype = child.get("type")
        if ctype == "text":
            parts.append(child.get("raw", child.get("text", "")).strip())
        elif ctype == "link":
            label = flatten_ast_as_text(child.get("children", []))
            url = child.get("attrs", {}).get("url", "")
            parts.append(f"{label} ({url})")
        elif ctype in ("paragraph", "block_text", "list_item", "strong", "emphasis"):
            inner = flatten_ast_as_text(child.get("children", []))
            parts.append(inner)
        elif "children" in child:
            parts.append(flatten_ast_as_text(child["children"]))
    return " ".join(parts).strip()

if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(
        description="Parse a Jupyter notebook and print structured output."
    )
    parser.add_argument("notebook_path", type=Path, help="Path to the Jupyter .ipynb file")
    args = parser.parse_args()

    parsed = parse_notebook(args.notebook_path)
    print(json.dumps(parsed, indent=2, ensure_ascii=False))
