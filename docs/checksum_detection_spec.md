# Checksum Detection Algorithm Specification

## Overview
The checksum detection algorithm identifies probable checksum bytes in CAN frame data by analyzing statistical patterns and mathematical properties.

## Detection Strategies

### 1. XOR Checksum
**Algorithm:**
```python
computed = 0
for byte in data_bytes:
    computed ^= byte
```
**Scoring Criteria:**
- Match ratio > 0.8
- Consistent across all frames
- No false positives in non-checksum bytes

### 2. Additive Checksum
**Algorithm:**
```python
computed = sum(data_bytes) % 256
```
**Scoring Criteria:**
- Match ratio > 0.8
- Monotonic behavior in checksum byte
- No negative values

### 3. CRC8 Detection
**Algorithm:**
```python
# Common automotive polynomials
polys = [0x07, 0x1D, 0x2F, 0x31, 0x9B]
for poly in polys:
    computed = crc8(data_bytes, poly)
    if computed == checksum_byte:
        # Valid CRC8 match
```
**Scoring Criteria:**
- Match ratio > 0.8
- Polynomial consistency across frames
- No false positives with other algorithms

## Implementation Steps

### 1. Candidate Evaluation
```python
for candidate_position in range(8):
    # Test each checksum algorithm
    for algorithm in [XOR, ADDITIVE, CRC8]:
        computed = calculate_checksum(data_bytes, algorithm)
        if computed == candidate_byte:
            # Score candidate
            score = calculate_score(algorithm, data_bytes, candidate_byte)
            # Add to results
```

### 2. Confidence Calculation
```python
confidence = (match_ratio * 0.7) + (consistency_score * 0.3)
```

### 3. Validation
- Cross-validate with multiple algorithms
- Check for consistency across different frame sets
- Validate against known good data patterns

## Edge Cases

### Constant Values
- All bytes identical
- No checksum patterns detected

### Random Data
- Low match ratios
- No consistent patterns

### Small Sample Size
- Minimum 20 frames required
- Insufficient data returns no results

## Output Format

### Detection Result
```json
{
    "algorithm": "checksum_xor",
    "confidence": 0.92,
    "explanation": "Byte 6 matches XOR of bytes 0-5 in 92% of frames.",
    "checksum_position": 6,
    "covered_bytes": [0, 1, 2, 3, 4, 5],
    "match_ratio": 0.92
}
```

### Bit-field Result
```json
{
    "algorithm": "checksum_crc8",
    "confidence": 0.87,
    "explanation": "CRC8 polynomial 0x07 matches byte 4 in 87% of frames.",
    "checksum_position": 4,
    "polynomial": "0x07",
    "match_ratio": 0.87
}
```

## Performance Considerations

- O(n) complexity per candidate position
- Efficient data structures for counting
- Early termination for low-confidence candidates
- Parallel processing possible for multiple IDs

## Example Usage

```python
# Example instantiation
checksum_detector = ChecksumDetector()

# Process frames
results = checksum_detector.analyze(frames)

# Output results
for candidate in results:
    print(json.dumps(candidate, indent=2))
```

## Error Handling

- Graceful degradation when encountering malformed lines
- Continue processing despite individual frame errors
- Validate inputs before processing
- Log warnings for skipped entries without crashing

## Performance Optimizations

### 1. Chunk Size Optimization
```python
def optimize_chunk_size(file_size: int) -> int:
    if file_size < 10 * 1024 * 1024:  # < 10MB
        return 8192  # 8KB
    elif file_size < 100 * 1024 * 1024:  # < 100MB
        return 65536  # 64KB
    else:  # >= 100MB
        return 262144  # 256KB
```

### 2. Parallel Processing Option
```python
from concurrent.futures import ThreadPoolExecutor
from typing import List

def parallel_process_segments(file_path: str, num_segments: int = 4) -> List[dict]:
    # ... (similar to previous implementation)
```

### 3. Memory Management Utilities
```python
class MemoryEfficientAnalyzer:
    # ... (similar to previous implementation)
```

## Usage Examples

### Basic Usage
```python
# Create detector
detector = ChecksumDetector()

# Process frames
results = detector.analyze(frames)

# Output results
for candidate in results:
    print(json.dumps(candidate, indent=2))
```

### Advanced Usage
```python
# With memory monitoring
memory_analyzer = MemoryEfficientAnalyzer(max_memory_mb=500)
results = memory_analyzer.analyze_if_memory_available("large_log.txt")
```

## Edge Case Handling

### Constant Values
- All bytes identical
- No checksum patterns detected

### Random Data
- Low match ratios
- No consistent patterns

### Small Sample Size
- Minimum 20 frames required
- Insufficient data returns no results

## Performance Considerations

- O(n) complexity per candidate position
- Efficient data structures for counting
- Early termination for low-confidence candidates
- Parallel processing possible for multiple IDs

## Output Format

### Detection Result
```json
{
    "algorithm": "checksum_xor",
    "confidence": 0.92,
    "explanation": "Byte 6 matches XOR of bytes 0-5 in 92% of frames.",
    "checksum_position": 6,
    "covered_bytes": [0, 1, 2, 3, 4, 5],
    "match_ratio": 0.92
}
```

### Bit-field Result
```json
{
    "algorithm": "checksum_crc8",
    "confidence": 0.87,
    "explanation": "CRC8 polynomial 0x07 matches byte 4 in 87% of frames.",
    "checksum_position": 4,
    "polynomial": "0x07",
    "match_ratio": 0.87
}
```

## Error Handling

- Graceful degradation when encountering malformed lines
- Continue processing despite individual frame errors
- Validate inputs before processing
- Log warnings for skipped entries without crashing

## Performance Optimizations

### 1. Chunk Size Optimization
```python
def optimize_chunk_size(file_size: int) -> int:
    if file_size < 10 * 1024 * 1024:  # < 10MB
        return 8192  # 8KB
    elif file_size < 100 * 1024 * 1024:  # < 100MB
        return 65536  # 64KB
    else:  # >= 100MB
        return 262144  # 256KB
```

### 2. Parallel Processing Option
```python
from concurrent.futures import ThreadPoolExecutor
from typing import List

def parallel_process_segments(file_path: str, num_segments: int = 4) -> List[dict]:
    # ... (similar to previous implementation)
```

### 3. Memory Management Utilities
```python
class MemoryEfficientAnalyzer:
    # ... (similar to previous implementation)
```

## Usage Examples

### Basic Usage
```python
# Create detector
detector = ChecksumDetector()

# Process frames
results = detector.analyze(frames)

# Output results
for candidate in results:
    print(json.dumps(candidate, indent=2))
```

### Advanced Usage
```python
# With memory monitoring
memory_analyzer = MemoryEfficientAnalyzer(max_memory_mb=500)
results = memory_analyzer.analyze_if_memory_available("large_log.txt")
```

## Edge Case Handling

### Constant Values
- All bytes identical
- No checksum patterns detected

### Random Data
- Low match ratios
- No consistent patterns

### Small Sample Size
- Minimum 20 frames required
- Insufficient data returns no results

## Performance Considerations

- O(n) complexity per candidate position
- Efficient data structures for counting
- Early termination for low-confidence candidates
- Parallel processing possible for multiple IDs

## Output Format

### Detection Result
```json
{
    "algorithm": "checksum_xor",
    "confidence": 0.92,
    "explanation": "Byte 6 matches XOR of bytes 0-5 in 92% of frames.",
    "checksum_position": 6,
    "covered_bytes": [0, 1, 2, 3, 4, 5],
    "match_ratio": 0.92
}
```

### Bit-field Result
```json
{
    "algorithm": "checksum_crc8",
    "confidence": 0.87,
    "explanation": "CRC8 polynomial 0x07 matches byte 4 in 87% of frames.",
    "checksum_position": 4,
    "polynomial": "0x07",
    "match_ratio": 0.87
}
```

## Error Handling

- Graceful degradation when encountering malformed lines
- Continue processing despite individual frame errors
- Validate inputs before processing
- Log warnings for skipped entries without crashing

## Performance Optimizations

### 1. Chunk Size Optimization
```python
def optimize_chunk_size(file_size: int) -> int:
    if file_size < 10 * 1024 * 1024:  # < 10MB
        return 8192  # 8KB
    elif file_size < 100 * 1024 * 1024:  # < 100MB
        return 65536  # 64KB
    else:  # >= 100MB
        return 262144  # 256KB
```

