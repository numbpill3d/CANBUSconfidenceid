# CAN Hypothesis Engine - Architecture Plan

## High-Level Architecture

The application will follow a modular design with clear separation of concerns:

```
┌─────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│   CLI Layer     │ -> │  Processing      │ -> │   Analysis       │
│                 │    │  Pipeline        │    │   Modules        │
└─────────────────┘    └──────────────────┘    └──────────────────┘
                              │
                       ┌──────────────────┐
                       │   Output         │
                       │   Formatter      │
                       └──────────────────┘
```

## Module Structure

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

## Data Models

### CANFrame
```python
class CANFrame:
    timestamp: float
    arbitration_id: int  # 11 or 29-bit identifier
    dlc: int             # Data Length Code (0-8)
    data: bytes          # Payload (0-8 bytes)
```

### AnalysisResult
```python
class AnalysisResult:
    arbitration_id: str
    rolling_counters: List[RollingCounterCandidate]
    checksum_candidates: List[ChecksumCandidate]
    multi_byte_candidates: List[MultiByteCandidate]
    entropy_summary: List[EntropySummary]
```

## Core Components

### 1. CAN Parser (`core/can_parser.py`)
- Parse candump format logs
- Support both compact (#) and bracketed ([ ]) formats
- Handle malformed lines gracefully
- Stream processing for large files

### 2. Frame Analyzer (`core/analyzer.py`)
- Group frames by arbitration ID
- Apply minimum frame count threshold (20 frames)
- Coordinate analysis modules
- Aggregate results

### 3. Rolling Counter Detector (`analysis/rolling_counter.py`)
- Analyze each byte position for rolling counter patterns
- Calculate monotonicity scores
- Detect wrap behavior
- Score confidence in counter hypothesis

### 4. Checksum Detector (`analysis/checksum.py`)
- Test various checksum algorithms (XOR, additive, CRC8)
- Validate checksum positions
- Score match ratios
- Identify most likely checksum algorithm

### 5. Multi-byte Signal Detector (`analysis/multi_byte.py`)
- Identify adjacent byte pairs forming larger values
- Calculate variance and smoothness metrics
- Detect endianness patterns

### 6. Entropy Analyzer (`analysis/entropy.py`)
- Calculate Shannon entropy per byte position
- Classify byte behavior patterns
- Support other analysis modules with entropy data

## Processing Pipeline

1. **Input**: Read CAN log file in streaming fashion
2. **Parse**: Convert log lines to CANFrame objects
3. **Group**: Organize frames by arbitration ID
4. **Filter**: Remove IDs with fewer than 20 frames
5. **Analyze**: Run each analysis module per ID
6. **Score**: Calculate confidence scores for each hypothesis
7. **Format**: Generate JSON and human-readable outputs
8. **Output**: Write results to specified destination

## Error Handling Strategy

- Graceful degradation when encountering malformed log entries
- Continue processing despite individual frame errors
- Log warnings for skipped entries without crashing
- Validate inputs before processing

## Performance Considerations

- Streaming processing to handle large files efficiently
- Per-ID analysis to avoid O(n²) complexity
- Efficient data structures for frame storage
- Memory management for large datasets

## Testing Strategy

- Unit tests for each analysis module
- Integration tests for the complete pipeline
- Mock data for various CAN patterns
- Edge case testing (empty payloads, single frames, etc.)