# Glossary

Short definitions for technical terms that appear in the current wiki pages.

See also: [Concepts](concepts.md)

## Adam

A popular adaptive optimizer. The generalization paper proposes an SNR-style extension on top of Adam.

## Agent skill

A reusable natural-language document that tells an agent how to act in a domain or tool environment.

## Benign overfitting

A regime where a model fits the training data, including some noise, yet still generalizes well.

## Claude Code harness

A tool-using execution environment where the model can act through files, commands, and iterative steps.

## Codex harness

A coding-agent execution loop used in the SkillOpt experiments to evaluate skill transfer across environments.

## Cumulative dissipation

The integrated training effect used in the generalization paper to define the signal channel and reservoir.

## Deep learning generalization

Why high-capacity neural networks still perform well on unseen data.

## Direct chat

A plain prompting setup without the richer tool-use loop of a coding harness.

## Double descent

A modern generalization pattern where error first drops, then rises, then drops again as model capacity increases.

## Feature learning

A training regime where the effective representation changes substantially during optimization.

## Generalization bound

A theoretical statement that limits the gap between training and test performance.

## Grokking

Late generalization after a long period of near-memorization during training.

## Held-out gate

A validation check that must be passed before a skill update is accepted.

## Implicit bias

The tendency of an optimizer to prefer certain solutions even without explicit regularization.

## NTK

Short for neural tangent kernel.

## Population risk

Expected loss over the true data distribution, not only the training sample.

## Rejected-edit buffer

A store of rejected skill changes and the regressions they caused.

## Reservoir

The part of output space where training can hide residual error without affecting test predictions in the paper's framework.

## SNR preconditioner

A signal-to-noise-ratio based modifier that prefers updates with stronger estimated population signal.

## Self-evolving skill

A skill document that is updated from execution feedback through an automated optimization loop.

## Signal channel

The part of output space where training updates transfer into test-time behavior.

## Text-space optimization

Optimization where the state being updated is a text artifact rather than model weights.

## Train-test coupling

A relation between movement on training outputs and movement on test outputs along the realized trajectory.

## Validation split

A held-out subset used to decide whether an update should be kept.