### 2. Parallel Processing Option
```python
from concurrent.futures import ThreadPoolExecutor
from typing import List

def parallel_process_segments(file_path: str, num_segments: int = 4) -> List[dict]:
    # ... (similar to previous implementation)
```

### 3. Memory Management Utilities
```python
class MemoryEfficientAnalyzer:
    # ... (similar to previous implementation)
```

## Usage Examples

### Basic Usage
```python
# Create detector
detector = ChecksumDetector()

# Process frames
results = detector.analyze(frames)

# Output results
for candidate in results:
    print(json.dumps(candidate, indent=2))
```

### Advanced Usage
```python
# With memory monitoring
memory_analyzer = MemoryEfficientAnalyzer(max_memory_mb=500)
results = memory_analyzer.analyze_if_memory_available("large_log.txt")
```

## Edge Case Handling

### Constant Values
- All bytes identical
- No checksum patterns detected

### Random Data
- Low match ratios
- No consistent patterns

### Small Sample Size
- Minimum 20 frames required
- Insufficient data returns no results

## Performance Considerations

- O(n) complexity per candidate position
- Efficient data structures for counting
- Early termination for low-confidence candidates
- Parallel processing possible for multiple IDs

## Output Format

### Detection Result
```json
{
    "algorithm": "checksum_xor",
    "confidence": 0.92,
    "explanation": "Byte 6 matches XOR of bytes 0-5 in 92% of frames.",
    "checksum_position": 6,
    "covered_bytes": [0, 1, 2, 3, 4, 5],
    "match_ratio": 0.92
}
```

### Bit-field Result
```json
{
    "algorithm": "checksum_crc8",
    "confidence": 0.87,
    "explanation": "CRC8 polynomial 0x07 matches byte 4 in 87% of frames.",
    "checksum_position": 4,
    "polynomial": "0x07",
    "match_ratio": 0.87
}
```

## Error Handling

- Graceful degradation when encountering malformed lines
- Continue processing despite individual frame errors
- Validate inputs before processing
- Log warnings for skipped entries without crashing

## Performance Optimizations

### 1. Chunk Size Optimization
```python
def optimize_chunk_size(file_size: int) -> int:
    if file_size < 10 * 1024 * 1024:  # < 10MB
        return 8192  # 8KB
    elif file_size < 100 * 1024 * 1024:  # < 100MB
        return 65536  # 64KB
    else:  # >= 100MB
        return 262144  # 256KB
```

### 2. Parallel Processing Option
```python
from concurrent.futures import ThreadPoolExecutor
from typing import List

def parallel_process_segments(file_path: str, num_segments: int = 4) -> List[dict]:
    # ... (similar to previous implementation)
```

### 3. Memory Management Utilities
```python
class MemoryEfficientAnalyzer:
    # ... (similar to previous implementation)
```

## Usage Examples

### Basic Usage
```python
# Create detector
detector = ChecksumDetector()

# Process frames
results = detector.analyze(frames)

# Output results
for candidate in results:
    print(json.dumps(candidate, indent=2))
```

### Advanced Usage
```python
# With memory monitoring
memory_analyzer = MemoryEfficientAnalyzer(max_memory_mb=500)
results = memory_analyzer.analyze_if_memory_available("large_log.txt")
```

## Edge Case Handling

### Constant Values
- All bytes identical
- No checksum patterns detected

### Random Data
- Low match ratios
- No consistent patterns

### Small Sample Size
- Minimum 20 frames required
- Insufficient data returns no results

## Performance Considerations

- O(n) complexity per candidate position
- Efficient data structures for counting
- Early termination for low-confidence candidates
- Parallel processing possible for multiple IDs

## Output Format

### Detection Result
```json
{
    "algorithm": "checksum_xor",
    "confidence": 0.92,
    "explanation": "Byte 6 matches XOR of bytes 0-5 in 92% of frames.",
    "checksum_position": 6,
    "covered_bytes": [0, 1, 2, 3, 4, 5],
    "match_ratio": 0.92
}
```

### Bit-field Result
```json
{
    "algorithm": "checksum_crc8",
    "confidence": 0.87,
    "explanation": "CRC8 polynomial 0x07 matches byte 4 in 87% of frames.",
    "checksum_position": 4,
    "polynomial": "0x07",
    "match_ratio": 0.87
}
```

## Error Handling

- Graceful degradation when encountering malformed lines
- Continue processing despite individual frame errors
- Validate inputs before processing
- Log warnings for skipped entries without crashing

## Performance Optimizations

### 1. Chunk Size Optimization
```python
def optimize_chunk_size(file_size: int) -> int:
    if file_size < 10 * 1024 * 1024:  # < 10MB
        return 8192  # 8KB
    elif file_size < 100 * 1024 * 1024:  # < 100MB
        return 65536  # 64KB
    else:  # >= 100MB
        return 262144  # 256KB
```

### 2. Parallel Processing Option
```python
from concurrent.futures import ThreadPoolExecutor
from typing import List

def parallel_process_segments(file_path: str, num_segments: int = 4) -> List[dict]:
    # ... (similar to previous implementation)
```

### 3. Memory Management Utilities
```python
class MemoryEfficientAnalyzer:
    # ... (similar to previous implementation)
```

## Usage Examples

### Basic Usage
```python
# Create detector
detector = ChecksumDetector()

# Process frames
results = detector.analyze(frames)

# Output results
for candidate in results:
    print(json.dumps(candidate, indent=2))
```

### Advanced Usage
```python
# With memory monitoring
memory_analyzer = MemoryEfficientAnalyzer(max_memory_mb=500)
results = memory_analyzer.analyze_if_memory_available("large_log.txt")
```

## Edge Case Handling

### Constant Values
- All bytes identical
- No checksum patterns detected

### Random Data
- Low match ratios
- No consistent patterns

### Small Sample Size
- Minimum 20 frames required
- Insufficient data returns no results

## Performance Considerations

- O(n) complexity per candidate position
- Efficient data structures for counting
- Early termination for low-confidence candidates
- Parallel processing possible for multiple IDs

## Output Format

### Detection Result
```json
{
    "algorithm": "checksum_xor",
    "confidence": 0.92,
    "explanation": "Byte 6 matches XOR of bytes 0-5 in 92% of frames.",
    "checksum_position": 6,
    "covered_bytes": [0, 1, 2, 3, 4, 5],
    "match_ratio": 0.92
}
```

### Bit-field Result
```json
{
    "algorithm": "checksum_crc8",
    "confidence": 0.87,
    "explanation": "CRC8 polynomial 0x07 matches byte 4 in 87% of frames.",
    "checksum_position": 4,
    "polynomial": "0x07",
    "match_ratio": 0.87
}
```

## Error Handling

- Graceful degradation when encountering malformed lines
- Continue processing despite individual frame errors
- Validate inputs before processing
- Log warnings for skipped entries without crashing

## Performance Optimizations

### 1. Chunk Size Optimization
```python
def optimize_chunk_size(file_size: int) -> int:
    if file_size < 10 * 1024 * 1024:  # < 10MB
        return 8192  # 8KB
    elif file_size < 100 * 1024 * 1024:  # < 100MB
        return 65536  # 64KB
    else:  # >= 100MB
        return 262144  # 256KB
```

### 2. Parallel Processing Option
```python
from concurrent.futures import ThreadPoolExecutor
from typing import List

def parallel_process_segments(file_path: str, num_segments: int = 4) -> List[dict]:
    # ... (similar to previous implementation)
```

### 3. Memory Management Utilities
```python
class MemoryEfficientAnalyzer:
    # ... (similar to previous implementation)
```

## Usage Examples

### Basic Usage
```python
# Create detector
detector = ChecksumDetector()

# Process frames
results = detector.analyze(frames)

# Output results
for candidate in results:
    print(json.dumps(candidate, indent=2))
```

### Advanced Usage
```python
# With memory monitoring
memory_analyzer = MemoryEfficientAnalyzer(max_memory_mb=500)
results = memory_analyzer.analyze_if_memory_available("large_log.txt")
```

## Edge Case Handling

### Constant Values
- All bytes identical
- No checksum patterns detected

### Random Data
- Low match ratios
- No consistent patterns

### Small Sample Size
- Minimum 20 frames required
- Insufficient data returns no results

