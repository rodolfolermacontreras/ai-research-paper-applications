# Agent Skill Registry

This application provides a small skill registry for AI agents inspired by the skill management ideas in *SkillOpt: Executive Strategy for Self-Evolving Agent Skills*.

## What it does

- registers skills with names, descriptions, tags, and callables
- discovers skills by metadata
- composes multiple skills into a sequential pipeline
- evaluates skills on small benchmark sets
- tracks rolling score and latency metrics per skill

## Files

- `registry.py` - registry data model, discovery, composition, and metrics tracking
- `evaluator.py` - evaluation helpers and scoring rules
- `example_skills.py` - runnable demonstration

## How to run

From the repository root:

```powershell
.\.venv\Scripts\python.exe output\code_applications\agent_skill_registry\example_skills.py
```

Artifacts are written to `output\code_applications\agent_skill_registry\artifacts\`.
