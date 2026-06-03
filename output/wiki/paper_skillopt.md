# SkillOpt: Executive Strategy for Self-Evolving Agent Skills

Source directory: `2605_23904v2_skillopt_self_evolving_agent_skills`

See also: [Index](index.md), [Concepts](concepts.md), [Practical applications](practical_applications.md), [Cross references](cross_references.md), [Glossary](glossary.md)

Companion deep summary: [output/summaries/2605_23904v2_skillopt_self_evolving_agent_skills.md](../summaries/2605_23904v2_skillopt_self_evolving_agent_skills.md)

---

## If you remember nothing else

1. **Skills are external state, not prompts.** SkillOpt treats `best_skill.md` as the trainable object for a frozen agent and applies the discipline of weight-space training (batches, learning rate, validation gate, momentum) to text edits.
2. **The validation gate is the load-bearing piece.** A candidate skill is accepted only if it *strictly* improves a held-out selection score. Without this, plausible textual edits accumulate as silent regressions.
3. **Edits are bounded, not free-form rewrites.** The textual learning rate is `L_t`, the max number of add/delete/replace edits per step. Cosine decay over epochs is the default. This is what stops skill drift.
4. **Optimizer is separate from runtime.** A stronger model proposes edits offline; the deployed agent only ever sees the final text. Deployment adds **zero** inference-time calls.
5. **Optimized skills travel.** Across 52 (model, benchmark, harness) cells SkillOpt is best or tied-best on every one; skills transfer across model scales, across Codex / Claude Code harnesses, and to nearby benchmarks without re-training.

---

## Why this paper matters for engineers

If you ship an agent against a closed frontier API, you cannot fine-tune the model and you usually cannot meaningfully change the harness. The only knob you control is the procedural skill artifact wedged between the user task and the model. SkillOpt is the first paper that treats that artifact as a *trainable* object with a real optimization protocol -- batched evidence, bounded edits, held-out gating, rejected-edit memory, slow consolidation -- instead of as a prompt to tweak. The deployed deliverable is still a plain markdown file you can code-review and roll back.

## Core problem

Today's three skill-update regimes -- handwritten, one-shot LLM-generated, or self-revising -- all share the same failure: skill drift. There is no learning rate, no validation gate, and no memory of failed edits, so plausible-sounding revisions silently regress production behavior and leave no auditable trail.

## Core idea

Reframe skill editing as text-space optimization. A separate optimizer model converts scored rollouts into structured `ADD` / `DEL` / `REP` edits; a textual learning rate `L_t` clips the edit pool; a strict held-out validation gate decides what survives; a rejected-edit buffer prevents the optimizer from repeating bad ideas; an epoch-wise slow/meta update carries longer-horizon lessons across epochs.

---

## Concept map

These are the concepts the paper introduces or relies on. The orchestrator will wire the cross-references in `concepts.md`, `cross_references.md`, and `glossary.md`.

### Concepts introduced by this paper
- **Bounded skill edit** -- localized `ADD`/`DEL`/`REP` operation against a skill document, capped per step by `L_t`.
- **Textual learning rate (`L_t`)** -- max number of edits per step; supports constant / linear / cosine / autonomous schedules.
- **Validation gate** -- strict acceptance rule: candidate skill must improve the score on `D_sel`.
- **Rejected-edit buffer** -- epoch-local memory of failed edits and their score drops; the negative-feedback channel.
- **Slow / meta update** -- epoch-end consolidation pass into a protected slow-update field; the momentum analogue.
- **Executive strategy** -- the management layer that decides *which* edits to apply and *which* skill chain to deploy.
- **Skill manifest / `best_skill.md`** -- the deployed text artifact; the trained output.
- **Patch mode vs rewrite mode** -- localized edit operations vs bounded full-skill rewrite under the same edit budget.
- **Harness-agnostic deployment** -- the adapter pattern that lets the same optimizer drive direct chat, Codex, and Claude Code.

### Concepts SkillOpt connects to in the broader literature
- **Prompt-as-optimizable-text** -- TextGrad, GEPA, ABSTRAL, EvoTest. SkillOpt differs by optimizing a persistent skill artifact rather than the prompt itself.
- **Trajectory reflection** -- Reflexion, Self-Refine, Trace2Skill. SkillOpt adds validation gating and bounded updates on top of reflection.
- **Skill libraries and procedural memory** -- Voyager, SkillsBench, EvoSkill, AutoSkill. SkillOpt narrows the scope to *one* compact skill with strong controls instead of growing a multi-skill repository.
- **Agent harnesses** -- ReAct, Toolformer, SWE-agent, Codex, Claude Code. SkillOpt's harness-agnostic adapter is what lets it work across all of them.
- **Meta-learning analogy** -- not gradient-based meta-learning, but the training discipline (rollout batches as evidence, edit budget as learning rate, gate as validation, slow update as momentum) is borrowed wholesale.

