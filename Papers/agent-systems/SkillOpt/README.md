# SkillOpt: Self-Evolving Agent Skills

**Text-Space Optimization Framework for Automated Agent Improvement**

[📄 arXiv:2605.23904v2](https://arxiv.org/abs/2605.23904) | [💻 GitHub](https://github.com/microsoft/SkillOpt) | [📦 PyPI](https://pypi.org/project/skillopt/) | [📚 Docs](https://microsoft.github.io/SkillOpt/)

---

## 📖 Overview

SkillOpt is a groundbreaking framework from Microsoft Research that enables AI agents to automatically improve their own skills through text-space optimization. Instead of tuning numerical parameters, SkillOpt treats prompts and instructions as trainable text that evolves based on performance feedback.

**Key Innovation:** LLM-as-optimizer architecture where one model executes skills (target) while another analyzes performance and generates improvements (optimizer).

**Impact:**
- **+23.5 to +24.8 points** average improvement across GPT-5.5, Codex, and Claude Code
- **Best-in-class** on all 52 evaluated (model × benchmark × harness) combinations
- **Production-ready** PyPI package with multi-backend support

---

## 🗂️ Files in This Folder

### Quick Start
- **[📋 README_SkillOpt.md](README_SkillOpt.md)** — Comprehensive paper summary (12.86 KB)
- **[⚡ SUMMARY_SkillOpt.md](SUMMARY_SkillOpt.md)** — Executive summary (10.30 KB)
- **[🎯 SkillOpt_Executive_OnePager.md](SkillOpt_Executive_OnePager.md)** — STAR-formatted one-pager (14.63 KB)

### Implementation Guides
- **[🔧 SkillOpt_Implementation_Guide.md](SkillOpt_Implementation_Guide.md)** — Production deployment guide (19.58 KB)
  - **Most important for practitioners**
  - Complete integration guide for official Microsoft package
  - All 5 backend configurations
  - Training commands and troubleshooting
  
- **[📦 SkillOpt_Complete_Package_README.md](SkillOpt_Complete_Package_README.md)** — Master navigation (12.61 KB)
  - File inventory and learning paths
  - Quick-start workflows by role

### Code & Tutorials
- **[🐍 skillopt_implementation.py](skillopt_implementation.py)** — Reference implementation (25.23 KB)
  - From-scratch implementation based on paper
  - Educational code with detailed comments
  - Demonstrates core algorithms

- **[⚙️ skillopt_integration_examples.py](skillopt_integration_examples.py)** — Integration examples (14.87 KB)
  - Official package integration
  - Installation validation
  - Command templates for 5 training scenarios

- **[📓 SkillOpt_Tutorial.ipynb](SkillOpt_Tutorial.ipynb)** — Interactive tutorial (18.44 KB)
  - Step-by-step walkthrough
  - Runnable examples
  - Hands-on learning

### Analysis & Investigation
- **[🔍 SkillOpt_Repository_Investigation_Report.md](SkillOpt_Repository_Investigation_Report.md)** — Repo findings (14.28 KB)
  - Before/after value analysis
  - Key discoveries from official repository
  - Gap closure documentation

### Web Resources
- **[🌐 SkillOpt_OnePager.html](SkillOpt_OnePager.html)** — Interactive HTML one-pager (25.08 KB)
  - Beautiful visual presentation
  - Animated diagrams
  - Collapsible sections

---

## 🧠 Core Concepts Introduced

This paper introduces several fundamental concepts now cataloged in our knowledge graph:

### [Text-Space Optimization](../../../knowledge-graph/concepts/text-space-optimization.md)
Treating prompts as trainable parameters in text space rather than numeric weights. LLMs generate improved versions of text-based parameters through reflection and editing.

### [Validation Gating](../../../knowledge-graph/concepts/validation-gating.md)
Using held-out validation set performance as a binary gate to accept or reject skill updates, preventing overfitting and ensuring generalization.

### [Rollout-Reflect-Edit Loop](../../../knowledge-graph/concepts/rollout-reflect-edit.md)
Iterative improvement cycle: execute skills on training data, analyze performance, generate improvements based on feedback.

---

## 🔧 Patterns Discovered

The paper establishes several reusable architectural and design patterns:

### [Optimizer-Target Separation](../../../knowledge-graph/patterns/optimizer-target-separation.md)
Separate the model being optimized (target) from the model doing optimization (optimizer) for interpretable, controllable improvement.

### [Bounded Edit Budget](../../../knowledge-graph/patterns/bounded-edit-budget.md)
Limit the size of textual edits to prevent catastrophic changes, analogous to learning rates in numerical optimization.

### [Rejected-Edit Buffer](../../../knowledge-graph/patterns/rejected-edit-buffer.md)
Store rejected edits as negative examples to prevent re-exploring bad directions and accelerate convergence.

---

## ⚡ Implementation Techniques

Concrete techniques you can use in your own projects:

### [Cosine Learning Rate Schedule](../../../knowledge-graph/techniques/cosine-lr-schedule.md)
Smoothly decay edit budget over training using cosine annealing for stable, predictable improvement.

### [Minibatch Reflection](../../../knowledge-graph/techniques/minibatch-reflection.md)
Analyze performance on small batches separately, then aggregate insights for focused, actionable feedback.

### [Slow Update + Meta Skill](../../../knowledge-graph/techniques/slow-update-meta-skill.md)
Maintain epoch-level memory and meta-information alongside skill text for long-term context.

---

## 🚀 Quick Start

### Installation (Official Package)
```bash
# Basic installation
pip install skillopt

# With WebUI dashboard
pip install skillopt[webui]

# Verify installation
python -c "import skillopt; print(skillopt.__version__)"
```

### First Training Run
```bash
# Using GPT-5.5 on built-in benchmark
python -m skillopt.main \
  --task HumanEval \
  --optimizer-model gpt-5.5 \
  --target-model gpt-5.5 \
  --train-ratio 0.6 \
  --val-ratio 0.2 \
  --test-ratio 0.2 \
  --num-iters 50 \
  --output-dir ./output/humaneval_run1
```

### Using Pre-Trained Skills
```bash
# Zero-training evaluation with pre-trained GPT-5.5 skills
python -m skillopt.main \
  --task SpreadsheetBench \
  --target-model gpt-5.5 \
  --ckpt ckpt/gpt-5.5/SpreadsheetBench/skill.txt \
  --skip-training \
  --output-dir ./output/spreadsheet_eval
```

See **[Implementation Guide](SkillOpt_Implementation_Guide.md)** for complete details.

---

## 📊 Performance Results

**Average improvement across models:**
- GPT-5.5 Direct Chat: **+23.5 points**
- GPT-5.5 Codex: **+24.8 points**  
- Claude Code: **+19.1 points**

**Best-in-class benchmarks:**
- SpreadsheetBench: 41.8% → 80.7% **(+38.9)**
- OfficeQA: 33.1% → 72.1% **(+39.0)**
- HumanEval: 72.0% → 91.5% **(+19.5)**

**Generalization:** Tied or best on all 52 (model × benchmark × harness) combinations.

---

## 🎯 Learning Paths

### For Researchers (Understanding)
1. Start: [SUMMARY_SkillOpt.md](SUMMARY_SkillOpt.md) — Get the big picture
2. Deep dive: [README_SkillOpt.md](README_SkillOpt.md) — Full technical details
3. Context: [SkillOpt_Repository_Investigation_Report.md](SkillOpt_Repository_Investigation_Report.md) — See what's production-ready
4. Explore: Follow wiki links to concepts, patterns, and techniques

### For Practitioners (Implementation)
1. Start: [SkillOpt_Implementation_Guide.md](SkillOpt_Implementation_Guide.md) — Production integration
2. Validate: [skillopt_integration_examples.py](skillopt_integration_examples.py) — Check your setup
3. Learn: [SkillOpt_Tutorial.ipynb](SkillOpt_Tutorial.ipynb) — Hands-on examples
4. Build: Use techniques catalog to adapt to your use case

### For Decision-Makers (Evaluation)
1. Start: [SkillOpt_Executive_OnePager.md](SkillOpt_Executive_OnePager.md) — Business case
2. Visual: [SkillOpt_OnePager.html](SkillOpt_OnePager.html) — Interactive presentation
3. ROI: Check performance results and production readiness
4. Resources: See GitHub, PyPI, and docs links above

---

## 🔗 Related Papers

*(As you add more papers to the knowledge base, cross-link them here)*

- **Multi-Agent Coordination** — *(Coming soon)* — How SkillOpt skills could coordinate
- **Prompt Engineering** — *(Coming soon)* — Manual techniques vs. SkillOpt automation
- **Meta-Learning** — *(Coming soon)* — Learning to learn connections

---

## 📚 Citations

**BibTeX:**
```bibtex
@article{skillopt2026,
  title={SkillOpt: Self-Evolving Agent Skills via Text-Space Optimization},
  author={Microsoft Research},
  journal={arXiv preprint arXiv:2605.23904},
  year={2026}
}
```

---

## 🤝 Contributing

Found an issue or improvement in this documentation?

1. Check [SkillOpt_Complete_Package_README.md](SkillOpt_Complete_Package_README.md) for full context
2. Update relevant files with corrections or additions
3. Add new concepts/patterns/techniques to knowledge graph if discovered
4. Update this README to reflect changes

---

## 📖 Additional Resources

- **Official Repository:** [github.com/microsoft/SkillOpt](https://github.com/microsoft/SkillOpt)
- **Project Website:** [microsoft.github.io/SkillOpt](https://microsoft.github.io/SkillOpt/)
- **PyPI Package:** [pypi.org/project/skillopt](https://pypi.org/project/skillopt/)
- **ArXiv Paper:** [arxiv.org/abs/2605.23904](https://arxiv.org/abs/2605.23904)

---

**Last Updated:** 2026-06-03  
**Total Documentation:** ~170 KB across 10 files
