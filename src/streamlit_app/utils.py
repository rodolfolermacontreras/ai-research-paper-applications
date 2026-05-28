from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Iterable, Sequence

import fitz
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
PAPERS_DIR = REPO_ROOT / "Papers"
OUTPUT_DIR = REPO_ROOT / "output"
SUMMARIES_DIR = OUTPUT_DIR / "summaries"
EXTRACTED_DIR = OUTPUT_DIR / "extracted"
IMAGES_DIR = EXTRACTED_DIR / "images"
TABLES_DIR = EXTRACTED_DIR / "tables"
TEXT_DIR = EXTRACTED_DIR / "text"
WIKI_DIR = OUTPUT_DIR / "wiki"
CODE_APPLICATIONS_DIR = OUTPUT_DIR / "code_applications"

CODE_EXTENSIONS = {
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".java",
    ".go",
    ".rs",
    ".cpp",
    ".c",
    ".cs",
    ".rb",
    ".php",
    ".swift",
    ".kt",
    ".scala",
    ".r",
    ".sql",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".sh",
    ".ps1",
    ".html",
    ".css",
    ".md",
}

TABLE_EXTENSIONS = {".csv", ".tsv", ".json", ".xlsx", ".xls", ".parquet"}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}
TEXT_EXTENSIONS = {".md", ".txt"}


@dataclass(frozen=True)
class PaperMetadata:
    name: str
    stem: str
    path: Path
    page_count: int
    size_bytes: int
    analyzed: bool


@dataclass(frozen=True)
class TableResult:
    name: str
    data: pd.DataFrame
    path: Path


@dataclass(frozen=True)
class CodeFile:
    path: Path
    content: str
    language: str


@dataclass(frozen=True)
class AnalysisResults:
    summary: str | None
    sections: list[tuple[str, str]]
    figures: list[Path]
    tables: list[TableResult]
    code_readme: str | None
    code_files: list[CodeFile]
    references: list[str]


LANGUAGE_BY_SUFFIX = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".java": "java",
    ".go": "go",
    ".rs": "rust",
    ".cpp": "cpp",
    ".c": "c",
    ".cs": "csharp",
    ".rb": "ruby",
    ".php": "php",
    ".swift": "swift",
    ".kt": "kotlin",
    ".scala": "scala",
    ".r": "r",
    ".sql": "sql",
    ".json": "json",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".toml": "toml",
    ".sh": "bash",
    ".ps1": "powershell",
    ".html": "html",
    ".css": "css",
    ".md": "markdown",
}


def ensure_directories() -> None:
    for directory in (
        PAPERS_DIR,
        OUTPUT_DIR,
        SUMMARIES_DIR,
        EXTRACTED_DIR,
        IMAGES_DIR,
        TABLES_DIR,
        TEXT_DIR,
        WIKI_DIR,
        CODE_APPLICATIONS_DIR,
    ):
        directory.mkdir(parents=True, exist_ok=True)


def get_papers_list() -> list[Path]:
    ensure_directories()
    return sorted(PAPERS_DIR.glob("*.pdf"), key=lambda path: path.name.lower())


def get_paper_path(paper_name: str) -> Path | None:
    for paper_path in get_papers_list():
        if paper_path.name == paper_name:
            return paper_path
    return None


def get_paper_metadata(paper_path: Path) -> PaperMetadata:
    page_count = _get_pdf_page_count(paper_path)
    analyzed = _is_paper_analyzed(paper_path)
    return PaperMetadata(
        name=paper_path.name,
        stem=paper_path.stem,
        path=paper_path,
        page_count=page_count,
        size_bytes=paper_path.stat().st_size,
        analyzed=analyzed,
    )


def get_all_paper_metadata() -> list[PaperMetadata]:
    return [get_paper_metadata(paper_path) for paper_path in get_papers_list()]


