# 📚 All Papers Index

**Complete catalog of all research papers in the knowledge base**

---

## Quick Navigation

- **[🧠 Concepts Map](concepts/INDEX.md)** — Cross-paper concepts
- **[🔧 Patterns Library](patterns/INDEX.md)** — Discovered patterns
- **[⚡ Techniques Catalog](techniques/INDEX.md)** — Implementation techniques
- **[← Back to Home](../README.md)**

---

## Papers by Topic

### 🤖 Agent Systems & LLMs

#### SkillOpt: Self-Evolving Agent Skills
**[📁 Paper Folder](../Papers/agent-systems/SkillOpt/) | [📄 Summary](../Papers/agent-systems/SkillOpt/SUMMARY_SkillOpt.md) | [💻 Implementation](../Papers/agent-systems/SkillOpt/SkillOpt_Implementation_Guide.md)**

- **ArXiv:** 2605.23904v2
- **Authors:** Microsoft Research
- **Year:** 2026
- **Status:** ✅ Repository Available | ✅ PyPI Package | ✅ Production Ready

**Key Innovation:** Text-space optimization framework for self-evolving AI agent skills using LLM-as-optimizer architecture.

**Core Concepts:**
- [Text-Space Optimization](concepts/text-space-optimization.md) — Treating prompts as trainable parameters
- [Validation Gating](concepts/validation-gating.md) — Held-out performance gates for skill evolution
- [Rollout-Reflect-Edit Loop](concepts/rollout-reflect-edit.md) — Core pattern for iterative improvement

**Patterns Introduced:**
- [Optimizer-Target Separation](patterns/optimizer-target-separation.md) — Separate models for generation vs. optimization
- [Bounded Edit Budget](patterns/bounded-edit-budget.md) — Textual learning rate for stable training
- [Rejected-Edit Buffer](patterns/rejected-edit-buffer.md) — Negative feedback mechanism

**Techniques:**
- [Cosine Learning Rate Schedule](techniques/cosine-lr-schedule.md) — Smooth decay for edit budgets
- [Minibatch Reflection](techniques/minibatch-reflection.md) — Separate analysis of success/failure cases
- [Slow Update + Meta Skill](techniques/slow-update-meta-skill.md) — Epoch-level memory mechanisms

**Impact:**
- +23.5 to +24.8 points average improvement across models
- Best-in-class on 52/52 (model × benchmark × harness) combinations
- Production package available: `pip install skillopt`

**Resources:**
- **GitHub:** [microsoft/SkillOpt](https://github.com/microsoft/SkillOpt)
- **PyPI:** [skillopt](https://pypi.org/project/skillopt/)
- **Docs:** [microsoft.github.io/SkillOpt](https://microsoft.github.io/SkillOpt/)
- **Tutorial:** [SkillOpt_Tutorial.ipynb](../Papers/agent-systems/SkillOpt/SkillOpt_Tutorial.ipynb)

---

### 🧠 Machine Learning

*(Coming soon — add your first ML paper)*

---

### 💬 Natural Language Processing

*(Coming soon — add your first NLP paper)*

---

### 👁️ Computer Vision

*(Coming soon — add your first CV paper)*

---

### 🎮 Reinforcement Learning

*(Coming soon — add your first RL paper)*

---

### 🔬 Other Topics

*(Coming soon — add papers in new categories)*

---

## Statistics

- **Total Papers:** 1
- **Topics Covered:** Agent Systems
- **Concepts Extracted:** 3
- **Patterns Identified:** 3
- **Techniques Documented:** 3
- **Cross-Links:** 15+

---

## Timeline View

### 2026
- **[SkillOpt](../Papers/agent-systems/SkillOpt/)** (2605.23904v2) — Self-Evolving Agent Skills

---

## By Research Group

### Microsoft Research
- [SkillOpt](../Papers/agent-systems/SkillOpt/) — Self-evolving agent skills via text-space optimization

---

## By Application Domain

### AI Agent Development
- [SkillOpt](../Papers/agent-systems/SkillOpt/) — Automatic skill improvement for agents

### Prompt Engineering
- [SkillOpt](../Papers/agent-systems/SkillOpt/) — Automated prompt optimization

### MLOps & Training
- [SkillOpt](../Papers/agent-systems/SkillOpt/) — Training frameworks for text-based parameters

---

## Search Tips

### Finding Related Papers
1. Browse by **topic** (Agent Systems, ML, NLP, etc.)
2. Explore **concepts** (e.g., all papers using validation gating)
3. Check **patterns** (e.g., all papers using optimizer-target separation)
4. Filter by **techniques** (e.g., all papers using cosine learning rate schedules)

### Using Wiki Links
- Every concept/pattern/technique page lists **all papers that use it**
- Follow cross-references to discover related work
- Build learning paths by chaining related concepts

---

**Last Updated:** 2026-06-03

**Next Paper to Add:** *(Your choice! Use `tools/new_paper.py` to add it)*
