# HƯỚNG DẪN SỬ DỤNG IPv6 Proxy API

> Tổng hợp từ mã nguồn `api_server.py`, `proxy_server.py`, các script tạo và kiểm tra proxy. API chạy tại `http://127.0.0.1:5000` (Flask + Waitress). Mỗi proxy được cấp một địa chỉ IPv6 riêng và lắng nghe qua cổng nội bộ (localhost) cho HTTP hoặc SOCKS5.

## 1. Kiến Trúc & Nguyên Tắc
- Mỗi lần gọi `/api/create_proxy` sẽ:
  1. Sinh IPv6 mới (không tái sử dụng) qua `IPv6Generator`.
  2. Gán IPv6 vào interface Windows được chỉ định.
  3. Khởi chạy server proxy dạng socket nội bộ (listen `127.0.0.1:<dynamic_port>`).
  4. Lưu instance vào bộ nhớ (`proxy_instances`).
- Proxy outbound KẾT NỐI IPv6-ONLY (không fallback IPv4). Nếu host không có AAAA record => trả về lỗi 502.
- Loại proxy hỗ trợ: `http`, `socks5`, `both`.
- Proxy thường sống mãi cho đến khi gọi DELETE (auto-cleanup idle TẮT). Proxy tạm (temp) có TTL.

## 2. Danh Sách Endpoint
| Method | Path | Mô tả | Body / Params | Trả về chính |
|--------|------|-------|---------------|--------------|
| POST | `/api/create_proxy` | Tạo proxy mới | `{ type, interface }` (`interface` bắt buộc) | `instance_id`, `proxy_endpoint` hoặc `endpoints`, `ipv6_address` |
| GET | `/api/list_proxies` | Liệt kê tất cả proxy | - | `proxies[]` + stats |
| GET | `/api/proxy/<id>` | Chi tiết một proxy | - | Thông tin + stats |
| DELETE | `/api/proxy/<id>` | Xóa proxy | - | `message` |
| POST | `/api/proxy/bulk_delete` | Xóa nhiều proxy | `{ instance_ids[] }` hoặc `{ delete_all: true }` | `deleted_count` |
| POST | `/api/proxy/create_temp` | Tạo proxy tạm TTL | `{ type, ttl, interface? }` | giống create + `expires_at` |
| POST | `/api/cleanup` | Dọn proxy tạm hết hạn | - | `cleaned_instances` |
| GET | `/api/stats` | Thống kê tổng quan | - | `total_proxies`, `interfaces[]`, bytes |
| GET | `/api/health` | Kiểm tra tình trạng | - | `status` |

### 2.1. Request Body `create_proxy`
```json
{
  "type": "socks5" | "http" | "both",
  "interface": "Ethernet"  // BẮT BUỘC: tên interface đang hoạt động
}
```
- `both`: trả về hai cổng: HTTP và SOCKS5.
- Nếu thiếu `interface` => 400 `Interface name is required...`

### 2.2. Response Ví Dụ (SOCKS5)
```json
{
  "instance_id": "e5e8...",
  "proxy_endpoint": "127.0.0.1:63124",
  "ipv6_address": "2001:db8:...",
  "interface": "Ethernet",
  "type": "socks5",
  "created_at": 1731920000.123
}
```

### 2.3. Response (BOTH)
```json
{
  "instance_id": "2d47...",
  "ipv6_address": "2001:db8:...",
  "interface": "Ethernet",
  "type": "both",
  "created_at": 1731920100.456,
  "endpoints": {
    "http": "127.0.0.1:63130",
    "socks5": "127.0.0.1:63131"
  }
}
```

## 3. Ví Dụ CURL (PowerShell)
```powershell
# Tạo SOCKS5 proxy
curl -X POST http://127.0.0.1:5000/api/create_proxy `
  -H "Content-Type: application/json" `
  -d '{"type":"socks5","interface":"Ethernet"}'

# Tạo HTTP proxy
curl -X POST http://127.0.0.1:5000/api/create_proxy `
  -H "Content-Type: application/json" `
  -d '{"type":"http","interface":"Ethernet"}'

# Tạo cả hai
curl -X POST http://127.0.0.1:5000/api/create_proxy `
  -H "Content-Type: application/json" `
  -d '{"type":"both","interface":"Ethernet"}'

# Danh sách
curl http://127.0.0.1:5000/api/list_proxies

# Chi tiết một instance
curl http://127.0.0.1:5000/api/proxy/<INSTANCE_ID>

# Xóa một proxy
curl -X DELETE http://127.0.0.1:5000/api/proxy/<INSTANCE_ID>

# Bulk delete
curl -X POST http://127.0.0.1:5000/api/proxy/bulk_delete `
  -H "Content-Type: application/json" `
  -d '{"instance_ids":["ID1","ID2"]}'

# Delete all
curl -X POST http://127.0.0.1:5000/api/proxy/bulk_delete `
  -H "Content-Type: application/json" `
  -d '{"delete_all":true}'
```

