# A Theory of Generalization in Deep Learning

## Title and Authors

**Title:** A Theory of Generalization in Deep Learning
**Authors:** Elon Litman, Gabe Guo
**Affiliation:** Stanford University
**Paper type:** arXiv preprint, May 2026
**Paper ID:** 2605_01172v1_a_theory_of_generalization_in_deep_learning

---

## Abstract

> We present a non-asymptotic theory of generalization in deep learning where the empirical neural tangent kernel partitions the output space. In directions corresponding to signal, error dissipates rapidly; in the vast orthogonal dimensions corresponding to noise, the kernel's near-zero eigenvalues trap residual error in a test-invisible reservoir. Within the signal channel, minibatch SGD ensures that coherent population signal accumulates via fast linear drift, while idiosyncratic memorization is suppressed into a slow, diffusive random walk. We prove generalization survives even when the kernel evolves O(1) in operator norm, the full feature-learning regime. This theory naturally explains disparate phenomena in deep learning theory, such as benign overfitting, double descent, implicit bias, and grokking. Lastly, we derive an exact population-risk objective from a single training run with no validation data, for any architecture, loss, or optimizer, and prove that it measures precisely the noise in the signal channel. This objective reduces in practice to an SNR preconditioner on top of Adam, adding one state vector at no extra cost; it accelerates grokking by 5x, suppresses memorization in PINNs and implicit neural representations, and improves DPO fine-tuning under noisy preferences while staying 3x closer to the reference policy.

---

## Problem Statement and Motivation

Modern deep neural networks routinely achieve near-zero training loss while still generalizing to unseen data. Classical statistical learning theory, built on uniform convergence, VC dimension, and Rademacher complexity, provides bounds that are either vacuous for overparameterized models or require strong assumptions (e.g., linear networks, frozen kernels, infinite width) that do not hold in practice.

The neural tangent kernel (NTK) framework, introduced by Jacot, Gabriel, and Hongler (2018), offered a cleaner story: in the infinitely wide, lazy training limit, the network's tangent kernel is approximately constant and generalization can be analyzed through classical kernel regression. But in real networks the kernel changes substantially during training, and standard NTK theory breaks down precisely where practitioners care most: the feature-learning regime.

Prior work on benign overfitting, double descent, grokking, and implicit bias each offered partial explanations for why interpolating networks can generalize, but no single framework unified all four phenomena. The authors identified four open questions that their theory targets:

1. Why do overparameterized networks fit noise without necessarily hurting test accuracy?
2. How does minibatch SGD separate meaningful signal from memorization pressure?
3. Can we characterize train-test coupling even when features evolve substantially?
4. Can a principled population-risk objective be estimated online, with no validation set?

See the overview figure for the paper's conceptual framing:

![Overview page 1](../extracted/images/2605_01172v1_a_theory_of_generalization_in_deep_learning/2605_01172v1_a_theory_of_generalization_in_deep_learning_page_001_rendered.png)

---

## Key Theoretical Contributions

### 1. Neural Tangent Kernel and Output-Space Framing

The paper's starting point is the **empirical tangent kernel** on the training set $S$:

$$K_{SS}(w) = J_S(w) J_S(w)^\top$$

where $J_S(w) \in \mathbb{R}^{n \times p}$ is the Jacobian of training outputs with respect to the parameter vector $w \in \mathbb{R}^p$, and $n$ is the number of training samples.

Most previous work fixed $K_{SS}$ at initialization and analyzed it as a static kernel. The key novelty here is that the authors integrate the kernel **over the realized optimization trajectory** from step $s$ to step $T$:

$$W_S(s, T) = I - \mathcal{T}\exp\!\left(-\int_s^T K_{SS}(w(t))\,dt\right)$$

They call $W_S(s, T)$ the **cumulative dissipation operator**. This object records where training actually spent effort reducing loss, accumulating evidence over the entire path rather than a single snapshot. It is well-defined even when the kernel drifts substantially.

### 2. Signal Channel and Reservoir

The central structural result is a clean partition of output space into two subspaces defined by $W_S(s, T)$:

- **Signal channel:** the range of $W_S(s, T)$. Directions in which training dissipated loss and which can transfer to unseen test points.
- **Reservoir:** the kernel (null space) of $W_S(s, T)$. Directions in which residual fitting error accumulates but which test predictions cannot access.

