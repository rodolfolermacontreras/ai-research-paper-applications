# AI Research Papers Knowledge Base

**A Systematic Knowledge Graph for AI Research Papers**

Welcome to a structured knowledge management system for exploring, understanding, and connecting insights across AI research papers.

---

## 🗺️ Navigation

### Quick Access
- **[📚 All Papers Index](knowledge-graph/INDEX.md)** — Complete catalog of all papers
- **[🧠 Concepts Map](knowledge-graph/concepts/INDEX.md)** — Cross-paper concepts and ideas
- **[🔧 Patterns Library](knowledge-graph/patterns/INDEX.md)** — Discovered patterns and architectures
- **[⚡ Techniques Catalog](knowledge-graph/techniques/INDEX.md)** — Implementation techniques
- **[🛠️ Tools](tools/README.md)** — Automation scripts and utilities

---

## 📂 Structure

This knowledge base is organized using a hybrid approach combining:
- **Hierarchical organization** (papers by topic)
- **Wiki-style linking** (cross-references between related concepts)
- **Knowledge graph connections** (concepts, patterns, techniques)

```
AI-Research-Papers/
├── papers/                           # All papers organized by topic
│   ├── agent-systems/                # Agent & LLM systems
│   │   ├── SkillOpt/                 # Self-Evolving Agent Skills
│   │   │   ├── README.md             # Paper overview + links
│   │   │   ├── *.md                   # Documentation
│   │   │   ├── *.py                   # Code implementations
│   │   │   └── *.ipynb                # Tutorials
│   │   └── ...                        # More agent papers
│   ├── machine-learning/              # ML fundamentals
│   ├── nlp/                           # Natural Language Processing
│   └── computer-vision/               # Vision models
│
├── knowledge-graph/                   # Wiki & interconnected knowledge
│   ├── INDEX.md                       # Master paper index
│   ├── concepts/                      # Concepts across papers
│   │   ├── INDEX.md                   # Concept catalog
│   │   ├── validation-gating.md       # Example: Validation Gating
│   │   ├── text-space-optimization.md # Example: Text-space Optimization
│   │   └── ...                        # More concepts
│   ├── patterns/                      # Patterns discovered
│   │   ├── INDEX.md                   # Pattern library
│   │   ├── rollout-reflect-edit.md    # Example: Rollout-Reflect-Edit
│   │   └── ...                        # More patterns
│   └── techniques/                    # Implementation techniques
│       ├── INDEX.md                   # Technique catalog
│       ├── cosine-lr-schedule.md      # Example: Cosine LR Schedule
│       └── ...                        # More techniques
│
├── tools/                             # Automation & utilities
│   ├── README.md                      # Tools documentation
│   ├── new_paper.py                   # Script to add new papers
│   ├── update_knowledge_graph.py      # Update wiki links
│   └── ...                            # More automation
│
└── templates/                         # Templates for new content
    ├── paper_README_template.md       # Template for paper overviews
    ├── concept_template.md            # Template for concept pages
    ├── pattern_template.md            # Template for patterns
    └── technique_template.md          # Template for techniques
```

---

## 🎯 How to Use This Knowledge Base

### For Researchers (Understanding)
1. Start with **[Papers Index](knowledge-graph/INDEX.md)** to browse all papers
2. Read a paper's **README.md** for overview and key insights
3. Follow wiki links to explore related **concepts**, **patterns**, and **techniques**
4. Use the knowledge graph to discover connections across papers

### For Practitioners (Implementation)
1. Browse **[Techniques Catalog](knowledge-graph/techniques/INDEX.md)** for implementation guides
2. Check **[Patterns Library](knowledge-graph/patterns/INDEX.md)** for architectural patterns
3. Find code examples in paper folders (*.py, *.ipynb files)
4. Use automation tools to scaffold new implementations

### For Knowledge Builders (Contributing)
1. Use `tools/new_paper.py` to add new papers
2. Update knowledge graph as you find connections
3. Extract concepts, patterns, and techniques to wiki pages
4. Cross-link related ideas across papers

---

## 📚 Papers by Topic

