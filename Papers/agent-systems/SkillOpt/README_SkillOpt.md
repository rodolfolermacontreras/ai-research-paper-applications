# SkillOpt: Self-Evolving Agent Skills

**Complete Implementation and Tutorial for Text-Space Skill Optimization**

Based on: [arXiv:2605.23904v2](https://arxiv.org/abs/2605.23904) "SkillOpt: Executive Strategy for Self-Evolving Agent Skills"

---

## 🎯 Overview

This repository contains a complete, production-ready implementation of **SkillOpt**, the first systematic text-space optimizer for agent skills. SkillOpt treats a skill document as the **external trainable state** of a frozen agent—similar to how weights are optimized in deep learning, but in natural language.

### Key Innovation

A separate optimizer model turns scored rollouts into bounded add/delete/replace edits on a skill document, accepting edits **only when they improve held-out validation performance**.

### Performance Highlights

SkillOpt achieves **best or tied-best on 52/52 evaluated cells** across:
- 7 models (GPT-5.5, GPT-5.4, GPT-5.2, Claude variants, Qwen)
- 6 benchmarks (SearchQA, SpreadsheetBench, OfficeQA, DocVQA, LiveMathBench, ALFWorld)
- 3 harnesses (direct chat, Codex, Claude Code)

**Average gains on GPT-5.5**: +23.5 points absolute improvement

---

## 📁 Repository Contents

```
.
├── SkillOpt_Executive_OnePager.md    # Comprehensive one-pager with theory & practice
├── skillopt_implementation.py         # Full Python implementation
├── SkillOpt_Tutorial.ipynb           # Interactive Jupyter tutorial
├── README_SkillOpt.md                # This file
└── examples/                         # (Future: Domain-specific examples)
```

---

## 🚀 Quick Start

### 1. Installation

```bash
# Clone repository
git clone https://github.com/rodolfolermacontreras/ai-research-paper-applications.git
cd ai-research-paper-applications

# Install dependencies
pip install -r requirements.txt

# For Jupyter tutorial
pip install jupyter matplotlib seaborn pandas numpy
```

### 2. Run Basic Example

```python
from skillopt_implementation import SkillOptimizer, SkillDocument

# Define your initial skill
initial_skill = SkillDocument(
    content="""# Task: Customer Support

## Core Approach
Address customer inquiries professionally and efficiently.

## Key Guidelines
- Listen to the customer's concern
- Provide clear, accurate information
- Follow up to ensure satisfaction
"""
)

# Configure optimizer
optimizer = SkillOptimizer(
    target_model=your_llm_function,      # e.g., GPT-4, Claude
    optimizer_model=your_optimizer_llm,   # Stronger model for reflection
    rollout_batch_size=40,
    reflection_minibatch_size=8,
    edit_budget_initial=4,
    edit_budget_floor=2,
    epochs=4,
)

# Run optimization
best_skill, history = optimizer.optimize(
    initial_skill=initial_skill,
    train_tasks=train_data,
    validation_tasks=val_data,
)

print(best_skill.content)
```

### 3. Explore Tutorial

```bash
jupyter notebook SkillOpt_Tutorial.ipynb
```

---

## 📊 Results from Paper

| Benchmark | No Skill | SkillOpt | Gain |
|-----------|----------|----------|------|
| SearchQA | 77.7 | 87.3 | **+9.6** |
| SpreadsheetBench | 41.8 | 80.7 | **+38.9** |
| OfficeQA | 33.1 | 72.1 | **+39.0** |
| DocVQA | 78.8 | 91.2 | **+12.4** |
| LiveMathBench | 37.6 | 66.9 | **+29.3** |
| ALFWorld | 83.6 | 95.5 | **+11.9** |

**Key Findings:**
- ✅ Compact skills: 300-2,000 tokens (median ~920)
- ✅ Edit economy: Only 1-4 accepted edits produce massive gains
- ✅ Transferable: Skills work across models, harnesses, and benchmarks
- ✅ Zero inference cost: Optimizer runs offline; deployment adds only a text prompt

---

## 💻 Implementation Guide

### Core Algorithm

```python
# SkillOpt Optimization Loop

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
        selected_edits = merged_edits[:edit_budget]
        candidate_skill = apply_edits(current_skill, selected_edits)
        
        # 4. Validation Gate
        if evaluate(M, candidate_skill, val_split) > evaluate(M, current_skill, val_split):
            current_skill = candidate_skill  # Accept
        else:
            rejected_buffer.add(selected_edits)  # Negative feedback
    
    # 5. Epoch-wise Slow/Meta Update
    slow_update = compare_epochs(prev_skill, current_skill)
```

### Key Components

1. **Rollout Batch**: Execute tasks with current skill, collect trajectories
2. **Minibatch Reflection**: Analyze failures/successes in batches to find recurring patterns
3. **Edit Operations**: APPEND, INSERT_AFTER, REPLACE, DELETE
4. **Edit Budget (Learning Rate)**: Cosine schedule from 8→2, prevents unbounded rewrites
5. **Validation Gate**: Accept only if `score_new > score_current` (strict improvement)
6. **Rejected-Edit Buffer**: Store failed edits as negative feedback
7. **Slow/Meta Update**: Epoch-boundary longitudinal insights

---

## 🛠️ API Integration Examples

### OpenAI (GPT-4)

```python
import openai

openai_client = openai.OpenAI(api_key="your-key")

def gpt4_target_model(skill: str, task: dict) -> dict:
    response = openai_client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": skill},
            {"role": "user", "content": task["input"]}
        ],
        max_tokens=500,
    )
    
    output = response.choices[0].message.content
    # ... scoring logic ...
    
    return {"output": output, "success": success, "score": score}
```

### Anthropic (Claude)

```python
import anthropic

anthropic_client = anthropic.Anthropic(api_key="your-key")

def claude_target_model(skill: str, task: dict) -> dict:
    response = anthropic_client.messages.create(
        model="claude-opus-4-5",
        max_tokens=500,
        system=skill,
        messages=[{"role": "user", "content": task["input"]}],
    )
    
    output = response.content[0].text
    # ... scoring logic ...
    
    return {"output": output, "success": success, "score": score}
```

---

## 📚 Applications

### Ideal Use Cases

1. **Procedural Tasks** - Where rules, tool policies, output formats matter
2. **Domain Adaptation** - Adapt frozen frontier models to specific domains
3. **Cost-Constrained Settings** - No model weights to update
4. **Reusable Artifacts** - Train once, deploy across models/harnesses
5. **Auditable AI** - Skills are human-readable, inspectable text

### Example Domains

- 📊 **Spreadsheet automation** (41.8 → 80.7)
- 📄 **Document QA** (33.1 → 72.1)
- 🧮 **Mathematical reasoning** (37.6 → 66.9)
- 🏠 **Embodied agents** (83.6 → 95.5)
- 🔍 **Information retrieval** (77.7 → 87.3)

### Learned Rules from Paper

**SearchQA:**  
*"Infer the expected answer type from clue wording, then choose the shortest canonical entity supported by co-occurring distinctive evidence."*

**SpreadsheetBench:**  
*"Inspect workbook structure and formulas, then write evaluated static values across the full requested target range instead of relying on Excel recalculation."*

**OfficeQA:**  
*"Treat oracle parsed pages as primary evidence, lock table/date/unit context, and output exactly the requested rounded value without extra labels."*

**LiveMathBench:**  
*"In strongest-statement MCQs, rank choices by theorem strength and prefer a justified stronger-result option over true but weaker corollaries."*

---

## ⚙️ Configuration

### Recommended Hyperparameters

```python
config = {
    "epochs": 4,
    "rollout_batch_size": 40,           # 24-40 for most tasks
    "reflection_minibatch_size": 8,     # 4-8 sweet spot
    "edit_budget_initial": 4,           # Start high
    "edit_budget_schedule": "cosine",   # or "linear", "constant"
    "edit_budget_floor": 2,             # Minimum edits per step
    "validation_gate": "strict_improvement",
    "slow_update_enabled": True,
    "slow_update_samples": 20,
    "rejected_buffer_enabled": True,
}
```

### When to Tune

- **Small train set** (<50 examples): Reduce batch size, increase epochs
- **Long trajectories**: Increase rollout accumulation factor
- **High-variance domain**: Increase minibatch size for stability

---

## 📖 Documentation

### Complete Guide

See [`SkillOpt_Executive_OnePager.md`](./SkillOpt_Executive_OnePager.md) for:
- Deep Learning analogy
- Complete algorithm pseudocode
- Results & validation
- Implementation checklist
- Best practices & common pitfalls
- Hyperparameter guidance
- Key insights & conclusions

### Interactive Tutorial

See [`SkillOpt_Tutorial.ipynb`](./SkillOpt_Tutorial.ipynb) for:
- Setup instructions
- Core concepts walkthrough
- Basic math problem example
- Real LLM integration templates
- Results visualization
- Next steps guidance

---

## 🔑 Key Insights

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

---

## 📊 Comparison to Other Approaches

| Approach | SkillOpt Advantage |
|----------|-------------------|
| **No skill** | +23.5 points average on GPT-5.5 |
| **Human-written skill** | Learns from rollout feedback, not intuition |
| **One-shot LLM skill** | Iterative improvement vs. single generation |
| **TextGrad/GEPA** | Optimizes persistent skill artifact, not just prompts |
| **Trace2Skill** | Validation gate prevents overfitting to training trajectories |
| **EvoSkill** | Bounded updates + rejected-edit buffer = stability |
| **Fine-tuning** | No weight updates; works on closed models; reusable across models |

---

## 🧪 Testing

```bash
# Run unit tests (if available)
pytest tests/

# Run implementation example
python skillopt_implementation.py

# Expected output: Optimized skill document with improved validation score
```

---

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

- [ ] Skill libraries with shared infrastructure
- [ ] Reward-free validation for open-ended tasks
- [ ] Self-distillation: optimize skill → fine-tune model with skill
- [ ] Curriculum learning across benchmarks
- [ ] Additional domain examples (legal, medical, code generation)
- [ ] Distributed optimization for massive skill libraries

---

## 📝 Citation

If you use this implementation or find it helpful, please cite the original paper:

```bibtex
@article{yang2026skillopt,
  title={SkillOpt: Executive Strategy for Self-Evolving Agent Skills},
  author={Yang, Yifan and others},
  journal={arXiv preprint arXiv:2605.23904},
  year={2026}
}
```

---

## 📄 License

This implementation is released under the MIT License. See `LICENSE` file for details.

The original SkillOpt paper and methodology are © 2026 Microsoft, Shanghai Jiao Tong University, Tongji University, Fudan University.

---

## 🔗 Resources

- **Paper**: [arXiv:2605.23904v2](https://arxiv.org/abs/2605.23904)
- **One-Pager**: [`SkillOpt_Executive_OnePager.md`](./SkillOpt_Executive_OnePager.md)
- **Implementation**: [`skillopt_implementation.py`](./skillopt_implementation.py)
- **Tutorial**: [`SkillOpt_Tutorial.ipynb`](./SkillOpt_Tutorial.ipynb)
- **Repository**: [ai-research-paper-applications](https://github.com/rodolfolermacontreras/ai-research-paper-applications)

---

## 💡 Support

For questions, issues, or discussions:
- Open an issue on GitHub
- Check the tutorial notebook for common questions
- Review the one-pager for implementation details

---

**Built with ❤️ for the AI research community**

*SkillOpt proves that compact natural-language skills can serve as a practical domain-adaptation layer for frontier agents, enabling reusable improvement without modifying model weights.*
