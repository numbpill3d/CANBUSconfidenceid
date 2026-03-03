"""
Checksum Detection Algorithms
"""

from typing import List, Dict, Optional
from ..models.analysis_results import ChecksumCandidate, DetectionAlgorithm
import math


def detect_checksums(frames: List['CANFrame']) -> List[ChecksumCandidate]:
    """
    Detect checksum patterns in CAN frame data using various algorithms.
    
    Args:
        frames: List of CAN frames to analyze
        
    Returns:
        List of ChecksumCandidate objects representing detected checksums
    """
    if len(frames) < 20:
        return []  # Need minimum 20 frames for reliable analysis
    
    candidates = []
    
    # Test each byte position as a potential checksum byte (0-7)
    for checksum_pos in range(8):
        # Skip if any frame doesn't have this byte
        if not all(frame.get_byte_at_offset(checksum_pos) is not None for frame in frames):
            continue
            
        # Test each checksum algorithm
        algorithms = [
            ("xor", lambda data: _calculate_xor_checksum(data)),
            ("additive", lambda data: _calculate_additive_checksum(data)),
            ("inverted_sum", lambda data: _calculate_inverted_sum_checksum(data)),
            ("ones_complement", lambda data: _calculate_ones_complement_checksum(data)),
        ]
        
        # For each algorithm, test if it matches the checksum byte
        for algorithm_name, checksum_func in algorithms:
            matches = 0
            covered_bytes = []
            
            # Try different combinations of bytes as covered bytes
            for num_covered in range(1, min(8, checksum_pos) + 1):
                # Try different starting positions
                for start_byte in range(0, checksum_pos - num_covered + 1):
                    covered_bytes = list(range(start_byte, start_byte + num_covered))
                    
                    # Calculate checksum for each frame
                    valid_frames = 0
                    for frame in frames:
                        # Get data bytes for covered range
                        data_bytes = []
                        for pos in covered_bytes:
                            byte_val = frame.get_byte_at_offset(pos)
                            if byte_val is not None:
                                data_bytes.append(byte_val)
                        
                        if len(data_bytes) == num_covered:
                            valid_frames += 1
                            calculated_checksum = checksum_func(data_bytes)
                            actual_checksum = frame.get_byte_at_offset(checksum_pos)
                            
                            if calculated_checksum == actual_checksum:
                                matches += 1
                    
                    if valid_frames > 0:
                        match_ratio = matches / valid_frames if valid_frames > 0 else 0
                        
                        # Only consider if match ratio is high enough
                        if match_ratio > 0.8:
                            # Calculate confidence score
                            confidence = match_ratio * 0.7 + 0.3 * (len(covered_bytes) / 8)
                            
                            # Generate explanation
                            explanation = _generate_checksum_explanation(
                                algorithm_name, checksum_pos, covered_bytes, match_ratio, confidence
                            )
                            
                            # Create candidate
                            candidate = ChecksumCandidate(
                                algorithm=getattr(DetectionAlgorithm, f"CHECKSUM_{algorithm_name.upper()}"),
                                checksum_position=checksum_pos,
                                covered_bytes=covered_bytes,
                                confidence=confidence,
                                explanation=explanation,
                                match_ratio=match_ratio,
                                byte_positions=[checksum_pos] + covered_bytes
                            )
                            candidates.append(candidate)
    
    # Also test CRC8 algorithms
    crc_candidates = _detect_crc8(frames)
    candidates.extend(crc_candidates)
    
    return candidates


def _calculate_xor_checksum(data_bytes: List[int]) -> int:
    """Calculate XOR checksum of data bytes."""
    checksum = 0
    for byte in data_bytes:
        checksum ^= byte
    return checksum


def _calculate_additive_checksum(data_bytes: List[int]) -> int:
    """Calculate additive checksum of data bytes."""
    return sum(data_bytes) % 256


def _calculate_inverted_sum_checksum(data_bytes: List[int]) -> int:
    """Calculate inverted sum checksum of data bytes."""
    return (~sum(data_bytes)) & 0xFF


def _calculate_ones_complement_checksum(data_bytes: List[int]) -> int:
    """Calculate ones complement checksum of data bytes."""
    total = sum(data_bytes)
    # Handle carry bits
    while total >> 8:
        total = (total & 0xFF) + (total >> 8)
    return ~total & 0xFF