## 4. Sử Dụng Trong Python
### 4.1. Tạo Proxy và Test SOCKS5
```python
import requests
# Tạo
resp = requests.post("http://127.0.0.1:5000/api/create_proxy",
                     json={"type": "socks5", "interface": "Ethernet"}, timeout=30)
info = resp.json()
endpoint = info["proxy_endpoint"]  # 127.0.0.1:<port>
proxies = {
    "http": f"socks5://{endpoint}",
    "https": f"socks5://{endpoint}"
}
print(requests.get("https://api.ipify.org?format=json", proxies=proxies, timeout=15).json())
```
### 4.2. Dùng HTTP Proxy
```python
resp = requests.post("http://127.0.0.1:5000/api/create_proxy",
                     json={"type": "http", "interface": "Ethernet"}, timeout=30)
info = resp.json()
endpoint = info["proxy_endpoint"]
proxies = {
    "http": f"http://{endpoint}",
    "https": f"http://{endpoint}"
}
print(requests.get("http://httpbin.org/ip", proxies=proxies, timeout=15).text)
```
### 4.3. urllib + PySocks
```python
import urllib.request
endpoint = "127.0.0.1:63124"
handler = urllib.request.ProxyHandler({
  "http": f"socks5://{endpoint}",
  "https": f"socks5://{endpoint}"
})
opener = urllib.request.build_opener(handler)
print(opener.open("http://httpbin.org/ip", timeout=10).read())
```

## 5. Stats & Giám Sát
- `GET /api/stats` trả: tổng bytes, connections, interface list.
- Mỗi instance có `stats` từ `proxy_server.get_stats()`:
  - `connections`: số phiên đã chấp nhận.
  - `bytes_sent`, `bytes_received`.
  - `last_activity_ts`, `uptime`.
- Không có endpoint riêng lấy stats từng phần; dùng `/api/proxy/<id>`.

## 6. Xóa & Dọn Dẹp
- Xóa đơn: `DELETE /api/proxy/<id>`.
- Xóa hàng loạt: `POST /api/proxy/bulk_delete`.
- Proxy TẠM tạo bằng `/api/proxy/create_temp` có TTL => cleanup bằng `/api/cleanup` hoặc thread nền.
- Proxy thường SỐNG MÃI cho đến khi xóa (idle cleanup DISABLED).

## 7. Lỗi Phổ Biến & Khắc Phục
| Vấn đề | Nguyên nhân | Khắc phục |
|--------|-------------|-----------|
| 400 Interface name is required | Thiếu `interface` trong body | Chỉ định tên interface hợp lệ (ví dụ `Ethernet`) |
| 500 Failed to assign IPv6 | Hệ thống không gán IPv6 | Kiểm tra quyền admin, driver mạng, firewall |
| 502 Bad Gateway - IPv6 Only | Đích không hỗ trợ IPv6 / timeout | Thử domain khác có AAAA, kiểm tra connectivity |
| Timeout khi tạo proxy | Interface không phản hồi | Xác nhận interface hoạt động, thử lại với tên chính xác |
| Không tạo firewall rule | Quyền bị hạn chế | Chạy PowerShell/EXE dưới quyền Administrator |

### Kiểm tra firewall thủ công
```powershell
Get-NetFirewallRule -DisplayName "Allow IPv6 Outbound Proxy"
New-NetFirewallRule -DisplayName "Allow IPv6 Outbound Proxy" -Direction Outbound -Protocol TCP -Action Allow
```

## 8. Bảo Mật & Khuyến Nghị
- API hiện chỉ bind `127.0.0.1` (an toàn nội bộ). Nếu mở ra ngoài cần:
  - Thêm auth token / IP whitelist.
  - Rate limiting (Flask middleware hoặc reverse proxy).
- Mỗi proxy có IPv6 riêng: giảm correlation nhưng tăng số lượng địa chỉ – cần quản lý giới hạn hệ thống.

## 9. Mở Rộng Gợi Ý (Future)
- Thêm tham số TTL trực tiếp vào `/api/create_proxy`.
- Endpoint kiểm tra IP outbound: `/api/proxy/<id>/test` trả về IP thực.
- Tính năng recycle IPv6 để tránh cạn prefix.
- Logging chi tiết per-instance tách file.

## 10. Quy Trình Mẫu Tổng Hợp
```powershell
# 1. Lấy danh sách interface
curl http://127.0.0.1:5000/api/stats
# 2. Tạo proxy SOCKS5
curl -X POST http://127.0.0.1:5000/api/create_proxy -H "Content-Type: application/json" -d '{"type":"socks5","interface":"Ethernet"}'
# 3. Dùng endpoint trả về trong ứng dụng (socks5://127.0.0.1:<port>)
# 4. Kiểm tra hoạt động
curl http://127.0.0.1:5000/api/proxy/<INSTANCE_ID>
# 5. Xóa khi xong
curl -X DELETE http://127.0.0.1:5000/api/proxy/<INSTANCE_ID>
```

## 11. FAQ Nhanh
**Hỏi:** Có thể dùng cho IPv4 không?  
**Đáp:** Thiết kế hiện tại cưỡng bức IPv6 outbound; nếu đích không có IPv6 => lỗi 502.

**Hỏi:** Vì sao port thay đổi mỗi lần?  
**Đáp:** Port được bind với giá trị 0 => hệ thống cấp phát port khả dụng tự động.

**Hỏi:** Có giới hạn số proxy?  
**Đáp:** Phụ thuộc số IPv6 có thể gán vào interface + tài nguyên hệ thống (threads, sockets).

---
**Phiên bản tài liệu:** 1.0  
**Nguồn:** Tự động trích xuất từ mã nguồn ngày hiện tại.
