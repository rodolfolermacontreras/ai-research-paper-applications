# SkillOpt: Executive One-Pager
**Self-Evolving Agent Skills through Text-Space Optimization**

---

## 🎯 Core Concept

**SkillOpt** is the first systematic, controllable text-space optimizer for agent skills. It treats a skill document as the **external trainable state** of a frozen agent—similar to how weights are optimized in deep learning, but in natural language.

**Key Innovation:** A separate optimizer model turns scored rollouts into bounded add/delete/replace edits on a skill document, accepting edits **only when they improve held-out validation performance**.

### The Deep Learning Analogy

| Deep Learning | SkillOpt |
|--------------|----------|
| Parameters | Skill document |
| Gradient direction | Trajectory-derived edits |
| Learning rate | Edit budget (max edits/step) |
| Validation check | Held-out selection gate |
| Batch/minibatch/schedule | Rollout batches, reflection minibatches, edit schedules |

---

## 💻 Core Algorithm

### Algorithm Overview

```python
# SkillOpt Optimization Loop

Input:
  - Frozen target model M
  - Optimizer model O
  - Initial skill s₀
  - Train/validation/test splits
  - Edit budget schedule Lₜ
  
Process:
  for each epoch:
    for each optimization step:
      # 1. Forward Pass: Rollout Evidence
      trajectories = execute_batch(M, current_skill, train_split)
      
      # 2. Backward Pass: Minibatch Reflection
      failures, successes = split_trajectories(trajectories)
      failure_edits = O.analyze_failures(failures)
      success_edits = O.analyze_successes(successes)
      
      # 3. Bounded Text Update
      merged_edits = merge_and_rank(failure_edits, success_edits)
      selected_edits = merged_edits[:Lₜ]  # Apply edit budget
      candidate_skill = apply_edits(current_skill, selected_edits)
      
      # 4. Validation Gate
      score_candidate = evaluate(M, candidate_skill, validation_split)
      score_current = evaluate(M, current_skill, validation_split)
      
      if score_candidate > score_current:
        current_skill = candidate_skill  # Accept
        if score_candidate > best_score:
          best_skill = candidate_skill
      else:
        rejected_buffer.add(selected_edits)  # Negative feedback
    
    # 5. Epoch-wise Slow/Meta Update
    slow_update = compare_epochs(prev_skill, current_skill)
    meta_skill = update_optimizer_memory()

Output: best_skill.md (300-2000 tokens)
```

### Key Components

**1. Rollout Batch** - Execute tasks with current skill, collect trajectories

**2. Minibatch Reflection** - Analyze failures/successes in batches to find recurring patterns

**3. Edit Operations**
```markdown
- APPEND: Add content at end
- INSERT_AFTER: Insert after specific heading/text
- REPLACE: Swap exact text
- DELETE: Remove exact text
```

**4. Edit Budget (Learning Rate)**
- Cosine schedule: Start large (Lₜ=8), decay to small (Lₜ=2)
- Prevents unbounded rewrites
- Maintains skill continuity

**5. Validation Gate** - Accept only if `score_new > score_current` (strict improvement)

**6. Rejected-Edit Buffer** - Store failed edits as negative feedback for future steps

**7. Slow/Meta Update** (Epoch-boundary)
- Compare same tasks under previous vs. current skill
- Write longitudinal guidance to protected section
- Captures durable patterns invisible to step-level edits

---

## 📊 Results & Validation

### Performance Highlights

**Best or tied-best on 52/52 evaluated (model, benchmark, harness) cells**

| Benchmark | No Skill | SkillOpt | Gain |
|-----------|----------|----------|------|
| SearchQA | 77.7 | 87.3 | **+9.6** |
| SpreadsheetBench | 41.8 | 80.7 | **+38.9** |
| OfficeQA | 33.1 | 72.1 | **+39.0** |
| DocVQA | 78.8 | 91.2 | **+12.4** |
| LiveMathBench | 37.6 | 66.9 | **+29.3** |
| ALFWorld | 83.6 | 95.5 | **+11.9** |

**GPT-5.5 Average:** +23.5 points (direct chat), +24.8 (Codex), +19.1 (Claude Code)

### Key Findings

✅ **Wins on all 52 cells** - Best or tied across 7 models, 6 benchmarks, 3 harnesses

✅ **Beats all baselines** - Outperforms human skills, one-shot LLM, Trace2Skill, TextGrad, GEPA, EvoSkill by +5.4 points (oracle baseline)

✅ **Compact skills** - Final artifacts: 300-2,000 tokens (median ~920 tokens)

✅ **Edit economy** - Only 1-4 accepted edits produce massive gains

✅ **Transferable** - Skills transfer across:
- Model scales (GPT-5.4 → GPT-5.4-mini: +9.4 on SpreadsheetBench)
- Harnesses (Codex → Claude Code: +59.7 on SpreadsheetBench)
- Benchmarks (OlympiadBench → Omni-MATH: +3.7 on GPT-5.4)

---

## 🛠️ Applications

### When to Use SkillOpt

