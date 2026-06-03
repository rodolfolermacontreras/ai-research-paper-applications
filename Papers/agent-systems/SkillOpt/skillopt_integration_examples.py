"""
SkillOpt Practical Integration Example
======================================

This script demonstrates how to integrate the official Microsoft SkillOpt
package into your own projects with practical, runnable examples.

Repository: https://github.com/microsoft/SkillOpt
PyPI: https://pypi.org/project/skillopt/
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Any


# =============================================================================
# SECTION 1: Installation Check & Setup
# =============================================================================

def check_installation():
    """Verify SkillOpt is installed and configured."""
    try:
        import skillopt
        print("✅ SkillOpt is installed!")
        print(f"   Version: {skillopt.__version__ if hasattr(skillopt, '__version__') else 'Unknown'}")
        return True
    except ImportError:
        print("❌ SkillOpt is NOT installed.")
        print("\nInstall with:")
        print("  pip install skillopt")
        print("\nOr from source:")
        print("  git clone https://github.com/microsoft/SkillOpt.git")
        print("  cd SkillOpt")
        print("  pip install -e .")
        return False


def check_environment_variables():
    """Check if required environment variables are set."""
    required_vars = {
        "AZURE_OPENAI_ENDPOINT": "Azure OpenAI endpoint URL",
        "AZURE_OPENAI_API_KEY": "Azure OpenAI API key (if using api_key mode)",
    }
    
    optional_vars = {
        "ANTHROPIC_API_KEY": "Anthropic Claude API key",
        "QWEN_CHAT_BASE_URL": "Qwen local vLLM base URL",
        "MINIMAX_API_KEY": "MiniMax API key",
    }
    
    print("\n🔍 Checking environment variables...")
    print("\nRequired (for Azure OpenAI):")
    for var, desc in required_vars.items():
        value = os.environ.get(var)
        if value:
            masked = f"{value[:8]}..." if len(value) > 8 else "***"
            print(f"  ✅ {var}: {masked}")
        else:
            print(f"  ❌ {var}: NOT SET ({desc})")
    
    print("\nOptional (for other backends):")
    for var, desc in optional_vars.items():
        value = os.environ.get(var)
        if value:
            masked = f"{value[:8]}..." if len(value) > 8 else "***"
            print(f"  ✅ {var}: {masked}")
        else:
            print(f"  ⚪ {var}: NOT SET ({desc})")


# =============================================================================
# SECTION 2: Data Preparation Examples
# =============================================================================

def create_sample_dataset(output_dir: str = "data/custom_qa_split"):
    """
    Create a sample dataset in SkillOpt's expected format.
    
    Directory structure:
        data/custom_qa_split/
        ├── train/items.json
        ├── val/items.json
        └── test/items.json
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Sample QA data
    train_data = [
        {
            "id": "train_001",
            "question": "What is the capital of France?",
            "context": "[DOC] Paris is the capital and most populous city of France.",
            "answers": ["Paris"]
        },
        {
            "id": "train_002",
            "question": "Who wrote Romeo and Juliet?",
            "context": "[DOC] William Shakespeare was an English playwright and poet.",
            "answers": ["William Shakespeare", "Shakespeare"]
        },
    ]
    
    val_data = [
        {
            "id": "val_001",
            "question": "What is the largest planet in our solar system?",
            "context": "[DOC] Jupiter is the largest planet in our solar system.",
            "answers": ["Jupiter"]
        },
    ]
    
    test_data = [
        {
            "id": "test_001",
            "question": "What is the speed of light?",
            "context": "[DOC] The speed of light in vacuum is 299,792,458 meters per second.",
            "answers": ["299,792,458 meters per second", "approximately 300,000 km/s"]
        },
        {
            "id": "test_002",
            "question": "Who painted the Mona Lisa?",
            "context": "[DOC] Leonardo da Vinci painted the Mona Lisa in the early 16th century.",
            "answers": ["Leonardo da Vinci", "da Vinci"]
        },
    ]
    
    # Write to files
    for split, data in [("train", train_data), ("val", val_data), ("test", test_data)]:
        split_dir = Path(output_dir) / split
        split_dir.mkdir(exist_ok=True)
        with open(split_dir / "items.json", "w") as f:
            json.dump(data, f, indent=2)
    
    print(f"\n✅ Created sample dataset at: {output_dir}")
    print(f"   - {len(train_data)} training examples")
    print(f"   - {len(val_data)} validation examples")
    print(f"   - {len(test_data)} test examples")
    
    return output_dir


# =============================================================================
# SECTION 3: Training Command Examples
# =============================================================================

