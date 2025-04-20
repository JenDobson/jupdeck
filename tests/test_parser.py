import nbformat
import pytest
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

from notebook_summarizer.core import parser


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
        outputs = result["cells"][0]["outputs"]
        assert any(out.get("name") == "stdout" for out in outputs)
        assert any(out.get("name") == "stderr" for out in outputs)

    def test_parse_notebook_with_empty_output(self, make_notebook):
        cell = new_code_cell(source="x = 1 + 1", execution_count=2, outputs=[])
        nb_content = new_notebook(cells=[cell])
        path = make_notebook(nb_content, "empty_output_notebook.ipynb")
        result = parser.parse_notebook(path)
        assert result["cells"][0]["type"] == "code"
        assert result["cells"][0]["outputs"] == []

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
        outputs = result["cells"][0]["outputs"]
        assert outputs[0]["output_type"] == "error"
        assert outputs[0]["ename"] == "ZeroDivisionError"


class TestNotebookMarkdownParsing:
    def test_parse_notebook_with_nonstring_markdown(self, make_notebook):
        cell = new_markdown_cell(source="# Heading Line 1\nMore text on line 2")
        nb_content = new_notebook(cells=[cell])
        path = make_notebook(nb_content, "nonstring_markdown.ipynb")
        result = parser.parse_notebook(path)
        assert result["cells"][0]["type"] == "markdown"
        assert "Heading Line 1" in result["cells"][0]["source"]
