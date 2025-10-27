# -*- coding: utf-8 -*-
"""
RUMBLE SIMPLE BYPASS - Version đơn giản với CAPTCHA solver
Chỉ thêm những gì cần thiết để vượt qua Rumble bot detection
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import logging
import random
import string
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Import NextCaptcha
from nextcaptcha.next import YesCaptchaAPI

os.makedirs('logs', exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/rumble_simple.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# NextCaptcha API key
CAPTCHA_API_KEY = "559d1b2771bedd55455c09865b97be55e04a0a9877978"

class RumbleSimpleBypass:
    def __init__(self):
        self.driver = None
        self.captcha_api = YesCaptchaAPI(client_key=CAPTCHA_API_KEY, open_log=False)
        self.setup_driver()
    
    def setup_driver(self):
        """Setup Chrome driver với stealth cơ bản"""
        try:
            from selenium.webdriver.chrome.options import Options
            
            chrome_options = Options()
            
            # Basic anti-detection
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Random User-Agent
            user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ]
            chrome_options.add_argument(f"--user-agent={random.choice(user_agents)}")
            
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--no-sandbox")
            
            service = Service()
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Hide webdriver property
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            logger.info("[OK] Driver initialized")
            return True
            
        except Exception as e:
            logger.error(f"[FAIL] Driver setup failed: {e}")
            return False
    
    def solve_turnstile_captcha(self):
        """Giải Cloudflare Turnstile CAPTCHA"""
        try:
            logger.info("[CAPTCHA] Detecting Turnstile...")
            
            current_url = self.driver.current_url
            page_source = self.driver.page_source
            
            # Tìm sitekey
            website_key = None
            
            # Method 1: Từ iframe
            try:
                iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
                for iframe in iframes:
                    src = iframe.get_attribute('src') or ''
                    if 'challenges.cloudflare.com' in src or 'turnstile' in src.lower():
                        logger.info(f"[CAPTCHA] Found Turnstile iframe: {src[:80]}...")
                        # Extract sitekey từ URL
                        import re
                        match = re.search(r'sitekey=([^&]+)', src)
                        if match:
                            website_key = match.group(1)
                            logger.info(f"[CAPTCHA] Sitekey from iframe: {website_key}")
                            break
            except Exception as e:
                logger.debug(f"Iframe search failed: {e}")
            
            # Method 2: Từ data-sitekey
            if not website_key:
                try:
                    elements = self.driver.find_elements(By.XPATH, "//*[@data-sitekey]")
                    for elem in elements:
                        key = elem.get_attribute('data-sitekey')
                        if key and len(key) > 10:
                            website_key = key
                            logger.info(f"[CAPTCHA] Sitekey from data-sitekey: {website_key}")
                            break
                except:
                    pass
            
            # Method 3: Từ page source
            if not website_key:
                import re
                patterns = [
                    r'data-sitekey=["\']([^"\']+)["\']',
                    r'sitekey["\s:]+["\']([^"\']+)["\']',
                    r'turnstile\.render\([^,]+,\s*{\s*sitekey:\s*["\']([^"\']+)["\']'
                ]
                for pattern in patterns:
                    match = re.search(pattern, page_source)
                    if match:
                        website_key = match.group(1)
                        logger.info(f"[CAPTCHA] Sitekey from page source: {website_key}")
                        break
            
            if not website_key:
                logger.error("[FAIL] Could not find Turnstile sitekey")
                logger.info("[INFO] Waiting 30 seconds for manual solve...")
                time.sleep(30)
                return False
            
            # Gọi NextCaptcha API
            logger.info(f"[SOLVING] Calling NextCaptcha API...")
            logger.info(f"[INFO] URL: {current_url[:60]}...")
            logger.info(f"[INFO] Sitekey: {website_key}")
            
            result = self.captcha_api.turnstile(
                website_url=current_url,
                website_key=website_key
            )
            
            if result and result.get("status") == "ready":
                token = result.get("solution", {}).get("token", "")
                logger.info(f"[SUCCESS] Turnstile solved! Token length: {len(token)}")
                
                # Inject token
                self.inject_turnstile_token(token)
                
                # Click submit lại
                logger.info("[SUBMIT] Clicking submit button again...")
                try:
                    submit_btn = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(normalize-space(), 'Next') or @type='submit']"))
                    )
                    submit_btn.click()
                    logger.info("[OK] Submit button clicked after CAPTCHA solve")
                    time.sleep(3)
                except:
                    logger.warning("[WARN] Could not click submit after solving CAPTCHA")
                
                return True
            else:
                error_msg = result.get('errorDescription', 'Unknown error') if result else 'No response'
                logger.error(f"[FAIL] Turnstile solving failed: {error_msg}")
                return False
                
        except Exception as e:
            logger.error(f"[ERROR] Turnstile solving error: {e}")
            return False
    
    def inject_turnstile_token(self, token):
        """Inject Turnstile token vào page"""
        try:
            logger.info("[INJECT] Injecting token...")
            
            js_script = f"""
            var token = '{token}';
            
            // Method 1: Find all hidden inputs
            var hiddenInputs = document.querySelectorAll('input[type="hidden"]');
            var injected = false;
            
            hiddenInputs.forEach(function(input) {{
                var name = input.name || '';
                if (name.includes('cf') || name.includes('turnstile') || name.includes('token')) {{
                    input.value = token;
                    console.log('Token injected into: ' + name);
                    injected = true;
                }}
            }});
            
            // Method 2: Create new input if none found
            if (!injected) {{
                var newInput = document.createElement('input');
                newInput.type = 'hidden';
                newInput.name = 'cf-turnstile-response';
                newInput.value = token;
                var forms = document.getElementsByTagName('form');
                if (forms.length > 0) {{
                    forms[0].appendChild(newInput);
                    console.log('New hidden input created with token');
                    injected = true;
                }}
            }}
            
            // Method 3: Try turnstile callback
            if (window.turnstile && window.turnstile.getResponse) {{
                console.log('Turnstile API found');
            }}
            
            // Dispatch custom event
            document.dispatchEvent(new CustomEvent('cf-turnstile-response', {{ detail: token }}));
            
            return injected ? 'Token injected successfully' : 'No suitable input found';
            """
            
            result = self.driver.execute_script(js_script)
            logger.info(f"[INJECT] {result}")
            time.sleep(2)
            
        except Exception as e:
            logger.error(f"[ERROR] Token injection failed: {e}")
    
    def navigate_to_registration(self):
        """Navigate tới trang đăng ký"""
        try:
            url = "https://rumble.com/register/"
            logger.info(f"[NAV] Navigating to {url}")
            self.driver.get(url)
            
            # Đợi email field
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.NAME, "email"))
            )
            
            time.sleep(2)
            logger.info("[OK] Registration page loaded")
            return True
            
        except Exception as e:
            logger.error(f"[FAIL] Navigation failed: {e}")
            return False
    
    def generate_user_data(self):
        """Generate random user data"""
        username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        domain = random.choice(["gmail.com", "yahoo.com", "outlook.com", "hotmail.com"])
        email = f"{username}.{random.randint(1000,9999)}@{domain}"
        
        today = datetime.now()
        age_days = random.uniform(18*365, 65*365)
        birth_date = today - timedelta(days=age_days)
        
        data = {
            'email': email,
            'username': username + str(random.randint(10,99)),
            'gender': random.choice(["male", "female"]),
            'birth_month': birth_date.strftime('%B'),
            'birth_day': str(birth_date.day),
            'birth_year': str(birth_date.year),
        }
        
        logger.info(f"[USER] Email: {email}")
        return data
    
    def fill_form(self, user_data):
        """Fill registration form"""
        try:
            logger.info("[FORM] Filling form...")
            wait = WebDriverWait(self.driver, 15)
            
            # Email
            email_field = wait.until(EC.visibility_of_element_located((By.NAME, "email")))
            email_field.clear()
            for char in user_data['email']:
                email_field.send_keys(char)
                time.sleep(random.uniform(0.05, 0.12))
            logger.info("[OK] Email filled")
            time.sleep(0.5)
            
            # Username (if exists)
            try:
                username_field = WebDriverWait(self.driver, 2).until(
                    EC.visibility_of_element_located((By.NAME, "username"))
                )
                username_field.clear()
                for char in user_data['username']:
                    username_field.send_keys(char)
                    time.sleep(random.uniform(0.05, 0.12))
                logger.info("[OK] Username filled")
                time.sleep(0.5)
            except:
                logger.info("[INFO] Username field not found (short form)")
            
            # Gender (if exists)
            try:
                gender_select = WebDriverWait(self.driver, 2).until(
                    EC.element_to_be_clickable((By.NAME, "gender"))
                )
                Select(gender_select).select_by_value(user_data['gender'])
                logger.info(f"[OK] Gender: {user_data['gender']}")
                time.sleep(0.5)
            except:
                logger.info("[INFO] Gender field not found (short form)")
            
            # Birthday
            month_select = wait.until(EC.element_to_be_clickable((By.NAME, "birthday_month")))
            Select(month_select).select_by_visible_text(user_data['birth_month'])
            time.sleep(0.3)
            
            day_select = wait.until(EC.element_to_be_clickable((By.NAME, "birthday_day")))
            Select(day_select).select_by_value(user_data['birth_day'])
            time.sleep(0.3)
            
            year_select = wait.until(EC.element_to_be_clickable((By.NAME, "birthday_year")))
            Select(year_select).select_by_value(user_data['birth_year'])
            logger.info(f"[OK] Birthday: {user_data['birth_month']} {user_data['birth_day']}, {user_data['birth_year']}")
            time.sleep(0.5)
            
            # Country (if exists)
            try:
                country_select = WebDriverWait(self.driver, 2).until(
                    EC.element_to_be_clickable((By.NAME, "country"))
                )
                Select(country_select).select_by_visible_text("United States")
                logger.info("[OK] Country: United States")
                time.sleep(0.5)
            except:
                logger.info("[INFO] Country field not found (short form)")
            
            logger.info("[OK] Form filled successfully")
            return True
            
        except Exception as e:
            logger.error(f"[FAIL] Form filling failed: {e}")
            return False
    
    def submit_form(self):
        """Submit form"""
        try:
            logger.info("[SUBMIT] Submitting form...")
            wait = WebDriverWait(self.driver, 12)
            
            # Check for terms checkbox (long form)
            try:
                checkbox_xpaths = [
                    "//input[@type='checkbox'][contains(@id, 'terms') or contains(@name, 'terms')]",
                    "//label[contains(., 'By creating')]/input[@type='checkbox']",
                    "(//form//input[@type='checkbox'])[1]"
                ]
                
                checkbox_found = False
                for xpath in checkbox_xpaths:
                    try:
                        checkbox = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
                        if not checkbox.is_selected():
                            checkbox.click()
                            logger.info("[OK] Terms checkbox checked")
                            time.sleep(0.5)
                        checkbox_found = True
                        break
                    except:
                        continue
                
                if not checkbox_found:
                    logger.info("[INFO] No terms checkbox (short form)")
                    
            except Exception as e:
                logger.debug(f"Terms checkbox handling: {e}")
            
            # Click submit/next button
            submit_xpaths = [
                "//button[contains(normalize-space(), 'Next') and not(@disabled)]",
                "//button[@type='submit' and not(@disabled)]",
                "//input[@type='submit' and not(@disabled)]"
            ]
            
            for xpath in submit_xpaths:
                try:
                    btn = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
                    btn.click()
                    logger.info("[OK] Submit button clicked")
                    time.sleep(2)
                    return True
                except:
                    continue
            
            logger.error("[FAIL] Could not find submit button")
            return False
            
        except Exception as e:
            logger.error(f"[FAIL] Submit failed: {e}")
            return False
    
    def wait_for_result(self):
        """Đợi và kiểm tra kết quả"""
        try:
            logger.info("[WAIT] Waiting for result...")
            time.sleep(3)
            
            current_url = self.driver.current_url
            logger.info(f"[INFO] Current URL: {current_url}")
            
            # Check nếu có CAPTCHA
            page_source = self.driver.page_source.lower()
            
            if 'turnstile' in page_source or 'challenges.cloudflare.com' in page_source or 'challenge' in current_url:
                logger.warning("[CAPTCHA] Cloudflare Turnstile detected after submit!")
                
                # Giải CAPTCHA
                if self.solve_turnstile_captcha():
                    logger.info("[OK] CAPTCHA solved, checking result again...")
                    time.sleep(5)
                    current_url = self.driver.current_url
                    page_source = self.driver.page_source.lower()
                else:
                    logger.error("[FAIL] Could not solve CAPTCHA")
                    return False
            
            # Check success
            wait = WebDriverWait(self.driver, 15)
            try:
                wait.until(EC.any_of(
                    EC.presence_of_element_located((By.NAME, "password")),
                    EC.visibility_of_element_located((By.XPATH, "//*[contains(text(),'verify your email')]")),
                ))
                
                if 'password' in page_source:
                    logger.info("[SUCCESS] Password page reached!")
                    return True
                elif 'verify' in page_source or 'email' in page_source:
                    logger.info("[SUCCESS] Email verification page reached!")
                    return True
                    
            except TimeoutException:
                logger.warning("[TIMEOUT] Waiting for next step...")
            
            # Check if still on registration page
            if '/signup' in current_url or '/register' in current_url:
                logger.error("[FAIL] Still on registration page")
                return False
            else:
                logger.info("[SUCCESS] Page changed, likely succeeded")
                return True
                
        except Exception as e:
            logger.error(f"[ERROR] Result check failed: {e}")
            return False
    
    def run(self):
        """Chạy toàn bộ flow"""
        try:
            print("\n" + "="*60)
            print("RUMBLE SIMPLE BYPASS - With CAPTCHA Solver")
            print("="*60)
            
            if not self.driver:
                logger.error("[FAIL] Driver not initialized")
                return False
            
            # Check balance
            try:
                balance = self.captcha_api.get_balance()
                logger.info(f"[BALANCE] NextCaptcha: {balance}")
            except Exception as e:
                logger.warning(f"[WARN] Could not check balance: {e}")
            
            # Navigate
            if not self.navigate_to_registration():
                return False
            
            # Generate data
            user_data = self.generate_user_data()
            
            # Fill form
            if not self.fill_form(user_data):
                return False
            
            # Submit
            if not self.submit_form():
                return False
            
            # Wait for result
            success = self.wait_for_result()
            
            if success:
                print("\n" + "="*60)
                print("[SUCCESS] REGISTRATION COMPLETED!")
                print("="*60)
            else:
                print("\n" + "="*60)
                print("[FAILED] Registration failed")
                print("="*60)
            
            # Keep browser open
            logger.info("[INFO] Keeping browser open for 30 seconds...")
            time.sleep(30)
            
            return success
            
        except Exception as e:
            logger.error(f"[ERROR] Run failed: {e}")
            return False
        finally:
            if self.driver:
                logger.info("[CLOSE] Closing browser...")
                self.driver.quit()

def main():
    print("="*60)
    print("RUMBLE SIMPLE BYPASS")
    print("Features:")
    print("  - Basic stealth")
    print("  - Cloudflare Turnstile solver")
    print("  - Simple and reliable")
    print("="*60)
    
    bot = RumbleSimpleBypass()
    bot.run()

if __name__ == "__main__":
    main()
