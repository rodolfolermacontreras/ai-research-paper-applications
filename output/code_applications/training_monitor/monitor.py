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
    gradient_snr: float


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
        minibatch_gradients: list[dict[str, np.ndarray | float]] | None = None,
    ) -> None:
        """Store one monitoring record.

        Args:
            epoch: Current training epoch.
            model: The model being trained.
            X_train: Full training inputs.
            y_train: Full training targets.
            X_test: Test inputs.
            y_test: Test targets.
            gradients: Gradient dict from the current full-batch step.
            minibatch_gradients: Optional list of per-minibatch gradient dicts.
                When provided, the gradient SNR is estimated from the mean and
                variance across minibatches (paper Section 6 population-risk
                objective).  When None, SNR is set to -1.0 (not available).
        """
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

        # Gradient SNR: ratio of squared mean gradient to per-parameter variance
        # across minibatches.  This implements the paper's population-risk signal:
        # update parameter k only when mu_k^2 > sigma_k^2 / (b - 1).
        if minibatch_gradients and len(minibatch_gradients) >= 2:
            flat_grads = np.stack(
                [
                    np.concatenate(
                        [
                            np.asarray(g["W1"]).ravel(),
                            np.asarray(g["b1"]).ravel(),
                            np.asarray(g["W2"]).ravel(),
                            np.array([float(g["b2"])]),
                        ]
                    )
                    for g in minibatch_gradients
                ]
            )
            mu = np.mean(flat_grads, axis=0)
            sigma2 = np.var(flat_grads, axis=0, ddof=1)
            b = len(minibatch_gradients)
            # SNR = mean(mu^2) / mean(sigma^2 / (b-1)); scalar summary
            snr_numerator = float(np.mean(mu**2))
            snr_denominator = float(np.mean(sigma2 / max(b - 1, 1))) + 1e-12
            gradient_snr = snr_numerator / snr_denominator
        else:
            gradient_snr = -1.0

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
                gradient_snr=gradient_snr,
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

        # Second figure: gradient SNR over time (if available)
        snr_available = frame["gradient_snr"].gt(0).any()
        if snr_available:
            fig2, ax2 = plt.subplots(figsize=(8, 4))
            ax2.plot(frame.loc[frame["gradient_snr"] > 0, "epoch"],
                     frame.loc[frame["gradient_snr"] > 0, "gradient_snr"],
                     color="#54A24B", linewidth=2)
            ax2.axhline(y=1.0, linestyle="--", color="gray", alpha=0.7, label="SNR = 1 threshold")
            ax2.set_title("Gradient SNR (paper Section 6 population-risk gate)")
            ax2.set_xlabel("Epoch")
            ax2.set_ylabel("mean(mu^2) / mean(sigma^2 / (b-1))")
            ax2.legend()
            fig2.tight_layout()
            snr_path = output_path / "gradient_snr.png"
            fig2.savefig(snr_path, dpi=160, bbox_inches="tight")
            plt.close(fig2)

        return csv_path, figure_path


__all__ = [
    "MonitorRecord",
    "SimpleMLPRegressor",
    "TrainingMonitor",
    "compute_empirical_ntk",
    "effective_dimension",
]


if __name__ == "__main__":
    import argparse

    from sklearn.datasets import make_friedman1
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler

    parser = argparse.ArgumentParser(description="Run training monitor demo.")
    parser.add_argument("--epochs", type=int, default=260, help="Number of training epochs.")
    parser.add_argument("--hidden", type=int, default=24, help="Hidden layer width.")
    parser.add_argument("--lr", type=float, default=0.035, help="Learning rate.")
    parser.add_argument("--seed", type=int, default=19, help="Random seed.")
    parser.add_argument(
        "--output-dir",
        type=str,
        default="artifacts",
        help="Directory for artifacts (relative to this file or absolute).",
    )
    args = parser.parse_args()

    X_all, y_all = make_friedman1(n_samples=240, n_features=10, noise=1.2, random_state=args.seed)
    X_tr, X_te, y_tr, y_te = train_test_split(X_all, y_all, test_size=0.7, random_state=args.seed)
    feat_scaler = StandardScaler()
    tgt_scaler = StandardScaler()
    X_tr = feat_scaler.fit_transform(X_tr)
    X_te = feat_scaler.transform(X_te)
    y_tr = tgt_scaler.fit_transform(y_tr.reshape(-1, 1)).ravel()
    y_te = tgt_scaler.transform(y_te.reshape(-1, 1)).ravel()

    model_cli = SimpleMLPRegressor(n_features=X_tr.shape[1], hidden_dim=args.hidden, seed=args.seed)
    monitor_cli = TrainingMonitor()
    output_dir_path = (
        Path(args.output_dir)
        if Path(args.output_dir).is_absolute()
        else Path(__file__).resolve().parent / args.output_dir
    )

    for epoch in range(1, args.epochs + 1):
        loss, grads = model_cli.loss_and_gradients(X_tr, y_tr)
        model_cli.step(grads, lr=args.lr)
        if epoch == 1 or epoch % 5 == 0:
            monitor_cli.log(epoch, model_cli, X_tr, y_tr, X_te, y_te, grads)
        if epoch == 1 or epoch % 40 == 0:
            print(f"epoch={epoch:3d} train_loss={loss:.5f}")

    csv_out, fig_out = monitor_cli.save_artifacts(output_dir_path)
    summary = monitor_cli.to_frame().iloc[-1]
    print(f"Final train loss: {summary['train_loss']:.5f}")
    print(f"Final test loss:  {summary['test_loss']:.5f}")
    print(f"Final gap:        {summary['generalization_gap']:.5f}")
    print(f"Artifacts: {csv_out}, {fig_out}")
