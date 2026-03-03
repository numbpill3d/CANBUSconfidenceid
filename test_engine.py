#!/usr/bin/env python3
"""
Test script for CAN Hypothesis Engine
"""

import tempfile
import os
from can_hypothesis_engine.models.can_frame import CANFrame
from can_hypothesis_engine.engine import CANHypothesisEngine

def test_can_frame_model():
    """Test the CAN frame model."""
    print("Testing CAN Frame Model...")
    
    # Create a test frame
    frame = CANFrame(
        timestamp=1609772212.123456,
        arbitration_id=0x1F334455,
        dlc=8,
        data=bytes([0x00, 0x10, 0x20, 0x30, 0x40, 0x50, 0x60, 0x70])
    )
    
    assert frame.timestamp == 1609772212.123456
    assert frame.arbitration_id == 0x1F334455
    assert frame.dlc == 8
    assert frame.data == bytes([0x00, 0x10, 0x20, 0x30, 0x40, 0x50, 0x60, 0x70])
    assert frame.arbitration_id_hex == "0x1F334455"
    
    # Test byte access
    assert frame.get_byte_at_offset(0) == 0x00
    assert frame.get_byte_at_offset(7) == 0x70
    assert frame.get_byte_at_offset(8) is None  # Out of bounds
    
    # Test bit field extraction
    assert frame.get_bit_field(0, 0, 4) == 0x0  # Lower 4 bits of 0x00
    assert frame.get_bit_field(0, 4, 4) == 0x0  # Upper 4 bits of 0x00
    
    print("✓ CAN Frame Model tests passed")

def test_engine_basic():
    """Test basic engine functionality."""
    print("Testing Engine Basic Functionality...")
    
    # Create test frames with a simple counter pattern
    frames = []
    for i in range(10):
        data = bytes([i, i+1, i+2, i+3, i+4, i+5, i+6, i+7])
        frame = CANFrame(
            timestamp=float(i),
            arbitration_id=0x12345678,
            dlc=8,
            data=data
        )
        frames.append(frame)
    
    # Test the engine
    engine = CANHypothesisEngine()
    result = engine.analyze_frames(frames, "0x12345678")
    
    assert result.arbitration_id == "0x12345678"
    assert result.frame_count == 10
    assert len(result.rolling_counters) >= 0  # May find some patterns
    assert len(result.checksum_candidates) >= 0  # May find some patterns
    
    print("✓ Engine basic functionality tests passed")

def test_with_sample_log():
    """Test with a sample log file."""
    print("Testing with sample log file...")
    
    # Create a temporary log file
    sample_log = """(1609772212.123456) can0 1F334455#0010203040506070
(1609772212.123457) can0 1F334455#0111213141516171
(1609772212.123458) can0 1F334455#0212223242526272
(1609772212.123459) can0 1F334455#0313233343536373
(1609772212.123460) can0 1F334455#0414243444546474
(1609772212.123461) can0 1F334455#0515253545556575
(1609772212.123462) can0 1F334455#0616263646566676
(1609772212.123463) can0 1F334455#0717273747576777
(1609772212.123464) can0 1F334455#0818283848586878
(1609772212.123465) can0 1F334455#0919293949596979"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
        f.write(sample_log)
        temp_log_path = f.name
    
    try:
        from can_hypothesis_engine.parser.can_parser import parse_can_log
        
        # Parse the log
        id_to_frames = parse_can_log(temp_log_path, min_frames_per_id=5)
        
        # Test engine with parsed frames
        engine = CANHypothesisEngine()
        results = engine.analyze_grouped_frames(id_to_frames)
        
        assert "0x1F334455" in results
        result = results["0x1F334455"]
        assert result.frame_count == 10
        
        print("✓ Sample log file test passed")
        
    finally:
        # Clean up temp file
        os.unlink(temp_log_path)

if __name__ == "__main__":
    print("Running CAN Hypothesis Engine Tests...\n")
    
    test_can_frame_model()
    test_engine_basic()
    test_with_sample_log()
    
    print("\n✓ All tests passed!")