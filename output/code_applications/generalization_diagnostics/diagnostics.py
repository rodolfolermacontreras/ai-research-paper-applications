"""Utilities for diagnosing generalization behavior in small NumPy neural networks."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np


@dataclass
class GeneralizationReport:
    """Summary statistics for a trained model and its empirical NTK."""

    train_mse: float
    test_mse: float
    generalization_gap: float
    ntk_condition_number: float
    effective_dimension: float
    signal_rank: int
    signal_energy_ratio: float
    noise_signal_ratio: float
    top_eigenvalue: float
    median_eigenvalue: float

    def to_dict(self) -> dict[str, float | int]:
        """Return a JSON-friendly view of the report."""
        return {
            "train_mse": self.train_mse,
            "test_mse": self.test_mse,
            "generalization_gap": self.generalization_gap,
            "ntk_condition_number": self.ntk_condition_number,
            "effective_dimension": self.effective_dimension,
            "signal_rank": self.signal_rank,
            "signal_energy_ratio": self.signal_energy_ratio,
            "noise_signal_ratio": self.noise_signal_ratio,
            "top_eigenvalue": self.top_eigenvalue,
            "median_eigenvalue": self.median_eigenvalue,
        }


class SimpleMLPRegressor:
    """A tiny one-hidden-layer regressor implemented only with NumPy."""

    def __init__(
        self,
        n_features: int,
        hidden_dim: int = 16,
        seed: int = 0,
        weight_scale: float = 0.4,
    ) -> None:
        rng = np.random.default_rng(seed)
        self.n_features = n_features
        self.hidden_dim = hidden_dim
        self.W1 = rng.normal(scale=weight_scale / np.sqrt(n_features), size=(n_features, hidden_dim))
        self.b1 = np.zeros(hidden_dim, dtype=float)
        self.W2 = rng.normal(scale=weight_scale / np.sqrt(hidden_dim), size=hidden_dim)
        self.b2 = 0.0

    def forward(self, X: np.ndarray) -> np.ndarray:
        """Return model predictions for a batch."""
        hidden = np.tanh(X @ self.W1 + self.b1)
        return hidden @ self.W2 + self.b2

    def loss_and_gradients(self, X: np.ndarray, y: np.ndarray) -> tuple[float, dict[str, np.ndarray | float]]:
        """Compute mean-squared error and gradients."""
        hidden = np.tanh(X @ self.W1 + self.b1)
        preds = hidden @ self.W2 + self.b2
        errors = preds - y
        loss = float(np.mean(errors**2))

        scale = 2.0 / len(X)
        d_out = scale * errors
        dW2 = hidden.T @ d_out
        db2 = float(np.sum(d_out))
        hidden_grad = np.outer(d_out, self.W2) * (1.0 - hidden**2)
        dW1 = X.T @ hidden_grad
        db1 = np.sum(hidden_grad, axis=0)
        return loss, {"W1": dW1, "b1": db1, "W2": dW2, "b2": db2}

    def apply_gradients(self, gradients: dict[str, np.ndarray | float], lr: float) -> None:
        """Apply a gradient descent update."""
        self.W1 -= lr * np.asarray(gradients["W1"])
        self.b1 -= lr * np.asarray(gradients["b1"])
        self.W2 -= lr * np.asarray(gradients["W2"])
        self.b2 -= lr * float(gradients["b2"])

    def fit(
        self,
        X: np.ndarray,
        y: np.ndarray,
        epochs: int = 2000,
        lr: float = 0.03,
        verbose: bool = False,
    ) -> list[float]:
        """Train the model with full-batch gradient descent."""
        history: list[float] = []
        for epoch in range(1, epochs + 1):
            loss, gradients = self.loss_and_gradients(X, y)
            self.apply_gradients(gradients, lr=lr)
            history.append(loss)
            if verbose and (epoch == 1 or epoch % 250 == 0):
                print(f"epoch={epoch:4d} loss={loss:.6f}")
        return history

    def parameter_vector(self) -> np.ndarray:
        """Flatten all trainable parameters into one vector."""
        return np.concatenate(
            [self.W1.ravel(), self.b1.ravel(), self.W2.ravel(), np.array([self.b2], dtype=float)]
        )

    def per_sample_output_gradients(self, X: np.ndarray) -> np.ndarray:
        """Return the Jacobian of outputs with respect to parameters."""
        hidden = np.tanh(X @ self.W1 + self.b1)
        local = (1.0 - hidden**2) * self.W2
        jacobian = np.zeros((len(X), self.parameter_vector().size), dtype=float)
        for index, (x_row, hidden_row, local_row) in enumerate(zip(X, hidden, local)):
            dW1 = np.outer(x_row, local_row).ravel()
            db1 = local_row.ravel()
            dW2 = hidden_row.ravel()
            jacobian[index] = np.concatenate([dW1, db1, dW2, np.array([1.0])])
        return jacobian


def make_sinusoidal_dataset(
    n_train: int = 60,
    n_test: int = 140,
    noise_std: float = 0.2,
    seed: int = 7,
) -> dict[str, np.ndarray]:
    """Create a one-dimensional regression problem with known signal and noise."""
    rng = np.random.default_rng(seed)
    X = rng.uniform(-3.5, 3.5, size=n_train + n_test).reshape(-1, 1)
    clean = np.sin(1.5 * X[:, 0]) + 0.25 * X[:, 0]
    observed = clean + rng.normal(scale=noise_std, size=clean.shape)
    permutation = rng.permutation(len(X))
    X = X[permutation]
    clean = clean[permutation]
    observed = observed[permutation]
    split = n_train
    return {
        "X_train": X[:split],
        "y_train": observed[:split],
        "y_train_clean": clean[:split],
        "X_test": X[split:],
        "y_test": observed[split:],
        "y_test_clean": clean[split:],
    }


def compute_empirical_ntk(model: SimpleMLPRegressor, X: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Compute the empirical NTK Gram matrix and its Jacobian."""
    jacobian = model.per_sample_output_gradients(X)
    kernel = jacobian @ jacobian.T
    kernel = 0.5 * (kernel + kernel.T)
    return kernel, jacobian


