# SkillOpt: Complete Implementation Guide

**Official Microsoft Repository Integration**  
*From Paper to Production: A Practical Guide to Self-Evolving Agent Skills*

---

## 🚀 Quick Start: Get Running in 5 Minutes

### Installation (Option 1: PyPI - Recommended)

```bash
# Install the production-ready package
pip install skillopt

# With optional features
pip install skillopt[alfworld]    # ALFWorld benchmark support
pip install skillopt[webui]       # Gradio monitoring dashboard
pip install skillopt[claude]      # Claude model backend
```

### Installation (Option 2: From Source)

```bash
# Clone the official Microsoft repository
git clone https://github.com/microsoft/SkillOpt.git
cd SkillOpt
pip install -e .

# Optional: Install ALFWorld benchmark
pip install -e ".[alfworld]"
alfworld-download
```

---

## 🔑 Configuration & API Setup

### Azure OpenAI (Recommended by Microsoft)

```bash
# Copy the example environment file
cp .env.example .env

# Configure your credentials
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"

# Option 1: API key authentication
export AZURE_OPENAI_API_KEY="your-key-here"

# Option 2: Azure CLI authentication (no API key needed)
export AZURE_OPENAI_AUTH_MODE="azure_cli"
```

**Critical Note:** `AZURE_OPENAI_ENDPOINT` is **required** for all three auth modes (`api_key`, `azure_cli`, `openai_compatible`). Without it, all LLM calls will fail.

### OpenAI-Compatible Endpoints (Standard OpenAI)

```bash
export AZURE_OPENAI_ENDPOINT="https://api.openai.com/v1"
export AZURE_OPENAI_API_KEY="sk-..."
export AZURE_OPENAI_AUTH_MODE="openai_compatible"
```

**Note:** SkillOpt reuses the `AZURE_OPENAI_*` environment variable names even in this mode — there is no separate `OPENAI_API_KEY` variable.

### Anthropic Claude

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

### Qwen (Local vLLM)

```bash
export QWEN_CHAT_BASE_URL="http://localhost:8000/v1"
export QWEN_CHAT_MODEL="Qwen/Qwen3.5-4B"
```

For separate optimizer and target models on different vLLM instances:

```bash
python scripts/train.py \
    --config configs/searchqa/default.yaml \
    --optimizer_backend qwen_chat \
    --target_backend qwen_chat \
    --optimizer_model Qwen/Qwen3.5-4B \
    --target_model Qwen/Qwen3.5-4B \
    --optimizer_qwen_chat_base_url http://localhost:8001/v1 \
    --target_qwen_chat_base_url http://localhost:8000/v1
```

### MiniMax

```bash
export MINIMAX_BASE_URL="https://api.minimax.io/v1"
export MINIMAX_API_KEY="your-key"
export MINIMAX_MODEL="MiniMax-M2.7"
```

---

## 📊 Training Your First Skill

### Example 1: Train on SearchQA

```bash
python scripts/train.py \
    --config configs/searchqa/default.yaml \
    --split_dir /path/to/your/searchqa_split \
    --azure_openai_endpoint https://your-resource.openai.azure.com/ \
    --optimizer_model gpt-5.5 \
    --target_model gpt-5.5 \
    --num_epochs 4 \
    --batch_size 40 \
    --workers 8 \
    --out_root outputs/my_searchqa_run
```

### Example 2: Train on LiveMathematicianBench

```bash
python scripts/train.py \
    --config configs/livemathematicianbench/default.yaml \
    --split_dir /path/to/your/livemath_split \
    --azure_openai_endpoint https://your-resource.openai.azure.com/ \
    --optimizer_model gpt-5.5 \
    --target_model gpt-5.5
```

### Example 3: Train on ALFWorld (Embodied Agent)

```bash
python scripts/train.py \
    --config configs/alfworld/default.yaml \
    --split_dir data/alfworld_path_split \
    --azure_openai_endpoint https://your-resource.openai.azure.com/ \
    --optimizer_model gpt-5.5 \
    --target_model gpt-5.5
```

### Key Training Arguments

