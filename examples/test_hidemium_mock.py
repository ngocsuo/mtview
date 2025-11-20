"""Mock test for Hidemium workflow (when service not available).

Demonstrates the complete flow with simulated responses.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import MagicMock, patch
import time


def mock_hidemium_test():
    print("=== Hidemium Mock Test Script ===")
    print("(Simulating workflow when service is unavailable)\n")
    
    # Mock HidemiumClient
    print("[1/7] Checking Hidemium service...")
    print("✅ Service is running (mocked)\n")
    
    # Mock get default configs
    print("[2/7] Fetching default configs...")
    mock_config = {
        "data": {
            "content": [
                {"id": 24741, "name": "Windows Chrome Config"}
            ]
        }
    }
    config_id = 24741
    print(f"✅ Found config ID: {config_id}\n")
    
    # Mock create profile
    print("[3/7] Creating profile from default config...")
    mock_uuid = "abc-123-test-profile"
    print(f"✅ Profile created: {mock_uuid}\n")
    
    # Mock readiness check
    print("[4/7] Waiting for profile to be ready...")
    for i in range(3):
        print(f"  → Checking readiness... ({i+1}/3)")
        time.sleep(0.5)
    print("✅ Profile is ready\n")
    
    # Mock open profile
    print("[5/7] Opening profile...")
    mock_ws = "ws://127.0.0.1:9222/devtools/browser/abc-123"
    print(f"✅ Profile opened")
    print(f"WebSocket endpoint: {mock_ws}\n")
    
    # Mock Playwright automation
    print("[6/7] Running Playwright automation...")
    print("  → Navigating to google.com...")
    time.sleep(1)
    print("  → Searching for 'hvnteam'...")
    time.sleep(1)
    print("  → Search submitted")
    time.sleep(0.5)
    print("  ✅ Search results loaded")
    time.sleep(0.5)
    print("  ✅ Automation completed\n")
    
    # Mock close profile
    print("[7/7] Closing profile...")
    time.sleep(0.5)
    print("✅ Profile closed\n")
    
    # Mock delete profile
    print("[Cleanup] Deleting profile...")
    time.sleep(0.3)
    print(f"✅ Profile deleted: {mock_uuid}")
    
    print("\n=== Mock Test Complete ===")
    print("\n📝 Note: To run real test, start Hidemium service at http://127.0.0.1:2222")
    print("Then run: python examples/test_hidemium_google.py")


if __name__ == "__main__":
    mock_hidemium_test()
