# SkillOpt: Executive Strategy for Self-Evolving Agent Skills

## Title and Authors
**Title:** SkillOpt: Executive Strategy for Self-Evolving Agent Skills

**Authors:** Yifan Yang, Ziyang Gong, Weiquan Huang, Qihao Yang, Ziwei Zhou, Zisu Huang, Yan Li, Xuemei Gao, Qi Dai, Bei Liu, Kai Qiu, Yuqing Yang, Dongdong Chen, Xue Yang, Chong Luo

**Affiliations:** Microsoft, Shanghai Jiao Tong University, Tongji University, Fudan University

**Date:** May 2026 (arXiv:2605.23904v2)

**Code:** https://aka.ms/SkillOpt

---

## 1. Problem Statement and Motivation

Frontier language-model agents are routinely shipped behind closed APIs: their weights are frozen, fine-tuning is unavailable or expensive, and the only knobs the integrator gets to turn are the prompt, the tool surface, and a small bag of procedural instructions usually written into a `SKILL.md`, system message, or developer note. In practice, almost every gain on a real-world agent task -- spreadsheet automation, document QA, math reasoning, code execution, embodied control -- comes from carefully refining that procedural artifact: where to look for evidence, how to phrase the final answer, when to call which tool, how to recover from a verifier complaint.

The paper observes that today this refinement looks nothing like training. People either hand-write skills, ask an LLM to draft one in a single shot, or let the agent revise its own skill through loose self-reflection. All three regimes share the same failure mode: **skill drift**. Without a learning rate, without a held-out validation gate, and without memory of what previously failed, each edit can quietly erase rules that were doing real work, replace them with plausible-sounding but worse ones, and leave the team with no auditable record of what changed or why. The result is a stochastic, hard-to-improve, hard-to-rollback adaptation layer that sits between the model and the user.

SkillOpt's central reframing is to treat the skill document itself as the trainable object -- the external state of a frozen agent -- and to apply the same discipline that makes weight-space optimization reproducible: batched evidence, bounded steps, validation-gated acceptance, memory of rejected steps, and a slow consolidation pass. The deployed output is still a compact `best_skill.md` of roughly 300--2,000 tokens, which means zero added inference cost; everything expensive lives in the offline training loop.

Why text-space evolution matters in particular: the same conditions that make weight-space training inaccessible (closed APIs, vendor-managed models, cost) make text-space optimization unusually attractive, because the skill artifact is small, portable, code-reviewable, version-controllable, and transferable across model variants and execution harnesses. The paper's empirical claim is that this is not a hack: with the right controls, training a skill behaves enough like training weights to recover most of the benefit of fine-tuning, while remaining a plain text file you can diff in a pull request.

---

## 2. Method Walkthrough

SkillOpt has four moving pieces:

1. **Frozen target model `M`** -- the agent being adapted. It may run as direct chat or inside a tool-using harness such as Codex or Claude Code. Its weights are never touched.
2. **Current skill document `s_t`** -- the trainable external state, injected into the agent context as instructions or persistent procedural memory.
3. **Frontier optimizer model** -- a separate, typically stronger, model that reads scored rollouts and proposes structured edits. It is offline-only; it never runs at deployment.
4. **Validation/selection machinery** -- a fixed held-out split `D_sel` that decides whether a candidate skill survives.

Training data is partitioned into `D_tr`, `D_sel`, `D_test` once and never re-mixed. `D_tr` produces evidence, `D_sel` gates acceptance, and `D_test` is locked until the final report. This three-way split is what gives SkillOpt its training-like property: every accepted update has crossed a gate the optimizer has never seen.

### 2.1 The forward pass: rollout evidence
At each step `t`, the frozen target model runs a rollout batch from `D_tr` using the current skill `s_t`. The harness records everything procedurally relevant: task metadata, messages, tool calls, observations, command outputs, final answers, verifier feedback, and benchmark-specific context such as spreadsheet previews, document references, or compact execution traces. Each trajectory $\tau(s)$ produces a scalar score $r(s) \in [0, 1]$, following