| Argument | Description | Example |
|----------|-------------|---------|
| `--config` | Benchmark configuration YAML | `configs/searchqa/default.yaml` |
| `--split_dir` | Path to data split directory | `/path/to/split` |
| `--azure_openai_endpoint` | Azure OpenAI endpoint URL | `https://your-resource.openai.azure.com/` |
| `--optimizer_model` | Optimizer model deployment name | `gpt-5.5` |
| `--target_model` | Target model deployment name | `gpt-5.5` |
| `--num_epochs` | Number of training epochs | `4` (default) |
| `--batch_size` | Batch size per step | `40` (default) |
| `--workers` | Parallel rollout workers | `8` |
| `--out_root` | Output directory | `outputs/my_run` |

---

## 🧪 Evaluation: Testing Skills Without Training

### Evaluate a Pre-trained Skill

```bash
# Evaluate the packaged GPT-5.5 SearchQA skill on test split
python scripts/eval_only.py \
  --config configs/searchqa/default.yaml \
  --skill ckpt/searchqa/gpt5.5_skill.md \
  --split valid_unseen \
  --split_dir /path/to/searchqa_split \
  --azure_openai_endpoint https://your-resource.openai.azure.com/
```

### Evaluate on All Data Splits

```bash
# Evaluate on train, validation, and test splits
python scripts/eval_only.py \
  --config configs/searchqa/default.yaml \
  --skill ckpt/searchqa/gpt5.5_skill.md \
  --split all \
  --split_dir /path/to/searchqa_split \
  --azure_openai_endpoint https://your-resource.openai.azure.com/
```

### Data Split Types

| Split | Description | Use Case |
|-------|-------------|----------|
| `valid_unseen` | Test set | Final evaluation, unseen data |
| `valid_seen` | Validation set | Hyperparameter tuning, model selection |
| `train` | Training set | Training examples |
| `all` | All splits combined | Comprehensive evaluation (default) |

---

## 📁 Understanding the Output Structure

After training, SkillOpt creates a structured output directory:

```
outputs/<run_name>/
├── config.json              # Flattened runtime configuration
├── history.json             # Per-step training history (losses, scores)
├── runtime_state.json       # Resume checkpoint (auto-resume support)
├── best_skill.md            # 🏆 BEST VALIDATED SKILL (deploy this!)
├── skills/
│   ├── skill_v0001.md      # Skill snapshot at step 1
│   ├── skill_v0002.md      # Skill snapshot at step 2
│   └── ...
├── steps/
│   ├── step_0001/          # Per-step artifacts
│   │   ├── patches/        # Proposed edits
│   │   └── evals/          # Evaluation results
│   └── ...
├── slow_update/
│   ├── epoch_01/           # Slow update logs for epoch 1
│   └── ...
└── meta_skill/
    ├── epoch_01/           # Meta skill logs for epoch 1
    └── ...
```

### Key Files to Know

- **`best_skill.md`** — Deploy this file! It's the validated, optimized skill ready for production.
- **`history.json`** — Track training progress: scores, accepted/rejected edits, validation metrics.
- **`runtime_state.json`** — Auto-resume checkpoint. Re-running the same command continues from here.

---

## 🎯 Pre-trained Skills: Skip Training and Evaluate Immediately

Microsoft provides pre-trained GPT-5.5 optimized skills in the `ckpt/` directory as reference artifacts:

```bash
# See available pre-trained skills
ls ckpt/

# Example structure:
ckpt/
├── searchqa/gpt5.5_skill.md
├── spreadsheetbench/gpt5.5_skill.md
├── livemathematicianbench/gpt5.5_skill.md
└── ...
```

