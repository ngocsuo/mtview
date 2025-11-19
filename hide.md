# HƯỚNG DẪN SỬ DỤNG HIDEMIUM API (Profiles)

> Trích từ mã nguồn: `hidemium_client.py`, `get_hidemium_default_config.py`, `hidemium_profile_templates.json`, `HIDEMIUM_PROFILE_README.md`. Mục tiêu: Lấy default config, tạo profile (default & custom), mở, kiểm tra trạng thái, đóng và xoá profile.

## 1. Tổng Quan Kiến Trúc
- Service Hidemium chạy tại: `http://127.0.0.1:2222` (mặc định).
- Profile = tập hợp fingerprint + thông số hệ thống (OS, browser, canvas, WebRTC...).
- Hai cách tạo profile:
  1. Nhanh: Dùng `defaultConfigId` (ít tuỳ biến).
  2. Custom: Gửi body đầy đủ / merge default config.
- Proxy có thể gắn lúc mở profile (param `proxy`) hoặc nhúng trong payload create (trường `proxy`).
- Chuỗi proxy format: `PROTOCOL|HOST|PORT|USER|PASS` (USER/PASS optional). Ví dụ: `SOCKS5|127.0.0.1|63124`.

## 2. Danh Sách Endpoint Chính
| Method | Endpoint | Mô tả | Body / Params |
|--------|----------|-------|---------------|
| GET | `/v2/default-config?page=&limit=` | Lấy danh sách default configs | Query: `page`, `limit` |
| POST | `/create-profile-by-default?is_local=` | Tạo profile từ default config ID | `{ "defaultConfigId": <int> }` |
| POST | `/create-profile-custom?is_local=` | Tạo profile tùy biến | JSON payload fingerprint + system |
| GET | `/openProfile?uuid=&command=&proxy=` | Mở profile (trả browser launched) | Query params |
| GET | `/closeProfile?uuid=` | Đóng profile | Query param `uuid` |
| GET | `/authorize?uuid=` | Kiểm tra profile đang chạy không | Query param `uuid` |
| DELETE | `/v1/browser/destroy?is_local=` | Xóa nhiều profile | `{ "uuid_browser": ["uuid1", ...] }` |
| GET | `/profile/{uuid}` | Lấy thông tin profile (readiness check) | - |
| GET | `/v2/browser/get-profile-by-uuid/{uuid}?is_local=` | Lấy data chi tiết (automation) | Query `is_local` |

## 3. Lấy Default Config & Chọn ID
### CURL (PowerShell)
```powershell
curl "http://127.0.0.1:2222/v2/default-config?page=1&limit=5"
```
### Python
```python
from hidemium_client import HidemiumClient
client = HidemiumClient()
configs = client.get_default_configs(page=1, limit=5)
# Trích ID đầu tiên
items = []
if isinstance(configs, dict):
    data = configs.get("data")
    if isinstance(data, dict):
        items = data.get("content", [])
    elif isinstance(data, list):
        items = data
elif isinstance(configs, list):
    items = configs
first_id = items[0]["id"] if items else None
print("DefaultConfigId:", first_id)
```
### Script có sẵn
```powershell
python get_hidemium_default_config.py --page 1 --limit 10
python get_hidemium_default_config.py --config-id 24741 --json
```

## 4. Tạo Profile
### 4.1. Theo Default Config ID (Nhanh)
```python
resp = client.create_profile_by_default(default_config_id=24741, is_local=True)
profile_uuid = resp.get("uuid") or resp.get("profileUUID")
```
Request thực tế:
```
POST /create-profile-by-default?is_local=true
Body: { "defaultConfigId": 24741 }
```

### 4.2. Custom (Tuỳ Biến Cao)
```python
profile = client.create_profile(
    profile_name="Gmail_VN",
    os="win",
    browser="chrome",
    proxy="SOCKS5|127.0.0.1|63124",  # tuỳ chọn
    extra_fields={"default_config": items[0]},  # merge default config đầu tiên
    is_local=True,
    webrtc_mode="disabled"
)
profile_uuid = profile.get("uuid")
```

### 4.3. Payload Custom Ví Dụ (Tối Thiểu)
```python
import requests
payload = {
  "os": "win",
  "osVersion": "10",
  "browser": "chrome",
  "version": "139",
  "name": "Basic_Profile",
  "folder_name": "gmail_profiles",
  "language": "vi-VN",
  "resolution": "1920x1080",
  "canvas": "noise",
  "webRTC": "disabled",
  "restoreSession": "true"
}
r = requests.post("http://127.0.0.1:2222/create-profile-custom?is_local=true", json=payload, timeout=30)
print(r.json())
```

### 4.4. Thêm Proxy Trong Payload
```python
payload["proxy"] = "SOCKS5|127.0.0.1|63124"
```

## 5. Mở Profile
Format proxy chuỗi (nếu chưa đưa vào lúc tạo): `SOCKS5|HOST|PORT` hoặc thêm auth.
```python
open_resp = client.open_profile(
    uuid=profile_uuid,
    command="--lang=vi --disable-gpu",
    proxy="SOCKS5|127.0.0.1|63124"
)
```
Raw request:
```
GET /openProfile?uuid=<UUID>&command=--lang=vi&proxy=SOCKS5|127.0.0.1|63124
```

