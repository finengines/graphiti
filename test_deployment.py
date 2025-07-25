#!/usr/bin/env python3
"""
Simple test script to verify Graphiti deployment
"""

import requests
import sys
import time

def test_endpoint(url, description):
    """Test an endpoint and return success status"""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print(f"✓ {description}: {url}")
            return True
        else:
            print(f"✗ {description}: {url} (status: {response.status_code})")
            return False
    except Exception as e:
        print(f"✗ {description}: {url} (error: {e})")
        return False

def main():
    """Test the deployment"""
    print("Testing Graphiti deployment...")
    
    # Test endpoints
    endpoints = [
        ("http://localhost:8000/", "Root endpoint"),
        ("http://localhost:8000/healthcheck", "Health check"),
    ]
    
    success_count = 0
    total_count = len(endpoints)
    
    for url, description in endpoints:
        if test_endpoint(url, description):
            success_count += 1
        time.sleep(1)  # Small delay between requests
    
    print(f"\nResults: {success_count}/{total_count} endpoints working")
    
    if success_count == total_count:
        print("✓ Deployment is working correctly!")
        return 0
    else:
        print("✗ Some endpoints are not working")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 