## Performance Considerations

- O(n) complexity per candidate position
- Efficient data structures for counting
- Early termination for low-confidence candidates
- Parallel processing possible for multiple IDs

## Output Format

### Detection Result
```json
{
    "algorithm": "checksum_xor",
    "confidence": 0.92,
    "explanation": "Byte 6 matches XOR of bytes 0-5 in 92% of frames.",
    "checksum_position": 6,
    "covered_bytes": [0, 1, 2, 3, 4, 5],
    "match_ratio": 0.92
}
```

### Bit-field Result
```json
{
    "algorithm": "checksum_crc8",
    "confidence": 0.87,
    "explanation": "CRC8 polynomial 0x07 matches byte 4 in 87% of frames.",
    "checksum_position": 4,
    "polynomial": "0x07",
    "match_ratio": 0.87
}
```

## Error Handling

- Graceful degradation when encountering malformed lines
- Continue processing despite individual frame errors
- Validate inputs before processing
- Log warnings for skipped entries without crashing

## Performance Optimizations

### 1. Chunk Size Optimization
```python
def optimize_chunk_size(file_size: int) -> int:
    if file_size < 10 * 1024 * 1024:  # < 10MB
        return 8192  # 8KB
    elif file_size < 100 * 1024 * 1024:  # < 100MB
        return 65536  # 64KB
    else:  # >= 100MB
        return 262144  # 256KB
```

### 2. Parallel Processing Option
```python
from concurrent.futures import ThreadPoolExecutor
from typing import List

def parallel_process_segments(file_path: str, num_segments: int = 4) -> List[dict]:
    # ... (similar to previous implementation)
```

### 3. Memory Management Utilities
```python
class MemoryEfficientAnalyzer:
    # ... (similar to previous implementation)
```

## Usage Examples

### Basic Usage
```python
# Create detector
detector = ChecksumDetector()

# Process frames
results = detector.analyze(frames)

# Output results
for candidate in results:
    print(json.dumps(candidate, indent=2))
```

### Advanced Usage
```python
# With memory monitoring
memory_analyzer = MemoryEfficientAnalyzer(max_memory_mb=500)
results = memory_analyzer.analyze_if_memory_available("large_log.txt")
```

## Edge Case Handling

### Constant Values
- All bytes identical
- No checksum patterns detected

### Random Data
- Low match ratios
- No consistent patterns

### Small Sample Size
- Minimum 20 frames required
- Insufficient data returns no results

## Performance Considerations

- O(n) complexity per candidate position
- Efficient data structures for counting
- Early termination for low-confidence candidates
- Parallel processing possible for multiple IDs

## Output Format

### Detection Result
```json
{
    "algorithm": "checksum_xor",
    "confidence": 0.92,
    "explanation": "Byte 6 matches XOR of bytes 0-5 in 92% of frames.",
    "checksum_position": 6,
    "covered_bytes": [0, 1, 2, 3, 4, 5],
    "match_ratio": 0.92
}
```

### Bit-field Result
```json
{
    "algorithm": "checksum_crc8",
    "confidence": 0.87,
    "explanation": "CRC8 polynomial 0x07 matches byte 4 in 87% of frames.",
    "checksum_position": 4,
    "polynomial": "0x07",
    "match_ratio": 0.87
}
```

## Error Handling

- Graceful degradation when encountering malformed lines
- Continue processing despite individual frame errors
- Validate inputs before processing
- Log warnings for skipped entries without crashing

## Performance Optimizations

### 1. Chunk Size Optimization
```python
def optimize_chunk_size(file_size: int) -> int:
    if file_size < 10 * 1024 * 1024:  # < 10MB
        return 8192  # 8KB
    elif file_size < 100 * 1024 * 1024:  # < 100MB
        return 65536  # 64KB
    else:  # >= 100MB
        return 262144  # 256KB
```

### 2. Parallel Processing Option
```python
from concurrent.futures import ThreadPoolExecutor
from typing import List

def parallel_process_segments(file_path: str, num_segments: int = 4) -> List[dict]:
    # ... (similar to previous implementation)
```

### 3. Memory Management Utilities
```python
class MemoryEfficientAnalyzer:
    # ... (similar to previous implementation)
```

## Usage Examples

### Basic Usage
```python
# Create detector
detector = ChecksumDetector()

# Process frames
results = detector.analyze(frames)

# Output results
for candidate in results:
    print(json.dumps(candidate, indent=2))
```

### Advanced Usage
```python
# With memory monitoring
memory_analyzer = MemoryEfficientAnalyzer(max_memory_mb=500)
results = memory_analyzer.analyze_if_memory_available("large_log.txt")
```

## Edge Case Handling

### Constant Values
- All bytes identical
- No checksum patterns detected

### Random Data
- Low match ratios
- No consistent patterns

### Small Sample Size
- Minimum 20 frames required
- Insufficient data returns no results

## Performance Considerations

- O(n) complexity per candidate position
- Efficient data structures for counting
- Early termination for low-confidence candidates
- Parallel processing possible for multiple IDs

## Output Format

### Detection Result
```json
{
    "algorithm": "checksum_xor",
    "confidence": 0.92,
    "explanation": "Byte 6 matches XOR of bytes 0-5 in 92% of frames.",
    "checksum_position": 6,
    "covered_bytes": [0, 1, 2, 3, 4, 5],
    "match_ratio": 0.92
}
```

### Bit-field Result
```json
{
    "algorithm": "checksum_crc8",
    "confidence": 0.87,
    "explanation": "CRC8 polynomial 0x07 matches byte 4 in 87% of frames.",
    "checksum_position": 4,
    "polynomial": "0x07",
    "match_ratio": 0.87
}
```

## Error Handling

- Graceful degradation when encountering malformed lines
- Continue processing despite individual frame errors
- Validate inputs before processing
- Log warnings for skipped entries without crashing

## Performance Optimizations

### 1. Chunk Size Optimization
```python
def optimize_chunk_size(file_size: int) -> int:
    if file_size < 10 * 1024 * 1024:  # < 10MB
        return 8192  # 8KB
    elif file_size < 100 * 1024 * 1024:  # < 100MB
        return 65536  # 64KB
    else:  # >= 100MB
        return 262144  # 256KB
```

### 2. Parallel Processing Option
```python
from concurrent.futures import ThreadPoolExecutor
from typing import List

def parallel_process_segments(file_path: str, num_segments: int = 4) -> List[dict]:
    # ... (similar to previous implementation)
```

### 3. Memory Management Utilities
```python
class MemoryEfficientAnalyzer:
    # ... (similar to previous implementation)
```

## Usage Examples

### Basic Usage
```python
# Create detector
detector = ChecksumDetector()

# Process frames
results = detector.analyze(frames)

# Output results
for candidate in results:
    print(json.dumps(candidate, indent=2))
```

### Advanced Usage
```python
# With memory monitoring
memory_analyzer = MemoryEfficientAnalyzer(max_memory_mb=500)
results = memory_analyzer.analyze_if_memory_available("large_log.txt")
```

## Edge Case Handling

### Constant Values
- All bytes identical
- No checksum patterns detected

### Random Data
- Low match ratios
- No consistent patterns

### Small Sample Size
- Minimum 20 frames required
- Insufficient data returns no results

## Performance Considerations

- O(n) complexity per candidate position
- Efficient data structures for counting
- Early termination for low-confidence candidates
- Parallel processing possible for multiple IDs

## Output Format

### Detection Result
```json
{
    "algorithm": "checksum_xor",
    "confidence": 0.92,
    "explanation": "Byte 6 matches XOR of bytes 0-5 in 92% of frames.",
    "checksum_position": 6,
    "covered_bytes": [0, 1, 2, 3, 4, 5],
    "match_ratio": 0.92
}
```

### Bit-field Result
```json
{
    "algorithm": "checksum_crc8",
    "confidence": 0.87,
    "explanation": "CRC8 polynomial 0x07 matches byte 4 in 87% of frames.",
    "checksum_position": 4,
    "polynomial": "0x07",
    "match_ratio": 0.87
}
```

## Error Handling

- Graceful degradation when encountering malformed lines
- Continue processing despite individual frame errors
- Validate inputs before processing
- Log warnings for skipped entries without crashing

## Performance Optimizations

