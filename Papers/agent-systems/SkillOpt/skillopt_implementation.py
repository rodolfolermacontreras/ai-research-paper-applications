#!/usr/bin/env python3
"""
SkillOpt: Practical Implementation Example
==========================================

This module demonstrates how to implement the core SkillOpt algorithm for
text-space optimization of agent skills.

Based on: arXiv:2605.23904v2 "SkillOpt: Executive Strategy for Self-Evolving Agent Skills"

Author: AI Research Papers Project
Date: 2026-06-02
"""

import json
import re
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Callable
from enum import Enum
import hashlib


class EditType(Enum):
    """Types of skill document edits."""
    APPEND = "APPEND"
    INSERT_AFTER = "INSERT_AFTER"
    REPLACE = "REPLACE"
    DELETE = "DELETE"


@dataclass
class Edit:
    """Represents a single edit operation on a skill document."""
    edit_type: EditType
    content: str
    anchor: Optional[str] = None  # For INSERT_AFTER and REPLACE
    target: Optional[str] = None  # For REPLACE and DELETE
    score: float = 0.0  # Impact score for ranking
    
    def __hash__(self):
        """Hash for deduplication."""
        return hash((self.edit_type, self.content, self.anchor, self.target))


@dataclass
class Trajectory:
    """Represents a single task execution trajectory."""
    task_id: str
    task_input: str
    agent_output: str
    success: bool
    score: float
    steps: List[Dict] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)


@dataclass
class SkillDocument:
    """Represents a skill document (the external trainable state)."""
    content: str
    version: int = 0
    validation_score: float = 0.0
    
    def hash(self) -> str:
        """Generate hash for caching/deduplication."""
        return hashlib.md5(self.content.encode()).hexdigest()
    
    def apply_edit(self, edit: Edit) -> 'SkillDocument':
        """Apply a single edit to create a new skill version."""
        new_content = self.content
        
        if edit.edit_type == EditType.APPEND:
            new_content = new_content + "\n\n" + edit.content
            
        elif edit.edit_type == EditType.INSERT_AFTER:
            if edit.anchor and edit.anchor in new_content:
                parts = new_content.split(edit.anchor, 1)
                new_content = parts[0] + edit.anchor + "\n\n" + edit.content + parts[1]
            
        elif edit.edit_type == EditType.REPLACE:
            if edit.target and edit.target in new_content:
                new_content = new_content.replace(edit.target, edit.content, 1)
            
        elif edit.edit_type == EditType.DELETE:
            if edit.target and edit.target in new_content:
                new_content = new_content.replace(edit.target, "", 1)
        
        return SkillDocument(
            content=new_content.strip(),
            version=self.version + 1,
            validation_score=0.0
        )
    
    def apply_edits(self, edits: List[Edit]) -> 'SkillDocument':
        """Apply multiple edits sequentially."""
        skill = self
        for edit in edits:
            skill = skill.apply_edit(edit)
        return skill


