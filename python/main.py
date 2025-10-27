# rumble_ultimate_fix.py
import time
import logging
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotInteractableException, ElementClickInterceptedException
from fake_useragent import UserAgent
import random
import string
from datetime import datetime, timedelta

# TẠO THƯ MỤC LOGS
os.makedirs('logs', exist_ok=True)

# SETUP LOGGING
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/rumble_tool.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class RumbleAutoRegister:
    def __init__(self, local_api_key=None, nextcaptcha_key=None):
        self.driver = None
        self.ua = UserAgent()
        
        # Import and initialize CAPTCHA solver
        try:
            from captcha_solver import CaptchaSolver
            self.captcha_solver = CaptchaSolver(
                local_api_key=local_api_key,
                nextcaptcha_client_key=nextcaptcha_key
            )
            logger.info("[CAPTCHA] Solver initialized")
        except Exception as e:
            logger.warning(f"[CAPTCHA] Solver not available: {e}")
            self.captcha_solver = None
        
        if not self.setup_driver():
             logger.critical("[FAIL] CRITICAL: Failed to initialize WebDriver during class instantiation.")

    def setup_driver(self):
        """Setup Chrome driver (sử dụng Service() tự động)"""
        if self.driver:
             logger.info("[INFO] Driver already initialized.")
             return True
        try:
            from selenium.webdriver.chrome.options import Options

            chrome_options = Options()
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            try:
                 user_agent = self.ua.random
                 chrome_options.add_argument(f"--user-agent={user_agent}")
                 logger.info(f"[UA] Using User-Agent: {user_agent}")
            except Exception as ua_err:
                 logger.warning(f"[WARN] Could not get random User-Agent, using default: {ua_err}")
            chrome_options.add_argument("--window-size=1200,800")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-gpu")

            try:
                service = Service() # Tự động tìm driver
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            except Exception as driver_init_err:
                logger.error(f"[FAIL] Failed to start ChromeDriver: {driver_init_err}")
                logger.error("   Ensure 'chromedriver.exe' is in your system's PATH, or install 'webdriver-manager' (`pip install webdriver-manager`).")
                return False

            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            logger.info("[OK] Driver initialized successfully")
            return True

        except Exception as e:
            logger.exception(f"[FAIL] Unexpected error during Driver setup: {e}")
            return False

    def navigate_to_registration(self):
        """Điều hướng đến trang đăng ký"""
        if not self.driver:
             logger.error("[FAIL] Cannot navigate: Driver is not initialized.")
             return False
        try:
            registration_url = "https://rumble.com/register/"
            logger.info(f"Navigating to: {registration_url}")
            self.driver.get(registration_url)
            # Đợi cả email và ít nhất một select birthday xuất hiện
            WebDriverWait(self.driver, 20).until(
                EC.all_of(
                    EC.presence_of_element_located((By.NAME, "email")),
                    EC.presence_of_element_located((By.NAME, "birthday_month"))
                )
            )
            logger.info("[OK] Navigated to registration page and basic elements located.")
            time.sleep(random.uniform(1.5, 3.0))
            return True
        except TimeoutException:
             logger.error("[FAIL] Timeout waiting for registration page elements (email/birthday).")
             self.take_screenshot("navigation_timeout")
             return False
        except Exception as e:
            logger.error(f"[FAIL] Navigation failed: {e}")
            self.take_screenshot("navigation_error")
            return False

    def detect_and_solve_turnstile(self, timeout=120):
        """Detect and solve Cloudflare Turnstile CAPTCHA"""
        if not self.captcha_solver:
            logger.warning("[CAPTCHA] No solver configured, skipping")
            return False
        
        try:
            # Check for Turnstile iframe
            iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
            turnstile_found = False
            
            for iframe in iframes:
                src = iframe.get_attribute("src") or ""
                if "challenges.cloudflare.com" in src or "turnstile" in src.lower():
                    turnstile_found = True
                    logger.info("[CAPTCHA] Cloudflare Turnstile detected!")
                    break
            
            if not turnstile_found:
                logger.info("[CAPTCHA] No Turnstile detected")
                return True
            
            # Extract sitekey from page source
            page_source = self.driver.page_source
            sitekey = None
            
            # Try different methods to find sitekey
            import re
            
            # Method 1: data-sitekey attribute
            match = re.search(r'data-sitekey="([^"]+)"', page_source)
            if match:
                sitekey = match.group(1)
            
            # Method 2: sitekey in iframe src
            if not sitekey:
                for iframe in iframes:
                    src = iframe.get_attribute("src") or ""
                    match = re.search(r'sitekey=([^&]+)', src)
                    if match:
                        sitekey = match.group(1)
                        break
            
            # Method 3: Search in JavaScript
            if not sitekey:
                match = re.search(r"sitekey['\"]?\s*[:=]\s*['\"]([^'\"]+)['\"]", page_source)
                if match:
                    sitekey = match.group(1)
            
            if not sitekey:
                logger.error("[CAPTCHA] Could not extract Turnstile sitekey")
                self.take_screenshot("turnstile_no_sitekey")
                return False
            
            logger.info(f"[CAPTCHA] Sitekey found: {sitekey}")
            logger.info("[CAPTCHA] Sending to solver API...")
            
            # Solve CAPTCHA
            current_url = self.driver.current_url
            token = self.captcha_solver.solve_turnstile(current_url, sitekey, timeout)
            
            if not token:
                logger.error("[CAPTCHA] Solver failed to get token")
                return False
            
            logger.info("[CAPTCHA] Token received, injecting...")
            
            # Inject token into page
            inject_script = f"""
            var forms = document.querySelectorAll('form');
            for (var i = 0; i < forms.length; i++) {{
                var input = document.createElement('input');
                input.type = 'hidden';
                input.name = 'cf-turnstile-response';
                input.value = '{token}';
                forms[i].appendChild(input);
            }}
            
            var textarea = document.querySelector('textarea[name="cf-turnstile-response"]');
            if (textarea) {{
                textarea.value = '{token}';
            }}
            
            if (typeof window.turnstile !== 'undefined') {{
                console.log('[CAPTCHA] Turnstile API available, setting token...');
            }}
            
            console.log('[CAPTCHA] Token injected successfully');
            """
            
            self.driver.execute_script(inject_script)
            logger.info("[CAPTCHA] Token injected successfully")
            time.sleep(2)
            
            return True
            
        except Exception as e:
            logger.error(f"[CAPTCHA] Error during Turnstile detection/solving: {e}")
            return False

    # --- HÀM FILL BASIC FIELDS (Sử dụng tên tháng) ---
    def fill_basic_fields(self, user_data):
        """Điền tất cả các field có thể có, dùng tên tháng cho Birthday."""
        if not self.driver: return False
        try:
            logger.info("\n[FORM] Filling form fields...")
            wait = WebDriverWait(self.driver, 10)

            # --- Email ---
            try:
                email_field = wait.until(EC.visibility_of_element_located((By.NAME, "email")))
                email_field.clear()
                for char in user_data['email']:
                    email_field.send_keys(char)
                    time.sleep(random.uniform(0.04, 0.10))
                self.driver.execute_script("arguments[0].dispatchEvent(new Event('blur', { bubbles: true }));", email_field)
                logger.info("   [OK] Email filled and 'blur' triggered")
                time.sleep(random.uniform(0.3, 0.6))
            except (TimeoutException, NoSuchElementException) as e:
                logger.error(f"   [FAIL] Could not find or fill Email field: {e}")
                self.take_screenshot("email_field_error")
                return False

            # --- Username (Kiểm tra sự tồn tại) ---
            try:
                 username_field = WebDriverWait(self.driver, 3).until(
                     EC.visibility_of_element_located((By.NAME, "username"))
                 )
                 username_field.clear()
                 for char in user_data['username']:
                     username_field.send_keys(char)
                     time.sleep(random.uniform(0.04, 0.10))
                 self.driver.execute_script("arguments[0].dispatchEvent(new Event('blur', { bubbles: true }));", username_field)
                 logger.info("   [OK] Username filled and 'blur' triggered")
                 time.sleep(random.uniform(0.3, 0.6))
            except TimeoutException:
                 logger.info("   [INFO] Username field not detected on this form.")
            except Exception as e:
                 logger.warning(f"   [WARN] Error interacting with Username field: {e}")

            # --- Gender (Kiểm tra sự tồn tại và chọn bằng Select + Trigger Events + Click Out) ---
            try:
                gender_select_el = WebDriverWait(self.driver, 3).until(
                    EC.element_to_be_clickable((By.NAME, "gender"))
                )
                Select(gender_select_el).select_by_value(user_data['gender_value'])
                self.driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", gender_select_el)
                self.driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", gender_select_el)
                self.driver.execute_script("arguments[0].dispatchEvent(new Event('blur', { bubbles: true }));", gender_select_el)
                logger.info(f"   [OK] Gender selected & events triggered: {user_data['gender_value']}")
                time.sleep(0.2)
                try:
                    self.driver.find_element(By.XPATH, "//label[contains(text(), 'Email')]").click()
                    logger.info("      Clicked outside Gender select (on Email label).")
                except:
                    self.driver.find_element(By.TAG_NAME, "body").click()
                    logger.info("      Clicked outside Gender select (on body).")
                time.sleep(random.uniform(0.5, 0.8))
            except TimeoutException:
                 logger.info("   [INFO] Gender <select> field not detected on this form.")
            except NoSuchElementException:
                 logger.error(f"   [FAIL] Invalid gender value '{user_data['gender_value']}' for <select name='gender'>")
                 self.take_screenshot("gender_value_error")
            except Exception as e:
                 logger.warning(f"   [WARN] Error selecting/triggering/clicking out Gender: {e}")

            # --- Birthday (Dùng <select> chuẩn + Trigger Events + Click Out) ---
            try:
                # *** SỬ DỤNG select_by_visible_text CHO THÁNG ***
                month_select_el = wait.until(EC.element_to_be_clickable((By.NAME, "birthday_month")))
                Select(month_select_el).select_by_visible_text(user_data['birth_month_text']) # Dùng tên tháng
                self.driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", month_select_el)
                self.driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", month_select_el)
                self.driver.execute_script("arguments[0].dispatchEvent(new Event('blur', { bubbles: true }));", month_select_el)
                time.sleep(0.2)
                logger.info(f"   [OK] Month selected: {user_data['birth_month_text']}")

                # Ngày và Năm vẫn dùng select_by_value
                day_select_el = wait.until(EC.element_to_be_clickable((By.NAME, "birthday_day")))
                Select(day_select_el).select_by_value(user_data['birth_day']) # Dùng giá trị số (dạng chuỗi)
                self.driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", day_select_el)
                self.driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", day_select_el)
                self.driver.execute_script("arguments[0].dispatchEvent(new Event('blur', { bubbles: true }));", day_select_el)
                time.sleep(0.2)
                logger.info(f"   [OK] Day selected: {user_data['birth_day']}")

                year_select_el = wait.until(EC.element_to_be_clickable((By.NAME, "birthday_year")))
                Select(year_select_el).select_by_value(user_data['birth_year']) # Dùng giá trị số (dạng chuỗi)
                self.driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", year_select_el)
                self.driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", year_select_el)
                self.driver.execute_script("arguments[0].dispatchEvent(new Event('blur', { bubbles: true }));", year_select_el)
                time.sleep(0.2)
                logger.info(f"   [OK] Year selected: {user_data['birth_year']}")

                # Click ra ngoài sau khi chọn xong năm sinh
                try:
                    self.driver.find_element(By.XPATH, "//label[contains(text(), 'Email')]").click()
                    logger.info("      Clicked outside Birthday select (on Email label).")
                except:
                    self.driver.find_element(By.TAG_NAME, "body").click()
                    logger.info("      Clicked outside Birthday select (on body).")
                logger.info("   [OK] Birthday selected & events triggered & clicked out")
                time.sleep(random.uniform(0.5, 0.8))
            except (NoSuchElementException, TimeoutException) as bd_err:
                 # Bắt lỗi nếu tên tháng không khớp
                 if 'birth_month_text' in user_data and isinstance(bd_err, NoSuchElementException):
                      logger.error(f"   [FAIL] CRITICAL: Could not find month text '{user_data['birth_month_text']}' in options. Check spelling/case.")
                 else: # Hoặc lỗi timeout khi tìm element
                      logger.error(f"   [FAIL] CRITICAL: Failed to find or select standard <select> birthday fields: {bd_err}")
                 self.take_screenshot("birthday_select_error")
                 return False # Dừng lại vì Birthday quan trọng

            # --- Country (Kiểm tra sự tồn tại và chọn bằng Select + Trigger Events + Click Out) ---
            try:
                country_select_el = WebDriverWait(self.driver, 3).until(
                    EC.element_to_be_clickable((By.NAME, "country"))
                )
                target_country_texts = ["United States"] # Thử các cách viết
                country_selected = False
                selected_country_text = "N/A"
                for country_text_attempt in target_country_texts:
                    try:
                        logger.info(f"   [CLICK] Trying to select Country: '{country_text_attempt}'")
                        Select(country_select_el).select_by_visible_text(country_text_attempt)
                        self.driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", country_select_el)
                        self.driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", country_select_el)
                        self.driver.execute_script("arguments[0].dispatchEvent(new Event('blur', { bubbles: true }));", country_select_el)
                        selected_country_text = country_text_attempt
                        logger.info(f"   [OK] Country selected & events triggered: {selected_country_text}")
                        country_selected = True
                        time.sleep(0.2)
                        try:
                           self.driver.find_element(By.XPATH, "//label[contains(text(), 'Email')]").click()
                           logger.info("      Clicked outside Country select (on Email label).")
                        except:
                           self.driver.find_element(By.TAG_NAME, "body").click()
                           logger.info("      Clicked outside Country select (on body).")
                        time.sleep(random.uniform(0.5, 0.8))
                        break
                    except NoSuchElementException:
                        logger.debug(f"      ...Text '{country_text_attempt}' not found, trying next.")
                        continue

                if not country_selected:
                    logger.error(f"   [FAIL] Could not find any of the target countries {target_country_texts} in <select name='country'> options.")
                    self.take_screenshot("country_text_error")

            except TimeoutException:
                 logger.info("   [INFO] Country <select> field not detected on this form.")
            except Exception as e:
                 logger.warning(f"   [WARN] Error selecting/triggering/clicking out Country: {e}")

            logger.info("[OK] Finished filling form fields.")
            return True
        except Exception as e:
            logger.exception(f"   [FAIL] Unexpected error during fill_basic_fields: {e}")
            self.take_screenshot("basic_fields_unexpected_error")
            return False

    # --- HÀM GENERATE USER DATA (SỬA LẠI FORMAT THÁNG - DÙNG TÊN ĐẦY ĐỦ) ---
    def generate_user_data(self):
        """Tạo dữ liệu user, dùng tên tháng đầy đủ (January, February...)."""
        username_part = ''.join(random.choices(string.ascii_lowercase + string.digits, k=random.randint(8, 11)))
        domain = random.choice(["gmail.com", "yahoo.com", "outlook.com", "hotmail.com"])
        email = f"{username_part}.{random.randint(100,9999)}@{domain}"
        username = f"{username_part}{random.randint(10,99)}"

        today = datetime.now()
        min_age_days = 18 * 365.25
        max_age_days = 65 * 365.25
        random_days_ago = random.uniform(min_age_days, max_age_days)
        birth_date = today - timedelta(days=random_days_ago)
        gender_value = random.choice(["male", "female"])
        country_text = "Vietnam" # Hàm fill sẽ thử "Viet Nam"

        user_data = {
            'email': email,
            'username': username,
            'gender_value': gender_value,
            # *** SỬA LẠI FORMAT THÁNG: DÙNG %B ĐỂ LẤY TÊN ĐẦY ĐỦ ***
            'birth_month_text': birth_date.strftime('%B'), # Ví dụ: 'January', 'February', ...
            'birth_day': str(birth_date.day),         # Giữ nguyên số (dạng chuỗi)
            'birth_year': str(birth_date.year),       # Giữ nguyên số (dạng chuỗi)
            'country_text': country_text
        }
        # Cập nhật log để hiển thị tên tháng
        logger.info(f"[FORM] Generated user: {user_data['email']}, User: {user_data['username']}, Gender: {user_data['gender_value']}, Birthday: {user_data['birth_month_text']} {user_data['birth_day']}, {user_data['birth_year']}, Country Target: {user_data['country_text']}")
        return user_data

    # --- CHECK TERMS AND SUBMIT (Giữ nguyên) ---
    def check_terms_and_submit(self):
        """Tích terms và submit, dùng XPath checkbox linh hoạt hơn."""
        # (Giữ nguyên hàm này từ v3.2)
        if not self.driver: return False
        try:
            logger.info("\n[OK] Checking terms and submitting...")
            wait = WebDriverWait(self.driver, 12)
            checkbox = None
            checkbox_xpaths = [
                "//label[contains(., 'By creating an account with Rumble')]/input[@type='checkbox']",
                "//input[@type='checkbox'][contains(@id, 'terms') or contains(@name, 'terms')]",
                "//a[contains(@href, 'terms')]/ancestor::label/input[@type='checkbox']",
                "//a[contains(@href, 'terms')]/preceding-sibling::input[@type='checkbox']",
                "//a[contains(@href, 'terms')]/following-sibling::input[@type='checkbox']",
                "(//form//input[@type='checkbox'])[1]",
                "//button[contains(normalize-space(), 'Next')]/preceding::input[@type='checkbox'][1]"
            ]
            checkbox_found = False
            found_xpath = None
            for i, xpath in enumerate(checkbox_xpaths):
                try:
                    logger.info(f"   [CLICK] Trying checkbox XPath #{i+1}: {xpath}")
                    checkbox_present = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});", checkbox_present)
                    time.sleep(0.5)
                    checkbox = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
                    logger.info(f"   [OK] Found clickable checkbox with XPath #{i+1}")
                    checkbox_found = True
                    found_xpath = xpath
                    break
                except (TimeoutException, NoSuchElementException, ElementNotInteractableException) as e:
                    logger.debug(f"      ...Checkbox not found or not clickable with XPath #{i+1}: {e}")
                    continue

            if not checkbox_found:
                 logger.error("   [FAIL] Could not find the Terms checkbox using any XPath!")
                 self.take_screenshot("terms_checkbox_not_found")
                 return False

            if not checkbox.is_selected():
                logger.info("   [CLICK] Clicking terms checkbox...")
                try:
                    self.driver.execute_script("arguments[0].click();", checkbox)
                except Exception as e_cb_js:
                    logger.warning(f"   [WARN] JS click failed for checkbox ({e_cb_js}), trying regular click...")
                    checkbox.click()
                time.sleep(random.uniform(0.7, 1.2))
                try:
                    WebDriverWait(self.driver, 3).until(EC.element_located_to_be_selected((By.XPATH, found_xpath)))
                    logger.info("   [OK] Terms checked successfully.")
                except TimeoutException:
                     logger.error("   [FAIL] Failed to verify terms checkbox is selected after clicking!")
                     self.take_screenshot("terms_check_failed")
                     return False
            else:
                logger.info("   [OK] Terms already checked.")

            next_button_xpath = "//button[contains(normalize-space(), 'Next') and not(@disabled)]"
            try:
                button = wait.until(EC.visibility_of_element_located((By.XPATH, next_button_xpath)))
                button = wait.until(EC.element_to_be_clickable((By.XPATH, next_button_xpath)))
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});", button)
                time.sleep(0.6)
                logger.info("   [CLICK] Clicking Next button...")
                try:
                    self.driver.execute_script("arguments[0].click();", button)
                except Exception as e_btn_js:
                    logger.warning(f"   [WARN] JS click failed for Next button ({e_btn_js}), trying regular click...")
                    button.click()
                logger.info("   [OK] Next button clicked")
                return True
            except (TimeoutException, NoSuchElementException):
                 logger.error("   [FAIL] Could not find or click the enabled 'Next' button!")
                 self.take_screenshot("next_button_not_found")
                 return False

        except Exception as e:
            logger.exception(f"   [FAIL] Unexpected error during check_terms_and_submit: {e}")
            self.take_screenshot("submit_unexpected_error")
            return False

    def take_screenshot(self, name):
        """Chụp ảnh màn hình"""
        # (Giữ nguyên hàm này)
        if not self.driver: return None
        try:
            filename = f"logs/screenshot_{name}_{int(time.time())}.png"
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            if self.driver.save_screenshot(filename):
                 logger.info(f"   [SCREENSHOT] Screenshot saved: {filename}")
                 return filename
            else:
                 logger.error("   [FAIL] Screenshot failed (save_screenshot returned False).")
                 return None
        except Exception as e:
            logger.error(f"   [FAIL] Screenshot exception: {e}")
            return None
    
    def close(self):
        """Close browser"""
        try:
            if self.driver:
                logger.info("Closing browser...")
                self.driver.quit()
                logger.info("Browser closed")
        except Exception as e:
            logger.error(f"Error closing browser: {e}")

    # --- HÀM CHÍNH ĐỂ CHẠY ĐĂNG KÝ (Luôn kiểm tra Checkbox) ---
    # --- HÀM CHÍNH ĐỂ CHẠY ĐĂNG KÝ (BỎ QUA CHECKBOX CHO FORM NGẮN) ---
    def run_ultimate_registration(self):
        """Chạy đăng ký, xử lý form ngắn/dài, bỏ qua checkbox nếu là form ngắn."""
        if not self.driver:
             logger.error("[FAIL] Cannot run registration: Driver is not initialized.")
             return False
        print("\n" + "="*60)
        print(f"[TARGET] RUMBLE STANDARD REGISTRATION - Attempt @ {datetime.now().strftime('%H:%M:%S')}")
        print("="*60)

        user_data = self.generate_user_data()

        try:
            # self.debug_page_interactive() # Bỏ comment nếu cần debug XPath
            self.take_screenshot("initial_page")

            # --- Check CAPTCHA BEFORE filling form ---
            logger.info("[CAPTCHA] Checking for CAPTCHA before form submission...")
            initial_captcha_check = self.detect_and_solve_turnstile(timeout=60)
            if initial_captcha_check:
                logger.info("[CAPTCHA] Initial check passed")
            time.sleep(2)
            # -----------------

            # --- Điền form ---
            if not self.fill_basic_fields(user_data):
                logger.error("[FAIL] Failed at filling critical form fields. Aborting.")
                return False
            # -----------------

            # --- KIỂM TRA LẠI ĐỂ XÁC ĐỊNH FORM DÀI HAY NGẮN ---
            is_long_form = False
            try:
                # Check if username/gender/country fields EXIST (regardless of visibility)
                # Chỉ cần tìm thấy MỘT trong các trường này là đủ kết luận form dài
                username_exists = len(self.driver.find_elements(By.NAME, "username")) > 0
                gender_exists = len(self.driver.find_elements(By.NAME, "gender")) > 0
                country_exists = len(self.driver.find_elements(By.NAME, "country")) > 0
                
                if username_exists or gender_exists or country_exists:
                    is_long_form = True
                    logger.info("   [INFO] Detected LONG registration form (Username/Gender/Country found).")
                else:
                    logger.info("   [INFO] Detected SHORT registration form (Username/Gender/Country NOT found).")
            except Exception as e:
                logger.warning(f"   [WARN] Error detecting form type: {e}")
                logger.info("   [INFO] Defaulting to SHORT registration form.")
            # -----------------------------------------------

            self.take_screenshot("before_submit")

            # --- LOGIC SUBMIT TÙY THEO LOẠI FORM ---
            submit_successful = False
            if is_long_form:
                # Nếu là form dài, BẮT BUỘC phải check terms rồi mới submit
                logger.info("   ⏩ Proceeding with Terms check and Submit (Long Form)...")
                submit_successful = self.check_terms_and_submit() # Hàm này tìm checkbox, tick, rồi click Next
            else:
                # Nếu là form ngắn, thử click Next ngay, BỎ QUA checkbox
                logger.info("   ⏩ Skipping Terms check, proceeding directly to Submit (Short Form)...")
                try:
                    wait = WebDriverWait(self.driver, 10) # Wait cho nút Next
                    next_button_xpath = "//button[contains(normalize-space(), 'Next') and not(@disabled)]"
                    # Đảm bảo nút Next hiển thị và click được
                    button = wait.until(EC.visibility_of_element_located((By.XPATH, next_button_xpath)))
                    button = wait.until(EC.element_to_be_clickable((By.XPATH, next_button_xpath)))
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});", button)
                    time.sleep(0.6)
                    logger.info("   [CLICK] Clicking Next button (Short Form)...")
                    try:
                        self.driver.execute_script("arguments[0].click();", button)
                    except Exception as e_btn_js:
                        logger.warning(f"   [WARN] JS click failed for Next button ({e_btn_js}), trying regular click...")
                        button.click()
                    logger.info("   [OK] Next button clicked (Short Form)")
                    submit_successful = True
                except (TimeoutException, NoSuchElementException):
                     logger.error("   [FAIL] Could not find or click the enabled 'Next' button (Short Form)!")
                     self.take_screenshot("next_button_not_found_short_form")
                     submit_successful = False
                except Exception as e:
                     logger.exception(f"   [FAIL] Unexpected error clicking Next button (Short Form): {e}")
                     self.take_screenshot("submit_unexpected_error_short_form")
                     submit_successful = False
            # ---------------------------------------

            # --- KIỂM TRA VÀ GIẢI CAPTCHA SAU KHI SUBMIT ---
            if submit_successful:
                logger.info("\n[SUCCESS] FORM SUBMITTED! Checking for CAPTCHA...")
                time.sleep(3)  # Wait for CAPTCHA to load
                
                # Try to detect and solve Turnstile CAPTCHA
                captcha_result = self.detect_and_solve_turnstile(timeout=120)
                if captcha_result:
                    logger.info("[CAPTCHA] Solved or not needed, continuing...")
                else:
                    logger.warning("[CAPTCHA] Could not solve, but continuing anyway...")
                
                logger.info("\nWaiting up to 20 seconds for the next step...")
                wait_after_submit = WebDriverWait(self.driver, 20)
                try:
                    # Logic chờ và kiểm tra kết quả giữ nguyên như trước
                    next_step_element = wait_after_submit.until(
                        EC.any_of(
                            EC.presence_of_element_located((By.NAME, "password")),
                            EC.visibility_of_element_located((By.XPATH, "//*[contains(text(),'verify your email') or contains(text(), 'check your email') or contains(text(), 'Resend verification')]")),
                            EC.presence_of_element_located((By.XPATH, "//iframe[contains(@title,'captcha') or contains(@src,'challenge')]")),
                            EC.visibility_of_element_located((By.ID, "cf-challenge-running")),
                            EC.visibility_of_element_located((By.XPATH, "//*[contains(text(),'verify you are human') or contains(text(),'Security check')]")),
                            EC.visibility_of_element_located((By.XPATH, "//*[contains(@class, 'error') or contains(@class, 'alert')][contains(.,'already exists') or contains(.,'taken') or contains(.,'invalid')]"))
                        )
                    )
                    # (Phần còn lại của logic kiểm tra kết quả giữ nguyên)
                    logger.info("[OK] Detected a potential next step or known error.")
                    self.take_screenshot("after_submit_detected")
                    page_source_after_wait = self.driver.page_source.lower()
                    current_url_after_wait = self.driver.current_url
                    captcha_keywords = ['captcha', 'verify you are human', 'challenge-platform', 'are you a robot', 'security check', 'cf-challenge']
                    success_keywords = ['password', 'verification', 'verify your email', 'check your email', 'account created', 'resend verification']
                    error_keywords = ['already exists', 'email has already been taken', 'invalid data']

                    if any(keyword in page_source_after_wait for keyword in captcha_keywords) or "challenge" in current_url_after_wait:
                         logger.warning("✋ CAPTCHA/Human verification challenge detected. Manual intervention needed.")
                         print("\n✋ CAPTCHA / Human Verification challenge detected. Please solve it manually in the browser.")
                         input("   Press ENTER after solving the challenge to close the browser...")
                         return True
                    elif any(keyword in page_source_after_wait for keyword in success_keywords):
                        logger.info(f"[OK] SUCCESS! Likely moved to next step (Password/Verification). URL: {current_url_after_wait}")
                        return True
                    elif any(keyword in page_source_after_wait for keyword in error_keywords):
                        logger.warning(f"✋ Registration submitted, but encountered a known error (e.g., email exists). URL: {current_url_after_wait}")
                        # (Code log error message giữ nguyên)
                        try:
                            error_elements = self.driver.find_elements(By.XPATH, "//*[contains(@class, 'error') or contains(@class, 'alert') or contains(@role, 'alert')]")
                            for err_el in error_elements:
                                if err_el.is_displayed() and err_el.text:
                                    logger.warning(f"   Error message found on page: {err_el.text.strip()}")
                        except: pass
                        return True
                    else: # Không rõ
                        logger.warning(f"[WARN] Detected an element but unsure of the exact next step. URL: {current_url_after_wait}")
                        print("\n--- Page Source Snippet (after submit, detected element) ---")
                        print(page_source_after_wait[:2000])
                        print("---------------------------------------------------------------")
                        return True

                except TimeoutException: # Timeout sau khi submit
                    current_url_timeout = self.driver.current_url
                    logger.error(f"[FAIL] TIMEOUT after submit! Waited 20s, but no expected element appeared.")
                    logger.error(f"   Current URL after timeout: {current_url_timeout}")
                    self.take_screenshot("after_submit_timeout")
                    if "/register" in current_url_timeout or "/signup" in current_url_timeout:
                         logger.warning("   [WARN] Still on registration page after timeout. Likely a hidden validation error or undetected CAPTCHA.")
                         # Kiểm tra lại CAPTCHA một lần nữa bằng cách khác
                         try:
                              captcha_iframe_check = WebDriverWait(self.driver, 2).until(
                                   EC.presence_of_element_located((By.XPATH, "//iframe[contains(@title,'captcha') or contains(@src,'challenge')] | //div[@id='cf-challenge-running']")) # Thêm check div Cloudflare
                              )
                              if captcha_iframe_check:
                                   logger.warning("✋ CAPTCHA iframe/challenge found after timeout. Manual intervention needed.")
                                   print("\n✋ CAPTCHA / Human Verification challenge detected (after timeout). Please solve it manually.")
                                   input("   Press ENTER after solving the challenge to close the browser...")
                                   return True
                         except TimeoutException:
                              logger.error("   [FAIL] Still on registration page and no obvious CAPTCHA found. Submit likely failed silently.")
                         return False # Coi là thất bại nếu còn ở trang đăng ký và không thấy CAPTCHA
                    else: # Đã chuyển sang trang khác nhưng không nhận diện được
                         logger.warning("   [WARN] Landed on an unexpected page after timeout.")
                         return True # Vẫn coi là submit thành công về mặt kỹ thuật

            else: # Nếu submit_successful là False
                logger.error("[FAIL] FAILED TO SUBMIT FORM (Checkbox or Next button issue).")
                # Screenshot đã được chụp bên trong hàm submit tương ứng
                return False
        #---------------------------------------------

        except Exception as e:
            logger.exception(f"[FAIL] An unexpected error occurred during registration process: {e}")
            self.take_screenshot("runtime_error")
            return False

