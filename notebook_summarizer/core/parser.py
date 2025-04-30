# parser.py
"""Functions to parse .ipynb files."""

import io
from pathlib import Path
from typing import Any, Dict, List

import nbformat
import pandas as pd


def load_notebook(notebook_path: Path) -> nbformat.NotebookNode:
    """Load a Jupyter notebook from a file path."""
    with notebook_path.open("r", encoding="utf-8") as f:
        return nbformat.read(f, as_version=4)


def extract_cells(nb: nbformat.NotebookNode) -> List[Dict[str, Any]]:
    """Extract relevant data from notebook cells in a structured format."""
    parsed = []
    for idx, cell in enumerate(nb.cells):
        cell_type = cell.get("cell_type")
        base = {
            "index": idx,
            "type": cell_type,
            "source": cell.source.strip(),
            "outputs": [],
        }
        if cell_type == "code":
            outputs = cell.get("outputs", [])
            images = []
            table = []
            for output in outputs:
                if output.get("output_type") == "display_data":
                    img_data = output.get("data", {}).get("image/png")
                    if img_data:
                        images.append(
                            {
                                "mime_type": "image/png",
                                "data": img_data,
                            }
                        )
                    # Try to extract table from HTML output
                html = output.get("data", {}).get("text/html")
                if html and "<table" in html:
                    try:
                        dfs = pd.read_html(io.StringIO(html))
                        if dfs:
                            table = {"data": dfs[0].to_dict(orient="records")}
                    except Exception:
                        pass  # Silently ignore if read_html fails

                base["outputs"].append(output)

            if images:
                base["images"] = images

            if table:
                base["table"] = table

        parsed.append(base)
    return parsed


def parse_notebook(notebook_path: Path) -> Dict[str, Any]:
    """Full notebook parsing pipeline."""
    nb = load_notebook(notebook_path)
    cell_data = extract_cells(nb)
    return {"metadata": nb.metadata, "cells": cell_data}


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
