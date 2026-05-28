# A Theory of Generalization in Deep Learning

## Title and Authors

**Title:** A Theory of Generalization in Deep Learning  
**Authors:** Elon Litman, Gabe Guo  
**Affiliation:** Stanford University  
**Paper type:** arXiv preprint, May 2026

## Abstract

> We present a non-asymptotic theory of generalization in deep learning where the empirical neural tangent kernel partitions the output space. In directions corresponding to signal, error dissipates rapidly; in the vast orthogonal dimensions corresponding to noise, the kernel’s near-zero eigenvalues trap residual error in a test-invisible reservoir. Within the signal channel, minibatch SGD ensures that coherent population signal accumulates via fast linear drift, while idiosyncratic memorization is suppressed into a slow, diffusive random walk. We prove generalization survives even when the kernel evolves O(1) in operator norm, the full feature-learning regime. This theory naturally explains disparate phenomena in deep learning theory, such as benign overfitting, double descent, implicit bias, and grokking. Lastly, we derive an exact population-risk objective from a single training run with no validation data, for any architecture, loss, or optimizer, and prove that it measures precisely the noise in the signal channel. This objective reduces in practice to an SNR preconditioner on top of Adam, adding one state vector at no extra cost; it accelerates grokking by 5×, suppresses memorization in PINNs and implicit neural representations, and improves DPO fine-tuning under noisy preferences while staying 3× closer to the reference policy.

## Key Contributions

- Proposes a non-asymptotic generalization theory that works in the **full feature-learning regime**, not just the lazy or frozen-NTK regime.
- Introduces a clean geometric split of training dynamics into a **signal channel** and a **reservoir** using the cumulative empirical tangent kernel.
- Shows that errors trapped in the reservoir are **invisible to test predictions**, which gives a concrete explanation for why networks can memorize noise without necessarily hurting generalization.
- Proves a **drift-versus-diffusion** story for minibatch SGD: true population signal accumulates coherently, while memorization noise behaves more like a random walk and grows much more slowly.
- Derives an **exact train-test coupling result** under squared loss along the realized training path, even when the kernel changes substantially during training.
- Turns the theory into a practical **population-risk objective** that can be estimated from one training run with no validation set.
- Shows this objective reduces to a simple **SNR-style per-parameter gate** on top of Adam/AdamW.
- Uses the framework to unify several major phenomena: **benign overfitting, double descent, implicit bias, and grokking**.

## Core Concepts Explained

The paper’s core claim is that deep nets generalize because training does not treat all output directions equally. Some directions correspond to reusable structure in the data; others correspond to sample-specific junk. The empirical neural tangent kernel tells us which directions the optimizer can actually move along during the trajectory.

The authors integrate that kernel over time and call the result the **cumulative dissipation operator**. This operator partitions output space into two parts:

- **Signal channel:** directions where training actually dissipated loss in a way that can transfer to test examples.
- **Reservoir:** directions where residual fitting can remain, but that do not couple to test predictions.

A useful engineering interpretation is this: the network can overfit the training set in some coordinates that never matter for out-of-sample behavior. That is the paper’s explanation for why interpolation is not automatically fatal.

The second big idea is about SGD noise. In minibatch training, the average gradient contains a coherent component and a noisy component. The paper argues that:

- the coherent part aligned with population signal builds up **linearly over training time**, while
- the noisy part behaves diffusively, more like accumulated variance than directed progress.

So even inside the signal channel, useful structure wins over memorization if training is allowed to integrate enough consistent signal.

The third big idea is that **training motion predicts test motion**. Under squared loss, the paper shows that once you look through the right operator, the change in test predictions is determined exactly by the change in training predictions along the actual path taken by optimization. This is important because many NTK-style arguments become fragile once features move a lot. Here, the authors claim the coupling still works even when the empirical kernel drifts by O(1), which is meant to cover realistic deep learning rather than just infinitely wide lazy training.

Finally, they convert the theory into an optimizer rule. Instead of updating every parameter equally according to empirical risk, they propose updating parameters only when the **squared mean gradient** is larger than a minibatch-noise threshold. In plain terms: if a parameter’s update looks like stable signal rather than batch noise, keep it; otherwise suppress it.

