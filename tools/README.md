# 🛠️ Automation Tools

**Scripts and utilities for managing the knowledge base**

---

## Available Tools

### 1. `new_paper.py`
**Purpose:** Scaffold a new paper entry with all necessary files and cross-links.

**Usage:**
```bash
python tools/new_paper.py \
  --title "Paper Title" \
  --topic agent-systems \
  --arxiv 2605.23904 \
  --authors "Author 1, Author 2" \
  --year 2026
```

**What it does:**
- Creates folder in `papers/{topic}/{paper-name}/`
- Generates initial README.md from template
- Adds entry to knowledge graph INDEX.md
- Creates placeholder files for implementation
- Initializes git tracking

---

### 2. `update_knowledge_graph.py`
**Purpose:** Re-index all papers and update cross-references in the knowledge graph.

**Usage:**
```bash
python tools/update_knowledge_graph.py
```

**What it does:**
- Scans all paper folders
- Extracts metadata (title, concepts, patterns, techniques)
- Updates INDEX.md files in knowledge-graph/
- Validates all wiki links
- Generates statistics

---

### 3. `extract_concepts.py`
**Purpose:** Semi-automatically extract concepts, patterns, and techniques from paper documentation.

**Usage:**
```bash
python tools/extract_concepts.py \
  --paper Papers/agent-systems/SkillOpt \
  --interactive
```

**What it does:**
- Scans paper documentation for key ideas
- Suggests concepts, patterns, and techniques
- Prompts for confirmation (if --interactive)
- Creates wiki pages for confirmed extractions
- Updates INDEX.md files

---

### 4. `find_patterns.py`
**Purpose:** Identify common patterns across multiple papers.

**Usage:**
```bash
python tools/find_patterns.py --min-papers 2
```

**What it does:**
- Analyzes all papers in knowledge base
- Identifies recurring concepts, patterns, techniques
- Suggests cross-paper connections
- Generates pattern report

---

### 5. `validate_knowledge_graph.py`
**Purpose:** Check integrity of the knowledge graph (links, structure, consistency).

**Usage:**
```bash
python tools/validate_knowledge_graph.py --fix
```

**What it does:**
- Validates all markdown links
- Checks folder structure consistency
- Identifies orphaned files
- Verifies cross-references
- Optionally fixes common issues (with --fix)

---

## Installation

```bash
# Install dependencies
pip install -r tools/requirements.txt
```

**Dependencies:**
- `pyyaml` — YAML parsing for metadata
- `click` — CLI framework
- `rich` — Beautiful terminal output
- `networkx` — Graph analysis for pattern detection

---

## Quick Reference

| Task | Command |
|------|---------|
| Add new paper | `python tools/new_paper.py --title "..." --topic ...` |
| Update indexes | `python tools/update_knowledge_graph.py` |
| Extract concepts | `python tools/extract_concepts.py --paper Papers/.../...` |
| Find patterns | `python tools/find_patterns.py` |
| Validate | `python tools/validate_knowledge_graph.py` |

---

## Tool Details

### new_paper.py

Creates a complete paper entry with all necessary structure.

**Arguments:**
- `--title` (required): Paper title
- `--topic` (required): Topic folder (agent-systems, machine-learning, nlp, computer-vision, etc.)
- `--arxiv`: ArXiv ID (e.g., 2605.23904)
- `--authors`: Comma-separated author list
- `--year`: Publication year
- `--github`: Optional GitHub repository URL
- `--pypi`: Optional PyPI package name

**Output structure:**
```
Papers/{topic}/{paper-slug}/
├── README.md                    # Generated from template
├── SUMMARY.md                   # Placeholder
├── implementation.py            # Placeholder
└── tutorial.ipynb               # Placeholder
```

**Template variables:**
- `{TITLE}` — Paper title
- `{ARXIV}` — ArXiv ID
- `{AUTHORS}` — Author list
- `{YEAR}` — Publication year
- `{GITHUB}` — GitHub URL
- `{PYPI}` — PyPI package
- `{TOPIC}` — Topic category

---

### update_knowledge_graph.py

Scans all papers and regenerates knowledge graph indexes.

**Process:**
1. Scan `Papers/**/*` for all paper folders
2. Parse README.md for metadata
3. Extract concepts, patterns, techniques from content
4. Update `knowledge-graph/INDEX.md`
5. Update topic-specific indexes
6. Generate statistics

**Configuration:**
Edit `tools/config.yaml` to customize:
- Index templates
- Metadata extraction patterns
- Cross-linking rules

---

### extract_concepts.py

Interactive concept extraction tool.

**Modes:**
- `--interactive` — Prompt for confirmation before creating pages
- `--auto` — Automatically create all suggested extractions
- `--dry-run` — Show what would be extracted without creating files

**Extraction heuristics:**
- Capitalized phrases (e.g., "Text-Space Optimization")
- Phrases in **bold** or *italics*
- Section headings
- Terms defined with "Definition:" or "What:"

**Output:**
Creates wiki pages in:
- `knowledge-graph/concepts/` — Conceptual ideas
- `knowledge-graph/patterns/` — Architectural patterns
- `knowledge-graph/techniques/` — Implementation techniques

---

### find_patterns.py

Cross-paper pattern analysis.

**Analysis types:**
- Concept overlap (same concepts in multiple papers)
- Pattern similarity (similar architectural choices)
- Technique reuse (same techniques applied)
- Citation networks (papers citing each other)

**Output:**
Generates `knowledge-graph/patterns/cross-paper-patterns.md` with:
- Common patterns across N papers
- Evolution of concepts
- Related work clusters

---

### validate_knowledge_graph.py

Integrity checker for the entire knowledge base.

**Checks:**
- [ ] All internal markdown links resolve
- [ ] All papers have README.md
- [ ] All concepts/patterns/techniques have INDEX entries
- [ ] No orphaned files
- [ ] Consistent naming (kebab-case)
- [ ] Required metadata present
- [ ] Cross-references are bidirectional

**Fixes (with --fix):**
- Auto-create missing INDEX entries
- Fix broken links (best-effort)
- Standardize naming
- Add missing cross-references

---

## Development

### Adding a New Tool

1. Create `tools/new_tool.py`
2. Use `click` for CLI
3. Use `rich` for output
4. Add entry to this README
5. Update `tools/requirements.txt` if needed

**Template:**
```python
#!/usr/bin/env python3
"""
New Tool Description
"""
import click
from rich.console import Console

console = Console()

@click.command()
@click.option('--option', help='Option description')
def main(option):
    """Tool purpose."""
    console.print("[green]Starting...[/green]")
    # Tool logic here
    console.print("[green]Done![/green]")

if __name__ == '__main__':
    main()
```

---

## Roadmap

### Planned Tools

- [ ] `export_to_obsidian.py` — Export knowledge graph to Obsidian vault
- [ ] `generate_learning_path.py` — Create custom learning paths
- [ ] `paper_recommender.py` — Suggest papers based on interests
- [ ] `citation_tracker.py` — Track citations across papers
- [ ] `concept_evolution.py` — Visualize how concepts evolve
- [ ] `dashboard.py` — Interactive web dashboard for knowledge base

---

**Last Updated:** 2026-06-03
