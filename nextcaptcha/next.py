import logging
import time
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import requests
import urllib3
import base64
import os

logging.basicConfig(level=logging.INFO)

# Các loại CAPTCHA
RECAPTCHAV2_TYPE = "RecaptchaV2TaskProxyless"
HCAPTCHA_TYPE = "HCaptchaTaskProxyless"
TURNSTILE_TYPE = "TurnstileTaskProxyless"
IMAGE_CAPTCHA_TYPE = "ImageToTextTask"

TIMEOUT = 120

PENDING_STATUS = "pending"
PROCESSING_STATUS = "processing"
READY_STATUS = "ready"
FAILED_STATUS = "failed"


class TaskBadParametersError(Exception):
    pass


class ApiClient:
    HOST = "https://api.yescaptcha.com"

    def __init__(self, client_key: str, solft_id: str = "", callback_url: str = "", open_log: bool = True) -> None:
        self.client_key = client_key
        self.solft_id = solft_id
        self.callback_url = callback_url
        self.open_log = open_log
        self.session = requests.session()

        adapter = HTTPAdapter(pool_maxsize=1000)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)

        urllib3.disable_warnings()

    def _get_balance(self) -> str:
        resp = self.session.post(url=self.HOST + "/getBalance", json={"clientKey": self.client_key})
        if resp.status_code != 200:
            if self.open_log:
                logging.error(f"Error: {resp.status_code} {resp.text}")
            return resp.json()
        if self.open_log:
            logging.info(f"Balance: {resp.json().get('balance')}")
        return resp.json().get("balance")

    def _send(self, task: dict) -> dict:
        data = {
            "clientKey": self.client_key,
            "softId": self.solft_id,
            "callbackUrl": self.callback_url,
            "task": task,
        }
        resp = self.session.post(url=self.HOST + "/createTask", json=data)
        if resp.status_code != 200:
            if self.open_log:
                logging.error(f"Error: {resp.status_code} {resp.text}")
                logging.error(f"Data: {data}")
            return resp.json()
        resp = resp.json()
        task_id = resp.get("taskId")
        if self.open_log:
            logging.info(f"Task {task_id} created {resp}")

        start_time = time.time()
        while True:
            if time.time() - start_time > TIMEOUT:
                return {"errorId": 12, "errorDescription": "Timeout", "status": "failed"}

            resp = self.session.post(url=self.HOST + "/getTaskResult",
                                     json={"clientKey": self.client_key, "taskId": task_id})
            if resp.status_code != 200:
                if self.open_log:
                    logging.error(f"Error: {resp.status_code} {resp.text}")
                return resp.json()
            status = resp.json().get("status")
            if self.open_log:
                logging.info(f"Task status: {status}")
            if status == READY_STATUS:
                if self.open_log:
                    logging.info(f"Task {task_id} ready {resp.json()}")
                return resp.json()
            if status == FAILED_STATUS:
                if self.open_log:
                    logging.error(f"Task {task_id} failed {resp.json()}")
                return resp.json()
            time.sleep(2)


class YesCaptchaAPI:
    def __init__(self, client_key: str, solft_id: str = "", callback_url: str = "", open_log: bool = True) -> None:
        logging.info(f"YesCaptchaAPI created with clientKey={client_key}")
        self.api = ApiClient(client_key=client_key, solft_id=solft_id, callback_url=callback_url, open_log=open_log)

    def recaptchav2(self, website_url: str, website_key: str, **kwargs) -> dict:
        task = {
            "type": RECAPTCHAV2_TYPE,
            "websiteURL": website_url,
            "websiteKey": website_key,
        }
        return self.api._send(task)

    def hcaptcha(self, website_url: str, website_key: str, **kwargs) -> dict:
        task = {
            "type": HCAPTCHA_TYPE,
            "websiteURL": website_url,
            "websiteKey": website_key,
        }
        return self.api._send(task)

    def turnstile(self, website_url: str, website_key: str, **kwargs) -> dict:
        """Giải Cloudflare Turnstile CAPTCHA"""
        task = {
            "type": TURNSTILE_TYPE,
            "websiteURL": website_url,
            "websiteKey": website_key,
        }
        return self.api._send(task)

    def image_captcha(self, image_base64: str = "", case_sensitive: bool = False) -> dict:
        """Giải CAPTCHA hình ảnh (nhập ký tự)"""
        task = {
            "type": IMAGE_CAPTCHA_TYPE,
            "body": image_base64,
            "case": case_sensitive
        }
        return self.api._send(task)

    def get_balance(self) -> str:
        return self.api._get_balance()


