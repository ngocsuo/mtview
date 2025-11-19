# MTView Project

Python automation toolkit integrating IPv6 proxy management and Hidemium browser profile automation.

## Modules

### 1. Proxy Module (`proxy_module/`)
Client for local IPv6 Proxy API (http://127.0.0.1:5000).

**Features:**
- Create/delete IPv6 proxies (HTTP, SOCKS5, or both)
- List and inspect proxy instances
- Automatic cleanup and resource management
- IPv6-only outbound connections

**Quick Start:**
```python
from proxy_module import ProxyManager

pm = ProxyManager()
proxy = pm.create_proxy("socks5", "Ethernet")
print(f"Proxy: {proxy.endpoints}")
pm.delete_proxy(proxy.instance_id)
```

See [proxy_module/README.md](proxy_module/README.md) for details.

### 2. Hidemium Module (`hidemium_module/`)
Client for Hidemium browser profile API (http://127.0.0.1:2222).

**Features:**
- Create profiles from default configs or custom fingerprints
- Open/close browser instances
- Proxy integration (SOCKS5/HTTP)
- Profile lifecycle management
- Readiness and status checking

**Quick Start:**
```python
from hidemium_module import HidemiumClient

hc = HidemiumClient()
result = hc.create_and_open(
    profile_name="MyProfile",
    proxy="SOCKS5|127.0.0.1|63124"
)
uuid = result["uuid"]
# ... automation ...
hc.close_profile_with_check(uuid)
hc.delete_profiles([uuid])
```

See [hidemium_module/README.md](hidemium_module/README.md) for details.

## Integration Example

Complete workflow combining both modules:

```python
from proxy_module import ProxyManager
from hidemium_module import HidemiumClient

# Create proxy
pm = ProxyManager()
proxy = pm.create_proxy("socks5", "Ethernet")
endpoint = list(proxy.endpoints.values())[0]
proxy_str = f"SOCKS5|{endpoint.replace(':', '|')}"

# Create and open profile
hc = HidemiumClient()
result = hc.create_and_open(
    profile_name="AutoProfile",
    proxy=proxy_str,
    wait_ready=True
)

# Automation here...

# Cleanup
hc.close_profile_with_check(result["uuid"])
hc.delete_profiles([result["uuid"]])
pm.delete_proxy(proxy.instance_id)
```

See [examples/integration_example.py](examples/integration_example.py) for full example.

## Installation

```bash
pip install -r requirements.txt
```

## Requirements

- Python 3.8+
- requests >= 2.31.0
- Local IPv6 Proxy API running at http://127.0.0.1:5000
- Hidemium service running at http://127.0.0.1:2222

## Testing

```bash
python -m unittest discover -s tests -v
```

## Documentation

- [Proxy API Reference](proxyai.md)
- [Hidemium API Reference](hide.md)
- [Proxy Module README](proxy_module/README.md)
- [Hidemium Module README](hidemium_module/README.md)

## License

MIT

## Notes

- Proxy service creates IPv6-only outbound connections
- Hidemium profiles support fingerprint customization
- Both modules designed for multi-threaded automation workflows
