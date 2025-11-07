import struct
import os

def read_mbr(device_path):
    """Read MBR from a block device"""
    try:
        with open(device_path, 'rb') as f:
            mbr_data = f.read(512)
        return mbr_data
    except Exception as e:
        print(f"Error reading MBR: {e}")
        return None

def write_mbr(device_path, mbr_data):
    """Write MBR to a block device - USE WITH EXTREME CAUTION"""
    if len(mbr_data) != 512:
        raise ValueError("MBR must be exactly 512 bytes")
    
    # Add safety checks
    confirmation = input(f"WARNING: This will overwrite MBR on {device_path}. Type 'YES' to confirm: ")
    if confirmation != 'YES':
        print("Operation cancelled")
        return False
    
    try:
        with open(device_path, 'wb') as f:
            f.write(mbr_data)
        print("MBR written successfully")
        return True
    except Exception as e:
        print(f"Error writing MBR: {e}")
        return False
# These will destroy your bootloader and make system unbootable:
write_mbr("/dev/sda", b'\x00' * 512)  # Wipes MBR