### Concepts to cross-reference with the generalization paper
- **Validation as the load-bearing safeguard.** SkillOpt's held-out gate plays the role of the validation set in classical supervised learning. The generalization paper's emphasis on signal-vs-noise decomposition is the theoretical complement: SkillOpt's gate is the operational mechanism that prevents the noise channel from dominating skill updates.
- **Bounded steps prevent overfitting to a batch.** Just as small gradient steps and learning-rate decay prevent overfitting to a single batch, bounded textual edits with cosine decay prevent over-fitting to a single rollout's anecdotal failures.
- **Cross-model transfer.** SkillOpt's cross-model transfer (skill trained on GPT-5.4 helps GPT-5.4-mini and GPT-5.4-nano) is a text-space echo of the weight-space generalization story.

---

## Glossary candidates

Terms below are specific to this paper or use the paper's particular meaning. Suggested for promotion into `glossary.md`.

| Term | Definition |
|---|---|
| `best_skill.md` | The deployed skill artifact; the validation-gated best skill at end of training. Typically 300--2,000 tokens. |
| Bounded edit | One `ADD`, `DEL`, or `REP` operation against the skill document; counted toward the per-step edit budget `L_t`. |
| Edit budget `L_t` | Maximum number of bounded edits applied at step `t`. The textual analogue of a learning rate. |
| Executive strategy | The control layer that ranks and clips edits, runs the validation gate, and decides which skill chain to deploy. |
| Frozen target model `M` | The agent being adapted. Its weights never change. SkillOpt only changes the skill `s_t`. |
| Harness `h` | The execution environment (direct chat, Codex, Claude Code). One rollout: $(\tau, r) = h(M, x, s)$. |
| Meta-skill `mu` | Optimizer-side memory across epochs of which edit patterns helped, failed, or persisted. Not shipped at deployment. |
| Patch mode | Edits are localized `append` / `insert` / `replace` / `delete` operations on the skill text. |
| Rejected-edit buffer `B` | Epoch-local set of edits that were tried, failed the validation gate, and the score drop they caused. Negative feedback for later optimizer calls. |
| Rewrite mode | The ranked edit pool conditions a bounded full-skill rewrite instead of being applied as patches. |
| Rollout batch | A sample from `D_tr` executed by `M` with the current skill `s_t`; the evidence unit for one optimization step. |
| Skill `s` | A natural-language policy prepended to the agent context. The trainable external state in SkillOpt. |
| Slow / meta update | Epoch-end consolidation written into a protected slow-update field by comparing the same training items under previous- and current-epoch skills. |
| Slow-update field | A protected section of the skill that step-level edits cannot overwrite. Reserved for cross-epoch consolidation. |
| Validation gate | Strict-improvement acceptance rule on `D_sel`. Ties are rejected. |
| `D_tr` / `D_sel` / `D_test` | Train, selection, and test splits. `D_sel` gates acceptance; `D_test` is locked until the final report. |

---

## Practical applications

### Build a disciplined skill-training loop for your existing agent
Wrap your agent with a separate optimizer that proposes structured `ADD`/`DEL`/`REP` edits to your `SKILL.md` and accepts them only after a held-out benchmark improves. Even without slow update or rejected-edit memory, just the validation gate removes the most common production failure: plausible diagnoses that make things worse.

### Version and audit agent behavior as text
Because the deliverable is a compact text file, engineering teams can diff, code-review, test, and roll back agent behavior changes the same way they manage configuration. Combined with the rejected-edit log, you get a real change-history of *why* the skill is what it is.

### Optimize once, redeploy across models and harnesses
The transfer results say it directly: train a skill on the strongest model you have, then run the same skill against smaller and cheaper variants and across different agent harnesses. Validate empirically per cell, but expect positive carryover.

### Build domain skills for high-impact verifiable workflows
SkillOpt's gate needs a scalar score, so it lands best on tasks with verifiers or exact-match metrics: spreadsheet automation, document QA, code execution, math reasoning, embodied control. These are exactly the workflows enterprise copilots are being deployed against.

