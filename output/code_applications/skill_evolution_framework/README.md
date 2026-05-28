# Skill Evolution Framework

This application turns the paper *SkillOpt: Executive Strategy for Self-Evolving Agent Skills* into a compact local framework for selecting, composing, and improving text-processing skills.

## What it does

- defines a reusable skill library for normalization, keyword extraction, summarization, and sentiment analysis
- adds an executive strategy that chooses skill chains by task type
- runs a bounded optimization loop that proposes better chains and only accepts them when validation improves
- demonstrates the framework on summary, keyword, and sentiment tasks

## Paper concepts implemented

- skill library with composable skills
- executive strategy for deciding which skills to apply
- bounded edits to skill compositions instead of unrestricted rewrites
- validation gate that keeps only improvements

## Files

- `skills.py` - skill definitions and the default skill library
- `executive.py` - task model and composition strategy
- `skill_optimizer.py` - simplified evolution loop
- `demo.py` - runnable end-to-end demo

## How to run

From the repository root:

```powershell
.\.venv\Scripts\python.exe output\code_applications\skill_evolution_framework\demo.py
```

Artifacts are written to `output\code_applications\skill_evolution_framework\artifacts\`.
