import pytest
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE

from notebook_summarizer.core.models import ParsedCell
from notebook_summarizer.core.renderer import PowerPointRenderer, clean_title_line


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("# Title", "Title"),
        ("###  Section 1:", "Section 1"),
        ("## Heading...   ", "Heading"),
        (" #   Cleaned - ", "Cleaned"),
        ("## Data   Exploration -", "Data Exploration"),
        ("#######    Summary     ", "Summary"),
        ("##   Ending.", "Ending"),
        ("###   Overview ---", "Overview"),
        (" #Extra #Hashes #In #Title--", "Extra Hashes In Title"),
    ],
)
def test_clean_title_line_formats(raw, expected):
    assert clean_title_line(raw) == expected


def test_render_markdown_slide(tmp_path):
    parsed = {
        "cells": [ParsedCell(index=0,type="markdown", title="Hello world")],
        "metadata": {},
    }
    output_file = tmp_path / "test.pptx"
    renderer = PowerPointRenderer(output_file)
    renderer.render(parsed)

    assert output_file.exists()

    prs = Presentation(output_file)
    assert len(prs.slides) == 1
    assert prs.slides[0].shapes.title.text.startswith("Hello world")


def test_render_code_cell_with_image(tmp_path):
    minimal_png = (
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwM"
        "CAO+XZhEAAAAASUVORK5CYII="
    )

    parsed = {
        "cells": [ParsedCell(index=0,type="code", 
                             code="plt.plot(x, y)",
                             images=[{"mime_type": "image/png", "data": minimal_png}])],
        "metadata": {},
    }
    output_file = tmp_path / "code_with_image.pptx"
    renderer = PowerPointRenderer(output_file)
    renderer.render(parsed)

    prs = Presentation(output_file)
    assert len(prs.slides) == 1
    slide = prs.slides[0]
    assert any(shape.shape_type == MSO_SHAPE_TYPE.PICTURE for shape in slide.shapes)  # 13 = PICTURE


def test_render_code_cell_without_image(tmp_path):
    parsed = {
        "cells": [ParsedCell(index=0,type="code",code="print('Hello')")],
        "metadata": {},
    }
    output_file = tmp_path / "code_no_image.pptx"
    renderer = PowerPointRenderer(output_file)
    renderer.render(parsed)

    prs = Presentation(output_file)
    text_shapes = [s for s in prs.slides[0].shapes if s.has_text_frame]
    assert any("print('Hello')" in shape.text for shape in text_shapes)


def test_slide_title_from_code_comment_with_image(tmp_path):
    minimal_png = (
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwC"
        "AAAAC0lEQVR42mP8/x8AAwMCAO+XZhEAAAAASUVORK5CYII="
    )

    parsed = {
        "cells": [
            ParsedCell(index=0,
                       type="code",
                       title="This is the title",
                       code="plt.plot(x, y)",
                       images=[{"mime_type": "image/png", "data": minimal_png}])
            ],
        "metadata": {},
        }
    output_file = tmp_path / "comment_with_image.pptx"
    renderer = PowerPointRenderer(output_file)
    renderer.render(parsed)

    prs = Presentation(output_file)
    slide = prs.slides[0]
    assert slide.shapes.title.text == "This is the title"


def test_render_small_table_inline(tmp_path):
    parsed = {
        "cells": [ParsedCell(index=0,
                             type="code",
                             code="df.head()",
                             table={"data": [{"A": 1, "B": 2}, {"A": 3, "B": 4}]})],
        "metadata": {},
    }

    output_file = tmp_path / "small_table.pptx"
    renderer = PowerPointRenderer(output_file)
    renderer.render(parsed)

    prs = Presentation(output_file)
    slide = prs.slides[0]
    tables = [s for s in slide.shapes if s.shape_type == MSO_SHAPE_TYPE.TABLE]
    assert tables, "Expected table to be rendered"
    assert not any("truncated" in s.text for s in slide.shapes if s.has_text_frame)


def test_render_large_table_with_link(tmp_path):
    rows = [{"A": i, "B": i * 2} for i in range(20)]  # 20 rows = large
    parsed = {
        "cells": [ParsedCell(index=0,
                             type="code",
                             code="df",
                             table={"data": rows, "link_file": "full_data.xlsx"})],
        "metadata": {},
    }

    output_file = tmp_path / "large_table.pptx"
    renderer = PowerPointRenderer(output_file)
    renderer.render(parsed)

    prs = Presentation(output_file)
    slide = prs.slides[0]
    textboxes = [s.text for s in slide.shapes if s.has_text_frame]
    assert any("truncated" in text.lower() for text in textboxes)
    assert any("cell_0_table_1.xlsx" in text for text in textboxes)
