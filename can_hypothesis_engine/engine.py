"""
Main CAN Hypothesis Engine
"""

from typing import Dict, List, Optional
from .models.can_frame import CANFrame
from .models.analysis_results import AnalysisResult
from .algorithms.rolling_counter import detect_rolling_counters, detect_modulo_counters
from .algorithms.checksum import detect_checksums
from .algorithms.entropy import calculate_entropy


class CANHypothesisEngine:
    """
    Main engine for analyzing CAN frame data and detecting rolling counters and checksums.
    """
    
    def __init__(self):
        """Initialize the CAN Hypothesis Engine."""
        pass
    
    def analyze_frames(self, frames: List[CANFrame], arbitration_id: str) -> AnalysisResult:
        """
        Analyze a list of CAN frames for rolling counters and checksums.
        
        Args:
            frames: List of CAN frames to analyze
            arbitration_id: The arbitration ID being analyzed
            
        Returns:
            AnalysisResult object containing all findings
        """
        if not frames:
            return AnalysisResult(
                arbitration_id=arbitration_id,
                frame_count=0,
                rolling_counters=[],
                checksum_candidates=[],
                multi_byte_candidates=[],
                entropy_summary=[]
            )
        
        # Detect rolling counters
        rolling_counters = detect_rolling_counters(frames)
        
        # Detect modulo counters
        modulo_counters = detect_modulo_counters(frames)
        rolling_counters.extend(modulo_counters)
        
        # Detect checksums
        checksum_candidates = detect_checksums(frames)
        
        # Calculate entropy
        entropy_summary = calculate_entropy(frames)
        
        # Create and return analysis result
        return AnalysisResult(
            arbitration_id=arbitration_id,
            frame_count=len(frames),
            rolling_counters=rolling_counters,
            checksum_candidates=checksum_candidates,
            multi_byte_candidates=[],  # Placeholder for future implementation
            entropy_summary=entropy_summary
        )
    
    def analyze_grouped_frames(self, id_to_frames: Dict[str, List[CANFrame]]) -> Dict[str, AnalysisResult]:
        """
        Analyze grouped CAN frames by arbitration ID.
        
        Args:
            id_to_frames: Dictionary mapping arbitration IDs to lists of frames
            
        Returns:
            Dictionary mapping arbitration IDs to AnalysisResult objects
        """
        results = {}
        for arb_id, frames in id_to_frames.items():
            results[arb_id] = self.analyze_frames(frames, arb_id)
        return results