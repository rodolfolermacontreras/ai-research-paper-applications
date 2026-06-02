"""Generate a self-contained HTML one-pager from a paper summary markdown file."""

from __future__ import annotations

import html
import re
from pathlib import Path
from typing import Any


def generate_onepager(
    summary_path: str | Path,
    output_path: str | Path | None = None,
    metadata: dict[str, Any] | None = None,
) -> str:
    """Read a markdown summary and produce a polished, self-contained HTML file.

    Parameters
    ----------
    summary_path:
        Path to the markdown summary file (``output/summaries/*.md``).
    output_path:
        Where to write the HTML. If *None*, defaults to the same directory
        with an ``.html`` extension.
    metadata:
        Optional dict with keys ``title``, ``authors``, ``date``, ``keywords``
        to override what is parsed from the markdown header.

    Returns
    -------
    str
        The absolute path of the generated HTML file.
    """

    summary = Path(summary_path)
    if not summary.exists():
        raise FileNotFoundError(f"Summary not found: {summary}")

    md_text = summary.read_text(encoding="utf-8")
    parsed = _parse_summary_markdown(md_text)

    if metadata:
        for key in ("title", "authors", "date", "keywords"):
            if key in metadata:
                parsed[key] = metadata[key]

    html_content = _render_html(parsed)

    if output_path is None:
        output_path = summary.with_suffix(".html")
    else:
        output_path = Path(output_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html_content, encoding="utf-8")
    return str(output_path.resolve())


def generate_all_onepagers(
    summaries_dir: str | Path,
    output_dir: str | Path | None = None,
) -> list[str]:
    """Generate HTML one-pagers for every markdown summary in a directory.

    Returns a list of generated HTML file paths.
    """

    src = Path(summaries_dir)
    dst = Path(output_dir) if output_dir else src
    dst.mkdir(parents=True, exist_ok=True)

    paths: list[str] = []
    for md_file in sorted(src.glob("*.md")):
        html_path = dst / md_file.with_suffix(".html").name
        paths.append(generate_onepager(md_file, html_path))
    return paths


# ---------------------------------------------------------------------------
# Markdown parsing
# ---------------------------------------------------------------------------

_HEADING_RE = re.compile(r"^(#{1,3})\s+(.+)$", re.MULTILINE)


def _parse_summary_markdown(md_text: str) -> dict[str, Any]:
    """Extract structured data from the summary markdown."""

    sections: list[dict[str, str]] = []
    title = ""
    authors = ""
    date = ""
    abstract = ""

    current_heading = ""
    current_body: list[str] = []

    for line in md_text.splitlines():
        heading_match = _HEADING_RE.match(line)
        if heading_match:
            if current_heading and current_body:
                sections.append({"heading": current_heading, "body": "\n".join(current_body).strip()})
            current_heading = heading_match.group(2).strip()
            current_body = []

            if not title and heading_match.group(1) == "#":
                title = current_heading
            continue

        current_body.append(line)

    if current_heading and current_body:
        sections.append({"heading": current_heading, "body": "\n".join(current_body).strip()})

    # Extract metadata from known section patterns
    for section in sections:
        heading_lower = section["heading"].lower()
        body = section["body"]
        if "title and authors" in heading_lower or "authors" in heading_lower:
            title_match = re.search(r"\*\*Title:\*\*\s*(.+)", body)
            if title_match:
                title = title_match.group(1).strip()
            author_match = re.search(r"\*\*Authors?:\*\*\s*(.+)", body)
            if author_match:
                authors = author_match.group(1).strip()
            date_match = re.search(r"\*\*(?:Date|Paper type):\*\*\s*(.+)", body)
            if date_match:
                date = date_match.group(1).strip()
        if heading_lower == "abstract":
            abstract = body.lstrip("> ").replace("\n> ", "\n").strip()

    return {
        "title": title,
        "authors": authors,
        "date": date,
        "abstract": abstract,
        "sections": sections,
    }


# ---------------------------------------------------------------------------
# HTML rendering
# ---------------------------------------------------------------------------


def _md_inline_to_html(text: str) -> str:
    """Convert basic inline markdown to HTML."""

    escaped = html.escape(text)
    # Bold
    escaped = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)
    # Italic
    escaped = re.sub(r"\*(.+?)\*", r"<em>\1</em>", escaped)
    # Inline code
    escaped = re.sub(r"`(.+?)`", r"<code>\1</code>", escaped)
    return escaped


