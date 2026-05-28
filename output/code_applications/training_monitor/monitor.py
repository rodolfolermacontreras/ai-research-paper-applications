"""Monitoring utilities for tracking generalization dynamics during NumPy training."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


@dataclass
class MonitorRecord:
    """Snapshot of the training state at one monitoring step."""

    epoch: int
    train_loss: float
    test_loss: float
    generalization_gap: float
    gradient_norm: float
    parameter_norm: float
    effective_dimension: float
    ntk_trace: float


class SimpleMLPRegressor:
    """A compact regression network that exposes gradients for monitoring."""

    def __init__(self, n_features: int, hidden_dim: int = 20, seed: int = 0, weight_scale: float = 0.35) -> None:
        rng = np.random.default_rng(seed)
        self.W1 = rng.normal(scale=weight_scale / np.sqrt(n_features), size=(n_features, hidden_dim))
        self.b1 = np.zeros(hidden_dim, dtype=float)
        self.W2 = rng.normal(scale=weight_scale / np.sqrt(hidden_dim), size=hidden_dim)
        self.b2 = 0.0

    def forward(self, X: np.ndarray) -> np.ndarray:
        """Compute predictions."""
        hidden = np.tanh(X @ self.W1 + self.b1)
        return hidden @ self.W2 + self.b2

    def loss_and_gradients(self, X: np.ndarray, y: np.ndarray) -> tuple[float, dict[str, np.ndarray | float]]:
        """Return mean-squared error and parameter gradients."""
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

    def step(self, gradients: dict[str, np.ndarray | float], lr: float) -> None:
        """Apply a single gradient descent update."""
        self.W1 -= lr * np.asarray(gradients["W1"])
        self.b1 -= lr * np.asarray(gradients["b1"])
        self.W2 -= lr * np.asarray(gradients["W2"])
        self.b2 -= lr * float(gradients["b2"])

    def parameter_vector(self) -> np.ndarray:
        """Flatten parameters to a single vector."""
        return np.concatenate([self.W1.ravel(), self.b1, self.W2, np.array([self.b2])])

    def per_sample_output_gradients(self, X: np.ndarray) -> np.ndarray:
        """Return per-sample output gradients for empirical NTK calculations."""
        hidden = np.tanh(X @ self.W1 + self.b1)
        local = (1.0 - hidden**2) * self.W2
        jacobian = np.zeros((len(X), self.parameter_vector().size), dtype=float)
        for index, (x_row, hidden_row, local_row) in enumerate(zip(X, hidden, local)):
            dW1 = np.outer(x_row, local_row).ravel()
            jacobian[index] = np.concatenate([dW1, local_row, hidden_row, np.array([1.0])])
        return jacobian


def compute_empirical_ntk(model: SimpleMLPRegressor, X: np.ndarray) -> np.ndarray:
    """Construct the empirical NTK on a batch of inputs."""
    jacobian = model.per_sample_output_gradients(X)
    kernel = jacobian @ jacobian.T
    return 0.5 * (kernel + kernel.T)


def effective_dimension(kernel: np.ndarray, ridge: float = 1e-6) -> float:
    """Compute an effective dimension from the NTK spectrum."""
    eigenvalues = np.linalg.eigvalsh(kernel)
    eigenvalues = np.clip(eigenvalues, a_min=0.0, a_max=None)
    return float(np.sum(eigenvalues / (eigenvalues + ridge)))


class TrainingMonitor:
    """Collect and visualize generalization metrics during training."""

    def __init__(self) -> None:
        self.records: list[MonitorRecord] = []

    def log(
        self,
        epoch: int,
        model: SimpleMLPRegressor,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_test: np.ndarray,
        y_test: np.ndarray,
        gradients: dict[str, np.ndarray | float],
    ) -> None:
        """Store one monitoring record."""
        train_loss = float(np.mean((model.forward(X_train) - y_train) ** 2))
        test_loss = float(np.mean((model.forward(X_test) - y_test) ** 2))
        gradient_vector = np.concatenate(
            [
                np.asarray(gradients["W1"]).ravel(),
                np.asarray(gradients["b1"]).ravel(),
                np.asarray(gradients["W2"]).ravel(),
                np.array([float(gradients["b2"])]),
            ]
        )
        parameter_vector = model.parameter_vector()
        kernel = compute_empirical_ntk(model, X_train)
        self.records.append(
            MonitorRecord(
                epoch=epoch,
                train_loss=train_loss,
                test_loss=test_loss,
                generalization_gap=test_loss - train_loss,
                gradient_norm=float(np.linalg.norm(gradient_vector)),
                parameter_norm=float(np.linalg.norm(parameter_vector)),
                effective_dimension=effective_dimension(kernel),
                ntk_trace=float(np.trace(kernel)),
            )
        )

    def to_frame(self) -> pd.DataFrame:
        """Return monitoring data as a DataFrame."""
        return pd.DataFrame([asdict(record) for record in self.records])

    def save_artifacts(self, output_dir: str | Path) -> tuple[Path, Path]:
        """Write a CSV table and a figure summarizing training dynamics."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        frame = self.to_frame()
        csv_path = output_path / "training_dynamics.csv"
        frame.to_csv(csv_path, index=False)

        figure, axes = plt.subplots(2, 2, figsize=(12, 9))
        axes[0, 0].plot(frame["epoch"], frame["train_loss"], label="train")
        axes[0, 0].plot(frame["epoch"], frame["test_loss"], label="test")
        axes[0, 0].set_title("Loss dynamics")
        axes[0, 0].set_xlabel("Epoch")
        axes[0, 0].set_ylabel("MSE")
        axes[0, 0].legend()

        axes[0, 1].plot(frame["epoch"], frame["generalization_gap"], color="#E45756")
        axes[0, 1].set_title("Train/test gap")
        axes[0, 1].set_xlabel("Epoch")
        axes[0, 1].set_ylabel("Gap")

        axes[1, 0].plot(frame["epoch"], frame["gradient_norm"], label="gradient norm")
        axes[1, 0].plot(frame["epoch"], frame["parameter_norm"], label="parameter norm")
        axes[1, 0].set_title("Optimization scale")
        axes[1, 0].set_xlabel("Epoch")
        axes[1, 0].legend()

        axes[1, 1].plot(frame["epoch"], frame["effective_dimension"], label="effective dimension")
        axes[1, 1].plot(frame["epoch"], frame["ntk_trace"], label="NTK trace")
        axes[1, 1].set_title("Capacity proxies")
        axes[1, 1].set_xlabel("Epoch")
        axes[1, 1].legend()

        figure.tight_layout()
        figure_path = output_path / "generalization_dynamics.png"
        figure.savefig(figure_path, dpi=160, bbox_inches="tight")
        plt.close(figure)
        return csv_path, figure_path


__all__ = [
    "MonitorRecord",
    "SimpleMLPRegressor",
    "TrainingMonitor",
    "compute_empirical_ntk",
    "effective_dimension",
]
