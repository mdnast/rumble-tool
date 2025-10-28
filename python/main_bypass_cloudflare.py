"""
RUMBLE CLOUDFLARE BYPASS - Manual + Auto hybrid
Vượt qua Cloudflare Turnstile với nhiều phương pháp
"""

import time
import logging
import os
import random
import string
from datetime import datetime, timedelta

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Setup logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/bypass_cloudflare.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CloudflareBypass:
    def __init__(self, manual_solve=False):
        """
        Args:
            manual_solve: Nếu True, sẽ chờ user giải captcha thủ công
        """
        self.driver = None
        self.manual_solve = manual_solve
        self.setup_driver()
    
    def setup_driver(self):
        """Setup Chrome với stealth mode"""
        try:
            logger.info("[DRIVER] Khởi tạo Chrome...")
            
            options = uc.ChromeOptions()
            
            # Anti-detection
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--no-sandbox')
            options.add_argument('--start-maximized')
            
            # User agent
            options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36')
            
            # Prefs
            prefs = {
                "credentials_enable_service": False,
                "profile.password_manager_enabled": False,
            }
            options.add_experimental_option("prefs", prefs)
            
            # Init driver
            self.driver = uc.Chrome(options=options, use_subprocess=True)
            self.driver.implicitly_wait(10)
            
            logger.info("[DRIVER] Chrome khởi tạo thành công")
            time.sleep(2)
            
        except Exception as e:
            logger.error(f"[DRIVER] Lỗi: {e}")
    
    def take_screenshot(self, name):
        """Chụp màn hình"""
        try:
            filename = f"logs/screenshot_{name}_{int(time.time())}.png"
            self.driver.save_screenshot(filename)
            logger.info(f"[SCREENSHOT] {filename}")
            return filename
        except Exception as e:
            logger.error(f"[SCREENSHOT] Lỗi: {e}")
            return None
    
    def human_delay(self, min_sec=0.5, max_sec=2.0):
        """Delay giống người"""
        time.sleep(random.uniform(min_sec, max_sec))
    
    def human_type(self, element, text):
        """Gõ chữ giống người"""
        element.clear()
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))
        self.human_delay(0.3, 0.6)
    
    def detect_turnstile(self):
        """Kiểm tra có Turnstile không"""
        try:
            # Kiểm tra iframe
            iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
            for iframe in iframes:
                src = iframe.get_attribute("src") or ""
                if "challenges.cloudflare.com" in src or "turnstile" in src.lower():
                    logger.info(f"[TURNSTILE] Phát hiện Cloudflare Turnstile!")
                    return True
            
            # Kiểm tra widget
            widgets = self.driver.find_elements(By.XPATH, "//*[contains(@class, 'cf-turnstile')]")
            if widgets:
                logger.info("[TURNSTILE] Phát hiện Turnstile widget!")
                return True
            
            return False
        except:
            return False
    
    def wait_for_turnstile_solve(self, timeout=60):
        """Chờ Turnstile được giải (tự động hoặc thủ công)"""
        logger.info(f"[TURNSTILE] Đang chờ giải quyết (timeout: {timeout}s)...")
        
        if self.manual_solve:
            logger.info("[MANUAL] *** VUI LÒNG GIẢI CAPTCHA THỦ CÔNG! ***")
            logger.info("[MANUAL] Bấm vào checkbox Turnstile trong trình duyệt")
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # Kiểm tra xem Turnstile còn không
                has_turnstile = self.detect_turnstile()
                
                if not has_turnstile:
                    logger.info("[TURNSTILE] Đã vượt qua!")
                    return True
                
                # Kiểm tra có token không
                token_check = self.driver.execute_script("""
                    var textarea = document.querySelector('textarea[name="cf-turnstile-response"]');
                    if (textarea && textarea.value && textarea.value.length > 0) {
                        return textarea.value;
                    }
                    return null;
                """)
                
                if token_check:
                    logger.info(f"[TURNSTILE] Token tìm thấy: {token_check[:50]}...")
                    return True
                
                # Thử tự động click nếu có checkbox visible
                try:
                    iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
                    for iframe in iframes:
                        src = iframe.get_attribute("src") or ""
                        if "turnstile" in src.lower() or "challenges.cloudflare.com" in src:
                            # Switch to iframe
                            self.driver.switch_to.frame(iframe)
                            
                            # Tìm checkbox
                            checkboxes = self.driver.find_elements(By.XPATH, "//input[@type='checkbox']")
                            if checkboxes:
                                checkbox = checkboxes[0]
                                if checkbox.is_displayed() and checkbox.is_enabled():
                                    logger.info("[TURNSTILE] Tìm thấy checkbox, đang click...")
                                    checkbox.click()
                                    self.human_delay(1, 2)
                            
                            # Switch back
                            self.driver.switch_to.default_content()
                            break
                except Exception as click_error:
                    logger.debug(f"[TURNSTILE] Không thể click: {click_error}")
                    self.driver.switch_to.default_content()
                
                time.sleep(2)
                
            except Exception as e:
                logger.debug(f"[TURNSTILE] Lỗi khi kiểm tra: {e}")
                time.sleep(2)
        
        logger.error("[TURNSTILE] Timeout!")
        return False
    
    def fill_form(self):
        """Điền form đăng ký"""
        try:
            logger.info("[FORM] Đang điền form...")
            
            # Generate data
            random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=11))
            email = f"{random_str}@gmail.com"
            username = f"{random_str[:8]}{random.randint(100, 999)}"
            
            years_ago = random.randint(18, 30)
            birth_date = datetime.now() - timedelta(days=years_ago * 365 + random.randint(0, 365))
            months = ["January", "February", "March", "April", "May", "June", 
                      "July", "August", "September", "October", "November", "December"]
            
            # Email
            email_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "email"))
            )
            self.human_type(email_field, email)
            logger.info(f"[FORM] Email: {email}")
            self.human_delay(0.3, 0.6)
            
            # Username (nếu có)
            try:
                username_field = self.driver.find_element(By.NAME, "username")
                self.human_type(username_field, username)
                logger.info(f"[FORM] Username: {username}")
                self.human_delay(0.3, 0.6)
            except:
                pass
            
            # Gender (nếu có)
            try:
                gender_element = self.driver.find_element(By.NAME, "gender")
                gender_select = Select(gender_element)
                gender_select.select_by_value(random.choice(['male', 'female']))
                logger.info("[FORM] Gender: đã chọn")
                self.human_delay(0.3, 0.6)
            except:
                pass
            
            # Birthday
            month_element = self.driver.find_element(By.NAME, "birthday_month")
            month_select = Select(month_element)
            month_select.select_by_visible_text(months[birth_date.month - 1])
            self.human_delay(0.5, 0.8)
            
            day_element = self.driver.find_element(By.NAME, "birthday_day")
            day_select = Select(day_element)
            day_select.select_by_value(str(birth_date.day))
            self.human_delay(0.5, 0.8)
            
            year_element = self.driver.find_element(By.NAME, "birthday_year")
            year_select = Select(year_element)
            year_select.select_by_value(str(birth_date.year))
            logger.info(f"[FORM] Birthday: {birth_date.strftime('%B %d, %Y')}")
            self.human_delay(0.5, 0.8)
            
            # Country (nếu có)
            try:
                country_element = self.driver.find_element(By.NAME, "country")
                country_select = Select(country_element)
                country_select.select_by_value("US")
                logger.info("[FORM] Country: United States")
                self.human_delay(0.3, 0.6)
            except:
                pass
            
            logger.info("[FORM] Đã điền xong!")
            return True
            
        except Exception as e:
            logger.error(f"[FORM] Lỗi: {e}")
            return False
    
    def submit_form(self):
        """Submit form"""
        try:
            logger.info("[SUBMIT] Đang submit...")
            
            # Check terms checkbox
            try:
                checkbox = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//input[@type='checkbox']"))
                )
                if not checkbox.is_selected():
                    checkbox.click()
                    logger.info("[SUBMIT] Đã check terms")
                    self.human_delay(0.5, 1.0)
            except:
                pass
            
            # Find Next button
            button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Next')]"))
            )
            
            self.human_delay(1, 2)
            button.click()
            logger.info("[SUBMIT] Đã click Next")
            
            return True
            
        except Exception as e:
            logger.error(f"[SUBMIT] Lỗi: {e}")
            return False
    
    def check_success(self):
        """Kiểm tra đăng ký thành công"""
        try:
            time.sleep(3)
            
            current_url = self.driver.current_url
            page_source = self.driver.page_source.lower()
            
            # Success indicators
            if "password" in page_source or "verify" in current_url or "success" in page_source:
                logger.info("[SUCCESS] Đăng ký thành công!")
                return True
            
            # Error indicators
            if "not available" in page_source or "error" in page_source:
                logger.error("[FAIL] Đăng ký thất bại")
                return False
            
            return None  # Unknown
            
        except Exception as e:
            logger.error(f"[CHECK] Lỗi: {e}")
            return None
    
    def run(self):
        """Chạy quy trình đăng ký"""
        try:
            logger.info("="*60)
            logger.info("RUMBLE CLOUDFLARE BYPASS")
            logger.info("="*60)
            
            # Step 1: Navigate
            logger.info("[1] Đang mở trang đăng ký...")
            self.driver.get("https://rumble.com/register/")
            time.sleep(3)
            self.take_screenshot("01_page_loaded")
            
            # Step 2: Fill form
            logger.info("[2] Đang điền form...")
            if not self.fill_form():
                logger.error("Điền form thất bại!")
                return False
            
            self.take_screenshot("02_form_filled")
            time.sleep(1)
            
            # Step 3: Submit
            logger.info("[3] Đang submit...")
            if not self.submit_form():
                logger.error("Submit thất bại!")
                return False
            
            time.sleep(2)
            self.take_screenshot("03_after_submit")
            
            # Step 4: Handle Turnstile
            logger.info("[4] Kiểm tra Cloudflare Turnstile...")
            if self.detect_turnstile():
                logger.info("[TURNSTILE] Phát hiện Cloudflare!")
                self.take_screenshot("04_turnstile_detected")
                
                # Wait for solve
                if self.manual_solve:
                    solved = self.wait_for_turnstile_solve(timeout=120)
                else:
                    solved = self.wait_for_turnstile_solve(timeout=60)
                
                if solved:
                    logger.info("[TURNSTILE] Đã vượt qua!")
                    self.take_screenshot("05_turnstile_solved")
                else:
                    logger.error("[TURNSTILE] Không vượt qua được!")
                    self.take_screenshot("05_turnstile_failed")
                    return False
            else:
                logger.info("[4] Không có Turnstile")
            
            # Step 5: Check result
            time.sleep(3)
            self.take_screenshot("06_final_result")
            
            result = self.check_success()
            if result == True:
                logger.info("="*60)
                logger.info("[SUCCESS] ĐĂNG KÝ THÀNH CÔNG!")
                logger.info("="*60)
                return True
            elif result == False:
                logger.error("="*60)
                logger.error("[FAILED] ĐĂNG KÝ THẤT BẠI!")
                logger.error("="*60)
                return False
            else:
                logger.warning("[UNKNOWN] Không xác định được kết quả")
                logger.info(f"URL hiện tại: {self.driver.current_url}")
                return None
            
        except Exception as e:
            logger.exception(f"[ERROR] Lỗi: {e}")
            self.take_screenshot("error")
            return False
        finally:
            # Keep browser open
            logger.info("\n[INFO] Browser sẽ mở trong 30 giây để bạn kiểm tra...")
            time.sleep(30)
    
    def close(self):
        """Đóng browser"""
        try:
            if self.driver:
                logger.info("[CLOSE] Đang đóng browser...")
                self.driver.quit()
        except Exception as e:
            logger.error(f"[CLOSE] Lỗi: {e}")

