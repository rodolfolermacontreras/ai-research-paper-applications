# SkillOpt: Executive Strategy for Self-Evolving Agent Skills

## Title and Authors
**Title:** SkillOpt: Executive Strategy for Self-Evolving Agent Skills

**Authors:** Yifan Yang, Ziyang Gong, Weiquan Huang, Qihao Yang, Ziwei Zhou, Zisu Huang, Yan Li, Xuemei Gao, Qi Dai, Bei Liu, Kai Qiu, Yuqing Yang, Dongdong Chen, Xue Yang, Chong Luo

**Affiliations:** Microsoft, Shanghai Jiao Tong University, Tongji University, Fudan University

**Date:** May 2026

## Abstract
Agent skills are often written by hand, generated once, or updated through loosely controlled self-revision. The paper argues that this is too unstable and too hard to improve systematically. Instead, the authors treat the skill itself as a trainable external state for a frozen agent. SkillOpt is their proposed text-space optimizer for agent skills: a separate optimizer model reads scored execution traces, proposes bounded add/delete/replace edits to one skill document, and accepts an edit only if it improves a held-out validation score. Stability comes from several training-style controls: a textual learning-rate budget, a rejected-edit buffer, and an epoch-wise slow/meta update. Across six benchmarks, seven target models, and three execution settings (direct chat, Codex, Claude Code), SkillOpt is best or tied-best on all 52 evaluated model/benchmark/harness cells. On GPT-5.5, it improves average no-skill accuracy by +23.5 points in direct chat, +24.8 in Codex, and +19.1 in Claude Code. The learned skill artifacts also transfer across model scales, across agent harnesses, and to a nearby math benchmark without further optimization.

## Key Contributions
- Reframes agent-skill learning as optimization over an external natural-language artifact rather than model weights.
- Introduces **SkillOpt**, a controllable skill optimizer with rollout batches, reflection minibatches, bounded edits, validation gating, rejected-edit memory, and slow/meta updates.
- Shows strong empirical performance across six benchmarks, seven target models, and three execution environments.
- Demonstrates that optimized skills are portable artifacts that can transfer across models, harnesses, and nearby tasks.
- Provides evidence that compact textual skills can act as a practical domain-adaptation layer for frozen frontier agents.

## Core Concepts Explained
### What is SkillOpt?
SkillOpt is an offline training loop for agent skills. The target agent model stays frozen. Instead of tuning weights or only rewriting a prompt, SkillOpt repeatedly edits a persistent skill document such as `best_skill.md`. That document contains procedural guidance: how to inspect evidence, how to use tools, how to format answers, what common failure modes to avoid, and what verification habits to follow.

The central idea is simple: if the thing that changes agent behavior in practice is often the procedural instructions around the model, then that instruction artifact should itself be optimized like a trainable object.

### How does skill evolution work?
Skill evolution in this paper is not free-form self-editing. It follows a controlled loop:
1. Run the frozen agent on tasks using the current skill.
2. Collect trajectories, scores, tool calls, outputs, and failures.
3. Use a separate optimizer model to analyze common patterns across multiple successes and failures.
4. Convert those patterns into a small set of structured edits.
5. Apply only a limited number of edits.
6. Keep the new skill only if it beats the previous one on a held-out validation split.

That makes skill learning look more like optimization and less like prompt tinkering.

### What is the “executive strategy”?
The paper’s “executive strategy” is essentially a management layer over skill revision. Instead of letting the model rewrite instructions however it wants, SkillOpt constrains the update process through explicit controls:
- bounded edit budgets,
- minibatch reflection over multiple traces,
- held-out validation before accepting changes,
- memory of rejected edits,
- slower cross-epoch consolidation separate from fast local edits.

In practical terms, this means the system behaves like a disciplined editor or training supervisor for agent instructions.

## System Architecture
SkillOpt has four main parts:

1. **Frozen target model**  
   This is the agent being improved. It may run as direct chat or inside a tool-using harness like Codex or Claude Code. Its weights never change.

2. **Current skill document**  
   This is the trainable external policy. It is injected into the agent context as instructions or persistent procedural memory.

3. **Optimizer model**  
   A separate frontier model reads rollout evidence and proposes edits. It acts like a teacher or optimizer, not the deployed runtime agent.

