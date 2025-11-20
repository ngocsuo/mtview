"""Worker thread for YouTube view bot."""

import threading
import time
import random
from typing import Callable, Optional
from datetime import datetime, timedelta

from proxy_module import ProxyManager, ProxyInstance, ProxyListManager, ProxyEntry
from hidemium_module import HidemiumClient
from playwright.sync_api import sync_playwright, Page


class ViewBotWorker(threading.Thread):
    """Worker thread that handles one view cycle."""
    
    RANDOM_SITES = [
        "https://www.bing.com",
        "https://www.yahoo.com",
        "https://www.wikipedia.org",
    ]
    
    def __init__(
        self,
        worker_id: int,
        video_url: str,
        watch_time: int,
        hidemium_client: HidemiumClient,
        interface: str,
        log_callback: Callable[[str], None],
        proxy_manager: Optional[ProxyManager] = None,
        proxy_list_manager: Optional[ProxyListManager] = None
    ):
        super().__init__(daemon=True)
        self.worker_id = worker_id
        self.video_url = video_url
        self.watch_time = watch_time
        self.proxy_manager = proxy_manager
        self.proxy_list_manager = proxy_list_manager
        self.hidemium_client = hidemium_client
        self.interface = interface
        self.log = log_callback
        self.should_stop = False

        # Proxy tracking
        self.proxy_instance: Optional[ProxyInstance] = None  # For API mode
        self.proxy_entry: Optional[ProxyEntry] = None  # For file mode
        self.proxy_str: Optional[str] = None  # Hidemium format proxy string

        self.profile_uuid: Optional[str] = None
    
    def stop(self):
        """Signal worker to stop."""
        self.should_stop = True
    
    def run(self):
        """Main worker logic."""
        try:
            self.log(f"[Worker {self.worker_id}] Bắt đầu...")
            
            # Random delay to avoid overwhelming APIs (0.5-2s per worker)
            delay = random.uniform(0.5, 2.0)
            time.sleep(delay)
            
            # Step 1: Create proxy
            if not self.create_proxy():
                return
            
            # Step 2: Create and open profile
            if not self.create_profile():
                return
            
            # Step 3: Watch YouTube video (with embedded iframe)
            if not self.watch_video():
                return
            
            self.log(f"[Worker {self.worker_id}] ✅ Hoàn thành")
            
        except Exception as e:
            self.log(f"[Worker {self.worker_id}] ❌ Lỗi: {e}")
            import traceback
            self.log(traceback.format_exc())
        finally:
            self.cleanup()
    
    def create_proxy(self) -> bool:
        """Create or get proxy from configured source."""
        try:
            if self.proxy_manager:
                # API mode: Create proxy from API server
                self.log(f"[Worker {self.worker_id}] Tạo proxy từ API...")
                self.proxy_instance = self.proxy_manager.create_proxy("socks5", self.interface)

                # Get endpoint - should be in format "127.0.0.1:PORT"
                if "socks5" in self.proxy_instance.endpoints:
                    endpoint = self.proxy_instance.endpoints["socks5"]
                else:
                    # Fallback to first available endpoint
                    endpoint = next(iter(self.proxy_instance.endpoints.values()), None)

                if not endpoint:
                    self.log(f"[Worker {self.worker_id}] ❌ Không có endpoint")
                    return False

                # Convert to Hidemium format: SOCKS5|HOST|PORT
                host, port = endpoint.split(':', 1)
                self.proxy_str = f"SOCKS5|{host}|{port}"

                self.log(f"[Worker {self.worker_id}] ✅ Proxy API: {endpoint}")
                return True

            elif self.proxy_list_manager:
                # File mode: Get next proxy from list
                self.log(f"[Worker {self.worker_id}] Lấy proxy từ file...")
                self.proxy_entry = self.proxy_list_manager.get_next_proxy()

                if not self.proxy_entry:
                    self.log(f"[Worker {self.worker_id}] ❌ Không có proxy trong file")
                    return False

                # Convert to Hidemium format
                self.proxy_str = self.proxy_entry.to_hidemium_format()

                self.log(f"[Worker {self.worker_id}] ✅ Proxy File: {self.proxy_entry.to_endpoint_format()}")
                return True

            else:
                self.log(f"[Worker {self.worker_id}] ❌ Không có proxy manager")
                return False

        except Exception as e:
            self.log(f"[Worker {self.worker_id}] ❌ Lỗi tạo proxy: {e}")
            return False
    
    def create_profile(self) -> bool:
        """Create and open Hidemium profile."""
        try:
            self.log(f"[Worker {self.worker_id}] Tạo profile...")
            
            # Get default config
            configs = self.hidemium_client.get_default_configs(page=1, limit=5)
            data = configs.get("data", {})
            items = data.get("content", []) if isinstance(data, dict) else data
            
            if not items:
                self.log(f"[Worker {self.worker_id}] ❌ Không có default config")
                return False
            
            config_id = items[0]["id"]
            
            # Create profile
            resp = self.hidemium_client.create_profile_by_default(config_id, is_local=True)
            
            # Extract UUID from response
            if isinstance(resp.get("content"), dict):
                self.profile_uuid = resp["content"].get("uuid")
            else:
                self.profile_uuid = resp.get("uuid") or resp.get("profileUUID")
            
            if not self.profile_uuid:
                self.log(f"[Worker {self.worker_id}] ❌ Không có UUID")
                return False
            
            self.log(f"[Worker {self.worker_id}] ✅ Profile: {self.profile_uuid}")
            
            # Wait for readiness (best effort)
            time.sleep(2)

            # Open profile with proxy
            if not self.proxy_str:
                self.log(f"[Worker {self.worker_id}] ❌ Không có proxy string")
                return False

            self.log(f"[Worker {self.worker_id}] Opening profile with proxy: {self.proxy_str}")

            open_resp = self.hidemium_client.open_profile(self.profile_uuid, proxy=self.proxy_str)
            
            # Extract WebSocket
            if isinstance(open_resp.get("data"), dict):
                self.ws_endpoint = open_resp["data"].get("web_socket")
            else:
                self.ws_endpoint = None
            
            if not self.ws_endpoint:
                self.log(f"[Worker {self.worker_id}] ⚠️ Không có WebSocket endpoint")
                return False
            
            self.log(f"[Worker {self.worker_id}] ✅ Browser opened")
            return True
            
        except Exception as e:
            self.log(f"[Worker {self.worker_id}] ❌ Lỗi tạo profile: {e}")
            return False
    

    
    def generate_cookies(self, context, page: Page):
        """Generate realistic cookies."""
        try:
            # Get current cookies
            cookies = context.cookies()
            current_count = len(cookies)
            
            # Generate additional cookies to reach 100-300
            target = random.randint(100, 300)
            needed = max(0, target - current_count)
            
            if needed > 0:
                # Generate fake but realistic cookies
                now = datetime.now()
                
                for i in range(needed):
                    cookie_name = f"_ga{random.randint(1000, 9999)}"
                    cookie_value = ''.join(random.choices('0123456789abcdef', k=32))
                    
                    expires = now + timedelta(days=random.randint(30, 365))
                    
                    context.add_cookies([{
                        "name": cookie_name,
                        "value": cookie_value,
                        "domain": ".example.com",
                        "path": "/",
                        "expires": int(expires.timestamp()),
                        "httpOnly": False,
                        "secure": False,
                        "sameSite": "Lax"
                    }])
            
            final_count = len(context.cookies())
            self.log(f"[Worker {self.worker_id}] Cookies: {final_count}")
            
        except Exception as e:
            self.log(f"[Worker {self.worker_id}] ⚠️ Lỗi tạo cookies: {e}")
    
    def watch_video(self) -> bool:
        """Watch YouTube video via embedded iframe on random site."""
        try:
            self.log(f"[Worker {self.worker_id}] Xem video...")
            
            with sync_playwright() as p:
                browser = p.chromium.connect_over_cdp(self.ws_endpoint)
                context = browser.contexts[0] if browser.contexts else browser.new_context()
                page = context.pages[0] if context.pages else context.new_page()
                
                # Pick random site to embed video
                random_site = random.choice(self.RANDOM_SITES)
                self.log(f"[Worker {self.worker_id}] → Vào {random_site}")
                
                page.goto(random_site, wait_until="domcontentloaded", timeout=15000)
                time.sleep(2)
                
                # Generate cookies before injecting video
                self.generate_cookies(context, page)
                
                # Extract video ID from URL
                video_id = self.video_url.split("v=")[-1].split("&")[0] if "v=" in self.video_url else self.video_url.split("/")[-1]
                
                # Inject YouTube embed iframe (no autoplay) in corner of page
                inject_script = f"""
                () => {{
                    // Create floating container in bottom-right corner
                    const container = document.createElement('div');
                    container.id = 'yt-embed-container';
                    container.style.cssText = `
                        position: fixed;
                        bottom: 20px;
                        right: 20px;
                        width: 640px;
                        height: 360px;
                        z-index: 999999;
                        box-shadow: 0 4px 20px rgba(0,0,0,0.5);
                        border-radius: 8px;
                        overflow: hidden;
                        background: #000;
                    `;
                    
                    // Create iframe (no autoplay)
                    const iframe = document.createElement('iframe');
                    iframe.width = '640';
                    iframe.height = '360';
                    iframe.src = 'https://www.youtube.com/embed/{video_id}?rel=0&modestbranding=1';
                    iframe.frameBorder = '0';
                    iframe.allow = 'accelerometer; encrypted-media; gyroscope; picture-in-picture';
                    iframe.allowFullscreen = true;
                    iframe.style.cssText = 'border: none; width: 100%; height: 100%;';
                    
                    container.appendChild(iframe);
                    document.body.appendChild(container);
                    
                    return true;
                }}
                """
                
                page.evaluate(inject_script)
                self.log(f"[Worker {self.worker_id}] ✅ Đã inject video embed")
                time.sleep(3)
                
                # Switch to iframe and click play
                try:
                    iframe = page.frame_locator('iframe[src*="youtube.com/embed"]')
                    
                    # Click play button in iframe
                    self.log(f"[Worker {self.worker_id}] 🖱️ Click play...")
                    iframe.locator('button.ytp-large-play-button').click(timeout=5000)
                    time.sleep(2)
                    
                    self.log(f"[Worker {self.worker_id}] ▶️ Đang phát video")
                    
                except Exception as e:
                    self.log(f"[Worker {self.worker_id}] ⚠️ Không thể click play: {e}")
                
                # Wait for watch time with random variation
                actual_watch_time = self.watch_time + random.randint(-3, 3)
                actual_watch_time = max(10, actual_watch_time)
                
                self.log(f"[Worker {self.worker_id}] ⏱️ Đợi {actual_watch_time}s...")
                
                for i in range(actual_watch_time):
                    if self.should_stop:
                        break
                    time.sleep(1)
                
                browser.close()
            
            return True
            
        except Exception as e:
            self.log(f"[Worker {self.worker_id}] ❌ Lỗi xem video: {e}")
            return False
    
    def cleanup(self):
        """Clean up resources."""
        try:
            self.log(f"[Worker {self.worker_id}] Dọn dẹp...")
            
            # Close profile
            if self.profile_uuid:
                try:
                    self.hidemium_client.close_profile_with_check(self.profile_uuid, retries=2)
                    self.log(f"[Worker {self.worker_id}] ✅ Đóng profile")
                except Exception as e:
                    self.log(f"[Worker {self.worker_id}] ⚠️ Lỗi đóng profile: {e}")
                
                # Delete profile
                try:
                    self.hidemium_client.delete_profiles([self.profile_uuid], is_local=True)
                    self.log(f"[Worker {self.worker_id}] ✅ Xóa profile")
                except Exception as e:
                    self.log(f"[Worker {self.worker_id}] ⚠️ Lỗi xóa profile: {e}")
            
            # Delete proxy (only for API mode)
            if self.proxy_instance and self.proxy_manager:
                try:
                    self.proxy_manager.delete_proxy(self.proxy_instance.instance_id)
                    self.log(f"[Worker {self.worker_id}] ✅ Xóa proxy API")
                except Exception as e:
                    self.log(f"[Worker {self.worker_id}] ⚠️ Lỗi xóa proxy: {e}")
            elif self.proxy_entry:
                # File mode: No cleanup needed, just log
                self.log(f"[Worker {self.worker_id}] ✅ Proxy file đã sử dụng")
            
        except Exception as e:
            self.log(f"[Worker {self.worker_id}] ❌ Lỗi cleanup: {e}")
