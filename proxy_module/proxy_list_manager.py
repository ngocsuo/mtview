"""Proxy List Manager - Quản lý proxy từ file txt"""

import re
from typing import List, Optional, Dict
from dataclasses import dataclass


@dataclass
class ProxyEntry:
    """Đại diện cho một proxy entry từ file."""
    protocol: str  # "http" hoặc "socks5"
    host: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None
    
    def to_hidemium_format(self) -> str:
        """Chuyển đổi sang format Hidemium: PROTOCOL|HOST|PORT|USERNAME|PASSWORD"""
        protocol_upper = self.protocol.upper()
        if self.username and self.password:
            return f"{protocol_upper}|{self.host}|{self.port}|{self.username}|{self.password}"
        else:
            return f"{protocol_upper}|{self.host}|{self.port}"
    
    def to_endpoint_format(self) -> str:
        """Chuyển đổi sang format endpoint: host:port"""
        return f"{self.host}:{self.port}"
    
    def __str__(self) -> str:
        if self.username and self.password:
            return f"{self.protocol}://{self.host}:{self.port}:{self.username}:{self.password}"
        else:
            return f"{self.protocol}://{self.host}:{self.port}"


class ProxyListManager:
    """Quản lý danh sách proxy từ file txt."""
    
    def __init__(self, proxy_file: Optional[str] = None):
        """
        Khởi tạo ProxyListManager.
        
        Args:
            proxy_file: Đường dẫn đến file chứa danh sách proxy
        """
        self.proxy_file = proxy_file
        self.proxies: List[ProxyEntry] = []
        self.current_index = 0
        
        if proxy_file:
            self.load_proxies(proxy_file)
    
    def load_proxies(self, proxy_file: str) -> int:
        """
        Load danh sách proxy từ file.
        
        Format hỗ trợ:
        - socks5://ip:port
        - socks5://ip:port:username:password
        - http://ip:port
        - http://ip:port:username:password
        
        Args:
            proxy_file: Đường dẫn đến file
            
        Returns:
            Số lượng proxy đã load thành công
        """
        self.proxy_file = proxy_file
        self.proxies = []
        self.current_index = 0
        
        try:
            with open(proxy_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                
                # Bỏ qua dòng trống và comment
                if not line or line.startswith('#'):
                    continue
                
                proxy = self._parse_proxy_line(line)
                if proxy:
                    self.proxies.append(proxy)
                else:
                    print(f"Warning: Không thể parse dòng {line_num}: {line}")
            
            return len(self.proxies)
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Không tìm thấy file: {proxy_file}")
        except Exception as e:
            raise Exception(f"Lỗi khi đọc file proxy: {e}")
    
    def _parse_proxy_line(self, line: str) -> Optional[ProxyEntry]:
        """
        Parse một dòng proxy.
        
        Args:
            line: Dòng proxy cần parse
            
        Returns:
            ProxyEntry nếu parse thành công, None nếu thất bại
        """
        # Pattern: protocol://host:port hoặc protocol://host:port:username:password
        # Hỗ trợ: socks5, http, https
        pattern = r'^(socks5|http|https)://([^:]+):(\d+)(?::([^:]+):(.+))?$'
        match = re.match(pattern, line, re.IGNORECASE)
        
        if not match:
            return None
        
        protocol = match.group(1).lower()
        # Chuyển https thành http (vì Hidemium chỉ hỗ trợ http/socks5)
        if protocol == 'https':
            protocol = 'http'
        
        host = match.group(2)
        port = int(match.group(3))
        username = match.group(4) if match.group(4) else None
        password = match.group(5) if match.group(5) else None
        
        return ProxyEntry(
            protocol=protocol,
            host=host,
            port=port,
            username=username,
            password=password
        )
    
    def get_next_proxy(self) -> Optional[ProxyEntry]:
        """
        Lấy proxy tiếp theo theo kiểu round-robin.
        
        Returns:
            ProxyEntry hoặc None nếu không có proxy
        """
        if not self.proxies:
            return None
        
        proxy = self.proxies[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.proxies)
        return proxy
    
    def get_proxy_count(self) -> int:
        """Trả về số lượng proxy trong danh sách."""
        return len(self.proxies)
    
    def reset_index(self):
        """Reset index về 0."""
        self.current_index = 0

