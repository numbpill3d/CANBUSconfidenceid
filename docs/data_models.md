# CAN Hypothesis Engine - Data Models

## Core Data Models

### CANFrame
Represents a single CAN frame parsed from the log file.

```python
from dataclasses import dataclass
from typing import Optional
import struct

@dataclass
class CANFrame:
    """Represents a single CAN frame parsed from the log file."""
    timestamp: Optional[float]  # Unix timestamp (seconds) or None if not present
    arbitration_id: int        # 11 or 29-bit identifier
    dlc: int                  # Data Length Code (0-8)
    data: bytes               # Payload (0-8 bytes)
    
    def __post_init__(self):
        # Ensure data is padded to dlc length if shorter
        if len(self.data) < self.dlc:
            self.data = self.data.ljust(self.dlc, b'\x00')
        # Truncate if longer than dlc
        elif len(self.data) > self.dlc:
            self.data = self.data[:self.dlc]
    
    @property
    def arbitration_id_hex(self) -> str:
        """Return arbitration ID as hex string with 0x prefix."""
        return f"0x{self.arbitration_id:X}"
    
    def get_byte_at_offset(self, offset: int) -> Optional[int]:
        """Get byte value at specific offset, or None if offset out of bounds."""
        if 0 <= offset < len(self.data):
            return self.data[offset]
        return None
    
    def get_bit_field(self, byte_offset: int, start_bit: int, num_bits: int) -> Optional[int]:
        """Extract a bit field from the specified byte."""
        if 0 <= byte_offset < len(self.data):
            byte_val = self.data[byte_offset]
            mask = (1 << num_bits) - 1  # Create mask with num_bits set to 1
            shifted = byte_val >> start_bit
            return shifted & mask
        return None
```

### Analysis Result Models

#### Base Result Classes
```python
from enum import Enum
from typing import List, Dict, Any
import json

class DetectionAlgorithm(Enum):
    """Enumeration of different detection algorithms."""
    ROLLING_COUNTER_MONOTONIC = "rolling_counter_monotonic"
    ROLLING_COUNTER_WRAP = "rolling_counter_wrap"
    ROLLING_COUNTER_MODULO = "rolling_counter_modulo"
    CHECKSUM_XOR = "checksum_xor"
    CHECKSUM_ADDITIVE = "checksum_additive"
    CHECKSUM_INVERTED_SUM = "checksum_inverted_sum"
    CHECKSUM_ONES_COMPLEMENT = "checksum_ones_complement"
    CHECKSUM_CRC8 = "checksum_crc8"
    MULTI_BYTE_LINEAR = "multi_byte_linear"
    MULTI_BYTE_SMOOTH = "multi_byte_smooth"

@dataclass
class DetectionCandidate:
    """Base class for all detection candidates."""
    algorithm: DetectionAlgorithm
    confidence: float  # 0.0 to 1.0
    explanation: str
    byte_positions: List[int]  # Which byte positions this candidate relates to
```

#### Rolling Counter Candidate
```python
@dataclass
class RollingCounterCandidate(DetectionCandidate):
    """Represents a potential rolling counter detection."""
    algorithm: DetectionAlgorithm = DetectionAlgorithm.ROLLING_COUNTER_MONOTONIC
    byte_position: int  # Single byte position (0-7)
    cycle_length: Optional[int] = None  # Expected cycle length (e.g., 256 for full byte, 16 for nibble)
    increment_pattern: Optional[List[int]] = None  # Common increments observed
    wrap_points: Optional[List[int]] = None  # Values where wrapping occurs
    
    def __post_init__(self):
        if self.algorithm not in [
            DetectionAlgorithm.ROLLING_COUNTER_MONOTONIC,
            DetectionAlgorithm.ROLLING_COUNTER_WRAP,
            DetectionAlgorithm.ROLLING_COUNTER_MODULO
        ]:
            raise ValueError("algorithm must be a rolling counter type")
```

