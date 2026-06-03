"""Demo for the simplified skill evolution framework."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from executive import ExecutiveStrategy, TextTask
from skill_optimizer import SkillOptimizer
from skills import create_default_skill_library


def build_datasets() -> tuple[list[TextTask], list[TextTask]]:
    """Create train and validation tasks for the evolution demo."""
    train_tasks = [
        TextTask(
            task_id="sum-train-1",
            task_type="summarize",
            text="Team update. Revenue jumped 18 percent after the new checkout flow launched. Several cosmetic bugs remain.",
            expected="Revenue jumped 18 percent after the new checkout flow launched.",
        ),
        TextTask(
            task_id="sum-train-2",
            task_type="summarize",
            text="Research memo. The strongest result was a 12 point accuracy gain on noisy data. Future work covers scaling.",
            expected="The strongest result was a 12 point accuracy gain on noisy data.",
        ),
        TextTask(
            task_id="kw-train-1",
            task_type="keywords",
            text="The registry tracks latency, accuracy, and reliability for every agent skill.",
            expected=["registry", "latency", "accuracy", "reliability", "skill"],
        ),
        TextTask(
            task_id="kw-train-2",
            task_type="keywords",
            text="Generalization diagnostics highlight signal, noise, eigenspectrum, and train gap.",
            expected=["generalization", "diagnostics", "signal", "noise", "eigenspectrum"],
        ),
        TextTask(
            task_id="sent-train-1",
            task_type="sentiment",
            text="The assistant was helpful, reliable, and fast during testing.",
            expected="positive",
        ),
        TextTask(
            task_id="sent-train-2",
            task_type="sentiment",
            text="The interface felt buggy, confusing, and slow.",
            expected="negative",
        ),
    ]
    validation_tasks = [
        TextTask(
            task_id="sum-val-1",
            task_type="summarize",
            text="Program note. Model calibration reduced false alarms by 30 percent in production. Documentation updates are pending.",
            expected="Model calibration reduced false alarms by 30 percent in production.",
        ),
        TextTask(
            task_id="sum-val-2",
            task_type="summarize",
            text="Status report. The most important change was adding validation gating to the optimizer. Benchmarks will run tomorrow.",
            expected="The most important change was adding validation gating to the optimizer.",
        ),
        TextTask(
            task_id="kw-val-1",
            task_type="keywords",
            text="Executive strategy chooses skills, composes them, and tracks validation gains.",
            expected=["executive", "strategy", "skills", "validation", "gains"],
        ),
        TextTask(
            task_id="sent-val-1",
            task_type="sentiment",
            text="The rollout was smooth and the final result was excellent.",
            expected="positive",
        ),
    ]
    return train_tasks, validation_tasks


def summarize_scores(frame: pd.DataFrame) -> pd.Series:
    """Aggregate average score by task type."""
    return frame.groupby("task_type")["score"].mean().sort_index()


def print_iteration_report(history_frame: pd.DataFrame, baseline_scores: pd.Series, improved_scores: pd.Series) -> None:
    """Print a human-readable per-epoch optimization report to stdout.

    Shows accepted and rejected steps, final score deltas, and a summary
    line per task type -- mirroring the epoch-wise reporting a real
    SkillOpt loop would produce.
    """
    print()
    print("=== Optimization history by epoch and task type ===")
    for epoch in sorted(history_frame["epoch"].unique()):
        epoch_rows = history_frame[history_frame["epoch"] == epoch]
        accepted = epoch_rows[epoch_rows["accepted"]]
        rejected = epoch_rows[~epoch_rows["accepted"]]
        print(f"\n-- Epoch {epoch} --")
        if accepted.empty:
            print("  Accepted edits: none")
        else:
            for _, row in accepted.iterrows():
                chain_str = " -> ".join(row["candidate_chain"])
                print(f"  ACCEPTED  [{row['task_type']}]  chain={chain_str}")
                print(f"            train_score={row['train_score']:.3f}  val_score={row['validation_score']:.3f}")
        if not rejected.empty:
            for _, row in rejected.iterrows():
                chain_str = " -> ".join(row["candidate_chain"])
                print(f"  rejected  [{row['task_type']}]  chain={chain_str}")
                print(f"            train_score={row['train_score']:.3f}  val_score={row['validation_score']:.3f}")

    print()
    print("=== Final delta (baseline -> improved) ===")
    all_types = sorted(set(baseline_scores.index) | set(improved_scores.index))
    for task_type in all_types:
        base = baseline_scores.get(task_type, 0.0)
        impr = improved_scores.get(task_type, 0.0)
        delta = impr - base
        direction = "+" if delta >= 0 else ""
        print(f"  {task_type:<12}  {base:.3f} -> {impr:.3f}  ({direction}{delta:.3f})")
    print()


def main() -> None:
    """Run the skill evolution demo and save a before/after comparison plot."""
    app_dir = Path(__file__).resolve().parent
    output_dir = app_dir / "artifacts"
    output_dir.mkdir(exist_ok=True)

    library = create_default_skill_library()
    executive = ExecutiveStrategy()
    optimizer = SkillOptimizer(library, executive)
    train_tasks, validation_tasks = build_datasets()

    baseline = optimizer.evaluate_dataset(validation_tasks)
    history = optimizer.optimize(train_tasks, validation_tasks, epochs=3)
    improved = optimizer.evaluate_dataset(validation_tasks)

    baseline_scores = summarize_scores(baseline)
    improved_scores = summarize_scores(improved)
    history_frame = optimizer.history_frame(history)

    comparison = pd.DataFrame({"baseline": baseline_scores, "improved": improved_scores}).fillna(0.0)
    comparison.plot(kind="bar", figsize=(8, 5), ylim=(0.0, 1.05), title="Skill evolution performance")
    plt.ylabel("Average score")
    plt.tight_layout()
    figure_path = output_dir / "skill_evolution_scores.png"
    plt.savefig(figure_path, dpi=160, bbox_inches="tight")
    plt.close()

    history_path = output_dir / "optimization_history.json"
    history_path.write_text(history_frame.to_json(orient="records", indent=2), encoding="utf-8")

    print_iteration_report(history_frame, baseline_scores, improved_scores)

    print("Skill evolution demo complete.")
    print("Baseline validation scores:")
    for task_type, score in baseline_scores.items():
        print(f"- {task_type}: {score:.3f}")
    print("Improved validation scores:")
    for task_type, score in improved_scores.items():
        print(f"- {task_type}: {score:.3f}")
    print("Accepted edits:")
    accepted = history_frame[history_frame["accepted"]]
    if accepted.empty:
        print("- none")
    else:
        for _, row in accepted.iterrows():
            print(f"- epoch {int(row['epoch'])} {row['task_type']}: {' -> '.join(row['candidate_chain'])}")
    print(f"Saved plot: {figure_path}")
    print(f"Saved optimization history: {history_path}")


if __name__ == "__main__":
    main()