These skills are ready to evaluate with `scripts/eval_only.py` on matching data splits without re-running training. See [`ckpt/README.md`](https://github.com/microsoft/SkillOpt/blob/main/ckpt/README.md) for the full per-benchmark command.

**Note:** This is the first artifact batch; Microsoft plans to upload remaining optimized skills and benchmark split manifests as they are cleaned and verified.

---

## 📦 Data Preparation: Format Your Own Datasets

### Directory Layout

SkillOpt expects data in a **split directory** with `train/`, `val/`, `test/` subdirectories:

```
data/my_split/
├── train/items.json
├── val/items.json
└── test/items.json
```

### JSON Format Example (SearchQA)

Each JSON file is an array of task items:

```json
[
  {
    "id": "unique_item_id_001",
    "question": "Who wrote the novel 1984?",
    "context": "[DOC] George Orwell was an English novelist...",
    "answers": ["George Orwell"]
  },
  {
    "id": "unique_item_id_002",
    "question": "What is the capital of France?",
    "context": "[DOC] Paris is the capital and most populous city of France...",
    "answers": ["Paris"]
  }
]
```

**Note:** Required fields depend on the benchmark. See `skillopt/envs/<benchmark>/dataloader.py` for the exact format each benchmark expects.

### Provided Dataset: SearchQA

Microsoft provides the exact SearchQA split used in the paper at:
```
data/searchqa_id_split/
├── train/items.json       # 400 training examples
├── val/items.json         # 200 validation examples
└── test/items.json        # 1400 test examples
```

---

## 🧩 Supported Benchmarks

| Benchmark | Type | Config | Description |
|-----------|------|--------|-------------|
| **SearchQA** | Question Answering | `configs/searchqa/default.yaml` | Document-based QA with search context |
| **ALFWorld** | Embodied Agent | `configs/alfworld/default.yaml` | Interactive household tasks |
| **DocVQA** | Document QA | `configs/docvqa/default.yaml` | Visual document question answering |
| **LiveMathematicianBench** | Math Reasoning | `configs/livemathematicianbench/default.yaml` | Advanced mathematics problems |
| **SpreadsheetBench** | Code Generation | `configs/spreadsheetbench/default.yaml` | Spreadsheet formula automation |
| **OfficeQA** | Tool-Augmented QA | `configs/officeqa/default.yaml` | Office document QA with tools |

---

## ⚙️ Advanced Configuration

### Default Settings (Paper Reproduction)

`configs/_base_/default.yaml` is the **single source of truth** for SkillOpt's runtime parameters. Default settings match the paper protocol:

- **Epochs:** 4
- **Rollout batch size:** 40
- **Reflection minibatch size:** 8
- **Textual learning rate:** 4 (with cosine decay)
- **Validation gating:** Strict hard validation
- **Slow update + meta skill:** Enabled

### Slow-Update Acceptance Mode

Controlled by `optimizer.slow_update_gate_with_selection`:

```yaml
optimizer:
  slow_update_gate_with_selection: false   # current main default
```

**Options:**

1. **`false` (current default)** — **Force-accept mode:** Slow-update guidance is injected into both `current_skill` and `best_skill` unconditionally at epoch boundary. This is the newer post-submission behavior.

2. **`true` (paper reproduction)** — **Gated mode:** Slow-update candidate is evaluated on the selection split and accepted only if it passes the same validation gate as a step-level edit. Use this to match the paper protocol and the provenance of provided `ckpt/` skills.

**Startup message:** The trainer prints which mode is active: `[slow update] acceptance=...`

### Gate Metric Selection

Controlled by `gate_metric`:

```yaml
optimizer:
  gate_metric: hard   # default
```

**Options:**

1. **`hard` (default, paper)** — Exact-match accuracy. Strictly greater than current score required.
   - **Use when:** You have a large selection split (>20 items) and discrete correctness.

2. **`soft`** — Per-item soft/partial-credit score.
   - **Use when:** Selection split is small (≤10 items) AND reward is continuous. The discrete hard gate often rejects every candidate in this scenario.

3. **`mixed`** — Weighted average: `(1 - w) * hard + w * soft`, where `w` is set by `gate_mixed_weight` (default `0.5`).
   - **Use when:** You want a balance between exact-match rigor and partial-credit flexibility.

### Optional Feature Configs

These are **NOT** default SkillOpt settings — they are optional feature configs contributed by users for specific scenarios. **The paper-reported numbers were obtained with default settings, not these.**

**Example: Soft Gate Config**

```bash
# Use soft gate (from PR #25 by @lvbaocheng)
# See configs/features/soft_gate.yaml for when to use
```

---

## 📈 Expected Performance Gains

### Paper Results Summary (GPT-5.5 on Direct Chat)

| Benchmark | No-Skill Accuracy | With SkillOpt | Gain |
|-----------|-------------------|---------------|------|
| **SearchQA** | 77.5% | 87.1% | **+9.6** |
| **SpreadsheetBench** | 41.8% | 80.7% | **+38.9** |
| **OfficeQA** | 33.1% | 72.1% | **+39.0** |
| **DocVQA** | 63.2% | 75.6% | **+12.4** |
| **LiveMathematicianBench** | 37.6% | 66.9% | **+29.3** |
| **ALFWorld** | 83.6% | 95.5% | **+11.9** |
| **Average Gain** | — | — | **+23.5** |

### Agentic Harness Results

| Harness | Average Gain (GPT-5.5) |
|---------|------------------------|
| **Direct Chat** | +23.5 points |
| **Codex CLI** | +24.8 points |
| **Claude Code CLI** | +19.1 points |

### Key Insight from Results

- **Best or tied-best on all 52 evaluated cells** (model × benchmark × harness combinations)
- **Compact skills:** 300–2,000 tokens (median ~920 tokens)
- **Zero inference-time overhead:** Optimizer runs offline; deployed artifact is just `best_skill.md`
- **Transferable:** Skills work across model scales, harnesses, and nearby benchmarks

---

## 🎨 WebUI: Gradio Monitoring Dashboard

### Installation

```bash
pip install -e ".[webui]"
```

### Launch the Dashboard

```bash
python -m skillopt_webui.app
```

### CLI Flags

| Flag | Default | Description |
|------|---------|-------------|
| `--port` | 7860 | Server port |
| `--host` | `0.0.0.0` | Bind address (accessible from all interfaces) |
| `--share` | off | Create a public Gradio share link |

### Example: Public Dashboard

```bash
# Launch dashboard accessible from any device on your network
python -m skillopt_webui.app --port 8080 --share
```

---

## 🔧 Extending SkillOpt

### Adding a New Backend

A **backend** is a chat/exec target (e.g., `openai_chat`, `claude_chat`, `qwen_chat`, `codex_exec`).

**Step-by-step:**

1. Create `skillopt/model/<name>_backend.py` module
2. Register it in `skillopt/model/common.py` + `backend_config.py`
3. Wire it through the router in `skillopt/model/__init__.py`

**Templates:** Use `qwen_backend.py` and `minimax_backend.py` as reference implementations.

**Full guide:** [`docs/guide/new-backend.md`](https://github.com/microsoft/SkillOpt/blob/main/docs/guide/new-backend.md)

### Adding a New Benchmark

A **benchmark** is a `skillopt/envs/<name>/` package containing:

- `dataloader.py` — Load and parse task items
- `rollout.py` — Execute tasks and collect trajectories
- `initial.md` — Seed skill document

**Simplest reference:** `skillopt/envs/searchqa/`

**Full guide:** [`docs/guide/new-benchmark.md`](https://github.com/microsoft/SkillOpt/blob/main/docs/guide/new-benchmark.md)

---

## 🚨 Common Issues & Troubleshooting

### Issue 1: "All LLM calls fail"

**Symptom:** All API calls fail immediately

**Fix:** Verify `AZURE_OPENAI_ENDPOINT` is set. This variable is **required** for all auth modes, even when using standard OpenAI.

```bash
# Verify it's set
echo $AZURE_OPENAI_ENDPOINT

# If empty, set it
export AZURE_OPENAI_ENDPOINT="https://api.openai.com/v1"  # for OpenAI
# OR
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"  # for Azure
```

### Issue 2: "Validation gate rejects every candidate"

**Symptom:** Training runs but no edits are accepted

**Diagnosis:** This usually happens when:
- Selection split is too small (< 10 items)
- Reward function is noisy or continuous
- Hard gate is too strict for your dataset

**Fix:** Switch to soft or mixed gate metric:

```yaml
# In your config file or via CLI
optimizer:
  gate_metric: soft
  # OR
  gate_metric: mixed
  gate_mixed_weight: 0.5
```

### Issue 3: "Paper results don't reproduce"

**Symptom:** Your results differ from paper-reported numbers

**Fix:** Ensure you're using paper-aligned settings:

```yaml
optimizer:
  slow_update_gate_with_selection: true   # Paper protocol (gated)
  gate_metric: hard                       # Paper default
```

### Issue 4: "Auto-resume not working"

**Symptom:** Re-running training starts from scratch

**Check:** Verify `runtime_state.json` exists in the output directory:

```bash
ls outputs/my_run/runtime_state.json
```

If it's missing, the previous run didn't complete successfully. Check logs for errors.

---

## 📚 Additional Resources

### Official Links

- **Project Page:** [https://microsoft.github.io/SkillOpt/](https://microsoft.github.io/SkillOpt/)
- **Paper (arXiv):** [https://arxiv.org/abs/2605.23904](https://arxiv.org/abs/2605.23904)
- **GitHub Repository:** [https://github.com/microsoft/SkillOpt](https://github.com/microsoft/SkillOpt)
- **PyPI Package:** [https://pypi.org/project/skillopt/](https://pypi.org/project/skillopt/)
- **Demo Video:** [https://youtu.be/JUBMDTCiM0M](https://youtu.be/JUBMDTCiM0M)

### Documentation

- **Backend Guide:** [`docs/guide/new-backend.md`](https://github.com/microsoft/SkillOpt/blob/main/docs/guide/new-backend.md)
- **Benchmark Guide:** [`docs/guide/new-benchmark.md`](https://github.com/microsoft/SkillOpt/blob/main/docs/guide/new-benchmark.md)
- **Pre-trained Skills:** [`ckpt/README.md`](https://github.com/microsoft/SkillOpt/blob/main/ckpt/README.md)

---

## 🎓 Citation

If you use SkillOpt in your research, please cite:

```bibtex
@misc{yang2026skilloptexecutivestrategyselfevolving,
      title={SkillOpt: Executive Strategy for Self-Evolving Agent Skills}, 
      author={Yifan Yang and Ziyang Gong and Weiquan Huang and Qihao Yang and Ziwei Zhou and Zisu Huang and Yan Li and Xuemei Gao and Qi Dai and Bei Liu and Kai Qiu and Yuqing Yang and Dongdong Chen and Xue Yang and Chong Luo},
      year={2026},
      eprint={2605.23904},
      archivePrefix={arXiv},
      primaryClass={cs.AI},
      url={https://arxiv.org/abs/2605.23904}
}
```

---

## 📝 License

MIT License

Copyright (c) Microsoft Corporation

See [`LICENSE`](https://github.com/microsoft/SkillOpt/blob/main/LICENSE) for full terms.

---

## 🌟 What Makes SkillOpt Special?

### 1. **Zero Inference-Time Cost**

The optimizer runs offline during training. At deployment, the target model only uses the compact `best_skill.md` file (300–2K tokens). No extra API calls, no latency overhead.

### 2. **Transferable Skills**

Skills optimized for one model (e.g., GPT-5.5) transfer to:
- Different model scales (GPT-5.4, GPT-5.4-mini)
- Different execution harnesses (Codex CLI → Claude Code CLI)
- Nearby benchmarks (SearchQA → related QA tasks)

### 3. **Reproducible & Principled**

Unlike ad-hoc prompt engineering or one-shot generation, SkillOpt applies deep-learning discipline:
- **Epochs & batches:** Structured training loop
- **Learning rate:** Bounded edit budget
- **Validation gating:** Held-out selection prevents overfitting
- **Memory mechanisms:** Slow update, meta skill, rejected-edit buffer

### 4. **Production-Ready**

- **Auto-resume:** Training picks up from last checkpoint
- **Monitoring:** Built-in WebUI dashboard
- **Multi-backend:** OpenAI, Azure, Claude, Qwen, MiniMax
- **Extensible:** Add your own backends and benchmarks

---

## 🚀 Next Steps

1. **Install:** `pip install skillopt`
2. **Configure:** Set your API credentials
3. **Train:** Run `python scripts/train.py --config configs/searchqa/default.yaml ...`
4. **Deploy:** Use the generated `best_skill.md` with your target model
5. **Monitor:** Launch the WebUI dashboard to track progress
6. **Extend:** Add custom backends/benchmarks for your domain

**Welcome to the future of self-evolving agent skills!** 🎉
