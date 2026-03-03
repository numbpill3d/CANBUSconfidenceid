# Streaming File Processing Implementation Specification

## Overview
The streaming file processing system handles large CAN log files efficiently by processing them in chunks without loading the entire file into memory.

## Core Components

### 1. Memory-Efficient File Reader
```python
from typing import Iterator, Callable, Any
import os

class StreamingFileProcessor:
    """Handles streaming processing of large files."""
    
    def __init__(self, chunk_size: int = 8192):
        self.chunk_size = chunk_size
    
    def process_with_callback(self, file_path: str, callback: Callable[[str], Any]) -> None:
        """
        Process a file line by line with a callback function.
        
        Args:
            file_path: Path to the file to process
            callback: Function to call for each line
        """
        with open(file_path, 'r', buffering=self.chunk_size) as f:
            for line in f:
                callback(line.rstrip('\n\r'))
    
    def process_with_generator(self, file_path: str) -> Iterator[str]:
        """
        Process a file line by line using a generator.
        
        Args:
            file_path: Path to the file to process
            
        Yields:
            Each line from the file
        """
        with open(file_path, 'r', buffering=self.chunk_size) as f:
            for line in f:
                yield line.rstrip('\n\r')
```

### 2. CAN-Specific Streaming Processor
```python
from typing import Dict, List
from .frame import CANFrame
from .can_parser import _parse_line
import re

class CANStreamingProcessor(StreamingFileProcessor):
    """Specialized streaming processor for CAN log files."""
    
    def __init__(self, chunk_size: int = 8192, min_frames_per_id: int = 20):
        super().__init__(chunk_size)
        self.min_frames_per_id = min_frames_per_id
        # Precompile regex patterns
        self.compact_pattern = re.compile(r'\(([\d.]+)\)\s+\w+\s+([0-9A-Fa-f]+)#([0-9A-Fa-f]*)')
        self.bracketed_pattern = re.compile(r'\w+\s+([0-9A-Fa-f]+)\s+\[([\d]+)\]\s+([0-9A-Fa-f\s]*)')
    
    def process_can_log_streaming(self, file_path: str) -> Iterator[CANFrame]:
        """
        Stream-process a CAN log file, yielding frames one at a time.
        
        Args:
            file_path: Path to the CAN log file
            
        Yields:
            CANFrame objects as they are parsed
        """
        buffer = ""
        
        with open(file_path, 'r', buffering=self.chunk_size) as f:
            while True:
                chunk = f.read(self.chunk_size)
                if not chunk:
                    # Process any remaining content in buffer
                    if buffer:
                        lines = buffer.split('\n')
                        for line in lines:
                            if line.strip():
                                frame = _parse_line(
                                    line.strip(), 
                                    self.compact_pattern, 
                                    self.bracketed_pattern
                                )
                                if frame:
                                    yield frame
                    break
                
                buffer += chunk
                lines = buffer.split('\n')
                
                # Process all complete lines (all except the last one)
                for line in lines[:-1]:
                    if line.strip():
                        frame = _parse_line(
                            line.strip(), 
                            self.compact_pattern, 
                            self.bracketed_pattern
                        )
                        if frame:
                            yield frame
                
                # Keep the last (potentially incomplete) line in buffer
                buffer = lines[-1]
    
    def process_and_group_by_id(self, file_path: str) -> Dict[str, List[CANFrame]]:
        """
        Process a CAN log file and group frames by arbitration ID.
        
        Args:
            file_path: Path to the CAN log file
            
        Returns:
            Dictionary mapping arbitration ID to list of frames
        """
        id_to_frames: Dict[str, List[CANFrame]] = {}
        
        for frame in self.process_can_log_streaming(file_path):
            id_str = frame.arbitration_id_hex
            if id_str not in id_to_frames:
                id_to_frames[id_str] = []
            id_to_frames[id_str].append(frame)
        
        # Filter out IDs with insufficient frames
        return {
            arb_id: frames 
            for arb_id, frames in id_to_frames.items() 
            if len(frames) >= self.min_frames_per_id
        }
    
    def get_file_stats(self, file_path: str) -> Dict[str, Any]:
        """
        Get statistics about the CAN log file without processing all frames.
        
        Args:
            file_path: Path to the CAN log file
            
        Returns:
            Statistics about the file
        """
        stats = {
            'total_lines': 0,
            'parsed_frames': 0,
            'unique_ids': set(),
            'lines_skipped': 0,
            'file_size': os.path.getsize(file_path),
            'estimated_frame_count': 0
        }
        
        for line in self.process_with_generator(file_path):
            stats['total_lines'] += 1
            frame = _parse_line(line, self.compact_pattern, self.bracketed_pattern)
            if frame:
                stats['parsed_frames'] += 1
                stats['unique_ids'].add(frame.arbitration_id_hex)
            else:
                stats['lines_skipped'] += 1
        
        stats['unique_ids'] = list(stats['unique_ids'])
        return stats
```