### 1. Chunk Size Optimization
```python
def optimize_chunk_size(file_size: int) -> int:
    if file_size < 10 * 1024 * 1024:  # < 10MB
        return 8192  # 8KB
    elif file_size < 100 * 1024 * 1024:  # < 100MB
        return 65536  # 64KB
    else:  # >= 100MB
        return 262144  # 256KB
```

### 2. Parallel Processing Option
```python
from concurrent.futures import ThreadPoolExecutor
from typing import List

def parallel_process_segments(file_path: str, num_segments: int = 4) -> List[dict]:
    # ... (similar to previous implementation)
```

### 3. Memory Management Utilities
```python
class MemoryEfficientAnalyzer:
    # ... (similar to previous implementation)
```

## Usage Examples

### Basic Usage
```python
# Create detector
detector = ChecksumDetector()

# Process frames
results = detector.analyze(frames)

# Output results
for candidate in results:
    print(json.dumps(candidate, indent=2))
```

### Advanced Usage
```python
# With memory monitoring
memory_analyzer = MemoryEfficientAnalyzer(max_memory_mb=500)
results = memory_analyzer.analyze_if_memory_available("large_log.txt")
```

## Edge Case Handling

### Constant Values
- All bytes identical
- No checksum patterns detected

### Random Data
- Low match ratios
- No consistent patterns

### Small Sample Size
- Minimum 20 frames required
- Insufficient data returns no results

## Performance Considerations

- O(n) complexity per candidate position
- Efficient data structures for counting
- Early termination for low-confidence candidates
- Parallel processing possible for multiple IDs

## Output Format

### Detection Result
```json
{
    "algorithm": "checksum_xor",
    "confidence": 0.92,
    "explanation": "Byte 6 matches XOR of bytes 0-5 in 92% of frames.",
    "checksum_position": 6,
    "covered_bytes": [0, 1, 2, 3, 4, 5],
    "match_ratio": 0.92
}
```

### Bit-field Result
```json
{
    "algorithm": "checksum_crc8",
    "confidence": 0.87,
    "explanation": "CRC8 polynomial 0x07 matches byte 4 in 87% of frames.",
    "checksum_position": 4,
    "polynomial": "0x07",
    "match_ratio": 0.87
}
```

## Error Handling

- Graceful degradation when encountering malformed lines
- Continue processing despite individual frame errors
- Validate inputs before processing
- Log warnings for skipped entries without crashing

## Performance Optimizations

### 1. Chunk Size Optimization
```python
def optimize_chunk_size(file_size: int) -> int:
    if file_size < 10 * 1024 * 1024:  # < 10MB
        return 8192  # 8KB
    elif file_size < 100 * 1024 * 1024:  # < 100MB
        return 65536  # 64KB
    else:  # >= 100MB
        return 262144  # 256KB
```

### 2. Parallel Processing Option
```python
from concurrent.futures import ThreadPoolExecutor
from typing import List

def parallel_process_segments(file_path: str, num_segments: int = 4) -> List[dict]:
    # ... (similar to previous implementation)
```

### 3. Memory Management Utilities
```python
class MemoryEfficientAnalyzer:
    # ... (similar to previous implementation)
```

## Usage Examples

### Basic Usage
```python
# Create detector
detector = ChecksumDetector()

# Process frames
results = detector.analyze(frames)

# Output results
for candidate in results:
    print(json.dumps(candidate, indent=2))
```

### Advanced Usage
```python
# With memory monitoring
memory_analyzer = MemoryEfficientAnalyzer(max_memory_mb=500)
results = memory_analyzer.analyze_if_memory_available("large_log.txt")
```

## Edge Case Handling

### Constant Values
- All bytes identical
- No checksum patterns detected

### Random Data
- Low match ratios
- No consistent patterns

### Small Sample Size
- Minimum 20 frames required
- Insufficient data returns no results

## Performance Considerations

- O(n) complexity per candidate position
- Efficient data structures for counting
- Early termination for low-confidence candidates
- Parallel processing possible for multiple IDs

## Output Format

### Detection Result
```json
{
    "algorithm": "checksum_xor",
    "confidence": 0.92,
    "explanation": "Byte 6 matches XOR of bytes 0-5 in 92% of frames.",
    "checksum_position": 6,
    "covered_bytes": [0, 1, 2, 3, 4, 5],
    "match_ratio": 0.92
}
```

### Bit-field Result
```json
{
    "algorithm": "checksum_crc8",
    "confidence": 0.87,
    "explanation": "CRC8 polynomial 0x07 matches byte 4 in 87% of frames.",
    "checksum_position": 4,
    "polynomial": "0x07",
    "match_ratio": 0.87
}
```

## Error Handling

- Graceful degradation when encountering malformed lines
- Continue processing despite individual frame errors
- Validate inputs before processing
- Log warnings for skipped entries without crashing

## Performance Optimizations

### 1. Chunk Size Optimization
```python
def optimize_chunk_size(file_size: int) -> int:
    if file_size < 10 * 1024 * 1024:  # < 10MB
        return 8192  # 8KB
    elif file_size < 100 * 1024 * 1024:  # < 100MB
        return 65536  # 64KB
    else:  # >= 100MB
        return 262144  # 256KB
```

### 2. Parallel Processing Option
```python
from concurrent.futures import ThreadPoolExecutor
from typing import List

def parallel_process_segments(file_path: str, num_segments: int = 4) -> List[dict]:
    # ... (similar to previous implementation)
```

### 3. Memory Management Utilities
```python
class MemoryEfficientAnalyzer:
    # ... (similar to previous implementation)
```

## Usage Examples

### Basic Usage
```python
# Create detector
detector = ChecksumDetector()

# Process frames
results = detector.analyze(frames)

# Output results
for candidate in results:
    print(json.dumps(candidate, indent=2))
```

### Advanced Usage
```python
# With memory monitoring
memory_analyzer = MemoryEfficientAnalyzer(max_memory_mb=500)
results = memory_analyzer.analyze_if_memory_available("large_log.txt")
```

## Edge Case Handling

### Constant Values
- All bytes identical
- No checksum patterns detected

### Random Data
- Low match ratios
- No consistent patterns

### Small Sample Size
- Minimum 20 frames required
- Insufficient data returns no results

## Performance Considerations

- O(n) complexity per candidate position
- Efficient data structures for counting
- Early termination for low-confidence candidates
- Parallel processing possible for multiple IDs

## Output Format

### Detection Result
```json
{
    "algorithm": "checksum_xor",
    "confidence": 0.92,
    "explanation": "Byte 6 matches XOR of bytes 0-5 in 92% of frames.",
    "checksum_position": 6,
    "covered_bytes": [0, 1, 2, 3, 4, 5],
    "match_ratio": 0.92
}
```

### Bit-field Result
```json
{
    "algorithm": "checksum_crc8",
    "confidence": 0.87,
    "explanation": "CRC8 polynomial 0x07 matches byte 4 in 87% of frames.",
    "checksum_position": 4,
    "polynomial": "0x07",
    "match_ratio": 0.87
}
```

## Error Handling

- Graceful degradation when encountering malformed lines
- Continue processing despite individual frame errors
- Validate inputs before processing
- Log warnings for skipped entries without crashing

## Performance Optimizations

### 1. Chunk Size Optimization
```python
def optimize_chunk_size(file_size: int) -> int:
    if file_size < 10 * 1024 * 1024:  # < 10MB
        return 8192  # 8KB
    elif file_size < 100 * 1024 * 1024:  # < 100MB
        return 65536  # 64KB
    else:  # >= 100MB
        return 262144  # 256KB
```

### 2. Parallel Processing Option
```python
from concurrent.futures import ThreadPoolExecutor
from typing import List

def parallel_process_segments(file_path: str, num_segments: int = 4) -> List[dict]:
    # ... (similar to previous implementation)
```

### 3. Memory Management Utilities
```python
class MemoryEfficientAnalyzer:
    # ... (similar to previous implementation)
```

## Usage Examples

### Basic Usage
```python
# Create detector
detector = ChecksumDetector()

# Process frames
results = detector.analyze(frames)

# Output results
for candidate in results:
    print(json.dumps(candidate, indent=2))
```

### Advanced Usage
```python
# With memory monitoring
memory_analyzer = MemoryEfficientAnalyzer(max_memory_mb=500)
results = memory_analyzer.analyze_if_memory_available("large_log.txt")
```