def load_analysis_results(paper: str | Path) -> AnalysisResults:
    paper_path = Path(paper)
    aliases = _build_aliases(paper_path.stem)

    summary = _load_summary(aliases)
    sections = _load_sections(aliases, summary)
    figures = _find_related_files(IMAGES_DIR, aliases, IMAGE_EXTENSIONS)
    tables = _load_tables(aliases)
    code_readme, code_files = _load_code_assets(aliases)
    references = _load_references(aliases, summary)

    return AnalysisResults(
        summary=summary,
        sections=sections,
        figures=figures,
        tables=tables,
        code_readme=code_readme,
        code_files=code_files,
        references=references,
    )


def get_code_application_directories() -> list[Path]:
    ensure_directories()
    return sorted([path for path in CODE_APPLICATIONS_DIR.iterdir() if path.is_dir()], key=lambda path: path.name.lower())


def format_file_size(size_bytes: int) -> str:
    value = float(size_bytes)
    for unit in ("B", "KB", "MB", "GB"):
        if value < 1024 or unit == "GB":
            return f"{value:.1f} {unit}" if unit != "B" else f"{int(value)} {unit}"
        value /= 1024
    return f"{value:.1f} GB"


def _get_pdf_page_count(paper_path: Path) -> int:
    try:
        with fitz.open(paper_path) as document:
            return document.page_count
    except Exception:
        return 0


def _is_paper_analyzed(paper_path: Path) -> bool:
    aliases = _build_aliases(paper_path.stem)
    return any(
        (
            _find_related_files(SUMMARIES_DIR, aliases, TEXT_EXTENSIONS)
            or _find_related_files(IMAGES_DIR, aliases, IMAGE_EXTENSIONS)
            or _find_related_files(TABLES_DIR, aliases, TABLE_EXTENSIONS)
            or _find_matching_directories(CODE_APPLICATIONS_DIR, aliases)
        )
    )


def _load_summary(aliases: Sequence[str]) -> str | None:
    summary_files = _find_related_files(SUMMARIES_DIR, aliases, TEXT_EXTENSIONS)
    for summary_file in summary_files:
        content = _safe_read_text(summary_file)
        if content:
            return content
    return None


def _load_sections(aliases: Sequence[str], summary: str | None) -> list[tuple[str, str]]:
    if summary:
        markdown_sections = _parse_markdown_sections(summary)
        if markdown_sections:
            return markdown_sections

    text_files = _find_related_files(TEXT_DIR, aliases, TEXT_EXTENSIONS)
    sections: list[tuple[str, str]] = []
    for text_file in text_files:
        if "reference" in text_file.stem.lower() or "bibliograph" in text_file.stem.lower():
            continue
        content = _safe_read_text(text_file)
        if content:
            title = text_file.stem.replace("_", " ").replace("-", " ").title()
            sections.append((title, content))
    return sections


def _load_tables(aliases: Sequence[str]) -> list[TableResult]:
    table_results: list[TableResult] = []
    for table_path in _find_related_files(TABLES_DIR, aliases, TABLE_EXTENSIONS):
        data_frame = _read_table(table_path)
        if data_frame is not None:
            table_results.append(TableResult(name=table_path.stem, data=data_frame, path=table_path))
    return table_results


def _load_code_assets(aliases: Sequence[str]) -> tuple[str | None, list[CodeFile]]:
    code_directories = _find_matching_directories(CODE_APPLICATIONS_DIR, aliases)
    readme_content: str | None = None
    code_files: list[CodeFile] = []

    for code_directory in code_directories:
        if readme_content is None:
            for readme_path in sorted(code_directory.rglob("README.md")):
                readme_content = _safe_read_text(readme_path)
                if readme_content:
                    break

        for file_path in sorted(code_directory.rglob("*")):
            if not file_path.is_file():
                continue
            if file_path.name.lower() == "readme.md" or file_path.suffix.lower() not in CODE_EXTENSIONS:
                continue
            content = _safe_read_text(file_path)
            if not content:
                continue
            code_files.append(
                CodeFile(
                    path=file_path,
                    content=content,
                    language=LANGUAGE_BY_SUFFIX.get(file_path.suffix.lower(), "text"),
                )
            )

    return readme_content, code_files


