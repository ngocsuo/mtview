"""Example: Complete workflow integrating Proxy + Hidemium modules.

Demonstrates:
1. Create IPv6 proxy (SOCKS5)
2. Create Hidemium profile with proxy
3. Open profile for automation
4. Close and cleanup both profile and proxy
"""

from proxy_module import ProxyManager
from hidemium_module import HidemiumClient


def main():
    # Initialize clients
    pm = ProxyManager()
    hc = HidemiumClient()

    # Check Hidemium service
    if not hc.health():
        print("Error: Hidemium service not running at http://127.0.0.1:2222")
        return

    print("=== Step 1: Create IPv6 Proxy ===")
    proxy_inst = pm.create_proxy(proxy_type="socks5", interface="Ethernet")
    print(f"Proxy created: {proxy_inst.instance_id}")
    print(f"IPv6: {proxy_inst.ipv6_address}")
    
    # Get proxy endpoint
    endpoint = list(proxy_inst.endpoints.values())[0]  # e.g., 127.0.0.1:63124
    proxy_str = f"SOCKS5|{endpoint.replace(':', '|')}"
    print(f"Proxy string: {proxy_str}")

    try:
        print("\n=== Step 2: Create Hidemium Profile ===")
        result = hc.create_and_open(
            profile_name="AutomationProfile",
            os="win",
            browser="chrome",
            proxy=proxy_str,
            canvas="noise",
            webRTC="disabled",
            language="vi-VN",
            resolution="1920x1080",
            wait_ready=True,
        )
        uuid = result["uuid"]
        print(f"Profile created and opened: {uuid}")
        print(f"Open response: {result['open_response']}")

        print("\n=== Step 3: Automation Placeholder ===")
        print("// Connect Playwright/Selenium to profile endpoint")
        print("// Perform automation tasks...")
        input("Press Enter to close and cleanup...")

        print("\n=== Step 4: Cleanup ===")
        closed = hc.close_profile_with_check(uuid, retries=3)
        print(f"Profile closed: {closed}")
        
        deleted = hc.delete_profiles([uuid], is_local=True)
        print(f"Profile deleted: {deleted}")

    finally:
        # Always cleanup proxy
        pm.delete_proxy(proxy_inst.instance_id)
        print(f"Proxy deleted: {proxy_inst.instance_id}")


if __name__ == "__main__":
    main()
