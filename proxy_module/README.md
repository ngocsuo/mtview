# Proxy Module (IPv6 Local Proxy API Client)

Python wrapper around the local IPv6 Proxy API exposed at `http://127.0.0.1:5000`.

## Features
- Create persistent proxies (http, socks5, both)
- Create temporary TTL proxies
- List, inspect, delete, bulk delete proxies
- Cleanup expired temp proxies
- Fetch stats
- Convenience: obtain a ready `requests` proxies mapping in one call

## Install Dependencies
```
pip install -r requirements.txt
```

## Quick Start
```python
from proxy_module import ProxyManager

pm = ProxyManager()  # base_url defaults to http://127.0.0.1:5000

# Create SOCKS5 proxy and use with requests
inst = pm.create_proxy("socks5", interface="Ethernet")
proxies = inst.to_requests_proxies()

import requests
print(requests.get("https://api.ipify.org?format=json", proxies=proxies, timeout=15).json())

# Or let manager handle reuse/create automatically
proxies2 = pm.get_ready_requests_proxies("http", "Ethernet")
print(requests.get("http://httpbin.org/ip", proxies=proxies2, timeout=10).text)
```

## Temporary Proxy
```python
temp_proxies = pm.ensure_temp("both", ttl=120, interface="Ethernet")
```

## Bulk Delete
```python
deleted = pm.bulk_delete(delete_all=True)
print("Deleted", deleted)
```

## Error Handling
`ProxyAPIError` for network/HTTP issues, `ProxyValidationError` for invalid inputs.

## Notes
- API enforces IPv6-only outbound; destinations lacking AAAA will fail.
- Ports are ephemeral per instance.
- Prefer reusing existing proxies via `get_or_create` to limit resource usage.
