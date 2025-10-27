"""
RUMBLE ULTIMATE BOT BYPASS - FULL STEALTH VERSION
Tích hợp tất cả kỹ thuật bypass bot detection:
- Undetected ChromeDriver
- NextCaptcha API (Turnstile/reCAPTCHA/hCaptcha)
- Advanced fingerprint spoofing
- Human-like behavior simulation
- Proxy support
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import logging
import random
import string
from datetime import datetime, timedelta
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotInteractableException
import undetected_chromedriver as uc

# Import stealth utilities
from stealth_utils import (
    STEALTH_JS, HumanBehavior, apply_stealth,
    get_proxy_config, random_viewport, get_random_user_agent
)

# Import NextCaptcha API
from nextcaptcha.next import YesCaptchaAPI

os.makedirs('logs', exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/rumble_ultimate.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# NextCaptcha API key
CAPTCHA_API_KEY = "559d1b2771bedd55455c09865b97be55e04a0a9877978"

class RumbleUltimateBypass:
    def __init__(self, proxy=None, headless=False):
        self.driver = None
        self.proxy = proxy
        self.headless = headless
        self.captcha_api = YesCaptchaAPI(client_key=CAPTCHA_API_KEY, open_log=True)
        self.setup_driver()
    
    def setup_driver(self):
        """Setup undetected Chrome driver with maximum stealth"""
        try:
            logger.info("[INIT] Initializing undetected ChromeDriver...")
            
            options = uc.ChromeOptions()
            
            # Basic stealth settings
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-setuid-sandbox')
            options.add_argument('--disable-infobars')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-software-rasterizer')
            options.add_argument('--disable-popup-blocking')
            
            # Randomize viewport
            viewport = random_viewport()
            options.add_argument(f'--window-size={viewport["width"]},{viewport["height"]}')
            
            # User agent
            user_agent = get_random_user_agent()
            options.add_argument(f'--user-agent={user_agent}')
            logger.info(f"[UA] User-Agent: {user_agent[:80]}...")
            
            # Language
            options.add_argument('--lang=en-US,en')
            options.add_experimental_option('prefs', {
                'intl.accept_languages': 'en-US,en'
            })
            
            # Headless mode (if requested)
            if self.headless:
                options.add_argument('--headless=new')
                logger.info("[HEADLESS] Headless mode enabled")
            
            # Proxy configuration
            if self.proxy:
                proxy_config = get_proxy_config(self.proxy)
                if proxy_config:
                    options.add_argument(f'--proxy-server={self.proxy}')
            
            # Additional preferences
            prefs = {
                "credentials_enable_service": False,
                "profile.password_manager_enabled": False,
                "profile.default_content_setting_values.notifications": 2,
                "webrtc.ip_handling_policy": "disable_non_proxied_udp",
                "webrtc.multiple_routes_enabled": False,
                "webrtc.nonproxied_udp_enabled": False
            }
            options.add_experimental_option("prefs", prefs)
            
            # Exclude logging - removed experimental options as they're not compatible with some Chrome versions
            # options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
            # options.add_experimental_option('useAutomationExtension', False)
            
            # Initialize undetected ChromeDriver
            self.driver = uc.Chrome(
                options=options,
                version_main=None,  # Auto-detect
                driver_executable_path=None,
                use_subprocess=True
            )
            
            # Apply stealth scripts
            self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': STEALTH_JS
            })
            
            # Set timeouts
            self.driver.set_page_load_timeout(60)
            self.driver.implicitly_wait(10)
            
            logger.info("[OK] Undetected ChromeDriver initialized successfully")
            logger.info(f"[VIEWPORT] Viewport: {viewport['width']}x{viewport['height']}")
            
            # Test stealth
            self.test_stealth()
            
            return True
            
        except Exception as e:
            logger.exception(f"[FAIL] Failed to initialize driver: {e}")
            return False
    
    def test_stealth(self):
        """Test if bot detection is bypassed"""
        try:
            logger.info("[TEST] Testing stealth capabilities...")
            self.driver.get("https://www.google.com")
            time.sleep(2)
            
            # Check webdriver property
            is_webdriver = self.driver.execute_script("return navigator.webdriver")
            logger.info(f"   navigator.webdriver: {is_webdriver}")
            
            # Check plugins
            plugins_length = self.driver.execute_script("return navigator.plugins.length")
            logger.info(f"   navigator.plugins.length: {plugins_length}")
            
            # Check languages
            languages = self.driver.execute_script("return navigator.languages")
            logger.info(f"   navigator.languages: {languages}")
            
            if is_webdriver is None and plugins_length > 0:
                logger.info("[OK] Stealth test PASSED - Bot detection bypassed!")
            else:
                logger.warning("[WARN] Stealth test WARNING - May be detected as bot")
                
        except Exception as e:
            logger.error(f"[FAIL] Stealth test failed: {e}")
    
    def navigate_to_registration(self):
        """Navigate to Rumble registration page"""
        try:
            registration_url = "https://rumble.com/register/"
            logger.info(f"[NAV] Navigating to: {registration_url}")
            
            self.driver.get(registration_url)
            
            # Simulate human reading
            HumanBehavior.simulate_reading(self.driver, min_time=2, max_time=4)
            
            # Wait for email field
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.NAME, "email"))
            )
            
            logger.info("[OK] Registration page loaded")
            self.take_screenshot("registration_page")
            return True
            
        except TimeoutException:
            logger.error("[FAIL] Timeout loading registration page")
            self.take_screenshot("navigation_timeout")
            return False
        except Exception as e:
            logger.error(f"[FAIL] Navigation failed: {e}")
            self.take_screenshot("navigation_error")
            return False
    
    def solve_captcha(self):
        """Detect and solve CAPTCHA using NextCaptcha API"""
        try:
            logger.info("[CAPTCHA CHECK] Checking for CAPTCHA...")
            
            current_url = self.driver.current_url
            page_source = self.driver.page_source.lower()
            
            # Check for Cloudflare Turnstile
            if 'turnstile' in page_source or 'challenges.cloudflare.com' in page_source:
                logger.info("[CAPTCHA] Cloudflare Turnstile detected!")
                return self.solve_turnstile()
            
            # Check for reCAPTCHA
            elif 'recaptcha' in page_source or 'google.com/recaptcha' in page_source:
                logger.info("[CAPTCHA] reCAPTCHA detected!")
                return self.solve_recaptcha()
            
            # Check for hCaptcha
            elif 'hcaptcha' in page_source or 'hcaptcha.com' in page_source:
                logger.info("[CAPTCHA] hCaptcha detected!")
                return self.solve_hcaptcha()
            
            # Check for generic challenge
            elif any(keyword in page_source for keyword in ['challenge', 'verify you are human', 'security check']):
                logger.warning("[WARN] Generic CAPTCHA/challenge detected")
                # Try Turnstile first as Rumble often uses Cloudflare
                return self.solve_turnstile()
            
            logger.info("[OK] No CAPTCHA detected")
            return True
            
        except Exception as e:
            logger.error(f"[FAIL] CAPTCHA detection failed: {e}")
            return False
    
    def solve_turnstile(self):
        """Solve Cloudflare Turnstile CAPTCHA"""
        try:
            logger.info("[SOLVING] Solving Cloudflare Turnstile...")
            
            # Find website key
            website_key = None
            
            # Method 1: From data-sitekey attribute
            try:
                elements = self.driver.find_elements(By.XPATH, "//*[@data-sitekey]")
                for elem in elements:
                    key = elem.get_attribute('data-sitekey')
                    if key and len(key) > 10:
                        website_key = key
                        logger.info(f"   Found sitekey: {key}")
                        break
            except:
                pass
            
            # Method 2: From page source
            if not website_key:
                page_source = self.driver.page_source
                import re
                match = re.search(r'data-sitekey=["\']([^"\']+)["\']', page_source)
                if match:
                    website_key = match.group(1)
                    logger.info(f"   Found sitekey in source: {website_key}")
            
            if not website_key:
                logger.error("[FAIL] Could not find Turnstile sitekey")
                return False
            
            # Call NextCaptcha API
            current_url = self.driver.current_url
            logger.info(f"   Sending to NextCaptcha API...")
            
            result = self.captcha_api.turnstile(
                website_url=current_url,
                website_key=website_key
            )
            
            if result and result.get("status") == "ready":
                token = result.get("solution", {}).get("token", "")
                logger.info(f"[OK] Turnstile solved! Token: {token[:50]}...")
                
                # Inject token
                self.inject_turnstile_token(token)
                return True
            else:
                error_msg = result.get('errorDescription', 'Unknown error') if result else 'No response'
                logger.error(f"[FAIL] Turnstile solving failed: {error_msg}")
                return False
                
        except Exception as e:
            logger.exception(f"[FAIL] Turnstile solving error: {e}")
            return False
    
    def inject_turnstile_token(self, token):
        """Inject Turnstile token into page"""
        try:
            logger.info("[INJECT] Injecting Turnstile token...")
            
            js_script = f"""
            var token = '{token}';
            
            // Find all hidden inputs
            var hiddenInputs = document.querySelectorAll('input[type="hidden"]');
            hiddenInputs.forEach(function(input) {{
                if (input.name && (input.name.includes('cf') || input.name.includes('token') || input.name.includes('turnstile'))) {{
                    input.value = token;
                    console.log('Token injected into: ' + input.name);
                }}
            }});
            
            // Trigger turnstile callback if exists
            if (window.turnstile && window.turnstile.render) {{
                var widgets = document.querySelectorAll('[data-sitekey]');
                widgets.forEach(function(widget) {{
                    try {{
                        var callback = widget.getAttribute('data-callback');
                        if (callback && window[callback]) {{
                            window[callback](token);
                            console.log('Turnstile callback triggered: ' + callback);
                        }}
                    }} catch (e) {{
                        console.log('Error triggering callback: ' + e);
                    }}
                }});
            }}
            
            // Dispatch event
            var event = new Event('cf-turnstile-response');
            document.dispatchEvent(event);
            
            return 'Token injection completed';
            """
            
            result = self.driver.execute_script(js_script)
            logger.info(f"   {result}")
            
            time.sleep(2)
            logger.info("[OK] Token injected successfully")
            
        except Exception as e:
            logger.error(f"[FAIL] Token injection failed: {e}")
    
    def solve_recaptcha(self):
        """Solve reCAPTCHA v2"""
        try:
            logger.info("[SOLVING] Solving reCAPTCHA...")
            
            # Find website key from iframe
            try:
                iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
                website_key = None
                
                for iframe in iframes:
                    src = iframe.get_attribute('src') or ''
                    if 'google.com/recaptcha' in src:
                        import re
                        match = re.search(r'k=([^&]+)', src)
                        if match:
                            website_key = match.group(1)
                            logger.info(f"   Found reCAPTCHA key: {website_key}")
                            break
                
                if not website_key:
                    logger.error("[FAIL] Could not find reCAPTCHA key")
                    return False
                
                # Call NextCaptcha API
                current_url = self.driver.current_url
                result = self.captcha_api.recaptchav2(
                    website_url=current_url,
                    website_key=website_key
                )
                
                if result and result.get("status") == "ready":
                    token = result.get("solution", {}).get("gRecaptchaResponse", "")
                    logger.info(f"[OK] reCAPTCHA solved! Token: {token[:50]}...")
                    
                    # Inject token
                    js_script = f"""
                    document.getElementById('g-recaptcha-response').innerHTML = '{token}';
                    """
                    self.driver.execute_script(js_script)
                    time.sleep(1)
                    
                    return True
                else:
                    error_msg = result.get('errorDescription', 'Unknown error') if result else 'No response'
                    logger.error(f"[FAIL] reCAPTCHA solving failed: {error_msg}")
                    return False
                    
            except Exception as e:
                logger.exception(f"[FAIL] reCAPTCHA solving error: {e}")
                return False
                
        except Exception as e:
            logger.exception(f"[FAIL] reCAPTCHA error: {e}")
            return False
    
    def solve_hcaptcha(self):
        """Solve hCaptcha"""
        try:
            logger.info("[SOLVING] Solving hCaptcha...")
            
            # Find website key
            try:
                elements = self.driver.find_elements(By.XPATH, "//*[@data-sitekey]")
                website_key = None
                
                for elem in elements:
                    key = elem.get_attribute('data-sitekey')
                    if key and len(key) > 10:
                        website_key = key
                        logger.info(f"   Found hCaptcha key: {key}")
                        break
                
                if not website_key:
                    logger.error("[FAIL] Could not find hCaptcha key")
                    return False
                
                # Call NextCaptcha API
                current_url = self.driver.current_url
                result = self.captcha_api.hcaptcha(
                    website_url=current_url,
                    website_key=website_key
                )
                
                if result and result.get("status") == "ready":
                    token = result.get("solution", {}).get("token", "")
                    logger.info(f"[OK] hCaptcha solved! Token: {token[:50]}...")
                    
                    # Inject token
                    js_script = f"""
                    document.querySelector('[name="h-captcha-response"]').innerHTML = '{token}';
                    document.querySelector('[name="g-recaptcha-response"]').innerHTML = '{token}';
                    """
                    self.driver.execute_script(js_script)
                    time.sleep(1)
                    
                    return True
                else:
                    error_msg = result.get('errorDescription', 'Unknown error') if result else 'No response'
                    logger.error(f"[FAIL] hCaptcha solving failed: {error_msg}")
                    return False
                    
            except Exception as e:
                logger.exception(f"[FAIL] hCaptcha solving error: {e}")
                return False
                
        except Exception as e:
            logger.exception(f"[FAIL] hCaptcha error: {e}")
            return False
    
    def generate_user_data(self):
        """Generate random user data"""
        username_part = ''.join(random.choices(string.ascii_lowercase + string.digits, k=random.randint(8, 11)))
        domain = random.choice(["gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "protonmail.com"])
        email = f"{username_part}.{random.randint(100,9999)}@{domain}"
        username = f"{username_part}{random.randint(10,99)}"
        
        today = datetime.now()
        min_age_days = 18 * 365.25
        max_age_days = 65 * 365.25
        random_days_ago = random.uniform(min_age_days, max_age_days)
        birth_date = today - timedelta(days=random_days_ago)
        
        gender_value = random.choice(["male", "female"])
        
        user_data = {
            'email': email,
            'username': username,
            'gender_value': gender_value,
            'birth_month_text': birth_date.strftime('%B'),
            'birth_day': str(birth_date.day),
            'birth_year': str(birth_date.year),
            'country_text': 'United States'
        }
        
        logger.info(f"[FORM] Generated user: {email}")
        logger.info(f"   Username: {username}, Birthday: {user_data['birth_month_text']} {user_data['birth_day']}, {user_data['birth_year']}")
        
        return user_data
    
    def fill_basic_fields(self, user_data):
        """Fill registration form fields with human-like behavior"""
        try:
            logger.info("[FORM] Filling registration form...")
            wait = WebDriverWait(self.driver, 15)
            
            # Email field
            try:
                email_field = wait.until(EC.visibility_of_element_located((By.NAME, "email")))
                
                # Random scroll and mouse movement
                HumanBehavior.random_scroll(self.driver)
                HumanBehavior.random_delay(0.5, 1.0)
                
                # Scroll to element
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", email_field)
                HumanBehavior.random_delay(0.3, 0.7)
                
                # Type email with human behavior
                HumanBehavior.human_type(email_field, user_data['email'], self.driver)
                
                # Trigger blur event
                self.driver.execute_script("arguments[0].dispatchEvent(new Event('blur', { bubbles: true }));", email_field)
                logger.info("   [OK] Email filled")
                
                HumanBehavior.random_delay(0.5, 1.0)
                
            except Exception as e:
                logger.error(f"   [FAIL] Email field error: {e}")
                return False
            
            # Username field (if exists)
            try:
                username_field = WebDriverWait(self.driver, 3).until(
                    EC.visibility_of_element_located((By.NAME, "username"))
                )
                
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", username_field)
                HumanBehavior.random_delay(0.3, 0.7)
                
                HumanBehavior.human_type(username_field, user_data['username'], self.driver)
                self.driver.execute_script("arguments[0].dispatchEvent(new Event('blur', { bubbles: true }));", username_field)
                logger.info("   [OK] Username filled")
                
                HumanBehavior.random_delay(0.5, 1.0)
                
            except TimeoutException:
                logger.info("   [INFO] Username field not found (short form)")
            
            # Gender field (if exists)
            try:
                gender_select = WebDriverWait(self.driver, 3).until(
                    EC.element_to_be_clickable((By.NAME, "gender"))
                )
                
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", gender_select)
                HumanBehavior.random_delay(0.3, 0.7)
                
                Select(gender_select).select_by_value(user_data['gender_value'])
                self.driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", gender_select)
                logger.info(f"   [OK] Gender selected: {user_data['gender_value']}")
                
                HumanBehavior.random_delay(0.5, 1.0)
                
            except TimeoutException:
                logger.info("   [INFO] Gender field not found (short form)")
            
            # Birthday fields
            try:
                # Month
                month_select = wait.until(EC.element_to_be_clickable((By.NAME, "birthday_month")))
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", month_select)
                HumanBehavior.random_delay(0.3, 0.7)
                
                Select(month_select).select_by_visible_text(user_data['birth_month_text'])
                self.driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", month_select)
                logger.info(f"   [OK] Birth month: {user_data['birth_month_text']}")
                
                HumanBehavior.random_delay(0.3, 0.6)
                
                # Day
                day_select = wait.until(EC.element_to_be_clickable((By.NAME, "birthday_day")))
                Select(day_select).select_by_value(user_data['birth_day'])
                self.driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", day_select)
                logger.info(f"   [OK] Birth day: {user_data['birth_day']}")
                
                HumanBehavior.random_delay(0.3, 0.6)
                
                # Year
                year_select = wait.until(EC.element_to_be_clickable((By.NAME, "birthday_year")))
                Select(year_select).select_by_value(user_data['birth_year'])
                self.driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", year_select)
                logger.info(f"   [OK] Birth year: {user_data['birth_year']}")
                
                HumanBehavior.random_delay(0.5, 1.0)
                
            except Exception as e:
                logger.error(f"   [FAIL] Birthday fields error: {e}")
                return False
            
            # Country field (if exists)
            try:
                country_select = WebDriverWait(self.driver, 3).until(
                    EC.element_to_be_clickable((By.NAME, "country"))
                )
                
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", country_select)
                HumanBehavior.random_delay(0.3, 0.7)
                
                Select(country_select).select_by_visible_text(user_data['country_text'])
                self.driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", country_select)
                logger.info(f"   [OK] Country: {user_data['country_text']}")
                
                HumanBehavior.random_delay(0.5, 1.0)
                
            except TimeoutException:
                logger.info("   [INFO] Country field not found (short form)")
            
            logger.info("[OK] All form fields filled successfully")
            return True
            
        except Exception as e:
            logger.exception(f"[FAIL] Form filling error: {e}")
            self.take_screenshot("form_fill_error")
            return False
    
    def check_terms_and_submit(self):
        """Check terms checkbox and submit form"""
        try:
            logger.info("[OK] Checking terms and submitting...")
            wait = WebDriverWait(self.driver, 12)
            
            # Find terms checkbox
            checkbox_xpaths = [
                "//label[contains(., 'By creating an account with Rumble')]/input[@type='checkbox']",
                "//input[@type='checkbox'][contains(@id, 'terms') or contains(@name, 'terms')]",
                "//a[contains(@href, 'terms')]/ancestor::label/input[@type='checkbox']",
                "//a[contains(@href, 'terms')]/preceding-sibling::input[@type='checkbox']",
                "(//form//input[@type='checkbox'])[1]"
            ]
            
            checkbox_found = False
            checkbox = None
            
            for xpath in checkbox_xpaths:
                try:
                    checkbox = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", checkbox)
                    HumanBehavior.random_delay(0.5, 1.0)
                    
                    checkbox = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
                    checkbox_found = True
                    logger.info(f"   [OK] Found terms checkbox")
                    break
                except (TimeoutException, NoSuchElementException):
                    continue
            
            # Check if checkbox is needed
            if checkbox_found and not checkbox.is_selected():
                logger.info("   [CLICK] Clicking terms checkbox...")
                
                # Random mouse movement before click
                HumanBehavior.random_mouse_movement(self.driver)
                HumanBehavior.random_delay(0.3, 0.7)
                
                try:
                    self.driver.execute_script("arguments[0].click();", checkbox)
                except:
                    checkbox.click()
                
                HumanBehavior.random_delay(0.5, 1.0)
                logger.info("   [OK] Terms checked")
            elif checkbox_found:
                logger.info("   [OK] Terms already checked")
            else:
                logger.info("   [INFO] No terms checkbox (short form)")
            
            # Find and click submit button
            submit_button_xpaths = [
                "//button[contains(normalize-space(), 'Next') and not(@disabled)]",
                "//button[@type='submit' and not(@disabled)]",
                "//input[@type='submit' and not(@disabled)]"
            ]
            
            submit_button = None
            for xpath in submit_button_xpaths:
                try:
                    submit_button = wait.until(EC.visibility_of_element_located((By.XPATH, xpath)))
                    submit_button = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
                    break
                except (TimeoutException, NoSuchElementException):
                    continue
            
            if not submit_button:
                logger.error("   [FAIL] Submit button not found")
                return False
            
            # Scroll to submit button
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", submit_button)
            HumanBehavior.random_delay(0.5, 1.0)
            
            # Random mouse movement
            HumanBehavior.random_mouse_movement(self.driver)
            HumanBehavior.random_delay(0.3, 0.7)
            
            logger.info("   [CLICK] Clicking submit button...")
            try:
                self.driver.execute_script("arguments[0].click();", submit_button)
            except:
                submit_button.click()
            
            logger.info("   [OK] Form submitted!")
            return True
            
        except Exception as e:
            logger.exception(f"[FAIL] Submit error: {e}")
            self.take_screenshot("submit_error")
            return False
    
    def run_registration(self):
        """Run complete registration process"""
        try:
            print("\n" + "="*60)
            print(f"[TARGET] RUMBLE ULTIMATE BOT BYPASS - {datetime.now().strftime('%H:%M:%S')}")
            print("="*60)
            
            # Navigate to registration
            if not self.navigate_to_registration():
                logger.error("[FAIL] Failed to navigate")
                return False
            
            # Check and solve CAPTCHA (initial check)
            if not self.solve_captcha():
                logger.warning("[WARN] Initial CAPTCHA check had issues")
            
            # Generate user data
            user_data = self.generate_user_data()
            
            # Fill form
            self.take_screenshot("before_fill")
            if not self.fill_basic_fields(user_data):
                logger.error("[FAIL] Failed to fill form")
                return False
            
            self.take_screenshot("after_fill")
            
            # Check for CAPTCHA before submit
            if not self.solve_captcha():
                logger.warning("[WARN] Pre-submit CAPTCHA check had issues")
            
            # Submit form
            if not self.check_terms_and_submit():
                logger.error("[FAIL] Failed to submit")
                return False
            
            # Wait for result
            logger.info("[WAIT] Waiting for result...")
            time.sleep(5)
            
            # Check for post-submit CAPTCHA
            if not self.solve_captcha():
                logger.warning("[WARN] Post-submit CAPTCHA check had issues")
            
            # Analyze result
            self.take_screenshot("after_submit")
            
            wait = WebDriverWait(self.driver, 20)
            try:
                wait.until(EC.any_of(
                    EC.presence_of_element_located((By.NAME, "password")),
                    EC.visibility_of_element_located((By.XPATH, "//*[contains(text(),'verify your email')]")),
                    EC.presence_of_element_located((By.XPATH, "//iframe[contains(@title,'captcha')]")),
                ))
                
                current_url = self.driver.current_url
                page_text = self.driver.page_source.lower()
                
                logger.info(f"[NAV] Current URL: {current_url}")
                
                # Check results
                if 'password' in page_text:
                    logger.info("[SUCCESS] SUCCESS! Password page reached!")
                    print("\n[SUCCESS] REGISTRATION SUCCESSFUL - PASSWORD PAGE REACHED!")
                    return True
                elif 'verify your email' in page_text or 'check your email' in page_text:
                    logger.info("[SUCCESS] SUCCESS! Email verification page reached!")
                    print("\n[SUCCESS] REGISTRATION SUCCESSFUL - EMAIL VERIFICATION NEEDED!")
                    return True
                elif any(kw in page_text for kw in ['captcha', 'challenge', 'verify you are human']):
                    logger.warning("[WARN] CAPTCHA appeared after submit - solving again...")
                    if self.solve_captcha():
                        logger.info("[OK] Post-submit CAPTCHA solved!")
                        time.sleep(5)
                        return self.run_registration()  # Retry
                    else:
                        logger.error("[FAIL] Failed to solve post-submit CAPTCHA")
                        return False
                else:
                    logger.warning("[WARN] Unknown result page")
                    return True
                    
            except TimeoutException:
                current_url = self.driver.current_url
                logger.error(f"[FAIL] Timeout waiting for result. URL: {current_url}")
                
                if '/register' not in current_url:
                    logger.info("[WARN] Page changed - may have succeeded")
                    return True
                else:
                    logger.error("[FAIL] Still on registration page - likely failed")
                    return False
            
        except Exception as e:
            logger.exception(f"[FAIL] Registration error: {e}")
            self.take_screenshot("registration_error")
            return False
    
    def take_screenshot(self, name):
        """Take screenshot"""
        try:
            filename = f"logs/screenshot_{name}_{int(time.time())}.png"
            if self.driver.save_screenshot(filename):
                logger.info(f"   [SCREENSHOT] Screenshot: {filename}")
                return filename
        except Exception as e:
            logger.error(f"   [FAIL] Screenshot failed: {e}")
        return None
    
    def close(self):
        """Close browser"""
        try:
            if self.driver:
                logger.info("[CAPTCHA] Closing browser...")
                self.driver.quit()
                logger.info("[OK] Browser closed")
        except Exception as e:
            logger.error(f"[FAIL] Error closing browser: {e}")

def main():
    """Main execution"""
    print("=" * 60)
    print("[TARGET] RUMBLE ULTIMATE BOT BYPASS - FULL STEALTH VERSION")
    print("=" * 60)
    print("Features:")
    print("  [OK] Undetected ChromeDriver")
    print("  [OK] NextCaptcha API (Turnstile/reCAPTCHA/hCaptcha)")
    print("  [OK] Advanced fingerprint spoofing")
    print("  [OK] Human-like behavior simulation")
    print("  [OK] Proxy support")
    print("=" * 60)
    
    bot = None
    try:
        # Configuration
        PROXY = None  # Set proxy: "http://user:pass@host:port"
        HEADLESS = False  # Set True for headless mode
        
        # Initialize bot
        bot = RumbleUltimateBypass(proxy=PROXY, headless=HEADLESS)
        
        if not bot.driver:
            print("\n[FAIL] Failed to initialize browser")
            return
        
        # Check NextCaptcha balance
        try:
            balance = bot.captcha_api.get_balance()
            logger.info(f"[BALANCE] NextCaptcha balance: {balance}")
        except Exception as e:
            logger.warning(f"[WARN] Could not check balance: {e}")
        
        # Run registration
        success = bot.run_registration()
        
        if success:
            print("\n" + "="*60)
            print("[SUCCESS] REGISTRATION PROCESS COMPLETED SUCCESSFULLY!")
            print("="*60)
        else:
            print("\n" + "="*60)
            print("[FAIL] REGISTRATION FAILED - Check logs for details")
            print("="*60)
        
        # Keep browser open for manual verification
        print("\n[TIME] Browser will close in 30 seconds...")
        print("   (Press Ctrl+C to close immediately)")
        time.sleep(30)
        
    except KeyboardInterrupt:
        print("\n[STOP] Interrupted by user")
    except Exception as e:
        logger.exception(f"[FAIL] Fatal error: {e}")
    finally:
        if bot:
            bot.close()
        print("\n[OK] Done")

if __name__ == "__main__":
    main()