def _md_block_to_html(body: str) -> str:
    """Convert a markdown body block into HTML paragraphs and lists."""

    lines = body.split("\n")
    html_parts: list[str] = []
    in_list = False
    in_code = False
    code_lines: list[str] = []
    paragraph: list[str] = []

    def flush_paragraph() -> None:
        if paragraph:
            html_parts.append(f"<p>{_md_inline_to_html(' '.join(paragraph))}</p>")
            paragraph.clear()

    for line in lines:
        # Code fences
        if line.strip().startswith("```"):
            if in_code:
                html_parts.append(f"<pre><code>{html.escape(chr(10).join(code_lines))}</code></pre>")
                code_lines.clear()
                in_code = False
            else:
                flush_paragraph()
                in_code = True
            continue
        if in_code:
            code_lines.append(line)
            continue

        stripped = line.strip()

        # Blockquote
        if stripped.startswith(">"):
            flush_paragraph()
            quote_text = stripped.lstrip("> ").strip()
            html_parts.append(f"<blockquote><p>{_md_inline_to_html(quote_text)}</p></blockquote>")
            continue

        # Unordered list
        if re.match(r"^[-*]\s+", stripped):
            flush_paragraph()
            if not in_list:
                html_parts.append("<ul>")
                in_list = True
            item = re.sub(r"^[-*]\s+", "", stripped)
            html_parts.append(f"<li>{_md_inline_to_html(item)}</li>")
            continue

        if in_list and (not stripped or not re.match(r"^[-*]\s+", stripped)):
            html_parts.append("</ul>")
            in_list = False

        if not stripped:
            flush_paragraph()
            continue

        paragraph.append(stripped)

    flush_paragraph()
    if in_list:
        html_parts.append("</ul>")

    return "\n".join(html_parts)


def _render_html(parsed: dict[str, Any]) -> str:
    """Render a self-contained HTML one-pager."""

    title = html.escape(parsed.get("title", "Paper Summary"))
    authors = html.escape(parsed.get("authors", ""))
    date = html.escape(parsed.get("date", ""))
    abstract = parsed.get("abstract", "")

    sections_html: list[str] = []
    skip_headings = {"title and authors", "abstract"}

    for section in parsed.get("sections", []):
        heading = section["heading"]
        if heading.lower() in skip_headings or heading == parsed.get("title", ""):
            continue
        body_html = _md_block_to_html(section["body"])
        if body_html.strip():
            safe_heading = html.escape(heading)
            sections_html.append(
                f'<section>\n<h2>{safe_heading}</h2>\n{body_html}\n</section>'
            )

    abstract_html = ""
    if abstract:
        abstract_html = f"""<section class="abstract">
<h2>Abstract</h2>
<blockquote><p>{_md_inline_to_html(abstract)}</p></blockquote>
</section>"""

    body_sections = "\n".join(sections_html)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
:root {{
  --primary: #1a365d;
  --accent: #2b6cb0;
  --bg: #f7fafc;
  --card-bg: #ffffff;
  --text: #2d3748;
  --text-muted: #718096;
  --border: #e2e8f0;
  --code-bg: #edf2f7;
}}
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{
  font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
  background: var(--bg);
  color: var(--text);
  line-height: 1.7;
  padding: 2rem 1rem;
}}
.container {{
  max-width: 860px;
  margin: 0 auto;
}}
header {{
  background: var(--primary);
  color: #fff;
  padding: 2rem 2.5rem;
  border-radius: 12px 12px 0 0;
}}
header h1 {{
  font-size: 1.65rem;
  line-height: 1.3;
  margin-bottom: 0.5rem;
}}
header .meta {{
  font-size: 0.92rem;
  opacity: 0.85;
}}
main {{
  background: var(--card-bg);
  padding: 2rem 2.5rem;
  border-radius: 0 0 12px 12px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.06);
}}
section {{
  margin-bottom: 1.8rem;
  padding-bottom: 1.2rem;
  border-bottom: 1px solid var(--border);
}}
section:last-child {{
  border-bottom: none;
  margin-bottom: 0;
}}
h2 {{
  color: var(--accent);
  font-size: 1.2rem;
  margin-bottom: 0.7rem;
  padding-bottom: 0.3rem;
  border-bottom: 2px solid var(--accent);
  display: inline-block;
}}
p {{ margin-bottom: 0.8rem; }}
ul {{ margin: 0.5rem 0 1rem 1.5rem; }}
li {{ margin-bottom: 0.4rem; }}
blockquote {{
  background: var(--code-bg);
  border-left: 4px solid var(--accent);
  padding: 0.8rem 1.2rem;
  margin: 0.8rem 0;
  border-radius: 0 6px 6px 0;
}}
blockquote p {{ margin-bottom: 0; }}
pre {{
  background: #1a202c;
  color: #e2e8f0;
  padding: 1rem;
  border-radius: 6px;
  overflow-x: auto;
  font-size: 0.85rem;
  margin: 0.8rem 0;
}}
code {{
  background: var(--code-bg);
  padding: 0.15rem 0.35rem;
  border-radius: 3px;
  font-size: 0.9em;
}}
pre code {{
  background: transparent;
  padding: 0;
}}
strong {{ color: var(--primary); }}
.abstract blockquote {{
  font-style: italic;
  font-size: 0.95rem;
}}
footer {{
  text-align: center;
  margin-top: 1.5rem;
  font-size: 0.8rem;
  color: var(--text-muted);
}}
@media print {{
  body {{ padding: 0; }}
  header {{ border-radius: 0; }}
  main {{ box-shadow: none; border-radius: 0; }}
  section {{ page-break-inside: avoid; }}
}}
</style>
</head>
<body>
<div class="container">
<header>
  <h1>{title}</h1>
  <div class="meta">{authors}{(' -- ' + date) if date else ''}</div>
</header>
<main>
{abstract_html}
{body_sections}
</main>
<footer>Generated by AI Research Paper Applications</footer>
</div>
</body>
</html>
"""
