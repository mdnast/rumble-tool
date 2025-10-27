# 🚀 CÀI ĐẶT VÀ SỬ DỤNG NHANH

## ✅ Yêu cầu hệ thống

- **Python**: 3.8+ (Đang dùng: Python 3.12)
- **Chrome Browser**: Đã cài đặt trên máy
- **Windows**: 10/11 (hoặc Linux/Mac)
- **RAM**: Tối thiểu 4GB
- **Internet**: Kết nối ổn định

---

## 📦 Bước 1: Cài đặt

### 1.1. Kiểm tra Python

```bash
python --version
# Phải là Python 3.8 trở lên
```

### 1.2. Cài đặt dependencies

```bash
# Từ thư mục gốc C:\rumble-tool

# Kích hoạt virtual environment
.venv\Scripts\activate

# Cài đặt packages
pip install -r python\requirements.txt

# Cài setuptools (bắt buộc)
pip install setuptools
```

### 1.3. Kiểm tra cài đặt

```bash
python -c "import undetected_chromedriver; import selenium; print('OK')"
# Phải hiện "OK"
```

---

## 🎯 Bước 2: Chạy Tool

### Option 1: Dùng file .bat (Dễ nhất)

```bash
# Từ thư mục python\
cd python
RUN.bat
```

Chọn từ menu:
- **1** = Chạy Ultimate version (bypass đầy đủ) ⭐ KHUYẾN NGHỊ
- **2** = Chạy version gốc (không bypass)
- **3** = Test stealth (kiểm tra bypass)
- **4-6** = Quick run với số lần khác nhau

### Option 2: Chạy trực tiếp

```bash
cd python

# Chạy Ultimate version
python main_ultimate.py

# Hoặc Quick run
python run_quick.py

# Với options
python run_quick.py --count 3
python run_quick.py --proxy http://proxy.com:8080
python run_quick.py --headless --count 5
```

### Option 3: Test trước

```bash
cd python

# Test xem có bị phát hiện bot không
python test_stealth.py
```

---

## ⚙️ Bước 3: Cấu hình (Tùy chọn)

### 3.1. NextCaptcha API Key

Mở file `python/main_ultimate.py`, tìm dòng 33:

```python
CAPTCHA_API_KEY = "559d1b2771bedd55455c09865b97be55e04a0a9877978"
```

Thay bằng API key của bạn nếu cần.

**Kiểm tra balance**:
- Tool sẽ tự động hiển thị balance khi chạy
- Hoặc kiểm tra tại: https://yescaptcha.com

### 3.2. Proxy (Tùy chọn)

**Cách 1**: File `python/proxy_config.py`

```python
PROXY_LIST = [
    "http://user:pass@proxy1.com:8080",
    "http://user:pass@proxy2.com:8080",
]
USE_PROXY_ROTATION = True
```

**Cách 2**: Command line

```bash
python run_quick.py --proxy http://user:pass@proxy.com:8080
```

### 3.3. Headless Mode

Trong `main_ultimate.py`, hàm `main()`:

```python
HEADLESS = True  # True = không hiện browser, False = hiện browser
```

Hoặc command line:

```bash
python run_quick.py --headless
```

---

## 🧪 Bước 4: Test

### 4.1. Test Stealth

```bash
cd python
python test_stealth.py
```

**Kết quả mong đợi**:
```
✅ PASSED: Stealth successful on Bot.Sannysoft
✅ PASSED: Stealth successful on AreYouHeadless
✅ PASSED: Successfully loaded Rumble.com
🎉 ALL TESTS PASSED!
```

### 4.2. Test Registration

```bash
cd python
python run_quick.py --count 1
```

**Kết quả mong đợi**:
```
✅ Undetected ChromeDriver initialized successfully
✅ Stealth test PASSED - Bot detection bypassed!
✅ Registration page loaded
✅ All form fields filled successfully
🎉 SUCCESS! Password page reached!
```

---

## 📊 Bước 5: Xem kết quả

### 5.1. Logs

```bash
# Xem log real-time (nếu có tail command)
tail -f python\logs\rumble_ultimate.log

# Hoặc mở file trực tiếp
notepad python\logs\rumble_ultimate.log
```

### 5.2. Screenshots

Trong thư mục `python/logs/`:
- `screenshot_registration_page_*.png` - Trang đăng ký
- `screenshot_before_fill_*.png` - Trước khi điền form
- `screenshot_after_fill_*.png` - Sau khi điền form
- `screenshot_after_submit_*.png` - Sau khi submit
- `screenshot_*_error_*.png` - Khi có lỗi

---

## 🐛 Xử lý lỗi thường gặp

### ❌ Error: "ModuleNotFoundError: No module named 'distutils'"

**Giải pháp**:
```bash
pip install setuptools
```

### ❌ Error: "ChromeDriver not found"

**Giải pháp**:
```bash
pip install webdriver-manager --upgrade
```

Hoặc cài Chrome browser nếu chưa có.

### ❌ Error: "CAPTCHA solving failed"

**Nguyên nhân**: 
- Hết credit NextCaptcha
- Network timeout

