# CAN Hypothesis Engine - Directory Structure

## Planned Structure

```
can_infer/
├── __init__.py
├── cli.py                    # Command-line interface
├── core/
│   ├── __init__.py
│   ├── can_parser.py         # CAN log parsing utilities
│   ├── frame.py              # CAN frame data model
│   ├── analyzer.py           # Main analysis orchestrator
│   └── results.py            # Result data models
├── analysis/
│   ├── __init__.py
│   ├── rolling_counter.py    # Rolling counter detection
│   ├── checksum.py           # Checksum detection algorithms
│   ├── multi_byte.py         # Multi-byte signal detection
│   └── entropy.py            # Entropy analysis
├── utils/
│   ├── __init__.py
│   ├── math_utils.py         # Mathematical utilities
│   └── file_utils.py         # File handling utilities
├── tests/
│   ├── __init__.py
│   ├── test_can_parser.py
│   ├── test_rolling_counter.py
│   ├── test_checksum.py
│   └── test_integration.py
├── examples/
│   └── sample_log.txt
└── docs/
    └── specification_analysis.md
```

This structure will be implemented when moving to code mode.