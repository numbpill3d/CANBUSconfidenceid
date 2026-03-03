"""
Rolling Counter Detection Algorithm
"""

from typing import List, Dict, Tuple, Optional
from ..models.analysis_results import RollingCounterCandidate, DetectionAlgorithm
import math


def detect_rolling_counters(frames: List['CANFrame']) -> List[RollingCounterCandidate]:
    """
    Detect rolling counter patterns in CAN frame data.
    
    Args:
        frames: List of CAN frames to analyze
        
    Returns:
        List of RollingCounterCandidate objects representing detected counters
    """
    if len(frames) < 20:
        return []  # Need minimum 20 frames for reliable analysis
    
    candidates = []
    
    # Analyze each byte position (0-7)
    for byte_pos in range(8):
        # Skip if any frame doesn't have this byte
        if not all(frame.get_byte_at_offset(byte_pos) is not None for frame in frames):
            continue
            
        # Calculate deltas for this byte position
        deltas = []
        for i in range(1, len(frames)):
            prev_byte = frames[i-1].get_byte_at_offset(byte_pos)
            curr_byte = frames[i].get_byte_at_offset(byte_pos)
            if prev_byte is not None and curr_byte is not None:
                delta = (curr_byte - prev_byte) % 256
                deltas.append(delta)
        
        if not deltas:
            continue
            
        # Count delta occurrences
        delta_counts = {}
        for delta in deltas:
            delta_counts[delta] = delta_counts.get(delta, 0) + 1
        
        # Calculate scores
        total_transitions = len(deltas)
        monotonicity_score = delta_counts.get(1, 0) / total_transitions if total_transitions > 0 else 0
        
        # Count wrap occurrences (from 255 to 0)
        wrap_count = 0
        for i in range(1, len(deltas)):
            if deltas[i] == 0 and deltas[i-1] == 255:
                wrap_count += 1
                
        wrap_consistency = wrap_count / total_transitions if total_transitions > 0 else 0
        
        # Count small increments (1-5)
        low_randomness = sum(1 for delta in deltas if 1 <= delta <= 5)
        low_randomness_score = low_randomness / total_transitions if total_transitions > 0 else 0
        
        # Calculate cycle repeatability (simplified)
        cycle_repeatability = 0.0
        if deltas:
            # Look for repeating patterns in deltas
            # Simple approach: check if there's a dominant delta value
            max_delta_count = max(delta_counts.values()) if delta_counts else 0
            cycle_repeatability = max_delta_count / total_transitions if total_transitions > 0 else 0
        
        # Calculate overall score
        score = 0.5 * monotonicity_score + 0.2 * wrap_consistency + 0.2 * low_randomness_score + 0.1 * cycle_repeatability
        
        # Generate explanation
        explanation = _generate_rolling_counter_explanation(
            byte_pos, score, monotonicity_score, wrap_consistency, 
            low_randomness_score, cycle_repeatability, deltas
        )
        
        # Create candidate if score is high enough
        if score > 0.5:  # Threshold for consideration
            candidate = RollingCounterCandidate(
                algorithm=DetectionAlgorithm.ROLLING_COUNTER_MONOTONIC,
                byte_position=byte_pos,
                confidence=score,
                explanation=explanation,
                byte_positions=[byte_pos],
                cycle_length=256,  # Default assumption for full byte
                increment_pattern=list(delta_counts.keys()),
                wrap_points=[d for i, d in enumerate(deltas) if i > 0 and deltas[i] == 0 and deltas[i-1] == 255]
            )
            candidates.append(candidate)
    
    return candidates