#### Checksum Candidate
```python
@dataclass
class ChecksumCandidate(DetectionCandidate):
    """Represents a potential checksum detection."""
    algorithm: DetectionAlgorithm = DetectionAlgorithm.CHECKSUM_XOR
    checksum_position: int  # Position of the checksum byte (0-7)
    covered_bytes: List[int]  # Positions of bytes that contribute to this checksum
    polynomial: Optional[str] = None  # For CRC algorithms, the polynomial used
    match_ratio: float = 0.0  # Ratio of frames where calculated checksum matches
    
    def __post_init__(self):
        if self.algorithm not in [
            DetectionAlgorithm.CHECKSUM_XOR,
            DetectionAlgorithm.CHECKSUM_ADDITIVE,
            DetectionAlgorithm.CHECKSUM_INVERTED_SUM,
            DetectionAlgorithm.CHECKSUM_ONES_COMPLEMENT,
            DetectionAlgorithm.CHECKSUM_CRC8
        ]:
            raise ValueError("algorithm must be a checksum type")
```

#### Multi-byte Candidate
```python
@dataclass
class MultiByteCandidate(DetectionCandidate):
    """Represents a potential multi-byte signal detection."""
    algorithm: DetectionAlgorithm = DetectionAlgorithm.MULTI_BYTE_LINEAR
    start_byte: int  # Starting byte position (0-7)
    end_byte: int    # Ending byte position (start_byte to 7)
    is_little_endian: bool = True  # Endianness of the multi-byte value
    variance: float = 0.0  # Variance of the combined value over time
    smoothness: float = 0.0  # Average absolute delta between consecutive values
    monotonic_ratio: float = 0.0  # Ratio of monotonic changes
    
    def __post_init__(self):
        if self.algorithm not in [
            DetectionAlgorithm.MULTI_BYTE_LINEAR,
            DetectionAlgorithm.MULTI_BYTE_SMOOTH
        ]:
            raise ValueError("algorithm must be a multi-byte type")
        if self.start_byte >= self.end_byte or self.end_byte > 7:
            raise ValueError("Invalid byte range for multi-byte candidate")
```

#### Entropy Summary
```python
@dataclass
class EntropySummary:
    """Summary of entropy analysis for each byte position."""
    byte_position: int  # Position (0-7)
    entropy: float     # Shannon entropy value (0.0 to 8.0)
    interpretation: str  # Human-readable interpretation
    
    @staticmethod
    def interpret_entropy(entropy: float) -> str:
        """Provide interpretation based on entropy value."""
        if entropy < 1.0:
            return "Low entropy - likely constant or flag"
        elif entropy < 3.0:
            return "Medium-low entropy - possibly structured data"
        elif entropy < 5.0:
            return "Medium entropy - possibly numeric with patterns"
        elif entropy < 7.0:
            return "Medium-high entropy - possibly complex data"
        else:
            return "High entropy - possibly random, checksum, or encrypted data"
```

