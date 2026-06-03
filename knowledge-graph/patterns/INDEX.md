# 🔧 Patterns Library

**Discovered architectural and design patterns across papers**

Patterns are recurring solutions to common problems in AI systems design, implementation, and training.

---

## Quick Navigation

- **[📚 All Papers](../INDEX.md)** — Back to papers index
- **[🧠 Concepts Map](../concepts/INDEX.md)** — Core concepts
- **[⚡ Techniques Catalog](../techniques/INDEX.md)** — Implementation techniques
- **[← Back to Home](../../README.md)**

---

## Architecture Patterns

### Optimizer-Target Separation
**Pattern:** Separate the model being optimized (target) from the model doing optimization (optimizer).

**Problem:**
- How to improve an AI system's performance without direct gradient access
- Need for interpretable, controllable optimization
- Want to avoid expensive retraining of large models

**Solution:**
- **Target Model:** Executes the task using current skills/prompts
- **Optimizer Model:** Analyzes performance and generates improvements
- Two models can be different sizes, architectures, or even modalities
- Optimizer focuses on meta-cognitive tasks (reflection, planning, editing)

**Benefits:**
- Target model can be lightweight or API-based
- Optimizer model can be specialized for improvement generation
- Clear separation of concerns
- Enables human-in-the-loop optimization

**Papers Using This Pattern:**
- **[SkillOpt](../../Papers/agent-systems/SkillOpt/)** — Target executes skills, Optimizer generates edits

**Related Concepts:**
- [Text-Space Optimization](../concepts/text-space-optimization.md)
- [Rollout-Reflect-Edit Loop](../concepts/rollout-reflect-edit.md)

**Code Example:**
See [SkillOpt Implementation](../../Papers/agent-systems/SkillOpt/skillopt_implementation.py) — `SkillOptimizer` class

---

### Bounded Edit Budget
**Pattern:** Limit the size of textual edits to prevent catastrophic changes, analogous to learning rates in numerical optimization.

**Problem:**
- Large text edits can completely change skill semantics
- Hard to recover from bad edits
- Need stability during optimization
- Want gradual, controllable improvement

**Solution:**
- Define maximum edit size (e.g., 20% of original text)
- Use token-based or character-based limits
- Schedule edit budgets (e.g., cosine decay over training)
- Reject edits exceeding budget
- Separate addition and deletion budgets if needed

**Benefits:**
- Prevents drastic skill changes in one step
- Smoother convergence
- Easier to debug and understand changes
- Natural regularization effect

**Papers Using This Pattern:**
- **[SkillOpt](../../Papers/agent-systems/SkillOpt/)** — 20% edit budget with cosine schedule

**Related Concepts:**
- [Text-Space Optimization](../concepts/text-space-optimization.md)
- [Validation Gating](../concepts/validation-gating.md)

**Related Techniques:**
- [Cosine Learning Rate Schedule](../techniques/cosine-lr-schedule.md)

**Code Example:**
See [SkillOpt Implementation](../../Papers/agent-systems/SkillOpt/skillopt_implementation.py) — `_apply_edit_budget()` method

---

### Rejected-Edit Buffer
**Pattern:** Store rejected edits as negative examples to prevent re-exploring bad directions.

**Problem:**
- Optimizer may repeatedly suggest similar bad edits
- No memory of what didn't work
- Want to learn from failures
- Need negative feedback signal

**Solution:**
- Maintain a buffer of rejected edits
- Include rejection reasons (e.g., validation performance drop)
- Feed rejected edits + reasons to optimizer during reflection
- "Here's what we tried before and why it failed"
- Helps optimizer avoid similar mistakes

**Benefits:**
- Faster convergence (fewer wasted iterations)
- Richer feedback signal (success + failure)
- Natural curriculum learning (hardest cases accumulate)
- Debuggability (see what was tried and rejected)

**Papers Using This Pattern:**
- **[SkillOpt](../../Papers/agent-systems/SkillOpt/)** — Slow-update mode with rejected edit memory

**Related Concepts:**
- [Validation Gating](../concepts/validation-gating.md)
- [Rollout-Reflect-Edit Loop](../concepts/rollout-reflect-edit.md)

**Related Techniques:**
- [Slow Update + Meta Skill](../techniques/slow-update-meta-skill.md)

---

## Training Patterns

### Minibatch Reflection
**Pattern:** Analyze performance on small batches separately before aggregating insights.

**Problem:**
- Reflecting on all examples at once is expensive and noisy
- Different failure modes need different fixes
- Want focused, actionable feedback
- Need to identify patterns in successes vs. failures

