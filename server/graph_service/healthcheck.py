#!/usr/bin/env python3
"""
Health check script for Graphiti Knowledge Server
"""

import urllib.request
import sys

def check_health():
    """Check if the server is healthy"""
    try:
        response = urllib.request.urlopen('http://localhost:8000/healthcheck', timeout=5)
        if response.getcode() == 200:
            print("Server is healthy")
            return True
        else:
            print(f"Server returned status code: {response.getcode()}")
            return False
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

if __name__ == "__main__":
    if check_health():
        sys.exit(0)
    else:
        sys.exit(1) 