from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional


@dataclass
class ImageData:
    mime_type: str
    data: str  # base64-encoded image string

@dataclass
class SlideContent:
    title: Optional[str]
    layout_hint: str = "auto"  # e.g. "text_left_image_right", "full_image", "bullets"
    bullets: List[str] = field(default_factory=list)
    paragraphs: List[str] = field(default_factory=list)
    code: Optional[str] = None
    images: List[ImageData] = field(default_factory=list)
    table: Optional[List[Dict[str, Any]]] = None
    notes: Optional[str] = None  # Speaker notes
    source_cell_index: Optional[int] = None  # For traceability/debugging

@dataclass
class ParsedCell:
    type: Literal["markdown", "code"]
    title: Optional[str] = None         # e.g., from markdown heading
    bullets: List[str] = field(default_factory=list)  # extracted from markdown
    paragraphs: List[str] = field(default_factory=list)  # raw or interpreted prose
    code: Optional[str] = None          # source code (cleaned or annotated)
    images: List[ImageData] = field(default_factory=list)  # base64 or file path
    table: Optional[List[Dict[str, Any]]] = None  # structured table data
    raw_outputs: Optional[List[Dict[str, Any]]] = None  # full outputs if needed
    metadata: Dict[str, Any] = field(default_factory=dict)  # magic commands, tags

    def merge_cells(self, others: List["ParsedCell"]) -> "ParsedCell":
        merged_bullets = self.bullets[:]
        merged_paragraphs = self.paragraphs[:]
        merged_images = self.images[:]
        merged_raw_outputs = self.raw_outputs[:] if self.raw_outputs else []

        final_table = self.table
        for other in others:
            merged_bullets.extend(other.bullets)
            merged_paragraphs.extend(other.paragraphs)
            merged_images.extend(other.images)
            if other.raw_outputs:
                merged_raw_outputs.extend(other.raw_outputs)
            if not final_table and other.table:
                final_table = other.table

        merged_metadata = {**self.metadata}
        for other in others:
            merged_metadata.update(
                {k: v for k, v in other.metadata.items() if k not in merged_metadata})

        return ParsedCell(
            type=self.type,
            title=self.title,
            bullets=merged_bullets,
            paragraphs=merged_paragraphs,
            code=self.code,
            images=merged_images,
            table=final_table,
            raw_outputs=merged_raw_outputs,
            metadata=merged_metadata
        )