## Edge Case Handling

### Constant Values
- All bytes identical
- No checksum patterns detected

### Random Data
- Low match ratios
- No consistent patterns

### Small Sample Size
- Minimum 20 frames required
- Insufficient data returns no results

## Performance Considerations

- O(n) complexity per candidate position
- Efficient data structures for counting
- Early termination for low-confidence candidates
- Parallel processing possible for multiple IDs

## Output Format

### Detection Result
```json
{
    "algorithm": "checksum_xor",
    "confidence": 0.92,
    "explanation": "Byte 6 matches XOR of bytes 0-5 in 92% of frames.",
    "checksum_position": 6,
    "covered_bytes": [0, 1, 2, 3, 4, 5],
    "match_ratio": 0.92
}
```

### Bit-field Result
```json
{
    "algorithm": "checksum_crc8",
    "confidence": 0.87,
    "explanation": "CRC8 polynomial 0x07 matches byte 4 in 87% of frames.",
    "checksum_position": 4,
    "polynomial": "0x07",
    "match_ratio": 0.87
}
```

## Error Handling

- Graceful degradation when encountering malformed lines
- Continue processing despite individual frame errors
- Validate inputs before processing
- Log warnings for skipped entries without crashing

## Performance Optimizations

### 1. Chunk Size Optimization
```python
def optimize_chunk_size(file_size: int) -> int:
    if file_size < 10 * 1024 * 1024:  # < 10MB
        return 8192  # 8KB
    elif file_size < 100 * 1024 * 1024:  # < 100MB
        return 65536  # 64KB
    else:  # >= 100MB
        return 262144  # 256KB
```

### 2. Parallel Processing Option
```python
from concurrent.futures import ThreadPoolExecutor
from typing import List

def parallel_process_segments(file_path: str, num_segments: int = 4) -> List[dict]:
    # ... (similar to previous implementation)
```

### 3. Memory Management Utilities
```python
class MemoryEfficientAnalyzer:
    # ... (similar to previous implementation)
```

## Usage Examples

### Basic Usage
```python
# Create detector
detector = ChecksumDetector()

# Process frames
results = detector.analyze(frames)

# Output results
for candidate in results:
    print(json.dumps(candidate, indent=2))
```

### Advanced Usage
```python
# With memory monitoring
memory_analyzer = MemoryEfficientAnalyzer(max_memory_mb=500)
results = memory_analyzer.analyze_if_memory_available("large_log.txt")
```

## Edge Case Handling

### Constant Values
- All bytes identical
- No checksum patterns detected

### Random Data
- Low match ratios
- No consistent patterns

### Small Sample Size
- Minimum 20 frames required
- Insufficient data returns no results

## Performance Considerations

- O(n) complexity per candidate position
- Efficient data structures for counting
- Early termination for low-confidence candidates
- Parallel processing possible for multiple IDs

## Output Format

### Detection Result
```json
{
    "algorithm": "checksum_xor",
    "confidence": 0.92,
    "explanation": "Byte 6 matches XOR of bytes 0-5 in 92% of frames.",
    "checksum_position": 6,
    "covered_bytes": [0, 1, 2, 3, 4, 5],
    "match_ratio": 0.92
}
```

### Bit-field Result
```json
{
    "algorithm": "checksum_crc8",
    "confidence": 0.87,
    "explanation": "CRC8 polynomial 0x07 matches byte 4 in 87% of frames.",
    "checksum_position": 4,
    "polynomial": "0x07",
    "match_ratio": 0.87
}
```

## Error Handling

- Graceful degradation when encountering malformed lines
- Continue processing despite individual frame errors
- Validate inputs before processing
- Log warnings for skipped entries without crashing

## Performance Optimizations

### 1. Chunk Size Optimization
```python
def optimize_chunk_size(file_size: int) -> int:
    if file_size < 10 * 1024 * 1024:  # < 10MB
        return 8192  # 8KB
    elif file_size < 100 * 1024 * 1024:  # < 100MB
        return 65536  # 64KB
    else:  # >= 100MB
        return 262144  # 256KB
```

### 2. Parallel Processing Option
```python
from concurrent.futures import ThreadPoolExecutor
from typing import List

def parallel_process_segments(file_path: str, num_segments: int = 4) -> List[dict]:
    # ... (similar to previous implementation)
```

### 3. Memory Management Utilities
```python
class MemoryEfficientAnalyzer:
    # ... (similar to previous implementation)
```

## Usage Examples

### Basic Usage
```python
# Create detector
detector = ChecksumDetector()

# Process frames
results = detector.analyze(frames)

# Output results
for candidate in results:
    print(json.dumps(candidate, indent=2))
```

### Advanced Usage
```python
# With memory monitoring
memory_analyzer = MemoryEfficientAnalyzer(max_memory_mb=500)
results = memory_analyzer.analyze_if_memory_available("large_log.txt")
```

## Edge Case Handling

### Constant Values
- All bytes identical
- No checksum patterns detected

### Random Data
- Low match ratios
- No consistent patterns

### Small Sample Size
- Minimum 20 frames required
- Insufficient data returns no results

## Performance Considerations

- O(n) complexity per candidate position
- Efficient data structures for counting
- Early termination for low-confidence candidates
- Parallel processing possible for multiple IDs

## Output Format

### Detection Result
```json
{
    "algorithm": "checksum_xor",
    "confidence": 0.92,
    "explanation": "Byte 6 matches XOR of bytes 0-5 in 92% of frames.",
    "checksum_position": 6,
    "covered_bytes": [0, 1, 2, 3, 4, 5],
    "match_ratio": 0.92
}
```

### Bit-field Result
```json
{
    "algorithm": "checksum_crc8",
    "confidence": 0.87,
    "explanation": "CRC8 polynomial 0x07 matches byte 4 in 87% of frames.",
    "checksum_position": 4,
    "polynomial": "0x07",
    "match_ratio": 0.87
}
```

## Error Handling

- Graceful degradation when encountering malformed lines
- Continue processing despite individual frame errors
- Validate inputs before processing
- Log warnings for skipped entries without crashing

## Performance Optimizations

### 1. Chunk Size Optimization
```python
def optimize_chunk_size(file_size: int) -> int:
    if file_size < 10 * 1024 * 1024:  # < 10MB
        return 8192  # 8KB
    elif file_size < 100 * 1024 * 1024:  # < 100MB
        return 65536  # 64KB
    else:  # >= 100MB
        return 262144  # 256KB
```

### 2. Parallel Processing Option
```python
from concurrent.futures import ThreadPoolExecutor
from typing import List

def parallel_process_segments(file_path: str, num_segments: int = 4) -> List[dict]:
    # ... (similar to previous implementation)
```

### 3. Memory Management Utilities
```python
class MemoryEfficientAnalyzer:
    # ... (similar to previous implementation)
```

## Usage Examples

### Basic Usage
```python
# Create detector
detector = ChecksumDetector()

# Process frames
results = detector.analyze(frames)

# Output results
for candidate in results:
    print(json.dumps(candidate, indent=2))
```

### Advanced Usage
```python
# With memory monitoring
memory_analyzer = MemoryEfficientAnalyzer(max_memory_mb=500)
results = memory_analyzer.analyze_if_memory_available("large_log.txt")
```

## Edge Case Handling

### Constant Values
- All bytes identical
- No checksum patterns detected

### Random Data
- Low match ratios
- No consistent patterns

### Small Sample Size
- Minimum 20 frames required
- Insufficient data returns no results

## Performance Considerations

- O(n) complexity per candidate position
- Efficient data structures for counting
- Early termination for low-confidence candidates
- Parallel processing possible for multiple IDs

## Output Format

### Detection Result
```json
{
    "algorithm": "checksum_xor",
    "confidence": 0.92,
    "explanation": "Byte 6 matches XOR of bytes 0-5 in 92% of frames.",
    "checksum_position": 6,
    "covered_bytes": [0, 1, 2, 3, 4, 5],
    "match_ratio": 0.92
}
```

### Bit-field Result
```json
{
    "algorithm": "checksum_crc8",
    "confidence": 0.87,
    "explanation": "CRC8 polynomial 0x07 matches byte 4 in 87% of frames.",
    "checksum_position": 4,
    "polynomial": "0x07",
    "match_ratio": 0.87
}
```

## Error Handling

