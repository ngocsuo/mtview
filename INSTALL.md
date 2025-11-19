# Installation Guide - MTView Project

Hướng dẫn cài đặt đầy đủ cho máy mới.

## Yêu Cầu Hệ Thống

- Windows 10/11
- Python 3.8 trở lên
- Git
- Network interface hỗ trợ IPv6
- Proxy API server (http://127.0.0.1:5000)
- Hidemium service (http://127.0.0.1:2222)

## Bước 1: Cài Đặt Python

1. Tải Python từ: https://www.python.org/downloads/
2. Chạy installer, **check** "Add Python to PATH"
3. Verify:
```powershell
python --version
```

## Bước 2: Cài Đặt Git

1. Tải Git từ: https://git-scm.com/download/win
2. Chạy installer với cấu hình mặc định
3. Verify:
```powershell
git --version
```

## Bước 3: Clone Repository

```powershell
cd Desktop
git clone https://github.com/ngocsuo/mtview.git
cd mtview
```

## Bước 4: Cài Đặt Dependencies

### Cài Python packages

**Nếu pip hoạt động:**
```powershell
pip install -r requirements.txt
```

**Nếu pip không tìm thấy, dùng python -m:**
```powershell
python -m pip install -r requirements.txt
```

**Hoặc dùng py (Windows):**
```powershell
py -m pip install -r requirements.txt
```

### Cài Playwright browsers
```powershell
python -m playwright install chromium
```

## Bước 5: Kiểm Tra Services

### Kiểm tra Proxy API
```powershell
curl http://127.0.0.1:5000/api/stats
```

### Kiểm tra Hidemium
```powershell
curl http://127.0.0.1:2222/
```

## Bước 6: Test Modules

### Test Proxy Module
```powershell
python -m pytest tests/test_manager.py -v
```

### Test Hidemium Module
```powershell
python -m pytest tests/test_hidemium.py -v
```

Hoặc dùng unittest:
```powershell
python -m unittest discover -s tests -v
```

## Bước 7: Chạy YouTube View Bot

```powershell
python youtube_view_bot.py
```

## Cài Đặt Một Lệnh (PowerShell)

Copy và chạy script sau:

```powershell
# Install Python packages (chọn 1 trong 3 lệnh)
pip install -r requirements.txt
# hoặc
python -m pip install -r requirements.txt
# hoặc
py -m pip install -r requirements.txt

# Install Playwright
python -m playwright install chromium

# Verify installation
python -c "import requests; import playwright; import bs4; print('All packages OK')"
```

## Dependencies List

```
requests>=2.31.0          # HTTP client
playwright>=1.40.0        # Browser automation
beautifulsoup4>=4.12.0    # HTML parsing
```

## Troubleshooting

### Lỗi: "pip is not recognized"
Python đã cài nhưng pip không trong PATH. Thử các cách sau:

**Cách 1: Dùng python -m pip**
```powershell
python -m pip install -r requirements.txt
python -m pip install playwright
```

**Cách 2: Dùng py launcher (Windows)**
```powershell
py -m pip install -r requirements.txt
py -m pip install playwright
```

**Cách 3: Thêm Python vào PATH**
1. Tìm đường dẫn Python: 
   ```powershell
   where python
   # hoặc
   py -c "import sys; print(sys.executable)"
   ```
2. Thêm vào PATH:
   - Mở "Environment Variables"
   - Edit "Path" trong User variables
   - Thêm: `C:\Python3xx\Scripts\` (thay xx bằng version)
   - Restart terminal

**Cách 4: Cài lại Python**
- Download từ python.org
- Uninstall Python cũ
- Install mới, **BẮT BUỘC check "Add Python to PATH"**

### Lỗi: "python not found"
- Cài lại Python và check "Add to PATH"
- Hoặc dùng: `py` thay vì `python`

### Lỗi: "playwright not found"
- Chạy: `python -m pip install playwright`
- Sau đó: `python -m playwright install chromium`

### Lỗi: "No module named 'proxy_module'"
- Đảm bảo đang ở thư mục `mtview`
- Set PYTHONPATH: `$env:PYTHONPATH="C:\path\to\mtview"`

### Hidemium service không chạy
- Khởi động Hidemium trước khi chạy bot
- Kiểm tra port 2222 không bị chiếm

### Proxy API không available
- Khởi động Proxy server
- Kiểm tra port 5000

## Network Interface

Xem danh sách interfaces:
```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

Sử dụng tên interface chính xác (ví dụ: "Ethernet", "Wi-Fi") trong tool.

## Quick Start After Installation

```powershell
# Clone
git clone https://github.com/ngocsuo/mtview.git
cd mtview

# Install
pip install -r requirements.txt
playwright install chromium

# Run
python youtube_view_bot.py
```

## Update Project

```powershell
cd mtview
git pull origin master
pip install -r requirements.txt --upgrade
```
