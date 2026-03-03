"""
CAN Frame Data Model
"""

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