def test_cloudflare_turnstile():
    """Test Cloudflare Turnstile CAPTCHA trên trang 2captcha"""
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.chrome.service import Service
        import time
        
        print("☁️ Đang test Cloudflare Turnstile CAPTCHA...")
        
        # Khởi động Chrome
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        try:
            # Mở trang demo Cloudflare Turnstile của 2captcha
            print("📄 Đang mở trang 2captcha Cloudflare Turnstile demo...")
            demo_url = "https://auth.rumble.com/signup?theme=s&redirect_uri=https%3A%2F%2Frumble.com%2F&lang=en_US"
            driver.get(demo_url)
            
            # Chờ trang load
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            time.sleep(5)
            
            initial_url = driver.current_url
            print(f"📍 URL ban đầu: {initial_url}")
            
            # IN RA TOÀN BỘ TRANG ĐỂ DEBUG
            print("🔍 Đang phân tích cấu trúc trang...")
            page_source = driver.page_source
            
            # Tìm tất cả các element có thể liên quan đến Turnstile
            print("🔎 Tìm kiếm Cloudflare Turnstile elements...")
            
            # Cách 1: Tìm div chứa Turnstile
            turnstile_divs = driver.find_elements(By.XPATH, "//div[contains(@class, 'cf-turnstile')]")
            print(f"📦 Tìm thấy {len(turnstile_divs)} div cf-turnstile")
            
            for i, div in enumerate(turnstile_divs):
                print(f"  Div {i+1}: class='{div.get_attribute('class')}' data-sitekey='{div.get_attribute('data-sitekey')}'")
            
            # Cách 2: Tìm iframe của Cloudflare
            iframes = driver.find_elements(By.TAG_NAME, "iframe")
            print(f"🖼️ Tìm thấy {len(iframes)} iframe trên trang:")
            
            for i, iframe in enumerate(iframes):
                src = iframe.get_attribute('src') or ''
                title = iframe.get_attribute('title') or ''
                print(f"  Iframe {i+1}: src='{src[:100]}...' title='{title}'")
            
            # Cách 3: Tìm bằng data-sitekey
            sitekey_elements = driver.find_elements(By.XPATH, "//*[@data-sitekey]")
            print(f"🔑 Tìm thấy {len(sitekey_elements)} elements với data-sitekey:")
            
            for i, elem in enumerate(sitekey_elements):
                sitekey = elem.get_attribute('data-sitekey')
                tag = elem.tag_name
                classes = elem.get_attribute('class') or ''
                print(f"  Element {i+1}: <{tag}> class='{classes}' data-sitekey='{sitekey}'")
            
            # Cách 4: Tìm script chứa turnstile
            scripts = driver.find_elements(By.TAG_NAME, "script")
            turnstile_scripts = []
            for script in scripts:
                src = script.get_attribute('src') or ''
                if 'turnstile' in src.lower() or 'challenges.cloudflare.com' in src:
                    turnstile_scripts.append(src)
            
            print(f"📜 Tìm thấy {len(turnstile_scripts)} script liên quan đến Turnstile:")
            for script in turnstile_scripts:
                print(f"  Script: {script[:100]}...")
            
            # XÁC ĐỊNH WEBSITE KEY
            website_key = None
            
            # Ưu tiên tìm từ data-sitekey
            for elem in sitekey_elements:
                potential_key = elem.get_attribute('data-sitekey')
                if potential_key and len(potential_key) > 10:
                    website_key = potential_key
                    print(f"✅ Tìm thấy website key từ data-sitekey: {website_key}")
                    break
            
            # Nếu không tìm thấy, thử các key mặc định cho demo
            if not website_key:
                # Key demo phổ biến cho Cloudflare Turnstile
                demo_keys = [
                    "0x4AAAAAAABS7vwBOPVpo2sP",  # Key demo phổ biến
                    "1x00000000000000000000AA",   # Key test
                    "2x00000000000000000000AB"    # Key test khác
                ]
                
                # Kiểm tra xem key nào có trong trang
                for demo_key in demo_keys:
                    if demo_key in page_source:
                        website_key = demo_key
                        print(f"✅ Sử dụng website key demo: {website_key}")
                        break
            
            if not website_key:
                print("❌ Không tìm thấy website key, đang thử key mặc định...")
                website_key = "0x4AAAAAAABS7vwBOPVpo2sP"
            
            print(f"🎯 Sử dụng website key: {website_key}")
            
            # GIẢI CLOUDFLARE TURNSTILE
            print("🤖 Đang gửi yêu cầu giải Cloudflare Turnstile...")
            captcha_api = YesCaptchaAPI(client_key="559d1b2771bedd55455c09865b97be55e04a0a9877978")
            
            result = captcha_api.turnstile(
                website_url=initial_url,
                website_key=website_key
            )
            
            if result and result.get("status") == "ready":
                token = result.get("solution", {}).get("token", "")
                print(f"✅ Cloudflare Turnstile giải thành công!")
                print(f"🔐 Token nhận được (50 ký tự đầu): {token[:50]}...")
                
                if token:
                    # THỰC HIỆN SUBMIT FORM VỚI TOKEN
                    print("🔄 Đang xử lý token...")
                    
                    # Cách 1: Tìm form và input ẩn
                    forms = driver.find_elements(By.TAG_NAME, "form")
                    print(f"📝 Tìm thấy {len(forms)} form trên trang")
                    
                    for i, form in enumerate(forms):
                        form_html = form.get_attribute('outerHTML')[:200]
                        print(f"  Form {i+1}: {form_html}...")
                    
                    # Tìm input cho token
                    token_inputs = driver.find_elements(By.XPATH, "//input[@type='hidden' and contains(@name, 'cf')]")
                    if not token_inputs:
                        token_inputs = driver.find_elements(By.XPATH, "//input[@type='hidden' and contains(@name, 'token')]")
                    if not token_inputs:
                        token_inputs = driver.find_elements(By.XPATH, "//input[@type='hidden']")
                    
                    print(f"🔍 Tìm thấy {len(token_inputs)} input ẩn")
                    
                    # Set token vào input ẩn
                    for input_elem in token_inputs:
                        input_name = input_elem.get_attribute('name') or ''
                        driver.execute_script(f"arguments[0].value = '{token}';", input_elem)
                        print(f"✅ Đã set token vào input: name='{input_name}'")
                    
                    # Cách 2: Sử dụng JavaScript để trigger Turnstile
                    js_script = f"""
                    // Thử tìm và set token cho Turnstile
                    var token = '{token}';
                    
                    // Tìm tất cả các element có thể chứa token
                    var hiddenInputs = document.querySelectorAll('input[type="hidden"]');
                    hiddenInputs.forEach(function(input) {{
                        if (input.name && (input.name.includes('cf') || input.name.includes('token'))) {{
                            input.value = token;
                            console.log('Set token for input: ' + input.name);
                        }}
                    }});
                    
                    // Thử trigger sự kiện turnstile
                    if (window.turnstile) {{
                        var widgets = document.querySelectorAll('[data-sitekey]');
                        widgets.forEach(function(widget) {{
                            try {{
                                turnstile.execute(widget, {{response: token}});
                                console.log('Executed turnstile with token');
                            }} catch (e) {{
                                console.log('Error executing turnstile: ' + e);
                            }}
                        }});
                    }}
                    
                    return 'Token processing completed';
                    """
                    
                    js_result = driver.execute_script(js_script)
                    print(f"🔄 Kết quả JavaScript: {js_result}")
                    
                    # TÌM VÀ CLICK NÚT SUBMIT
                    print("🔘 Đang tìm nút submit...")
                    submit_selectors = [
                        "//button[@type='submit']",
                        "//input[@type='submit']", 
                        "//button[contains(text(), 'Submit')]",
                        "//button[contains(text(), 'Verify')]",
                        "//button[contains(text(), 'Check')]"
                    ]
                    
                    submitted = False
                    for selector in submit_selectors:
                        try:
                            submit_btn = WebDriverWait(driver, 10).until(
                                EC.element_to_be_clickable((By.XPATH, selector))
                            )
                            submit_btn.click()
                            print(f"✅ Đã click submit với: {selector}")
                            submitted = True
                            break
                        except Exception as e:
                            print(f"⚠️ Không thể click {selector}: {e}")
                    
                    if not submitted:
                        # Thử submit form đầu tiên
                        try:
                            forms[0].submit()
                            print("✅ Đã submit form đầu tiên")
                            submitted = True
                        except:
                            print("⚠️ Không thể submit form")
                    
                    if submitted:
                        print("⏳ Đang chờ kết quả xác minh...")
                        time.sleep(10)
                        
                        # KIỂM TRA KẾT QUẢ
                        current_url = driver.current_url
                        page_text = driver.page_source.lower()
                        
                        print(f"🌐 URL hiện tại: {current_url}")
                        
                        if current_url != initial_url:
                            print("🎉 THÀNH CÔNG! Đã chuyển trang - CAPTCHA đã được vượt qua!")
                        elif 'success' in page_text or 'verified' in page_text or 'correct' in page_text:
                            print("🎉 THÀNH CÔNG! Thông báo thành công xuất hiện!")
                        elif 'error' in page_text or 'invalid' in page_text or 'failed' in page_text:
                            print("❌ THẤT BẠI! Thông báo lỗi xuất hiện!")
                        else:
                            print("ℹ️ Không xác định được kết quả rõ ràng")
                            # Chụp ảnh để debug
                            driver.save_screenshot("turnstile_result.png")
                            print("📸 Đã chụp ảnh kết quả: turnstile_result.png")
                    else:
                        print("❌ Không thể submit form")
                        
                else:
                    print("❌ Không nhận được token từ API")
            else:
                error_msg = result.get('errorDescription', 'Unknown error') if result else 'No response'
                print(f"❌ Giải Cloudflare Turnstile thất bại: {error_msg}")
                
        except Exception as e:
            print(f"❌ Lỗi: {e}")
            import traceback
            traceback.print_exc()
            
        finally:
            print("⏰ Đóng trình duyệt sau 10 giây...")
            time.sleep(10)
            driver.quit()
            print("🔒 Đã đóng trình duyệt")
            
    except Exception as e:
        print(f"❌ Lỗi khởi động: {e}")


def check_balance_and_demo():
    """Kiểm tra số dư và chạy demo"""
    print("🚀 BẮT ĐẦU TEST CLOUDFLARE TURNSTILE")
    print("=" * 60)
    
    MY_CLIENT_KEY = "559d1b2771bedd55455c09865b97be55e04a0a9877978"
    
    print(f"🔑 Client Key: {MY_CLIENT_KEY[:20]}...")
    
    try:
        captcha_api = YesCaptchaAPI(client_key=MY_CLIENT_KEY)
        
        print("💰 Đang kiểm tra số dư tài khoản...")
        balance_result = captcha_api.get_balance()
        
        if isinstance(balance_result, dict) and 'errorId' in balance_result:
            error_msg = balance_result.get('errorDescription', 'Unknown error')
            print(f"❌ Lỗi: {error_msg}")
        else:
            print(f"✅ Số dư: {balance_result}")
            print("\n🎯 Đang test Cloudflare Turnstile...")
            test_cloudflare_turnstile()
            
    except Exception as e:
        print(f"❌ Lỗi: {e}")
    
    print("=" * 60)
    print("🏁 KẾT THÚC")


if __name__ == "__main__":
    check_balance_and_demo()