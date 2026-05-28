# Key Concepts Across Papers

This page collects the main ideas that appear across the current paper set and explains why they matter for engineering work.

See also: [Index](index.md), [Cross references](cross_references.md), [Glossary](glossary.md)

## Neural tangent kernel

**Definition:** A kernel built from model Jacobians that describes how predictions move when parameters are updated. In the generalization paper it is the main object used to separate learnable signal from hard-to-transfer noise.

**Appears in:** [Generalization paper](paper_generalization.md)

**Practical relevance:** Useful when you want to reason about why a training setup generalizes, compare lazy-training behavior to feature learning, or build diagnostics around which directions in output space are actually trainable.

## Generalization

**Definition:** The ability of a model to perform well on unseen data instead of only fitting the training set.

**Appears in:** [Generalization paper](paper_generalization.md)

**Practical relevance:** This is the core question behind choosing architectures, optimizers, validation strategies, and regularization methods in production ML systems.

## Signal channel

**Definition:** The subspace of output directions where training dissipates loss and where information can transfer from training behavior to test behavior.

**Appears in:** [Generalization paper](paper_generalization.md)

**Practical relevance:** Think of it as the part of learning that carries real task structure. Diagnostics that approximate this idea can help engineers separate useful learning from memorization.

## Reservoir

**Definition:** The orthogonal subspace where residual error remains but does not transfer to test predictions in the paper's theory.

**Appears in:** [Generalization paper](paper_generalization.md)

**Practical relevance:** This is a practical lens for understanding benign overfitting, memorization, and why some fitted noise does not always hurt test performance.

## Drift-diffusion separation

**Definition:** The paper's argument that coherent signal accumulates as directional drift while minibatch noise behaves more like diffusion and grows much more slowly.

**Appears in:** [Generalization paper](paper_generalization.md)

**Practical relevance:** Helpful for thinking about batch size, noisy labels, optimizer design, and why SGD can still work in noisy settings.

## Train-test coupling

**Definition:** A result showing that, under the paper's conditions, test movement can be predicted from training movement even in feature-learning regimes.

**Appears in:** [Generalization paper](paper_generalization.md)

**Practical relevance:** Suggests ways to monitor training trajectories and estimate out-of-sample behavior without relying only on static complexity bounds.

## Population-risk objective

**Definition:** An objective derived from a single training run that estimates population-risk decrease directly from training-time quantities.

**Appears in:** [Generalization paper](paper_generalization.md)

**Practical relevance:** Promising for low-label-budget workflows where validation data is scarce and engineers still need a principled signal for update quality.

## SNR preconditioning

**Definition:** A practical optimizer modification that uses a signal-to-noise ratio style gate to emphasize updates that look population-safe.

**Appears in:** [Generalization paper](paper_generalization.md)

**Practical relevance:** Can inspire optimizer plugins or adaptive learning-rate rules for noisy preference learning, PINNs, or implicit neural representations.

## Agent skills

**Definition:** Portable natural-language artifacts that encode procedures, tool rules, output constraints, and domain heuristics for an AI agent.

**Appears in:** [SkillOpt paper](paper_skillopt.md)

**Practical relevance:** A clean interface for adapting an agent without retraining weights. Teams can version, review, and deploy skills like code or configuration.

## Self-evolution

**Definition:** Improving an agent's skill document through repeated execution feedback rather than only manual edits or one-shot prompting.

**Appears in:** [SkillOpt paper](paper_skillopt.md)

**Practical relevance:** Enables continuous improvement loops for coding agents, office automation agents, and domain-specific copilots.

## Text-space optimization

**Definition:** Treating a text artifact such as a skill document as the thing being optimized, with bounded edits, schedules, and validation gates.

**Appears in:** [SkillOpt paper](paper_skillopt.md)

**Practical relevance:** This gives engineering teams a safer way to iterate on prompts and skills than uncontrolled rewriting.

## Validation-gated updates

**Definition:** Accepting a proposed change only when it improves a held-out evaluation score.

**Appears in:** [SkillOpt paper](paper_skillopt.md)

**Practical relevance:** This is a practical guardrail for autonomous agent improvement loops because plausible edits often regress behavior.

## Rejected-edit buffer

**Definition:** A memory of failed skill edits that is fed back into later optimization rounds so the optimizer does not repeat the same bad move.

**Appears in:** [SkillOpt paper](paper_skillopt.md)

**Practical relevance:** Useful for any agent-tuning pipeline that needs negative feedback, auditability, and faster convergence.

## Slow/meta update

**Definition:** An epoch-level update that preserves longer-horizon lessons separately from fast local edits.

**Appears in:** [SkillOpt paper](paper_skillopt.md)

**Practical relevance:** Good pattern for keeping deployed skills compact while still letting the optimizer remember stable lessons over time.

## Harness-agnostic deployment

**Definition:** Designing skills so they work across direct chat and agentic tool-use environments such as Codex and Claude Code.

**Appears in:** [SkillOpt paper](paper_skillopt.md)

**Practical relevance:** Important when a team wants one reusable skill artifact across multiple execution environments.

## Optimization

**Definition:** The process of making repeated updates that improve an objective under constraints.

**Appears in:** [Generalization paper](paper_generalization.md), [SkillOpt paper](paper_skillopt.md)

**Practical relevance:** Both papers view learning as structured optimization: one in neural training dynamics, the other in editable agent-skill text.
