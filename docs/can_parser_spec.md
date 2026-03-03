# CAN Log Parser Implementation Specification

## Overview
The CAN log parser will handle standard Linux `candump` format logs supporting both compact and bracketed formats.

## Supported Formats

### Compact Format
```
(1609772212.123456) can0 1F334455#0010203040506070
```

### Bracketed Format
```
can0 1F334455 [8] 00 10 20 30 40 50 60 70
```

## Parser Implementation

### Core Parser Function
```python
import re
from typing import Generator, Optional
from .frame import CANFrame

def parse_can_log(file_path: str, min_frames_per_id: int = 20) -> dict[str, list[CANFrame]]:
    """
    Parse a CAN log file and return frames grouped by arbitration ID.
    
    Args:
        file_path: Path to the CAN log file
        min_frames_per_id: Minimum number of frames required for analysis
        
    Returns:
        Dictionary mapping arbitration ID (hex string) to list of CANFrames
    """
    # Precompile regex patterns for efficiency
    compact_pattern = re.compile(r'\(([\d.]+)\)\s+\w+\s+([0-9A-Fa-f]+)#([0-9A-Fa-f]*)')
    bracketed_pattern = re.compile(r'\w+\s+([0-9A-Fa-f]+)\s+\[([\d]+)\]\s+([0-9A-Fa-f\s]*)')
    
    id_to_frames = {}
    
    with open(file_path, 'r') as f:
        for line_num, line in enumerate(f, 1):
            try:
                frame = _parse_line(line.strip(), compact_pattern, bracketed_pattern)
                if frame:
                    id_str = frame.arbitration_id_hex
                    if id_str not in id_to_frames:
                        id_to_frames[id_str] = []
                    id_to_frames[id_str].append(frame)
            except Exception as e:
                # Log warning for malformed line but continue processing
                print(f"Warning: Skipping malformed line {line_num}: {line.strip()} - {str(e)}")
                continue
    
    # Filter out IDs with insufficient frames
    filtered_results = {
        arb_id: frames 
        for arb_id, frames in id_to_frames.items() 
        if len(frames) >= min_frames_per_id
    }
    
    return filtered_results

def _parse_line(line: str, compact_pattern: re.Pattern, bracketed_pattern: re.Pattern) -> Optional[CANFrame]:
    """
    Parse a single line from the CAN log file.
    
    Args:
        line: A single line from the log file
        compact_pattern: Precompiled regex for compact format
        bracketed_pattern: Precompiled regex for bracketed format
        
    Returns:
        CANFrame object if parsing succeeds, None otherwise
    """
    # Try compact format first
    compact_match = compact_pattern.match(line)
    if compact_match:
        timestamp_str, id_str, data_str = compact_match.groups()
        try:
            timestamp = float(timestamp_str)
            arbitration_id = int(id_str, 16)
            
            # Convert hex data string to bytes
            if data_str:
                # Pad odd-length hex strings with leading zero
                if len(data_str) % 2:
                    data_str = '0' + data_str
                data = bytes.fromhex(data_str)
            else:
                data = b''
            
            dlc = len(data)
            return CANFrame(timestamp=timestamp, arbitration_id=arbitration_id, dlc=dlc, data=data)
        except ValueError:
            return None
    
    # Try bracketed format
    bracketed_match = bracketed_pattern.match(line)
    if bracketed_match:
        id_str, dlc_str, data_str = bracketed_match.groups()
        try:
            arbitration_id = int(id_str, 16)
            dlc = int(dlc_str)
            
            # Process data bytes (space-separated hex values)
            if data_str.strip():
                data_parts = data_str.split()
                data_bytes = []
                for part in data_parts:
                    if part:  # Skip empty parts
                        data_bytes.append(int(part, 16))
                data = bytes(data_bytes)
            else:
                data = b''
            
            # Use the smaller of parsed DLC or actual data length
            dlc = min(dlc, len(data))
            
            return CANFrame(timestamp=None, arbitration_id=arbitration_id, dlc=dlc, data=data)
        except ValueError:
            return None
    
    # Line doesn't match either format
    return None

def stream_parse_can_log(file_path: str, chunk_size: int = 8192) -> Generator[CANFrame, None, None]:
    """
    Stream-parse a CAN log file, yielding frames one at a time.
    
    Args:
        file_path: Path to the CAN log file
        chunk_size: Size of chunks to read at a time
        
    Yields:
        CANFrame objects as they are parsed
    """
    compact_pattern = re.compile(r'\(([\d.]+)\)\s+\w+\s+([0-9A-Fa-f]+)#([0-9A-Fa-f]*)')
    bracketed_pattern = re.compile(r'\w+\s+([0-9A-Fa-f]+)\s+\[([\d]+)\]\s+([0-9A-Fa-f\s]*)')
    
    with open(file_path, 'r') as f:
        buffer = ""
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                # Process remaining buffer content
                lines = buffer.split('\n')
                for i, line in enumerate(lines):
                    if i == len(lines) - 1 and buffer and not chunk:  # Last line without newline
                        # Process incomplete line if it exists
                        if line.strip():
                            frame = _parse_line(line.strip(), compact_pattern, bracketed_pattern)
                            if frame:
                                yield frame
                    elif line.strip():
                        frame = _parse_line(line.strip(), compact_pattern, bracketed_pattern)
                        if frame:
                            yield frame
                break
            
            buffer += chunk
            lines = buffer.split('\n')
            
            # Process all complete lines (all except the last one)
            for line in lines[:-1]:
                if line.strip():
                    frame = _parse_line(line.strip(), compact_pattern, bracketed_pattern)
                    if frame:
                        yield frame
            
            # Keep the last (potentially incomplete) line in buffer
            buffer = lines[-1]

def group_frames_by_id(frames: Generator[CANFrame, None, None], min_frames_per_id: int = 20) -> dict[str, list[CANFrame]]:
    """
    Group streamed frames by arbitration ID.
    
    Args:
        frames: Generator of CANFrame objects
        min_frames_per_id: Minimum number of frames required for analysis
        
    Returns:
        Dictionary mapping arbitration ID to list of frames
    """
    id_to_frames = {}
    
    for frame in frames:
        id_str = frame.arbitration_id_hex
        if id_str not in id_to_frames:
            id_to_frames[id_str] = []
        id_to_frames[id_str].append(frame)
    
    # Filter out IDs with insufficient frames
    return {
        arb_id: frames 
        for arb_id, frames in id_to_frames.items() 
        if len(frames) >= min_frames_per_id
    }
```

## Key Features

1. **Format Flexibility**: Handles both compact and bracketed candump formats
2. **Error Tolerance**: Skips malformed lines without crashing
3. **Memory Efficiency**: Streaming parser for large files
4. **Frame Filtering**: Automatically filters IDs with insufficient frames
5. **Data Normalization**: Ensures consistent data representation

## Error Handling

- Malformed lines are logged with line numbers and skipped
- Invalid hex values cause the line to be skipped
- Incomplete frames are handled gracefully
- DLC mismatches between header and actual data are resolved

## Performance Considerations

- Precompiled regex patterns for efficiency
- Streaming processing to handle large files
- Efficient data structure usage
- Early filtering of insufficient frame IDs