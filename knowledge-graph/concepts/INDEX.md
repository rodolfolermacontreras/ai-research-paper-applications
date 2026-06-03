# 🧠 Concepts Map

**Cross-paper concepts and ideas extracted from research**

Concepts are fundamental ideas, mechanisms, or principles that appear across multiple papers or are central to understanding a research area.

---

## Quick Navigation

- **[📚 All Papers](../INDEX.md)** — Back to papers index
- **[🔧 Patterns Library](../patterns/INDEX.md)** — Architectural patterns
- **[⚡ Techniques Catalog](../techniques/INDEX.md)** — Implementation techniques
- **[← Back to Home](../../README.md)**

---

## Core Concepts

### Text-Space Optimization
**Definition:** Treating prompts and instructions as trainable parameters in text space, rather than numeric weights.

**Key Ideas:**
- LLM-as-optimizer: Use a language model to generate improved versions of text-based parameters
- Natural language gradients: Reflections and critiques serve as textual gradients
- Edit operations replace weight updates
- Bounded edits maintain stability (like learning rates in numeric optimization)

**Papers Using This Concept:**
- **[SkillOpt](../../Papers/agent-systems/SkillOpt/)** — Core innovation

**Related Concepts:**
- [Validation Gating](#validation-gating) — Quality control for text-space updates
- [Rollout-Reflect-Edit Loop](#rollout-reflect-edit-loop) — Execution pattern

**Related Patterns:**
- [Optimizer-Target Separation](../patterns/optimizer-target-separation.md)
- [Bounded Edit Budget](../patterns/bounded-edit-budget.md)

---

### Validation Gating
**Definition:** Using held-out validation set performance as a gate to accept or reject skill updates.

**Key Ideas:**
- Separate training, validation, and test sets (like classical ML)
- Only accept edits that improve validation performance
- Prevents overfitting to training examples
- Creates natural selection pressure for generalizable skills

**Papers Using This Concept:**
- **[SkillOpt](../../Papers/agent-systems/SkillOpt/)** — Core quality control mechanism

**Related Concepts:**
- [Text-Space Optimization](#text-space-optimization) — What is being gated
- [Rejected-Edit Buffer](../patterns/rejected-edit-buffer.md) — What happens to rejected edits

**Related Techniques:**
- [Minibatch Reflection](../techniques/minibatch-reflection.md) — How validation is performed

---

### Rollout-Reflect-Edit Loop
**Definition:** Iterative improvement cycle of executing skills, analyzing performance, and editing based on feedback.

**Key Ideas:**
- **Rollout:** Execute current skill on training examples
- **Reflect:** Analyze successes and failures to generate insights
- **Edit:** Propose improvements based on reflections
- Cycle repeats until convergence or budget exhausted

**Papers Using This Concept:**
- **[SkillOpt](../../Papers/agent-systems/SkillOpt/)** — Core training loop

**Related Concepts:**
- [Text-Space Optimization](#text-space-optimization) — Framework this loop operates in
- [Validation Gating](#validation-gating) — Gate between reflect and edit

**Related Patterns:**
- [Optimizer-Target Separation](../patterns/optimizer-target-separation.md)
- [Bounded Edit Budget](../patterns/bounded-edit-budget.md)

**Related Techniques:**
- [Minibatch Reflection](../techniques/minibatch-reflection.md)
- [Slow Update + Meta Skill](../techniques/slow-update-meta-skill.md)

---

## Emerging Concepts

*(Add more concepts as you analyze new papers)*

### Multi-Agent Coordination
**Status:** 🔴 Not yet covered
**Waiting for:** Next agent systems paper

### Knowledge Distillation
**Status:** 🔴 Not yet covered
**Waiting for:** ML fundamentals paper

### Few-Shot Learning
**Status:** 🔴 Not yet covered
**Waiting for:** Meta-learning paper

---

## Concept Relationships

```
Text-Space Optimization
├── Validation Gating (quality control)
├── Rollout-Reflect-Edit Loop (execution pattern)
├── Optimizer-Target Separation (architecture)
└── Bounded Edit Budget (stability)

Validation Gating
├── Rejected-Edit Buffer (negative feedback)
└── Minibatch Reflection (evaluation method)

Rollout-Reflect-Edit Loop
├── Slow Update + Meta Skill (memory mechanism)
└── Cosine LR Schedule (budget control)
```

---

## How to Use This Map

### For Researchers
1. **Understand Fundamentals:** Read concept pages to grasp core ideas
2. **Trace Origins:** See which papers introduced each concept
3. **Follow Evolution:** Track how concepts are refined across papers
4. **Discover Connections:** Use relationship map to find related ideas

### For Practitioners
1. **Find Techniques:** Each concept links to implementation techniques
2. **See Patterns:** Concepts connect to architectural patterns
3. **Get Code:** Follow links to papers with code examples
4. **Build Understanding:** Start with concepts, drill into specifics

---

## Contributing

### Adding a New Concept
1. Create `concept-name.md` using the template
2. Add entry to this INDEX.md
3. Cross-link to related papers, patterns, and techniques
4. Update relationship diagram

### Template Structure
```markdown
# Concept Name

**Definition:** One-sentence definition

## Key Ideas
- Bullet list of core ideas
- Keep it clear and concise

## Papers Using This Concept
- [Paper Name](link) — How it uses the concept

## Related Concepts / Patterns / Techniques
- [Related Item](link)

## Code Examples
(If applicable)

## Further Reading
(External resources)
```

---

**Total Concepts:** 3  
**Last Updated:** 2026-06-03
