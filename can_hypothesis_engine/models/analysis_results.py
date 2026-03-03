"""
Analysis Result Models
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
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


@dataclass
class RollingCounterCandidate(DetectionCandidate):
    """Represents a potential rolling counter detection."""
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


@dataclass
class ChecksumCandidate(DetectionCandidate):
    """Represents a potential checksum detection."""
    checksum_position: int  # Position of the checksum byte (0-7)
    covered_bytes: List[int]  # Positions of bytes that contribute to this checksum
    polynomial: Optional[str] = None  # For CRC algorithms, the polynomial used
    match_ratio: float = 0.0  # Ratio of frames where calculated checksum matches


@dataclass
class MultiByteCandidate(DetectionCandidate):
    """Represents a potential multi-byte signal detection."""
    start_byte: int  # Starting byte position (0-7)
    end_byte: int    # Ending byte position (start_byte to 7)
    is_little_endian: bool = True  # Endianness of the multi-byte value
    variance: float = 0.0  # Variance of the combined value over time
    smoothness: float = 0.0  # Average absolute delta between consecutive values
    monotonic_ratio: float = 0.0  # Ratio of monotonic changes


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


@dataclass
class AnalysisResult:
    """Complete analysis result for a single arbitration ID."""
    arbitration_id: str  # Hex string like "0x1F334455"
    frame_count: int     # Number of frames analyzed
    rolling_counters: List[RollingCounterCandidate] = field(default_factory=list)
    checksum_candidates: List[ChecksumCandidate] = field(default_factory=list)
    multi_byte_candidates: List[MultiByteCandidate] = field(default_factory=list)
    entropy_summary: List[EntropySummary] = field(default_factory=list)
    
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