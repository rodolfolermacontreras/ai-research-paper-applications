"""Table extraction utilities for research paper PDFs."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import fitz
import pandas as pd
import pdfplumber

from extraction.models import Table


def extract_tables(pdf_path: str | Path, output_dir: str | Path) -> list[Table]:
    """Extract tables from a PDF using PyMuPDF with a pdfplumber fallback."""

    pdf = Path(pdf_path)
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)

    paper_id = _slugify(pdf.stem)
    document = fitz.open(pdf)
    extracted_tables: list[Table] = []
    seen_signatures: set[str] = set()

    with pdfplumber.open(pdf) as plumber_document:
        for page_index in range(document.page_count):
            page_number = page_index + 1
            page = document[page_index]
            page_tables = _extract_tables_with_pymupdf(page)
            if not page_tables:
                page_tables = _extract_tables_with_pdfplumber(plumber_document.pages[page_index])

            for table_index, table_data in enumerate(page_tables, start=1):
                dataframe = _to_dataframe(table_data.get("data"))
                if dataframe.empty:
                    continue
                signature = dataframe.to_csv(index=False)
                if signature in seen_signatures:
                    continue
                seen_signatures.add(signature)

                csv_path = destination / f"{paper_id}_page_{page_number:03d}_table_{table_index:02d}.csv"
                markdown_path = destination / f"{paper_id}_page_{page_number:03d}_table_{table_index:02d}.md"
                dataframe.to_csv(csv_path, index=False)
                markdown_path.write_text(_dataframe_to_markdown(dataframe), encoding="utf-8")

                extracted_tables.append(
                    Table(
                        csv_path=str(csv_path),
                        markdown_path=str(markdown_path),
                        page_number=page_number,
                        rows=int(dataframe.shape[0]),
                        columns=int(dataframe.shape[1]),
                        bbox=table_data.get("bbox"),
                        headers=[str(column) for column in dataframe.columns],
                        source=table_data.get("source", ""),
                    )
                )

    return extracted_tables


def _extract_tables_with_pymupdf(page: fitz.Page) -> list[dict[str, Any]]:
    try:
        found = page.find_tables()
    except Exception:
        return []

    tables = getattr(found, "tables", [])
    results: list[dict[str, Any]] = []
    for table in tables:
        try:
            data = table.extract()
        except Exception:
            continue
        if not data:
            continue
        bbox = tuple(float(value) for value in getattr(table, "bbox", (0.0, 0.0, 0.0, 0.0)))
        results.append({"data": data, "bbox": bbox, "source": "pymupdf"})
    return results


def _extract_tables_with_pdfplumber(page: pdfplumber.page.Page) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for table in page.extract_tables() or []:
        if not table:
            continue
        results.append({"data": table, "bbox": None, "source": "pdfplumber"})
    return results


def _to_dataframe(table_data: Any) -> pd.DataFrame:
    if not table_data:
        return pd.DataFrame()

    rows = [["" if value is None else str(value).strip() for value in row] for row in table_data if row]
    rows = [row for row in rows if any(cell for cell in row)]
    if not rows:
        return pd.DataFrame()

    header = rows[0]
    body = rows[1:] if len(rows) > 1 else []
    if len(set(header)) != len(header) or any(not cell for cell in header):
        header = [f"column_{index + 1}" for index in range(len(rows[0]))]
        body = rows

    normalized_body = [row + [""] * (len(header) - len(row)) for row in body]
    return pd.DataFrame(normalized_body, columns=header)


def _dataframe_to_markdown(dataframe: pd.DataFrame) -> str:
    headers = [str(column) for column in dataframe.columns]
    separator = ["---"] * len(headers)
    lines = [f"| {' | '.join(headers)} |", f"| {' | '.join(separator)} |"]
    for _, row in dataframe.iterrows():
        values = [str(value).replace("\n", " ") for value in row.tolist()]
        lines.append(f"| {' | '.join(values)} |")
    return "\n".join(lines)


def _slugify(value: str) -> str:
    cleaned = "".join(character if character.isalnum() else "_" for character in value)
    return "_".join(part for part in cleaned.split("_") if part).lower()
