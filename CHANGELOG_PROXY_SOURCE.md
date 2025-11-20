# Changelog - Thêm Chức Năng Nguồn Proxy

## Tổng Quan Thay Đổi

Đã thêm chức năng cho phép người dùng chọn nguồn proxy:
- **API Server**: Tạo proxy IPv6 động từ API server (chế độ cũ)
- **Import File**: Sử dụng danh sách proxy từ file txt (chế độ mới)

## Files Mới

### 1. `proxy_module/proxy_list_manager.py`
Module quản lý danh sách proxy từ file txt.

**Classes:**
- `ProxyEntry`: Đại diện cho một proxy entry
  - Thuộc tính: protocol, host, port, username, password
  - Methods: `to_hidemium_format()`, `to_endpoint_format()`, `__str__()`

- `ProxyListManager`: Quản lý danh sách proxy
  - Methods:
    - `load_proxies(proxy_file)`: Load proxy từ file
    - `get_next_proxy()`: Lấy proxy tiếp theo (round-robin)
    - `get_proxy_count()`: Số lượng proxy
    - `reset_index()`: Reset index về 0

**Format hỗ trợ:**
```
socks5://ip:port
socks5://ip:port:username:password
http://ip:port
http://ip:port:username:password
```

### 2. `examples/proxy_list_sample.txt`
File mẫu chứa danh sách proxy với nhiều format khác nhau.

### 3. `examples/test_proxy_list.py`
Script test để kiểm tra ProxyListManager.

### 4. `PROXY_SOURCE_GUIDE.md`
Hướng dẫn chi tiết sử dụng chức năng nguồn proxy.

### 5. `CHANGELOG_PROXY_SOURCE.md`
File này - tóm tắt các thay đổi.

## Files Đã Sửa

### 1. `proxy_module/__init__.py`
- Import và export `ProxyListManager` và `ProxyEntry`

### 2. `youtube_view_bot.py`
**Imports:**
- Thêm `filedialog` từ tkinter
- Thêm `ProxyListManager` từ proxy_module

**GUI Changes:**
- Thêm radio button chọn nguồn proxy (API Server / Import File)
- Thêm field "Proxy File" với nút "Browse..."
- Field "Network Interface" chỉ hiện khi chọn API Server
- Field "Proxy File" chỉ hiện khi chọn Import File

**New Methods:**
- `on_proxy_source_change()`: Xử lý khi đổi nguồn proxy
- `browse_proxy_file()`: Mở dialog chọn file và load proxy

**Modified Methods:**
- `__init__()`: Thêm `proxy_list_manager` attribute
- `validate_inputs()`: Validate proxy source và file
- `run_bot()`: Thêm parameter `proxy_source`, truyền manager tương ứng cho worker

### 3. `youtube_bot/worker.py`
**Imports:**
- Thêm `ProxyListManager` và `ProxyEntry` từ proxy_module

**Constructor Changes:**
- Thêm parameters: `proxy_list_manager` (Optional)
- Đổi `proxy_manager` thành Optional
- Thêm attributes:
  - `proxy_list_manager`: Manager cho file mode
  - `proxy_entry`: ProxyEntry cho file mode
  - `proxy_str`: Proxy string format Hidemium (dùng chung)

**Modified Methods:**

**`create_proxy()`:**
- Hỗ trợ 2 mode:
  - API mode: Tạo proxy từ API server (code cũ)
  - File mode: Lấy proxy từ ProxyListManager
- Chuẩn bị `proxy_str` ở format Hidemium cho cả 2 mode

**`create_profile()`:**
- Sử dụng `self.proxy_str` thay vì parse từ `proxy_instance`
- Hoạt động với cả 2 mode

**`cleanup()`:**
- API mode: Xóa proxy từ API server (code cũ)
- File mode: Chỉ log, không xóa proxy

## Cách Sử Dụng

### Mode 1: API Server (Mặc định)
1. Chọn "API Server"
2. Nhập Network Interface
3. Start

### Mode 2: Import File
1. Chọn "Import File"
2. Click "Browse..." và chọn file proxy
3. Kiểm tra log xem đã load bao nhiêu proxy
4. Start

## Testing

### Test ProxyListManager
```bash
python examples/test_proxy_list.py
```

### Test GUI
1. Chạy `python youtube_view_bot.py`
2. Test cả 2 mode: API Server và Import File
3. Kiểm tra log để xem proxy được sử dụng đúng

## Backward Compatibility

✅ **Hoàn toàn tương thích ngược**
- Chế độ mặc định vẫn là "API Server"
- Code cũ vẫn hoạt động bình thường
- Không breaking changes

## Technical Details

### Proxy Format Conversion

**File format → Hidemium format:**
```
socks5://127.0.0.1:1080:user:pass
↓
SOCKS5|127.0.0.1|1080|user|pass
```

**API format → Hidemium format:**
```
127.0.0.1:1080 (from API)
↓
SOCKS5|127.0.0.1|1080
```

### Round-Robin Algorithm
```python
proxy = proxies[current_index]
current_index = (current_index + 1) % len(proxies)
```

## Future Improvements

Có thể cải thiện thêm:
1. Hỗ trợ proxy rotation strategies khác (random, weighted)
2. Health check proxy trước khi sử dụng
3. Retry với proxy khác nếu proxy hiện tại fail
4. Statistics về proxy usage
5. Hỗ trợ load proxy từ URL
6. Proxy pool management với auto-refresh

## Notes

- Proxy từ file không bị xóa sau khi dùng → có thể tái sử dụng
- Nên có ít nhất số proxy = số luồng để tránh trùng
- File proxy hỗ trợ comment (dòng bắt đầu bằng #)
- Encoding file: UTF-8

