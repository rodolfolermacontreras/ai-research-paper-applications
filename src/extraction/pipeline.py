"""Main orchestration pipeline for PDF extraction."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from extraction.code_extractor import extract_code_blocks
from extraction.image_extractor import extract_images
from extraction.metadata_extractor import extract_metadata
from extraction.models import PaperAnalysis
from extraction.reference_extractor import extract_references
from extraction.table_extractor import extract_tables
from extraction.text_extractor import extract_text_sections


def run_pipeline(pdf_path: str | Path, output_dir: str | Path) -> PaperAnalysis:
    """Run the complete extraction workflow for a single PDF."""

    pdf = Path(pdf_path)
    output_root = Path(output_dir)
    paper_id = _slugify(pdf.stem)

    text_output_dir = output_root / "extracted" / "text" / paper_id
    image_output_dir = output_root / "extracted" / "images" / paper_id
    table_output_dir = output_root / "extracted" / "tables" / paper_id
    text_output_dir.mkdir(parents=True, exist_ok=True)
    image_output_dir.mkdir(parents=True, exist_ok=True)
    table_output_dir.mkdir(parents=True, exist_ok=True)

    errors: list[str] = []

    try:
        text_data = extract_text_sections(pdf)
    except Exception as exc:
        text_data = {"abstract": "", "full_text": "", "sections": []}
        errors.append(f"text_extractor: {exc}")

    try:
        metadata = extract_metadata(pdf)
    except Exception as exc:
        metadata = extract_metadata_fallback(pdf)
        errors.append(f"metadata_extractor: {exc}")

    if not metadata.abstract:
        metadata.abstract = str(text_data.get("abstract", ""))

    try:
        figures = extract_images(pdf, image_output_dir)
    except Exception as exc:
        figures = []
        errors.append(f"image_extractor: {exc}")

    try:
        tables = extract_tables(pdf, table_output_dir)
    except Exception as exc:
        tables = []
        errors.append(f"table_extractor: {exc}")

    try:
        code_blocks = extract_code_blocks(pdf)
    except Exception as exc:
        code_blocks = []
        errors.append(f"code_extractor: {exc}")

    try:
        reference_data = extract_references(pdf, sections=text_data.get("sections"), full_text=text_data.get("full_text"))
    except Exception as exc:
        reference_data = {"references": [], "in_text_citations": [], "urls": []}
        errors.append(f"reference_extractor: {exc}")

    analysis = PaperAnalysis(
        paper_id=paper_id,
        pdf_path=str(pdf),
        output_dir=str(output_root),
        metadata=metadata,
        abstract=str(text_data.get("abstract", "")) or metadata.abstract,
        full_text=str(text_data.get("full_text", "")),
        sections=list(text_data.get("sections", [])),
        figures=figures,
        tables=tables,
        code_blocks=code_blocks,
        references=list(reference_data.get("references", [])),
        in_text_citations=list(reference_data.get("in_text_citations", [])),
        urls=list(reference_data.get("urls", [])),
        errors=errors,
    )

    _write_text_outputs(text_output_dir, analysis)
    return analysis


def analyze_paper(pdf_path: str, output_dir: str) -> dict[str, Any]:
    """Analyze a paper PDF and return a JSON-serializable dictionary."""

    return run_pipeline(pdf_path, output_dir).to_dict()


def extract_metadata_fallback(pdf_path: Path) -> Any:
    """Create a minimal metadata payload when extraction fails."""

    return extract_metadata(pdf_path)


def _write_text_outputs(output_dir: Path, analysis: PaperAnalysis) -> None:
    sections_payload = [asdict(section) for section in analysis.sections]
    figures_payload = [asdict(figure) for figure in analysis.figures]
    tables_payload = [asdict(table) for table in analysis.tables]
    code_payload = [asdict(block) for block in analysis.code_blocks]
    references_payload = [asdict(reference) for reference in analysis.references]

    (output_dir / "metadata.json").write_text(json.dumps(asdict(analysis.metadata), indent=2), encoding="utf-8")
    (output_dir / "abstract.txt").write_text(analysis.abstract, encoding="utf-8")
    (output_dir / "full_text.txt").write_text(analysis.full_text, encoding="utf-8")
    (output_dir / "sections.json").write_text(json.dumps(sections_payload, indent=2), encoding="utf-8")
    (output_dir / "figures.json").write_text(json.dumps(figures_payload, indent=2), encoding="utf-8")
    (output_dir / "tables.json").write_text(json.dumps(tables_payload, indent=2), encoding="utf-8")
    (output_dir / "code_blocks.json").write_text(json.dumps(code_payload, indent=2), encoding="utf-8")
    (output_dir / "references.json").write_text(
        json.dumps(
            {
                "references": references_payload,
                "in_text_citations": analysis.in_text_citations,
                "urls": analysis.urls,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (output_dir / "analysis.json").write_text(json.dumps(analysis.to_dict(), indent=2), encoding="utf-8")


def _slugify(value: str) -> str:
    cleaned = "".join(character if character.isalnum() else "_" for character in value)
    return "_".join(part for part in cleaned.split("_") if part).lower()
