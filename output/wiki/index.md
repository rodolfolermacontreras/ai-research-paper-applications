# AI Research Paper Wiki

This wiki turns extracted research paper artifacts into an engineer-facing knowledge base. It emphasizes what each paper contributes, how the ideas connect, and what a practitioner could build with them.

## Table of contents

- [Main index](index.md)
- [Concepts](concepts.md)
- [Practical applications](practical_applications.md)
- [Cross references](cross_references.md)
- [Glossary](glossary.md)
- [Generalization paper](paper_generalization.md)
- [SkillOpt paper](paper_skillopt.md)

## Papers in this wiki

## A Theory of Generalization in Deep Learning

- Page: [Generalization paper](paper_generalization.md)
- Summary: A theory paper that explains why deep networks can generalize in full feature-learning regimes and turns that theory into an optimizer-side signal for safer updates.
- Engineer view: This paper reframes generalization around training dynamics in output space. Instead of relying on classic worst-case bounds, it tracks where training can actually move predictions and shows how signal and memorization separate over time.
## SkillOpt: Executive Strategy for Self-Evolving Agent Skills

- Page: [SkillOpt paper](paper_skillopt.md)
- Summary: A systems paper about training an agent's skill document with bounded text edits, held-out validation, and optimizer-style controls instead of relying on one-shot prompting or uncontrolled self-revision.
- Engineer view: This paper treats an agent skill like an external, versionable optimization state. The target model stays frozen while a separate optimizer model proposes controlled skill edits and keeps only the ones that improve held-out performance.

## Cross-reference summary

- Both papers treat learning as an optimization problem with explicit control over what updates are allowed.
- The generalization paper focuses on how neural training separates transferable signal from noise; SkillOpt applies a similar discipline to text-based agent skills.
- Together they suggest a practical design rule: use structure, validation, and update constraints to improve systems without blindly trusting every training signal.
- Shared concepts detected across the imported papers: Optimization.
