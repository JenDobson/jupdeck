import nbformat
import pytest
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

from notebook_summarizer.core import parser
from notebook_summarizer.core.models import ParsedCell


@pytest.fixture
def make_notebook(tmp_path):
    def _make(nb_content: nbformat.NotebookNode, filename: str = "test_notebook.ipynb"):
        path = tmp_path / filename
        notebook_node = nbformat.from_dict(nb_content)
        with path.open("w", encoding="utf-8") as f:
            nbformat.write(notebook_node, f)
        return path

    return _make

class TestNotebookOutputParsing:
    def test_parse_notebook_with_stdout_and_stderr(self, make_notebook):
        cell = new_code_cell(
            source="print('Hello')\nraise Exception('Error')",
            execution_count=1,
            outputs=[
                {"output_type": "stream", "name": "stdout", "text": "This is standard output\n"},
                {"output_type": "stream", "name": "stderr", "text": "This is an error message\n"},
            ],
        )
        nb_content = new_notebook(cells=[cell])
        path = make_notebook(nb_content, "stdout_stderr_output.ipynb")
        result = parser.parse_notebook(path)
        outputs = result["cells"][0].raw_outputs
        assert any(out.get("name") == "stdout" for out in outputs)
        assert any(out.get("name") == "stderr" for out in outputs)

    def test_parse_notebook_with_empty_output(self, make_notebook):
        cell = new_code_cell(source="x = 1 + 1", execution_count=2, outputs=[])
        nb_content = new_notebook(cells=[cell])
        path = make_notebook(nb_content, "empty_output_notebook.ipynb")
        result = parser.parse_notebook(path)
        parsed_cell = result["cells"][0]
        assert parsed_cell.type == "code"
        assert not parsed_cell.raw_outputs

    def test_parse_notebook_with_error_output(self, make_notebook):
        cell = new_code_cell(
            source="1 / 0",
            execution_count=3,
            outputs=[
                {
                    "output_type": "error",
                    "ename": "ZeroDivisionError",
                    "evalue": "division by zero",
                    "traceback": [
                        "Traceback (most recent call last):",
                        '  File "<stdin>", line 1, in <module>',
                        "ZeroDivisionError: division by zero",
                    ],
                }
            ],
        )
        nb_content = new_notebook(cells=[cell])
        path = make_notebook(nb_content, "error_output_notebook.ipynb")
        result = parser.parse_notebook(path)
        parsed_cell = result["cells"][0]
        outputs = parsed_cell.raw_outputs
        assert outputs[0]["output_type"] == "error"
        assert outputs[0]["ename"] == "ZeroDivisionError"

    def test_parse_notebook_with_image_output(self, make_notebook):
        # Minimal base64-encoded PNG (1x1 black pixel)
        minimal_png = (
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAAAAAA6fptVAAAACklEQVR4nGNgYA"
            "AAAAMAAWgmWQ0AAAAASUVORK5CYII="
        )
        cell = new_code_cell(
            source="plt.plot(x, y)",
            execution_count=1,
            outputs=[
                {"output_type": "display_data", "data": {"image/png": minimal_png}, "metadata": {}}
            ],
        )
        nb_content = new_notebook(cells=[cell])
        path = make_notebook(nb_content, "image_output_notebook.ipynb")
        result = parser.parse_notebook(path)
        parsed_cell = result["cells"][0]

        assert parsed_cell.type == "code"
        assert parsed_cell.images
        assert len(parsed_cell.images) == 1
        assert parsed_cell.images[0].mime_type == "image/png"
        assert parsed_cell.images[0].data == minimal_png

    def test_parser_extracts_table_from_html_output(self, make_notebook):
        # Simulate pandas DataFrame HTML output
        html_table = """
        <table>
        <thead>
            <tr><th>name</th><th>score</th></tr>
        </thead>
        <tbody>
            <tr><td>Alice</td><td>95</td></tr>
            <tr><td>Bob</td><td>88</td></tr>
        </tbody>
        </table>
        """

        cell = new_code_cell(
            source="df.head()",
            outputs=[
                {
                    "output_type": "execute_result",
                    "data": {"text/html": html_table},
                    "metadata": {},
                    "execution_count": 1,
                }
            ],
        )

        nb_content = new_notebook(cells=[cell])
        path = make_notebook(nb_content, "table_test.ipynb")
        result = parser.parse_notebook(path)
        parsed_cell = result["cells"][0]

        assert parsed_cell.table[0] == {"name": "Alice", "score": 95}
        assert parsed_cell.table[1] == {"name": "Bob", "score": 88}


