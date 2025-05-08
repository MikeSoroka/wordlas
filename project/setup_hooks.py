#!/usr/bin/env python
"""
Setup script for pre-commit hooks and linting tools.
Run this script to set up the development environment.
"""

import os
import subprocess
import sys

def run_command(command, cwd=None):
    """Run a command and print its output."""
    print(f"Running: {' '.join(command)}")
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            check=True,
            text=True,
            capture_output=True,
        )
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        if e.stdout:
            print(e.stdout)
        if e.stderr:
            print(e.stderr)
        return False

def main():
    """Main setup function."""
    # Get the project root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Install Python requirements
    print("Installing Python requirements...")
    if not run_command([sys.executable, "-m", "pip", "install", "-r", "../requirements.txt"], cwd=script_dir):
        return
    
    # Install JS dependencies
    print("Installing JavaScript dependencies...")
    if not run_command(["npm", "install"], cwd=script_dir):
        print("Failed to install npm dependencies. Make sure npm is installed.")
    
    # Install pre-commit hooks
    print("Installing pre-commit hooks...")
    run_command([sys.executable, "-m", "pre_commit", "install"], cwd=script_dir)
    
    print("\nSetup completed successfully!")
    print("You can now use the following commands:")
    print("- pre-commit run --all-files  # Run hooks on all files")
    print("- npm run lint:js              # Run JSLint on JavaScript files")
    print("- npm run format:js            # Format JavaScript files")
    print("- pylint project               # Run pylint on Python files")
    print("- black project                # Format Python files")

if __name__ == "__main__":
    main() 