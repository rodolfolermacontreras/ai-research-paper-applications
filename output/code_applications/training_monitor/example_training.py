"""Example training script for monitoring generalization dynamics."""

from __future__ import annotations

from pathlib import Path

from sklearn.datasets import make_friedman1
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from monitor import SimpleMLPRegressor, TrainingMonitor


def main() -> None:
    """Train a small network and save monitored generalization metrics."""
    app_dir = Path(__file__).resolve().parent
    output_dir = app_dir / "artifacts"
    output_dir.mkdir(exist_ok=True)

    X, y = make_friedman1(n_samples=240, n_features=10, noise=1.2, random_state=19)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.7, random_state=19)

    feature_scaler = StandardScaler()
    target_scaler = StandardScaler()
    X_train = feature_scaler.fit_transform(X_train)
    X_test = feature_scaler.transform(X_test)
    y_train = target_scaler.fit_transform(y_train.reshape(-1, 1)).ravel()
    y_test = target_scaler.transform(y_test.reshape(-1, 1)).ravel()

    model = SimpleMLPRegressor(n_features=X_train.shape[1], hidden_dim=24, seed=19)
    monitor = TrainingMonitor()
    epochs = 260
    learning_rate = 0.035

    for epoch in range(1, epochs + 1):
        train_loss, gradients = model.loss_and_gradients(X_train, y_train)
        model.step(gradients, lr=learning_rate)
        if epoch == 1 or epoch % 5 == 0:
            monitor.log(epoch, model, X_train, y_train, X_test, y_test, gradients)
        if epoch == 1 or epoch % 40 == 0:
            print(f"epoch={epoch:3d} train_loss={train_loss:.5f}")

    csv_path, figure_path = monitor.save_artifacts(output_dir)
    summary = monitor.to_frame().iloc[-1]
    print("Training monitor example complete.")
    print(f"- final train loss: {summary['train_loss']:.5f}")
    print(f"- final test loss: {summary['test_loss']:.5f}")
    print(f"- final gap: {summary['generalization_gap']:.5f}")
    print(f"- final effective dimension: {summary['effective_dimension']:.3f}")
    print(f"- saved metrics: {csv_path}")
    print(f"- saved figure: {figure_path}")


if __name__ == "__main__":
    main()
