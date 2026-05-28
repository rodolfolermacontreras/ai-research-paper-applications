# Generalization Diagnostics

This application turns the paper *A Theory of Generalization in Deep Learning* into a small, runnable diagnostic workflow for NumPy neural networks.

## What it does

- trains a tiny one-hidden-layer regressor without PyTorch or TensorFlow
- computes an empirical neural tangent kernel (NTK) from per-sample parameter gradients
- decomposes observed labels into clean signal and noise projections over NTK signal and reservoir subspaces
- reports generalization metrics such as train/test gap, NTK condition number, effective dimension, and signal/noise energy ratios
- saves a figure showing the NTK eigenspectrum, signal-vs-noise energy, model fit, and NTK Gram matrix

## Paper concepts implemented

- empirical NTK as a local linearization of the network
- signal vs. reservoir decomposition via the NTK eigenspace
- effective dimensionality from the NTK spectrum
- generalization gap measured on held-out data

## Files

- `diagnostics.py` - core model, NTK computation, decomposition, and plotting utilities
- `example_usage.py` - runnable end-to-end demo

## How to run

From the repository root:

```powershell
.\.venv\Scripts\python.exe output\code_applications\generalization_diagnostics\example_usage.py
```

Artifacts are written to `output\code_applications\generalization_diagnostics\artifacts\`.