def spectral_signal_noise_decomposition(
    kernel: np.ndarray,
    clean_targets: np.ndarray,
    noisy_targets: np.ndarray,
    energy_threshold: float = 0.95,
) -> dict[str, Any]:
    """Project clean signal and observation noise onto NTK signal and reservoir subspaces."""
    eigenvalues, eigenvectors = np.linalg.eigh(kernel)
    order = np.argsort(eigenvalues)[::-1]
    eigenvalues = np.clip(eigenvalues[order], a_min=0.0, a_max=None)
    eigenvectors = eigenvectors[:, order]

    total_energy = float(np.sum(eigenvalues))
    if total_energy <= 1e-12:
        signal_rank = 1
    else:
        cumulative = np.cumsum(eigenvalues) / total_energy
        signal_rank = int(np.searchsorted(cumulative, energy_threshold) + 1)
    signal_basis = eigenvectors[:, :signal_rank]
    reservoir_basis = eigenvectors[:, signal_rank:]

    def project(vector: np.ndarray, basis: np.ndarray) -> np.ndarray:
        if basis.size == 0:
            return np.zeros_like(vector)
        return basis @ (basis.T @ vector)

    noise_targets = noisy_targets - clean_targets
    clean_signal = project(clean_targets, signal_basis)
    clean_reservoir = clean_targets - clean_signal
    noise_signal = project(noise_targets, signal_basis)
    noise_reservoir = noise_targets - noise_signal

    return {
        "eigenvalues": eigenvalues,
        "eigenvectors": eigenvectors,
        "signal_rank": signal_rank,
        "signal_basis": signal_basis,
        "reservoir_basis": reservoir_basis,
        "clean_signal": clean_signal,
        "clean_reservoir": clean_reservoir,
        "noise_signal": noise_signal,
        "noise_reservoir": noise_reservoir,
    }


def effective_dimension(eigenvalues: np.ndarray) -> float:
    """Return a participation-ratio style effective dimension."""
    stable = np.clip(np.asarray(eigenvalues, dtype=float), a_min=0.0, a_max=None)
    numerator = float(np.sum(stable) ** 2)
    denominator = float(np.sum(stable**2)) + 1e-12
    return numerator / denominator


