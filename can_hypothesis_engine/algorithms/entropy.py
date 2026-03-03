"""
Entropy Analysis Module
"""

from typing import List, Dict
from ..models.analysis_results import EntropySummary
import math


def calculate_entropy(frames: List['CANFrame']) -> List[EntropySummary]:
    """
    Calculate Shannon entropy for each byte position in the frames.
    
    Args:
        frames: List of CAN frames to analyze
        
    Returns:
        List of EntropySummary objects for each byte position
    """
    if not frames:
        return []
    
    entropy_summaries = []
    
    # Analyze each byte position (0-7)
    for byte_pos in range(8):
        # Collect all byte values at this position
        byte_values = []
        for frame in frames:
            byte_val = frame.get_byte_at_offset(byte_pos)
            if byte_val is not None:
                byte_values.append(byte_val)
        
        if not byte_values:
            continue
            
        # Calculate frequency of each byte value (0-255)
        frequency = {}
        for val in byte_values:
            frequency[val] = frequency.get(val, 0) + 1
        
        # Calculate entropy
        total_bytes = len(byte_values)
        entropy = 0.0
        
        for count in frequency.values():
            probability = count / total_bytes
            if probability > 0:
                entropy -= probability * math.log2(probability)
        
        # Ensure entropy is within valid range (0-8)
        entropy = max(0.0, min(8.0, entropy))
        
        # Interpret entropy
        interpretation = EntropySummary.interpret_entropy(entropy)
        
        summary = EntropySummary(
            byte_position=byte_pos,
            entropy=entropy,
            interpretation=interpretation
        )
        
        entropy_summaries.append(summary)
    
    return entropy_summaries