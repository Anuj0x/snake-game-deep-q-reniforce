#!/usr/bin/env python3
"""
Snake Game AI Training Script
This script attempts to run the training and provides helpful error messages
for missing dependencies.
"""

import sys
import subprocess

def check_and_install_dependencies():
    """Check for required packages and install missing ones"""
    required_packages = [
        'torch',
        'pygame',
        'numpy',
        'matplotlib',
        'ipython'
    ]

    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)

    if missing_packages:
        print(f"Missing packages: {', '.join(missing_packages)}")
        print("Installing missing dependencies...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_packages)
            print("Dependencies installed successfully!")
        except subprocess.CalledProcessError:
            print("Failed to install dependencies automatically.")
            print("Please run: pip install -r requirements.txt")
            return False

    return True

def run_training():
    """Run the training script"""
    try:
        import agent
        agent.train()
    except KeyboardInterrupt:
        print("\nTraining interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"Error during training: {e}")
        return False
    return True

if __name__ == "__main__":
    print("Snake Game AI Training Setup")
    print("============================")

    if check_and_install_dependencies():
        print("\nStarting training...")
        run_training()
    else:
        print("\nPlease install dependencies and try again.")
        sys.exit(1)
