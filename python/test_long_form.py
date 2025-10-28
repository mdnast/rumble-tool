"""
Test LONG FORM only - Gender and Country fix
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

# Setup logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/test_long_form.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TestLongForm:
    def __init__(self):
        self.driver = None
        self.setup_driver()
    
    def setup_driver(self):
        """Setup Chrome"""
        try:
            logger.info("[DRIVER] Initializing Chrome...")
            
            options = uc.ChromeOptions()
            options.add_argument('--start-maximized')
            
            self.driver = uc.Chrome(options=options, use_subprocess=True)
            self.driver.implicitly_wait(10)
            
            logger.info("[DRIVER] Chrome initialized")
            return True
            
        except Exception as e:
            logger.error(f"[DRIVER] Failed: {e}")
            return False
    
    def human_delay(self, min_sec=0.5, max_sec=2.0):
        """Random delay"""
        time.sleep(random.uniform(min_sec, max_sec))
    
    def human_type(self, element, text):
        """Type text"""
        element.clear()
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))
        self.human_delay(0.3, 0.6)
    
    def take_screenshot(self, name):
        """Take screenshot"""
        try:
            filename = f"logs/test_long_{name}_{int(time.time())}.png"
            self.driver.save_screenshot(filename)
            logger.info(f"[SCREENSHOT] {filename}")
            return filename
        except Exception as e:
            logger.error(f"[SCREENSHOT] Error: {e}")
            return None
    
    def generate_user_data(self):
        """Generate test data"""
        random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=11))
        
        years_ago = random.randint(18, 30)
        birth_date = datetime.now() - timedelta(days=years_ago * 365 + random.randint(0, 365))
        
        months = ["January", "February", "March", "April", "May", "June", 
                  "July", "August", "September", "October", "November", "December"]
        
        return {
            'email': f"test_{random_str}@gmail.com",
            'username': f"user_{random_str}",
            'gender_value': random.choice(['male', 'female']),
            'birth_month_text': months[birth_date.month - 1],
            'birth_day': str(birth_date.day),
            'birth_year': str(birth_date.year)
        }
    
    def fill_long_form(self, user_data):
        """Fill LONG form with Gender and Country"""
        try:
            logger.info("[FORM] Filling LONG form...")
            wait = WebDriverWait(self.driver, 10)
            
            # Email
            email_field = wait.until(EC.presence_of_element_located((By.NAME, "email")))
            email_field.click()
            self.human_delay(0.2, 0.4)
            self.human_type(email_field, user_data['email'])
            logger.info(f"[FORM] Email: {user_data['email']}")
            
            # Username
            username_field = self.driver.find_element(By.NAME, "username")
            username_field.click()
            self.human_delay(0.2, 0.4)
            self.human_type(username_field, user_data['username'])
            logger.info(f"[FORM] Username: {user_data['username']}")
            
            # Gender - FIX HERE
            try:
                self.human_delay(0.3, 0.5)
                
                gender_element = self.driver.find_element(By.NAME, "gender")
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", gender_element)
                self.human_delay(0.5, 0.8)
                
                # Try Select first
                try:
                    gender_select = Select(gender_element)
                    gender_select.select_by_value(user_data['gender_value'])
                    logger.info(f"[FORM] Gender set via Select: {user_data['gender_value']}")
                except Exception as select_error:
                    logger.info(f"[FORM] Custom gender dropdown: {select_error}")
                    
                    # Click parent or element
                    try:
                        parent = gender_element.find_element(By.XPATH, "./parent::*")
                        parent.click()
                    except:
                        gender_element.click()
                    
                    self.human_delay(1.0, 1.5)
                    self.take_screenshot("gender_dropdown_open")
                    
                    # Find option
                    option_found = False
                    gender_text = "Male" if user_data['gender_value'] == 'male' else "Female"
                    
                    selectors = [
                        f"//div[contains(@class, 'option') and contains(text(), '{gender_text}')]",
                        f"//li[contains(text(), '{gender_text}')]",
                        f"//*[@role='option' and contains(text(), '{gender_text}')]",
                        f"//div[contains(@class, 'dropdown')]//div[contains(text(), '{gender_text}')]",
                        f"//div[contains(@class, 'select')]//div[contains(text(), '{gender_text}')]"
                    ]
                    
                    for selector in selectors:
                        try:
                            option = WebDriverWait(self.driver, 3).until(
                                EC.presence_of_element_located((By.XPATH, selector))
                            )
                            self.driver.execute_script("arguments[0].scrollIntoView({block: 'nearest'});", option)
                            self.human_delay(0.2, 0.4)
                            try:
                                option.click()
                            except:
                                self.driver.execute_script("arguments[0].click();", option)
                            option_found = True
                            logger.info(f"[FORM] Gender clicked: {gender_text}")
                            break
                        except:
                            continue
                    
                    if not option_found:
                        logger.warning("[FORM] Could not click option, using JS")
                        self.driver.execute_script(f"""
                            var el = arguments[0];
                            el.value = '{user_data['gender_value']}';
                            el.dispatchEvent(new Event('input', {{ bubbles: true }}));
                            el.dispatchEvent(new Event('change', {{ bubbles: true }}));
                            el.dispatchEvent(new Event('blur', {{ bubbles: true }}));
                        """, gender_element)
                
                # Trigger events
                self.driver.execute_script("""
                    var el = arguments[0];
                    el.dispatchEvent(new Event('input', { bubbles: true }));
                    el.dispatchEvent(new Event('change', { bubbles: true }));
                    el.dispatchEvent(new Event('blur', { bubbles: true }));
                """, gender_element)
                
                logger.info(f"[FORM] Gender: {user_data['gender_value']}")
                self.human_delay(0.5, 0.8)
                self.take_screenshot("gender_filled")
                
            except Exception as e:
                logger.error(f"[FORM] Gender error: {e}")
                self.take_screenshot("gender_error")
                return False
            
            # Birthday
            self.human_delay(0.5, 0.8)
            
            # Month
            month_element = self.driver.find_element(By.NAME, "birthday_month")
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", month_element)
            self.human_delay(0.3, 0.5)
            month_element.click()
            self.human_delay(0.5, 0.8)
            month_select = Select(month_element)
            month_select.select_by_visible_text(user_data['birth_month_text'])
            self.driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", month_element)
            logger.info(f"[FORM] Month: {user_data['birth_month_text']}")
            self.human_delay(0.5, 0.8)
            
            # Day
            day_element = self.driver.find_element(By.NAME, "birthday_day")
            day_element.click()
            self.human_delay(0.5, 0.8)
            day_select = Select(day_element)
            day_select.select_by_value(user_data['birth_day'])
            self.driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", day_element)
            logger.info(f"[FORM] Day: {user_data['birth_day']}")
            self.human_delay(0.5, 0.8)
            
            # Year
            year_element = self.driver.find_element(By.NAME, "birthday_year")
            year_element.click()
            self.human_delay(0.5, 0.8)
            year_select = Select(year_element)
            year_select.select_by_value(user_data['birth_year'])
            self.driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", year_element)
            logger.info(f"[FORM] Year: {user_data['birth_year']}")
            self.human_delay(0.5, 0.8)
            
            # Country - FIX HERE
            try:
                self.human_delay(0.3, 0.5)
                
                country_element = self.driver.find_element(By.NAME, "country")
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", country_element)
                self.human_delay(0.5, 0.8)
                
                # Try Select first
                try:
                    country_select = Select(country_element)
                    try:
                        country_select.select_by_value("US")
                    except:
                        try:
                            country_select.select_by_visible_text("United States")
                        except:
                            country_select.select_by_index(1)
                    logger.info("[FORM] Country set via Select: United States")
                except Exception as select_error:
                    logger.info(f"[FORM] Custom country dropdown: {select_error}")
                    
                    # Click parent or element
                    try:
                        parent = country_element.find_element(By.XPATH, "./parent::*")
                        parent.click()
                    except:
                        country_element.click()
                    
                    self.human_delay(1.0, 1.5)
                    self.take_screenshot("country_dropdown_open")
                    
                    # Find United States
                    option_found = False
                    selectors = [
                        "//div[contains(@class, 'option') and contains(text(), 'United States')]",
                        "//li[contains(text(), 'United States')]",
                        "//*[@role='option' and contains(text(), 'United States')]",
                        "//div[contains(@class, 'dropdown')]//div[contains(text(), 'United States')]",
                        "//div[contains(@class, 'select')]//div[contains(text(), 'United States')]",
                        "//div[contains(@class, 'option') and contains(text(), 'USA')]",
                        "//li[contains(text(), 'USA')]",
                        "//*[@role='option' and contains(text(), 'USA')]"
                    ]
                    
                    for selector in selectors:
                        try:
                            option = WebDriverWait(self.driver, 3).until(
                                EC.presence_of_element_located((By.XPATH, selector))
                            )
                            self.driver.execute_script("arguments[0].scrollIntoView({block: 'nearest'});", option)
                            self.human_delay(0.2, 0.4)
                            try:
                                option.click()
                            except:
                                self.driver.execute_script("arguments[0].click();", option)
                            option_found = True
                            logger.info("[FORM] Country clicked: United States")
                            break
                        except:
                            continue
                    
                    if not option_found:
                        logger.warning("[FORM] Could not click option, using JS")
                        self.driver.execute_script("""
                            var el = arguments[0];
                            el.value = 'US';
                            el.dispatchEvent(new Event('input', { bubbles: true }));
                            el.dispatchEvent(new Event('change', { bubbles: true }));
                            el.dispatchEvent(new Event('blur', { bubbles: true }));
                        """, country_element)
                
                # Trigger events
                self.driver.execute_script("""
                    var el = arguments[0];
                    el.dispatchEvent(new Event('input', { bubbles: true }));
                    el.dispatchEvent(new Event('change', { bubbles: true }));
                    el.dispatchEvent(new Event('blur', { bubbles: true }));
                """, country_element)
                
                logger.info("[FORM] Country: United States")
                self.human_delay(0.5, 0.8)
                self.take_screenshot("country_filled")
                
            except Exception as e:
                logger.error(f"[FORM] Country error: {e}")
                self.take_screenshot("country_error")
                return False
            
            logger.info("[FORM] Form filled successfully!")
            return True
            
        except Exception as e:
            logger.error(f"[FORM] Error: {e}")
            self.take_screenshot("form_error")
            return False
    
    def run(self):
        """Run test"""
        try:
            logger.info("="*60)
            logger.info("[TEST] Starting LONG FORM test")
            logger.info("="*60)
            
            # Navigate
            logger.info("[NAV] Going to registration page...")
            self.driver.get("https://rumble.com/register/")
            time.sleep(5)
            
            self.take_screenshot("01_page_loaded")
            
            # Check if it's long form
            has_username = len(self.driver.find_elements(By.NAME, "username")) > 0
            has_gender = len(self.driver.find_elements(By.NAME, "gender")) > 0
            has_country = len(self.driver.find_elements(By.NAME, "country")) > 0
            
            logger.info(f"[DETECT] username={has_username}, gender={has_gender}, country={has_country}")
            
            if not (has_username and has_gender and has_country):
                logger.error("[ERROR] This is NOT a long form! Please check the page.")
                logger.info("[INFO] If you see short form, Rumble may show long form after first submit.")
                self.take_screenshot("not_long_form")
                return False
            
            # Generate data
            user_data = self.generate_user_data()
            logger.info(f"[USER] {user_data}")
            
            # Fill form
            if not self.fill_long_form(user_data):
                logger.error("[TEST] Form fill failed")
                return False
            
            self.take_screenshot("02_form_filled")
            
            logger.info("[SUCCESS] Long form filled successfully!")
            
            # Check terms checkbox
            logger.info("[SUBMIT] Checking for terms checkbox...")
            try:
                checkbox = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//input[@type='checkbox']"))
                )
                if not checkbox.is_selected():
                    self.human_delay(0.5, 0.8)
                    checkbox.click()
                    logger.info("[SUBMIT] Terms checkbox checked")
                    self.human_delay(0.5, 0.8)
            except:
                logger.info("[SUBMIT] No terms checkbox found")
            
            # Click Next button
            logger.info("[SUBMIT] Looking for Next button...")
            self.human_delay(1, 2)
            
            try:
                # Try multiple button selectors
                next_button = None
                button_selectors = [
                    "//button[contains(normalize-space(), 'Next')]",
                    "//button[contains(text(), 'Next')]",
                    "//button[@type='submit']"
                ]
                
                for selector in button_selectors:
                    try:
                        next_button = WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((By.XPATH, selector))
                        )
                        logger.info(f"[SUBMIT] Found button with: {selector}")
                        break
                    except:
                        continue
                
                if not next_button:
                    logger.error("[SUBMIT] Could not find Next button")
                    self.take_screenshot("button_not_found")
                    logger.info("[INFO] Browser will stay open for 60 seconds - please check manually...")
                    time.sleep(60)
                    return True
                
                # Scroll to button
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)
                self.human_delay(1, 1.5)
                
                self.take_screenshot("03_before_click")
                
                logger.info("[SUBMIT] Clicking Next button...")
                try:
                    next_button.click()
                except:
                    self.driver.execute_script("arguments[0].click();", next_button)
                
                logger.info("[SUBMIT] Next button clicked!")
                self.take_screenshot("04_after_click")
                
                # Wait and check result
                logger.info("[WAIT] Waiting for response...")
                for i in range(15):
                    time.sleep(2)
                    
                    try:
                        current_url = self.driver.current_url
                        page_text = self.driver.page_source.lower()
                        
                        # Check success
                        if "password" in page_text or "verify" in page_text or "/password" in current_url:
                            logger.info("[SUCCESS] ✅ BYPASS SUCCESSFUL - Moved to password step!")
                            self.take_screenshot("05_success")
                            logger.info("[INFO] Browser will stay open for 30 seconds...")
                            time.sleep(30)
                            return True
                        
                        # Check error
                        if "not available" in page_text:
                            logger.error("[FAILED] ❌ Bot detected - Registration not available")
                            self.take_screenshot("05_bot_detected")
                            logger.info("[INFO] Browser will stay open for 30 seconds...")
                            time.sleep(30)
                            return False
                        
                        # Check if CAPTCHA
                        if "turnstile" in page_text or "cloudflare" in page_text:
                            logger.warning(f"[CAPTCHA] ⚠️ CAPTCHA detected at {i*2}s")
                            if i == 0:
                                self.take_screenshot("05_captcha_detected")
                    except:
                        pass
                
                # Timeout
                logger.warning("[TIMEOUT] No clear result after 30s")
                self.take_screenshot("05_timeout")
                
                try:
                    final_url = self.driver.current_url
                    logger.info(f"[INFO] Final URL: {final_url}")
                except:
                    pass
                
                logger.info("[INFO] Browser will stay open for 30 seconds for manual check...")
                time.sleep(30)
                
            except Exception as e:
                logger.error(f"[SUBMIT] Error: {e}")
                self.take_screenshot("submit_error")
                logger.info("[INFO] Browser will stay open for 30 seconds...")
                time.sleep(30)
            
            return True
            
        except Exception as e:
            logger.error(f"[TEST] Error: {e}")
            self.take_screenshot("test_error")
            return False
    
    def close(self):
        """Close browser"""
        try:
            if self.driver:
                logger.info("[CLOSE] Closing browser...")
                self.driver.quit()
        except Exception as e:
            logger.error(f"[CLOSE] Error: {e}")

def main():
    print("="*60)
    print("TEST LONG FORM - Gender and Country Fix")
    print("="*60)
    
    test = None
    try:
        test = TestLongForm()
        
        if not test.driver:
            print("[ERROR] Failed to initialize driver")
            return
        
        success = test.run()
        
        if success:
            print("\n" + "="*60)
            print("[SUCCESS] Test completed!")
            print("="*60)
        else:
            print("\n" + "="*60)
            print("[FAILED] Test failed")
            print("="*60)
        
    except KeyboardInterrupt:
        print("\n[STOP] User interrupted")
    except Exception as e:
        logger.exception(f"[FATAL] Error: {e}")
    finally:
        if test:
            test.close()

if __name__ == "__main__":
    main()