def _load_references(aliases: Sequence[str], summary: str | None) -> list[str]:
    reference_files = [
        path
        for path in _find_related_files(TEXT_DIR, aliases, TEXT_EXTENSIONS)
        if "reference" in path.stem.lower() or "bibliograph" in path.stem.lower()
    ]
    for reference_file in reference_files:
        references = _parse_reference_lines(_safe_read_text(reference_file))
        if references:
            return references

    if summary:
        for title, section_content in _parse_markdown_sections(summary):
            if "reference" in title.lower() or "bibliograph" in title.lower():
                references = _parse_reference_lines(section_content)
                if references:
                    return references

    return []


def _parse_markdown_sections(content: str) -> list[tuple[str, str]]:
    sections: list[tuple[str, str]] = []
    current_title = "Overview"
    current_lines: list[str] = []

    for raw_line in content.splitlines():
        heading_match = re.match(r"^#{1,3}\s+(.*)", raw_line.strip())
        if heading_match:
            section_content = "\n".join(current_lines).strip()
            if section_content:
                sections.append((current_title, section_content))
            current_title = heading_match.group(1).strip()
            current_lines = []
            continue
        current_lines.append(raw_line)

    final_content = "\n".join(current_lines).strip()
    if final_content:
        sections.append((current_title, final_content))

    return sections


def _parse_reference_lines(content: str | None) -> list[str]:
    if not content:
        return []

    references: list[str] = []
    for raw_line in content.splitlines():
        line = raw_line.strip().lstrip("-*0123456789. ")
        if len(line) >= 10:
            references.append(line)
    return references


def _read_table(table_path: Path) -> pd.DataFrame | None:
    suffix = table_path.suffix.lower()
    try:
        if suffix == ".csv":
            return pd.read_csv(table_path)
        if suffix == ".tsv":
            return pd.read_csv(table_path, sep="\t")
        if suffix == ".json":
            return pd.read_json(table_path)
        if suffix in {".xlsx", ".xls"}:
            return pd.read_excel(table_path)
        if suffix == ".parquet":
            return pd.read_parquet(table_path)
    except Exception:
        return None
    return None


def _safe_read_text(file_path: Path) -> str | None:
    for encoding in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            return file_path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
        except OSError:
            return None
    return None


def _find_related_files(base_directory: Path, aliases: Sequence[str], extensions: Iterable[str]) -> list[Path]:
    if not base_directory.exists():
        return []

    normalized_extensions = {extension.lower() for extension in extensions}
    matches: list[Path] = []
    for path in base_directory.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in normalized_extensions:
            continue
        normalized_path = _normalize_text(str(path.relative_to(base_directory)))
        if any(alias and alias in normalized_path for alias in aliases):
            matches.append(path)
    return sorted(matches, key=lambda path: str(path).lower())


def _find_matching_directories(base_directory: Path, aliases: Sequence[str]) -> list[Path]:
    if not base_directory.exists():
        return []

    matches: list[Path] = []
    for path in base_directory.iterdir():
        if not path.is_dir():
            continue
        normalized_path = _normalize_text(path.name)
        if any(alias and alias in normalized_path for alias in aliases):
            matches.append(path)
    return sorted(matches, key=lambda path: path.name.lower())


def _build_aliases(stem: str) -> list[str]:
    aliases = {_normalize_text(stem)}
    parts = [part for part in stem.split() if part]
    if parts:
        aliases.add(_normalize_text(parts[0]))
    if len(parts) > 1:
        aliases.add(_normalize_text(" ".join(parts[1:])))
    hyphen_chunks = re.split(r"[-_]", stem)
    aliases.update(_normalize_text(chunk) for chunk in hyphen_chunks if chunk)
    return sorted((alias for alias in aliases if alias), key=len, reverse=True)


def _normalize_text(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())
