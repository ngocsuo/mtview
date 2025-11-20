import time
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any
import requests

from .exceptions import ProxyAPIError, ProxyValidationError


@dataclass
class ProxyInstance:
    instance_id: str
    ipv6_address: str
    interface: str
    type: str
    created_at: float
    endpoints: Dict[str, str] = field(default_factory=dict)
    expires_at: Optional[float] = None
    stats: Optional[Dict[str, Any]] = None

    @property
    def is_temp(self) -> bool:
        return self.expires_at is not None

    @property
    def expired(self) -> bool:
        return self.expires_at is not None and time.time() > self.expires_at

    def to_requests_proxies(self, prefer: str = "auto") -> Dict[str, str]:
        """Return a `requests` compatible proxies mapping.

        prefer: "auto" | "http" | "socks5"
        When type == both, choose which endpoint to expose. auto picks http if available else socks5.
        """
        if self.type == "both":
            chosen = self.endpoints.get("http") if prefer in ("auto", "http") else self.endpoints.get("socks5")
            if chosen is None:
                # fallback
                chosen = next(iter(self.endpoints.values()))
            # Decide scheme by inspecting chosen key name
            if chosen == self.endpoints.get("http"):
                return {"http": f"http://{chosen}", "https": f"http://{chosen}"}
            return {"http": f"socks5://{chosen}", "https": f"socks5://{chosen}"}
        if self.type == "http":
            endpoint = self.endpoints.get("http") or self.endpoints.get("proxy")
            return {"http": f"http://{endpoint}", "https": f"http://{endpoint}"}
        # socks5
            
        endpoint = self.endpoints.get("socks5") or self.endpoints.get("proxy")
        return {"http": f"socks5://{endpoint}", "https": f"socks5://{endpoint}"}


class ProxyManager:
    """High level client for the local IPv6 Proxy API.

    Base URL defaults to http://127.0.0.1:5000 as per documentation.
    Provides convenience methods to create, retrieve, list and delete proxies
    plus building ready-to-use `requests` proxies mapping.
    """

    def __init__(self, base_url: str = "http://127.0.0.1:5000", timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    # -------------------- Internal helpers --------------------
    def _request(self, method: str, path: str, **kwargs) -> Any:
        url = f"{self.base_url}{path}"
        try:
            resp = requests.request(method, url, timeout=self.timeout, **kwargs)
        except requests.RequestException as e:
            raise ProxyAPIError(f"HTTP request failed: {e}") from e
        
        # Debug logging
        print(f"[DEBUG] {method} {url}")
        print(f"[DEBUG] Status: {resp.status_code}")
        print(f"[DEBUG] Response: {resp.text[:500]}")
        
        if not resp.ok:
            raise ProxyAPIError(f"API error {resp.status_code}: {resp.text.strip()[:200]}")
        try:
            return resp.json()
        except ValueError as e:
            raise ProxyAPIError("Invalid JSON response") from e

    @staticmethod
    def _parse_instance(data: Dict[str, Any]) -> ProxyInstance:
        # unify endpoints
        endpoints: Dict[str, str] = {}
        if "endpoints" in data and isinstance(data["endpoints"], dict):
            endpoints = data["endpoints"].copy()
        else:
            # single endpoint (http or socks5)
            if data.get("proxy_endpoint"):
                # determine type name for key
                t = data.get("type")
                key = "http" if t == "http" else ("socks5" if t == "socks5" else "proxy")
                endpoints[key] = data["proxy_endpoint"]
        return ProxyInstance(
            instance_id=data.get("instance_id"),
            ipv6_address=data.get("ipv6_address"),
            interface=data.get("interface"),
            type=data.get("type"),
            created_at=data.get("created_at", 0.0),
            endpoints=endpoints,
            expires_at=data.get("expires_at"),
            stats=data.get("stats"),
        )

    # -------------------- Public API methods --------------------
    def create_proxy(self, proxy_type: str, interface: str) -> ProxyInstance:
        if proxy_type not in {"http", "socks5", "both"}:
            raise ProxyValidationError("proxy_type must be one of: http, socks5, both")
        if not interface:
            raise ProxyValidationError("interface is required")
        data = self._request(
            "POST",
            "/api/create_proxy",
            json={"type": proxy_type, "interface": interface},
        )
        return self._parse_instance(data)

    def create_temp_proxy(self, proxy_type: str, ttl: int, interface: Optional[str] = None) -> ProxyInstance:
        if proxy_type not in {"http", "socks5", "both"}:
            raise ProxyValidationError("proxy_type must be one of: http, socks5, both")
        if ttl <= 0:
            raise ProxyValidationError("ttl must be positive seconds")
        body = {"type": proxy_type, "ttl": ttl}
        if interface:
            body["interface"] = interface
        data = self._request("POST", "/api/proxy/create_temp", json=body)
        return self._parse_instance(data)

    def list_proxies(self) -> List[ProxyInstance]:
        data = self._request("GET", "/api/list_proxies")
        items = data.get("proxies") or []
        return [self._parse_instance(p) for p in items]

    def get_proxy(self, instance_id: str) -> ProxyInstance:
        if not instance_id:
            raise ProxyValidationError("instance_id required")
        data = self._request("GET", f"/api/proxy/{instance_id}")
        return self._parse_instance(data)

    def delete_proxy(self, instance_id: str) -> bool:
        if not instance_id:
            raise ProxyValidationError("instance_id required")
        data = self._request("DELETE", f"/api/proxy/{instance_id}")
        return "message" in data

    def bulk_delete(self, instance_ids: Optional[List[str]] = None, delete_all: bool = False) -> int:
        if not delete_all and not instance_ids:
            raise ProxyValidationError("Provide instance_ids or set delete_all=True")
        body: Dict[str, Any] = {}
        if delete_all:
            body["delete_all"] = True
        else:
            body["instance_ids"] = instance_ids
        data = self._request("POST", "/api/proxy/bulk_delete", json=body)
        return int(data.get("deleted_count", 0))

    def cleanup_expired(self) -> int:
        data = self._request("POST", "/api/cleanup")
        cleaned = data.get("cleaned_instances", [])
        return len(cleaned)

    def stats(self) -> Dict[str, Any]:
        return self._request("GET", "/api/stats")

    # -------------------- Convenience operations --------------------
    def get_or_create(self, proxy_type: str, interface: str, prefer: str = "auto") -> ProxyInstance:
        for inst in self.list_proxies():
            if inst.type == proxy_type and inst.interface == interface and not inst.expired:
                return inst
        return self.create_proxy(proxy_type, interface)

    def get_ready_requests_proxies(self, proxy_type: str, interface: str, prefer: str = "auto") -> Dict[str, str]:
        inst = self.get_or_create(proxy_type, interface, prefer=prefer)
        return inst.to_requests_proxies(prefer=prefer)

    def ensure_temp(self, proxy_type: str, ttl: int, interface: Optional[str] = None, prefer: str = "auto") -> Dict[str, str]:
        inst = self.create_temp_proxy(proxy_type, ttl, interface)
        return inst.to_requests_proxies(prefer=prefer)
