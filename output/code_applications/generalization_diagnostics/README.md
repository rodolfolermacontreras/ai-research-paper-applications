# Generalization Diagnostics

This application turns the paper *A Theory of Generalization in Deep Learning* into a small, runnable diagnostic workflow for NumPy neural networks.

## What it does

- trains a tiny one-hidden-layer regressor without PyTorch or TensorFlow
- computes an empirical neural tangent kernel (NTK) from per-sample parameter gradients
- decomposes observed labels into clean signal and noise projections over NTK signal and reservoir subspaces
- reports generalization metrics such as train/test gap, NTK condition number, effective dimension, and signal/noise energy ratios
- saves a figure showing the NTK eigenspectrum, signal-vs-noise energy, model fit, and NTK Gram matrix
- runs a **drift-diffusion simulation** (paper Section 4): quantifies how cumulative signal (drift) grows faster than cumulative memorization noise (diffusion) over training steps, and plots the resulting SNR curve

## Paper concepts implemented

- empirical NTK as a local linearization of the network
- signal vs. reservoir decomposition via the NTK eigenspace
- effective dimensionality from the NTK spectrum
- generalization gap measured on held-out data
- drift-diffusion decomposition: accumulated signal grows as O(T), accumulated noise grows as O(sqrt(T))

## Real-world usage scenarios

### Scenario 1: Understanding why a model generalizes despite overfitting

You have a model with near-zero training loss but good validation accuracy and want to understand why.  Run the NTK signal-reservoir decomposition and inspect `signal_energy_ratio` in the output JSON.  A low ratio (< 0.5) means most of the model's energy is in the reservoir subspace, which is test-invisible; the network has overfit there but it does not matter.  A high `noise_signal_ratio` means the label noise preferentially landed in reservoir directions, which is the benign-overfitting regime from the paper.

### Scenario 2: Diagnosing a model that memorizes but does not generalize

Run the drift-diffusion simulation.  If the final `snr` value is below 1.0, drift is not winning: the accumulated noise from memorization is as large as the accumulated signal.  This suggests your training targets contain too much label noise or that your batch size is too small for the signal strength.  Increasing batch size or reducing label noise should push the SNR above 1.0.

### Scenario 3: Selecting the signal rank threshold

The `signal_rank` metric in the diagnostics report tells you how many NTK eigenvectors are needed to capture 95% of the training-time dissipation energy.  In a well-behaved problem this should be much smaller than the number of training samples.  If `signal_rank` equals the number of training samples, the model has no effective reservoir; all directions are signal-channel and any noise in training labels directly hurts test accuracy.  Consider adding regularization or reducing label noise.

## Files

- `diagnostics.py` - core model, NTK computation, decomposition, drift-diffusion simulation, and plotting utilities
- `example_usage.py` - runnable end-to-end demo

## How to run

From the repository root:

```powershell
.\.venv\Scripts\python.exe output\code_applications\generalization_diagnostics\example_usage.py
```

Artifacts are written to `output\code_applications\generalization_diagnostics\artifacts\`:
- `generalization_diagnostics.png`: NTK eigenspectrum, signal-vs-noise energy, model fit, Gram matrix
- `generalization_report.json`: numeric summary of all diagnostics
- `drift_diffusion.png`: accumulated drift vs. diffusion curves and SNR over training steps