**Ideal Use Cases:**
1. **Procedural Tasks** - Where rules, tool policies, output formats matter
2. **Domain Adaptation** - Adapt frozen frontier models to specific domains
3. **Cost-Constrained Settings** - No model weights to update
4. **Reusable Artifacts** - Train once, deploy across models/harnesses
5. **Auditable AI** - Skills are human-readable, inspectable text

**Example Domains:**
- 📊 Spreadsheet automation (41.8 → 80.7)
- 📄 Document QA (33.1 → 72.1)
- 🧮 Mathematical reasoning (37.6 → 66.9)
- 🏠 Embodied agents (83.6 → 95.5)
- 🔍 Information retrieval (77.7 → 87.3)

### What SkillOpt Learns

Representative learned rules from the paper:

**SearchQA:** "Infer the expected answer type from clue wording, then choose the shortest canonical entity supported by co-occurring distinctive evidence."

**SpreadsheetBench:** "Inspect workbook structure and formulas, then write evaluated static values across the full requested target range instead of relying on Excel recalculation."

**OfficeQA:** "Treat oracle parsed pages as primary evidence, lock table/date/unit context, and output exactly the requested rounded value without extra labels."

**DocVQA:** "For tables, forms, charts, and legends, first bind the question to the exact visual row/header/field, then copy only the aligned answer span."

**LiveMathBench:** "In strongest-statement MCQs, rank choices by theorem strength and prefer a justified stronger-result option over true but weaker corollaries."

**ALFWorld:** "Keep a horizon-aware visited/frontier ledger, diversify search after repeated same-type failures, and avoid revisiting the destination until holding the target."

---

## 🚀 How to Use: Practical Implementation Guide

### Step 1: Setup

```python
# Define your components
target_model = "gpt-5.5"  # Frozen model to adapt
optimizer_model = "gpt-5.5"  # Can be same or stronger
harness = "direct_chat"  # or "codex", "claude_code"
benchmark = "your_task"

# Split your data
train_split = dataset[:200]       # Training rollouts
validation_split = dataset[200:250]  # Selection gate
test_split = dataset[250:]        # Final evaluation only

# Initialize skill
initial_skill = """
# Task: [Your Domain]

## Core Approach
[Basic strategy]

## Key Guidelines
[Initial rules]
"""
```

### Step 2: Configure Optimizer

```python
config = {
    "epochs": 4,
    "rollout_batch_size": 40,
    "reflection_minibatch_size": 8,
    "edit_budget_initial": 4,
    "edit_budget_schedule": "cosine",  # or "constant", "linear"
    "edit_budget_floor": 2,
    "validation_gate": "strict_improvement",  # score_new > score_current
    "slow_update_enabled": True,
    "slow_update_samples": 20,
    "meta_skill_enabled": True,
    "rejected_buffer_enabled": True,
}
```

### Step 3: Run Optimization

```python
from skillopt import SkillOptimizer

optimizer = SkillOptimizer(
    target_model=target_model,
    optimizer_model=optimizer_model,
    harness=harness,
    config=config
)

best_skill, history = optimizer.optimize(
    initial_skill=initial_skill,
    train_data=train_split,
    validation_data=validation_split,
    test_data=test_split
)

# Output: best_skill.md + optimization history
```

### Step 4: Deploy

```python
# The optimized skill is just a text file
with open("best_skill.md", "w") as f:
    f.write(best_skill)

# Deploy with your frozen model
def run_task(task_input):
    system_prompt = best_skill  # Prepend to system message
    response = target_model.complete(
        system=system_prompt,
        user=task_input
    )
    return response
```

### Step 5: Transfer (Optional)

```python
# Transfer to smaller model
smaller_model_result = evaluate(
    model="gpt-5.4-mini",
    skill=best_skill,  # Same skill, no retraining
    data=test_split
)

# Transfer to different harness
codex_result = evaluate(
    model=target_model,
    skill=best_skill,  # Same skill
    harness="codex",   # Different execution environment
    data=test_split
)
```

---

## 📝 Implementation Checklist

### Essential Components

- [ ] **Frozen Target Model** - The model you're adapting (no weight updates)
- [ ] **Optimizer Model** - Can be same or stronger (GPT-5.5 recommended)
- [ ] **Train/Val/Test Splits** - 2:1:7 default ratio
- [ ] **Scoring Function** - Automatic verifier for your domain
- [ ] **Initial Skill** - 100-500 token starting point
- [ ] **Edit Budget Schedule** - Cosine decay recommended

### Optimizer Prompts (Required)

1. **analyst_error.md** - Analyzes failure minibatches → proposes corrective edits
2. **analyst_success.md** - Analyzes success minibatches → proposes reinforcement edits
3. **merge_failure.md** - Merges failure patches, deduplicates
4. **merge_success.md** - Merges success patches conservatively
5. **merge_final.md** - Final merge (failure-prioritized)
6. **ranking.md** - Ranks edits by systematic impact, selects top Lₜ
7. **slow_update.md** - Epoch-boundary longitudinal guidance
8. **meta_skill.md** - Optimizer-side memory (not deployed)

### Validation & Safeguards