class TestNotebookMarkdownParsing:
    def test_parse_notebook_with_nonstring_markdown(self, make_notebook):
        cell = new_markdown_cell(source="# Heading Line 1\nMore text on line 2")
        nb_content = new_notebook(cells=[cell])
        path = make_notebook(nb_content, "nonstring_markdown.ipynb")
        result = parser.parse_notebook(path)
        parsed_cell = result["cells"][0]
        assert parsed_cell.type == "markdown"
        assert "Heading Line 1" in parsed_cell.title
        assert "More text on line 2" in parsed_cell.paragraphs[0]


class TestCellParsing:
    def test_parse_markdown_cell_heading_and_body(self):
        md_text = """# Overview

This notebook presents monthly trends in regional unemployment.
"""

        cell = new_markdown_cell(source=md_text)
        parsed = parser.parse_markdown_cell(cell)

        assert isinstance(parsed, ParsedCell)
        assert parsed.type == "markdown"
        assert parsed.title == "Overview"
        assert parsed.paragraphs == ["This notebook presents monthly trends in regional unemployment."]
        assert parsed.bullets == []
        assert parsed.code is None

    def test_parse_markdown_cell_with_link(self):
        md_text = """# Data Sources

This analysis uses [BLS unemployment data](https://www.bls.gov/data/) for all calculations.
"""

        cell = new_markdown_cell(source=md_text)
        parsed = parser.parse_markdown_cell(cell)

        assert parsed.title == "Data Sources"
        assert len(parsed.paragraphs) == 1

        paragraph = parsed.paragraphs[0]
        assert "BLS unemployment data" in paragraph
        assert "https://www.bls.gov" in paragraph  # Confirm we're including the raw URL
        assert "for all calculations" in paragraph

    def test_parse_markdown_cell_with_bullets(self):
        md_text = """# Key Findings

- Unemployment fell in 8 of 10 regions
- Tech sector shows 3% recovery
- Seasonal adjustment applied to all series
"""

        cell = new_markdown_cell(source=md_text)
        parsed = parser.parse_markdown_cell(cell)

        assert isinstance(parsed, ParsedCell)
        assert parsed.title == "Key Findings"
        assert parsed.bullets == [
            "Unemployment fell in 8 of 10 regions",
            "Tech sector shows 3% recovery",
            "Seasonal adjustment applied to all series"
        ]
        assert parsed.paragraphs == []  # No standalone paragraphs in this case

    def test_parse_markdown_cell_with_paragraphs_and_bullets(self):
        md_text = """# Introduction

This notebook demonstrates parsing.

* Bullet 1
* Bullet 2
* Bullet 3

With another paragraph at the end
"""
            
        cell = new_markdown_cell(source = md_text)
        parsed = parser.parse_markdown_cell(cell)

        assert isinstance(parsed, ParsedCell)
        assert parsed.title == "Introduction"
        assert parsed.bullets == [
            "Bullet 1",
            "Bullet 2",
            "Bullet 3"
        ]
        assert parsed.paragraphs == [
            "This notebook demonstrates parsing.",
            "With another paragraph at the end"
        ]  # No standalone paragraphs in this case

    def test_parse_markdown_cell_with_bullets_and_links(self):
        md_text = """# Data Source

- Summary statistics available
- See [BLS](https://bls.gov) for details
- More info at [OECD](https://www.oecd.org/)
"""

        cell = new_markdown_cell(source=md_text)
        parsed = parser.parse_markdown_cell(cell)

        assert isinstance(parsed, ParsedCell)
        assert parsed.title == "Data Source"
        assert parsed.bullets == [
            "Summary statistics available",
            "See BLS (https://bls.gov) for details",
            "More info at OECD (https://www.oecd.org/)"
        ]
        assert parsed.paragraphs == []


    def test_parse_markdown_cell_with_directives(self):
        md_text = """
<!-- slide: new-->
# Sample Analysis Notebook
This notebook demonstrates a basic data analysis workflow using Python. We'll begin by exploring a sample dataset, visualizing the raw data, and performing a linear regression analysis to uncover trends.
"""
        cell = new_markdown_cell(source=md_text)
        parsed = parser.parse_markdown_cell(cell)

        assert parsed.title == "Sample Analysis Notebook"
        assert parsed.paragraphs == [
            "This notebook demonstrates a basic data analysis workflow using Python. We'll begin by exploring a sample dataset, visualizing the raw data, and performing a linear regression analysis to uncover trends."
        ]
