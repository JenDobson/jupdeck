#!/usr/bin/env python
"""CLI script to parse a notebook and generate a PowerPoint report."""

import argparse
from pathlib import Path

from jupdeck.core import parser, renderer


def main():
    parser_main = argparse.ArgumentParser(description="JupDeck CLI")
    subparsers = parser_main.add_subparsers(dest="command", required=True)

    # Convert subcommand
    convert_parser = subparsers.add_parser("convert", help="Convert notebook to PowerPoint")
    convert_parser.add_argument("input", type=Path, help="Path to input notebook (.ipynb)")
    convert_parser.add_argument("output", type=Path, help="Path to output PowerPoint file (.pptx)")
    convert_parser.add_argument("--no-speaker-notes", action="store_true", help="Exclude speaker notes from slides")
    convert_parser.add_argument("--no-attribution", action="store_true", help="Exclude attribution from slides")
    
    args = parser_main.parse_args()

    if args.command == "convert":
        # Parse the notebook
        parsed = parser.parse_notebook(args.input)

        # Render to PowerPoint
        ppt_renderer = renderer.PowerPointRenderer(
            output_path = args.output,
            include_speaker_notes = not args.no_speaker_notes,
            include_attribution = not args.no_attribution,
            input_path = args.input
            )
        ppt_renderer.render_presentation(parsed)

        print(f"✅ Report generated: {args.output}")


if __name__ == "__main__":
    main()
