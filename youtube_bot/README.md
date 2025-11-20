# YouTube View Bot

GUI-based bot để tự động tăng view YouTube với proxy rotation và profile management.

## Tính Năng

- 🎯 GUI đơn giản, dễ sử dụng
- 🔄 Tự động lấy video mới nhất từ kênh YouTube
- 🌐 Tạo proxy IPv6 cho mỗi view (anti-detection)
- 🎭 Tạo profile Hidemium với fingerprint độc lập
- 🍪 Tạo cookies thực tế (100-300 cookies/profile)
- 🔍 Duyệt web ngẫu nhiên trước khi xem video (Bing, Yahoo, Wikipedia)
- ⏱️ Thời gian xem tùy chỉnh với random ±3s
- 🧹 Auto cleanup: đóng profile, xóa proxy & profile sau mỗi view
- 🧵 Hỗ trợ đa luồng

## Yêu Cầu

- Python 3.8+
- Proxy API server chạy tại `http://127.0.0.1:5000`
- Hidemium service chạy tại `http://127.0.0.1:2222`
- Network interface hỗ trợ IPv6

## Cài Đặt

```bash
pip install -r requirements.txt
playwright install chromium
```

## Sử Dụng

### Khởi động GUI

```bash
python youtube_view_bot.py
```

### Các Bước

1. **Nhập URL kênh YouTube** (ví dụ: `https://www.youtube.com/@channelname`)
2. **Cấu hình:**
   - Số luồng: 1-20 (khuyến nghị 3-5)
   - Thời gian xem: tối thiểu 10 giây
   - Số lượng view mục tiêu
   - Network interface (mặc định: `Ethernet`)
3. **Nhấn Start** - Bot sẽ tự động:
   - Lấy video mới nhất
   - Chạy các worker song song
   - Hiển thị log realtime
4. **Nhấn Stop** nếu muốn dừng

## Quy Trình Mỗi Worker

```
1. Tạo proxy IPv6 (SOCKS5)
   ↓
2. Tạo profile Hidemium với proxy
   ↓
3. Duyệt 3-5 trang web ngẫu nhiên
   ↓
4. Tạo 100-300 cookies thực tế
   ↓
5. Truy cập video YouTube
   ↓
6. Click play (không autoplay)
   ↓
7. Xem video trong thời gian cài đặt (±3s)
   ↓
8. Đóng profile
   ↓
9. Xóa proxy và profile
```

## Cấu Trúc

```
youtube_view_bot.py       # Main GUI application
youtube_bot/
  ├── __init__.py
  ├── youtube_helper.py   # YouTube channel parser
  └── worker.py           # Worker thread với automation
```

## Anti-Detection Features

- ✅ Proxy IPv6 độc lập mỗi view
- ✅ Fingerprint browser khác nhau (Hidemium)
- ✅ Cookies thực tế từ browsing history
- ✅ Thời gian xem random hóa
- ✅ User behavior simulation (scroll, random pauses)
- ✅ No autoplay (manual click)

## Troubleshooting

### Hidemium service không chạy
```bash
# Khởi động Hidemium service trước
```

### Proxy API không available
```bash
# Kiểm tra proxy server tại http://127.0.0.1:5000
curl http://127.0.0.1:5000/api/stats
```

### Không lấy được video mới nhất
- Kiểm tra URL kênh đúng format
- Kênh phải có video public
- Thử format: `@username` hoặc `/channel/CHANNEL_ID`

### Worker bị lỗi
- Xem log chi tiết trong GUI
- Giảm số luồng nếu hệ thống chậm
- Tăng thời gian xem nếu video dài

## Notes

- Bot chỉ dùng cho mục đích testing
- Mỗi view tốn 1 proxy và 1 profile (auto cleanup)
- Khuyến nghị chạy 3-5 luồng đồng thời
- Thời gian xem nên >= 30s để YouTube tính view
- Profile được tạo local (is_local=True)

## License

MIT