The key theorem is **reservoir invisibility**: for any test set $Q$ and any parameter trajectory, the error component in the reservoir direction satisfies

$$\Pi_{\ker(W_S)}\, U_Q(T) = \Pi_{\ker(W_S)}\, U_Q(s)$$

Test predictions never move in reservoir directions regardless of how much training error is trapped there. This gives the paper's mechanistic explanation for benign overfitting: the network can fit training noise in reservoir coordinates that are literally invisible to held-out evaluation.

Visually, this is illustrated by the output-space dynamics figure:

![Output-space dynamics page 5](../extracted/images/2605_01172v1_a_theory_of_generalization_in_deep_learning/2605_01172v1_a_theory_of_generalization_in_deep_learning_page_005_rendered.png)

### 3. Minibatch Drift-Diffusion Decomposition

The second major contribution analyzes how minibatch SGD processes signal versus memorization noise within the signal channel.

Each minibatch gradient can be decomposed as:

$$g_B = \mathbb{E}[g \mid w] + \xi_B$$

where the first term is the **conditional mean gradient** (aligned with population signal) and $\xi_B$ is **centered minibatch noise** (zero mean, batch-to-batch variance $\Sigma(w)$).

The paper shows that the two components accumulate at different rates over $T$ steps:

$$\|\text{accumulated mean}\| \propto T \cdot \|\mu\|, \quad \|\text{accumulated noise}\| \propto \sqrt{T} \cdot \|\sigma\|$$

The **signal-to-noise ratio in accumulated updates scales as** $\sqrt{T}$, improving with training length. Memorization pressure (the diffusive term) falls behind coherent signal as long as the signal is consistent across batches.

The drift-diffusion result is illustrated in the dynamics figure on page 6:

![Minibatch dynamics page 6](../extracted/images/2605_01172v1_a_theory_of_generalization_in_deep_learning/2605_01172v1_a_theory_of_generalization_in_deep_learning_page_006_rendered.png)

### 4. Train-Test Coupling under Feature Learning

The **train-test coupling theorem** under squared loss states that for test set $Q$:

$$U_Q(T) - U_Q(s) = A^*\bigl(U_S(T) - U_S(s)\bigr)$$

where $A^* = K_{QS}^{(0)} \bigl(K_{SS}^{(0)}\bigr)^{-1}$ is the optimal linear predictor from training to test outputs at initialization. Critically, this result holds along the **realized training path** even when the empirical kernel evolves by $O(1)$ in operator norm.

The paper reports empirical verification with kernel drift peaking around **4.8x** relative to initialization and ending around **2.4x**, well outside the lazy-training regime. The train-test correlation achieved is **0.991** with relative error **0.165**.

![Train-test coupling verification page 9](../extracted/images/2605_01172v1_a_theory_of_generalization_in_deep_learning/2605_01172v1_a_theory_of_generalization_in_deep_learning_page_009_rendered.png)

### 5. Population-Risk Objective and SNR Preconditioner

Using exchangeability and leave-one-out reasoning, the paper shows that the decrease in population risk per gradient step can be estimated as:

$$\Delta \hat{R}_{\text{pop}} \approx \sum_k \frac{\mu_k^2}{\mu_k^2 + \sigma_k^2 / (b-1)}$$

where $\mu_k$ and $\sigma_k^2$ are the per-parameter mean and variance of the minibatch gradient, and $b$ is the batch size.

This reduces to a **diagonal preconditioner** that promotes updates only when the estimated signal-to-noise ratio per parameter exceeds a threshold:

$$\text{promote update for parameter } k \iff \mu_k^2 > \frac{\sigma_k^2}{b - 1}$$

In practice this requires maintaining one extra EMA state vector alongside the standard Adam moments. The algorithm is described on pages 12-14:

![SNR preconditioner algorithm page 12](../extracted/images/2605_01172v1_a_theory_of_generalization_in_deep_learning/2605_01172v1_a_theory_of_generalization_in_deep_learning_page_012_rendered.png)

---

## Method Walkthrough

### Setup and Notation

Let $S = \{(x_i, y_i)\}_{i=1}^n$ be the training set, $f(x; w) \in \mathbb{R}$ the network output, and $U_S(w) = (f(x_1; w), \ldots, f(x_n; w))^\top \in \mathbb{R}^n$ the stacked training outputs.

The empirical NTK is $K_{SS}(w) = J_S(w) J_S(w)^\top$.

