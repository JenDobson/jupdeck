from jupdeck.core.models import ImageData, ParsedCell


def test_merge_cells_combines_all_fields():
    base = ParsedCell(
        type="markdown",
        title="Base Title",
        bullets=["Bullet 1"],
        paragraphs=["Paragraph 1"],
        code="print('Hello')",
        images=[ImageData(mime_type="image/png", data="base64image1")],
        table=[{"col1": "val1"}],
        raw_outputs=[{"output_type": "stream", "text": "Output 1"}],
        metadata={"author": "base"}
    )

    other = ParsedCell(
        type="markdown",
        title=None,
        bullets=["Bullet 2"],
        paragraphs=["Paragraph 2"],
        code=None,
        images=[ImageData(mime_type="image/png", data="base64image2")],
        table=None,
        raw_outputs=[{"output_type": "stream", "text": "Output 2"}],
        metadata={"date": "2025-06-13"}
    )

    merged = base.merge_cells([other])

    assert merged.title == "Base Title"
    assert merged.bullets == ["Bullet 1", "Bullet 2"]
    assert merged.paragraphs == ["Paragraph 1", "Paragraph 2"]
    assert merged.code == "print('Hello')"
    assert len(merged.images) == 2
    assert merged.table == [{"col1": "val1"}]
    assert len(merged.raw_outputs) == 2
    assert merged.metadata["author"] == "base"
    assert merged.metadata["date"] == "2025-06-13"