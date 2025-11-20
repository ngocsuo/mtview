# Hidemium Module

Python client cho Hidemium API (local service tại `http://127.0.0.1:2222`).

## Tính Năng
- Lấy danh sách default config
- Tạo profile theo default config ID (nhanh)
- Tạo profile custom (tuỳ biến fingerprint)
- Mở/đóng profile
- Xóa profile
- Kiểm tra readiness & trạng thái running
- Tích hợp proxy (format `PROTOCOL|HOST|PORT|USER|PASS`)

## Cài Đặt
```bash
pip install -r requirements.txt
```

## Sử Dụng Nhanh

### Tạo Profile Từ Default Config
```python
from hidemium_module import HidemiumClient

client = HidemiumClient()

# Kiểm tra service
if not client.health():
    print("Hidemium service not running!")
    exit(1)

# Lấy default configs
configs = client.get_default_configs(page=1, limit=5)
data = configs.get("data", {})
items = data.get("content", []) if isinstance(data, dict) else data
first_id = items[0]["id"] if items else None

# Tạo profile
resp = client.create_profile_by_default(first_id, is_local=True)
uuid = resp.get("uuid") or resp.get("profileUUID")
print(f"Created profile: {uuid}")

# Đợi sẵn sàng
client.check_profile_readiness(uuid)

# Mở profile với proxy
client.open_profile(uuid, proxy="SOCKS5|127.0.0.1|63124")

# ... automation ...

# Đóng và xóa
client.close_profile_with_check(uuid)
client.delete_profiles([uuid], is_local=True)
```

### Tạo Profile Custom
```python
profile = client.create_profile(
    profile_name="Gmail_VN",
    os="win",
    browser="chrome",
    proxy="SOCKS5|127.0.0.1|65000",
    canvas="noise",
    webRTC="disabled",
    language="vi-VN",
    resolution="1920x1080",
    doNotTrack="true",
)
uuid = profile.get("uuid")
```

### Tích Hợp Proxy Module
```python
from proxy_module import ProxyManager
from hidemium_module import HidemiumClient

pm = ProxyManager()
hc = HidemiumClient()

# Tạo proxy IPv6
proxy_inst = pm.create_proxy("socks5", "Ethernet")
endpoint = list(proxy_inst.endpoints.values())[0]  # e.g., 127.0.0.1:63124
proxy_str = f"SOCKS5|{endpoint.replace(':', '|')}"

# Tạo và mở profile
result = hc.create_and_open(
    profile_name="AutoProfile",
    proxy=proxy_str,
    wait_ready=True,
)
uuid = result["uuid"]

# ... automation ...

# Cleanup
hc.close_profile_with_check(uuid)
hc.delete_profiles([uuid])
pm.delete_proxy(proxy_inst.instance_id)
```

## API Methods

### Core
- `health()` - Kiểm tra service
- `get_default_configs(page, limit)` - Lấy default configs
- `create_profile_by_default(config_id, is_local)` - Tạo từ default
- `create_profile_custom(payload, is_local)` - Tạo custom
- `create_profile(name, os, browser, proxy, **kwargs)` - Helper tạo custom

### Operations
- `open_profile(uuid, command, proxy)` - Mở profile
- `close_profile(uuid)` - Đóng profile
- `delete_profiles(uuids, is_local)` - Xóa profiles

### Status
- `authorize_status(uuid)` - Kiểm tra đang chạy
- `get_profile_info(uuid)` - Thông tin cơ bản
- `get_profile_detail(uuid, is_local)` - Thông tin chi tiết
- `check_profile_readiness(uuid, max_retries, retry_delay)` - Đợi sẵn sàng

### Convenience
- `close_profile_with_check(uuid, retries, delay)` - Đóng và xác minh
- `create_and_open(name, os, browser, proxy, ...)` - Tạo + mở một lần

## Proxy Format
```
PROTOCOL|HOST|PORT[|USER|PASS]
```
Ví dụ:
- `SOCKS5|127.0.0.1|63124`
- `HTTP|proxy.example.com|8080|user|pass`

## Lỗi Phổ Biến
- `HidemiumAPIError`: API trả về lỗi hoặc không phản hồi
- `HidemiumValidationError`: Tham số đầu vào không hợp lệ

## Troubleshooting
- Service không chạy: Kiểm tra port 2222
- UUID không có sau create: In full response để debug
- Profile không đóng: Dùng `close_profile_with_check` với retries cao hơn
- Proxy không hoạt động: Kiểm tra format chuỗi, test proxy riêng trước

## Notes
- Proxy có thể gắn lúc tạo (trong payload) hoặc lúc mở (param)
- `is_local=True` lưu profile trên disk local
- Default config giúp tạo nhanh nhưng ít tuỳ biến
- Custom profile cho phép kiểm soát đầy đủ fingerprint