## Methodology

The paper combines theory and experiments.

On the theory side, it works in **output space** rather than parameter space. The setup defines stacked train outputs, their Jacobian with respect to parameters, and the empirical tangent kernel:

```text
K_SS(w) = J_S(w) J_S(w)^T
```

From the evolving kernel along training, the authors define a time-integrated operator `W_S(s, T)` that measures how much loss was actually dissipated along each output direction. They then analyze:

1. **Reservoir invisibility:** prove that directions in `ker(W_S)` do not affect any test prediction through the test-transfer operator.
2. **SGD drift-diffusion separation:** decompose minibatch gradients into conditional mean plus centered noise, then show the mean accumulates faster than diffusion on true signal directions.
3. **Train-test coupling:** show that, for squared loss, train displacement and test displacement factor through the same dissipation geometry, yielding an exact predictor of test motion from training motion.
4. **Population-risk estimation:** use exchangeability and leave-one-out style reasoning to derive an unbiased first-order estimate of population-risk decrease from a training batch.
5. **Optimizer design:** collapse that estimate into a parameter-space objective and derive a diagonal rule that becomes a gated Adam/AdamW update.

On the empirical side, they test the resulting update rule in three settings chosen because memorization and delayed generalization are known problems:

- a noisy-initial-condition **physics-informed neural network (PINN)**,
- **grokking** on modular division with a small transformer,
- **DPO fine-tuning** of Qwen2.5-0.5B-Instruct under noisy preference labels.

The comparisons keep architecture and most hyperparameters fixed, changing only the update rule.

## Key Results and Findings

The paper makes both conceptual and empirical claims.

First, it claims that the generalization gap can be decomposed into a small number of interpretable pieces. The important practical takeaway is that **noise in the reservoir does not hurt test performance**, while **noise in the signal channel is the main thing to fight**. This is the paper’s unified explanation for several otherwise disconnected phenomena.

Second, the paper reports strong evidence for train-test coupling under feature learning. In one figure, the predicted test motion from observed training motion reaches **correlation 0.991** with **relative error 0.165**, even though the empirical tangent kernel drifts far from its initialization. They report kernel drift peaking around **4.8×** and ending around **2.4×**, which they use to argue the result is well outside the lazy-training regime.

Third, the optimizer derived from the theory appears useful in practice:

- **PINN with noisy initial condition:** reaches relative `L2 <= 0.40` in **2.4× fewer iterations** than the best tuned AdamW baseline.
- **Grokking on modular division:** reaches **95% held-out accuracy at step 5,950** vs **29,450** for AdamW, about **4.9× faster**.
- **Noisy DPO fine-tuning:** improves reward accuracy from **0.566 to 0.641** while staying about **3.05× closer** to the reference policy in reward drift.

These results matter because they are not just accuracy improvements; they target a recurring engineering pain point: models fitting noisy or shortcut-like structure before they learn the intended rule.

## Practical Applications

For ML engineers, the paper is most useful as a way to reason about **which gradients are likely to transfer** and which are just memorization.

Potential applications include:

- **Noisy-label training:** the SNR-style gate could help when training data contains annotation noise, weak supervision, or synthetic labels.
- **Preference optimization and RLHF-style tuning:** the DPO result suggests the method may reduce overreaction to noisy preferences while preserving closeness to a base model.
- **Physics-informed models and implicit neural representations:** useful when the training signal contains structured noise or stiff optimization dynamics.
- **Grokking-like problems:** tasks where models memorize first and generalize later may benefit from suppressing parameter updates dominated by variance.
- **Adaptive optimizers:** the proposed rule is easy to interpret as a drop-in modification to Adam/AdamW using one extra state vector.
- **Debugging overfitting:** the signal-channel versus reservoir lens gives a more actionable story than generic “capacity is too high.” It suggests the real issue is whether harmful noise is landing in test-visible directions.

A practical mental model is: if you already use Adam, gradient clipping, EMA statistics, and batch-based heuristics, this paper gives a theory-backed way to turn those ideas into a **population-risk-aware update filter**.

## Limitations and Future Work

The paper is ambitious, but there are clear boundaries.

