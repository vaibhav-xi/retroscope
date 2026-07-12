import time
import sys
import random

def format_size(bytes_size):
    """Converts bytes to a human-readable format."""
    for unit in ['B', 'kB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} TB"

def simulate_pre_install():
    """Simulates the terminal output of apt-get upgrade."""
    steps = [
        ("Reading package lists...", 1.2),
        ("Building dependency tree...", 0.8),
        ("Reading state information...", 0.5),
        ("Calculating upgrade...", 1.5)
    ]
    
    for step, delay in steps:
        sys.stdout.write(f"{step}")
        sys.stdout.flush()
        time.sleep(delay)
        print(" Done")

    packages = [
        "linux-image-6.8.0-45-generic", "linux-headers-generic", "systemd", "systemd-sysv", 
        "libc6", "libc-bin", "python3.12", "python3-pip", "gcc-13", "libstdc++6", 
        "bash", "coreutils", "gnome-shell", "wayland-protocols", "xserver-xorg-core", 
        "libdrm2", "curl", "wget", "vim", "git", "mesa-va-drivers", "driver-535", 
        "network-manager", "pulseaudio", "pipewire", "docker-ce", "containerd.io",
        "openssh-server", "openssl", "grub-efi-amd64", "initramfs-tools", "dpkg", "apt"
    ]
    
    print("\nThe following packages will be upgraded:")
    
    # Print packages in wrapped lines like a real package manager
    line = "  "
    for pkg in packages:
        if len(line) + len(pkg) > 75:
            print(line)
            line = "  "
        line += pkg + " "
    print(line)
    
    print(f"\n{len(packages)} upgraded, 0 newly installed, 0 to remove and 0 not upgraded.")
    print("Need to get 5,632 MB of archives.")
    print("After this operation, 1,204 MB of additional disk space will be used.")
    
    # Fake a slight pause for "user input" assuming they passed -y flag
    time.sleep(1)
    print("Get:1 http://archive.ubuntu.com/ubuntu jammy-updates/main amd64 Packages [5,632 MB]")
    
    return packages

def main():
    # Hide terminal cursor for a cleaner look
    sys.stdout.write('\033[?25l')
    sys.stdout.flush()

    try:
        packages = simulate_pre_install()
        
        # Constants
        TOTAL_GB = 5.6
        TOTAL_BYTES = TOTAL_GB * 1024 * 1024 * 1024
        TOTAL_TIME_SECONDS = 8 * 60 * 60  # 8 hours
        BAR_LENGTH = 35
        
        downloaded = 0
        start_time = time.time()
        
        while downloaded < TOTAL_BYTES:
            current_time = time.time()
            elapsed = current_time - start_time
            remaining_time = TOTAL_TIME_SECONDS - elapsed
            
            if remaining_time <= 0:
                downloaded = TOTAL_BYTES
                current_speed = 0
                remaining_time = 0
            else:
                remaining_bytes = TOTAL_BYTES - downloaded
                # Calculate the exact speed needed to finish on time
                target_speed = remaining_bytes / remaining_time
                
                # Introduce fluctuation (between 10% and 190% of target speed)
                current_speed = target_speed * random.uniform(0.1, 1.9)
                
                if current_speed > remaining_bytes:
                    current_speed = remaining_bytes
                    
                downloaded += current_speed
            
            # Calculations for display
            percent = downloaded / TOTAL_BYTES
            filled_length = int(BAR_LENGTH * percent)
            bar = '#' * filled_length + '.' * (BAR_LENGTH - filled_length)
            
            hours, rem = divmod(int(remaining_time), 3600)
            minutes, seconds = divmod(rem, 60)
            eta_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            
            dl_mb = downloaded / (1024**2)
            total_mb = TOTAL_BYTES / (1024**2)
            
            # Determine which package is currently "downloading" based on percentage
            pkg_index = min(int(percent * len(packages)), len(packages) - 1)
            current_pkg = packages[pkg_index]
            
            # Formatting Display String
            # \033[K clears everything to the right of the cursor to prevent text overlap
            sys.stdout.write(
                f"\rProgress: [{percent:>5.1%}] [{bar}] "
                f"{dl_mb:.0f} MB / {total_mb:.0f} MB | "
                f"{format_size(current_speed).rjust(9)}/s | "
                f"ETA: {eta_str} | Fetching: {current_pkg}\033[K"
            )
            sys.stdout.flush()
            
            if downloaded >= TOTAL_BYTES:
                break
                
            time.sleep(1)

        # Clear the progress bar line and show extraction phase
        sys.stdout.write("\r\033[K")
        print("Fetched 5,632 MB in 8h 0m 0s (195 kB/s)")
        print("Extracting templates from packages: 100%")
        print("Preconfiguring packages ...")
        print("Setting up system upgrade ...")
        
        # Keep the script hanging as if it's installing
        while True:
            time.sleep(60)
        
    except KeyboardInterrupt:
        sys.stdout.write("\n\r\033[K")
        print("E: Interrupted by user")
    finally:
        # Restore terminal cursor
        sys.stdout.write('\033[?25h')
        sys.stdout.flush()

if __name__ == "__main__":
    main()