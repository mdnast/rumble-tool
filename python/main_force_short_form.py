"""
Test: Force short form detection by hiding long form fields
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
        logging.FileHandler('logs/force_short_form.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ForceShortForm:
    def __init__(self):
        self.driver = None
        self.setup_driver()
    
    def setup_driver(self):
        """Setup undetected Chrome"""
        try:
            options = uc.ChromeOptions()
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--window-size=1400,900')
            
            self.driver = uc.Chrome(options=options, use_subprocess=True)
            self.driver.implicitly_wait(10)
            
            logger.info("[DRIVER] Chrome initialized")
            return True
        except Exception as e:
            logger.error(f"[DRIVER] Failed: {e}")
            return False
    
    def generate_user_data(self):
        """Generate random user data"""
        random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=11))
        years_ago = random.randint(18, 30)
        birth_date = datetime.now() - timedelta(days=years_ago * 365 + random.randint(0, 365))
        
        months = ["January", "February", "March", "April", "May", "June", 
                  "July", "August", "September", "October", "November", "December"]
        
        return {
            'email': f"{random_str}.{random.randint(1000, 9999)}@outlook.com",
            'birth_month_text': months[birth_date.month - 1],
            'birth_day': str(birth_date.day),
            'birth_year': str(birth_date.year)
        }
    
    def test_form_detection(self):
        """Test if we can detect/modify form type"""
        try:
            self.driver.get("https://rumble.com/register/")
            
            # Wait for page load
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.NAME, "email"))
            )
            
            logger.info("[PAGE] Loaded")
            time.sleep(3)
            
            # Check what fields exist
            has_username = len(self.driver.find_elements(By.NAME, "username")) > 0
            has_gender = len(self.driver.find_elements(By.NAME, "gender")) > 0
            has_country = len(self.driver.find_elements(By.NAME, "country")) > 0
            
            logger.info(f"[FORM] Username: {has_username}, Gender: {has_gender}, Country: {has_country}")
            
            if has_username or has_gender or has_country:
                logger.info("[FORM] LONG FORM DETECTED - Attempting to hide fields...")
                
                # Try to hide long form fields via JavaScript
                hide_script = """
                // Hide username field
                var username = document.querySelector('[name="username"]');
                if (username) {
                    var usernameContainer = username.closest('div[class*="field"], div[class*="input"], div[class*="form"]');
                    if (usernameContainer) usernameContainer.style.display = 'none';
                }
                
                // Hide gender field
                var gender = document.querySelector('[name="gender"]');
                if (gender) {
                    var genderContainer = gender.closest('div[class*="field"], div[class*="input"], div[class*="form"]');
                    if (genderContainer) genderContainer.style.display = 'none';
                }
                
                // Hide country field
                var country = document.querySelector('[name="country"]');
                if (country) {
                    var countryContainer = country.closest('div[class*="field"], div[class*="input"], div[class*="form"]');
                    if (countryContainer) countryContainer.style.display = 'none';
                }
                
                return 'Fields hidden';
                """
                
                result = self.driver.execute_script(hide_script)
                logger.info(f"[JS] {result}")
                time.sleep(2)
                
                # Take screenshot
                self.driver.save_screenshot("logs/test_hidden_fields.png")
                logger.info("[SCREENSHOT] Saved")
                
            else:
                logger.info("[FORM] SHORT FORM DETECTED")
            
            # Now try to fill as short form
            user_data = self.generate_user_data()
            
            # Fill email
            email_field = self.driver.find_element(By.NAME, "email")
            email_field.send_keys(user_data['email'])
            logger.info(f"[FORM] Email: {user_data['email']}")
            time.sleep(1)
            
            # Fill birthday
            month_el = self.driver.find_element(By.NAME, "birthday_month")
            Select(month_el).select_by_visible_text(user_data['birth_month_text'])
            time.sleep(0.5)
            
            day_el = self.driver.find_element(By.NAME, "birthday_day")
            Select(day_el).select_by_value(user_data['birth_day'])
            time.sleep(0.5)
            
            year_el = self.driver.find_element(By.NAME, "birthday_year")
            Select(year_el).select_by_value(user_data['birth_year'])
            logger.info(f"[FORM] Birthday: {user_data['birth_month_text']} {user_data['birth_day']}, {user_data['birth_year']}")
            time.sleep(1)
            
            # Check terms
            checkbox = self.driver.find_element(By.XPATH, "//input[@type='checkbox']")
            if not checkbox.is_selected():
                checkbox.click()
                logger.info("[FORM] Terms checked")
            time.sleep(1)
            
            self.driver.save_screenshot("logs/test_before_submit.png")
            
            # Try submit
            button = self.driver.find_element(By.XPATH, "//button[contains(normalize-space(), 'Next')]")
            button.click()
            logger.info("[SUBMIT] Clicked Next")
            
            time.sleep(5)
            
            # Check result
            current_url = self.driver.current_url
            page_text = self.driver.page_source.lower()
            
            if "not available" in page_text:
                logger.error("[RESULT] BOT DETECTED")
            elif "password" in page_text or "verify" in page_text:
                logger.info("[RESULT] SUCCESS!")
            else:
                logger.warning(f"[RESULT] UNKNOWN - URL: {current_url}")
            
            self.driver.save_screenshot("logs/test_after_submit.png")
            
            time.sleep(10)
            
        except Exception as e:
            logger.exception(f"[ERROR] {e}")
    
    def close(self):
        if self.driver:
            self.driver.quit()

if __name__ == "__main__":
    tester = None
    try:
        tester = ForceShortForm()
        tester.test_form_detection()
    except KeyboardInterrupt:
        print("\n[STOP] User interrupted")
    finally:
        if tester:
            tester.close()
