"""Dataclasses for PDF extraction results."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class PaperMetadata:
    """Structured metadata extracted from a research paper PDF."""

    title: str = ""
    authors: list[str] = field(default_factory=list)
    date: str | None = None
    keywords: list[str] = field(default_factory=list)
    abstract: str = ""
    pdf_metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class Section:
    """A logical document section extracted from the paper text."""

    title: str
    content: str
    page_start: int
    page_end: int
    level: int = 1


@dataclass(slots=True)
class Figure:
    """Metadata for an extracted figure or image."""

    file_path: str
    page_number: int
    width: int
    height: int
    bbox: tuple[float, float, float, float] | None = None
    caption: str | None = None


@dataclass(slots=True)
class Table:
    """Metadata for an extracted table."""

    csv_path: str
    markdown_path: str
    page_number: int
    rows: int
    columns: int
    bbox: tuple[float, float, float, float] | None = None
    headers: list[str] = field(default_factory=list)
    source: str = ""


@dataclass(slots=True)
class CodeBlock:
    """A code snippet detected within the PDF."""

    language: str | None
    content: str
    page_number: int
    context: str = ""
    bbox: tuple[float, float, float, float] | None = None


@dataclass(slots=True)
class Reference:
    """A parsed bibliography entry."""

    raw_text: str
    authors: list[str] = field(default_factory=list)
    title: str | None = None
    year: str | None = None
    venue: str | None = None
    doi: str | None = None
    url: str | None = None


@dataclass(slots=True)
class PaperAnalysis:
    """Comprehensive analysis output produced by the extraction pipeline."""

    paper_id: str
    pdf_path: str
    output_dir: str
    metadata: PaperMetadata
    abstract: str
    full_text: str
    sections: list[Section] = field(default_factory=list)
    figures: list[Figure] = field(default_factory=list)
    tables: list[Table] = field(default_factory=list)
    code_blocks: list[CodeBlock] = field(default_factory=list)
    references: list[Reference] = field(default_factory=list)
    in_text_citations: list[str] = field(default_factory=list)
    urls: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert the analysis dataclass tree into plain Python objects."""

        return asdict(self)