## 6. Kiểm Tra Readiness & Trạng Thái
### Readiness (profile đã sẵn sàng data)
```python
ready = client.check_profile_readiness(profile_uuid, max_retries=10, retry_delay=1.0)
if not ready:
    print("Profile chưa sẵn sàng")
```
### Đang chạy?
```python
auth = client.authorize_status(profile_uuid)
is_running = bool(auth.get("status") is True)
```

## 7. Đóng Profile
### Đơn Giản
```python
close_resp = client.close_profile(profile_uuid)
```
### Đóng + Xác Minh
```python
close_verified = client.close_profile_with_check(profile_uuid, retries=3, delay_seconds=1.5)
print(close_verified)
```

## 8. Xóa Profile
Xóa một hoặc nhiều UUID:
```python
delete_resp = client.delete_profiles([profile_uuid], is_local=True)
```
Raw:
```
DELETE /v1/browser/destroy?is_local=true
Body: { "uuid_browser": ["uuid1", "uuid2"] }
```

## 9. Luồng Hoàn Chỉnh
```python
from hidemium_client import HidemiumClient
client = HidemiumClient()
assert client.health(), client.last_error
cfgs = client.get_default_configs(page=1, limit=5)
# trích first_id như hướng dẫn ở trên
resp = client.create_profile_by_default(first_id, is_local=True)
uuid = resp.get("uuid") or resp.get("profileUUID")
client.check_profile_readiness(uuid)
client.open_profile(uuid, proxy="SOCKS5|127.0.0.1|63124")
# ... thao tác tự động hóa ...
client.close_profile_with_check(uuid)
client.delete_profiles([uuid], is_local=True)
```

## 10. Các Trường Quan Trọng (Từ Template)
| Nhóm | Trường | Ý nghĩa |
|------|--------|---------|
| Core | os, osVersion, browser, version, userAgent | Nền tảng & trình duyệt |
| Profile | name, folder_name, language, resolution | Thông tin hiển thị & giao diện |
| Fingerprint | canvas, webRTC, webGLImage, audioContext, webGLMetadata, clientRectsEnable, noiseFont | Chống nhận dạng |
| Privacy | sslFingerprint, mediaMasking, doNotTrack, disableImage, plugins | Bảo mật |
| Advanced | restoreSession, hidemiumBluetooth, akamaiBypassDns, isCloudFolder | Tính năng nâng cao |
| DNS | dnsMode, dnsType, dnsValue | Cấu hình DNS |
| Proxy | proxy | Gắn proxy vào profile |

## 11. Proxy Tích Hợp Với Module IPv6 Proxy
- Sau khi dùng API riêng tạo proxy: nhận `127.0.0.1:<port>`.
- Gán vào Hidemium open hoặc payload create: `SOCKS5|127.0.0.1|<port>`.
- Nên kiểm tra hoạt động proxy trước bằng test IP.

## 12. Troubleshooting Nhanh
| Vấn đề | Nguyên nhân | Khắc phục |
|--------|-------------|-----------|
| Health check fail | Service chưa chạy / port sai | Kiểm tra tiến trình tại 2222 |
| `defaultConfigId` invalid | ID hết hạn hoặc không tồn tại | Lấy lại danh sách default config |
| Không có `uuid` sau create | API lỗi trả về error | In full response, kiểm tra status_code |
| openProfile lỗi 4xx | UUID sai hoặc chưa tạo | Xác nhận uuid từ response create |
| closeProfile không tắt | Process chưa shutdown | Dùng `close_profile_with_check`, tăng retries |
| delete thất bại | is_local sai | Thử cả true/false; xác định profile lưu local |
| proxy không áp dụng | Format sai | Đúng dạng: `SOCKS5|host|port` hoặc có auth đầy đủ |

## 13. Khuyến Nghị Thực Tế
- Random hóa `osVersion`, `version` để tránh mẫu lặp.
- Duy trì `restoreSession=true` cho Gmail / social login ổn định.
- Đặt `canvas=noise`, `webRTC=disabled` cho môi trường stealth (tuỳ nhu cầu).
- Cache default configs (đừng gọi mỗi lần) để giảm latency.

## 14. Mở Rộng Có Thể Thêm
- Hàm hợp nhất: `create + readiness + open` trả về state cuối.
- Tự động attach proxy tốt nhất (vòng xoay nhiều IPv6).
- Endpoint nội bộ thống kê thời gian sống profile.
- Recycle profile cũ (update fingerprint) thay vì xóa tạo mới.

## 15. Ví Dụ Tạo Stealth Profile + Proxy
```python
profile = client.create_profile(
  profile_name="Stealth_Profile",
  os="win",
  browser="chrome",
  proxy="SOCKS5|127.0.0.1|65000",
  extra_fields={
    "canvas": "noise",
    "webRTC": "disabled",
    "doNotTrack": "true",
    "sslFingerprint": "true"
  },
  is_local=True
)
print(profile)
```

## 16. FAQ
**Q:** Dùng default hay custom tốt hơn?  
**A:** Default nhanh nhưng thiếu tuỳ biến. Custom cho phép kiểm soát fingerprint. 

**Q:** Có thể cập nhật proxy sau khi tạo?  
**A:** Thường thực hiện bằng mở profile với param `proxy`. 

**Q:** Khác biệt `is_local=true/false`?  
**A:** Quyết định nơi lưu trữ profile (local disk vs remote/cloud). 

**Q:** Làm sao biết profile đã thật sự tắt?  
**A:** Gọi `authorize?uuid=...`; nếu `status != True` nghĩa là đã tắt. 

---
**Phiên bản:** 1.0  
**Ngày tạo:** Generated tự động từ source hiện tại.
