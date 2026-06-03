#!/usr/bin/env python3
"""
new_paper.py — Scaffold a new paper entry in the knowledge base

This tool creates a complete folder structure for a new research paper,
including README template, placeholders, and knowledge graph entries.

Usage:
    python tools/new_paper.py \\
        --title "SkillOpt: Self-Evolving Agent Skills" \\
        --topic agent-systems \\
        --arxiv 2605.23904 \\
        --authors "Microsoft Research" \\
        --year 2026 \\
        --github "microsoft/SkillOpt" \\
        --pypi "skillopt"
"""

import os
import re
from pathlib import Path
from datetime import datetime
import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

def slugify(text: str) -> str:
    """Convert title to kebab-case slug."""
    # Remove special chars, lowercase, replace spaces with hyphens
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    return text.strip('-')

def create_folder_structure(paper_path: Path):
    """Create the folder structure for a paper."""
    paper_path.mkdir(parents=True, exist_ok=True)
    console.print(f"[green]✓[/green] Created folder: {paper_path}")

def create_readme(paper_path: Path, title: str, arxiv: str, authors: str, 
                  year: int, github: str, pypi: str, topic: str):
    """Generate README.md from template."""
    slug = paper_path.name
    
    readme_content = f"""# {title}

**[Add one-line description of the paper]**

[📄 arXiv:{arxiv}](https://arxiv.org/abs/{arxiv})"""
    
    if github:
        readme_content += f" | [💻 GitHub](https://github.com/{github})"
    if pypi:
        readme_content += f" | [📦 PyPI](https://pypi.org/project/{pypi}/)"
    
    readme_content += f"""

---

## 📖 Overview

[Provide a 2-3 paragraph overview of the paper's key contribution]

**Key Innovation:** [Main innovation in one sentence]

**Impact:** [Key results or metrics]

---

## 🗂️ Files in This Folder

- **[📋 README.md](README.md)** — This file
- **[⚡ SUMMARY.md](SUMMARY.md)** — Executive summary
- **[🐍 implementation.py](implementation.py)** — Reference implementation
- **[📓 tutorial.ipynb](tutorial.ipynb)** — Interactive tutorial

---

## 🧠 Core Concepts Introduced

### [Concept Name 1](../../../knowledge-graph/concepts/concept-name-1.md)
Brief description of the concept.

### [Concept Name 2](../../../knowledge-graph/concepts/concept-name-2.md)
Brief description of the concept.

---

## 🔧 Patterns Discovered

### [Pattern Name 1](../../../knowledge-graph/patterns/pattern-name-1.md)
Brief description of the pattern.

---

## ⚡ Implementation Techniques

### [Technique Name 1](../../../knowledge-graph/techniques/technique-name-1.md)
Brief description of the technique.

---

## 🚀 Quick Start

```bash
# Installation (if applicable)
pip install {pypi or 'package-name'}

# Basic usage
# [Add command examples]
```

---

## 📊 Performance Results

[Add key performance metrics or results]

---

## 🎯 Learning Paths

### For Researchers (Understanding)
1. Start: [SUMMARY.md](SUMMARY.md)
2. Deep dive: [README.md](README.md) (this file)
3. Explore: Follow wiki links to concepts and patterns

### For Practitioners (Implementation)
1. Code: [implementation.py](implementation.py)
2. Learn: [tutorial.ipynb](tutorial.ipynb)
3. Build: Adapt to your use case

---

## 🔗 Related Papers

*(Add cross-links as you expand the knowledge base)*

---

## 📚 Citations

**BibTeX:**
```bibtex
@article{{{slug}{year},
  title={{{title}}},
  author={{{authors}}},
  journal={{arXiv preprint arXiv:{arxiv}}},
  year={{{year}}}
}}
```

---

## 📖 Additional Resources

- **ArXiv Paper:** [arxiv.org/abs/{arxiv}](https://arxiv.org/abs/{arxiv})"""
    
    if github:
        readme_content += f"\n- **GitHub Repository:** [github.com/{github}](https://github.com/{github})"
    if pypi:
        readme_content += f"\n- **PyPI Package:** [pypi.org/project/{pypi}](https://pypi.org/project/{pypi})"
    
    readme_content += f"""

---

**Last Updated:** {datetime.now().strftime('%Y-%m-%d')}
"""
    
    readme_path = paper_path / "README.md"
    readme_path.write_text(readme_content, encoding='utf-8')
    console.print(f"[green]✓[/green] Created README.md")

def create_summary(paper_path: Path, title: str):
    """Create SUMMARY.md placeholder."""
    summary_content = f"""# {title} — Summary

## Key Points

- [Point 1]
- [Point 2]
- [Point 3]

## Problem

[What problem does this paper solve?]

## Solution

[What is the proposed solution?]

## Results

[What are the key results?]

## Significance

[Why does this matter?]
"""
    
    summary_path = paper_path / "SUMMARY.md"
    summary_path.write_text(summary_content, encoding='utf-8')
    console.print(f"[green]✓[/green] Created SUMMARY.md")