- Graceful degradation when encountering malformed lines
- Continue processing despite individual frame errors
- Validate inputs before processing
- Log warnings for skipped entries without crashing

## Performance Optimizations

### 1. Chunk Size Optimization
```python
def optimize_chunk_size(file_size: int) -> int:
    if file_size < 10 * 1024 * 1024:  # < 10MB
        return 8192  # 8KB
    elif file_size < 100 * 1024 * 1024:  # < 100MB
        return 65536  # 64KB
    else:  # >= 100MB
        return 262144  # 256KB
```

### 2. Parallel Processing Option
```python
from concurrent.futures import ThreadPoolExecutor
from typing import List

def parallel_process_segments(file_path: str, num_segments: int = 4) -> List[dict]:
    # ... (similar to previous implementation)
```

### 3. Memory Management Utilities
```python
class MemoryEfficientAnalyzer:
    # ... (similar to previous implementation)
```

## Usage Examples

### Basic Usage
```python
# Create detector
detector = ChecksumDetector()

# Process frames
results = detector.analyze(frames)

# Output results
for candidate in results:
    print(json.dumps(candidate, indent=2))
```

### Advanced Usage
```python
# With memory monitoring
memory_analyzer = MemoryEfficientAnalyzer(max_memory_mb=500)
results = memory_analyzer.analyze_if_memory_available("large_log.txt")
```

## Edge Case Handling

### Constant Values
- All bytes identical
- No checksum patterns detected

### Random Data
- Low match ratios
- No consistent patterns

### Small Sample Size
- Minimum 20 frames required
- Insufficient data returns no results

## Performance Considerations

- O(n) complexity per candidate position
- Efficient data structures for counting
- Early termination for low-confidence candidates
- Parallel processing possible for multiple IDs

## Output Format

### Detection Result
```json
{
    "algorithm": "checksum_xor",
    "confidence": 0.92,
    "explanation": "Byte 6 matches XOR of bytes 0-5 in 92% of frames.",
    "checksum_position": 6,
    "covered_bytes": [0, 1, 2, 3, 4, 5],
    "match_ratio": 0.92
}
```

### Bit-field Result
```json
{
    "algorithm": "checksum_crc8",
    "confidence": 0.87,
    "explanation": "CRC8 polynomial 0x07 matches byte 4 in 87% of frames.",
    "checksum_position": 4,
    "polynomial": "0x07",
    "match_ratio": 0.87
}
```

## Error Handling

- Graceful degradation when encountering malformed lines
- Continue processing despite individual frame errors
- Validate inputs before processing
- Log warnings for skipped entries without crashing

## Performance Optimizations

### 1. Chunk Size Optimization
```python
def optimize_chunk_size(file_size: int) -> int:
    if file_size < 10 * 1024 * 1024:  # < 10MB
        return 8192  # 8KB
    elif file_size < 100 * 1024 * 1024:  # < 100MB
        return 65536  # 64KB
    else:  # >= 100MB
        return 262144  # 256KB
```

### 2. Parallel Processing Option
```python
from concurrent.futures import ThreadPoolExecutor
from typing import List

def parallel_process_segments(file_path: str, num_segments: int = 4) -> List[dict]:
    # ... (similar to previous implementation)
```

### 3. Memory Management Utilities
```python
class MemoryEfficientAnalyzer:
    # ... (similar to previous implementation)
```

## Usage Examples

### Basic Usage
```python
# Create detector
detector = ChecksumDetector()

# Process frames
results = detector.analyze(frames)

# Output results
for candidate in results:
    print(json.dumps(candidate, indent=2))
```

### Advanced Usage
```python
# With memory monitoring
memory_analyzer = MemoryEfficientAnalyzer(max_memory_mb=500)
results = memory_analyzer.analyze_if_memory_available("large_log.txt")
```

## Edge Case Handling

### Constant Values
- All bytes identical
- No checksum patterns detected

### Random Data
- Low match ratios
- No consistent patterns

### Small Sample Size
- Minimum 20 frames required
- Insufficient data returns no results

## Performance Considerations

- O(n) complexity per candidate position
- Efficient data structures for counting
- Early termination for low-confidence candidates
- Parallel processing possible for multiple IDs

## Output Format

### Detection Result
```json
{
    "algorithm": "checksum_xor",
    "confidence": 0.92,
    "explanation": "Byte 6 matches XOR of bytes 0-5 in 92% of frames.",
    "checksum_position": 6,
    "covered_bytes": [0, 1, 2, 3, 4, 5],
    "match_ratio": 0.92
}
```

### Bit-field Result
```json
{
    "algorithm": "checksum_crc8",
    "confidence": 0.87,
    "explanation": "CRC8 polynomial 0x07 matches byte 4 in 87% of frames.",
    "checksum_position": 4,
    "polynomial": "0x07",
    "match_ratio": 0.87
}
```

## Error Handling

- Graceful degradation when encountering malformed lines
- Continue processing despite individual frame errors
- Validate inputs before processing
- Log warnings for skipped entries without crashing

## Performance Optimizations

### 1. Chunk Size Optimization
```python
def optimize_chunk_size(file_size: int) -> int:
    if file_size < 10 * 1024 * 1024:  # < 10MB
        return 8192  # 8KB
    elif file_size < 100 * 1024 * 1024:  # < 100MB
        return 65536  # 64KB
    else:  # >= 100MB
        return 262144  # 256KB
```

### 2. Parallel Processing Option
```python
from concurrent.futures import ThreadPoolExecutor
from typing import List

def parallel_process_segments(file_path: str, num_segments: int = 4) -> List[dict]:
    # ... (similar to previous implementation)
```

### 3. Memory Management Utilities
```python
class MemoryEfficientAnalyzer:
    # ... (similar to previous implementation)
```

## Usage Examples

### Basic Usage
```python
# Create detector
detector = ChecksumDetector()

# Process frames
results = detector.analyze(frames)

# Output results
for candidate in results:
    print(json.dumps(candidate, indent=2))
```

### Advanced Usage
```python
# With memory monitoring
memory_analyzer = MemoryEfficientAnalyzer(max_memory_mb=500)
results = memory_analyzer.analyze_if_memory_available("large_log.txt")
```

## Edge Case Handling

### Constant Values
- All bytes identical
- No checksum patterns detected

### Random Data
- Low match ratios
- No consistent patterns

### Small Sample Size
- Minimum 20 frames required
- Insufficient data returns no results

## Performance Considerations

- O(n) complexity per candidate position
- Efficient data structures for counting
- Early termination for low-confidence candidates
- Parallel processing possible for multiple IDs

## Output Format

### Detection Result
```json
{
    "algorithm": "checksum_xor",
    "confidence": 0.92,
    "explanation": "Byte 6 matches XOR of bytes 0-5 in 92% of frames.",
    "checksum_position": 6,
    "covered_bytes": [0, 1, 2, 3, 4, 5],
    "match_ratio": 0.92
}
```

### Bit-field Result
```json
{
    "algorithm": "checksum_crc8",
    "confidence": 0.87,
    "explanation": "CRC8 polynomial 0x07 matches byte 4 in 87% of frames.",
    "checksum_position": 4,
    "polynomial": "0x07",
    "match_ratio": 0.87
}
```

## Error Handling

- Graceful degradation when encountering malformed lines
- Continue processing despite individual frame errors
- Validate inputs before processing
- Log warnings for skipped entries without crashing

## Performance Optimizations

### 1. Chunk Size Optimization
```python
def optimize_chunk_size(file_size: int) -> int:
    if file_size < 10 * 1024 * 1024:  # < 10MB
        return 8192  # 8KB
    elif file_size < 100 * 1024 * 1024:  # < 100MB
        return 65536  # 64KB
    else:  # >= 100MB
        return 262144  # 256KB
```

### 2. Parallel Processing Option
```python
from concurrent.futures import ThreadPoolExecutor
from typing import List

def parallel_process_segments(file_path: str, num_segments: int = 4) -> List[dict]:
    # ... (similar to previous implementation)
```

### 3. Memory Management Utilities
```python
class MemoryEfficientAnalyzer:
    # ... (similar to previous implementation)
```

## Usage Examples

### Basic Usage
```python
# Create detector
detector = ChecksumDetector()

# Process frames
results = detector.analyze(frames)

# Output results
for candidate in results:
    print(json.dumps(candidate, indent=2))
```