def generate_training_commands(split_dir: str):
    """Generate example training commands for different scenarios."""
    
    commands = {
        "Basic SearchQA Training": f"""
python scripts/train.py \\
    --config configs/searchqa/default.yaml \\
    --split_dir {split_dir} \\
    --azure_openai_endpoint https://your-resource.openai.azure.com/ \\
    --optimizer_model gpt-5.5 \\
    --target_model gpt-5.5
""",
        
        "Custom Hyperparameters": f"""
python scripts/train.py \\
    --config configs/searchqa/default.yaml \\
    --split_dir {split_dir} \\
    --azure_openai_endpoint https://your-resource.openai.azure.com/ \\
    --optimizer_model gpt-5.5 \\
    --target_model gpt-5.5 \\
    --num_epochs 6 \\
    --batch_size 50 \\
    --workers 12 \\
    --out_root outputs/custom_hyperparams
""",
        
        "Using Qwen (Local vLLM)": f"""
python scripts/train.py \\
    --config configs/searchqa/default.yaml \\
    --split_dir {split_dir} \\
    --optimizer_backend qwen_chat \\
    --target_backend qwen_chat \\
    --optimizer_model Qwen/Qwen3.5-4B \\
    --target_model Qwen/Qwen3.5-4B \\
    --optimizer_qwen_chat_base_url http://localhost:8001/v1 \\
    --target_qwen_chat_base_url http://localhost:8000/v1
""",
        
        "Using Claude": f"""
python scripts/train.py \\
    --config configs/searchqa/default.yaml \\
    --split_dir {split_dir} \\
    --optimizer_backend claude_chat \\
    --target_backend claude_chat \\
    --optimizer_model claude-opus-4 \\
    --target_model claude-haiku-3
""",
        
        "Paper Reproduction (Gated Slow Update)": f"""
python scripts/train.py \\
    --config configs/searchqa/default.yaml \\
    --split_dir {split_dir} \\
    --azure_openai_endpoint https://your-resource.openai.azure.com/ \\
    --optimizer_model gpt-5.5 \\
    --target_model gpt-5.5 \\
    --config_override 'optimizer.slow_update_gate_with_selection: true'
""",
    }
    
    print("\n📋 Example Training Commands:")
    print("=" * 80)
    for name, cmd in commands.items():
        print(f"\n## {name}")
        print(cmd.strip())
        print()


# =============================================================================
# SECTION 4: Evaluation Command Examples
# =============================================================================

def generate_evaluation_commands():
    """Generate example evaluation commands."""
    
    commands = {
        "Evaluate Pre-trained Skill (Test Split)": """
python scripts/eval_only.py \\
  --config configs/searchqa/default.yaml \\
  --skill ckpt/searchqa/gpt5.5_skill.md \\
  --split valid_unseen \\
  --split_dir /path/to/searchqa_split \\
  --azure_openai_endpoint https://your-resource.openai.azure.com/
""",
        
        "Evaluate on All Splits": """
python scripts/eval_only.py \\
  --config configs/searchqa/default.yaml \\
  --skill ckpt/searchqa/gpt5.5_skill.md \\
  --split all \\
  --split_dir /path/to/searchqa_split \\
  --azure_openai_endpoint https://your-resource.openai.azure.com/
""",
        
        "Evaluate Custom Trained Skill": """
python scripts/eval_only.py \\
  --config configs/searchqa/default.yaml \\
  --skill outputs/my_run/best_skill.md \\
  --split valid_unseen \\
  --split_dir /path/to/searchqa_split \\
  --azure_openai_endpoint https://your-resource.openai.azure.com/
""",
    }
    
    print("\n📊 Example Evaluation Commands:")
    print("=" * 80)
    for name, cmd in commands.items():
        print(f"\n## {name}")
        print(cmd.strip())
        print()


# =============================================================================
# SECTION 5: WebUI Dashboard Examples
# =============================================================================

def generate_webui_commands():
    """Generate WebUI dashboard launch commands."""
    
    commands = {
        "Basic Launch": """
pip install -e ".[webui]"
python -m skillopt_webui.app
""",
        
        "Custom Port": """
python -m skillopt_webui.app --port 8080
""",
        
        "Public Share Link": """
python -m skillopt_webui.app --share
""",
        
        "Production Setup": """
python -m skillopt_webui.app --host 0.0.0.0 --port 7860
""",
    }
    
    print("\n🎨 WebUI Dashboard Commands:")
    print("=" * 80)
    for name, cmd in commands.items():
        print(f"\n## {name}")
        print(cmd.strip())
        print()


