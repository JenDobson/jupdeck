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

