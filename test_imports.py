"""Test imports to find errors"""
import sys
import traceback

print("Python version:", sys.version)
print("Python path:", sys.executable)
print("\n" + "="*50)

# Test 1: Basic imports
print("\n1. Testing basic imports...")
try:
    import tkinter as tk
    print("✅ tkinter OK")
except Exception as e:
    print(f"❌ tkinter FAILED: {e}")
    traceback.print_exc()

try:
    from tkinter import ttk, scrolledtext, messagebox, filedialog
    print("✅ tkinter submodules OK")
except Exception as e:
    print(f"❌ tkinter submodules FAILED: {e}")
    traceback.print_exc()

# Test 2: Project imports
print("\n2. Testing project imports...")
try:
    from proxy_module import ProxyManager, ProxyListManager
    print("✅ proxy_module OK")
except Exception as e:
    print(f"❌ proxy_module FAILED: {e}")
    traceback.print_exc()

try:
    from hidemium_module import HidemiumClient
    print("✅ hidemium_module OK")
except Exception as e:
    print(f"❌ hidemium_module FAILED: {e}")
    traceback.print_exc()

try:
    from youtube_bot.worker import ViewBotWorker
    print("✅ youtube_bot.worker OK")
except Exception as e:
    print(f"❌ youtube_bot.worker FAILED: {e}")
    traceback.print_exc()

try:
    from youtube_bot.youtube_helper import get_latest_video_url
    print("✅ youtube_bot.youtube_helper OK")
except Exception as e:
    print(f"❌ youtube_bot.youtube_helper FAILED: {e}")
    traceback.print_exc()

# Test 3: Try to import main file
print("\n3. Testing main file import...")
try:
    import youtube_view_bot
    print("✅ youtube_view_bot OK")
except Exception as e:
    print(f"❌ youtube_view_bot FAILED: {e}")
    traceback.print_exc()

print("\n" + "="*50)
print("Test completed. Press Enter to exit...")
input()