class SkillOptimizer:
    """
    SkillOpt optimizer implementing text-space skill optimization.
    
    Key Features:
    - Rollout-based evidence gathering
    - Minibatch reflection for pattern detection
    - Bounded edit updates with learning rate schedule
    - Validation gating for quality control
    - Rejected-edit buffer for negative feedback
    - Slow/meta updates at epoch boundaries
    """
    
    def __init__(
        self,
        target_model: Callable,
        optimizer_model: Callable,
        rollout_batch_size: int = 40,
        reflection_minibatch_size: int = 8,
        edit_budget_initial: int = 4,
        edit_budget_floor: int = 2,
        edit_budget_schedule: str = "cosine",
        epochs: int = 4,
        slow_update_samples: int = 20,
        use_rejected_buffer: bool = True,
    ):
        """
        Initialize SkillOpt optimizer.
        
        Args:
            target_model: The frozen model being optimized (takes skill + task -> output)
            optimizer_model: The optimizer model (analyzes trajectories -> edits)
            rollout_batch_size: Number of tasks per rollout batch
            reflection_minibatch_size: Batch size for failure/success analysis
            edit_budget_initial: Starting edit budget (learning rate)
            edit_budget_floor: Minimum edit budget
            edit_budget_schedule: "cosine", "linear", or "constant"
            epochs: Number of optimization epochs
            slow_update_samples: Samples for epoch-boundary slow update
            use_rejected_buffer: Enable negative feedback from rejected edits
        """
        self.target_model = target_model
        self.optimizer_model = optimizer_model
        
        # Hyperparameters
        self.rollout_batch_size = rollout_batch_size
        self.reflection_minibatch_size = reflection_minibatch_size
        self.edit_budget_initial = edit_budget_initial
        self.edit_budget_floor = edit_budget_floor
        self.edit_budget_schedule = edit_budget_schedule
        self.epochs = epochs
        self.slow_update_samples = slow_update_samples
        self.use_rejected_buffer = use_rejected_buffer
        
        # State
        self.rejected_edits: List[Edit] = []
        self.optimization_history: List[Dict] = []
        self.skill_cache: Dict[str, float] = {}  # hash -> validation_score
        
    def compute_edit_budget(self, step: int, total_steps: int) -> int:
        """Compute edit budget for current step based on schedule."""
        if self.edit_budget_schedule == "constant":
            return self.edit_budget_initial
        
        elif self.edit_budget_schedule == "linear":
            progress = step / max(total_steps - 1, 1)
            budget = self.edit_budget_initial - (self.edit_budget_initial - self.edit_budget_floor) * progress
            return max(int(budget), self.edit_budget_floor)
        
        elif self.edit_budget_schedule == "cosine":
            import math
            progress = step / max(total_steps - 1, 1)
            budget = self.edit_budget_floor + (self.edit_budget_initial - self.edit_budget_floor) * (1 + math.cos(math.pi * progress)) / 2
            return max(int(budget), self.edit_budget_floor)
        
        return self.edit_budget_initial
    
    def execute_rollout(
        self,
        skill: SkillDocument,
        tasks: List[Dict],
        batch_size: int
    ) -> List[Trajectory]:
        """Execute rollout batch: run tasks with current skill."""
        trajectories = []
        
        for task in tasks[:batch_size]:
            # Execute task with target model using current skill
            result = self.target_model(skill.content, task)
            
            trajectory = Trajectory(
                task_id=task.get("id", ""),
                task_input=task.get("input", ""),
                agent_output=result.get("output", ""),
                success=result.get("success", False),
                score=result.get("score", 0.0),
                steps=result.get("steps", []),
                metadata=result.get("metadata", {}),
            )
            trajectories.append(trajectory)
        
        return trajectories
    
    def analyze_failures(
        self,
        failures: List[Trajectory],
        current_skill: SkillDocument,
        minibatch_size: int
    ) -> List[Edit]:
        """Analyze failure minibatches to propose corrective edits."""
        all_edits = []
        
        # Process in minibatches
        for i in range(0, len(failures), minibatch_size):
            minibatch = failures[i:i + minibatch_size]
            
            # Call optimizer model to analyze failures
            prompt = self._build_failure_analysis_prompt(minibatch, current_skill)
            response = self.optimizer_model(prompt)
            
            # Parse edits from response
            edits = self._parse_edits(response)
            all_edits.extend(edits)
        
        return all_edits
    
    def analyze_successes(
        self,
        successes: List[Trajectory],
        current_skill: SkillDocument,
        minibatch_size: int
    ) -> List[Edit]:
        """Analyze success minibatches to propose reinforcement edits."""
        all_edits = []
        
        # Process in minibatches
        for i in range(0, len(successes), minibatch_size):
            minibatch = successes[i:i + minibatch_size]
            
            # Call optimizer model to analyze successes
            prompt = self._build_success_analysis_prompt(minibatch, current_skill)
            response = self.optimizer_model(prompt)
            
            # Parse edits from response
            edits = self._parse_edits(response)
            all_edits.extend(edits)
        
        return all_edits
    
    def merge_and_rank_edits(
        self,
        failure_edits: List[Edit],
        success_edits: List[Edit],
        rejected_edits: List[Edit]
    ) -> List[Edit]:
        """
        Merge failure and success edits, deduplicate, and rank by impact.
        
        Failure edits are prioritized over success edits.
        Rejected edits are filtered out (negative feedback).
        """
        # Deduplicate
        unique_edits = list(set(failure_edits + success_edits))
        
        # Filter out rejected edits (negative feedback)
        if self.use_rejected_buffer:
            rejected_set = set(rejected_edits)
            unique_edits = [e for e in unique_edits if e not in rejected_set]
        
        # Rank by impact (failure edits get higher scores)
        for edit in unique_edits:
            if edit in failure_edits:
                edit.score += 2.0  # Prioritize corrective edits
            if edit in success_edits:
                edit.score += 1.0  # Reinforcement edits
        
        # Sort by score descending
        ranked_edits = sorted(unique_edits, key=lambda e: e.score, reverse=True)
        
        return ranked_edits
    
    def evaluate_skill(
        self,
        skill: SkillDocument,
        validation_tasks: List[Dict]
    ) -> float:
        """Evaluate skill on validation set."""
        # Check cache
        skill_hash = skill.hash()
        if skill_hash in self.skill_cache:
            return self.skill_cache[skill_hash]
        
        # Execute on validation set
        trajectories = self.execute_rollout(skill, validation_tasks, len(validation_tasks))
        
        # Compute score (e.g., accuracy or mean score)
        scores = [t.score for t in trajectories]
        avg_score = sum(scores) / len(scores) if scores else 0.0
        
        # Cache result
        self.skill_cache[skill_hash] = avg_score
        
        return avg_score
    
    def slow_update(
        self,
        prev_skill: SkillDocument,
        current_skill: SkillDocument,
        tasks: List[Dict]
    ) -> Optional[Edit]:
        """
        Epoch-boundary slow update: compare same tasks under prev vs current skill.
        
        Generates longitudinal guidance that captures durable patterns.
        """
        sample_tasks = tasks[:self.slow_update_samples]
        
        # Execute with both skills
        prev_trajectories = self.execute_rollout(prev_skill, sample_tasks, len(sample_tasks))
        current_trajectories = self.execute_rollout(current_skill, sample_tasks, len(sample_tasks))
        
        # Call optimizer to synthesize longitudinal insights
        prompt = self._build_slow_update_prompt(
            prev_skill, current_skill,
            prev_trajectories, current_trajectories
        )
        response = self.optimizer_model(prompt)
        
        # Parse edit (typically APPEND to protected section)
        edits = self._parse_edits(response)
        return edits[0] if edits else None
    
    def optimize(
        self,
        initial_skill: SkillDocument,
        train_tasks: List[Dict],
        validation_tasks: List[Dict],
        test_tasks: Optional[List[Dict]] = None,
    ) -> Tuple[SkillDocument, List[Dict]]:
        """
        Run SkillOpt optimization loop.
        
        Args:
            initial_skill: Starting skill document
            train_tasks: Training tasks for rollouts
            validation_tasks: Validation tasks for selection gate
            test_tasks: Optional test tasks for final evaluation
        
        Returns:
            Tuple of (best_skill, optimization_history)
        """
        current_skill = initial_skill
        best_skill = initial_skill
        best_score = self.evaluate_skill(initial_skill, validation_tasks)
        
        print(f"Initial skill validation score: {best_score:.4f}")
        
        # Compute total steps for edit budget schedule
        steps_per_epoch = len(train_tasks) // self.rollout_batch_size
        total_steps = self.epochs * steps_per_epoch
        
        step_counter = 0
        
        for epoch in range(self.epochs):
            print(f"\n=== Epoch {epoch + 1}/{self.epochs} ===")
            epoch_start_skill = current_skill
            
            for batch_idx in range(0, len(train_tasks), self.rollout_batch_size):
                # 1. Forward Pass: Rollout Evidence
                batch_tasks = train_tasks[batch_idx:batch_idx + self.rollout_batch_size]
                trajectories = self.execute_rollout(current_skill, batch_tasks, len(batch_tasks))
                
                # Split into failures and successes
                failures = [t for t in trajectories if not t.success]
                successes = [t for t in trajectories if t.success]
                
                print(f"  Step {step_counter}: {len(failures)} failures, {len(successes)} successes")
                
                if not failures and not successes:
                    continue
                
                # 2. Backward Pass: Minibatch Reflection
                failure_edits = self.analyze_failures(
                    failures, current_skill, self.reflection_minibatch_size
                ) if failures else []
                
                success_edits = self.analyze_successes(
                    successes, current_skill, self.reflection_minibatch_size
                ) if successes else []
                
                # 3. Bounded Text Update
                merged_edits = self.merge_and_rank_edits(
                    failure_edits, success_edits, self.rejected_edits
                )
                
                edit_budget = self.compute_edit_budget(step_counter, total_steps)
                selected_edits = merged_edits[:edit_budget]
                
                print(f"  Edit budget: {edit_budget}, Proposed: {len(merged_edits)}, Selected: {len(selected_edits)}")
                
                if not selected_edits:
                    step_counter += 1
                    continue
                
                candidate_skill = current_skill.apply_edits(selected_edits)
                
                # 4. Validation Gate
                candidate_score = self.evaluate_skill(candidate_skill, validation_tasks)
                current_score = self.evaluate_skill(current_skill, validation_tasks)
                
                print(f"  Validation: Current={current_score:.4f}, Candidate={candidate_score:.4f}")
                
                if candidate_score > current_score:
                    # Accept
                    print(f"  ✓ ACCEPTED (improvement: +{candidate_score - current_score:.4f})")
                    current_skill = candidate_skill
                    
                    if candidate_score > best_score:
                        best_skill = candidate_skill
                        best_score = candidate_score
                        print(f"  ★ NEW BEST: {best_score:.4f}")
                    
                    # Log history
                    self.optimization_history.append({
                        "epoch": epoch,
                        "step": step_counter,
                        "edits_applied": len(selected_edits),
                        "validation_score": candidate_score,
                        "accepted": True,
                    })
                else:
                    # Reject and add to buffer
                    print(f"  ✗ REJECTED (no improvement)")
                    if self.use_rejected_buffer:
                        self.rejected_edits.extend(selected_edits)
                    
                    self.optimization_history.append({
                        "epoch": epoch,
                        "step": step_counter,
                        "edits_applied": 0,
                        "validation_score": current_score,
                        "accepted": False,
                    })
                
                step_counter += 1
            
            # 5. Epoch-wise Slow/Meta Update
            if epoch < self.epochs - 1:  # Not on last epoch
                slow_edit = self.slow_update(epoch_start_skill, current_skill, train_tasks)
                if slow_edit:
                    print(f"  Slow update: Adding longitudinal guidance")
                    current_skill = current_skill.apply_edit(slow_edit)
        
        print(f"\n=== Optimization Complete ===")
        print(f"Best validation score: {best_score:.4f}")
        print(f"Initial -> Final improvement: +{best_score - self.evaluate_skill(initial_skill, validation_tasks):.4f}")
        
        # Optional: Final test evaluation
        if test_tasks:
            test_score = self.evaluate_skill(best_skill, test_tasks)
            print(f"Test score: {test_score:.4f}")
        
        return best_skill, self.optimization_history
    
    # -------------------------------------------------------------------------
    # Helper Methods (Prompt Building & Parsing)
    # -------------------------------------------------------------------------
    
    def _build_failure_analysis_prompt(
        self,
        failures: List[Trajectory],
        skill: SkillDocument
    ) -> str:
        """Build prompt for failure analysis."""
        examples = "\n\n".join([
            f"Task: {t.task_input}\nOutput: {t.agent_output}\nScore: {t.score}"
            for t in failures
        ])
        
        return f"""Analyze these {len(failures)} failed task executions.

Current Skill:
{skill.content}

Failed Examples:
{examples}

Identify recurring failure patterns and propose 1-3 CORRECTIVE edits to the skill document.

Format each edit as:
EDIT_TYPE: [APPEND|INSERT_AFTER|REPLACE|DELETE]
CONTENT: [new text to add/replace with]
ANCHOR: [text after which to insert] (for INSERT_AFTER only)
TARGET: [exact text to replace/delete] (for REPLACE/DELETE only)
---
"""
    
    def _build_success_analysis_prompt(
        self,
        successes: List[Trajectory],
        skill: SkillDocument
    ) -> str:
        """Build prompt for success analysis."""
        examples = "\n\n".join([
            f"Task: {t.task_input}\nOutput: {t.agent_output}\nScore: {t.score}"
            for t in successes
        ])
        
        return f"""Analyze these {len(successes)} successful task executions.

Current Skill:
{skill.content}

Successful Examples:
{examples}

Identify what the agent is doing RIGHT and propose 1-2 REINFORCEMENT edits to emphasize these patterns.

Format each edit as:
EDIT_TYPE: [APPEND|INSERT_AFTER|REPLACE|DELETE]
CONTENT: [new text to add/replace with]
ANCHOR: [text after which to insert] (for INSERT_AFTER only)
TARGET: [exact text to replace/delete] (for REPLACE/DELETE only)
---
"""
    
    def _build_slow_update_prompt(
        self,
        prev_skill: SkillDocument,
        current_skill: SkillDocument,
        prev_trajectories: List[Trajectory],
        current_trajectories: List[Trajectory]
    ) -> str:
        """Build prompt for epoch-boundary slow update."""
        comparisons = []
        for prev_t, curr_t in zip(prev_trajectories, current_trajectories):
            delta = curr_t.score - prev_t.score
            comparisons.append(
                f"Task: {prev_t.task_input}\n"
                f"Prev score: {prev_t.score:.2f} → Current score: {curr_t.score:.2f} (Δ{delta:+.2f})"
            )
        
        comparison_text = "\n\n".join(comparisons)
        
        return f"""Compare skill evolution over this epoch.

Previous Skill (start of epoch):
{prev_skill.content}

Current Skill (end of epoch):
{current_skill.content}

Performance on same tasks:
{comparison_text}

Synthesize durable patterns that emerged. Propose ONE longitudinal guidance edit (typically APPEND).

Format:
EDIT_TYPE: APPEND
CONTENT: [high-level strategic guidance learned this epoch]
---
"""
    
    def _parse_edits(self, response: str) -> List[Edit]:
        """Parse edits from optimizer model response."""
        edits = []
        
        # Split by edit separator
        blocks = response.split("---")
        
        for block in blocks:
            block = block.strip()
            if not block:
                continue
            
            # Parse fields
            edit_type_match = re.search(r"EDIT_TYPE:\s*(\w+)", block)
            content_match = re.search(r"CONTENT:\s*(.+?)(?=\nANCHOR:|\nTARGET:|$)", block, re.DOTALL)
            anchor_match = re.search(r"ANCHOR:\s*(.+?)(?=\nCONTENT:|\nTARGET:|$)", block, re.DOTALL)
            target_match = re.search(r"TARGET:\s*(.+?)(?=\nCONTENT:|\nANCHOR:|$)", block, re.DOTALL)
            
            if not edit_type_match or not content_match:
                continue
            
            try:
                edit_type = EditType[edit_type_match.group(1).strip()]
            except KeyError:
                continue
            
            content = content_match.group(1).strip()
            anchor = anchor_match.group(1).strip() if anchor_match else None
            target = target_match.group(1).strip() if target_match else None
            
            edit = Edit(
                edit_type=edit_type,
                content=content,
                anchor=anchor,
                target=target,
            )
            edits.append(edit)
        
        return edits