**Solution:**
- Split training data into minibatches
- Reflect on each batch independently
- Separate successful from failed examples
- Generate targeted insights per batch
- Aggregate reflections across batches for final edit proposal

**Benefits:**
- More specific, actionable feedback
- Lower LLM costs (smaller context per reflection)
- Better pattern detection
- Parallelizable across batches

**Papers Using This Pattern:**
- **[SkillOpt](../../Papers/agent-systems/SkillOpt/)** — Batch size 5-10 for reflection

**Related Concepts:**
- [Rollout-Reflect-Edit Loop](../concepts/rollout-reflect-edit.md)

**Related Techniques:**
- [Minibatch Reflection](../techniques/minibatch-reflection.md) (detailed implementation)

---

## Data Management Patterns

### Held-Out Validation Gating
**Pattern:** Use validation set performance as binary gate for accepting changes.

**Problem:**
- How to prevent overfitting in text-space optimization
- Need objective quality control
- Want generalization beyond training data
- Avoid degenerative optimization

**Solution:**
- Split data: train (for reflection), validation (for gating), test (for final eval)
- After each edit, evaluate on validation set
- Accept edit only if validation performance improves
- Validation set never influences edit generation (only accept/reject)

**Benefits:**
- Strong generalization guarantee
- Prevents overfitting
- Simple, objective decision rule
- Mirrors classical ML best practices

**Papers Using This Pattern:**
- **[SkillOpt](../../Papers/agent-systems/SkillOpt/)** — Core quality control mechanism

**Related Concepts:**
- [Validation Gating](../concepts/validation-gating.md)

**Code Example:**
See [SkillOpt Implementation](../../Papers/agent-systems/SkillOpt/skillopt_implementation.py) — `_evaluate_skill()` method

---

## Meta-Learning Patterns

### Slow Update + Meta Skill
**Pattern:** Maintain epoch-level memory and meta-information alongside skill text.

**Problem:**
- Need to track optimization history
- Want to avoid cycling between similar edits
- Benefit from long-term memory
- Need context beyond current skill state

**Solution:**
- **Meta Skill:** Store rejected edits, historical reflections, discovered patterns
- **Slow Update:** Only update meta skill at epoch boundaries, not every iteration
- Feed meta skill to optimizer during reflection
- Provides broader context for decision-making

**Benefits:**
- Richer optimization context
- Avoids local optima and cycles
- Progressive knowledge accumulation
- Better long-term planning

**Papers Using This Pattern:**
- **[SkillOpt](../../Papers/agent-systems/SkillOpt/)** — Slow-update mode with meta skill buffer

**Related Concepts:**
- [Rollout-Reflect-Edit Loop](../concepts/rollout-reflect-edit.md)

**Related Techniques:**
- [Slow Update + Meta Skill](../techniques/slow-update-meta-skill.md) (detailed implementation)

---

## Emerging Patterns

*(Add patterns as you discover them across papers)*

### Curriculum Learning
**Status:** 🔴 Not yet documented
**Waiting for:** Multi-task or curriculum learning paper

### Ensemble Skills
**Status:** 🔴 Not yet documented
**Waiting for:** Multi-agent or ensemble methods paper

### Human-in-the-Loop Optimization
**Status:** 🔴 Not yet documented
**Waiting for:** Interactive ML paper

---

## Pattern Relationships

```
Architecture Patterns
├── Optimizer-Target Separation
│   ├── Enables: Text-Space Optimization
│   └── Uses: Reflection-based feedback
└── Bounded Edit Budget
    ├── Provides: Training stability
    └── Uses: Cosine schedule

Training Patterns
├── Minibatch Reflection
│   ├── Enables: Efficient scaling
│   └── Feeds: Edit proposals
└── Held-Out Validation Gating
    ├── Ensures: Generalization
    └── Uses: Rejected-Edit Buffer

Meta-Learning Patterns
└── Slow Update + Meta Skill
    ├── Provides: Long-term memory
    └── Uses: Rejected-Edit Buffer
```

---

## How to Use This Library

### For System Designers
1. Browse patterns by category (Architecture, Training, Data, Meta-Learning)
2. Understand problem-solution pairs
3. See code examples from real papers
4. Adapt patterns to your use case

### For Researchers
1. Identify patterns in new papers you read
2. Compare with existing patterns
3. Document variations and improvements
4. Add new patterns to the library

---

## Contributing

### Adding a New Pattern
1. Create `pattern-name.md` using the template (see `templates/pattern_template.md`)
2. Add entry to this INDEX.md under appropriate category
3. Cross-link to related papers, concepts, and techniques
4. Include code example if available

---

**Total Patterns:** 6  
**Last Updated:** 2026-06-03