### 3. Memory Management Utilities
```python
import sys
from typing import Optional

def get_memory_usage() -> float:
    """Get current memory usage in MB if psutil is available."""
    try:
        import psutil
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024  # MB
    except ImportError:
        # Fallback to a rough estimate if psutil not available
        return 0.0

def monitor_memory_usage(threshold_mb: float = 500.0) -> bool:
    """
    Check if memory usage exceeds threshold.
    
    Args:
        threshold_mb: Threshold in MB
        
    Returns:
        True if memory usage exceeds threshold
    """
    current_usage = get_memory_usage()
    return current_usage > threshold_mb

class MemoryEfficientAnalyzer:
    """Analyzer that monitors memory usage during processing."""
    
    def __init__(self, max_memory_mb: float = 1000.0):
        self.max_memory_mb = max_memory_mb
    
    def analyze_if_memory_available(self, file_path: str, min_frames_per_id: int = 20):
        """
        Analyze CAN log if memory usage is within limits.
        
        Args:
            file_path: Path to the CAN log file
            min_frames_per_id: Minimum frames required per ID
            
        Returns:
            Analysis results if memory available, None otherwise
        """
        if monitor_memory_usage(self.max_memory_mb):
            print(f"Memory usage exceeds {self.max_memory_mb}MB, skipping analysis")
            return None
        
        processor = CANStreamingProcessor(min_frames_per_id=min_frames_per_id)
        return processor.process_and_group_by_id(file_path)
```

### 4. Large File Handling Strategies
```python
from typing import Tuple
import mmap

class AdvancedFileProcessor(CANStreamingProcessor):
    """Advanced file processor with additional strategies for very large files."""
    
    def __init__(self, chunk_size: int = 8192, min_frames_per_id: int = 20):
        super().__init__(chunk_size, min_frames_per_id)
    
    def process_with_mmap(self, file_path: str) -> Iterator[CANFrame]:
        """
        Process a file using memory mapping (for very large files).
        
        Args:
            file_path: Path to the CAN log file
            
        Yields:
            CANFrame objects as they are parsed
        """
        with open(file_path, 'r') as f:
            with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mmapped_file:
                for line in iter(mmapped_file.readline, b""):
                    line_str = line.decode('utf-8').rstrip('\n\r')
                    if line_str.strip():
                        frame = _parse_line(
                            line_str, 
                            self.compact_pattern, 
                            self.bracketed_pattern
                        )
                        if frame:
                            yield frame
    
    def process_in_chunks(self, file_path: str, chunk_callback: Callable[[List[CANFrame]], None]) -> None:
        """
        Process a file in chunks, calling a callback for each chunk.
        
        Args:
            file_path: Path to the CAN log file
            chunk_callback: Function to call with each chunk of frames
        """
        chunk = []
        chunk_size = 1000  # Process 1000 frames at a time
        
        for frame in self.process_can_log_streaming(file_path):
            chunk.append(frame)
            
            if len(chunk) >= chunk_size:
                chunk_callback(chunk)
                chunk = []  # Reset chunk
        
        # Process remaining frames
        if chunk:
            chunk_callback(chunk)
```

## Performance Optimizations

### 1. Chunk Size Optimization
```python
def optimize_chunk_size(file_size: int) -> int:
    """
    Determine optimal chunk size based on file size.
    
    Args:
        file_size: Size of the file in bytes
        
    Returns:
        Optimal chunk size in bytes
    """
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

def parallel_process_segments(file_path: str, num_segments: int = 4) -> Dict[str, List[CANFrame]]:
    """
    Process a large file by splitting it into segments and processing in parallel.
    
    Args:
        file_path: Path to the CAN log file
        num_segments: Number of segments to split the file into
        
    Returns:
        Combined results from all segments
    """
    file_size = os.path.getsize(file_path)
    segment_size = file_size // num_segments
    
    results = {}
    
    with ThreadPoolExecutor(max_workers=num_segments) as executor:
        futures = []
        
        for i in range(num_segments):
            start_pos = i * segment_size
            end_pos = start_pos + segment_size if i < num_segments - 1 else file_size
            
            future = executor.submit(_process_segment, file_path, start_pos, end_pos, i)
            futures.append(future)
        
        # Combine results from all segments
        for future in futures:
            segment_results = future.result()
            for arb_id, frames in segment_results.items():
                if arb_id not in results:
                    results[arb_id] = []
                results[arb_id].extend(frames)
    
    return results

def _process_segment(file_path: str, start_pos: int, end_pos: int, segment_id: int) -> Dict[str, List[CANFrame]]:
    """
    Process a segment of a file.
    
    Args:
        file_path: Path to the CAN log file
        start_pos: Starting position in the file
        end_pos: Ending position in the file
        segment_id: ID of this segment
        
    Returns:
        Results for this segment
    """
    results = {}
    
    with open(file_path, 'r') as f:
        f.seek(start_pos)
        content = f.read(end_pos - start_pos)
        
        # Process the content segment
        lines = content.split('\n')
        compact_pattern = re.compile(r'\(([\d.]+)\)\s+\w+\s+([0-9A-Fa-f]+)#([0-9A-Fa-f]*)')
        bracketed_pattern = re.compile(r'\w+\s+([0-9A-Fa-f]+)\s+\[([\d]+)\]\s+([0-9A-Fa-f\s]*)')
        
        for line in lines:
            if line.strip():
                frame = _parse_line(line.strip(), compact_pattern, bracketed_pattern)
                if frame:
                    arb_id = frame.arbitration_id_hex
                    if arb_id not in results:
                        results[arb_id] = []
                    results[arb_id].append(frame)
    
    return results
```

## Usage Examples

```python
# Basic usage
processor = CANStreamingProcessor(chunk_size=65536)
for frame in processor.process_can_log_streaming("large_can_log.txt"):
    print(f"Frame: {frame.arbitration_id_hex}")

# Group by ID
id_groups = processor.process_and_group_by_id("large_can_log.txt")

# With memory monitoring
memory_analyzer = MemoryEfficientAnalyzer(max_memory_mb=500)
results = memory_analyzer.analyze_if_memory_available("very_large_log.txt")
```

## Error Handling

- Memory usage monitoring prevents excessive consumption
- Graceful degradation when memory thresholds exceeded
- Proper cleanup of file handles and resources
- Recovery from partial processing failures