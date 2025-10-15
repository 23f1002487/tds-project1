#!/usr/bin/env python3
"""
Initialize log file for Hugging Face Spaces Files tab visibility.
This script ensures the log file is created and visible in the HF Files interface.
"""

import os
import logging
from datetime import datetime

# Set up basic logging to create the file
log_file = "task_log.txt"

# Ensure we're in the right directory (root of HF Space)
if not os.path.exists(log_file):
    with open(log_file, 'w') as f:
        f.write(f"# Student Task Processor Application Logs\n")
        f.write(f"# Log file created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"# This file is accessible via Hugging Face Spaces Files tab\n")
        f.write(f"#\n")
        f.write(f"# Log Format: TIMESTAMP [LEVEL] MODULE:LINE - FUNCTION() - MESSAGE\n")
        f.write(f"#\n\n")

print(f"✅ Log file initialized: {os.path.abspath(log_file)}")
print(f"📁 File will be visible in HF Spaces Files tab as: {log_file}")