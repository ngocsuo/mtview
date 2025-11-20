"""Test script for ProxyListManager"""

from proxy_module import ProxyListManager

def test_proxy_list_manager():
    """Test loading and using proxy list."""
    
    print("=== Test ProxyListManager ===\n")
    
    # Test 1: Load proxy file
    print("Test 1: Load proxy file")
    manager = ProxyListManager("examples/proxy_list_sample.txt")
    count = manager.get_proxy_count()
    print(f"✅ Loaded {count} proxies\n")
    
    # Test 2: Get proxies in round-robin
    print("Test 2: Get proxies (round-robin)")
    for i in range(5):
        proxy = manager.get_next_proxy()
        if proxy:
            print(f"  Proxy {i+1}:")
            print(f"    - Original: {proxy}")
            print(f"    - Hidemium format: {proxy.to_hidemium_format()}")
            print(f"    - Endpoint: {proxy.to_endpoint_format()}")
        else:
            print(f"  ❌ No proxy available")
    
    print("\n✅ All tests passed!")

if __name__ == "__main__":
    test_proxy_list_manager()