def _detect_crc8(frames: List['CANFrame']) -> List[ChecksumCandidate]:
    """
    Detect CRC8 checksum patterns in CAN frame data.
    
    Args:
        frames: List of CAN frames to analyze
        
    Returns:
        List of ChecksumCandidate objects representing detected CRC8 checksums
    """
    candidates = []
    
    # Common automotive CRC8 polynomials
    polynomials = [0x07, 0x1D, 0x2F, 0x31, 0x9B]
    
    # Test each byte position as a potential checksum byte (0-7)
    for checksum_pos in range(8):
        # Skip if any frame doesn't have this byte
        if not all(frame.get_byte_at_offset(checksum_pos) is not None for frame in frames):
            continue
            
        # Try different combinations of bytes as covered bytes
        for num_covered in range(1, min(8, checksum_pos) + 1):
            # Try different starting positions
            for start_byte in range(0, checksum_pos - num_covered + 1):
                covered_bytes = list(range(start_byte, start_byte + num_covered))
                
                # Test each polynomial
                for poly in polynomials:
                    matches = 0
                    valid_frames = 0
                    
                    # Calculate CRC8 for each frame
                    for frame in frames:
                        # Get data bytes for covered range
                        data_bytes = []
                        for pos in covered_bytes:
                            byte_val = frame.get_byte_at_offset(pos)
                            if byte_val is not None:
                                data_bytes.append(byte_val)
                        
                        if len(data_bytes) == num_covered:
                            valid_frames += 1
                            calculated_checksum = _calculate_crc8(data_bytes, poly)
                            actual_checksum = frame.get_byte_at_offset(checksum_pos)
                            
                            if calculated_checksum == actual_checksum:
                                matches += 1
                    
                    if valid_frames > 0:
                        match_ratio = matches / valid_frames if valid_frames > 0 else 0
                        
                        # Only consider if match ratio is high enough
                        if match_ratio > 0.8:
                            # Calculate confidence score
                            confidence = match_ratio * 0.7 + 0.3 * (len(covered_bytes) / 8)
                            
                            # Generate explanation
                            explanation = _generate_crc8_explanation(
                                checksum_pos, covered_bytes, poly, match_ratio, confidence
                            )
                            
                            # Create candidate
                            candidate = ChecksumCandidate(
                                algorithm=DetectionAlgorithm.CHECKSUM_CRC8,
                                checksum_position=checksum_pos,
                                covered_bytes=covered_bytes,
                                confidence=confidence,
                                explanation=explanation,
                                match_ratio=match_ratio,
                                polynomial=f"0x{poly:02X}",
                                byte_positions=[checksum_pos] + covered_bytes
                            )
                            candidates.append(candidate)
    
    return candidates


def _calculate_crc8(data_bytes: List[int], polynomial: int) -> int:
    """
    Calculate CRC8 checksum using the specified polynomial.
    
    Args:
        data_bytes: List of data bytes
        polynomial: CRC8 polynomial
        
    Returns:
        Calculated CRC8 value
    """
    crc = 0
    for byte in data_bytes:
        crc ^= byte
        for _ in range(8):
            if crc & 0x80:
                crc = (crc << 1) ^ polynomial
            else:
                crc <<= 1
            crc &= 0xFF
    return crc


def _generate_checksum_explanation(
    algorithm_name: str,
    checksum_pos: int,
    covered_bytes: List[int],
    match_ratio: float,
    confidence: float
) -> str:
    """Generate a human-readable explanation for checksum detection."""
    algorithm_map = {
        "xor": "XOR",
        "additive": "additive",
        "inverted_sum": "inverted sum",
        "ones_complement": "ones complement"
    }
    
    algorithm_display = algorithm_map.get(algorithm_name, algorithm_name)
    
    if len(covered_bytes) == 1:
        covered_text = f"byte {covered_bytes[0]}"
    else:
        covered_text = f"bytes {', '.join(map(str, covered_bytes))}"
    
    return f"Byte {checksum_pos} matches {algorithm_display} of {covered_text} in {match_ratio:.0%} of frames with {confidence:.0%} confidence"


def _generate_crc8_explanation(
    checksum_pos: int,
    covered_bytes: List[int],
    polynomial: int,
    match_ratio: float,
    confidence: float
) -> str:
    """Generate a human-readable explanation for CRC8 detection."""
    if len(covered_bytes) == 1:
        covered_text = f"byte {covered_bytes[0]}"
    else:
        covered_text = f"bytes {', '.join(map(str, covered_bytes))}"
    
    return f"Byte {checksum_pos} matches CRC8 polynomial 0x{polynomial:02X} of {covered_text} in {match_ratio:.0%} of frames with {confidence:.0%} confidence"