- [ ] **Held-out gate** - Evaluate every candidate on validation split
- [ ] **Strict improvement** - Accept only if `score_new > score_current`
- [ ] **Edit independence** - No two edits target same text region
- [ ] **Protected sections** - Slow update section off-limits to step edits
- [ ] **Rejected buffer** - Store failed edits for negative feedback
- [ ] **Deduplication** - Cache skill hashes, skip re-evaluation

---

## 🎓 Key Insights & Best Practices

### What Makes SkillOpt Work

1. **Bounded Updates** - Edit budget prevents unbounded rewrites, maintains continuity
2. **Validation Gating** - Prevents plausible but harmful edits from accumulating
3. **Minibatch Reflection** - Finds recurring patterns, not anecdotal fixes
4. **Failure Prioritization** - Corrective edits outweigh reinforcement edits
5. **Negative Feedback** - Rejected edits inform future optimizer calls
6. **Separation of Concerns** - Deployed skill stays compact; optimizer memory separate

### Common Pitfalls to Avoid

❌ **Don't skip validation gate** - Unconditional reflection accumulates harmful edits

❌ **Don't use unbounded rewrites** - Destroys continuity, loses previous lessons

❌ **Don't ignore edit economy** - 1-4 accepted edits is normal; more isn't better

❌ **Don't mix training-model and optimizer guidance** - Keep meta-skill separate

❌ **Don't deploy on test set** - Use held-out test only for final reporting

### Hyperparameter Guidance

**Most Robust Settings (from ablations):**
- Rollout batch: 24-40 (larger for procedural tasks)
- Minibatch size: 4-8 (sweet spot for pattern detection)
- Edit budget: 4 initial, cosine decay to 2 floor
- Slow update samples: 20 per epoch
- Epochs: 4 (diminishing returns after)

**When to Tune:**
- **Small train set** (<50 examples): Reduce batch size, increase epochs
- **Long trajectories**: Increase rollout accumulation factor
- **High-variance domain**: Increase minibatch size for stability

---

## 💡 Conclusions

### Main Contributions

1. **First systematic text-space optimizer** with training-style controls (batches, learning rates, validation, schedules)

2. **52/52 best-or-tied performance** across models, benchmarks, harnesses

3. **Compact, transferable artifacts** - 300-2K token skills work across models and harnesses

4. **Procedural knowledge extraction** - Learns generalizable rules, not instance-specific fixes

5. **Zero inference-time cost** - Optimizer runs offline; deployment adds only a text prompt

### When SkillOpt Beats Other Approaches

| Approach | SkillOpt Advantage |
|----------|-------------------|
| **No skill** | +23.5 points average on GPT-5.5 |
| **Human-written skill** | Learns from rollout feedback, not intuition |
| **One-shot LLM skill** | Iterative improvement vs. single generation |
| **TextGrad/GEPA** | Optimizes persistent skill artifact, not just prompts |
| **Trace2Skill** | Validation gate prevents overfitting to training trajectories |
| **EvoSkill** | Bounded updates + rejected-edit buffer = stability |
| **Fine-tuning** | No weight updates; works on closed models; reusable across models |

### Limitations & Future Work

**Current Limitations:**
- Requires automatic scoring (not ideal for open-ended creative tasks)
- Training cost: 0.6M-46.4M tokens per test-point gained (paid once)
- Single skill per domain (not skill libraries)
- Optimizes for one target; heterogeneous domains need multiple skills

**Future Directions:**
- Skill libraries with shared infrastructure
- Reward-free validation for open-ended tasks
- Self-distillation: optimize skill → fine-tune model with skill
- Curriculum learning across benchmarks

---

## 📚 References & Resources

**Paper:** [SkillOpt: Executive Strategy for Self-Evolving Agent Skills](https://aka.ms/SkillOpt)  
**Authors:** Yifan Yang et al. (Microsoft, Shanghai Jiao Tong University, Tongji University, Fudan University)  
**Published:** May 2026, arXiv:2605.23904v2

**Key Comparisons:**
- Human skill, LLM skill (one-shot)
- Trace2Skill (trajectory distillation)
- TextGrad (gradient-style prompt optimization)
- GEPA (reflective prompt evolution)
- EvoSkill (skill-folder evolution)

**Benchmarks Evaluated:**
- SearchQA, SpreadsheetBench, OfficeQA, DocVQA, LiveMathematicianBench, ALFWorld

**Models Tested:**
- GPT-5.5, GPT-5.4, GPT-5.4-mini, GPT-5.4-nano, GPT-5.2
- Qwen3.5-4B, Qwen3.6-35B-A3B

---

## 🔑 Takeaway

**SkillOpt proves that compact natural-language skills can serve as a practical domain-adaptation layer for frontier agents, enabling reusable improvement without modifying model weights.**

**Bottom Line:** If you have a frozen model, a scoring function, and a target domain, SkillOpt can optimize a 300-2K token skill that delivers +10 to +40 point gains—deployable across models and harnesses.

---

*For implementation details, optimizer prompts, and full experimental protocol, see Appendices A-C in the paper.*
