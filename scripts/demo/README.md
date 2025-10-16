# 🎬 SIFU Demo Scripts

This directory contains demonstration and example scripts for SIFU.

## 📁 Demo Scripts

- **`demo_performance_budget.py`** - Performance budget demonstration

## 🎯 Purpose

These scripts serve as educational examples showing:
- How to use SIFU features
- Example workflows and patterns
- Testing various SIFU capabilities
- Integration examples

## 🚀 Usage

```bash
# Run demo scripts
python -m scripts.demo.demo_performance_budget
```

## 📝 Creating New Demo Scripts

1. Place in `scripts/demo/`
2. Name: `demo_*.py` or descriptive names
3. Include clear docstring explaining the demo
4. Add comments explaining key concepts
5. Make it executable and educational

Example:
```python
#!/usr/bin/env python3
"""
Demo: Feature X demonstration

This script shows how to use Feature X in SIFU.
"""

def demo():
    """Demonstrate Feature X"""
    # Show usage example
    pass

if __name__ == "__main__":
    demo()
```

## 🗂️ Related Directories

- `../setup/` - Setup and configuration scripts
- `../deploy/` - Deployment automation
- `../monitoring/` - Monitoring utilities
- `../util/` - General utilities
- `../../tests/demo/` - Demo tests (educational test examples)
