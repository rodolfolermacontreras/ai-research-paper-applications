# Training Monitor

This application converts the monitoring ideas from *A Theory of Generalization in Deep Learning* into a lightweight NumPy training dashboard.

## What it tracks

- train loss and test loss over optimization
- generalization gap (`test_loss - train_loss`)
- gradient norm and parameter norm
- empirical NTK trace
- an effective dimension computed from the NTK spectrum
- gradient SNR: ratio of squared mean gradient to minibatch variance (the paper's Section 6 population-risk gate signal)

## Paper concepts implemented

- generalization dynamics tracked during gradient descent
- NTK-derived capacity measures as a proxy for how much of the target function the model can represent
- signal vs. noise intuition through the train/test gap and effective dimension over time
- gradient SNR tracking to identify memorization phases (paper Section 6: update parameter k when mu_k^2 > sigma_k^2 / (b-1))

## Real-world usage scenarios

### Scenario 1: Spotting memorization before it hurts

You are training on a noisy dataset (weak labels, synthetic annotations, or crowdsourced preferences) and your validation loss starts rising while training loss keeps falling.  Run the training monitor and inspect the `gradient_snr` column in `training_dynamics.csv`.  When `gradient_snr` drops below 1.0 and stays there for several epochs, the model is in a memorization phase: gradient variance dominates gradient mean, meaning each batch is pulling parameters in contradictory directions.  At this point, consider increasing batch size, adding label smoothing, or switching to the SNR-gated optimizer from the paper.

### Scenario 2: Deciding when to stop training

You do not have a clean validation set and need to make early-stopping decisions from training statistics alone.  The population-risk objective from the paper (encoded in `gradient_snr`) is an estimate of how much useful signal each update contains.  When `gradient_snr` plateaus near zero and the generalization gap is growing, training has exceeded its useful horizon.  Stop here rather than waiting for an explicit validation signal.

### Scenario 3: Diagnosing grokking-style tasks

You are training a transformer on an algorithmic task (modular arithmetic, boolean satisfiability, sequence prediction) and the model memorizes training labels quickly but does not generalize for hundreds of additional epochs.  The training monitor will show: effective dimension growing slowly, NTK trace high (model has large representational capacity), gradient SNR low in early epochs (noise dominated) and gradually increasing (signal accumulating).  Use this to confirm the grokking dynamic is present and to estimate how many more steps are needed for generalization.

### Scenario 4: Comparing optimizer configurations

Run the training monitor under different batch sizes, learning rates, or optimizer variants and compare the `gradient_snr` curve across runs.  Configurations where `gradient_snr` stays above 1.0 longer are more likely to generalize because they are spending more of their update budget on signal rather than noise.

## Files

- `monitor.py` - model, NTK utilities, monitoring, plotting, CSV export, and CLI entry point
- `example_training.py` - runnable demo on a noisy `sklearn` regression dataset with SNR tracking

## How to run

From the repository root:

```powershell
# Run the example script
.\.venv\Scripts\python.exe output\code_applications\training_monitor\example_training.py

# Or use the CLI entry point directly
.\.venv\Scripts\python.exe output\code_applications\training_monitor\monitor.py --epochs 300 --hidden 32 --lr 0.03
```

Available CLI flags: `--epochs`, `--hidden`, `--lr`, `--seed`, `--output-dir`.

Artifacts are written to `output\code_applications\training_monitor\artifacts\`:
- `training_dynamics.csv`: per-epoch metrics including gradient SNR
- `generalization_dynamics.png`: loss curves, gap, optimization scale, capacity proxies
- `gradient_snr.png`: gradient SNR over training (when minibatch gradients are logged)
