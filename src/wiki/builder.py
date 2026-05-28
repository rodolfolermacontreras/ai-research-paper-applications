from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
TEXT_DIR = REPO_ROOT / "output" / "extracted" / "text"
WIKI_DIR = REPO_ROOT / "output" / "wiki"


def _clean_text(value: str) -> str:
    value = value.replace("\x00", " ")
    value = value.replace("\r", "")
    value = re.sub(r"[ \t]+", " ", value)
    value = re.sub(r"\n{3,}", "\n\n", value)
    return value.strip()


def _read_text(path: Path) -> str:
    return _clean_text(path.read_text(encoding="utf-8", errors="ignore"))


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8", errors="ignore"))


def _first_non_empty(*values: str | None) -> str:
    for value in values:
        if value and value.strip():
            return value.strip()
    return ""


def _slugify(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_") or "paper"


def _sentence_case(value: str) -> str:
    value = value.strip()
    if not value:
        return value
    return value[0].upper() + value[1:]


@dataclass
class PaperProfile:
    paper_id: str
    title: str
    abstract: str
    full_text: str
    sections: list[dict[str, Any]]
    references: list[dict[str, Any]]
    short_name: str
    page_filename: str
    description: str
    engineer_summary: str
    core_problem: str
    core_idea: str
    key_contributions: list[str]
    concepts: list[str]
    methodologies: list[str]
    practical_applications: list[dict[str, str]]
    implementation_hints: list[str]
    notable_results: list[str]
    glossary_terms: list[str]
    sections_to_inspect: list[str]


CONCEPT_LIBRARY: dict[str, dict[str, str]] = {
    "Neural tangent kernel": {
        "definition": "A kernel built from model Jacobians that describes how predictions move when parameters are updated. In the generalization paper it is the main object used to separate learnable signal from hard-to-transfer noise.",
        "practical_relevance": "Useful when you want to reason about why a training setup generalizes, compare lazy-training behavior to feature learning, or build diagnostics around which directions in output space are actually trainable.",
    },
    "Generalization": {
        "definition": "The ability of a model to perform well on unseen data instead of only fitting the training set.",
        "practical_relevance": "This is the core question behind choosing architectures, optimizers, validation strategies, and regularization methods in production ML systems.",
    },
    "Signal channel": {
        "definition": "The subspace of output directions where training dissipates loss and where information can transfer from training behavior to test behavior.",
        "practical_relevance": "Think of it as the part of learning that carries real task structure. Diagnostics that approximate this idea can help engineers separate useful learning from memorization.",
    },
    "Reservoir": {
        "definition": "The orthogonal subspace where residual error remains but does not transfer to test predictions in the paper's theory.",
        "practical_relevance": "This is a practical lens for understanding benign overfitting, memorization, and why some fitted noise does not always hurt test performance.",
    },
    "Drift-diffusion separation": {
        "definition": "The paper's argument that coherent signal accumulates as directional drift while minibatch noise behaves more like diffusion and grows much more slowly.",
        "practical_relevance": "Helpful for thinking about batch size, noisy labels, optimizer design, and why SGD can still work in noisy settings.",
    },
    "Train-test coupling": {
        "definition": "A result showing that, under the paper's conditions, test movement can be predicted from training movement even in feature-learning regimes.",
        "practical_relevance": "Suggests ways to monitor training trajectories and estimate out-of-sample behavior without relying only on static complexity bounds.",
    },
    "Population-risk objective": {
        "definition": "An objective derived from a single training run that estimates population-risk decrease directly from training-time quantities.",
        "practical_relevance": "Promising for low-label-budget workflows where validation data is scarce and engineers still need a principled signal for update quality.",
    },
    "SNR preconditioning": {
        "definition": "A practical optimizer modification that uses a signal-to-noise ratio style gate to emphasize updates that look population-safe.",
        "practical_relevance": "Can inspire optimizer plugins or adaptive learning-rate rules for noisy preference learning, PINNs, or implicit neural representations.",
    },
    "Agent skills": {
        "definition": "Portable natural-language artifacts that encode procedures, tool rules, output constraints, and domain heuristics for an AI agent.",
        "practical_relevance": "A clean interface for adapting an agent without retraining weights. Teams can version, review, and deploy skills like code or configuration.",
    },
    "Self-evolution": {
        "definition": "Improving an agent's skill document through repeated execution feedback rather than only manual edits or one-shot prompting.",
        "practical_relevance": "Enables continuous improvement loops for coding agents, office automation agents, and domain-specific copilots.",
    },
    "Text-space optimization": {
        "definition": "Treating a text artifact such as a skill document as the thing being optimized, with bounded edits, schedules, and validation gates.",
        "practical_relevance": "This gives engineering teams a safer way to iterate on prompts and skills than uncontrolled rewriting.",
    },
    "Validation-gated updates": {
        "definition": "Accepting a proposed change only when it improves a held-out evaluation score.",
        "practical_relevance": "This is a practical guardrail for autonomous agent improvement loops because plausible edits often regress behavior.",
    },
    "Rejected-edit buffer": {
        "definition": "A memory of failed skill edits that is fed back into later optimization rounds so the optimizer does not repeat the same bad move.",
        "practical_relevance": "Useful for any agent-tuning pipeline that needs negative feedback, auditability, and faster convergence.",
    },
    "Slow/meta update": {
        "definition": "An epoch-level update that preserves longer-horizon lessons separately from fast local edits.",
        "practical_relevance": "Good pattern for keeping deployed skills compact while still letting the optimizer remember stable lessons over time.",
    },
    "Harness-agnostic deployment": {
        "definition": "Designing skills so they work across direct chat and agentic tool-use environments such as Codex and Claude Code.",
        "practical_relevance": "Important when a team wants one reusable skill artifact across multiple execution environments.",
    },
    "Optimization": {
        "definition": "The process of making repeated updates that improve an objective under constraints.",
        "practical_relevance": "Both papers view learning as structured optimization: one in neural training dynamics, the other in editable agent-skill text.",
    },
}


GLOSSARY_LIBRARY: dict[str, str] = {
    "Adam": "A popular adaptive optimizer. The generalization paper proposes an SNR-style extension on top of Adam.",
    "Agent skill": "A reusable natural-language document that tells an agent how to act in a domain or tool environment.",
    "Benign overfitting": "A regime where a model fits the training data, including some noise, yet still generalizes well.",
    "Claude Code harness": "A tool-using execution environment where the model can act through files, commands, and iterative steps.",
    "Codex harness": "A coding-agent execution loop used in the SkillOpt experiments to evaluate skill transfer across environments.",
    "Cumulative dissipation": "The integrated training effect used in the generalization paper to define the signal channel and reservoir.",
    "Deep learning generalization": "Why high-capacity neural networks still perform well on unseen data.",
    "Direct chat": "A plain prompting setup without the richer tool-use loop of a coding harness.",
    "Double descent": "A modern generalization pattern where error first drops, then rises, then drops again as model capacity increases.",
    "Drift-diffusion separation": "The idea that signal adds coherently while noise behaves like a slower random walk.",
    "Feature learning": "A training regime where the effective representation changes substantially during optimization.",
    "Generalization bound": "A theoretical statement that limits the gap between training and test performance.",
    "Grokking": "Late generalization after a long period of near-memorization during training.",
    "Held-out gate": "A validation check that must be passed before a skill update is accepted.",
    "Implicit bias": "The tendency of an optimizer to prefer certain solutions even without explicit regularization.",
    "NTK": "Short for neural tangent kernel.",
    "Population risk": "Expected loss over the true data distribution, not only the training sample.",
    "Rejected-edit buffer": "A store of rejected skill changes and the regressions they caused.",
    "Reservoir": "The part of output space where training can hide residual error without affecting test predictions in the paper's framework.",
    "Self-evolving skill": "A skill document that is updated from execution feedback through an automated optimization loop.",
    "Signal channel": "The part of output space where training updates transfer into test-time behavior.",
    "SNR preconditioner": "A signal-to-noise-ratio based modifier that prefers updates with stronger estimated population signal.",
    "Text-space optimization": "Optimization where the state being updated is a text artifact rather than model weights.",
    "Train-test coupling": "A relation between movement on training outputs and movement on test outputs along the realized trajectory.",
    "Validation split": "A held-out subset used to decide whether an update should be kept.",
}


PAPER_HINTS: list[tuple[str, dict[str, Any]]] = [
    (
        "a_theory_of_generalization_in_deep_learning",
        {
            "short_name": "Generalization paper",
            "page_filename": "paper_generalization.md",
            "description": "A theory paper that explains why deep networks can generalize in full feature-learning regimes and turns that theory into an optimizer-side signal for safer updates.",
            "engineer_summary": "This paper reframes generalization around training dynamics in output space. Instead of relying on classic worst-case bounds, it tracks where training can actually move predictions and shows how signal and memorization separate over time.",
            "core_problem": "Engineers know modern deep networks often generalize even when they are highly overparameterized, but standard capacity bounds are often too loose to explain what happens in practice.",
            "core_idea": "Use the empirical neural tangent kernel and its cumulative evolution to split learning into a signal channel and a reservoir. Signal transfers to test behavior, while some fitted noise remains trapped in directions that test points cannot see.",
            "key_contributions": [
                "Builds a non-asymptotic theory of generalization that still applies when the kernel changes by O(1) during feature learning.",
                "Defines the signal channel and reservoir using cumulative dissipation over the realized training path.",
                "Shows minibatch SGD separates coherent signal drift from slower noise diffusion.",
                "Proves train-test coupling under squared loss on the realized trajectory.",
                "Derives a population-risk objective and an SNR-style preconditioner that can be layered onto Adam with one extra state vector.",
            ],
            "concepts": [
                "Neural tangent kernel",
                "Generalization",
                "Signal channel",
                "Reservoir",
                "Drift-diffusion separation",
                "Train-test coupling",
                "Population-risk objective",
                "SNR preconditioning",
                "Optimization",
            ],
            "methodologies": [
                "Output-space analysis",
                "Kernel-based reasoning beyond the lazy regime",
                "Spectral decomposition of trainable directions",
                "SGD noise analysis",
                "Population-risk estimation from one run",
            ],
            "practical_applications": [
                {
                    "title": "Add an optimizer-side SNR gate to noisy training pipelines",
                    "details": "Use the paper's idea as an optimizer plugin for preference learning, noisy labels, or weak supervision. Keep an extra EMA-style state per parameter and promote updates whose estimated signal dominates minibatch variance.",
                },
                {
                    "title": "Build training diagnostics for memorization versus transferable learning",
                    "details": "Track whether updates look like signal-channel progress or reservoir-style memorization. This can help decide when to stop training, change batch size, or rebalance data.",
                },
                {
                    "title": "Improve PINNs and implicit neural representations under noisy supervision",
                    "details": "The paper explicitly reports better behavior on PINNs and implicit neural representations, so these are strong targets for experimentation.",
                },
                {
                    "title": "Estimate update quality when validation data is limited",
                    "details": "The population-risk objective suggests a way to score updates using training-time structure instead of relying only on a separate validation set.",
                },
            ],
            "implementation_hints": [
                "Start with an optimizer wrapper around Adam rather than modifying a trainer from scratch.",
                "Log gradient mean and variance statistics per parameter group to approximate signal-to-noise ratios.",
                "Compare standard Adam against the preconditioned variant on a noisy-label or DPO-style task before rolling it into a larger stack.",
                "Treat the signal channel idea as a diagnostic abstraction even if you cannot compute the full kernel exactly.",
            ],
            "notable_results": [
                "Explains grokking, implicit bias, benign overfitting, and double descent inside one signal-versus-reservoir framework.",
                "Claims the practical SNR preconditioner can accelerate grokking by 5x and keep DPO fine-tuning closer to the reference policy under noisy preferences.",
                "Argues generalization can still be characterized when the kernel drifts far beyond the lazy-training regime.",
            ],
            "glossary_terms": [
                "Adam",
                "Benign overfitting",
                "Cumulative dissipation",
                "Deep learning generalization",
                "Double descent",
                "Feature learning",
                "Generalization bound",
                "Grokking",
                "Implicit bias",
                "NTK",
                "Population risk",
                "Reservoir",
                "Signal channel",
                "SNR preconditioner",
                "Train-test coupling",
            ],
            "sections_to_inspect": [
                "Introduction and motivation for why classical bounds fail at modern scale",
                "Output-space dynamics, cumulative dissipation, and the signal-channel versus reservoir split",
                "Minibatch drift versus diffusion for separating coherent signal from label noise",
                "Train-test coupling in the feature-learning regime",
                "Population-risk training and the SNR-style optimizer update",
                "Connections to grokking, benign overfitting, implicit bias, and double descent",
            ],
        },
    ),
    (
        "skillopt_self_evolving_agent_skills",
        {
            "short_name": "SkillOpt paper",
            "page_filename": "paper_skillopt.md",
            "description": "A systems paper about training an agent's skill document with bounded text edits, held-out validation, and optimizer-style controls instead of relying on one-shot prompting or uncontrolled self-revision.",
            "engineer_summary": "This paper treats an agent skill like an external, versionable optimization state. The target model stays frozen while a separate optimizer model proposes controlled skill edits and keeps only the ones that improve held-out performance.",
            "core_problem": "Teams often adapt agents with prompt tweaks or handwritten skills, but these updates are hard to reproduce, easy to regress, and usually not disciplined like a training loop.",
            "core_idea": "Turn skill editing into text-space optimization. Use rollout batches, reflection minibatches, bounded add/delete/replace edits, learning-rate-like edit budgets, a validation gate, and a rejected-edit buffer to stabilize improvement.",
            "key_contributions": [
                "Introduces SkillOpt, a controllable optimizer for natural-language agent skills.",
                "Separates the target model from the optimizer model so the learned skill can be reused without extra deployment-time calls.",
                "Uses bounded edit budgets, validation-gated acceptance, and rejected-edit memory to reduce regressions.",
                "Shows broad gains across six benchmarks, seven target models, and direct chat, Codex, and Claude Code execution harnesses.",
                "Shows transfer across models, harnesses, and nearby benchmarks, which makes the learned skill artifact operationally useful.",
            ],
            "concepts": [
                "Agent skills",
                "Self-evolution",
                "Text-space optimization",
                "Validation-gated updates",
                "Rejected-edit buffer",
                "Slow/meta update",
                "Harness-agnostic deployment",
                "Optimization",
            ],
            "methodologies": [
                "Frozen-model adaptation through external text",
                "Trajectory-driven reflection",
                "Bounded edit schedules",
                "Held-out validation for autonomous updates",
                "Cross-model and cross-harness transfer evaluation",
            ],
            "practical_applications": [
                {
                    "title": "Build a reusable skill training loop for coding agents",
                    "details": "Wrap your current agent with a separate optimizer that proposes add, delete, and replace patches to a skill markdown file and accepts them only after a held-out benchmark improves.",
                },
                {
                    "title": "Create domain skills for office, spreadsheet, or support workflows",
                    "details": "The paper shows the pattern works across QA, spreadsheets, documents, math, and embodied tasks, so it is suitable for enterprise copilots that need consistent procedures.",
                },
                {
                    "title": "Version and audit agent behavior as text artifacts",
                    "details": "Because the deployed output is a compact skill file, engineering teams can code-review, diff, test, and roll back agent behavior changes like any other configuration artifact.",
                },
                {
                    "title": "Transfer tuned skills across model sizes or harnesses",
                    "details": "Optimize once on a stronger setup, then try the same skill on smaller models or a different execution harness to reduce repeated tuning cost.",
                },
            ],
            "implementation_hints": [
                "Store the current skill, best validated skill, and rejected edits as separate files so the workflow is inspectable.",
                "Use structured patch operations instead of full rewrites for most steps; it reduces destructive regressions.",
                "Keep a stable train, selection, and test split for the tasks used to tune the skill.",
                "Measure both direct-chat and tool-use harness performance if the agent is expected to operate in multiple environments.",
            ],
            "notable_results": [
                "Reports best-or-tied-best performance on all 52 evaluated model, benchmark, and harness cells.",
                "On GPT-5.5, reports average gains of +23.5 in direct chat, +24.8 in Codex, and +19.1 in Claude Code over a no-skill baseline.",
                "Shows a Codex-trained spreadsheet skill transferring to Claude Code with a +59.7 point gain.",
            ],
            "glossary_terms": [
                "Agent skill",
                "Claude Code harness",
                "Codex harness",
                "Direct chat",
                "Held-out gate",
                "Rejected-edit buffer",
                "Self-evolving skill",
                "Text-space optimization",
                "Validation split",
            ],
            "sections_to_inspect": [
                "Introduction and why prompts or handwritten skills are not enough",
                "Problem setup with train, selection, and test splits",
                "Rollout evidence and reflection minibatches",
                "Bounded text updates with edit budgets and schedules",
                "Validation gate plus rejected-edit buffer",
                "Epoch-wise slow or meta updates",
                "Cross-model, cross-harness, and cross-benchmark transfer results",
            ],
        },
    ),
]


def _build_profile(paper_dir: Path) -> PaperProfile:
    analysis = _load_json(paper_dir / "analysis.json")
    sections = _load_json(paper_dir / "sections.json") if (paper_dir / "sections.json").exists() else []
    references_blob = _load_json(paper_dir / "references.json") if (paper_dir / "references.json").exists() else {"references": []}
    references = references_blob.get("references", []) if isinstance(references_blob, dict) else []

    title = _first_non_empty(
        analysis.get("metadata", {}).get("title"),
        analysis.get("paper_id"),
        paper_dir.name,
    )
    abstract = _first_non_empty(
        analysis.get("abstract"),
        analysis.get("metadata", {}).get("abstract"),
        _read_text(paper_dir / "abstract.txt") if (paper_dir / "abstract.txt").exists() else "",
    )
    full_text = _read_text(paper_dir / "full_text.txt")

    for marker, hint in PAPER_HINTS:
        if marker in paper_dir.name:
            return PaperProfile(
                paper_id=paper_dir.name,
                title=title,
                abstract=abstract,
                full_text=full_text,
                sections=sections,
                references=references,
                short_name=hint["short_name"],
                page_filename=hint["page_filename"],
                description=hint["description"],
                engineer_summary=hint["engineer_summary"],
                core_problem=hint["core_problem"],
                core_idea=hint["core_idea"],
                key_contributions=hint["key_contributions"],
                concepts=hint["concepts"],
                methodologies=hint["methodologies"],
                practical_applications=hint["practical_applications"],
                implementation_hints=hint["implementation_hints"],
                notable_results=hint["notable_results"],
                glossary_terms=hint["glossary_terms"],
                sections_to_inspect=hint["sections_to_inspect"],
            )

    slug = _slugify(title)
    summary = _sentence_case(abstract.split(".")[0]) if abstract else "Automatically imported paper."
    return PaperProfile(
        paper_id=paper_dir.name,
        title=title,
        abstract=abstract,
        full_text=full_text,
        sections=sections,
        references=references,
        short_name=title,
        page_filename=f"paper_{slug}.md",
        description=summary,
        engineer_summary=summary,
        core_problem="This paper was imported automatically. Review the extracted text for a fuller manual interpretation.",
        core_idea=summary,
        key_contributions=[summary] if summary else [],
        concepts=["Optimization"],
        methodologies=["Automatic import from extracted paper artifacts"],
        practical_applications=[
            {
                "title": "Review this paper manually for domain-specific uses",
                "details": "The builder found the paper, but no custom engineering profile exists yet. Add one to src/wiki/builder.py for a richer wiki page.",
            }
        ],
        implementation_hints=["Extend PAPER_HINTS with a custom profile for this paper."],
        notable_results=[summary] if summary else [],
        glossary_terms=["Optimization"],
        sections_to_inspect=[],
    )


def _load_profiles() -> list[PaperProfile]:
    profiles: list[PaperProfile] = []
    if not TEXT_DIR.exists():
        return profiles

    for paper_dir in sorted(path for path in TEXT_DIR.iterdir() if path.is_dir()):
        if not (paper_dir / "analysis.json").exists() or not (paper_dir / "full_text.txt").exists():
            continue
        profiles.append(_build_profile(paper_dir))
    return profiles


def _detect_shared_concepts(profiles: list[PaperProfile]) -> list[str]:
    counts = Counter(concept for profile in profiles for concept in profile.concepts)
    return [concept for concept, count in counts.items() if count > 1]


def _reference_snippets(profile: PaperProfile, limit: int = 5) -> list[str]:
    snippets: list[str] = []
    for entry in profile.references[:limit]:
        if isinstance(entry, dict):
            raw_text = _clean_text(str(entry.get("raw_text", "")))
            if raw_text:
                snippets.append(raw_text)
    return snippets


def _common_reference_fragments(profiles: list[PaperProfile]) -> list[str]:
    normalized_by_paper: list[set[str]] = []
    for profile in profiles:
        fragments: set[str] = set()
        for entry in profile.references:
            raw = _clean_text(str(entry.get("raw_text", ""))) if isinstance(entry, dict) else ""
            for piece in re.split(r"\.\s+", raw):
                piece = piece.strip()
                if len(piece) >= 30:
                    fragments.add(piece.lower())
        if fragments:
            normalized_by_paper.append(fragments)
    if len(normalized_by_paper) < 2:
        return []
    common = set.intersection(*normalized_by_paper)
    return sorted(piece for piece in common if piece)[:5]


def _format_bullets(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def _link_list(profiles: list[PaperProfile]) -> list[tuple[str, str]]:
    links = [
        ("Main index", "index.md"),
        ("Concepts", "concepts.md"),
        ("Practical applications", "practical_applications.md"),
        ("Cross references", "cross_references.md"),
        ("Glossary", "glossary.md"),
    ]
    links.extend((profile.short_name, profile.page_filename) for profile in profiles)
    return links


def _build_index(profiles: list[PaperProfile]) -> str:
    links = _link_list(profiles)
    shared_concepts = _detect_shared_concepts(profiles)
    paper_summaries = "\n".join(
        f"## {profile.title}\n\n- Page: [{profile.short_name}]({profile.page_filename})\n- Summary: {profile.description}\n- Engineer view: {profile.engineer_summary}"
        for profile in profiles
    )
    cross_summary = [
        "Both papers treat learning as an optimization problem with explicit control over what updates are allowed.",
        "The generalization paper focuses on how neural training separates transferable signal from noise; SkillOpt applies a similar discipline to text-based agent skills.",
        "Together they suggest a practical design rule: use structure, validation, and update constraints to improve systems without blindly trusting every training signal.",
    ]
    if shared_concepts:
        cross_summary.append(
            "Shared concepts detected across the imported papers: " + ", ".join(shared_concepts) + "."
        )

    toc = "\n".join(f"- [{label}]({target})" for label, target in links)

    return _clean_text(
        f"""
# AI Research Paper Wiki

This wiki turns extracted research paper artifacts into an engineer-facing knowledge base. It emphasizes what each paper contributes, how the ideas connect, and what a practitioner could build with them.

## Table of contents

{toc}

## Papers in this wiki

{paper_summaries}

## Cross-reference summary

{_format_bullets(cross_summary)}
"""
    ) + "\n"


def _build_concepts(profiles: list[PaperProfile]) -> str:
    sections: list[str] = [
        "# Key Concepts Across Papers",
        "",
        "This page collects the main ideas that appear across the current paper set and explains why they matter for engineering work.",
        "",
        "See also: [Index](index.md), [Cross references](cross_references.md), [Glossary](glossary.md)",
        "",
    ]

    for concept, metadata in CONCEPT_LIBRARY.items():
        papers = [profile for profile in profiles if concept in profile.concepts]
        if not papers:
            continue
        paper_links = ", ".join(f"[{profile.short_name}]({profile.page_filename})" for profile in papers)
        sections.extend(
            [
                f"## {concept}",
                "",
                f"**Definition:** {metadata['definition']}",
                "",
                f"**Appears in:** {paper_links}",
                "",
                f"**Practical relevance:** {metadata['practical_relevance']}",
                "",
            ]
        )
    return "\n".join(sections).rstrip() + "\n"


def _build_practical_applications(profiles: list[PaperProfile]) -> str:
    blocks = [
        "# Practical Applications",
        "",
        "This page translates the papers into concrete engineering work. The goal is not to restate the papers, but to surface what an engineer could implement next.",
        "",
        "See also: [Concepts](concepts.md) and [Cross references](cross_references.md)",
        "",
    ]
    for profile in profiles:
        blocks.append(f"## {profile.title}")
        blocks.append("")
        blocks.append(profile.engineer_summary)
        blocks.append("")
        for application in profile.practical_applications:
            blocks.append(f"### {application['title']}")
            blocks.append("")
            blocks.append(f"- What to build: {application['details']}")
            blocks.append("")
        blocks.append("### Implementation hints")
        blocks.append("")
        blocks.extend(f"- {hint}" for hint in profile.implementation_hints)
        blocks.append("")
    return "\n".join(blocks).rstrip() + "\n"


def _build_cross_references(profiles: list[PaperProfile]) -> str:
    shared_concepts = _detect_shared_concepts(profiles)
    common_refs = _common_reference_fragments(profiles)
    pairwise_links: list[str] = []

    if len(profiles) >= 2:
        for left in profiles:
            for right in profiles:
                if left.paper_id >= right.paper_id:
                    continue
                pairwise_links.extend(
                    [
                        f"{left.short_name} studies optimization in model-training dynamics, while {right.short_name} applies optimizer-style controls to editable agent skills.",
                        f"{left.short_name} separates transferable signal from misleading noise; {right.short_name} uses validation-gated updates and rejected-edit memory to do a similar kind of filtering in text space.",
                        f"{left.short_name} is strongest for ML training diagnostics and optimizer ideas; {right.short_name} is strongest for agent workflow design, skill versioning, and autonomous improvement loops.",
                    ]
                )

    methodology_map = [
        "Both papers prefer controlled updates over unconstrained change.",
        "Both treat validation as a key safety mechanism: one through population-risk style reasoning and one through an explicit held-out acceptance gate.",
        "Both are useful when you want to improve a system without changing core model weights blindly.",
    ]

    lines = [
        "# Cross References and Connections",
        "",
        "This page highlights where the papers overlap and where they complement each other.",
        "",
        "See also: [Index](index.md), [Concepts](concepts.md), [Practical applications](practical_applications.md)",
        "",
        "## Shared themes",
        "",
    ]
    lines.extend(f"- {item}" for item in methodology_map)
    if shared_concepts:
        lines.append(f"- Shared concepts detected in the current import: {', '.join(shared_concepts)}.")
    lines.extend([
        "",
        "## How the papers relate",
        "",
    ])
    lines.extend(f"- {item}" for item in pairwise_links)
    lines.extend([
        "",
        "## Common references or methodologies",
        "",
    ])
    if common_refs:
        lines.extend(f"- Common reference fragment: {fragment}" for fragment in common_refs)
    else:
        lines.append("- No clear shared bibliographic references were detected in the extracted reference text. The stronger connection is methodological: both papers frame improvement as disciplined optimization under constraints.")
    lines.extend([
        "",
        "## Engineer takeaway",
        "",
        "- If you are training models, borrow the generalization paper's focus on separating signal from memorization.",
        "- If you are tuning agents, borrow SkillOpt's bounded edits, validation gates, and explicit rejected-update memory.",
        "- If you are building a full AI system, combine both: use strong update filters in both weight space and text-config space.",
    ])
    return "\n".join(lines).rstrip() + "\n"


def _build_glossary(profiles: list[PaperProfile]) -> str:
    terms = sorted({term for profile in profiles for term in profile.glossary_terms})
    lines = [
        "# Glossary",
        "",
        "Short definitions for technical terms that appear in the current wiki pages.",
        "",
        "See also: [Concepts](concepts.md)",
        "",
    ]
    for term in terms:
        definition = GLOSSARY_LIBRARY.get(term, "Definition pending. Extend GLOSSARY_LIBRARY in src/wiki/builder.py.")
        lines.append(f"## {term}")
        lines.append("")
        lines.append(definition)
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _build_paper_page(profile: PaperProfile) -> str:
    section_titles = [
        section.get("title", "")
        for section in profile.sections
        if isinstance(section, dict) and section.get("title")
    ]
    useful_sections = profile.sections_to_inspect or [title for title in section_titles if len(title) > 3][:8]
    references = _reference_snippets(profile)

    lines = [
        f"# {profile.title}",
        "",
        f"Source directory: `{profile.paper_id}`",
        "",
        f"See also: [Index](index.md), [Concepts](concepts.md), [Practical applications](practical_applications.md), [Cross references](cross_references.md), [Glossary](glossary.md)",
        "",
        "## Why this paper matters for engineers",
        "",
        profile.engineer_summary,
        "",
        "## Core problem",
        "",
        profile.core_problem,
        "",
        "## Core idea",
        "",
        profile.core_idea,
        "",
        "## Key contributions",
        "",
    ]
    lines.extend(f"- {item}" for item in profile.key_contributions)
    lines.extend([
        "",
        "## Practical applications",
        "",
    ])
    for application in profile.practical_applications:
        lines.append(f"### {application['title']}")
        lines.append("")
        lines.append(application["details"])
        lines.append("")
    lines.extend([
        "## Implementation hints",
        "",
    ])
    lines.extend(f"- {hint}" for hint in profile.implementation_hints)
    lines.extend([
        "",
        "## Notable results or claims",
        "",
    ])
    lines.extend(f"- {item}" for item in profile.notable_results)
    lines.extend([
        "",
        "## Methods and sections to inspect",
        "",
    ])
    if useful_sections:
        lines.extend(f"- {item}" for item in useful_sections)
    else:
        lines.append("- Section metadata was noisy in extraction, so use the full text and abstract for the most reliable reading.")
    lines.extend([
        "",
        "## References and related work",
        "",
    ])
    if references:
        lines.extend(f"- {item}" for item in references)
    else:
        lines.append("- Reference extraction was sparse for this paper.")
    lines.extend([
        "",
        "## Related wiki pages",
        "",
        f"- [Concepts](concepts.md) for shared terminology used in {profile.short_name.lower()}.",
        f"- [Practical applications](practical_applications.md) for implementation-oriented next steps based on {profile.short_name.lower()}.",
        f"- [Cross references](cross_references.md) to compare {profile.short_name.lower()} with the other imported papers.",
    ])
    return "\n".join(lines).rstrip() + "\n"


def generate_wiki() -> list[Path]:
    profiles = _load_profiles()
    WIKI_DIR.mkdir(parents=True, exist_ok=True)

    pages: dict[str, str] = {
        "index.md": _build_index(profiles),
        "concepts.md": _build_concepts(profiles),
        "practical_applications.md": _build_practical_applications(profiles),
        "cross_references.md": _build_cross_references(profiles),
        "glossary.md": _build_glossary(profiles),
    }
    for profile in profiles:
        pages[profile.page_filename] = _build_paper_page(profile)

    written: list[Path] = []
    for name, content in pages.items():
        target = WIKI_DIR / name
        target.write_text(content, encoding="utf-8")
        written.append(target)
    return written


def main() -> None:
    written = generate_wiki()
    print(f"Generated {len(written)} wiki files in {WIKI_DIR}")
    for path in written:
        print(f"- {path.name}")


if __name__ == "__main__":
    main()
