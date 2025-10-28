"""
TEST CLOUDFLARE BYPASS WITH FULL DEBUG
Chụp ảnh từng bước để phân tích vấn đề
"""

import time
import logging
import os
import random
import string
from datetime import datetime

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
        logging.FileHandler('logs/cloudflare_debug.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CloudflareDebugTest:
    def __init__(self):
        self.driver = None
        self.captcha_solver = None
        self.screenshot_counter = 0
        
        # Initialize CAPTCHA solver with YesCaptcha
        if HAS_CAPTCHA_SOLVER:
            try:
                self.captcha_solver = CaptchaSolver(
                    yescaptcha_client_key="559d1b2771bedd55455c09865b97be55e04a0a9877978"
                )
                logger.info("[CAPTCHA] YesCaptcha solver initialized")
            except Exception as e:
                logger.warning(f"[CAPTCHA] Init failed: {e}")
        
        self.setup_driver()
    
    def take_screenshot(self, name):
        """Take screenshot with counter"""
        try:
            self.screenshot_counter += 1
            log_dir = os.path.join(os.path.dirname(__file__), "logs")
            os.makedirs(log_dir, exist_ok=True)
            filename = os.path.join(log_dir, f"debug_{self.screenshot_counter:02d}_{name}_{int(time.time())}.png")
            
            self.driver.save_screenshot(filename)
            logger.info(f"[SCREENSHOT {self.screenshot_counter}] {name} -> {filename}")
            return filename
        except Exception as e:
            logger.error(f"[SCREENSHOT] Error: {e}")
            return None
    
    def setup_driver(self):
        """Setup undetected Chrome with maximum stealth"""
        try:
            logger.info("[DRIVER] Setting up undetected Chrome...")
            
            options = uc.ChromeOptions()
            
            # Anti-detection
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-infobars')
            options.add_argument('--start-maximized')
            
            # User agent
            options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36')
            
            # Prefs
            prefs = {
                "credentials_enable_service": False,
                "profile.password_manager_enabled": False,
                "profile.default_content_setting_values.notifications": 2,
            }
            options.add_experimental_option("prefs", prefs)
            
            # Initialize driver
            self.driver = uc.Chrome(options=options, use_subprocess=True)
            
            logger.info("[DRIVER] Browser opened, waiting for stabilization...")
            time.sleep(3)
            
            # Inject stealth scripts via CDP
            self.inject_stealth_scripts()
            
            # Set timeouts
            self.driver.implicitly_wait(10)
            
            logger.info("[DRIVER] Chrome initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"[DRIVER] Failed: {e}")
            return False
    
    def inject_stealth_scripts(self):
        """Inject anti-detection scripts"""
        try:
            logger.info("[STEALTH] Injecting scripts...")
            
            scripts = {
                'webdriver': "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});",
                'chrome': "window.chrome = {runtime: {}, loadTimes: function() {}, csi: function() {}, app: {}};",
                'permissions': """
                    const originalQuery = window.navigator.permissions.query;
                    window.navigator.permissions.query = (parameters) => (
                        parameters.name === 'notifications' ?
                            Promise.resolve({ state: Notification.permission }) :
                            originalQuery(parameters)
                    );
                """,
                'plugins': """
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => [
                            {name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer'},
                            {name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai'},
                            {name: 'Native Client', filename: 'internal-nacl-plugin'}
                        ]
                    });
                """,
                'languages': "Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});",
            }
            
            for name, script in scripts.items():
                try:
                    self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {'source': script})
                    logger.info(f"[STEALTH] Injected: {name}")
                except Exception as e:
                    logger.warning(f"[STEALTH] Failed {name}: {e}")
            
        except Exception as e:
            logger.warning(f"[STEALTH] Error: {e}")
    
    def detect_cloudflare(self):
        """Detect Cloudflare challenge"""
        try:
            page_source = self.driver.page_source.lower()
            
            # Check for Cloudflare indicators
            cf_indicators = [
                "checking your browser",
                "cloudflare",
                "turnstile",
                "cf-challenge",
                "ray id",
                "please wait",
                "verifying you are human"
            ]
            
            found_indicators = []
            for indicator in cf_indicators:
                if indicator in page_source:
                    found_indicators.append(indicator)
            
            if found_indicators:
                logger.warning(f"[CLOUDFLARE] Detected! Indicators: {found_indicators}")
                return True
            
            # Check for Cloudflare iframes
            iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
            for iframe in iframes:
                src = iframe.get_attribute("src") or ""
                if "challenges.cloudflare.com" in src or "turnstile" in src.lower():
                    logger.warning(f"[CLOUDFLARE] Turnstile iframe detected: {src}")
                    return True
            
            logger.info("[CLOUDFLARE] Not detected")
            return False
            
        except Exception as e:
            logger.error(f"[CLOUDFLARE] Detection error: {e}")
            return False
    
    def solve_cloudflare_challenge(self):
        """Solve Cloudflare Turnstile challenge"""
        try:
            if not self.captcha_solver:
                logger.error("[CAPTCHA] No solver available")
                return False
            
            # Find sitekey
            import re
            page_source = self.driver.page_source
            
            sitekey = None
            
            # Try multiple patterns
            patterns = [
                r'data-sitekey="([^"]+)"',
                r'sitekey:\s*["\']([^"\']+)["\']',
                r'sitekey=([^&\s]+)',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, page_source)
                if match:
                    sitekey = match.group(1)
                    logger.info(f"[CAPTCHA] Found sitekey with pattern: {pattern}")
                    break
            
            # Also check iframe src
            if not sitekey:
                iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
                for iframe in iframes:
                    src = iframe.get_attribute("src") or ""
                    if "turnstile" in src.lower() or "challenges.cloudflare.com" in src:
                        match = re.search(r'sitekey=([^&]+)', src)
                        if match:
                            sitekey = match.group(1)
                            logger.info(f"[CAPTCHA] Found sitekey in iframe: {src}")
                            break
            
            if not sitekey:
                logger.error("[CAPTCHA] Could not find sitekey")
                # Save page source for analysis
                with open("logs/page_source_no_sitekey.html", "w", encoding="utf-8") as f:
                    f.write(page_source)
                logger.info("[DEBUG] Page source saved to logs/page_source_no_sitekey.html")
                return False
            
            logger.info(f"[CAPTCHA] Sitekey: {sitekey}")
            logger.info(f"[CAPTCHA] URL: {self.driver.current_url}")
            logger.info("[CAPTCHA] Solving with YesCaptcha...")
            
            # Solve with YesCaptcha
            token = self.captcha_solver.solve_turnstile(
                self.driver.current_url, 
                sitekey, 
                timeout=120
            )
            
            if token:
                logger.info(f"[CAPTCHA] Token received: {token[:50]}...")
                logger.info("[CAPTCHA] Injecting token into page...")
                
                # Inject token (multiple strategies)
                injection_script = f"""
                // Strategy 1: Find and fill all cf-turnstile-response fields
                var textareas = document.querySelectorAll('textarea[name="cf-turnstile-response"]');
                console.log('Found ' + textareas.length + ' cf-turnstile-response textareas');
                for (var i = 0; i < textareas.length; i++) {{
                    textareas[i].value = '{token}';
                    console.log('Filled textarea ' + i);
                }}
                
                // Strategy 2: Add hidden inputs to all forms
                var forms = document.querySelectorAll('form');
                console.log('Found ' + forms.length + ' forms');
                for (var i = 0; i < forms.length; i++) {{
                    var input = document.createElement('input');
                    input.type = 'hidden';
                    input.name = 'cf-turnstile-response';
                    input.value = '{token}';
                    forms[i].appendChild(input);
                    console.log('Added input to form ' + i);
                }}
                
                // Strategy 3: Try to find Turnstile callback
                if (window.turnstile && window.turnstile.reset) {{
                    console.log('Found turnstile object');
                }}
                
                console.log('Token injection complete');
                return 'Injected';
                """
                
                result = self.driver.execute_script(injection_script)
                logger.info(f"[CAPTCHA] Injection result: {result}")
                
                # Wait a bit
                time.sleep(2)
                
                # Take screenshot after injection
                self.take_screenshot("after_token_injection")
                
                logger.info("[CAPTCHA] Token injected successfully")
                return True
            else:
                logger.error("[CAPTCHA] Failed to get token from YesCaptcha")
                return False
            
        except Exception as e:
            logger.error(f"[CAPTCHA] Error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def run_test(self):
        """Run full test with debug screenshots"""
        try:
            logger.info("="*60)
            logger.info("CLOUDFLARE BYPASS DEBUG TEST")
            logger.info("="*60)
            
            # Step 1: Visit Google first (look natural)
            logger.info("[STEP 1] Visiting Google...")
            self.driver.get("https://www.google.com")
            time.sleep(2)
            self.take_screenshot("01_google_loaded")
            
            # Quick Google interaction
            self.driver.execute_script("window.scrollTo(0, 100);")
            time.sleep(1)
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)
            
            # Step 2: Navigate to Rumble
            logger.info("[STEP 2] Navigating to Rumble...")
            self.driver.get("https://rumble.com/register/")
            time.sleep(3)
            self.take_screenshot("02_rumble_initial")
            
            # Step 3: Check for Cloudflare
            logger.info("[STEP 3] Checking for Cloudflare...")
            is_cloudflare = self.detect_cloudflare()
            self.take_screenshot("03_cloudflare_check")
            
            if is_cloudflare:
                logger.info("[STEP 4] Cloudflare detected, solving...")
                
                # Wait a bit for challenge to fully load
                time.sleep(3)
                self.take_screenshot("04_before_solving")
                
                # Solve challenge
                solved = self.solve_cloudflare_challenge()
                
                if solved:
                    logger.info("[STEP 5] Challenge solved, waiting for redirect...")
                    self.take_screenshot("05_after_solving")
                    
                    # Wait for page to process token
                    time.sleep(5)
                    self.take_screenshot("06_after_wait")
                    
                    # Check if we got through
                    is_cloudflare_still = self.detect_cloudflare()
                    if not is_cloudflare_still:
                        logger.info("[SUCCESS] Passed Cloudflare!")
                        self.take_screenshot("07_success")
                        
                        # Check if registration form is visible
                        try:
                            email_field = WebDriverWait(self.driver, 10).until(
                                EC.presence_of_element_located((By.NAME, "email"))
                            )
                            logger.info("[SUCCESS] Registration form is accessible!")
                            self.take_screenshot("08_form_visible")
                        except:
                            logger.warning("[WARN] No email field found yet")
                            self.take_screenshot("08_no_form")
                    else:
                        logger.error("[FAIL] Still blocked by Cloudflare")
                        self.take_screenshot("07_still_blocked")
                else:
                    logger.error("[FAIL] Could not solve challenge")
                    self.take_screenshot("05_solve_failed")
            else:
                logger.info("[INFO] No Cloudflare detected initially")
                
                # Check if form is there
                try:
                    email_field = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.NAME, "email"))
                    )
                    logger.info("[SUCCESS] Registration form loaded directly!")
                    self.take_screenshot("04_form_loaded")
                except Exception as e:
                    logger.warning(f"[WARN] No form found: {e}")
                    self.take_screenshot("04_no_form")
            
            # Final check
            logger.info("[FINAL] Current URL: " + self.driver.current_url)
            logger.info("[FINAL] Page title: " + self.driver.title)
            
            # Save final page source
            with open("logs/final_page_source.html", "w", encoding="utf-8") as f:
                f.write(self.driver.page_source)
            logger.info("[DEBUG] Final page source saved")
            
            # Keep browser open for manual inspection
            logger.info("\n[INFO] Browser will stay open for 30 seconds for inspection...")
            time.sleep(30)
            
            logger.info("="*60)
            logger.info("[COMPLETE] Test finished")
            logger.info("="*60)
            
        except Exception as e:
            logger.exception(f"[ERROR] Test failed: {e}")
            self.take_screenshot("error")
    
    def close(self):
        """Close browser"""
        try:
            if self.driver:
                logger.info("[CLOSE] Closing browser...")
                self.driver.quit()
        except Exception as e:
            logger.error(f"[CLOSE] Error: {e}")

def main():
    test = None
    try:
        test = CloudflareDebugTest()
        test.run_test()
    except KeyboardInterrupt:
        print("\n[STOP] Interrupted by user")
    except Exception as e:
        logger.exception(f"[FATAL] {e}")
    finally:
        if test:
            test.close()

if __name__ == "__main__":
    main()
