"""Tests for the PDF extraction pipeline and related modules."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

import pytest

# Ensure src/ is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from extraction.models import (
    CodeBlock,
    Figure,
    PaperAnalysis,
    PaperMetadata,
    Reference,
    Section,
    Table,
)

PAPERS_DIR = Path(__file__).resolve().parent.parent / "Papers"

PAPER_1 = PAPERS_DIR / "2605.01172v1 A Theory of Generalization in Deep Learning.pdf"
PAPER_2 = PAPERS_DIR / "2605.23904v2 SkillOpt Self Evolving Agent Skills.pdf"


def _skip_if_no_papers():
    """Skip tests when PDF files are not available."""
    if not PAPER_1.exists() or not PAPER_2.exists():
        pytest.skip("PDF files not available")


# ---------------------------------------------------------------------------
# Model serialization
# ---------------------------------------------------------------------------

class TestModels:
    def test_paper_metadata_defaults(self):
        meta = PaperMetadata()
        assert meta.title == ""
        assert meta.authors == []
        assert meta.date is None
        assert meta.keywords == []

    def test_section_fields(self):
        sec = Section(title="Intro", content="Hello", page_start=1, page_end=2, level=1)
        assert sec.title == "Intro"
        assert sec.level == 1

    def test_paper_analysis_to_dict(self):
        analysis = PaperAnalysis(
            paper_id="test",
            pdf_path="test.pdf",
            output_dir="out",
            metadata=PaperMetadata(title="Test"),
            abstract="abs",
            full_text="full",
        )
        d = analysis.to_dict()
        assert isinstance(d, dict)
        assert d["paper_id"] == "test"
        assert d["metadata"]["title"] == "Test"

    def test_reference_defaults(self):
        ref = Reference(raw_text="Some ref")
        assert ref.authors == []
        assert ref.doi is None

    def test_code_block_fields(self):
        cb = CodeBlock(language="python", content="x=1", page_number=3)
        assert cb.language == "python"
        assert cb.page_number == 3


# ---------------------------------------------------------------------------
# Text extractor
# ---------------------------------------------------------------------------

class TestTextExtractor:
    @pytest.fixture(autouse=True)
    def _check_papers(self):
        _skip_if_no_papers()

    def test_paper_1_sections_reduced(self):
        from extraction.text_extractor import extract_text_sections
        result = extract_text_sections(str(PAPER_1))
        sections = result["sections"]
        # Was 191 before fix; should now be under 70
        assert len(sections) < 70, f"Expected <70 sections, got {len(sections)}"
        assert len(sections) >= 10, f"Too few sections: {len(sections)}"

    def test_paper_1_has_abstract(self):
        from extraction.text_extractor import extract_text_sections
        result = extract_text_sections(str(PAPER_1))
        assert result["abstract"], "Abstract should not be empty"
        assert len(result["abstract"]) > 100

    def test_paper_1_has_full_text(self):
        from extraction.text_extractor import extract_text_sections
        result = extract_text_sections(str(PAPER_1))
        assert len(result["full_text"]) > 1000

    def test_paper_2_sections_reasonable(self):
        from extraction.text_extractor import extract_text_sections
        result = extract_text_sections(str(PAPER_2))
        sections = result["sections"]
        assert len(sections) >= 5
        assert len(sections) < 40
        titles = [s.title for s in sections]
        assert any("method" in t.lower() or "experiment" in t.lower() for t in titles)

    def test_sections_have_content(self):
        from extraction.text_extractor import extract_text_sections
        result = extract_text_sections(str(PAPER_2))
        for section in result["sections"]:
            assert section.content, f"Section '{section.title}' has no content"
            assert section.page_start >= 1
            assert section.page_end >= section.page_start


# ---------------------------------------------------------------------------
# Image extractor
# ---------------------------------------------------------------------------

class TestImageExtractor:
    @pytest.fixture(autouse=True)
    def _check_papers(self):
        _skip_if_no_papers()

    def test_paper_1_has_raster_images(self):
        from extraction.image_extractor import extract_images
        with tempfile.TemporaryDirectory() as tmpdir:
            figures = extract_images(str(PAPER_1), tmpdir)
            assert len(figures) > 0, "Paper 1 should have raster images"
            for fig in figures:
                assert Path(fig.file_path).exists()
                assert fig.width >= 100
                assert fig.height >= 100

    def test_paper_2_has_vector_figures(self):
        from extraction.image_extractor import extract_images
        with tempfile.TemporaryDirectory() as tmpdir:
            figures = extract_images(str(PAPER_2), tmpdir)
            assert len(figures) > 0, "Paper 2 should have vector-rendered figures"
            for fig in figures:
                assert Path(fig.file_path).exists()
                assert fig.file_path.endswith(".png")

    def test_figure_metadata(self):
        from extraction.image_extractor import extract_images
        with tempfile.TemporaryDirectory() as tmpdir:
            figures = extract_images(str(PAPER_1), tmpdir)
            for fig in figures:
                assert fig.page_number >= 1
                assert fig.width > 0
                assert fig.height > 0


# ---------------------------------------------------------------------------
# Table extractor
# ---------------------------------------------------------------------------

class TestTableExtractor:
    @pytest.fixture(autouse=True)
    def _check_papers(self):
        _skip_if_no_papers()

    def test_paper_1_extracts_tables(self):
        from extraction.table_extractor import extract_tables
        with tempfile.TemporaryDirectory() as tmpdir:
            tables = extract_tables(str(PAPER_1), tmpdir)
            assert len(tables) > 0, "Paper 1 should have tables"

    def test_table_files_created(self):
        from extraction.table_extractor import extract_tables
        with tempfile.TemporaryDirectory() as tmpdir:
            tables = extract_tables(str(PAPER_1), tmpdir)
            for table in tables:
                assert Path(table.csv_path).exists(), f"CSV not found: {table.csv_path}"
                assert Path(table.markdown_path).exists(), f"Markdown not found: {table.markdown_path}"

    def test_table_metadata(self):
        from extraction.table_extractor import extract_tables
        with tempfile.TemporaryDirectory() as tmpdir:
            tables = extract_tables(str(PAPER_1), tmpdir)
            for table in tables:
                assert table.rows > 0
                assert table.columns > 0
                assert table.page_number >= 1
                assert table.source in ("pymupdf", "pdfplumber")


# ---------------------------------------------------------------------------
# Code extractor
# ---------------------------------------------------------------------------

class TestCodeExtractor:
    @pytest.fixture(autouse=True)
    def _check_papers(self):
        _skip_if_no_papers()

    def test_paper_1_extracts_code(self):
        from extraction.code_extractor import extract_code_blocks
        blocks = extract_code_blocks(str(PAPER_1))
        assert len(blocks) > 0

    def test_code_block_fields(self):
        from extraction.code_extractor import extract_code_blocks
        blocks = extract_code_blocks(str(PAPER_1))
        for block in blocks:
            assert block.content.strip()
            assert block.page_number >= 1


# ---------------------------------------------------------------------------
# Reference extractor
# ---------------------------------------------------------------------------

class TestReferenceExtractor:
    @pytest.fixture(autouse=True)
    def _check_papers(self):
        _skip_if_no_papers()

    def test_paper_2_extracts_references(self):
        from extraction.reference_extractor import extract_references
        result = extract_references(str(PAPER_2))
        refs = result["references"]
        assert len(refs) > 10, f"Expected >10 references, got {len(refs)}"

    def test_reference_has_raw_text(self):
        from extraction.reference_extractor import extract_references
        result = extract_references(str(PAPER_2))
        for ref in result["references"]:
            assert ref.raw_text.strip()

    def test_urls_extracted(self):
        from extraction.reference_extractor import extract_references
        result = extract_references(str(PAPER_2))
        urls = result["urls"]
        assert isinstance(urls, list)


# ---------------------------------------------------------------------------
# Metadata extractor
# ---------------------------------------------------------------------------

class TestMetadataExtractor:
    @pytest.fixture(autouse=True)
    def _check_papers(self):
        _skip_if_no_papers()

    def test_paper_1_metadata(self):
        from extraction.metadata_extractor import extract_metadata
        meta = extract_metadata(str(PAPER_1))
        assert meta.title, "Title should not be empty"
        assert len(meta.title) > 5

    def test_paper_2_metadata(self):
        from extraction.metadata_extractor import extract_metadata
        meta = extract_metadata(str(PAPER_2))
        assert meta.title


# ---------------------------------------------------------------------------
# Pipeline integration
# ---------------------------------------------------------------------------

class TestPipeline:
    @pytest.fixture(autouse=True)
    def _check_papers(self):
        _skip_if_no_papers()

    def test_full_pipeline_paper_2(self):
        from extraction.pipeline import run_pipeline
        with tempfile.TemporaryDirectory() as tmpdir:
            result = run_pipeline(str(PAPER_2), tmpdir)
            assert result.paper_id
            assert len(result.sections) > 0
            assert len(result.figures) > 0
            assert len(result.references) > 0
            assert result.full_text, "Full text should not be empty"
            # Check output files
            text_dir = Path(tmpdir) / "extracted" / "text" / result.paper_id
            assert (text_dir / "analysis.json").exists()
            analysis = json.loads((text_dir / "analysis.json").read_text(encoding="utf-8"))
            assert analysis["paper_id"] == result.paper_id


# ---------------------------------------------------------------------------
# HTML one-pager
# ---------------------------------------------------------------------------

class TestHtmlOnepager:
    def test_generate_onepager(self):
        from analysis.html_onepager import generate_onepager
        summaries_dir = Path(__file__).resolve().parent.parent / "output" / "summaries"
        md_files = list(summaries_dir.glob("*.md"))
        if not md_files:
            pytest.skip("No summary markdown files available")
        with tempfile.TemporaryDirectory() as tmpdir:
            path = generate_onepager(str(md_files[0]), Path(tmpdir) / "test.html")
            html_content = Path(path).read_text(encoding="utf-8")
            assert html_content.startswith("<!DOCTYPE html>")
            assert "</html>" in html_content
            assert "<h1>" in html_content

    def test_generate_all_onepagers(self):
        from analysis.html_onepager import generate_all_onepagers
        summaries_dir = Path(__file__).resolve().parent.parent / "output" / "summaries"
        md_files = list(summaries_dir.glob("*.md"))
        if not md_files:
            pytest.skip("No summary markdown files available")
        with tempfile.TemporaryDirectory() as tmpdir:
            paths = generate_all_onepagers(str(summaries_dir), tmpdir)
            assert len(paths) == len(md_files)
            for p in paths:
                assert Path(p).exists()
                assert Path(p).suffix == ".html"

    def test_onepager_missing_file_raises(self):
        from analysis.html_onepager import generate_onepager
        with pytest.raises(FileNotFoundError):
            generate_onepager("nonexistent_file.md")