def analyze_generalization(
    model: SimpleMLPRegressor,
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_test: np.ndarray,
    y_test: np.ndarray,
    clean_train_targets: np.ndarray,
) -> tuple[GeneralizationReport, dict[str, Any]]:
    """Compute model quality metrics, empirical NTK diagnostics, and decompositions."""
    train_predictions = model.forward(X_train)
    test_predictions = model.forward(X_test)
    train_mse = float(np.mean((train_predictions - y_train) ** 2))
    test_mse = float(np.mean((test_predictions - y_test) ** 2))

    kernel, jacobian = compute_empirical_ntk(model, X_train)
    decomposition = spectral_signal_noise_decomposition(kernel, clean_train_targets, y_train)
    eigenvalues = decomposition["eigenvalues"]
    condition_number = float(eigenvalues[0] / max(eigenvalues[-1], 1e-8))
    clean_energy = float(np.linalg.norm(clean_train_targets) ** 2) + 1e-12
    noise_vector = y_train - clean_train_targets
    noise_energy = float(np.linalg.norm(noise_vector) ** 2) + 1e-12

    report = GeneralizationReport(
        train_mse=train_mse,
        test_mse=test_mse,
        generalization_gap=test_mse - train_mse,
        ntk_condition_number=condition_number,
        effective_dimension=effective_dimension(eigenvalues),
        signal_rank=int(decomposition["signal_rank"]),
        signal_energy_ratio=float(np.linalg.norm(decomposition["clean_signal"]) ** 2 / clean_energy),
        noise_signal_ratio=float(np.linalg.norm(decomposition["noise_signal"]) ** 2 / noise_energy),
        top_eigenvalue=float(eigenvalues[0]),
        median_eigenvalue=float(np.median(eigenvalues)),
    )

    details = {
        "kernel": kernel,
        "jacobian": jacobian,
        "train_predictions": train_predictions,
        "test_predictions": test_predictions,
        "observed_train_targets": y_train,
        "clean_train_targets": clean_train_targets,
        **decomposition,
    }
    return report, details


def plot_diagnostics(
    X_train: np.ndarray,
    y_train: np.ndarray,
    clean_train_targets: np.ndarray,
    details: dict[str, Any],
    output_dir: str | Path,
) -> Path:
    """Create a multi-panel figure summarizing NTK and signal/noise diagnostics."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    figure, axes = plt.subplots(2, 2, figsize=(12, 9))
    eigenvalues = np.asarray(details["eigenvalues"])
    axes[0, 0].semilogy(np.arange(1, len(eigenvalues) + 1), eigenvalues + 1e-12, marker="o")
    axes[0, 0].set_title("Empirical NTK eigenspectrum")
    axes[0, 0].set_xlabel("Eigenvalue index")
    axes[0, 0].set_ylabel("Magnitude")

    clean_signal = float(np.linalg.norm(details["clean_signal"]) ** 2)
    clean_reservoir = float(np.linalg.norm(details["clean_reservoir"]) ** 2)
    noise_signal = float(np.linalg.norm(details["noise_signal"]) ** 2)
    noise_reservoir = float(np.linalg.norm(details["noise_reservoir"]) ** 2)
    labels = ["clean→signal", "clean→reservoir", "noise→signal", "noise→reservoir"]
    values = [clean_signal, clean_reservoir, noise_signal, noise_reservoir]
    axes[0, 1].bar(labels, values, color=["#4C78A8", "#9ECAE9", "#E45756", "#F28E8E"])
    axes[0, 1].set_title("Signal vs. noise energy decomposition")
    axes[0, 1].tick_params(axis="x", rotation=20)
    axes[0, 1].set_ylabel("Projected energy")

    order = np.argsort(X_train[:, 0])
    axes[1, 0].plot(X_train[order, 0], clean_train_targets[order], label="clean target", linewidth=2)
    axes[1, 0].scatter(X_train[order, 0], y_train[order], label="observed target", s=25, alpha=0.8)
    axes[1, 0].plot(
        X_train[order, 0],
        details["train_predictions"][order],
        label="network prediction",
        linestyle="--",
        linewidth=2,
    )
    axes[1, 0].set_title("Fit against clean signal and noisy labels")
    axes[1, 0].set_xlabel("x")
    axes[1, 0].set_ylabel("y")
    axes[1, 0].legend()

    image = axes[1, 1].imshow(details["kernel"], aspect="auto", cmap="viridis")
    axes[1, 1].set_title("Empirical NTK Gram matrix")
    axes[1, 1].set_xlabel("Train sample index")
    axes[1, 1].set_ylabel("Train sample index")
    figure.colorbar(image, ax=axes[1, 1], fraction=0.046)

    figure.tight_layout()
    image_path = output_path / "generalization_diagnostics.png"
    figure.savefig(image_path, dpi=160, bbox_inches="tight")
    plt.close(figure)
    return image_path


__all__ = [
    "GeneralizationReport",
    "SimpleMLPRegressor",
    "analyze_generalization",
    "compute_empirical_ntk",
    "effective_dimension",
    "make_sinusoidal_dataset",
    "plot_diagnostics",
    "spectral_signal_noise_decomposition",
]


if __name__ == "__main__":
    dataset = make_sinusoidal_dataset()
    model = SimpleMLPRegressor(n_features=1, hidden_dim=18, seed=7)
    model.fit(dataset["X_train"], dataset["y_train"], epochs=1500, lr=0.03, verbose=True)
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
        Path(__file__).resolve().parent / "artifacts",
    )
    print("Generalization report:")
    for key, value in report.to_dict().items():
        print(f"  {key}: {value}")
    print(f"Saved diagnostics figure to {figure_path}")
