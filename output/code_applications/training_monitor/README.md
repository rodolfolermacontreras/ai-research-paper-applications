# Training Monitor

This application converts the monitoring ideas from *A Theory of Generalization in Deep Learning* into a lightweight NumPy training dashboard.

## What it tracks

- train loss and test loss over optimization
- generalization gap (`test_loss - train_loss`)
- gradient norm and parameter norm
- empirical NTK trace
- an effective dimension computed from the NTK spectrum

## Paper concepts implemented

- generalization dynamics tracked during gradient descent
- NTK-derived capacity measures as a proxy for how much of the target function the model can represent
- signal vs. noise intuition through the train/test gap and effective dimension over time

## Files

- `monitor.py` - model, NTK utilities, monitoring, plotting, and CSV export
- `example_training.py` - runnable demo on a noisy `sklearn` regression dataset

## How to run

From the repository root:

```powershell
.\.venv\Scripts\python.exe output\code_applications\training_monitor\example_training.py
```

Artifacts are written to `output\code_applications\training_monitor\artifacts\`.
