"""Unit tests for CLI."""



import json
import subprocess

from pptx import Presentation


def test_cli_creates_pptx(tmp_path):
    input_data = {
        "metadata": {},
        "cells": [
            {
                "type": "markdown",
                "title": "Demo Slide",
                "paragraphs": ["This is a test."],
                "bullets": [],
                "images": [],
                "table": None,
                "raw_outputs": None,
                "code": None,
                "metadata": {},
            }
        ]
    }
    input_file = tmp_path / "test_notebook.json"
    output_file = tmp_path / "test_output.pptx"

    input_file.write_text(json.dumps(input_data))

    subprocess.run(
        ["python", "notebook_summarizer/core/renderer.py", str(input_file), str(output_file)],
        check=True,
    )

    assert output_file.exists()
    prs = Presentation(str(output_file))
    assert len(prs.slides) == 1

def test_cli_no_speaker_notes(tmp_path):
    input_data = {
        "metadata": {},
        "cells": [
            {
                "type": "markdown",
                "title": "Demo Slide",
                "paragraphs": ["Speaker note should not appear."],
                "bullets": [],
                "images": [],
                "table": None,
                "raw_outputs": None,
                "code": None,
                "metadata": {},
            }
        ]
    }
    input_file = tmp_path / "test_notebook.json"
    output_file = tmp_path / "test_output.pptx"

    input_file.write_text(json.dumps(input_data))

    subprocess.run(
        ["python", "notebook_summarizer/core/renderer.py", str(input_file), str(output_file), "--no-speaker-notes"],
        check=True,
    )

    assert output_file.exists()
    prs = Presentation(str(output_file))
    notes_text = prs.slides[0].notes_slide.notes_text_frame.text
    assert "Speaker note should not appear." not in notes_text