def main():
    print("="*60)
    print("RUMBLE CLOUDFLARE BYPASS")
    print("="*60)
    print()
    print("Select mode:")
    print("1. Auto (try auto-click Turnstile)")
    print("2. Manual (you click Turnstile manually)")
    print()
    
    choice = input("Choose (1 or 2): ").strip()
    
    manual_solve = (choice == "2")
    
    if manual_solve:
        print("\n[MANUAL MODE] Bạn sẽ cần click vào Turnstile checkbox khi nó xuất hiện!")
        print("Browser sẽ không tự động đóng để bạn có thời gian giải captcha.\n")
    else:
        print("\n[AUTO MODE] Bot sẽ thử click Turnstile tự động.\n")
    
    time.sleep(2)
    
    bypass = None
    try:
        bypass = CloudflareBypass(manual_solve=manual_solve)
        result = bypass.run()
        
        if result == True:
            print("\n✅ THÀNH CÔNG!")
        elif result == False:
            print("\n❌ THẤT BẠI!")
        else:
            print("\n⚠️ KHÔNG RÕ KẾT QUẢ - Kiểm tra browser!")
        
    except KeyboardInterrupt:
        print("\n[STOP] Dừng bởi người dùng")
    except Exception as e:
        logger.exception(f"[FATAL] Lỗi: {e}")
    finally:
        if bypass:
            bypass.close()

if __name__ == "__main__":
    main()
