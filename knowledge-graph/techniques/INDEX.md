# ⚡ Techniques Catalog

**Implementation techniques extracted from research papers**

Techniques are specific, concrete implementation methods, algorithms, or code patterns that you can directly apply in your projects.

---

## Quick Navigation

- **[📚 All Papers](../INDEX.md)** — Back to papers index
- **[🧠 Concepts Map](../concepts/INDEX.md)** — Core concepts
- **[🔧 Patterns Library](../patterns/INDEX.md)** — Architectural patterns
- **[← Back to Home](../../README.md)**

---

## Training Techniques

### Cosine Learning Rate Schedule
**What:** Smoothly decay edit budget over training using cosine annealing.

**Implementation:**
```python
import math

def cosine_edit_budget(
    iteration: int,
    max_iterations: int,
    initial_budget: float = 0.2,
    min_budget: float = 0.05
) -> float:
    """
    Cosine decay schedule for edit budgets.
    
    Args:
        iteration: Current training iteration (0-indexed)
        max_iterations: Total number of iterations
        initial_budget: Starting edit budget (e.g., 0.2 = 20% of text)
        min_budget: Minimum edit budget (floor)
    
    Returns:
        Edit budget for current iteration
    """
    progress = iteration / max_iterations
    cosine_decay = 0.5 * (1 + math.cos(math.pi * progress))
    return min_budget + (initial_budget - min_budget) * cosine_decay

# Example: 100 iterations, 20% -> 5%
for i in range(100):
    budget = cosine_edit_budget(i, 100, 0.2, 0.05)
    print(f"Iter {i}: {budget:.2%} edit budget")
```

**When to Use:**
- Text-space optimization (SkillOpt, prompt optimization)
- Any iterative refinement process
- Want smooth, predictable decay
- Need aggressive early exploration, gentle late refinement

**Papers Using This:**
- **[SkillOpt](../../Papers/agent-systems/SkillOpt/)** — Edit budget scheduling

**Related Concepts:**
- [Text-Space Optimization](../concepts/text-space-optimization.md)

**Related Patterns:**
- [Bounded Edit Budget](../patterns/bounded-edit-budget.md)

**Full Code:**
See [SkillOpt Implementation](../../Papers/agent-systems/SkillOpt/skillopt_implementation.py) — `SkillOptimizer` class

---

### Minibatch Reflection
**What:** Reflect on small batches of successes/failures separately, then aggregate insights.

**Implementation:**
```python
from typing import List, Dict

def minibatch_reflection(
    examples: List[Dict],
    batch_size: int = 5,
    llm_reflect: callable = None
) -> List[str]:
    """
    Generate reflections on minibatches of successes/failures.
    
    Args:
        examples: List of dicts with 'input', 'output', 'success' keys
        batch_size: Size of each minibatch
        llm_reflect: Function that takes batch and returns reflection string
    
    Returns:
        List of reflection strings (one per batch)
    """
    successes = [ex for ex in examples if ex['success']]
    failures  = [ex for ex in examples if not ex['success']]
    
    reflections = []
    
    # Reflect on successful batches
    for i in range(0, len(successes), batch_size):
        batch = successes[i:i+batch_size]
        if batch:
            reflection = llm_reflect(batch, focus="What worked well?")
            reflections.append(reflection)
    
    # Reflect on failure batches
    for i in range(0, len(failures), batch_size):
        batch = failures[i:i+batch_size]
        if batch:
            reflection = llm_reflect(batch, focus="What went wrong?")
            reflections.append(reflection)
    
    return reflections

# Example usage
def mock_llm_reflect(batch, focus):
    return f"Analyzed {len(batch)} examples, focused on: {focus}"

examples = [
    {'input': 'q1', 'output': 'a1', 'success': True},
    {'input': 'q2', 'output': 'a2', 'success': False},
    # ... more examples
]

reflections = minibatch_reflection(examples, batch_size=5, llm_reflect=mock_llm_reflect)
```

**When to Use:**
- Large training sets (100+ examples)
- Need focused, specific feedback
- Want to identify patterns in success/failure
- LLM context length is limited

**Papers Using This:**
- **[SkillOpt](../../Papers/agent-systems/SkillOpt/)** — Batch size 5-10

**Related Concepts:**
- [Rollout-Reflect-Edit Loop](../concepts/rollout-reflect-edit.md)

