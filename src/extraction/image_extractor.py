"""Image extraction utilities for research paper PDFs."""

from __future__ import annotations

import re
from pathlib import Path

import fitz

from extraction.models import Figure


def extract_images(pdf_path: str | Path, output_dir: str | Path) -> list[Figure]:
    """Extract embedded images from a PDF and save them to disk.

    Uses two strategies:
    1. Extract raster images via ``get_images()``.
    2. For pages with vector-drawn figures but no raster images, render the
       page region as a PNG using ``get_pixmap()``.
    """

    pdf = Path(pdf_path)
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)

    document = fitz.open(pdf)
    paper_id = _slugify(pdf.stem)
    figures: list[Figure] = []
    pages_with_raster: set[int] = set()

    # Strategy 1: raster image extraction
    for page_index in range(document.page_count):
        page = document[page_index]
        page_number = page_index + 1
        page_images = page.get_images(full=True)

        for image_index, image_info in enumerate(page_images, start=1):
            xref = int(image_info[0])
            extracted = document.extract_image(xref)
            width = int(extracted.get("width", 0))
            height = int(extracted.get("height", 0))
            if width < 100 or height < 100:
                continue

            extension = extracted.get("ext", "png")
            image_bytes = extracted.get("image", b"")
            rects = page.get_image_rects(xref)
            if not rects:
                rects = [fitz.Rect(0, 0, float(width), float(height))]

            for rect_index, rect in enumerate(rects, start=1):
                file_name = f"{paper_id}_page_{page_number:03d}_figure_{image_index:02d}_{rect_index:02d}.{extension}"
                image_path = destination / file_name
                image_path.write_bytes(image_bytes)
                figures.append(
                    Figure(
                        file_path=str(image_path),
                        page_number=page_number,
                        width=width,
                        height=height,
                        bbox=(float(rect.x0), float(rect.y0), float(rect.x1), float(rect.y1)),
                    )
                )
                pages_with_raster.add(page_number)

    # Strategy 2: render pages that have vector figures but no raster images
    for page_index in range(document.page_count):
        page = document[page_index]
        page_number = page_index + 1
        if page_number in pages_with_raster:
            continue

        if not _page_has_vector_figures(page):
            continue

        pixmap = page.get_pixmap(dpi=200)
        file_name = f"{paper_id}_page_{page_number:03d}_rendered.png"
        image_path = destination / file_name
        pixmap.save(str(image_path))
        figures.append(
            Figure(
                file_path=str(image_path),
                page_number=page_number,
                width=pixmap.width,
                height=pixmap.height,
                bbox=(0.0, 0.0, float(page.rect.width), float(page.rect.height)),
                caption=f"Rendered page {page_number} (contains vector figures)",
            )
        )

    return figures


_FIGURE_LABEL_RE = re.compile(r"\b(?:Figure|Fig\.)\s+\d", re.IGNORECASE)


def _page_has_vector_figures(page: fitz.Page) -> bool:
    """Return True if the page likely contains a vector-drawn figure."""
    text = page.get_text()
    has_figure_label = bool(_FIGURE_LABEL_RE.search(text))
    drawings = page.get_drawings()
    has_many_drawings = len(drawings) >= 20
    return has_figure_label or has_many_drawings


def _slugify(value: str) -> str:
    cleaned = "".join(character if character.isalnum() else "_" for character in value)
    return "_".join(part for part in cleaned.split("_") if part).lower()