def _generate_rolling_counter_explanation(
    byte_pos: int, 
    score: float, 
    monotonicity: float, 
    wrap_consistency: float, 
    low_randomness: float, 
    cycle_repeatability: float,
    deltas: List[int]
) -> str:
    """
    Generate a human-readable explanation for the rolling counter detection.
    """
    # Determine the primary characteristic
    if monotonicity > 0.7:
        primary_char = "increments by 1"
    elif low_randomness > 0.5:
        primary_char = "has small incremental changes"
    elif wrap_consistency > 0.3:
        primary_char = "wraps consistently"
    else:
        primary_char = "shows counter-like behavior"
    
    # Determine confidence level
    if score >= 0.8:
        confidence_level = "high"
    elif score >= 0.5:
        confidence_level = "medium"
    else:
        confidence_level = "low"
    
    # Create explanation
    explanation = f"Byte {byte_pos} {primary_char} in {score:.0%} of transitions with {confidence_level} confidence"
    
    # Add more details if significant
    if monotonicity > 0.5:
        explanation += f" (monotonicity: {monotonicity:.0%})"
    if wrap_consistency > 0.2:
        explanation += f" (wrapping: {wrap_consistency:.0%})"
    if low_randomness > 0.3:
        explanation += f" (low randomness: {low_randomness:.0%})"
    
    return explanation


def detect_modulo_counters(frames: List['CANFrame']) -> List[RollingCounterCandidate]:
    """
    Detect modulo-based counters (e.g., nibble counters).
    
    Args:
        frames: List of CAN frames to analyze
        
    Returns:
        List of RollingCounterCandidate objects representing detected modulo counters
    """
    candidates = []
    
    # Analyze each byte position (0-7)
    for byte_pos in range(8):
        # Skip if any frame doesn't have this byte
        if not all(frame.get_byte_at_offset(byte_pos) is not None for frame in frames):
            continue
            
        # Analyze bit fields
        for bit_start in range(0, 8, 2):  # 0, 2, 4, 6
            for bit_width in [2, 4]:  # 2-bit and 4-bit fields
                if bit_start + bit_width > 8:
                    continue
                    
                # Extract bitfield values
                bitfield_values = []
                for frame in frames:
                    bitfield = frame.get_bit_field(byte_pos, bit_start, bit_width)
                    if bitfield is not None:
                        bitfield_values.append(bitfield)
                
                if len(bitfield_values) < 20:  # Minimum frames requirement
                    continue
                
                # Calculate deltas for bitfield
                deltas = []
                for i in range(1, len(bitfield_values)):
                    delta = (bitfield_values[i] - bitfield_values[i-1]) % (1 << bit_width)
                    deltas.append(delta)
                
                if not deltas:
                    continue
                
                # Calculate scores
                total_transitions = len(deltas)
                monotonicity_score = deltas.count(1) / total_transitions if total_transitions > 0 else 0
                
                # Count wrap occurrences
                wrap_count = 0
                for i in range(1, len(deltas)):
                    if deltas[i] == 0 and deltas[i-1] == (1 << bit_width) - 1:
                        wrap_count += 1
                        
                wrap_consistency = wrap_count / total_transitions if total_transitions > 0 else 0
                
                # Calculate score
                score = 0.6 * monotonicity_score + 0.4 * wrap_consistency
                
                # Generate explanation
                cycle_length = 1 << bit_width
                explanation = f"Bits {bit_start}-{bit_start+bit_width-1} in byte {byte_pos} form a {cycle_length}-value counter with {score:.0%} confidence"
                
                # Create candidate if score is high enough
                if score > 0.5:  # Threshold for consideration
                    candidate = RollingCounterCandidate(
                        algorithm=DetectionAlgorithm.ROLLING_COUNTER_MODULO,
                        byte_position=byte_pos,
                        confidence=score,
                        explanation=explanation,
                        byte_positions=[byte_pos],
                        cycle_length=cycle_length,
                        increment_pattern=list(set(deltas)),
                        wrap_points=[d for i, d in enumerate(deltas) if i > 0 and deltas[i] == 0 and deltas[i-1] == (1 << bit_width) - 1]
                    )
                    candidates.append(candidate)
    
    return candidates