### Output-Space ODE

Under continuous gradient flow with squared loss $L = \frac{1}{2}\|U_S - y\|^2$, the residual $r(t) = U_S(t) - y$ evolves as:

$$\dot{r} = -K_{SS}(w(t))\, r(t)$$

The solution uses the time-ordered matrix exponential:

$$r(T) = \mathcal{T}\exp\!\left(-\int_s^T K_{SS}(w(t))\,dt\right) r(s) = (I - W_S(s,T))\, r(s)$$

### Spectral Decomposition

Performing an eigendecomposition of $W_S(s, T) = V \Lambda V^\top$ with $\Lambda = \text{diag}(\lambda_1, \ldots, \lambda_n)$:

- Eigenvectors with $\lambda_i \approx 1$: **signal channel** (training fully dissipated loss in these directions)
- Eigenvectors with $\lambda_i \approx 0$: **reservoir** (training did not touch these directions)

The test error decomposes as:

$$\mathcal{E}_{\text{test}} = \underbrace{\text{bias}^2}_{\text{signal not yet fit}} + \underbrace{\text{signal-channel variance}}_{\text{noise in learned directions}} + \underbrace{\text{reservoir term}}_{\to 0 \text{ at test}}$$

---

## Experimental Setup and Findings

### Experiment 1: Physics-Informed Neural Networks

**Setup:** Network trained to solve a PDE with a noisy initial condition. Standard Adam versus SNR-preconditioned variant. Metric: relative $L_2$ error.

**Finding:** SNR preconditioner reaches relative $L_2 \leq 0.40$ in **2.4x fewer iterations** than best-tuned AdamW.

![PINN results page 13](../extracted/images/2605_01172v1_a_theory_of_generalization_in_deep_learning/2605_01172v1_a_theory_of_generalization_in_deep_learning_page_013_rendered.png)

### Experiment 2: Grokking on Modular Division

**Setup:** Small transformer on modular division benchmark. Standard AdamW versus SNR preconditioner. Metric: held-out accuracy.

**Finding:** SNR preconditioner reaches **95% held-out accuracy at step 5,950** versus **29,450** for AdamW, roughly **4.9x faster**.

![Grokking results page 14](../extracted/images/2605_01172v1_a_theory_of_generalization_in_deep_learning/2605_01172v1_a_theory_of_generalization_in_deep_learning_page_014_rendered.png)

### Experiment 3: DPO Fine-Tuning under Noisy Preferences

**Setup:** DPO fine-tuning of Qwen2.5-0.5B-Instruct on a noisy preference dataset. Metric: reward accuracy and KL divergence from reference policy.

**Finding:** Reward accuracy improves from **0.566 to 0.641** while staying **3.05x closer** to the reference policy.

---

## Unifying Explanations for Deep Learning Phenomena

### Benign Overfitting

The network fits training noise in reservoir directions that do not affect test predictions. The generalization gap is not driven by the amount of noise fitted, but by where it lands in output space.

### Double Descent

As model capacity grows, more noise lands in the reservoir (test-invisible) rather than the signal channel. The interpolation peak occurs when added capacity is just barely enough to fit training data but not yet enough to push most noise into the reservoir.

### Implicit Bias

The spectral structure of $W_S$ acts as a smoothness schedule. High-eigenvalue directions are learned first (fast dissipation of loss), reproducing the observed low-complexity-first bias of gradient descent.

### Grokking

The model first memorizes training labels by updating both signal-channel and reservoir directions simultaneously. Over extended training, the coherent signal term (linear drift) continues to accumulate in the signal channel while the noise term (random walk) stagnates. The SNR preconditioner accelerates this by suppressing reservoir-directed updates.

Additional experiments appear in the appendix figures:

![Appendix experiments page 44](../extracted/images/2605_01172v1_a_theory_of_generalization_in_deep_learning/2605_01172v1_a_theory_of_generalization_in_deep_learning_page_044_rendered.png)

---

## Limitations and Open Questions

