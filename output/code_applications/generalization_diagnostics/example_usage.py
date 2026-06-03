"""Example script for the NTK-based generalization diagnostics application."""

from __future__ import annotations

import json
from pathlib import Path

from diagnostics import (
    SimpleMLPRegressor,
    analyze_generalization,
    make_sinusoidal_dataset,
    plot_diagnostics,
    plot_drift_diffusion,
    simulate_drift_diffusion,
)


def main() -> None:
    """Train a small network, analyze it, and save plots and metrics."""
    app_dir = Path(__file__).resolve().parent
    output_dir = app_dir / "artifacts"
    output_dir.mkdir(exist_ok=True)

    dataset = make_sinusoidal_dataset(seed=11)
    model = SimpleMLPRegressor(n_features=1, hidden_dim=20, seed=11)
    model.fit(dataset["X_train"], dataset["y_train"], epochs=2200, lr=0.03, verbose=True)
    report, details = analyze_generalization(
        model,
        dataset["X_train"],
        dataset["y_train"],
        dataset["X_test"],
        dataset["y_test"],
        dataset["y_train_clean"],
    )
    figure_path = plot_diagnostics(
        dataset["X_train"],
        dataset["y_train"],
        dataset["y_train_clean"],
        details,
        output_dir,
    )

    metrics_path = output_dir / "generalization_report.json"
    metrics_path.write_text(json.dumps(report.to_dict(), indent=2), encoding="utf-8")

    print("Generalization diagnostics example complete.")
    for metric_name, metric_value in report.to_dict().items():
        print(f"- {metric_name}: {metric_value}")
    print(f"- Saved figure: {figure_path}")
    print(f"- Saved metrics: {metrics_path}")

    # Drift-diffusion diagnostic (paper Section 4)
    dd_result = simulate_drift_diffusion(
        model,
        dataset["X_train"],
        dataset["y_train_clean"],
        dataset["y_train"],
        n_steps=150,
        batch_size=20,
        seed=11,
    )
    dd_path = plot_drift_diffusion(dd_result, output_dir)
    final_snr = float(dd_result["snr"][-1])
    print(f"- Drift-diffusion SNR at final step: {final_snr:.3f}")
    print(f"- Saved drift-diffusion figure: {dd_path}")


if __name__ == "__main__":
    main()