$$
(\tau(s), r(s)) = h(M, x, s).
$$

Batch size acts like a noise control: small batches update quickly but noisily, large batches expose more recurring procedural failures before the skill changes. The implementation also supports *accumulation* -- several rollout batches reflected on separately and then merged -- which decouples execution throughput from update frequency.

### 2.2 The backward pass: minibatch reflection
The optimizer model separates failures from successes and partitions each group into reflection minibatches. This split matters because single trajectories produce anecdotal fixes ("add this one example"), while minibatches expose reusable procedural errors ("the agent consistently searches the wrong source", "the agent never verifies a numeric answer before writing it"). Failure minibatches propose missing or corrective rules; success minibatches preserve behaviors that already work.

Local edit proposals are merged hierarchically: failure-driven edits are consolidated first, success-driven edits second, and the two pools are then combined with priority on failure corrections. This step deduplicates contradictory or instance-specific suggestions before any budget is applied.

### 2.3 Bounded text updates -- the textual learning rate
The textual learning rate is the **edit budget `L_t`**: the maximum number of skill edits applied at step `t`. After aggregation, the optimizer ranks the merged edit pool by expected utility and clips it to the top `L_t` edits. SkillOpt supports constant, linear, cosine, and "autonomous" (model-chosen) schedules; the default cosine schedule starts with larger edits and decays toward smaller consolidation steps, mirroring standard cosine decay in weight-space training.

Two modes coexist: **patch mode** applies localized operations (`append`, `insert`, `replace`, `delete`) directly to the skill text; **rewrite mode** uses the ranked suggestions as conditioning for a bounded full rewrite. Critically, step-level edits cannot overwrite the *slow-update field* (a protected section of the skill), so fast local edits and slow consolidation never collide.

### 2.4 The validation gate and rejected-edit buffer
Every candidate skill `s_{t+1}` is scored on `D_sel` with the same frozen model and harness. The acceptance rule is **strict**: a candidate is accepted only if it improves on `D_sel`; if it also exceeds the best score so far, it becomes `best_skill.md`. Ties are rejected. This converts reflection into propose-and-test optimization rather than unconditional self-editing, which the paper argues is essential because plausible textual diagnoses can still hurt the actual target model.

Rejected updates are not discarded. The optimizer keeps an epoch-local **rejected-edit buffer**: each rejected edit is stored together with the score drop it caused and the failure pattern it tried to address. Later reflection calls in the same epoch receive this buffer, so the optimizer can avoid repeating bad ideas and concentrate on still-unresolved failures. This is the analogue of negative gradients without an actual gradient.

### 2.5 Epoch-wise slow / meta update
At the end of every epoch, SkillOpt runs the *same* training items under the previous epoch's skill and the current epoch's skill, partitions the results into improvements, regressions, persistent failures, and stable successes, and asks the optimizer to write a concise longitudinal guidance block into a protected slow-update field of the skill. That candidate still has to pass the validation gate. Slow update therefore captures durable cross-epoch lessons -- the equivalent of a momentum term -- without bloating step-level edits.

The **meta-skill** is optimizer-side only: it tracks which edit patterns helped, which were rejected, and which failures persisted across epochs, and is prepended to future optimizer prompts. The deployed skill stays compact and portable; the training-side memory is allowed to be richer.

### 2.6 Harness-agnostic deployment
A lightweight adapter interface lets the same loop drive direct chat, Codex, Claude Code, or any other agent harness. The adapter is the only thing that changes; the optimization loop, gate, buffer, and slow update are shared. This is the operational payoff of treating skills as the adaptation layer: optimize once with a strong optimizer, then deploy the resulting `best_skill.md` across model scales and harnesses without changing weights.

---

## 3. Algorithms in Pseudocode

The paper's notation: `s_t` is the skill at step `t`, `L_t` is the edit budget at step `t`, `D_tr / D_sel / D_test` are the data splits, `h(M, x, s)` is one harness rollout producing `(tau, r)`. Scores are mean rewards on a split.

