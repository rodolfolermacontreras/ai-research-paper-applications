# Technique Name

**Category:** [Training | Evaluation | Prompt Engineering | Data Handling | Other]

**Summary:** [One-sentence description of what this technique does]

---

## What It Does

[2-3 paragraph explanation of the technique. Make it practical and implementation-focused.]

---

## When to Use

**Good for:**
- Use case 1
- Use case 2
- Use case 3

**Not suitable for:**
- Anti-use case 1
- Anti-use case 2

---

## Implementation

### Python Implementation

```python
#!/usr/bin/env python3
"""
Technique Name — Reference Implementation

[Brief docstring explaining the technique]
"""

def technique_name(param1, param2, param3=None):
    """
    [Function docstring with full explanation]
    
    Args:
        param1: Description
        param2: Description
        param3: Optional description
    
    Returns:
        Return value description
    
    Example:
        >>> result = technique_name(value1, value2)
        >>> print(result)
        Expected output
    """
    # Step 1: [Description]
    step1_result = process(param1)
    
    # Step 2: [Description]
    step2_result = transform(step1_result, param2)
    
    # Step 3: [Description]
    final_result = finalize(step2_result, param3)
    
    return final_result

# Helper functions
def process(data):
    """Process step description."""
    return data  # Placeholder

def transform(data, config):
    """Transform step description."""
    return data  # Placeholder

def finalize(data, options):
    """Finalize step description."""
    return data  # Placeholder

# Example usage
if __name__ == "__main__":
    # Example 1: Basic usage
    result1 = technique_name("input1", "input2")
    print(f"Basic: {result1}")
    
    # Example 2: Advanced usage
    result2 = technique_name("input1", "input2", param3="advanced")
    print(f"Advanced: {result2}")
```

### TypeScript/JavaScript Implementation (if applicable)

```typescript
// TypeScript implementation
function techniqueName(param1: string, param2: string, param3?: string): ReturnType {
    // Implementation
}
```

---

## Configuration

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `param1` | `type` | — | Required parameter description |
| `param2` | `type` | — | Required parameter description |
| `param3` | `type` | `null` | Optional parameter description |

### Recommended Settings

**For small datasets (<100 examples):**
```python
technique_name(
    param1=value1,
    param2=value2,
    param3=small_dataset_value
)
```

**For large datasets (>1000 examples):**
```python
technique_name(
    param1=value1,
    param2=value2,
    param3=large_dataset_value
)
```

---

## Papers Using This Technique

### [Paper Name](../../Papers/topic/paper-name/)
**Context:** [Where/how the paper uses this technique]
**Results:** [What results it achieved]

### [Another Paper](../../Papers/topic/another-paper/)
**Context:** [Context]
**Results:** [Results]

---

## Related Concepts

- [Concept Name](../concepts/concept-name.md) — How they relate

---

## Related Patterns

- [Pattern Name](../patterns/pattern-name.md) — How they relate

---

## Related Techniques

- [Related Technique 1](./related-technique-1.md) — Relationship description
- [Related Technique 2](./related-technique-2.md) — Relationship description

---

## Variations

### Variation 1: [Name]
**When to use:** [Use case]
**How it differs:** [Differences from base technique]

```python
# Code example for variation
def technique_variation_1():
    pass
```

---

## Performance Considerations

**Time Complexity:** O(n) [or appropriate complexity]

**Space Complexity:** O(n) [or appropriate complexity]

**Benchmarks:**
- Dataset size: 1K → Processing time: X seconds
- Dataset size: 10K → Processing time: Y seconds
- Dataset size: 100K → Processing time: Z seconds

---

## Common Pitfalls

### Pitfall 1: [Description]
**Problem:** What can go wrong
**Solution:** How to avoid it

### Pitfall 2: [Description]
**Problem:** What can go wrong
**Solution:** How to avoid it

---

## Testing

```python
import unittest

class TestTechniqueName(unittest.TestCase):
    """Test suite for the technique."""
    
    def test_basic_usage(self):
        """Test basic functionality."""
        result = technique_name("input1", "input2")
        self.assertIsNotNone(result)
    
    def test_edge_case_empty(self):
        """Test edge case: empty input."""
        result = technique_name("", "")
        # Assert expected behavior
    
    def test_edge_case_large(self):
        """Test edge case: large input."""
        large_input = "x" * 10000
        result = technique_name(large_input, "param2")
        # Assert expected behavior

if __name__ == '__main__':
    unittest.main()
```

---

## Full Code Example

**Complete working example:** [Link to file](../../Papers/topic/paper/implementation.py)

**Runnable notebook:** [Link to notebook](../../Papers/topic/paper/tutorial.ipynb)

---

## References

- **Original Paper:** [Paper name and link](../../Papers/topic/paper/)
- **Implementation Source:** [GitHub link or other source]
- **Blog Posts:** [Links to tutorials or explanations]

---

## Changelog

- **v1.0** (YYYY-MM-DD): Initial implementation
- **v1.1** (YYYY-MM-DD): Added variation X
- **v1.2** (YYYY-MM-DD): Performance optimization

---

**Related Tags:** #technique #tag1 #tag2

**Last Updated:** [YYYY-MM-DD]