- Some of the cleanest results, especially the exact train-test coupling, are stated under **squared loss** or constant output Hessian assumptions. Extending the same exactness to modern cross-entropy training is less direct.
- The analysis assumes the network output is **twice differentiable** in the parameters and uses path-dependent operator constructions that may be expensive to estimate exactly in large production models.
- Parts of the SGD argument rely on **i.i.d. sampling, exchangeability, minibatch independence**, or a **replace-two stability** condition. Those assumptions may weaken in multi-epoch reuse, curriculum learning, or highly correlated data streams.
- The optimizer result is first-order and is presented mainly for a **diagonal preconditioner**, which is practical but leaves open whether richer structured preconditioners could work better.
- The experiments are promising but still relatively narrow: one PINN setup, one grokking benchmark, and one small-model DPO case. More large-scale supervised and language-model pretraining evidence would make the claims stronger.
- The theory explains when memorization can be harmless, but it does not remove the need for standard engineering controls like good data curation, robust evaluation, and validation on real downstream tasks.

Natural future directions include extending the population-risk update to larger LLM fine-tuning stacks, testing it on noisy web-scale supervision, and turning the signal-channel diagnostics into tools for training monitoring.

## Key Equations/Algorithms

The most important objects are easy to summarize in plain language.

```text
K_SS(w) = J_S(w) J_S(w)^T
```

This is the empirical tangent kernel on the training set. It tells you which output directions are reachable from the current parameters.

```text
W_S(s, T) = integral over time of propagated K_SS
```

This is the cumulative dissipation operator. It measures where training actually spent effort reducing loss over the whole trajectory. Its range is the signal channel; its kernel is the reservoir.

```text
U_Q(T) - U_Q(s) = -G_Q(T, s) g(s)
```

This links the current output gradient to how test predictions move over a training window.

```text
U_Q(T) - U_Q(s) = A* ( U_S(T) - U_S(s) )
```

Under squared loss, this is the train-test coupling result. Test movement can be predicted from training movement using the optimal linear operator `A*` along the realized path.

```text
test error = bias + signal-channel variance + reservoir term
```

The key simplification is that the reservoir term vanishes at test, so the remaining danger is noise that survives in the signal channel.

```text
update parameter k only if  mu_k^2 > sigma_k^2 / (b - 1)
```

This is the actionable optimizer rule. `mu_k` is the minibatch mean gradient for parameter `k`, `sigma_k^2` is its minibatch variance, and `b` is batch size. Intuitively, only update when signal beats noise.

For engineers, that rule is the paper’s main algorithmic output.

## Connections to Other Work

This paper sits at the intersection of several major threads in ML theory.

- **NTK and lazy training:** it keeps the NTK viewpoint but tries to escape the unrealistic frozen-kernel assumption. The key claim is that the right output-space operators remain useful even when features move substantially.
- **Benign overfitting and double descent:** the paper provides a mechanism for why interpolation can still generalize: some fitted noise ends up in test-invisible directions.
- **Implicit bias:** the spectral structure of the cumulative dissipation operator acts like a schedule for which directions get learned first.
- **Grokking:** the paper interprets grokking as signal gradually migrating from the reservoir into the signal channel as the kernel evolves.
- **Influence functions and leave-one-out:** the population-risk objective is closely related to influence estimation, but framed along the realized training path rather than as a local Hessian approximation at the end of training.
- **Classical generalization theory:** it positions itself as an alternative to loose worst-case uniform-convergence, stability, and PAC-Bayes stories by using path-dependent, data-dependent output-space quantities.

In the broader landscape, the paper is trying to do something valuable: bridge theory and optimizer design. Instead of stopping at an explanation of why deep nets might generalize, it produces a concrete training rule. Whether every theorem survives broader empirical stress tests remains to be seen, but the paper is notable because it gives practitioners a usable conceptual model:

- some fitted directions transfer,
- some do not,
- SGD already helps separate them,
- and the optimizer can be nudged to prefer the transferable ones.

That makes the work especially relevant for engineers dealing with noisy data, overparameterized models, and fine-tuning regimes where memorization is cheap but robust generalization is hard.