### Algorithm 1 -- SkillOpt training loop

```text
Inputs: frozen target model M, initial skill s_0, splits D_tr, D_sel, D_test,
        edit-budget schedule {L_t}, number of epochs E
State:  current skill s = s_0, best skill s* = s_0
        rejected-edit buffer B = {}, meta-skill mu = {}

for epoch e = 1..E:
    B = {}                                           # epoch-local
    for step t in epoch e:
        # Forward pass: rollout evidence
        batch X ~ sample(D_tr)
        traces = [h(M, x, s) for x in X]
        F, S = split_by_score(traces)                # failures, successes

        # Backward pass: minibatch reflection
        edits_F = reflect(F, mode="failure", meta=mu, rejected=B)
        edits_S = reflect(S, mode="success", meta=mu, rejected=B)

        # Hierarchical merge: failures take priority
        edits = merge(edits_F, edits_S)

        # Bounded textual update: rank and clip to L_t
        edits = rank_and_clip(edits, L_t)
        s_cand = apply_edits(s, edits)               # respects protected fields

        # Validation gate
        score_cur = mean(r for (_, r) in [h(M, x, s)      for x in D_sel])
        score_new = mean(r for (_, r) in [h(M, x, s_cand) for x in D_sel])
        if score_new > score_cur:                    # strict improvement
            s = s_cand
            if score_new > score(s*, D_sel):
                s* = s_cand                          # best_skill.md
        else:
            B = B union {(edits, score_new - score_cur)}
            update_meta(mu, edits, outcome="rejected")

    # Epoch-wise slow/meta update
    deltas = compare_same_tasks(s_prev_epoch, s, D_tr)
    s_slow = write_slow_field(s, deltas, meta=mu)
    if score(s_slow, D_sel) > score(s, D_sel):
        s = s_slow

return s*                                            # deployed skill
```

### Algorithm 2 -- Bounded patch application

```text
Input: skill text s, ranked edits e_1..e_L (each an ADD / DEL / REP operation)
for i = 1..L:
    if e_i targets the protected slow-update field:
        continue                                     # step edits cannot overwrite slow field
    s = apply_op(s, e_i)
return s
```

### Algorithm 3 -- Selection across candidates

The paper formalizes selection as

$$
s^\star_{sel} = \arg\max_{s \in C(D_{tr})} \tfrac{1}{|D_{sel}|} \sum_{x \in D_{sel}} r(s),
\qquad
\text{Test}(s^\star_{sel}) = \tfrac{1}{|D_{test}|} \sum_{x \in D_{test}} r(s^\star_{sel}).
$$

`C(D_tr)` is the set of skills produced during training; `D_test` is touched only for the final number.

Default hyper-parameters reported in the paper: 4 epochs, rollout batch size 40, reflection minibatch size 8, cosine schedule for `L_t`, slow update enabled, rejected-edit buffer enabled. (See appendix sections C.1--C.4 in the extracted text at `output/extracted/text/2605_23904v2_skillopt_self_evolving_agent_skills/sections_clean.json`.)

---

## 4. Experimental Setup, Benchmarks, and Results

### 4.1 Setting
SkillOpt is evaluated on six benchmarks covering five task families:

- **SearchQA** -- open-domain question answering with web evidence.
- **SpreadsheetBench** -- executable spreadsheet manipulation.
- **OfficeQA** -- document/office workflow QA.
- **DocVQA** -- multimodal document QA.
- **LiveMathematicianBench** -- adversarial math reasoning (abbreviated *LiveMath*).
- **ALFWorld** -- embodied decision making in a text-based household environment.

Seven target models are tested, spanning frontier scale to small open models: GPT-5.5, GPT-5.4, GPT-5.4-mini, GPT-5.4-nano, GPT-5.2, and two Qwen variants. Three execution harnesses are tested per model: direct chat, Codex, Claude Code. Baselines: **no skill**, **human-written skill**, **one-shot LLM-written skill**, **Trace2Skill**, **TextGrad**, **GEPA**, and **EvoSkill**.