**Giải pháp**:
1. Kiểm tra balance: Tool sẽ hiện balance khi chạy
2. Nạp thêm credit tại: https://yescaptcha.com
3. Kiểm tra mạng/proxy

### ❌ Error: "Timeout loading registration page"

**Giải pháp**:
1. Kiểm tra kết nối internet
2. Thử tắt proxy
3. Tăng timeout trong code
4. Đợi vài phút rồi thử lại

### ❌ Error: "selenium.common.exceptions.WebDriverException"

**Giải pháp**:
```bash
# Cài lại selenium và undetected-chromedriver
pip uninstall selenium undetected-chromedriver -y
pip install selenium==4.15.0 undetected-chromedriver==3.5.4
```

### ❌ Vẫn bị phát hiện là bot

**Giải pháp**:
1. Sử dụng proxy (residential proxy tốt nhất)
2. Tăng delay giữa các hành động:
   ```python
   # Trong main_ultimate.py
   HumanBehavior.random_delay(1.0, 3.0)  # Tăng từ 0.5-2.0
   ```
3. Xóa Chrome profile cũ:
   - Windows: `%LOCALAPPDATA%\Google\Chrome\User Data`
4. Chạy test stealth để kiểm tra:
   ```bash
   python test_stealth.py
   ```

---

## 📈 Tối ưu Success Rate

### 1. Sử dụng Proxy chất lượng

```python
# Residential proxy (tốt nhất)
python run_quick.py --proxy http://user:pass@residential-proxy.com:8080

# Datacenter proxy (tạm được)
python run_quick.py --proxy http://user:pass@datacenter-proxy.com:8080
```

### 2. Tăng delay giữa các hành động

Trong `stealth_utils.py`, class `HumanBehavior`:

```python
@staticmethod
def random_delay(min_seconds=1.0, max_seconds=3.0):  # Tăng từ 0.5-2.0
    delay = random.uniform(min_seconds, max_seconds)
    time.sleep(delay)
    return delay

@staticmethod
def typing_delay():
    return random.uniform(0.08, 0.20)  # Tăng từ 0.05-0.15 (chậm hơn)
```

### 3. Chạy vào giờ thấp điểm

- **Tốt**: 2AM - 6AM (giờ Việt Nam)
- **Tránh**: 8AM - 10PM (giờ cao điểm)

### 4. Không spam quá nhiều

```bash
# Tốt: Chạy từng đợt nhỏ
python run_quick.py --count 3
# Đợi 10-30 phút
python run_quick.py --count 3

# Tránh: Chạy liên tục quá nhiều
python run_quick.py --count 100  # ❌ Dễ bị ban IP
```

### 5. Headless mode (nhanh hơn nhưng dễ bị phát hiện hơn)

```bash
# Với browser hiển thị (bypass tốt hơn)
python run_quick.py --count 3

# Headless (nhanh hơn nhưng bypass kém hơn)
python run_quick.py --count 3 --headless
```

---

## 💰 Chi phí

### NextCaptcha API

| CAPTCHA Type | Chi phí/lần |
|--------------|-------------|
| Cloudflare Turnstile | ~$0.001 |
| reCAPTCHA v2 | ~$0.002 |
| hCaptcha | ~$0.002 |

**Ví dụ**: 
- 100 lần đăng ký = ~$0.10 - $0.20
- 1000 lần = ~$1.00 - $2.00

### Proxy (Tùy chọn)

| Loại | Chi phí |
|------|---------|
| Residential proxy | $5-15/GB |
| Datacenter proxy | $1-5/GB |
| Free proxy | $0 (không ổn định) |

---

## 📝 Checklist trước khi chạy

- [ ] Python 3.8+ đã cài
- [ ] Chrome browser đã cài
- [ ] Virtual environment đã kích hoạt
- [ ] Dependencies đã cài (`pip install -r requirements.txt`)
- [ ] Setuptools đã cài (`pip install setuptools`)
- [ ] NextCaptcha API key có credit (check balance)
- [ ] Proxy đã config (nếu dùng)
- [ ] Đã test stealth (`python test_stealth.py`)

---

## 🎯 Quick Commands

```bash
# 1. Setup lần đầu
.venv\Scripts\activate
pip install -r python\requirements.txt
pip install setuptools

# 2. Test stealth
cd python
python test_stealth.py

# 3. Chạy 1 lần test
python run_quick.py --count 1

# 4. Chạy production (3-5 lần)
python run_quick.py --count 3
python run_quick.py --count 5 --headless

# 5. Với proxy
python run_quick.py --proxy http://user:pass@proxy.com:8080 --count 3

# 6. Xem logs
notepad logs\rumble_ultimate.log

# 7. Dọn dẹp logs cũ
del logs\*.log
del logs\*.png
```

---

## 📞 Support

- 📖 **Hướng dẫn đầy đủ**: [HUONG_DAN_SU_DUNG.md](HUONG_DAN_SU_DUNG.md)
- 📚 **README**: [README.md](README.md)
- 🐛 **Logs**: `python/logs/rumble_ultimate.log`
- 💬 **NextCaptcha**: https://yescaptcha.com

---

**Chúc bạn bypass thành công! 🎉**