4. **Validation and selection machinery**  
   Candidate skills are evaluated on a held-out selection split. Only skills that strictly improve the validation score are accepted.

The interaction pattern is:
- agent executes tasks with current skill,
- harness records trajectories and scores,
- optimizer reflects over failures and successes,
- merged edits are ranked and clipped to a budget,
- candidate skill is validated,
- accepted skill becomes current and possibly best skill.

A slower epoch-level mechanism compares previous and current epoch skills on the same examples, then writes long-horizon guidance into a protected slow-update section. An optimizer-side meta-skill stores lessons about which edit patterns helped or hurt, but this meta-memory is not shipped at deployment.

## Methodology
The method follows a train/selection/test protocol.

- **Train split:** used to generate rollout evidence and candidate edits.
- **Selection split:** used as the acceptance gate for skill updates.
- **Test split:** used only for final reporting.

The main training loop works like this:

```text
initialize current skill = initial skill
for each epoch:
  run rollout batches on training tasks
  split trajectories into failures and successes
  reflect over minibatches to propose edits
  merge and deduplicate edits
  rank edits and keep only top L_t
  apply edits to get candidate skill
  evaluate candidate on held-out selection split
  if candidate strictly improves score:
    accept candidate
  else:
    store rejected edits as negative feedback
  optionally perform slow/meta update at epoch end
return best validation-gated skill
```

Important methodological choices:
- **Failure and success are analyzed separately.** Failures suggest missing or corrective rules; successes preserve good behaviors.
- **Edits are patch-like.** Operations include append, insert, replace, and delete.
- **Learning rate becomes edit budget.** Instead of gradient step size, SkillOpt uses `L_t`, the maximum number of edits allowed at a step.
- **Continuity matters.** Small bounded revisions preserve optimization history and reduce destructive rewriting.
- **Strict gating prevents silent regression.** Ties are rejected; only strictly better candidate skills survive.

Default settings reported in the paper include four epochs, rollout batch size 40, reflection minibatch size 8, cosine decay for the edit budget, slow update enabled, and a rejected-edit buffer.

## Key Results and Findings
The headline result is unusually strong for a no-weight-update method.

### Main benchmark results
Across 52 evaluated model/benchmark/harness cells, SkillOpt is best or tied-best on all 52.

For **GPT-5.5 direct chat**, SkillOpt improves:
- SearchQA: **77.7 -> 87.3**
- SpreadsheetBench: **41.8 -> 80.7**
- OfficeQA: **33.1 -> 72.1**
- DocVQA: **78.8 -> 91.2**
- LiveMathematicianBench: **37.6 -> 66.9**
- ALFWorld: **83.6 -> 95.5**

That is an average **+23.5 point** gain over no skill.

It also beats the strongest per-cell baseline from human-written skills, one-shot LLM skills, Trace2Skill, TextGrad, GEPA, and EvoSkill by **+5.4 points on average** for GPT-5.5 direct chat.

### Harness results
SkillOpt also works inside agentic execution loops, not just plain prompting.

For **GPT-5.5 in Codex**:
- average gain over no skill: **+24.8**
- average gain over EvoSkill: **+14.0**

For **GPT-5.5 in Claude Code**:
- average gain over no skill: **+19.1**
- average gain over EvoSkill: **+3.2**

This matters because it suggests the method is improving reusable procedure, not just prompt wording for one interface.

### Transfer findings
Transfer is one of the paper’s most useful engineering results.

- **Cross-model:** a SpreadsheetBench skill trained on GPT-5.4 improves GPT-5.4-mini and GPT-5.4-nano.
- **Cross-harness:** a spreadsheet skill trained in Codex transfers to Claude Code with **+59.7** points over the Claude Code baseline; the reverse transfer also stays strongly positive.
- **Cross-benchmark:** a skill trained on OlympiadBench improves Omni-MATH across three models, with smaller but consistently positive gains.

No transfer row falls below the target model’s no-skill baseline.

### Ablation findings
The gains depend most on the controls that make optimization stable:
- bounded textual learning rate,
- validation gate,
- rejected-edit buffer,
- slow/meta update.

Batch size and schedule matter less than having enough evidence and keeping updates controlled.

Removing both meta-skill and slow update causes a major drop on SpreadsheetBench, showing that long-horizon consolidation matters.

## Practical Applications
For engineers building AI agents, this paper suggests a very practical pattern:

- Treat the agent’s procedural instruction file as a versioned artifact that can be trained offline.
- Separate the **runtime model** from the **skill optimizer**. Use a stronger model for training if available, but deploy only the resulting skill text.
- Use task traces, verifier outputs, and tool logs as training evidence.
- Keep updates small and auditable rather than letting the optimizer rewrite everything.
- Validate every candidate skill on held-out tasks before shipping it.

This is especially applicable for:
- spreadsheet agents,
- coding agents,
- document QA systems,
- enterprise workflow agents,
- embodied or tool-using agents with repeatable tasks.

A concrete implementation pattern is to keep `SKILL.md` or `best_skill.md` as a first-class artifact in the repo, run periodic offline optimization jobs, and promote new skills only after automated evaluation passes.

## Limitations and Future Work
The paper is strong, but its scope is narrow.

### Limitations
- It relies on **scored trajectories** and a reliable validation signal, so it fits tasks with exact-match metrics, verifiers, or executable checks better than open-ended tasks.
- Training requires extra rollout cost and optimizer-model calls, even though deployment is cheap.
- It optimizes **one portable skill**, not a large multi-skill library.
- Optimized skills may encode heuristics tied to the training distribution, so transfer still needs evaluation.

### Future work proposed by the authors
- skill libraries across multiple domains,
- reuse of optimizer-side meta-skills across benchmarks,
- preference-based or reward-free validation gates for open-ended tasks,
- distilling optimized skills back into model weights.

## Key Algorithms
### 1. Rollout-and-reflect optimization loop
This is the main algorithm. Run tasks, collect evidence, summarize repeated failures and successes, propose edits, validate, and keep only winning updates.

### 2. Failure-prioritized patch merging
Failure minibatches and success minibatches each produce edits. These are merged hierarchically, with corrective edits from failures given priority. This helps the skill fix recurring problems without losing useful behaviors.

### 3. Bounded edit selection
The optimizer ranks proposed edits and clips them to the top `L_t` edits. This acts like a learning rate in text space: it limits how far the skill can move in one step.

### 4. Validation-gated acceptance
A candidate skill is accepted only when it strictly beats the current one on the selection split. This is the core safeguard against plausible but harmful revisions.

### 5. Rejected-edit memory
Rejected updates are not discarded. They are stored as negative feedback so future optimizer calls can avoid repeating bad ideas.

### 6. Epoch-wise slow/meta update
At the end of an epoch, the optimizer compares previous and current skill versions on the same tasks, then writes more durable guidance into a protected section. This acts like long-term consolidation or momentum.

## Connections to Other Work
SkillOpt sits at the intersection of several active lines of work.

### Agent frameworks and execution loops
The paper explicitly evaluates not just direct prompting but also Codex-style and Claude Code-style harnesses. That connects it to work like ReAct, Toolformer, SWE-agent, and other systems where agent performance depends heavily on procedure, tool policy, and verification habits.

### Skill learning and procedural memory
It builds on recent work framing skills as reusable procedural knowledge, including SkillsBench and surveys of agentic skills. It also relates to Trace2Skill, SkillForge, SkillFoundry, AutoSkill, SkillX, and other systems that derive reusable artifacts from experience. SkillOpt’s distinguishing choice is to optimize one compact skill with strong controls rather than grow a large skill repository.

### Prompt optimization and language-as-optimizer methods
The paper is closely related to TextGrad, GEPA, Reflexion, and Self-Refine. But it differs in two important ways:
- it focuses on a persistent skill artifact rather than just prompt wording,
- it adds validation-gated, bounded, auditable updates.

### Meta-learning analogy
The deep-learning analogy is central. The skill document is treated like a trainable state; rollout batches provide evidence; edit budget acts like a learning rate; the held-out gate acts like validation; slow/meta update acts like momentum or longer-horizon consolidation. It is not gradient-based meta-learning, but it borrows the training discipline of meta-learning and optimization.

## Engineering Takeaway
The most actionable idea in the paper is this: if you cannot or do not want to fine-tune model weights, you can still build a real adaptation pipeline by optimizing a structured skill artifact offline. The win is not just better scores. It is better operational discipline: versioned skills, auditable edits, stable promotion rules, low-cost deployment, and reusable improvements across models and agent runtimes.