### 4.2 Main results
Across the full grid of 52 (model, benchmark, harness) cells, SkillOpt is **best or tied-best on all 52**. The headline direct-chat numbers on GPT-5.5 are (no skill -> SkillOpt):

| Benchmark        | No skill | SkillOpt | Delta |
|------------------|---------:|---------:|------:|
| SearchQA         | 77.7     | 87.3     | +9.6  |
| SpreadsheetBench | 41.8     | 80.7     | +38.9 |
| OfficeQA         | 33.1     | 72.1     | +39.0 |
| DocVQA           | 78.8     | 91.2     | +12.4 |
| LiveMath         | 37.6     | 66.9     | +29.3 |
| ALFWorld         | 83.6     | 95.5     | +11.9 |
| **Average**      | --       | --       | **+23.5** |

These deltas come from the per-row tables saved under `output/extracted/tables/2605_23904v2_skillopt_self_evolving_agent_skills/` (page 7, tables 01--09, one per model in the main grid). On GPT-5.5 direct chat, SkillOpt beats the best per-cell baseline (drawn across human/LLM/Trace2Skill/TextGrad/GEPA/EvoSkill) by **+5.4 average points**.

### 4.3 Harness results
On GPT-5.5 inside agentic execution loops, the gains hold:

- **Codex harness:** +24.8 average over no skill; +14.0 average over EvoSkill.
- **Claude Code harness:** +19.1 average over no skill; +3.2 average over EvoSkill.

This matters because it rules out the "just better prompt wording for chat" hypothesis: the same optimizer is improving reusable procedure that survives a tool-using execution loop.

### 4.4 Transfer
Three transfer regimes are studied:

- **Cross-model.** A SpreadsheetBench skill trained on GPT-5.4 improves GPT-5.4-mini and GPT-5.4-nano without re-training.
- **Cross-harness.** A spreadsheet skill trained inside Codex transfers to Claude Code with **+59.7 points** over the Claude Code baseline; the reverse direction is also strongly positive.
- **Cross-benchmark.** A skill trained on OlympiadBench yields positive gains on Omni-MATH for three different target models.

No transfer row dips below the corresponding no-skill baseline. This is the headline operational claim: optimize once, audit as text, redeploy.

### 4.5 Ablations
Component ablations isolate where the gains come from. The biggest contributors are:

- **Bounded textual learning rate.** Removing the edit budget and letting the optimizer freely rewrite the skill produces noisier, less monotonic improvement and occasional regressions.
- **Validation gate.** Without the strict `D_sel` improvement check, plausible-sounding edits accumulate and the skill drifts.
- **Rejected-edit buffer.** Without the buffer, the optimizer re-proposes the same failed edits and wastes budget.
- **Slow / meta update.** Removing both meta-skill and slow update causes a large drop on SpreadsheetBench, which the paper attributes to long-horizon consolidation being essential when procedural rules interact in subtle ways.

Batch and minibatch sizes matter less than having *enough* evidence and keeping updates *controlled*.

### 4.6 Compactness and cost
Learned skills remain small: typically **300--2,000 tokens** after only **1--4 accepted edits per epoch**. The deployed skill therefore adds essentially no inference-time overhead; all of the cost lives in the offline optimizer-model calls during training.

---

## 5. Failure Modes and Limitations

The paper is forthright about scope. The honest limitations are:

1. **Requires a reliable scalar score.** SkillOpt's gate depends on $r(s) \in [0,1]$. Benchmarks with exact-match metrics, executable verifiers, or graders fit naturally; open-ended generation does not without a proxy reward.
2. **Training is expensive.** Even though deployment is free, training spends real money on optimizer-model calls, rollout batches, and validation passes per accepted edit. The paper does not pretend this is free.
3. **One skill, not a library.** SkillOpt optimizes a single compact skill per domain. It does not address how to grow, index, or retrieve from a large multi-skill library.
4. **Distribution-bound heuristics.** Optimized skills may encode shortcuts that match the training-task distribution. Transfer empirically generalizes but is not guaranteed.
5. **Local optima.** Bounded edits keep the skill close to where it has been; if the right policy is far from the initial skill, the schedule needs to start more aggressively, and the cosine default may need tuning.
6. **Optimizer-induced bias.** The optimizer is itself an LLM; biases in *what it considers a good rule* will leak into the trained skill in ways that are harder to audit than gradient updates.

Future-work hooks called out by the authors: skill libraries across multiple domains, reusable optimizer-side meta-skills, preference-based or reward-free gates for open-ended tasks, and eventual distillation of optimized skills back into model weights.

---

## 6. Why a Practitioner Should Care -- Five Concrete Takeaways

1. **Treat `SKILL.md` as a first-class artifact.** Promote it from "the prompt we forgot about" to a versioned, code-reviewed file with its own change-history, its own validation gate, and its own promotion process. This alone removes most skill-drift bugs even before any optimization loop is built.

2. **Separate the *runtime* model from the *optimizer* model.** The deployed agent should never have to do its own skill editing. Use the strongest available model offline to propose edits; deploy only the resulting text. This is operationally cheaper, more auditable, and easier to roll back than self-editing agents.

3. **Add a validation gate before *any* skill edit reaches production.** Even without the rest of SkillOpt, a strict "candidate skill must beat current skill on held-out tasks" rule is the highest-leverage change. It directly prevents the most common production failure: plausible diagnoses that make things worse.

4. **Keep a rejected-edit log.** It is cheap to maintain and prevents the optimizer (human or model) from re-proposing fixes that already failed. This is the practitioner analogue of the rejected-edit buffer and pays for itself within a few iterations.

5. **Make skills portable on purpose.** Constrain edits to be small, procedural, and harness-agnostic. The paper's transfer results suggest that skills with this shape carry across model scales, across harnesses (Codex <-> Claude Code), and to nearby tasks. That is what makes a skill a reusable asset rather than a one-shot prompt.

---

## 7. Pointers to Extracted Assets

- Cleaned section index: `output/extracted/text/2605_23904v2_skillopt_self_evolving_agent_skills/sections_clean.json`
- Raw sections (with noise): `output/extracted/text/2605_23904v2_skillopt_self_evolving_agent_skills/sections.json`
- Main results tables: `output/extracted/tables/2605_23904v2_skillopt_self_evolving_agent_skills/` (page 7, tables 01--09 cover the per-model main grid).
- Rendered figures (vector-PDF pages rasterized as PNG): `output/extracted/images/2605_23904v2_skillopt_self_evolving_agent_skills/`. Page 2 is the optimization-analogy figure; page 4 is the pipeline diagram; pages 7 and 12 contain results figures.
- Extracted pseudo-code blocks (including the appendix prompt contracts `analyst_error.md`, `analyst_success.md`, `merge_failure.md`, `merge_success.md`, `merge_final.md`, `ranking.md`, `slow_update.md`, `meta_skill.md`): `output/extracted/text/2605_23904v2_skillopt_self_evolving_agent_skills/code_blocks.json`
- Practical reimplementation: `output/code_applications/skill_evolution_framework/` (bounded edits + validation gate over composable skill chains) and `output/code_applications/agent_skill_registry/` (discovery, composition, leaderboard).

---

## 8. Bottom Line

SkillOpt's most defensible contribution is not the headline 52/52 result; it is the *operational stance* that an agent's procedural instructions are a trainable artifact and deserve training discipline. Bounded edits, strict validation, rejected-edit memory, and a slow consolidation pass are individually small ideas, but together they convert skill editing from prompt tinkering into something that behaves like an optimizer. For teams that cannot fine-tune frontier models -- which is almost everyone -- that conversion is the actionable contribution.