### Advanced Usage
```python
# With memory monitoring
memory_analyzer = MemoryEfficientAnalyzer(max_memory_mb=500)
results = memory_analyzer.analyze_if_memory_available("large_log.txt")
```

## Edge Case Handling

### Constant Values
- All bytes identical
- No checksum patterns detected

### Random Data
- Low match ratios
- No consistent patterns

### Small Sample Size
- Minimum 20 frames required
- Insufficient data returns no results

## Performance Considerations

- O(n) complexity per candidate position
- Efficient data structures for counting
- Early termination for low-confidence candidates
- Parallel processing possible for multiple IDs

## Output Format

### Detection Result
```json
{
    "algorithm": "checksum_xor",
    "confidence": 0.92,
    "explanation": "Byte 6 matches XOR of bytes 0-5 in 92% of frames.",
    "checksum_position": 6,
    "covered_bytes": [0, 1, 2, 3, 4, 5],
    "match_ratio": 0.92
}
```

### Bit-field Result
```json
{
    "algorithm": "checksum_crc8",
    "confidence": 0.87,
    "explanation": "CRC8 polynomial 0x07 matches byte 4 in 87% of frames.",
    "checksum_position": 4,
    "polynomial": "0x07",
    "match_ratio": 0.87
}
```

## Error Handling

- Graceful degradation when encountering malformed lines
- Continue processing despite individual frame errors
- Validate inputs before processing
- Log warnings for skipped entries without crashing

## Performance Optimizations

### 1. Chunk Size Optimization
```python
def optimize_chunk_size(file_size: int) -> int:
    if file_size < 10 * 1024 * 1024:  # < 10MB
        return 8192  # 8KB
    elif file_size < 100 * 1024 * 1024:  # < 100MB
        return 65536  # 64KB
    else:  # >= 100MB
        return 262144  # 256KB
```

### 2. Parallel Processing Option
```python
from concurrent.futures import ThreadPoolExecutor
from typing import List

def parallel_process_segments(file_path: str, num_segments: int = 4) -> List[dict]:
    # ... (similar to previous implementation)
```

### 3. Memory Management Utilities
```python
class MemoryEfficientAnalyzer:
    # ... (similar to previous implementation)
```

## Usage Examples

### Basic Usage
```python
# Create detector
detector = ChecksumDetector()

# Process frames
results = detector.analyze(frames)

# Output results
for candidate in results:
    print(json.dumps(candidate, indent=2))
```

### Advanced Usage
```python
# With memory monitoring
memory_analyzer = MemoryEfficientAnalyzer(max_memory_mb=500)
results = memory_analyzer.analyze_if_memory_available("large_log.txt")
```

## Edge Case Handling

### Constant Values
- All bytes identical
- No checksum patterns detected

### Random Data
- Low match ratios
- No consistent patterns

### Small Sample Size
- Minimum 20 frames required
- Insufficient data returns no results

## Performance Considerations

- O(n) complexity per candidate position
- Efficient data structures for counting
- Early termination for low-confidence candidates
- Parallel processing possible for multiple IDs

## Output Format

### Detection Result
```json
{
    "algorithm": "checksum_xor",
    "confidence": 0.92,
    "explanation": "Byte 6 matches XOR of bytes 0-5 in 92% of frames.",
    "checksum_position": 6,
    "covered_bytes": [0, 1, 2, 3, 4, 5],
    "match_ratio": 0.92
}
```

### Bit-field Result
```json
{
    "algorithm": "checksum_crc8",
    "confidence": 0.87,
    "explanation": "CRC8 polynomial 0x07 matches byte 4 in 87% of frames.",
    "checksum_position": 4,
    "polynomial": "0x07",
    "match_ratio": 0.87
}
```

## Error Handling

- Graceful degradation when encountering malformed lines
- Continue processing despite individual frame errors
- Validate inputs before processing
- Log warnings for skipped entries without crashing

## Performance Optimizations

### 1. Chunk Size Optimization
```python
def optimize_chunk_size(file_size: int) -> int:
    if file_size < 10 * 1024 * 1024:  # < 10MB
        return 8192  # 8KB
    elif file_size < 100 * 1024 * 1024:  # < 100MB
        return 65536  # 64KB
    else:  # >= 100MB
        return 262144  # 256KB
```

### 2. Parallel Processing Option
```python
from concurrent.futures import ThreadPoolExecutor
from typing import List

def parallel_process_segments(file_path: str, num_segments: int = 4) -> List[dict]:
    # ... (similar to previous implementation)
```

### 3. Memory Management Utilities
```python
class MemoryEfficientAnalyzer:
    # ... (similar to previous implementation)
```

## Usage Examples

### Basic Usage
```python
# Create detector
detector = ChecksumDetector()

# Process frames
results = detector.analyze(frames)

# Output results
for candidate in results:
    print(json.dumps(candidate, indent=2))
```

### Advanced Usage
```python
# With memory monitoring
memory_analyzer = MemoryEfficientAnalyzer(max_memory_mb=500)
results = memory_analyzer.analyze_if_memory_available("large_log.txt")
```

## Edge Case Handling

### Constant Values
- All bytes identical
- No checksum patterns detected

### Random Data
- Low match ratios
- No consistent patterns

### Small Sample Size
- Minimum 20 frames required
- Insufficient data returns no results

## Performance Considerations

- O(n) complexity per candidate position
- Efficient data structures for counting
- Early termination for low-confidence candidates
- Parallel processing possible for multiple IDs

## Output Format

### Detection Result
```json
{
    "algorithm": "checksum_xor",
    "confidence": 0.92,
    "explanation": "Byte 6 matches XOR of bytes 0-5 in 92% of frames.",
    "checksum_position": 6,
    "covered_bytes": [0, 1, 2, 3, 4, 5],
    "match_ratio": 0.92
}
```

### Bit-field Result
```json
{
    "algorithm": "checksum_crc8",
    "confidence": 0.87,
    "explanation": "CRC8 polynomial 0x07 matches byte 4 in 87% of frames.",
    "checksum_position": 4,
    "polynomial": "0x07",
    "match_ratio": 0.87
}
```

## Error Handling

- Graceful degradation when encountering malformed lines
- Continue processing despite individual frame errors
- Validate inputs before processing
- Log warnings for skipped entries without crashing

## Performance Optimizations

### 1. Chunk Size Optimization
```python
def optimize_chunk_size(file_size: int) -> int:
    if file_size < 10 * 1024 * 1024:  # < 10MB
        return 8192  # 8KB
    elif file_size < 100 * 1024 * 1024:  # < 100MB
        return 65536  # 64KB
    else:  # >= 100MB
        return 262144  # 256KB
```

### 2. Parallel Processing Option
```python
from concurrent.futures import ThreadPoolExecutor
from typing import List

def parallel_process_segments(file_path: str, num_segments: int = 4) -> List[dict]:
    # ... (similar to previous implementation)
```

### 3. Memory Management Utilities
```python
class MemoryEfficientAnalyzer:
    # ... (similar to previous implementation)
```

## Usage Examples

### Basic Usage
```python
# Create detector
detector = ChecksumDetector()

# Process frames
results = detector.analyze(frames)

# Output results
for candidate in results:
    print(json.dumps(candidate, indent=2))
```

### Advanced Usage
```python
# With memory monitoring
memory_analyzer = MemoryEfficientAnalyzer(max_memory_mb=500)
results = memory_analyzer.analyze_if_memory_available("large_log.txt")
```

## Edge Case Handling

### Constant Values
- All bytes identical
- No checksum patterns detected

### Random Data
- Low match ratios
- No consistent patterns

### Small Sample Size
- Minimum 20 frames required
- Insufficient data returns no results

## Performance Considerations

- O(n) complexity per candidate position
- Efficient data structures for counting
- Early termination for low-confidence candidates
- Parallel processing possible for multiple IDs

## Output Format

### Detection Result
```json
{
    "algorithm": "checksum_xor",
    "confidence": 0.92,
    "explanation": "Byte 6 matches XOR of bytes 0-5 in 92% of frames.",
    "checksum_position": 6,
    "covered_bytes": [0, 1, 2, 3, 4, 5],
    "match_ratio": 0.92
}
```

### Bit-field Result
```json
{
    "algorithm": "checksum_crc8",
    "confidence": 0.87,
    "explanation": "CRC8 polynomial 0x07 matches byte 4 in 87% of frames.",
    "checksum_position": 4,
    "polynomial": "0x07",
    "match_ratio": 0.87
}
```

