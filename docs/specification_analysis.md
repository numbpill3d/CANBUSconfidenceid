# CAN Rolling Counter + Checksum Hypothesis Engine - Specification Analysis

## Project Overview
The goal is to build a local-first desktop tool that analyzes raw CAN bus logs (candump format) and generates structural hypotheses about:
1. Rolling counters
2. Checksum bytes
3. Multi-byte numeric signals

The tool must operate purely from statistical and structural inference over raw logs, without depending on DBC files.

## Input Requirements
- Format: Standard Linux `candump` style logs
- Example formats supported:
  - `(1609772212.123456) can0 1F334455#0010203040506070`
  - `can0 1F334455 [8] 00 10 20 30 40 50 60 70`
- Must extract: timestamp, arbitration ID (hex), DLC, payload bytes
- Must normalize payload into fixed-length byte array
- Must group frames by arbitration ID
- Must tolerate malformed lines and skip safely

## Core Analysis Requirements
- All analysis operates per arbitration ID independently
- Minimum frame count threshold: 20 frames per ID (configurable)

## Rolling Counter Detection
For each byte offset (0-7), compute:
1. Differences between consecutive frames: delta = (current - previous) mod 256
2. Count occurrences of various delta values
3. Calculate monotonicity scores
4. Detect wrap consistency
5. Identify small modulo behavior
6. Detect bit-field counters in sub-byte segments

Scoring formula example:
```
score = 0.5 * ratio_incremental + 0.2 * wrap_consistency + 0.2 * low_randomness_factor + 0.1 * cycle_repeatability
```

## Checksum Detection
For each candidate checksum position, test:
1. XOR checksum: computed = XOR(all other bytes)
2. Additive checksum (8-bit): computed = sum(all other bytes) mod 256
3. Inverted sum: computed = (~sum(all other bytes)) mod 256
4. One's complement sum
5. CRC8 with common automotive polynomials: 0x07, 0x1D, 0x2F, 0x31, 0x9B

Require match ratio > 0.8 to consider valid.

## Multi-byte Signal Detection
For adjacent byte pairs, combine as big-endian/little-endian 16-bit values and compute:
- Variance over time
- Smoothness (average absolute delta)
- Monotonic trends

## Entropy Analysis
Compute Shannon entropy for each byte offset:
- Low entropy (< 1.0) → flag or constant
- Medium entropy → structured numeric
- High entropy (> 7.0) → possible checksum, counter, or encrypted data

## Output Requirements
Structured JSON format with rolling counters, checksum candidates, multi-byte candidates, and entropy summary.

## Performance Requirements
- Handle 100k+ frames without freezing
- Use streaming parsing
- Avoid O(n^2) comparisons
- Operate per ID to reduce complexity

## Architecture Preferences
- Backend: Python
- Frontend: CLI first, extensible to Tauri desktop UI later
- Strongly typed structures
- Modular analysis pipeline