# =============================================================================
# SECTION 6: Integration with Your Own Code
# =============================================================================

def example_skill_usage():
    """
    Example of how to use a trained skill in your own Python code.
    """
    
    code_example = '''
# Example: Load and use a trained skill programmatically

def load_skill(skill_path: str) -> str:
    """Load a trained skill document."""
    with open(skill_path, "r") as f:
        return f.read()

def apply_skill_to_query(skill: str, query: str, context: str) -> str:
    """Apply a skill to a query using an LLM."""
    import openai
    
    # Inject the skill into the system prompt
    system_prompt = f"""You are a helpful assistant with specialized expertise.

SKILL DOCUMENT:
{skill}

Use the above skill to guide your responses."""
    
    # Call the LLM
    client = openai.AzureOpenAI(
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
        api_version="2024-08-01-preview",
    )
    
    response = client.chat.completions.create(
        model="gpt-5.5",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Context: {context}\\n\\nQuestion: {query}"}
        ],
        temperature=0.0,
    )
    
    return response.choices[0].message.content

# Usage
skill = load_skill("outputs/my_run/best_skill.md")
answer = apply_skill_to_query(
    skill=skill,
    query="What is the capital of France?",
    context="[DOC] Paris is the capital and most populous city of France."
)
print(f"Answer: {answer}")
'''
    
    print("\n🔧 Integration Example:")
    print("=" * 80)
    print(code_example)


# =============================================================================
# SECTION 7: Configuration Examples
# =============================================================================

def example_config_customization():
    """Show how to customize SkillOpt configuration."""
    
    config_examples = {
        "Soft Gate Config (configs/features/soft_gate.yaml)": """
# Use soft validation gate for small validation splits
optimizer:
  gate_metric: soft

# This replaces the default hard exact-match gate with
# a soft partial-credit scoring system.
# 
# When to use:
# - Selection split is small (≤10 items)
# - Reward is continuous (not binary correct/incorrect)
# - Hard gate rejects every candidate
""",
        
        "Mixed Gate Config": """
# Balanced hard + soft gate
optimizer:
  gate_metric: mixed
  gate_mixed_weight: 0.5

# Weighted average: (1 - 0.5) * hard + 0.5 * soft
# Adjust gate_mixed_weight to tune the balance.
""",
        
        "Paper Reproduction Config": """
# Match the exact paper protocol
optimizer:
  slow_update_gate_with_selection: true  # Gated slow update
  gate_metric: hard                       # Exact-match accuracy
  
# This ensures your results match the paper-reported numbers.
""",
        
        "Aggressive Training Config": """
# More epochs, larger batches, more workers
training:
  num_epochs: 8
  batch_size: 60
  workers: 16

optimizer:
  edit_budget_initial: 6  # Higher learning rate
  edit_budget_floor: 2
""",
    }
    
    print("\n⚙️ Configuration Customization Examples:")
    print("=" * 80)
    for name, config in config_examples.items():
        print(f"\n## {name}")
        print(config.strip())
        print()


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    """Run all examples and checks."""
    print("=" * 80)
    print("SkillOpt Practical Integration Examples")
    print("=" * 80)
    
    # 1. Check installation
    if not check_installation():
        print("\n⚠️  Install SkillOpt first, then re-run this script.")
        return
    
    # 2. Check environment
    check_environment_variables()
    
    # 3. Create sample dataset
    split_dir = create_sample_dataset()
    
    # 4. Show training commands
    generate_training_commands(split_dir)
    
    # 5. Show evaluation commands
    generate_evaluation_commands()
    
    # 6. Show WebUI commands
    generate_webui_commands()
    
    # 7. Show integration example
    example_skill_usage()
    
    # 8. Show config customization
    example_config_customization()
    
    print("\n" + "=" * 80)
    print("✅ All examples generated successfully!")
    print("=" * 80)
    print("\n📚 Next Steps:")
    print("  1. Configure your API credentials (see environment variables above)")
    print("  2. Prepare your dataset (see sample dataset created)")
    print("  3. Run training (copy a command from the examples above)")
    print("  4. Evaluate results (copy an evaluation command)")
    print("  5. Deploy the best_skill.md to production")
    print("\n🔗 Resources:")
    print("  - GitHub: https://github.com/microsoft/SkillOpt")
    print("  - Paper: https://arxiv.org/abs/2605.23904")
    print("  - PyPI: https://pypi.org/project/skillopt/")
    print("  - Project Page: https://microsoft.github.io/SkillOpt/")
    print()


if __name__ == "__main__":
    main()
