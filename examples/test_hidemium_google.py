"""Test Hidemium: Create profile, automate Google search, cleanup.

Workflow:
1. Get default config
2. Create profile (no proxy)
3. Open profile
4. Connect Playwright to profile
5. Navigate to google.com and search "hvnteam"
6. Close profile
7. Delete profile
"""

import time
from hidemium_module import HidemiumClient


def main():
    print("=== Hidemium Test Script ===\n")
    
    # Initialize client
    client = HidemiumClient()
    
    # Check service
    print("[1/7] Checking Hidemium service...")
    if not client.health():
        print("❌ Error: Hidemium service not running at http://127.0.0.1:2222")
        print("Please start Hidemium service first.")
        return
    print("✅ Service is running\n")
    
    # Get default configs
    print("[2/7] Fetching default configs...")
    try:
        configs = client.get_default_configs(page=1, limit=5)
        data = configs.get("data", {})
        items = data.get("content", []) if isinstance(data, dict) else data
        
        if not items:
            print("❌ No default configs found")
            return
            
        first_id = items[0]["id"]
        print(f"✅ Found config ID: {first_id}\n")
    except Exception as e:
        print(f"❌ Failed to get configs: {e}")
        return
    
    # Create profile
    print("[3/7] Creating profile from default config...")
    try:
        resp = client.create_profile_by_default(first_id, is_local=True)
        # Try different response structures
        uuid = resp.get("uuid") or resp.get("profileUUID")
        if not uuid and "content" in resp:
            uuid = resp["content"].get("uuid")
        
        if not uuid:
            print(f"❌ No UUID in response: {resp}")
            return
            
        print(f"✅ Profile created: {uuid}\n")
    except Exception as e:
        print(f"❌ Failed to create profile: {e}")
        return
    
    # Wait for profile readiness (skip if endpoint not working)
    print("[4/7] Waiting for profile to be ready...")
    try:
        ready = client.check_profile_readiness(uuid, max_retries=3, retry_delay=1.0)
        if ready:
            print("✅ Profile is ready\n")
        else:
            print("⚠️  Profile readiness uncertain, continuing anyway...\n")
    except Exception as e:
        print(f"⚠️  Readiness check failed: {e}")
        print("Continuing anyway...\n")
    
    # Open profile
    print("[5/7] Opening profile...")
    try:
        open_resp = client.open_profile(uuid)
        print(f"✅ Profile opened: {open_resp}\n")
        
        # Extract connection info - check multiple possible locations
        ws_endpoint = None
        if isinstance(open_resp.get("data"), dict):
            ws_endpoint = open_resp["data"].get("web_socket")
        if not ws_endpoint:
            ws_endpoint = open_resp.get("ws", {}).get("puppeteer") or open_resp.get("ws", {}).get("playwright")
        
        if not ws_endpoint:
            print("⚠️  No WebSocket endpoint found in response")
            print("Response:", open_resp)
            print("\nWaiting 5 seconds for manual check...")
            time.sleep(5)
        else:
            print(f"✅ WebSocket endpoint: {ws_endpoint}")
            
    except Exception as e:
        print(f"❌ Failed to open profile: {e}")
        try:
            client.delete_profiles([uuid], is_local=True)
        except:
            pass
        return
    
    # Playwright automation
    print("[6/7] Running Playwright automation...")
    try:
        from playwright.sync_api import sync_playwright
        
        with sync_playwright() as p:
            # Connect to Hidemium browser
            if ws_endpoint:
                browser = p.chromium.connect_over_cdp(ws_endpoint)
            else:
                print("⚠️  Skipping Playwright connection (no WebSocket endpoint)")
                browser = None
            
            if browser:
                # Get default context and page
                contexts = browser.contexts
                if contexts:
                    context = contexts[0]
                    pages = context.pages
                    if pages:
                        page = pages[0]
                    else:
                        page = context.new_page()
                else:
                    context = browser.new_context()
                    page = context.new_page()
                
                print("  → Navigating to google.com...")
                page.goto("https://www.google.com", wait_until="domcontentloaded", timeout=30000)
                time.sleep(2)
                
                print("  → Searching for 'hvnteam'...")
                # Handle cookie consent if present
                try:
                    page.click('button:has-text("Accept all")', timeout=3000)
                except:
                    pass
                
                # Find search box (handle different selectors)
                try:
                    search_box = page.wait_for_selector('textarea[name="q"]', timeout=5000)
                except:
                    try:
                        search_box = page.wait_for_selector('input[name="q"]', timeout=5000)
                    except:
                        print("  ⚠️  Could not find search box")
                        search_box = None
                
                if search_box:
                    search_box.fill("hvnteam")
                    time.sleep(1)
                    search_box.press("Enter")
                    print("  → Search submitted")
                    
                    # Wait for results
                    try:
                        page.wait_for_selector("#search", timeout=10000)
                        print("  ✅ Search results loaded")
                        time.sleep(2)
                    except:
                        print("  ⚠️  Results may not have loaded completely")
                
                print("  ✅ Automation completed\n")
                browser.close()
            
    except ImportError:
        print("⚠️  Playwright not installed. Install with: pip install playwright")
        print("⚠️  Then run: playwright install chromium")
        print("Skipping automation...\n")
    except Exception as e:
        print(f"⚠️  Automation error: {e}\n")
    
    # Close profile
    print("[7/7] Closing profile...")
    try:
        closed = client.close_profile_with_check(uuid, retries=3, delay_seconds=1.5)
        if closed:
            print("✅ Profile closed")
        else:
            print("⚠️  Profile may not have closed properly")
    except Exception as e:
        print(f"⚠️  Close error: {e}")
    
    # Delete profile
    print("\n[Cleanup] Deleting profile...")
    try:
        delete_resp = client.delete_profiles([uuid], is_local=True)
        print(f"✅ Profile deleted: {delete_resp}")
    except Exception as e:
        print(f"⚠️  Delete error: {e}")
    
    print("\n=== Test Complete ===")


if __name__ == "__main__":
    main()