1. **Squared-loss exactness:** The train-test coupling theorem is stated most cleanly under squared loss. Extending to cross-entropy requires relaxing the constant Hessian assumption.
2. **Computational cost:** The full cumulative dissipation operator is expensive for large models. The diagonal SNR preconditioner is a tractable approximation that loses cross-parameter correlation information.
3. **Multi-epoch and correlated data:** The drift-diffusion argument relies on i.i.d. minibatch sampling and a replace-two stability condition, which weaken in multi-epoch training and correlated data streams.
4. **Scale validation:** Experiments cover a PINN, a small transformer, and a 0.5B language model. Large-scale pretraining evidence is still needed.
5. **Diagonal versus structured preconditioner:** Richer preconditioners might better approximate the full $W_S$ signal-channel projector but are computationally heavier.
6. **Non-constructive reservoir:** The theory proves the reservoir exists and is harmless but does not provide a practical algorithm to determine whether a specific fitted component resides in the signal channel or the reservoir.

---

## Why a Practitioner Should Care

1. **Principled story for safe overfitting.** The signal-versus-reservoir lens reframes model selection around output-space geometry: is noise landing in test-visible directions? This is a more actionable question than "is capacity too high?".

2. **Drop-in optimizer improvement for noisy training.** The SNR preconditioner requires one extra EMA state vector on top of Adam. For practitioners dealing with label noise, weak supervision, or noisy preferences, this is a low-cost experiment with reported 2-5x improvement in convergence speed.

3. **Diagnostic framework for memorization phases.** Tracking gradient mean and variance per parameter group gives a running signal-to-noise estimate. When SNR drops, the model is in a memorization phase, informing decisions about batch size, learning rate warmup, or data resampling without a separate validation set.

4. **Theoretical handle on grokking.** If your training curve shows a model that memorizes quickly but fails to generalize for hundreds of additional epochs, the framework predicts this and suggests remedies: larger batch size or the SNR gate both improve the signal accumulation rate.

5. **A template for theory-to-optimizer transfer.** The paper closes the loop from output-space theory to a practical training rule. The template (characterize geometry, derive population-risk objective, approximate with per-parameter statistic) is applicable to continual learning, federated learning, and other settings where training-time memorization is a concern.

---

## Key Equations Reference

| Quantity | Equation |
|---|---|
| Empirical NTK | $K_{SS}(w) = J_S(w) J_S(w)^\top$ |
| Cumulative dissipation | $W_S(s,T) = I - \mathcal{T}\exp(-\int_s^T K_{SS}(t)\,dt)$ |
| Reservoir invisibility | $\Pi_{\ker(W_S)} U_Q(T) = \Pi_{\ker(W_S)} U_Q(s)$ |
| Train-test coupling | $U_Q(T) - U_Q(s) = A^*(U_S(T) - U_S(s))$ |
| Population-risk estimate | $\Delta\hat{R}_\text{pop} \approx \sum_k \mu_k^2 / (\mu_k^2 + \sigma_k^2/(b-1))$ |
| SNR gate | promote update $k$ iff $\mu_k^2 > \sigma_k^2/(b-1)$ |
| Test error decomposition | $\mathcal{E}_\text{test} = \text{bias}^2 + \text{signal variance} + \text{reservoir} \approx \text{bias}^2 + \text{signal variance}$ |

---

## Connections to Prior Work

| Thread | How this paper connects |
|---|---|
| NTK / lazy training | Keeps NTK framing but escapes frozen-kernel assumption via path-integrated operators |
| Benign overfitting | Provides mechanism: reservoir directions are test-invisible |
| Double descent | Reservoir fraction grows with capacity, explaining second descent |
| Implicit bias | $W_S$ spectral ordering reproduces low-complexity-first learning |
| Grokking | Signal linear drift vs. noise random walk, with SNR gate as acceleration |
| Influence functions | Population-risk estimate is leave-one-out style but along realized trajectory |
| PAC-Bayes / stability | Supplements worst-case bounds with path-dependent, data-dependent quantities |

---

## Extracted Assets

Figures (53 total) are in:
`../extracted/images/2605_01172v1_a_theory_of_generalization_in_deep_learning/`

Key page renders referenced above:
- `page_001_rendered.png` -- paper overview / title page
- `page_005_rendered.png` -- output-space dynamics diagram
- `page_006_rendered.png` -- minibatch drift-diffusion illustration
- `page_008_figure_01_01.png` -- main conceptual figure
- `page_009_rendered.png` -- train-test coupling verification
- `page_012_rendered.png` -- SNR algorithm pseudocode
- `page_013_rendered.png` -- PINN experiment results
- `page_014_rendered.png` -- grokking experiment results
- `page_023_rendered.png` -- DPO experiment results
- `page_044_rendered.png` -- additional experiments (appendix)