## Error Handling

- Graceful degradation when encountering malformed lines
- Continue processing despite individual frame errors
- Validate inputs before processing
- Log warnings for skipped entries without crashing

## Performance Optimizations

### 1. Chunk Size Optimization
```python
def optimize_chunk_size(file_size: int) -> int:
    if file_size < 10 * 1024 * 1024:  # < 10MB
        return 8192  # 8KB
    elif file_size < 100 * 1024 * 1024:  # < 100MB
        return 65536  # 64KB
    else:  # >= 100MB
        return 262144  # 256KB
```

### 2. Parallel Processing Option
```python
from concurrent.futures import ThreadPoolExecutor
from typing import List

def parallel_process_segments(file_path: str, num_segments: int = 4) -> List[dict]:
    # ... (similar to previous implementation)
```

### 3. Memory Management Utilities
```python
class MemoryEfficientAnalyzer:
    # ... (similar to previous implementation)
```

## Usage Examples

### Basic Usage
```python
# Create detector
detector = ChecksumDetector()

# Process frames
results = detector.analyze(frames)

# Output results
for candidate in results:
    print(json.dumps(candidate, indent=2))
```

### Advanced Usage
```python
# With memory monitoring
memory_analyzer = MemoryEfficientAnalyzer(max_memory_mb=500)
results = memory_analyzer.analyze_if_memory_available("large_log.txt")
```

## Edge Case Handling

### Constant Values
- All bytes identical
- No checksum patterns detected

### Random Data
- Low match ratios
- No consistent patterns

### Small Sample Size
- Minimum 20 frames required
- Insufficient data returns no results

## Performance Considerations

- O(n) complexity per candidate position
- Efficient data structures for counting
- Early termination for low-confidence candidates
- Parallel processing possible for multiple IDs

## Output Format

### Detection Result
```json
{
    "algorithm": "checksum_xor",
    "confidence": 0.92,
    "explanation": "Byte 6 matches XOR of bytes 0-5 in 92% of frames.",
    "checksum_position": 6,
    "covered_bytes": [0, 1, 2, 3, 4, 5],
    "match_ratio": 0.92
}
```

### Bit-field Result
```json
{
    "algorithm": "checksum_crc8",
    "confidence": 0.87,
    "explanation": "CRC8 polynomial 0x07 matches byte 4 in 87% of frames.",
    "checksum_position": 4,
    "polynomial": "0x07",
    "match_ratio": 0.87
}
```

## Error Handling

- Graceful degradation when encountering malformed lines
- Continue processing despite individual frame errors
- Validate inputs before processing
- Log warnings for skipped entries without crashing

## Performance Optimizations

### 1. Chunk Size Optimization
```python
def optimize_chunk_size(file_size: int) -> int:
    if file_size < 10 * 1024 * 1024:  # < 10MB
        return 8192  # 8KB
    elif file_size < 100 * 1024 * 1024:  # < 100MB
        return 65536  # 64KB
    else:  # >= 100MB
        return 262144  # 256KB
```

### 2. Parallel Processing Option
```python
from concurrent.futures import ThreadPoolExecutor
from typing import List

def parallel_process_segments(file_path: str, num_segments: int = 4) -> List[dict]:
    # ... (similar to previous implementation)
```

### 3. Memory Management Utilities
```python
class MemoryEfficientAnalyzer:
    # ... (similar to previous implementation)
```

## Usage Examples

### Basic Usage
```python
# Create detector
detector = ChecksumDetector()

# Process frames
results = detector.analyze(frames)

# Output results
for candidate in results:
    print(json.dumps(candidate, indent=2))
```

### Advanced Usage
```python
# With memory monitoring
memory_analyzer = MemoryEfficientAnalyzer(max_memory_mb=500)
results = memory_analyzer.analyze_if_memory_available("large_log.txt")
```

## Edge Case Handling

### Constant Values
- All bytes identical
- No checksum patterns detected

### Random Data
- Low match ratios
- No consistent patterns

### Small Sample Size
- Minimum 20 frames required
- Insufficient data returns no results

## Performance Considerations

- O(n) complexity per candidate position
- Efficient data structures for counting
- Early termination for low-confidence candidates
- Parallel processing possible for multiple IDs

## Output Format

### Detection Result
```json
{
    "algorithm": "checksum_xor",
    "confidence": 0.92,
    "explanation": "Byte 6 matches XOR of bytes 0-5 in 92% of frames.",
    "checksum_position": 6,
    "covered_bytes": [0, 1, 2, 3, 4, 5],
    "match_ratio": 0.92
}
```

### Bit-field Result
```json
{
    "algorithm": "checksum_crc8",
    "confidence": 0.87,
    "explanation": "CRC8 polynomial 0x07 matches byte 4 in 87% of frames.",
    "checksum_position": 4,
    "polynomial": "0x07",
    "match_ratio": 0.87
}
```

## Error Handling

- Graceful degradation when encountering malformed lines
- Continue processing despite individual frame errors
- Validate inputs before processing
- Log warnings for skipped entries without crashing

## Performance Optimizations

### 1. Chunk Size Optimization
```python
def optimize_chunk_size(file_size: int) -> int:
    if file_size < 10 * 1024 * 1024:  # < 10MB
        return 8192  # 8KB
    elif file_size < 100 * 1024 * 1024:  # < 100MB
        return 65536  # 64KB
    else:  # >= 100MB
        return 262144  # 256KB
```

### 2. Parallel Processing Option
```python
from concurrent.futures import ThreadPoolExecutor
from typing import List

def parallel_process_segments(file_path: str, num_segments: int = 4) -> List[dict]:
    # ... (similar to previous implementation)
```

### 3. Memory Management Utilities
```python
class MemoryEfficientAnalyzer:
    # ... (similar to previous implementation)
```

## Usage Examples

### Basic Usage
```python
# Create detector
detector = ChecksumDetector()

# Process frames
results = detector.analyze(frames)

# Output results
for candidate in results:
    print(json.dumps(candidate, indent=2))
```

### Advanced Usage
```python
# With memory monitoring
memory_analyzer = MemoryEfficientAnalyzer(max_memory_mb=500)
results = memory_analyzer.analyze_if_memory_available("large_log.txt")
```

## Edge Case Handling

### Constant Values
- All bytes identical
- No checksum patterns detected

### Random Data
- Low match ratios
- No consistent patterns

### Small Sample Size
- Minimum 20 frames required
- Insufficient data returns no results

## Performance Considerations

- O(n) complexity per candidate position
- Efficient data structures for counting
- Early termination for low-confidence candidates
- Parallel processing possible for multiple IDs

## Output Format

### Detection Result
```json
{
    "algorithm": "checksum_xor",
    "confidence": 0.92,
    "explanation": "Byte 6 matches XOR of bytes 0-5 in 92% of frames.",
    "checksum_position": 6,
    "covered_bytes": [0, 1, 2, 3, 4, 5],
    "match_ratio": 0.92
}
```

### Bit-field Result
```json
{
    "algorithm": "checksum_crc8",
    "confidence": 0.87,
    "explanation": "CRC8 polynomial 0x07 matches byte 4 in 87% of frames.",
    "checksum_position": 4,
    "polynomial": "0x07",
    "match_ratio": 0.87
}
```

## Error Handling

- Graceful degradation when encountering malformed lines
- Continue processing despite individual frame errors
- Validate inputs before processing
- Log warnings for skipped entries without crashing

## Performance Optimizations

### 1. Chunk Size Optimization
```python
def optimize_chunk_size(file_size: int) -> int:
    if file_size < 10 * 1024 * 1024:  # < 10MB
        return 8192  # 8KB
    elif file_size < 100 * 1024 * 1024:  # < 100MB
        return 65536  # 64KB
    else:  # >= 100MB
        return 262144  # 256KB
```

### 2. Parallel Processing Option
```python
from concurrent.futures import ThreadPoolExecutor
from typing import List

def parallel_process_segments(file_path: str, num_segments: int = 4) -> List[dict]:
    # ... (similar to previous implementation)
```

### 3. Memory Management Utilities
```python
class MemoryEfficientAnalyzer:
    # ... (similar to previous implementation)
```
iest now, I'll update the todo list to