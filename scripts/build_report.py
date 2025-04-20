#!/usr/bin/env python
"""CLI script to parse a notebook and generate a PowerPoint report."""

import sys
from pathlib import Path

from notebook_summarizer.core import parser, renderer


def main():
    if len(sys.argv) != 3:
        print("Usage: build_report.py <notebook.ipynb> <output.pptx>")
        sys.exit(1)

    notebook_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    # Parse the notebook
    parsed = parser.parse_notebook(notebook_path)

    # Render to PowerPoint
    ppt_renderer = renderer.PowerPointRenderer(output_path)
    ppt_renderer.render(parsed)

    print(f"✅ Report generated: {output_path}")


if __name__ == "__main__":
    main()
