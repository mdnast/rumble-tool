# HƯỚNG DẪN SỬ DỤNG - RUMBLE ULTIMATE BOT BYPASS

## 🎯 Tính năng

Tool này tích hợp **TẤT CẢ** các kỹ thuật bypass bot detection mạnh nhất:

### ✅ Đã tích hợp:

1. **Undetected ChromeDriver** - Driver Chrome không bị phát hiện
2. **NextCaptcha API** - Tự động giải CAPTCHA:
   - ☁️ Cloudflare Turnstile
   - 🔐 reCAPTCHA v2
   - 🛡️ hCaptcha
3. **Advanced Fingerprint Spoofing**:
   - Canvas fingerprinting protection
   - WebGL fingerprinting protection
   - Audio context spoofing
   - Font fingerprinting bypass
   - Screen & viewport randomization
4. **Human-like Behavior Simulation**:
   - Random mouse movements
   - Natural scrolling patterns
   - Human typing speed with variations
   - Reading simulation with pauses
5. **Proxy Support** - Hỗ trợ HTTP/SOCKS5 proxy với rotation
6. **JavaScript Stealth Injection** - 50+ anti-detection scripts

---

## 📦 Cài đặt

### Bước 1: Cài đặt thư viện

```bash
# Từ thư mục gốc
cd C:\rumble-tool
.venv\Scripts\activate
pip install -r python\requirements.txt
```

### Bước 2: Kiểm tra Chrome/ChromeDriver

Tool sử dụng **undetected-chromedriver** - tự động tải ChromeDriver phù hợp.

**Lưu ý**: Cần có Chrome browser đã cài đặt trên máy.

---

## 🚀 Cách sử dụng

### Option 1: Chạy bản Ultimate (Khuyến nghị)

```bash
cd C:\rumble-tool\python
C:\rumble-tool\.venv\Scripts\python.exe main_ultimate.py
```

### Option 2: Chạy bản cũ (không có bypass)

```bash
cd C:\rumble-tool\python
C:\rumble-tool\.venv\Scripts\python.exe main.py
```

---

## ⚙️ Cấu hình

### 1. NextCaptcha API Key

File: `python/main_ultimate.py`

```python
# Line 33
CAPTCHA_API_KEY = "559d1b2771bedd55455c09865b97be55e04a0a9877978"
```

**Kiểm tra số dư**: Tool sẽ tự động kiểm tra balance khi chạy.

**Mua thêm credit**: https://yescaptcha.com

### 2. Proxy (Tùy chọn)

File: `python/proxy_config.py`

```python
PROXY_LIST = [
    "http://username:password@proxy.example.com:8080",
    "http://proxy.example.com:8080",
    "socks5://username:password@proxy.example.com:1080",
]

USE_PROXY_ROTATION = True  # Xoay proxy ngẫu nhiên
USE_SINGLE_PROXY = False
SINGLE_PROXY = None
```

**Hoặc** set trực tiếp trong `main_ultimate.py`:

```python
# Line trong main()
PROXY = "http://username:password@proxy.example.com:8080"
```

### 3. Headless Mode

File: `python/main_ultimate.py`

```python
# Line trong main()
HEADLESS = True  # True = ẩn browser, False = hiện browser
```

---

## 🔧 Tùy chỉnh nâng cao

### Điều chỉnh hành vi giống người

File: `python/stealth_utils.py`

```python
# Class HumanBehavior

# Tốc độ gõ phím
def typing_delay():
    return random.uniform(0.05, 0.15)  # Giảm = nhanh hơn

# Delay giữa các hành động
def random_delay(min_seconds=0.5, max_seconds=2.0):
    # Tăng = chậm hơn, giống người hơn
```

### Thay đổi User-Agent

File: `python/stealth_utils.py`

```python
def get_random_user_agent():
    chrome_versions = ['119', '120', '121', '122', '123']
    # Thêm version Chrome mới hơn nếu cần
```

### Viewport size

File: `python/stealth_utils.py`

```python
def random_viewport():
    viewports = [
        {'width': 1920, 'height': 1080},
        {'width': 1366, 'height': 768},
        # Thêm size khác nếu cần
    ]
```

---

## 📊 Logs và Screenshots

### Logs

- File: `python/logs/rumble_ultimate.log`
- Chứa toàn bộ quá trình chạy, errors, warnings

### Screenshots

- Thư mục: `python/logs/`
- Tự động chụp ảnh tại các bước quan trọng:
  - `screenshot_registration_page_*.png` - Trang đăng ký
  - `screenshot_before_fill_*.png` - Trước khi điền form
  - `screenshot_after_fill_*.png` - Sau khi điền form
  - `screenshot_after_submit_*.png` - Sau khi submit
  - `screenshot_*_error_*.png` - Khi có lỗi

---

## 🐛 Xử lý lỗi thường gặp

### 1. "ChromeDriver not found"

**Giải pháp**: Tool tự động tải, nhưng nếu lỗi:

```bash
# Cài manually
pip install webdriver-manager
```

### 2. "CAPTCHA solving failed"

**Nguyên nhân**: 
- Hết credit NextCaptcha
- Website key không đúng
- Network timeout

**Giải pháp**:
- Kiểm tra balance: https://yescaptcha.com
- Xem log để biết lỗi chi tiết
- Thử chạy lại

### 3. "Timeout loading registration page"

**Nguyên nhân**: 
- Mạng chậm
- Rumble đang maintenance
- Proxy không hoạt động

**Giải pháp**:
- Kiểm tra kết nối mạng
- Thử tắt proxy
- Đợi vài phút rồi chạy lại

### 4. "Still detected as bot"

**Nguyên nhân**: 
- IP đã bị blacklist
- Cookie/session cũ

**Giải pháp**:
- Sử dụng proxy
- Xóa Chrome profile: `%LOCALAPPDATA%\Google\Chrome\User Data`
- Tăng delay giữa các hành động

### 5. "Module not found"

**Giải pháp**:

```bash
# Cài lại toàn bộ dependencies
pip install -r python\requirements.txt --force-reinstall
```

---

## 🎓 Tips để bypass hiệu quả

### 1. Sử dụng Proxy

- **Residential proxy** tốt nhất (như Bright Data, Smartproxy)
- **Datacenter proxy** cũng được nhưng dễ bị chặn hơn
- Xoay proxy sau mỗi vài lần đăng ký

### 2. Tăng delay giống người

Trong `main_ultimate.py`, tăng thời gian chờ:

```python
# Sau khi điền form
HumanBehavior.random_delay(1.0, 3.0)  # Tăng từ 0.5-2.0

# Sau khi click
time.sleep(random.uniform(2, 4))  # Tăng lên
```

### 3. Chạy vào giờ thấp điểm

- Tránh giờ cao điểm (anti-bot nghiêm hơn)
- Chạy từng đợt nhỏ, không spam liên tục

### 4. Kiểm tra stealth

Tool có hàm `test_stealth()` tự động check:
- `navigator.webdriver` phải = `undefined`
- `navigator.plugins.length` phải > 0
- `navigator.languages` phải có giá trị

### 5. Monitor logs

Luôn xem logs để biết nguyên nhân thất bại:

```bash
tail -f python/logs/rumble_ultimate.log
```

---

## 📈 Tối ưu hiệu suất

### Chạy nhiều instance

```python
# Tạo file run_multiple.py
import multiprocessing
from main_ultimate import RumbleUltimateBypass

def run_bot(proxy):
    bot = RumbleUltimateBypass(proxy=proxy)
    bot.run_registration()
    bot.close()

if __name__ == "__main__":
    proxies = ["proxy1", "proxy2", "proxy3"]
    
    with multiprocessing.Pool(processes=3) as pool:
        pool.map(run_bot, proxies)
```

### Headless mode (nhanh hơn)

```python
bot = RumbleUltimateBypass(headless=True)
```

---

## 🔒 Bảo mật

### Không commit API key

Thêm vào `.gitignore`:

```
python/logs/
*.log
*.png
config_local.py
```

### Sử dụng environment variables

```python
import os
CAPTCHA_API_KEY = os.getenv("NEXTCAPTCHA_API_KEY", "your-key-here")
```

---

## 📞 Hỗ trợ

### Kiểm tra version

```bash
python -c "import undetected_chromedriver; print(undetected_chromedriver.__version__)"
python -c "import selenium; print(selenium.__version__)"
```

### Update tool

```bash
pip install --upgrade undetected-chromedriver
pip install --upgrade selenium
```

---

## ⚠️ Lưu ý quan trọng

1. **Tốc độ chậm = Bypass tốt**: Đừng cố tăng tốc quá nhanh
2. **Proxy tốt = Success rate cao**: Đầu tư vào proxy chất lượng
3. **NextCaptcha credit**: Mỗi lần giải CAPTCHA tốn ~$0.001-0.003
4. **Rate limiting**: Rumble có thể limit IP/account, đừng spam
5. **Legal**: Sử dụng tool này cần tuân thủ Terms of Service của Rumble

---

## 🎉 Success Indicators

Khi thành công, bạn sẽ thấy:

```
✅ Stealth test PASSED - Bot detection bypassed!
✅ Registration page loaded
✅ No CAPTCHA detected (hoặc CAPTCHA solved successfully)
✅ All form fields filled successfully
✅ Form submitted!
🎉 SUCCESS! Password page reached!
```

---

## 🔄 Updates

**Version**: 1.0.0 Ultimate
**Last update**: 2025-10-25
**Changelog**:
- ✅ Tích hợp undetected-chromedriver
- ✅ NextCaptcha API (Turnstile/reCAPTCHA/hCaptcha)
- ✅ Advanced fingerprint spoofing
- ✅ Human-like behavior simulation
- ✅ Proxy support

---

**Good luck bypassing! 🚀**