# =============================================================================
# Example Usage
# =============================================================================

def example_target_model(skill: str, task: Dict) -> Dict:
    """
    Mock target model for demonstration.
    
    In practice, this would call an LLM API with the skill as system prompt.
    """
    # Simplified: check if skill contains helpful keywords
    task_input = task.get("input", "")
    
    # Mock execution
    output = f"Processed: {task_input}"
    
    # Mock scoring
    if "search" in skill.lower() and "search" in task_input.lower():
        score = 0.9
        success = True
    else:
        score = 0.5
        success = score > 0.7
    
    return {
        "output": output,
        "success": success,
        "score": score,
        "steps": [],
        "metadata": {},
    }


def example_optimizer_model(prompt: str) -> str:
    """
    Mock optimizer model for demonstration.
    
    In practice, this would call a stronger LLM API to analyze trajectories.
    """
    # Simplified: return a mock edit
    if "failed" in prompt.lower() or "failures" in prompt.lower():
        return """
EDIT_TYPE: APPEND
CONTENT: When the task involves searching, use targeted search strategies and verify results.
---
"""
    else:
        return """
EDIT_TYPE: APPEND
CONTENT: Continue using the current successful approach for similar tasks.
---
"""


def run_example():
    """Run a simple SkillOpt optimization example."""
    
    # Initial skill
    initial_skill = SkillDocument(
        content="""# Task Completion Skill

## Core Approach
Analyze the task carefully and execute step by step.

## Key Guidelines
- Read instructions thoroughly
- Break complex tasks into steps
- Verify results before finalizing
"""
    )
    
    # Mock data
    train_tasks = [
        {"id": f"train_{i}", "input": f"Search for topic {i}"} for i in range(20)
    ] + [
        {"id": f"train_other_{i}", "input": f"Summarize document {i}"} for i in range(20)
    ]
    
    validation_tasks = [
        {"id": f"val_{i}", "input": f"Search for topic {i}"} for i in range(10)
    ]
    
    # Create optimizer
    optimizer = SkillOptimizer(
        target_model=example_target_model,
        optimizer_model=example_optimizer_model,
        rollout_batch_size=10,
        reflection_minibatch_size=5,
        edit_budget_initial=2,
        edit_budget_floor=1,
        epochs=2,
    )
    
    # Run optimization
    best_skill, history = optimizer.optimize(
        initial_skill=initial_skill,
        train_tasks=train_tasks,
        validation_tasks=validation_tasks,
    )
    
    print("\n" + "="*80)
    print("BEST SKILL DOCUMENT:")
    print("="*80)
    print(best_skill.content)
    print("="*80)
    
    return best_skill, history


if __name__ == "__main__":
    run_example()