### Agent Systems & LLMs
- **[SkillOpt](papers/agent-systems/SkillOpt/README.md)** — Self-Evolving Agent Skills via Text-Space Optimization

### Machine Learning
- *(Coming soon)*

### Natural Language Processing
- *(Coming soon)*

### Computer Vision
- *(Coming soon)*

---

## 🧠 Key Concepts Across Papers

**Browse the full [Concepts Map](knowledge-graph/concepts/INDEX.md)**

Featured concepts:
- **Text-Space Optimization** — Treating prompts as trainable parameters
- **Validation Gating** — Held-out performance gates for skill evolution
- **Rollout-Reflect-Edit Loop** — Core pattern for iterative improvement
- *(More concepts added as papers are integrated)*

---

## 🔧 Discovered Patterns

**Browse the full [Patterns Library](knowledge-graph/patterns/INDEX.md)**

Featured patterns:
- **Optimizer-Target Separation** — Separate models for generation vs. optimization
- **Bounded Edit Budget** — Textual learning rate for stable training
- **Rejected-Edit Buffer** — Negative feedback for avoiding bad directions
- *(More patterns added as papers are integrated)*

---

## ⚡ Implementation Techniques

**Browse the full [Techniques Catalog](knowledge-graph/techniques/INDEX.md)**

Featured techniques:
- **Cosine Learning Rate Schedule** — Smooth decay for edit budgets
- **Minibatch Reflection** — Separate analysis of success/failure cases
- **Slow Update + Meta Skill** — Epoch-level memory mechanisms
- *(More techniques added as papers are integrated)*

---

## 🛠️ Automation Tools

**See [Tools Documentation](tools/README.md) for full details**

- **`new_paper.py`** — Add a new paper to the knowledge base
- **`update_knowledge_graph.py`** — Re-index and update wiki links
- **`extract_concepts.py`** — Auto-extract concepts from paper documentation
- **`find_patterns.py`** — Identify common patterns across papers

---

## 📖 Learning Paths

### Path 1: Agent Systems Deep Dive
1. [SkillOpt](papers/agent-systems/SkillOpt/README.md) — Self-evolving skills
2. *(Next paper)* — Multi-agent coordination
3. *(Next paper)* — Tool-use agents

### Path 2: Training Techniques
1. [Text-Space Optimization](knowledge-graph/concepts/text-space-optimization.md)
2. [Validation Gating](knowledge-graph/concepts/validation-gating.md)
3. [Cosine LR Schedule](knowledge-graph/techniques/cosine-lr-schedule.md)

---

## 🤝 Contributing

### Adding a New Paper
```bash
# Use the automation tool
python tools/new_paper.py --paper "Paper Title" --topic agent-systems --arxiv 2605.23904
```

### Adding a Concept/Pattern/Technique
1. Copy the appropriate template from `templates/`
2. Fill in the content
3. Add wiki links to related papers/concepts
4. Update the relevant INDEX.md

### Updating the Knowledge Graph
```bash
# Re-index all papers and update cross-references
python tools/update_knowledge_graph.py
```

---

## 📊 Knowledge Base Statistics

- **Papers:** 1 (SkillOpt)
- **Concepts:** 3 (Text-Space Optimization, Validation Gating, Rollout-Reflect-Edit)
- **Patterns:** 3 (Optimizer-Target Separation, Bounded Edit Budget, Rejected-Edit Buffer)
- **Techniques:** 3 (Cosine LR Schedule, Minibatch Reflection, Slow Update)
- **Cross-Links:** 15+ connections across papers

*Last Updated: 2026-06-03*

---

## 🔗 External Resources

- **Papers:** [arXiv](https://arxiv.org), [Papers with Code](https://paperswithcode.com)
- **Code:** [GitHub](https://github.com), [Hugging Face](https://huggingface.co)
- **Tools:** [Obsidian](https://obsidian.md), [Zettelkasten](https://zettelkasten.de)

---

**🎯 Mission:** Build a living knowledge graph that grows smarter with each paper, discovering patterns and connections that individual papers cannot reveal alone.
