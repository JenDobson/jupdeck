from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE

from notebook_summarizer.core.renderer import PowerPointRenderer


def test_render_markdown_slide(tmp_path):
    parsed = {
        "cells": [{"type": "markdown", "source": "### Hello world"}],
        "metadata": {},
    }
    output_file = tmp_path / "test.pptx"
    renderer = PowerPointRenderer(output_file)
    renderer.render(parsed)

    assert output_file.exists()

    prs = Presentation(output_file)
    assert len(prs.slides) == 1
    assert prs.slides[0].shapes.title.text.startswith("Cell 1")


def test_render_code_cell_with_image(tmp_path):
    minimal_png = (
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwM"
        "CAO+XZhEAAAAASUVORK5CYII="
    )

    parsed = {
        "cells": [
            {
                "type": "code",
                "source": "plt.plot(x, y)",
                "images": [{"mime_type": "image/png", "data": minimal_png}],
            }
        ],
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
        "cells": [{"type": "code", "source": "print('Hello')"}],
        "metadata": {},
    }
    output_file = tmp_path / "code_no_image.pptx"
    renderer = PowerPointRenderer(output_file)
    renderer.render(parsed)

    prs = Presentation(output_file)
    text_shapes = [s for s in prs.slides[0].shapes if s.has_text_frame]
    assert any("print('Hello')" in shape.text for shape in text_shapes)