### Separate runtime from training
Run the optimizer offline against a stronger model than the one you deploy. The deployed agent never edits its own skill, never makes extra calls, and remains as cheap to serve as a stock model. This is the operational separation of concerns that makes SkillOpt deployable.

---

## Implementation hints

- Store **current skill**, **best validated skill**, and **rejected-edit buffer** as three separate files so the workflow is inspectable.
- Default to **patch mode** with cosine `L_t` decay. Reserve rewrite mode for early epochs or after major distribution shifts.
- Keep `D_tr` / `D_sel` / `D_test` splits stable across the whole training run. The gate is only meaningful if `D_sel` is locked.
- Reflect failures and successes **separately** before merging; do not let one giant minibatch decide everything.
- Protect the slow-update field from step-level edits in your patch applier, otherwise fast and slow updates collide.
- Measure both direct-chat and tool-use harness scores if the agent will run in multiple environments. SkillOpt transfers well, but verify per cell.

---

## Notable results or claims

- Best or tied-best on all **52** evaluated (model, benchmark, harness) cells.
- GPT-5.5 average gains over no skill: **+23.5** direct chat, **+24.8** Codex, **+19.1** Claude Code.
- GPT-5.5 direct chat: beats the strongest per-cell competitor (across human / LLM / Trace2Skill / TextGrad / GEPA / EvoSkill) by **+5.4** average.
- Codex-trained spreadsheet skill transfers to Claude Code with a **+59.7** point gain.
- Learned skills stay compact: **300--2,000 tokens**, **1--4 accepted edits per epoch**.

Source tables (per-model main grid, page 7): `output/extracted/tables/2605_23904v2_skillopt_self_evolving_agent_skills/2605_23904v2_skillopt_self_evolving_agent_skills_page_007_table_01.md` through `_table_09.md`.

---

## Methods and sections to inspect

- Section 3.1 Problem Setup -- the `D_tr` / `D_sel` / `D_test` split and the formal selection objective.
- Section 3.4 Bounded Text Updates -- the textual learning rate and edit-budget schedules.
- Section 3.5 Validation Gate and Rejected-Edit Buffer -- the load-bearing safeguard.
- Section 3.6 Epoch-Wise Slow/Meta Update -- the momentum analogue.
- Section 3.7 Harness-Agnostic Deployment -- why the same loop works in direct chat, Codex, and Claude Code.
- Section 4.1--4.3 Main results and harness results.
- Section 4.4 Transfer findings.
- Section 4.5 Ablations.
- Appendix C.2.1--C.2.8 Optimizer prompt contracts (`analyst_error.md`, `analyst_success.md`, `merge_failure.md`, `merge_success.md`, `merge_final.md`, `ranking.md`, `slow_update.md`, `meta_skill.md`).

Cleaned section index: `output/extracted/text/2605_23904v2_skillopt_self_evolving_agent_skills/sections_clean.json`.

---

## Companion code applications

- [output/code_applications/skill_evolution_framework/](../code_applications/skill_evolution_framework/) -- minimal SkillOpt loop with bounded chain edits, executive strategy, and validation-gated acceptance over composable text skills.
- [output/code_applications/agent_skill_registry/](../code_applications/agent_skill_registry/) -- skill registry with discovery, composition, evaluation, and a leaderboard view.

---

## References and related work (selected)

- [1] Yao et al. *ReAct: Synergizing Reasoning and Acting in Language Models.* arXiv:2210.03629, 2022.
- [2] Schick et al. *Toolformer: Language Models Can Teach Themselves to Use Tools.* NeurIPS 36, 2023.
- [3] Wang et al. *Voyager: An Open-Ended Embodied Agent with Large Language Models.* arXiv:2305.16291, 2023.
- [4] Yang et al. *SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering.* NeurIPS 37, 2024.
- [13] *GEPA* -- trajectory-feedback reflective prompt evolution; one of SkillOpt's strongest baselines.
- *TextGrad* -- prompt-optimization baseline; uses text-space gradients but lacks SkillOpt's validation gate and slow update.
- *Trace2Skill*, *EvoSkill* -- skill-evolution baselines that SkillOpt outperforms across all evaluated cells.

Full bibliography (56 references) at `output/extracted/text/2605_23904v2_skillopt_self_evolving_agent_skills/references.json`.

---

## Related wiki pages

- [Concepts](concepts.md) for shared terminology across the library.
- [Practical applications](practical_applications.md) for implementation-oriented next steps.
- [Cross references](cross_references.md) for how SkillOpt connects to the generalization paper (validation-as-safeguard, bounded-step-as-anti-overfitting, transfer-across-scale).
