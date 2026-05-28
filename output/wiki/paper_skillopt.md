# SkillOpt: Executive Strategy for Self-Evolving Agent Skills

Source directory: `2605_23904v2_skillopt_self_evolving_agent_skills`

See also: [Index](index.md), [Concepts](concepts.md), [Practical applications](practical_applications.md), [Cross references](cross_references.md), [Glossary](glossary.md)

## Why this paper matters for engineers

This paper treats an agent skill like an external, versionable optimization state. The target model stays frozen while a separate optimizer model proposes controlled skill edits and keeps only the ones that improve held-out performance.

## Core problem

Teams often adapt agents with prompt tweaks or handwritten skills, but these updates are hard to reproduce, easy to regress, and usually not disciplined like a training loop.

## Core idea

Turn skill editing into text-space optimization. Use rollout batches, reflection minibatches, bounded add/delete/replace edits, learning-rate-like edit budgets, a validation gate, and a rejected-edit buffer to stabilize improvement.

## Key contributions

- Introduces SkillOpt, a controllable optimizer for natural-language agent skills.
- Separates the target model from the optimizer model so the learned skill can be reused without extra deployment-time calls.
- Uses bounded edit budgets, validation-gated acceptance, and rejected-edit memory to reduce regressions.
- Shows broad gains across six benchmarks, seven target models, and direct chat, Codex, and Claude Code execution harnesses.
- Shows transfer across models, harnesses, and nearby benchmarks, which makes the learned skill artifact operationally useful.

## Practical applications

### Build a reusable skill training loop for coding agents

Wrap your current agent with a separate optimizer that proposes add, delete, and replace patches to a skill markdown file and accepts them only after a held-out benchmark improves.

### Create domain skills for office, spreadsheet, or support workflows

The paper shows the pattern works across QA, spreadsheets, documents, math, and embodied tasks, so it is suitable for enterprise copilots that need consistent procedures.

### Version and audit agent behavior as text artifacts

Because the deployed output is a compact skill file, engineering teams can code-review, diff, test, and roll back agent behavior changes like any other configuration artifact.

### Transfer tuned skills across model sizes or harnesses

Optimize once on a stronger setup, then try the same skill on smaller models or a different execution harness to reduce repeated tuning cost.

## Implementation hints

- Store the current skill, best validated skill, and rejected edits as separate files so the workflow is inspectable.
- Use structured patch operations instead of full rewrites for most steps; it reduces destructive regressions.
- Keep a stable train, selection, and test split for the tasks used to tune the skill.
- Measure both direct-chat and tool-use harness performance if the agent is expected to operate in multiple environments.

## Notable results or claims

- Reports best-or-tied-best performance on all 52 evaluated model, benchmark, and harness cells.
- On GPT-5.5, reports average gains of +23.5 in direct chat, +24.8 in Codex, and +19.1 in Claude Code over a no-skill baseline.
- Shows a Codex-trained spreadsheet skill transferring to Claude Code with a +59.7 point gain.

## Methods and sections to inspect

- Introduction and why prompts or handwritten skills are not enough
- Problem setup with train, selection, and test splits
- Rollout evidence and reflection minibatches
- Bounded text updates with edit budgets and schedules
- Validation gate plus rejected-edit buffer
- Epoch-wise slow or meta updates
- Cross-model, cross-harness, and cross-benchmark transfer results

## References and related work

- [1] Shunyu Yao, Jeffrey Zhao, Dian Yu, Nan Du, Izhak Shafran, Karthik Narasimhan, and Yuan Cao. React: Synergizing reasoning and acting in language models. arXiv preprint arXiv:2210.03629, 2022.
- [2] Timo Schick, Jane Dwivedi-Yu, Roberto Dessì, Roberta Raileanu, Maria Lomeli, Eric Hambro, Luke Zettlemoyer, Nicola Cancedda, and Thomas Scialom. Toolformer: Language models can teach themselves to use tools. Advances in neural information processing systems, 36: 68539–68551, 2023.
- [3] Guanzhi Wang, Yuqi Xie, Yunfan Jiang, Ajay Mandlekar, Chaowei Xiao, Yuke Zhu, Linxi Fan, and Anima Anandkumar. Voyager: An open-ended embodied agent with large language models. arXiv preprint arXiv:2305.16291, 2023.
- [4] John Yang, Carlos E Jimenez, Alexander Wettig, Kilian Lieret, Shunyu Yao, Karthik Narasimhan, and Ofir Press. Swe-agent: Agent-computer interfaces enable automated software engineering. Advances in Neural Information Processing Systems, 37:50528–50652,
- 2024.

## Related wiki pages

- [Concepts](concepts.md) for shared terminology used in skillopt paper.
- [Practical applications](practical_applications.md) for implementation-oriented next steps based on skillopt paper.
- [Cross references](cross_references.md) to compare skillopt paper with the other imported papers.
