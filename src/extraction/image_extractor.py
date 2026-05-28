"""Image extraction utilities for research paper PDFs."""

from __future__ import annotations

from pathlib import Path

import fitz

from extraction.models import Figure


def extract_images(pdf_path: str | Path, output_dir: str | Path) -> list[Figure]:
    """Extract embedded images from a PDF and save them to disk."""

    pdf = Path(pdf_path)
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)

    document = fitz.open(pdf)
    paper_id = _slugify(pdf.stem)
    figures: list[Figure] = []

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

    return figures


def _slugify(value: str) -> str:
    cleaned = "".join(character if character.isalnum() else "_" for character in value)
    return "_".join(part for part in cleaned.split("_") if part).lower()
