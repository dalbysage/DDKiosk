#!/usr/bin/env python3
import os
import sys
import re
import pwd
import grp
import shutil
import subprocess

TARGET_USER = "kiosk"
TARGET_GROUP = "gpio"
LOG_DIR = "/var/log/kiosk/"
HOME_DIR = f"/home/{TARGET_USER}/"
CONFIG_PATH = "/boot/firmware/config.txt"

CONFIG_TARGETS = [
    {"pattern": r"\bdtoverlay\s*=\s*disable-wifi", "exact_line": "dtoverlay=disable-wifi"},
    {"pattern": r"\bdtoverlay\s*=\s*disable-bt",   "exact_line": "dtoverlay=disable-bt"},
]

def configure_hardware():
    """Idempotently updates /boot/firmware/config.txt using regular expressions."""
    print("--- Configuring Hardware Settings (config.txt) ---")

    if not os.path.exists(CONFIG_PATH):
        print(f"Error: {CONFIG_PATH} not found.")
        sys.exit(1)

    with open(CONFIG_PATH, "r") as f:
        lines = f.read().splitlines()

    modified = False
    new_lines = []
    resolved_targets = {t["exact_line"]: False for t in CONFIG_TARGETS}

    for line in lines:
        matched_any_target = False

        for target in CONFIG_TARGETS:
            regex = rf"^\s*#*\s*{target['pattern']}\s*$"
            if re.match(regex, line):
                if line.strip() == target["exact_line"]:
                    new_lines.append(line)
                else:
                    new_lines.append(target["exact_line"])
                    print(f"Corrected/Uncommented: {target['exact_line']}")
                    modified = True

                resolved_targets[target["exact_line"]] = True
                matched_any_target = True
                break

        if not matched_any_target:
            new_lines.append(line)

    for target in CONFIG_TARGETS:
        if not resolved_targets[target["exact_line"]]:
            new_lines.append(target["exact_line"])
            print(f"Appended missing configuration: {target['exact_line']}")
            modified = True

    if modified:
        shutil.copy2(CONFIG_PATH, f"{CONFIG_PATH}.bak")
        with open(CONFIG_PATH, "w") as f:
            f.write("\n".join(new_lines) + "\n")
        print("Successfully updated config.txt.")
    else:
        print("Idempotency Check: config.txt configurations are already perfectly set.")

# Files to copy into the kiosk home directory
FILES_TO_DEPLOY = ["kiosk.py", "kiosk.cfg"]

def setup_environment():
    """Idempotently manages users, groups, and logs with native Python lookups."""
    print("\n--- Setting Up User Environment ---")

    # 1. User Creation
    try:
        pwd.getpwnam(TARGET_USER)
        print(f"Idempotency Check: User '{TARGET_USER}' already exists.")
    except KeyError:
        print(f"Creating user '{TARGET_USER}'...")
        subprocess.run(["useradd", "-m", TARGET_USER], check=True)

    kiosk_uid = pwd.getpwnam(TARGET_USER).pw_uid
    kiosk_gid = pwd.getpwnam(TARGET_USER).pw_gid

    # 2. Group Assignment
    try:
        user_groups = [g.gr_name for g in grp.getgrall() if TARGET_USER in g.gr_mem]
        user_groups.append(grp.getgrgid(kiosk_gid).gr_name)

        if TARGET_GROUP in user_groups:
            print(f"Idempotency Check: User '{TARGET_USER}' is already in group '{TARGET_GROUP}'.")
        else:
            print(f"Adding user '{TARGET_USER}' to group '{TARGET_GROUP}'...")
            subprocess.run(["usermod", "-aG", TARGET_GROUP, TARGET_USER], check=True)
    except KeyError:
        print(f"Warning: Group '{TARGET_GROUP}' does not exist on this system.")

    # 3. Log Directory Management
    if os.path.exists(LOG_DIR):
        print(f"Idempotency Check: Log directory '{LOG_DIR}' already exists.")
    else:
        print(f"Creating log directory '{LOG_DIR}'...")
        os.makedirs(LOG_DIR, exist_ok=True)
        os.chown(LOG_DIR, kiosk_uid, kiosk_gid)

def deploy_application_files():
    """Safely copies project files and ensures the kiosk user owns them."""
    print("\n--- Deploying Application Files ---")
    
    kiosk_uid = pwd.getpwnam(TARGET_USER).pw_uid
    kiosk_gid = pwd.getpwnam(TARGET_USER).pw_gid

    for file_name in FILES_TO_DEPLOY:
        if not os.path.exists(file_name):
            print(f"Error: Source file '{file_name}' not found.")
            sys.exit(1)
            
        destination = os.path.join(HOME_DIR, file_name)
        shutil.copy2(file_name, destination)
        os.chown(destination, kiosk_uid, kiosk_gid)
        print(f"Deployed: {file_name} -> {destination} (Owner: {TARGET_USER})")


if __name__ == "__main__":
    if os.geteuid() != 0:
        print("Error: This installer must be run with root privileges (sudo).")
        sys.exit(1)

    configure_hardware()
    setup_environment()
    deploy_application_files()
    
    print("\nDeployment complete! Please reboot the Raspberry Pi to apply boot configurations.")

