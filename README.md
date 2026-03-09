# CAN Rolling Counter + Checksum Hypothesis Engine

A powerful tool for analyzing CAN bus logs to infer rolling counters, checksum bytes, and multi-byte numeric signals from raw CAN data without requiring DBC files.

## Overview

This tool performs statistical and structural inference on raw CAN bus logs (candump format) to identify patterns that indicate:
- Rolling counters (modular incrementing values)
- Checksum bytes (various algorithms)
- Multi-byte numeric signals
- Data entropy characteristics

## Features

- **Cross-platform compatibility**: Works on macOS, Linux, and Windows
- **Memory efficient**: Streaming parser handles large log files
- **Comprehensive analysis**: Multiple detection algorithms
- **Confidence scoring**: Probabilistic claims with confidence levels
- **Multiple output formats**: JSON and human-readable reports
- **Robust error handling**: Gracefully handles malformed data

## Installation

### Prerequisites
- Python 3.7 or higher

### Install from source
```bash
git clone https://github.com/numbpill3d/CANBUSconfidenceid.git
cd CANBUSconfidenceid
pip install .
```

### Install directly from PyPI (if published)
```bash
pip install can-hypothesis-engine
```

## Usage

### Basic Usage
```bash
# Analyze a CAN log file
can-hypothesis input.log

# Generate human-readable report
can-hypothesis input.log --report

# Save results to JSON file
can-hypothesis input.log -o results.json

# Set minimum frames per ID (default: 20)
can-hypothesis input.log --min-frames 30
```

### Python API Usage
```python
from can_hypothesis_engine.parser.can_parser import parse_can_log
from can_hypothesis_engine.engine import CANHypothesisEngine

# Parse log file
id_to_frames = parse_can_log('input.log', min_frames_per_id=20)

# Analyze
engine = CANHypothesisEngine()
results = engine.analyze_grouped_frames(id_to_frames)

# Access results
for arb_id, result in results.items():
    print(result.to_human_readable())
```

## Input Format

Supports standard Linux `candump` format:

### Compact Format
```
(1609772212.123456) can0 1F334455#0010203040506070
```

### Bracketed Format  
```
can0 1F334455 [8] 00 10 20 30 40 50 60 70
```

## Output Format

### JSON Output
```json
{
  "0x1F334455": {
    "arbitration_id": "0x1F334455",
    "frame_count": 20,
    "rolling_counters": [
      {
        "algorithm": "rolling_counter_monotonic",
        "confidence": 0.8,
        "explanation": "Byte 0 increments by 1 in 80% of transitions...",
        "byte_position": 0,
        "cycle_length": 256,
        "increment_pattern": [1],
        "wrap_points": []
      }
    ],
    "checksum_candidates": [
      {
        "algorithm": "checksum_xor",
        "confidence": 0.92,
        "explanation": "Byte 6 matches XOR of bytes 0-5 in 92% of frames...",
        "checksum_position": 6,
        "covered_bytes": [0, 1, 2, 3, 4, 5],
        "match_ratio": 0.92
      }
    ],
    "multi_byte_candidates": [],
    "entropy_summary": [
      {
        "byte_position": 0,
        "entropy": 4.32,
        "interpretation": "Medium entropy - possibly numeric with patterns"
      }
    ]
  }
}
```

### Human-readable Report
```
Analysis Results for ID 0x1F334455 (20 frames)
============================================================

ROLLING COUNTERS:
  1. Byte 0 increments by 1 in 80% of transitions with medium confidence (monotonicity: 100%) (low randomness: 100%)
     Confidence: 0.80
     Algorithm: rolling_counter_monotonic
     Cycle Length: 256

CHECKSUM CANDIDATES:
  1. Byte 6 matches XOR of bytes 0-5 in 92% of frames with 92% confidence
     Confidence: 0.92
     Algorithm: checksum_xor
     Match Ratio: 0.92

ENTROPY SUMMARY:
  Byte 0: Entropy=4.32, Interpretation='Medium entropy - possibly numeric with patterns'
```

## Algorithms Implemented

### Rolling Counter Detection
- Monotonic increment detection (delta = 1)
- Wrap consistency analysis
- Small modulo behavior detection
- Bit-field counter detection

### Checksum Detection
- XOR checksum algorithm
- Additive checksum (8-bit)
- Inverted sum checksum
- Ones complement sum
- CRC8 with automotive polynomials (0x07, 0x1D, 0x2F, 0x31, 0x9B)

### Entropy Analysis
- Shannon entropy calculation for each byte position
- Data characterization based on entropy values

## Robustness Features

### Error Handling
- Graceful handling of malformed lines
- Continues processing despite individual frame errors
- Proper validation of inputs
- Logging of warnings for skipped entries

### Performance Optimizations
- Streaming file processing for large files
- Efficient data structures for analysis
- Early termination for low-confidence candidates
- Memory management for large datasets

### Cross-platform Compatibility
- Pure Python implementation
- Platform-independent file handling
- Compatible with all major operating systems
- No OS-specific dependencies

## Example Dataset

The repository includes `example_dataset.log` with realistic CAN data showing:
- Clear rolling counter patterns in bytes 0-7
- XOR checksum in byte 7 (calculated from bytes 0-6)
- Consistent frame structure for reliable analysis

## Testing

Run the built-in tests:
```bash
python test_engine.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License

## Support

For issues or questions, please open an issue on the GitHub repository.