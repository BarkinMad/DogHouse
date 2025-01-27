#!/usr/bin/env python3
import subprocess
import sys
import os
import shutil
import json
import tempfile
from pathlib import Path
from datetime import datetime

class AppBuilder:
    def __init__(self):
        self.exe_dir = os.path.join("build", "windows")
        
    def setup_exe_environment(self):
        """Set up the directory structure next to the exe"""
        print("\nSetting up exe environment...")
        
        # Create directory structure
        dirs_to_create = [
            os.path.join(self.exe_dir, "plugins", "builtin"),
            os.path.join(self.exe_dir, "plugins", "custom"),
            os.path.join(self.exe_dir, "processor", "builtin"),
            os.path.join(self.exe_dir, "processor", "custom")
        ]
        
        for dir_path in dirs_to_create:
            os.makedirs(dir_path, exist_ok=True)
        
        # Create clean config.json
        config = {
            "ZoomEye": {
                "api_key": "None"
            },
            "Hunter": {
                "api_key": "None"
            },
            "CriminalIP": {
                "api_key": "None"
            },
            "Manual Entry": {
                "enabled": True,
                "config": {}
            }
        }
        
        config_path = os.path.join(self.exe_dir, "plugins/config.json")
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)
        
        # Create __init__.py files
        for dir_path in dirs_to_create:
            init_file = os.path.join(dir_path, "__init__.py")
            Path(init_file).touch()
    
    def build(self):
        """Run the build process"""
        try:
            print("\nBuilding application...")
            build_args = [
                "flet", "build", "windows",
                "--project", "doghouse_app",
                "--product", "Dog House",
                "--org", "com.doghouse",
                "--description", "Dog House - Network Reconnaissance Tool",
                "--copyright", "© 2025",
                "--company", "BMaddox",
                "--exclude", "plugins/config.json plugins/builtin plugins/custom processor/builtin processor/custom"
                "--verbose",  
            ]
            
            print("Using build arguments:", " ".join(build_args))
            subprocess.run(build_args, check=True)
            
            # 3. Set up exe environment
            self.setup_exe_environment()
            
            print(f"\nBuild completed successfully!")
            print(f"Output location: {os.path.abspath(self.exe_dir)}")
            return 0
            
        except subprocess.CalledProcessError as e:
            print(f"Build failed with error: {e}")
            return e.returncode
        except Exception as e:
            print(f"An error occurred: {e}")
            return 1


if __name__ == "__main__":
    builder = AppBuilder()
    sys.exit(builder.build())