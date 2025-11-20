# Hướng Dẫn Sử Dụng Nguồn Proxy

## Tổng Quan

YouTube View Bot hiện hỗ trợ 2 nguồn proxy:

1. **API Server** - Tạo proxy IPv6 động từ API server local (http://127.0.0.1:5000)
2. **Import File** - Sử dụng danh sách proxy từ file txt

## 1. Sử Dụng API Server (Mặc định)

### Yêu Cầu
- Proxy API server phải chạy tại `http://127.0.0.1:5000`
- Network interface hỗ trợ IPv6 (ví dụ: "Ethernet")

### Cách Sử Dụng
1. Chọn radio button **"API Server"**
2. Nhập tên Network Interface (mặc định: "Ethernet")
3. Click **Start**

### Ưu Điểm
- Mỗi view sử dụng proxy IPv6 mới, độc lập
- Tự động tạo và xóa proxy
- Không cần chuẩn bị danh sách proxy trước

### Nhược Điểm
- Yêu cầu API server chạy
- Phụ thuộc vào network interface hỗ trợ IPv6

## 2. Sử Dụng Import File

### Format File Proxy

File proxy là file text (.txt) với mỗi dòng là một proxy theo format:

```
protocol://host:port
protocol://host:port:username:password
```

**Protocol hỗ trợ:**
- `socks5://` - SOCKS5 proxy
- `http://` - HTTP proxy
- `https://` - HTTPS proxy (sẽ tự động chuyển thành HTTP)

### Ví Dụ File Proxy

```txt
# SOCKS5 không auth
socks5://127.0.0.1:1080
socks5://192.168.1.100:1080

# SOCKS5 có auth
socks5://proxy1.example.com:1080:user1:pass1
socks5://proxy2.example.com:1080:user2:pass2

# HTTP không auth
http://127.0.0.1:8080
http://192.168.1.101:3128

# HTTP có auth
http://proxy3.example.com:8080:user3:pass3
http://proxy4.example.com:3128:user4:pass4
```

### Cách Sử Dụng

1. Tạo file proxy theo format trên
2. Trong GUI, chọn radio button **"Import File"**
3. Click nút **"Browse..."** và chọn file proxy
4. Kiểm tra log để xem số lượng proxy đã load
5. Click **Start**

### Cơ Chế Hoạt Động

- Proxy được sử dụng theo kiểu **round-robin** (vòng tròn)
- Mỗi worker lấy proxy tiếp theo từ danh sách
- Khi hết danh sách, quay lại proxy đầu tiên
- Proxy không bị xóa sau khi sử dụng (có thể tái sử dụng)

### Ưu Điểm

- Không cần API server
- Sử dụng proxy có sẵn (mua từ nhà cung cấp)
- Hỗ trợ cả HTTP và SOCKS5
- Hỗ trợ proxy có authentication

### Nhược Điểm

- Cần chuẩn bị danh sách proxy trước
- Proxy có thể bị trùng nếu số worker > số proxy
- Không tự động xóa proxy sau khi dùng

## Test Chức Năng

### Test ProxyListManager

```bash
python examples/test_proxy_list.py
```

### File Mẫu

Xem file mẫu tại: `examples/proxy_list_sample.txt`

## Lưu Ý

1. **Số lượng proxy vs số luồng:**
   - Nên có ít nhất số proxy = số luồng để tránh trùng
   - Nếu proxy < luồng, một số proxy sẽ được dùng nhiều lần

2. **Chất lượng proxy:**
   - Proxy phải hoạt động và có thể kết nối YouTube
   - Nên test proxy trước khi sử dụng

3. **Format file:**
   - Dòng trống và dòng bắt đầu bằng `#` sẽ bị bỏ qua
   - Encoding: UTF-8
   - Mỗi dòng một proxy

4. **Bảo mật:**
   - Không commit file proxy có username/password lên git
   - Giữ file proxy ở local hoặc sử dụng .gitignore

## Troubleshooting

### "File proxy không hợp lệ hoặc rỗng"
- Kiểm tra format của từng dòng proxy
- Đảm bảo file không rỗng
- Xem log để biết dòng nào bị lỗi

### "Không thể parse dòng X"
- Kiểm tra format dòng đó
- Đảm bảo đúng format: `protocol://host:port` hoặc `protocol://host:port:user:pass`

### Proxy không hoạt động
- Test proxy bằng curl hoặc công cụ khác
- Kiểm tra proxy có bị block YouTube không
- Thử đổi sang proxy khác

## API Reference

### ProxyListManager

```python
from proxy_module import ProxyListManager

# Khởi tạo và load file
manager = ProxyListManager("path/to/proxy_list.txt")

# Lấy số lượng proxy
count = manager.get_proxy_count()

# Lấy proxy tiếp theo (round-robin)
proxy = manager.get_next_proxy()

# Chuyển đổi format
hidemium_format = proxy.to_hidemium_format()  # "SOCKS5|HOST|PORT|USER|PASS"
endpoint = proxy.to_endpoint_format()  # "HOST:PORT"
```

### ProxyEntry

```python
from proxy_module import ProxyEntry

# Tạo proxy entry
proxy = ProxyEntry(
    protocol="socks5",
    host="127.0.0.1",
    port=1080,
    username="user",  # Optional
    password="pass"   # Optional
)

# Chuyển đổi format
print(proxy.to_hidemium_format())  # SOCKS5|127.0.0.1|1080|user|pass
print(proxy.to_endpoint_format())  # 127.0.0.1:1080
print(str(proxy))  # socks5://127.0.0.1:1080:user:pass
```