# --- MAIN EXECUTION ---
def main():
    """Hàm chính"""
    # Cập nhật version trong print statement
    print(f"RUMBLE REGISTRATION TOOL - v3.5 (CAPTCHA Solver Integrated)")
    print("=" * 60)

    register = None
    try:
        # Load API keys from config
        from config import Config
        register = RumbleAutoRegister(
            local_api_key=Config.LOCAL_CAPTCHA_API_KEY,
            nextcaptcha_key=Config.NEXTCAPTCHA_CLIENT_KEY
        )

        if not register or not register.driver:
             print("\n[ERROR] Critical Error: Failed to initialize WebDriver. Exiting.")
             return

        print("\n[NAV] Navigating to registration page...")
        if not register.navigate_to_registration():
            print("\n[ERROR] Critical Error: Failed to navigate to registration page. Exiting.")
            return

        print("\n[START] Starting registration process...")
        success = register.run_ultimate_registration() # Hàm này xử lý cả 2 form

        if success:
            print("\n" + "="*60)
            print("[SUCCESS] REGISTRATION PROCESS FINISHED (Check logs/browser for actual outcome)")
            print("="*60)
        else:
            print("\n" + "="*60)
            print("[FAILED] REGISTRATION FAILED or Stopped Early - Check logs/screenshots for errors")
            print("="*60)

    except KeyboardInterrupt:
        print("\n[STOP] User interrupted. Closing browser...")
    except Exception as e:
        logger.exception(f"[ERROR] FATAL ERROR in main execution: {e}")
        if register:
            register.take_screenshot("fatal_main_error")
    finally:
        # Sửa lại logic kiểm tra trước khi close
        if register and hasattr(register, 'driver') and register.driver:
            register.close()
        elif register and hasattr(register, 'close'): # Nếu có hàm close nhưng không có driver
             logger.info("Driver might not have initialized or already closed, attempting cleanup if possible.")
        print("\n[OK] Tool finished.")

if __name__ == "__main__":
    main()