### Main Analysis Result
```python
@dataclass
class AnalysisResult:
    """Complete analysis result for a single arbitration ID."""
    arbitration_id: str  # Hex string like "0x1F334455"
    frame_count: int     # Number of frames analyzed
    rolling_counters: List[RollingCounterCandidate]
    checksum_candidates: List[ChecksumCandidate]
    multi_byte_candidates: List[MultiByteCandidate]
    entropy_summary: List[EntropySummary]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "arbitration_id": self.arbitration_id,
            "frame_count": self.frame_count,
            "rolling_counters": [
                {
                    "algorithm": candidate.algorithm.value,
                    "confidence": candidate.confidence,
                    "explanation": candidate.explanation,
                    "byte_position": candidate.byte_position,
                    "cycle_length": candidate.cycle_length,
                    "increment_pattern": candidate.increment_pattern,
                    "wrap_points": candidate.wrap_points
                }
                for candidate in sorted(self.rolling_counters, key=lambda x: x.confidence, reverse=True)
            ],
            "checksum_candidates": [
                {
                    "algorithm": candidate.algorithm.value,
                    "confidence": candidate.confidence,
                    "explanation": candidate.explanation,
                    "checksum_position": candidate.checksum_position,
                    "covered_bytes": candidate.covered_bytes,
                    "polynomial": candidate.polynomial,
                    "match_ratio": candidate.match_ratio
                }
                for candidate in sorted(self.checksum_candidates, key=lambda x: x.confidence, reverse=True)
            ],
            "multi_byte_candidates": [
                {
                    "algorithm": candidate.algorithm.value,
                    "confidence": candidate.confidence,
                    "explanation": candidate.explanation,
                    "start_byte": candidate.start_byte,
                    "end_byte": candidate.end_byte,
                    "is_little_endian": candidate.is_little_endian,
                    "variance": candidate.variance,
                    "smoothness": candidate.smoothness,
                    "monotonic_ratio": candidate.monotonic_ratio
                }
                for candidate in sorted(self.multi_byte_candidates, key=lambda x: x.confidence, reverse=True)
            ],
            "entropy_summary": [
                {
                    "byte_position": summary.byte_position,
                    "entropy": summary.entropy,
                    "interpretation": summary.interpretation
                }
                for summary in sorted(self.entropy_summary, key=lambda x: x.byte_position)
            ]
        }
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    def to_human_readable(self) -> str:
        """Generate human-readable report."""
        lines = []
        lines.append(f"Analysis Results for ID {self.arbitration_id} ({self.frame_count} frames)")
        lines.append("=" * 60)
        
        # Rolling counters
        if self.rolling_counters:
            lines.append("\nROLLING COUNTERS:")
            for i, candidate in enumerate(sorted(self.rolling_counters, key=lambda x: x.confidence, reverse=True)):
                lines.append(f"  {i+1}. {candidate.explanation}")
                lines.append(f"     Confidence: {candidate.confidence:.2f}")
                lines.append(f"     Algorithm: {candidate.algorithm.value}")
                if candidate.cycle_length:
                    lines.append(f"     Cycle Length: {candidate.cycle_length}")
                lines.append("")
        
        # Checksum candidates
        if self.checksum_candidates:
            lines.append("CHECKSUM CANDIDATES:")
            for i, candidate in enumerate(sorted(self.checksum_candidates, key=lambda x: x.confidence, reverse=True)):
                lines.append(f"  {i+1}. {candidate.explanation}")
                lines.append(f"     Confidence: {candidate.confidence:.2f}")
                lines.append(f"     Algorithm: {candidate.algorithm.value}")
                lines.append(f"     Match Ratio: {candidate.match_ratio:.2f}")
                if candidate.polynomial:
                    lines.append(f"     Polynomial: {candidate.polynomial}")
                lines.append("")
        
        # Multi-byte candidates
        if self.multi_byte_candidates:
            lines.append("MULTI-BYTE SIGNALS:")
            for i, candidate in enumerate(sorted(self.multi_byte_candidates, key=lambda x: x.confidence, reverse=True)):
                lines.append(f"  {i+1}. {candidate.explanation}")
                lines.append(f"     Confidence: {candidate.confidence:.2f}")
                lines.append(f"     Algorithm: {candidate.algorithm.value}")
                lines.append(f"     Range: Bytes {candidate.start_byte}-{candidate.end_byte}")
                lines.append(f"     Endianness: {'Little' if candidate.is_little_endian else 'Big'}")
                lines.append(f"     Variance: {candidate.variance:.2f}")
                lines.append(f"     Smoothness: {candidate.smoothness:.2f}")
                lines.append("")
        
        # Entropy summary
        if self.entropy_summary:
            lines.append("ENTROPY SUMMARY:")
            for summary in sorted(self.entropy_summary, key=lambda x: x.byte_position):
                lines.append(f"  Byte {summary.byte_position}: "
                           f"Entropy={summary.entropy:.2f}, "
                           f"Interpretation='{summary.interpretation}'")
        
        return "\n".join(lines)
```

## Usage Example

```python
# Example instantiation of models
frame = CANFrame(
    timestamp=1609772212.123456,
    arbitration_id=0x1F334455,
    dlc=8,
    data=bytes([0x00, 0x10, 0x20, 0x30, 0x40, 0x50, 0x60, 0x70])
)

counter_candidate = RollingCounterCandidate(
    byte_position=7,
    confidence=0.94,
    explanation="Byte 7 increments by 1 in 94% of transitions and wraps every 256 frames.",
    cycle_length=256
)

checksum_candidate = ChecksumCandidate(
    checksum_position=6,
    covered_bytes=[0, 1, 2, 3, 4, 5],
    confidence=0.92,
    explanation="Byte 6 matches XOR of bytes 0-5 in 92% of frames.",
    match_ratio=0.92,
    algorithm=DetectionAlgorithm.CHECKSUM_XOR
)

result = AnalysisResult(
    arbitration_id="0x1F334455",
    frame_count=100,
    rolling_counters=[counter_candidate],
    checksum_candidates=[checksum_candidate],
    multi_byte_candidates=[],
    entropy_summary=[]
)

print(result.to_human_readable())