def create_implementation_placeholder(paper_path: Path, title: str):
    """Create implementation.py placeholder."""
    impl_content = f'''#!/usr/bin/env python3
"""
Reference implementation for: {title}

This is a from-scratch implementation based on the paper,
intended for educational purposes and understanding the core algorithms.
"""

def main():
    """Main entry point."""
    print("Implementation coming soon...")
    # TODO: Implement core algorithm from paper

if __name__ == "__main__":
    main()
'''
    
    impl_path = paper_path / "implementation.py"
    impl_path.write_text(impl_content, encoding='utf-8')
    console.print(f"[green]✓[/green] Created implementation.py")

def create_notebook_placeholder(paper_path: Path, title: str):
    """Create tutorial.ipynb placeholder."""
    notebook_content = {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [f"# {title} — Tutorial\n\n", "Interactive walkthrough of the paper's concepts and implementation."]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": ["## Setup\n\n", "Install dependencies:"]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": ["# !pip install <package-name>"]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": ["## Core Concepts\n\n", "[Explain key concepts]"]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": ["## Implementation\n\n", "[Walk through implementation]"]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": ["# Implementation code here"]
            }
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "name": "python",
                "version": "3.11.0"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 4
    }
    
    import json
    notebook_path = paper_path / "tutorial.ipynb"
    notebook_path.write_text(json.dumps(notebook_content, indent=2), encoding='utf-8')
    console.print(f"[green]✓[/green] Created tutorial.ipynb")

def update_index(topic: str, title: str, slug: str, arxiv: str, authors: str, year: int):
    """Add entry to knowledge-graph/INDEX.md."""
    # For now, print instructions (full implementation would edit the file)
    console.print("\n[yellow]⚠ Manual step required:[/yellow]")
    console.print(f"Add entry to knowledge-graph/INDEX.md under topic '{topic}':")
    console.print(f"""
#### {title}
**[📁 Paper Folder](../Papers/{topic}/{slug}/) | [📄 Summary](../Papers/{topic}/{slug}/SUMMARY.md)**

- **ArXiv:** {arxiv}
- **Authors:** {authors}
- **Year:** {year}

**Key Innovation:** [Add description]
""")

@click.command()
@click.option('--title', required=True, help='Paper title')
@click.option('--topic', required=True, 
              type=click.Choice(['agent-systems', 'machine-learning', 'nlp', 'computer-vision', 'reinforcement-learning', 'other']),
              help='Topic category')
@click.option('--arxiv', help='ArXiv ID (e.g., 2605.23904)')
@click.option('--authors', default='Unknown', help='Comma-separated author list')
@click.option('--year', type=int, default=datetime.now().year, help='Publication year')
@click.option('--github', help='GitHub repository (e.g., microsoft/SkillOpt)')
@click.option('--pypi', help='PyPI package name')
def main(title, topic, arxiv, authors, year, github, pypi):
    """Create a new paper entry in the knowledge base."""
    
    console.print(Panel.fit(
        f"[bold blue]Creating new paper entry[/bold blue]\n{title}",
        border_style="blue"
    ))
    
    # Generate slug
    slug = slugify(title.split(':')[0])  # Use first part before colon
    
    # Define paths
    project_root = Path(__file__).parent.parent
    paper_path = project_root / "Papers" / topic / slug
    
    # Create structure
    console.print(f"\n[bold]Creating folder structure...[/bold]")
    create_folder_structure(paper_path)
    
    console.print(f"\n[bold]Creating files...[/bold]")
    create_readme(paper_path, title, arxiv or 'TBD', authors, year, github or '', pypi or '', topic)
    create_summary(paper_path, title)
    create_implementation_placeholder(paper_path, title)
    create_notebook_placeholder(paper_path, title)
    
    # Summary table
    console.print(f"\n[bold green]✓ Paper entry created successfully![/bold green]\n")
    
    table = Table(title="Paper Details")
    table.add_column("Field", style="cyan")
    table.add_column("Value", style="green")
    table.add_row("Title", title)
    table.add_row("Topic", topic)
    table.add_row("Slug", slug)
    table.add_row("Location", str(paper_path.relative_to(project_root)))
    table.add_row("ArXiv", arxiv or 'TBD')
    table.add_row("Authors", authors)
    table.add_row("Year", str(year))
    if github:
        table.add_row("GitHub", github)
    if pypi:
        table.add_row("PyPI", pypi)
    
    console.print(table)
    
    # Next steps
    console.print("\n[bold]Next steps:[/bold]")
    console.print("1. Fill in README.md with paper details")
    console.print("2. Write SUMMARY.md")
    console.print("3. Implement core algorithm in implementation.py")
    console.print("4. Create tutorial in tutorial.ipynb")
    console.print("5. Extract concepts/patterns/techniques to knowledge graph")
    console.print("6. Update knowledge-graph/INDEX.md")
    
    update_index(topic, title, slug, arxiv or 'TBD', authors, year)

if __name__ == '__main__':
    main()
