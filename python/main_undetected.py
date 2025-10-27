# main_undetected.py - Version sử dụng undetected-chromedriver
# Đơn giản hóa: Chỉ tập trung vào bypass bot detection

import time
import logging
import os
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import random
import string
from datetime import datetime, timedelta

# Import CAPTCHA solver
try:
    from captcha_solver import CaptchaSolver
    from config import Config
    HAS_CAPTCHA_SOLVER = True
except:
    HAS_CAPTCHA_SOLVER = False

# Setup logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/rumble_undetected.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class RumbleUndetectedRegister:
    def __init__(self):
        self.driver = None
        self.captcha_solver = None
        
        # Initialize CAPTCHA solver if available
        if HAS_CAPTCHA_SOLVER:
            try:
                self.captcha_solver = CaptchaSolver(
                    local_api_key=Config.LOCAL_CAPTCHA_API_KEY,
                    nextcaptcha_client_key=Config.NEXTCAPTCHA_CLIENT_KEY
                )
                logger.info("[CAPTCHA] Solver initialized")
            except Exception as e:
                logger.warning(f"[CAPTCHA] Could not initialize solver: {e}")
        
        self.setup_driver()
    
    def setup_driver(self):
        """Setup undetected Chrome driver"""
        try:
            logger.info("[DRIVER] Initializing undetected Chrome...")
            
            options = uc.ChromeOptions()
            # Basic options only
            options.add_argument('--disable-blink-features=AutomationControlled')
            
            # Initialize undetected Chrome
            self.driver = uc.Chrome(options=options, use_subprocess=True, version_main=None)
            
            # Set implicit wait
            self.driver.implicitly_wait(10)
            
            logger.info("[DRIVER] Undetected Chrome initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"[DRIVER] Failed to initialize: {e}")
            return False
    
    def generate_user_data(self):
        """Generate random user data"""
        random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=11))
        
        # Random birthday (18-30 years old)
        years_ago = random.randint(18, 30)
        birth_date = datetime.now() - timedelta(days=years_ago * 365 + random.randint(0, 365))
        
        months = ["January", "February", "March", "April", "May", "June", 
                  "July", "August", "September", "October", "November", "December"]
        
        return {
            'email': f"{random_str}.{random.randint(1000, 9999)}@outlook.com",
            'username': f"{random_str}{random.randint(10, 99)}",
            'gender_value': random.choice(['male', 'female']),
            'birth_month_text': months[birth_date.month - 1],
            'birth_day': str(birth_date.day),
            'birth_year': str(birth_date.year)
        }
    
    def navigate_to_registration(self):
        """Navigate to registration page"""
        try:
            url = "https://rumble.com/register/"
            logger.info(f"[NAV] Navigating to: {url}")
            
            self.driver.get(url)
            
            # Wait for email field
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.NAME, "email"))
            )
            
            logger.info("[NAV] Page loaded successfully")
            time.sleep(3)  # Extra wait for any dynamic content
            return True
            
        except Exception as e:
            logger.error(f"[NAV] Failed: {e}")
            return False
    
    def detect_and_solve_captcha(self, timeout=120):
        """Detect and solve Cloudflare Turnstile"""
        if not self.captcha_solver:
            logger.info("[CAPTCHA] No solver configured")
            return True
        
        try:
            # Check for Turnstile
            iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
            for iframe in iframes:
                src = iframe.get_attribute("src") or ""
                if "challenges.cloudflare.com" in src or "turnstile" in src.lower():
                    logger.info("[CAPTCHA] Cloudflare Turnstile detected!")
                    
                    # Extract sitekey
                    import re
                    page_source = self.driver.page_source
                    
                    sitekey = None
                    match = re.search(r'data-sitekey="([^"]+)"', page_source)
                    if match:
                        sitekey = match.group(1)
                    
                    if not sitekey:
                        match = re.search(r'sitekey=([^&]+)', src)
                        if match:
                            sitekey = match.group(1)
                    
                    if sitekey:
                        logger.info(f"[CAPTCHA] Sitekey: {sitekey}")
                        logger.info("[CAPTCHA] Solving...")
                        
                        token = self.captcha_solver.solve_turnstile(
                            self.driver.current_url, 
                            sitekey, 
                            timeout
                        )
                        
                        if token:
                            logger.info("[CAPTCHA] Token received, injecting...")
                            
                            # Inject token
                            script = f"""
                            var forms = document.querySelectorAll('form');
                            for (var i = 0; i < forms.length; i++) {{
                                var input = document.createElement('input');
                                input.type = 'hidden';
                                input.name = 'cf-turnstile-response';
                                input.value = '{token}';
                                forms[i].appendChild(input);
                            }}
                            
                            var textarea = document.querySelector('textarea[name="cf-turnstile-response"]');
                            if (textarea) textarea.value = '{token}';
                            """
                            
                            self.driver.execute_script(script)
                            logger.info("[CAPTCHA] Token injected")
                            time.sleep(2)
                            return True
                        else:
                            logger.error("[CAPTCHA] Failed to solve")
                            return False
                    else:
                        logger.error("[CAPTCHA] Could not find sitekey")
                        return False
            
            logger.info("[CAPTCHA] No CAPTCHA detected")
            return True
            
        except Exception as e:
            logger.error(f"[CAPTCHA] Error: {e}")
            return False
    
    def fill_form(self, user_data):
        """Fill registration form"""
        try:
            logger.info("[FORM] Filling form...")
            wait = WebDriverWait(self.driver, 10)
            
            # Email
            email_field = wait.until(EC.presence_of_element_located((By.NAME, "email")))
            email_field.clear()
            for char in user_data['email']:
                email_field.send_keys(char)
                time.sleep(random.uniform(0.05, 0.12))
            logger.info(f"[FORM] Email: {user_data['email']}")
            time.sleep(0.5)
            
            # Check for username, gender, country (long form)
            has_username = len(self.driver.find_elements(By.NAME, "username")) > 0
            has_gender = len(self.driver.find_elements(By.NAME, "gender")) > 0
            has_country = len(self.driver.find_elements(By.NAME, "country")) > 0
            
            if has_username:
                username_field = self.driver.find_element(By.NAME, "username")
                username_field.clear()
                for char in user_data['username']:
                    username_field.send_keys(char)
                    time.sleep(random.uniform(0.05, 0.12))
                logger.info(f"[FORM] Username: {user_data['username']}")
                time.sleep(0.5)
            
            if has_gender:
                gender_select = Select(self.driver.find_element(By.NAME, "gender"))
                gender_select.select_by_value(user_data['gender_value'])
                logger.info(f"[FORM] Gender: {user_data['gender_value']}")
                time.sleep(0.5)
            
            # Birthday (always present)
            month_select = Select(wait.until(EC.presence_of_element_located((By.NAME, "birthday_month"))))
            month_select.select_by_visible_text(user_data['birth_month_text'])
            logger.info(f"[FORM] Month: {user_data['birth_month_text']}")
            time.sleep(0.3)
            
            day_select = Select(self.driver.find_element(By.NAME, "birthday_day"))
            day_select.select_by_value(user_data['birth_day'])
            logger.info(f"[FORM] Day: {user_data['birth_day']}")
            time.sleep(0.3)
            
            year_select = Select(self.driver.find_element(By.NAME, "birthday_year"))
            year_select.select_by_value(user_data['birth_year'])
            logger.info(f"[FORM] Year: {user_data['birth_year']}")
            time.sleep(0.5)
            
            if has_country:
                country_select = Select(self.driver.find_element(By.NAME, "country"))
                country_select.select_by_visible_text("United States")
                logger.info("[FORM] Country: United States")
                time.sleep(0.5)
            
            logger.info("[FORM] Form filled successfully")
            return True
            
        except Exception as e:
            logger.error(f"[FORM] Error filling form: {e}")
            return False
    
    def submit_form(self):
        """Submit the form"""
        try:
            logger.info("[SUBMIT] Looking for submit button...")
            wait = WebDriverWait(self.driver, 10)
            
            # Try to find and check terms checkbox first
            try:
                checkbox = wait.until(EC.element_to_be_clickable(
                    (By.XPATH, "//input[@type='checkbox']")
                ))
                if not checkbox.is_selected():
                    checkbox.click()
                    logger.info("[SUBMIT] Terms checkbox checked")
                    time.sleep(0.5)
            except:
                logger.info("[SUBMIT] No terms checkbox found or already checked")
            
            # Find and click Next/Submit button - try multiple XPaths
            button_xpaths = [
                "//button[contains(normalize-space(), 'Next')]",
                "//button[contains(text(), 'Next')]",
                "//button[@type='submit']",
                "//button[contains(normalize-space(), 'Submit')]",
                "//input[@type='submit']"
            ]
            
            button_found = False
            for xpath in button_xpaths:
                try:
                    logger.info(f"[SUBMIT] Trying XPath: {xpath}")
                    button = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
                    logger.info(f"[SUBMIT] Found button with XPath: {xpath}")
                    button_found = True
                    break
                except:
                    continue
            
            if not button_found:
                logger.error("[SUBMIT] Could not find submit button with any XPath")
                return False
            
            logger.info("[SUBMIT] Clicking submit button...")
            try:
                self.driver.execute_script("arguments[0].click();", button)
                logger.info("[SUBMIT] Form submitted (JS click)!")
            except:
                button.click()
                logger.info("[SUBMIT] Form submitted (regular click)!")
            
            return True
            
        except Exception as e:
            logger.error(f"[SUBMIT] Error: {e}")
            return False
    
    def wait_for_result(self, timeout=30):
        """Wait for registration result"""
        try:
            logger.info(f"[WAIT] Waiting up to {timeout}s for result...")
            wait = WebDriverWait(self.driver, timeout)
            
            # Wait for either success or error
            wait.until(
                EC.any_of(
                    # Success indicators
                    EC.presence_of_element_located((By.NAME, "password")),
                    EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'verify')]")),
                    # Error indicators
                    EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'not available')]")),
                    EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'error')]")),
                    # CAPTCHA
                    EC.presence_of_element_located((By.XPATH, "//iframe[contains(@src, 'captcha')]"))
                )
            )
            
            current_url = self.driver.current_url
            page_text = self.driver.page_source.lower()
            
            if "password" in page_text or "verify" in page_text:
                logger.info("[SUCCESS] Registration successful!")
                return True
            elif "not available" in page_text:
                logger.error("[FAIL] Registration not available (Bot detected)")
                return False
            elif "captcha" in current_url or "challenge" in current_url:
                logger.warning("[CAPTCHA] CAPTCHA challenge appeared")
                return False
            else:
                logger.warning("[UNKNOWN] Unknown state")
                return False
                
        except TimeoutException:
            logger.error(f"[TIMEOUT] No response after {timeout}s")
            logger.info(f"[INFO] Current URL: {self.driver.current_url}")
            return False
    
    def take_screenshot(self, name):
        """Take screenshot"""
        try:
            import os
            log_dir = os.path.join(os.path.dirname(__file__), "logs")
            os.makedirs(log_dir, exist_ok=True)
            filename = os.path.join(log_dir, f"screenshot_{name}_{int(time.time())}.png")
            self.driver.save_screenshot(filename)
            logger.info(f"[SCREENSHOT] Saved: {filename}")
            return filename
        except Exception as e:
            logger.error(f"[SCREENSHOT] Error: {e}")
            return None
    
    def run(self):
        """Run registration process"""
        logger.info("="*60)
        logger.info(f"[START] Registration attempt @ {datetime.now().strftime('%H:%M:%S')}")
        logger.info("="*60)
        
        try:
            # Navigate
            if not self.navigate_to_registration():
                return False
            
            self.take_screenshot("01_page_loaded")
            
            # Check CAPTCHA before filling
            logger.info("[CAPTCHA] Checking for initial CAPTCHA...")
            self.detect_and_solve_captcha(timeout=60)
            time.sleep(2)
            
            # Generate and fill form
            user_data = self.generate_user_data()
            logger.info(f"[USER] Email: {user_data['email']}")
            logger.info(f"[USER] Username: {user_data['username']}")
            
            if not self.fill_form(user_data):
                self.take_screenshot("02_fill_error")
                return False
            
            self.take_screenshot("03_form_filled")
            
            # Check CAPTCHA after filling
            logger.info("[CAPTCHA] Checking for post-fill CAPTCHA...")
            self.detect_and_solve_captcha(timeout=60)
            time.sleep(2)
            
            # Submit
            if not self.submit_form():
                self.take_screenshot("04_submit_error")
                return False
            
            time.sleep(3)
            self.take_screenshot("05_after_submit")
            
            # Check CAPTCHA after submit
            logger.info("[CAPTCHA] Checking for post-submit CAPTCHA...")
            self.detect_and_solve_captcha(timeout=120)
            
            # Wait for result
            result = self.wait_for_result(timeout=30)
            
            self.take_screenshot("06_final")
            
            return result
            
        except Exception as e:
            logger.exception(f"[ERROR] Registration failed: {e}")
            self.take_screenshot("error")
            return False
    
    def close(self):
        """Close browser"""
        try:
            if self.driver:
                logger.info("[CLOSE] Closing browser...")
                self.driver.quit()
                logger.info("[CLOSE] Browser closed")
        except Exception as e:
            logger.error(f"[CLOSE] Error: {e}")

def main():
    print("="*60)
    print("RUMBLE REGISTRATION TOOL - UNDETECTED VERSION")
    print("="*60)
    
    register = None
    try:
        register = RumbleUndetectedRegister()
        
        if not register.driver:
            print("[ERROR] Failed to initialize driver")
            return
        
        success = register.run()
        
        if success:
            print("\n" + "="*60)
            print("[SUCCESS] Registration completed")
            print("="*60)
        else:
            print("\n" + "="*60)
            print("[FAILED] Registration failed")
            print("="*60)
        
        # Keep browser open for 10 seconds for inspection
        logger.info("\nKeeping browser open for 10 seconds...")
        time.sleep(10)
        
    except KeyboardInterrupt:
        print("\n[STOP] User interrupted")
    except Exception as e:
        logger.exception(f"[FATAL] Error: {e}")
    finally:
        if register:
            register.close()

if __name__ == "__main__":
    main()
