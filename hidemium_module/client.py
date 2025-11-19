import time
from typing import Optional, Dict, List, Any

import requests

from .exceptions import HidemiumAPIError, HidemiumValidationError


class HidemiumClient:
    """High-level client for Hidemium local API.
    
    Parameters
    ----------
    base_url : str
        Base URL of Hidemium service (default: http://127.0.0.1:2222)
    timeout : int
        Request timeout in seconds
    """

    def __init__(self, base_url: str = "http://127.0.0.1:2222", timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.last_error: Optional[str] = None

    # -------------------- Internal helpers --------------------
    def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Any:
        """Execute HTTP request with error handling."""
        url = f"{self.base_url}{path}"
        
        # Debug logging
        print(f"[DEBUG Hidemium] {method} {url}")
        if params:
            print(f"[DEBUG Hidemium] Params: {params}")
        if json:
            print(f"[DEBUG Hidemium] JSON: {json}")
        
        try:
            resp = requests.request(
                method, url, params=params, json=json, timeout=self.timeout, **kwargs
            )
        except requests.RequestException as e:
            self.last_error = f"HTTP request failed: {e}"
            raise HidemiumAPIError(self.last_error) from e
        
        print(f"[DEBUG Hidemium] Status: {resp.status_code}")
        print(f"[DEBUG Hidemium] Response: {resp.text[:500]}")
        
        if not resp.ok:
            self.last_error = f"API error {resp.status_code}: {resp.text[:200]}"
            raise HidemiumAPIError(self.last_error)
        
        try:
            return resp.json()
        except ValueError:
            # Some endpoints return plain text or empty
            return {"raw": resp.text}

    # -------------------- Health & Default Configs --------------------
    def health(self) -> bool:
        """Check if Hidemium service is running."""
        try:
            resp = requests.get(f"{self.base_url}/", timeout=5)
            # Service is running if we get any response (even 404)
            return True
        except requests.exceptions.ConnectionError:
            self.last_error = "Connection refused"
            return False
        except Exception as e:
            self.last_error = str(e)
            return False

    def get_default_configs(
        self, page: int = 1, limit: int = 10, retries: int = 3, retry_delay: float = 2.0
    ) -> Dict[str, Any]:
        """Fetch default configuration templates.
        
        Returns nested structure; typically extract: data.content or data (list).
        With retry logic for transient 500 errors.
        """
        if page < 1 or limit < 1:
            raise HidemiumValidationError("page and limit must be >= 1")
        
        last_error = None
        for attempt in range(retries):
            try:
                return self._request("GET", "/v2/default-config", params={"page": page, "limit": limit})
            except HidemiumAPIError as e:
                last_error = e
                if attempt < retries - 1:
                    print(f"[RETRY] get_default_configs failed (attempt {attempt+1}/{retries}), retrying in {retry_delay}s...")
                    time.sleep(retry_delay)
                else:
                    raise last_error

    # -------------------- Create Profile --------------------
    def create_profile_by_default(
        self, default_config_id: int, is_local: bool = True
    ) -> Dict[str, Any]:
        """Create profile using a default config ID (fast method).
        
        Returns dict with 'uuid' or 'profileUUID'.
        """
        if default_config_id <= 0:
            raise HidemiumValidationError("default_config_id must be positive")
        return self._request(
            "POST",
            "/create-profile-by-default",
            params={"is_local": str(is_local).lower()},
            json={"defaultConfigId": default_config_id},
        )

    def create_profile_custom(
        self, payload: Dict[str, Any], is_local: bool = True
    ) -> Dict[str, Any]:
        """Create profile with custom fingerprint/system settings.
        
        payload should contain: os, osVersion, browser, version, name, etc.
        """
        if not payload:
            raise HidemiumValidationError("payload cannot be empty")
        return self._request(
            "POST",
            "/create-profile-custom",
            params={"is_local": str(is_local).lower()},
            json=payload,
        )

    def create_profile(
        self,
        profile_name: str,
        os: str = "win",
        browser: str = "chrome",
        proxy: Optional[str] = None,
        extra_fields: Optional[Dict[str, Any]] = None,
        is_local: bool = True,
        **kwargs,
    ) -> Dict[str, Any]:
        """Convenience wrapper to create custom profile with common params.
        
        proxy: format PROTOCOL|HOST|PORT|USER|PASS (USER/PASS optional)
        extra_fields: merge with base payload (can include default_config dict)
        **kwargs: additional fields like canvas, webRTC, language, resolution, etc.
        """
        payload = {
            "name": profile_name,
            "os": os,
            "browser": browser,
            "restoreSession": "true",
        }
        if proxy:
            payload["proxy"] = proxy
        if extra_fields:
            payload.update(extra_fields)
        payload.update(kwargs)
        return self.create_profile_custom(payload, is_local=is_local)

    # -------------------- Open / Close / Delete --------------------
    def open_profile(
        self,
        uuid: str,
        command: Optional[str] = None,
        proxy: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Open (launch) a profile browser instance.
        
        uuid: profile UUID
        command: Chrome/Firefox CLI args (e.g. --lang=vi)
        proxy: PROTOCOL|HOST|PORT|USER|PASS (overrides profile proxy if set)
        """
        if not uuid:
            raise HidemiumValidationError("uuid required")
        params = {"uuid": uuid}
        if command:
            params["command"] = command
        if proxy:
            params["proxy"] = proxy
        return self._request("GET", "/openProfile", params=params)

    def close_profile(self, uuid: str) -> Dict[str, Any]:
        """Close (shutdown) a running profile."""
        if not uuid:
            raise HidemiumValidationError("uuid required")
        return self._request("GET", "/closeProfile", params={"uuid": uuid})

    def delete_profiles(
        self, uuids: List[str], is_local: bool = True
    ) -> Dict[str, Any]:
        """Delete one or more profiles permanently.
        
        uuids: list of profile UUIDs
        """
        if not uuids:
            raise HidemiumValidationError("uuids list cannot be empty")
        return self._request(
            "DELETE",
            "/v1/browser/destroy",
            params={"is_local": str(is_local).lower()},
            json={"uuid_browser": uuids},
        )

    # -------------------- Status & Readiness --------------------
    def authorize_status(self, uuid: str) -> Dict[str, Any]:
        """Check if profile is currently running.
        
        Returns dict with 'status' key (True if running).
        """
        if not uuid:
            raise HidemiumValidationError("uuid required")
        return self._request("GET", "/authorize", params={"uuid": uuid})

    def get_profile_info(self, uuid: str) -> Dict[str, Any]:
        """Get basic profile info (readiness check endpoint)."""
        if not uuid:
            raise HidemiumValidationError("uuid required")
        return self._request("GET", f"/profile/{uuid}")

    def get_profile_detail(self, uuid: str, is_local: bool = True) -> Dict[str, Any]:
        """Get detailed profile data (automation info)."""
        if not uuid:
            raise HidemiumValidationError("uuid required")
        return self._request(
            "GET",
            f"/v2/browser/get-profile-by-uuid/{uuid}",
            params={"is_local": str(is_local).lower()},
        )

    def check_profile_readiness(
        self, uuid: str, max_retries: int = 10, retry_delay: float = 1.0
    ) -> bool:
        """Poll profile info until ready or retries exhausted.
        
        Returns True if profile info available, False otherwise.
        """
        for attempt in range(max_retries):
            try:
                info = self.get_profile_info(uuid)
                if info and isinstance(info, dict):
                    return True
            except HidemiumAPIError:
                pass
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
        return False

    # -------------------- Convenience Workflows --------------------
    def close_profile_with_check(
        self, uuid: str, retries: int = 3, delay_seconds: float = 1.5
    ) -> bool:
        """Close profile and verify shutdown via authorize status.
        
        Returns True if closed successfully.
        """
        try:
            self.close_profile(uuid)
        except HidemiumAPIError:
            pass
        
        for _ in range(retries):
            time.sleep(delay_seconds)
            try:
                auth = self.authorize_status(uuid)
                if not auth.get("status"):
                    return True
            except HidemiumAPIError:
                return True
        return False

    def create_and_open(
        self,
        profile_name: str,
        os: str = "win",
        browser: str = "chrome",
        proxy: Optional[str] = None,
        command: Optional[str] = None,
        wait_ready: bool = True,
        **kwargs,
    ) -> Dict[str, Any]:
        """Create profile, optionally wait for readiness, then open.
        
        Returns dict with 'uuid' and 'open_response'.
        """
        profile = self.create_profile(
            profile_name=profile_name,
            os=os,
            browser=browser,
            proxy=proxy,
            **kwargs,
        )
        uuid = profile.get("uuid") or profile.get("profileUUID")
        if not uuid:
            raise HidemiumAPIError("No UUID returned from create profile")
        
        if wait_ready:
            ready = self.check_profile_readiness(uuid)
            if not ready:
                raise HidemiumAPIError(f"Profile {uuid} not ready after retries")
        
        open_resp = self.open_profile(uuid, command=command, proxy=proxy)
        return {"uuid": uuid, "open_response": open_resp, "profile": profile}
