#!/usr/bin/env python
"""CLI script to parse a notebook and generate a PowerPoint report."""

import argparse
from pathlib import Path

from jupdeck.core import parser, renderer


def main():

    parser_arg = argparse.ArgumentParser(description="Parse a notebook and render a PowerPoint report.")
    parser_arg.add_argument("notebook", type=Path, help="Path to input notebook (.ipynb)")
    parser_arg.add_argument("output", type=Path, help="Path to output PowerPoint file (.pptx)")
    parser_arg.add_argument("--no-speaker-notes", action="store_true", help="Exclude speaker notes from slides")
    args = parser_arg.parse_args()

    notebook_path = args.notebook
    output_path = args.output

    # Parse the notebook
    parsed = parser.parse_notebook(notebook_path)

    # Render to PowerPoint
    ppt_renderer = renderer.PowerPointRenderer(
        output_path = output_path,
        include_speaker_notes = not args.no_speaker_notes)
    ppt_renderer.render_presentation(parsed)

    print(f"✅ Report generated: {output_path}")


if __name__ == "__main__":
    main()