**Related Patterns:**
- [Minibatch Reflection](../patterns/INDEX.md#minibatch-reflection) (pattern view)

---

### Slow Update + Meta Skill
**What:** Maintain epoch-level meta-information (rejected edits, insights) updated less frequently than the main skill.

**Implementation:**
```python
from dataclasses import dataclass, field
from typing import List

@dataclass
class MetaSkill:
    """Long-term memory for skill optimization."""
    rejected_edits: List[str] = field(default_factory=list)
    rejection_reasons: List[str] = field(default_factory=list)
    discovered_patterns: List[str] = field(default_factory=list)
    epoch_insights: List[str] = field(default_factory=list)
    
    def add_rejection(self, edit: str, reason: str):
        """Store a rejected edit with reason."""
        self.rejected_edits.append(edit)
        self.rejection_reasons.append(reason)
    
    def add_pattern(self, pattern: str):
        """Store a discovered pattern."""
        self.discovered_patterns.append(pattern)
    
    def add_epoch_insight(self, insight: str):
        """Store end-of-epoch insight."""
        self.epoch_insights.append(insight)
    
    def get_context(self, max_recent: int = 10) -> str:
        """Get meta skill context for optimizer."""
        context = "Meta Skill Memory:\n\n"
        
        if self.rejected_edits:
            context += "Recent Rejected Edits:\n"
            for edit, reason in zip(
                self.rejected_edits[-max_recent:],
                self.rejection_reasons[-max_recent:]
            ):
                context += f"  - Rejected: {edit}\n    Reason: {reason}\n"
        
        if self.discovered_patterns:
            context += "\nDiscovered Patterns:\n"
            for pattern in self.discovered_patterns[-max_recent:]:
                context += f"  - {pattern}\n"
        
        return context

# Example usage
meta_skill = MetaSkill()

# During training
meta_skill.add_rejection(
    edit="Add more examples to prompt",
    reason="Validation performance dropped by 5%"
)

meta_skill.add_pattern(
    "Shorter prompts work better for simple tasks"
)

# Feed to optimizer
optimizer_context = meta_skill.get_context()
```

**When to Use:**
- Iterative optimization over many steps
- Want to avoid repeating mistakes
- Need long-term memory beyond current state
- Benefit from historical context

**Papers Using This:**
- **[SkillOpt](../../Papers/agent-systems/SkillOpt/)** — Slow-update mode

**Related Concepts:**
- [Rollout-Reflect-Edit Loop](../concepts/rollout-reflect-edit.md)

**Related Patterns:**
- [Slow Update + Meta Skill](../patterns/INDEX.md#slow-update--meta-skill)
- [Rejected-Edit Buffer](../patterns/rejected-edit-buffer.md)

---

## Evaluation Techniques

### Validation Gating
**What:** Accept edits only if they improve validation set performance.

**Implementation:**
```python
from typing import Callable, List, Dict

def validate_edit(
    skill_current: str,
    skill_proposed: str,
    validation_set: List[Dict],
    eval_fn: Callable[[str, Dict], bool]
) -> tuple[bool, float, float]:
    """
    Gate edit based on validation performance.
    
    Args:
        skill_current: Current skill text
        skill_proposed: Proposed edited skill
        validation_set: List of validation examples
        eval_fn: Function(skill, example) -> success (bool)
    
    Returns:
        (accept: bool, current_score: float, proposed_score: float)
    """
    # Evaluate current skill
    current_successes = sum(
        eval_fn(skill_current, ex) for ex in validation_set
    )
    current_score = current_successes / len(validation_set)
    
    # Evaluate proposed skill
    proposed_successes = sum(
        eval_fn(skill_proposed, ex) for ex in validation_set
    )
    proposed_score = proposed_successes / len(validation_set)
    
    # Accept if improvement
    accept = proposed_score > current_score
    
    return accept, current_score, proposed_score

# Example usage
def mock_eval(skill, example):
    # Placeholder: execute skill on example
    return len(skill) > 50  # Dummy logic

validation_data = [{'input': f'q{i}'} for i in range(10)]

accept, curr_score, prop_score = validate_edit(
    skill_current="Current skill prompt...",
    skill_proposed="Improved skill prompt...",
    validation_set=validation_data,
    eval_fn=mock_eval
)

print(f"Accept: {accept} (Current: {curr_score:.2%}, Proposed: {prop_score:.2%})")
```

**When to Use:**
- Any optimization process with separate validation data
- Want strong generalization guarantees
- Need objective decision rule
- Prevent overfitting

**Papers Using This:**
- **[SkillOpt](../../Papers/agent-systems/SkillOpt/)** — Core quality control

**Related Concepts:**
- [Validation Gating](../concepts/validation-gating.md)

**Related Patterns:**
- [Held-Out Validation Gating](../patterns/INDEX.md#held-out-validation-gating)

---

## Prompt Engineering Techniques

### Few-Shot Skill Construction
**What:** Build initial skills from few-shot examples.

**Implementation:**
```python
def build_initial_skill(
    task_description: str,
    few_shot_examples: List[Dict[str, str]],
    output_format: str = "structured"
) -> str:
    """
    Construct initial skill from task description and examples.
    
    Args:
        task_description: What the skill should do
        few_shot_examples: List of input-output pairs
        output_format: Expected output format
    
    Returns:
        Initial skill text
    """
    skill = f"# Task: {task_description}\n\n"
    skill += "## Instructions\n"
    skill += "Follow these examples:\n\n"
    
    for i, ex in enumerate(few_shot_examples, 1):
        skill += f"Example {i}:\n"
        skill += f"Input: {ex['input']}\n"
        skill += f"Output: {ex['output']}\n\n"
    
    skill += f"## Output Format\n{output_format}\n\n"
    skill += "## Execution\nNow apply this pattern to the given input.\n"
    
    return skill

# Example
initial_skill = build_initial_skill(
    task_description="Extract named entities from text",
    few_shot_examples=[
        {'input': 'Apple announced new iPhone.', 'output': 'ORG: Apple, PRODUCT: iPhone'},
        {'input': 'Tim Cook visited Paris.', 'output': 'PERSON: Tim Cook, LOC: Paris'},
    ],
    output_format="List of entity type: entity name pairs"
)

print(initial_skill)
```

**When to Use:**
- Bootstrapping new skills from scratch
- Have good examples but no pre-trained skills
- Want interpretable, human-readable skills
- Starting point for optimization

**Papers Using This:**
- **[SkillOpt](../../Papers/agent-systems/SkillOpt/)** — Initial skill construction

---

## Data Handling Techniques

### Train-Val-Test Split for Text Tasks
**What:** Split dataset ensuring diversity across splits, not just random sampling.

**Implementation:**
```python
import random
from typing import List, Dict, Tuple
from collections import defaultdict

def stratified_split(
    data: List[Dict],
    train_ratio: float = 0.6,
    val_ratio: float = 0.2,
    test_ratio: float = 0.2,
    stratify_key: str = None
) -> Tuple[List[Dict], List[Dict], List[Dict]]:
    """
    Split data into train/val/test with optional stratification.
    
    Args:
        data: List of examples (dicts)
        train_ratio: Fraction for training
        val_ratio: Fraction for validation
        test_ratio: Fraction for test
        stratify_key: Optional key to stratify on (e.g., 'category')
    
    Returns:
        (train, val, test) tuple of lists
    """
    assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 1e-6
    
    if stratify_key:
        # Group by stratify key
        groups = defaultdict(list)
        for item in data:
            groups[item[stratify_key]].append(item)
        
        train, val, test = [], [], []
        for group_data in groups.values():
            random.shuffle(group_data)
            n = len(group_data)
            train_end = int(n * train_ratio)
            val_end = train_end + int(n * val_ratio)
            
            train.extend(group_data[:train_end])
            val.extend(group_data[train_end:val_end])
            test.extend(group_data[val_end:])
    else:
        # Simple random split
        random.shuffle(data)
        n = len(data)
        train_end = int(n * train_ratio)
        val_end = train_end + int(n * val_ratio)
        
        train = data[:train_end]
        val = data[train_end:val_end]
        test = data[val_end:]
    
    return train, val, test

# Example
dataset = [
    {'text': 'example 1', 'category': 'A'},
    {'text': 'example 2', 'category': 'B'},
    # ... more data
]

train, val, test = stratified_split(
    dataset,
    train_ratio=0.6,
    val_ratio=0.2,
    test_ratio=0.2,
    stratify_key='category'
)
```

**When to Use:**
- Any supervised learning task
- Need fair evaluation
- Want to ensure generalization
- Multiple categories or types in dataset

**Papers Using This:**
- **[SkillOpt](../../Papers/agent-systems/SkillOpt/)** — 60/20/20 split

---

## Emerging Techniques

*(Add techniques as you discover them)*

### Reinforcement Learning from Human Feedback (RLHF)
**Status:** 🔴 Not yet documented
**Waiting for:** RLHF or alignment paper

### Mixture of Experts (MoE) for Skills
**Status:** 🔴 Not yet documented
**Waiting for:** Multi-skill or routing paper

### Constrained Decoding
**Status:** 🔴 Not yet documented
**Waiting for:** Structured generation paper

---

## Technique Relationships

```
Training Techniques
├── Cosine LR Schedule → Controls edit budget
├── Minibatch Reflection → Generates insights
└── Slow Update + Meta Skill → Provides memory

Evaluation Techniques
└── Validation Gating → Quality control

Prompt Engineering
└── Few-Shot Skill Construction → Bootstrapping

Data Handling
└── Train-Val-Test Split → Dataset preparation
```

---

## How to Use This Catalog

### For Practitioners
1. Browse by category (Training, Evaluation, Prompting, Data)
2. Copy code snippets into your project
3. Adapt to your specific use case
4. Reference papers for deeper understanding

### For Researchers
1. Document new techniques you discover
2. Provide clean, reusable code
3. Cross-link to papers and concepts
4. Note when to use each technique

---

## Contributing

### Adding a New Technique
1. Create `technique-name.md` using the template (see `templates/technique_template.md`)
2. Add entry to this INDEX.md under appropriate category
3. Include working code example
4. Cross-link to related papers and patterns

---

**Total Techniques:** 6  
**Last Updated:** 2026-06-03
