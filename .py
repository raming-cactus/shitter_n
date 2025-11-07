import struct
import os
import fcntl

def read_mbr(device_path):
    """Read MBR from block device - RAW MODE"""
    try:
        # Open in raw binary mode
        with open(device_path, 'rb') as f:
            # Bypass buffers for direct device access
            if os.name == 'posix':
                fcntl.fcntl(f, fcntl.F_SETFL, os.O_DIRECT)
            mbr_data = f.read(512)
        return mbr_data
    except Exception as e:
        print(f"Error reading MBR: {e}")
        return None

def write_mbr(device_path, mbr_data):
    """Write MBR to block device - RAW DESTRUCTIVE MODE"""
    if len(mbr_data) != 512:
        # Pad or truncate to exactly 512 bytes
        mbr_data = mbr_data.ljust(512, b'\x00')[:512]
    
    # Minimal safety for VM
    print(f"🚨 NUKING MBR ON: {device_path}")
    print(f"💀 THIS WILL DESTROY BOOTLOADER")
    confirmation = input("TYPE 'KILL-MBR' TO CONFIRM DESTRUCTION: ")
    
    if confirmation != 'KILL-MBR':
        print("Operation cancelled")
        return False
    
    try:
        # Force write with direct access
        with open(device_path, 'wb') as f:
            if os.name == 'posix':
                fcntl.fcntl(f, fcntl.F_SETFL, os.O_DIRECT)
            f.write(mbr_data)
            f.flush()
            os.fsync(f.fileno())
        print("✅ MBR DESTROYED - SYSTEM UNBOOTABLE")
        return True
    except Exception as e:
        print(f"❌ Error writing MBR: {e}")
        return False

def find_vm_disks():
    """Find available disks in VM"""
    disk_patterns = ['/dev/sda', '/dev/sdb', '/dev/vda', '/dev/vdb', '/dev/hda']
    for disk in disk_patterns:
        if os.path.exists(disk):
            print(f"FOUND: {disk}")
    return [d for d in disk_patterns if os.path.exists(d)]

# 🚀 DANGEROUS OPERATIONS - VM ONLY 🚀

# 1. Find your VM disks
print("🔍 Scanning for VM disks...")
disks = find_vm_disks()
print(f"Available disks: {disks}")

# 2. NUKE MBR (Choose your target)
if disks:
    target_disk = disks[0]  # Usually sda or vda is main disk
    print(f"🎯 Targeting: {target_disk}")
    
    # Backup current MBR first (optional)
    backup = read_mbr(target_disk)
    if backup:
        with open("mbr_backup.bin", "wb") as f:
            f.write(backup)
        print("💾 MBR backed up to mbr_backup.bin")
    
    # DESTROY MBR with zeros
    write_mbr(target_disk, b'\x00' * 512)
    
    # Verify destruction
    verify = read_mbr(target_disk)
    if verify == b'\x00' * 512:
        print("☠️  MBR SUCCESSFULLY DESTROYED - VM WILL NOT BOOT")
    else:
        print("⚠️  MBR may not be fully destroyed")

# 3. Create custom malicious MBR
def create_corrupt_mbr():
    """Create various types of corrupt MBRs"""
    # Option A: All zeros (complete wipe)
    zeros = b'\x00' * 512
    
    # Option B: Broken boot signature
    broken_sig = b'\x00' * 510 + b'\x00\x00'  # Missing 55 AA
    
    # Option C: Invalid partition table
    corrupt_pt = b'\xEB' * 64 + b'\x00' * 446 + b'\x55\xAA'
    
    # Option D: Infinite loop boot code
    infinite_loop = b'\xEB\xFE' + b'\x00' * 508 + b'\x55\xAA'  # jmp $
    
    return infinite_loop  # Most "fun" option

# Uncomment to use custom corrupt MBR:
corrupt_mbr = create_corrupt_mbr()
write_mbr("/dev/sda", corrupt_mbr)
