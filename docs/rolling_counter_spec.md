# Rolling Counter Detection Algorithm Specification

## Overview
The rolling counter detection algorithm identifies bytes that behave like modulo-N counters by analyzing patterns in consecutive frame data.

## Detection Strategy

### 1. Delta Analysis
For each byte position (0-7):
1. Calculate differences between consecutive frames:
   ```
delta = (current_byte - previous_byte) mod 256
```
2. Count occurrences of specific delta values:
   - delta == 1 (monotonic increment)
   - delta in {2, 3, 4, 5} (small increments)
   - delta == 0 (no change)
   - delta == 255 (wrap from 255 to 0)

### 2. Monotonicity Scoring
Calculate monotonicity score:
```
monotonicity_score = (# delta == 1) / (total_transitions)
```

### 3. Wrap Detection
Detect wrap behavior:
```
wrap_count = count of (delta == 255 and previous_delta == 0)
```

### 4. Small Modulo Detection
Identify bytes with limited range:
```
low_randomness = count of (1 ≤ delta ≤ 5)
```

### 5. Bit-field Analysis
For each byte, analyze sub-byte segments:
- 2-bit windows (0-1, 2-3, 4-5, 6-7)
- 4-bit windows (0-3, 4-7)
- 8-bit windows (full byte)

## Scoring Model

### Base Scoring Formula
```
score = 0.5 * monotonicity_score + 0.2 * wrap_consistency + 0.2 * low_randomness + 0.1 * cycle_repeatability
```

### Component Details

#### Monotonicity Score (0.5 weight)
- Measures how often the byte increments by 1
- High score indicates strong monotonic behavior

#### Wrap Consistency (0.2 weight)
- Measures how often the byte wraps from 255 to 0
- High score indicates consistent cyclic behavior

#### Low Randomness (0.2 weight)
- Measures how often the byte changes by small amounts
- High score indicates limited range behavior

#### Cycle Repeatability (0.1 weight)
- Measures how often the same pattern repeats
- High score indicates predictable cyclic behavior

## Confidence Thresholds

### High Confidence (0.8+)
- Strong monotonic behavior
- Consistent wrapping
- Limited range changes

### Medium Confidence (0.5-0.8)
- Some monotonic behavior
- Occasional wrapping
- Moderate range changes

### Low Confidence (0.0-0.5)
- Random or unpredictable behavior
- No clear patterns

## Implementation Steps

### Step 1: Frame Grouping
```python
# Group frames by arbitration ID
id_to_frames = defaultdict(list)
for frame in frames:
    id_to_frames[frame.arbitration_id_hex].append(frame)
```

### Step 2: Byte Position Analysis
```python
for byte_pos in range(8):
    # Calculate deltas for this byte position
    deltas = []
    for i in range(1, len(frames)):
        prev_byte = frames[i-1].get_byte_at_offset(byte_pos)
        curr_byte = frames[i].get_byte_at_offset(byte_pos)
        if prev_byte is not None and curr_byte is not None:
            delta = (curr_byte - prev_byte) % 256
            deltas.append(delta)
```

### Step 3: Pattern Analysis
```python
# Count delta occurrences
delta_counts = defaultdict(int)
for delta in deltas:
    delta_counts[delta] += 1

# Calculate scores
monotonicity_score = delta_counts.get(1, 0) / len(deltas)
wrap_count = sum(1 for i in range(1, len(deltas)) if deltas[i] == 0 and deltas[i-1] == 255)
low_randomness = sum(1 for delta in deltas if 1 ≤ delta ≤ 5)
```

### Step 4: Bit-field Analysis
```python
for bit_start in range(0, 8, 2):
    for bit_width in [2, 4, 8]:
        if bit_start + bit_width > 8:
            continue
        
        # Extract bitfield and analyze
        bitfield = []
        for frame in frames:
            bitfield.append(frame.get_bit_field(byte_pos, bit_start, bit_width))
        
        # Analyze bitfield for counter patterns
        # (Implementation would go here)
```

## Edge Cases

### Constant Values
- If all bytes are the same, score = 0
- No monotonic behavior detected

### Random Data
- Low monotonicity score
- No consistent patterns
- Low confidence

### Small Sample Size
- Minimum 20 frames required per ID
- Insufficient data returns no results

## Output Format

### Detection Result
```python
{
    'algorithm': 'rolling_counter_monotonic',
    'confidence': 0.94,
    'explanation': 'Byte 7 increments by 1 in 94% of transitions and wraps every 256 frames.',
    'byte_position': 7,
    'cycle_length': 256
}
```

### Bit-field Result
```python
{
    'algorithm': 'rolling_counter_modulo',
    'confidence': 0.87,
    'explanation': 'Bits 4-7 form a 4-bit counter incrementing by 1 in 87% of transitions.',
    'byte_position': 3,
    'bit_range': (4, 7),
    'cycle_length': 16
}
```

## Performance Considerations

- O(n) complexity per byte position
- Efficient data structures for counting
- Early termination for low-confidence candidates
- Parallel processing possible for multiple IDs