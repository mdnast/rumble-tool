# captcha_solver.py - Universal CAPTCHA Solver
import requests
import time
import logging

logger = logging.getLogger(__name__)

class CaptchaSolver:
    """Universal CAPTCHA solver supporting local API and NextCaptcha"""
    
    def __init__(self, local_api_key=None, nextcaptcha_client_key=None):
        """
        Initialize CAPTCHA solver
        Args:
            local_api_key: API key for local solver (http://localhost:5000)
            nextcaptcha_client_key: Client key for NextCaptcha API
        """
        self.local_api_key = local_api_key
        self.nextcaptcha_client_key = nextcaptcha_client_key
        self.local_api_url = "http://localhost:5000/solve"
        self.nextcaptcha_api_url = "https://api.nextcaptcha.com"
        
    def solve_turnstile(self, url, sitekey, timeout=120):
        """
        Solve Cloudflare Turnstile CAPTCHA
        Returns: token string or None
        """
        # Try local API first
        if self.local_api_key:
            logger.info("[CAPTCHA] Trying local solver API...")
            token = self._solve_with_local_api(url, sitekey, timeout)
            if token:
                return token
        
        # Fallback to NextCaptcha
        if self.nextcaptcha_client_key:
            logger.info("[CAPTCHA] Trying NextCaptcha API...")
            token = self._solve_with_nextcaptcha(url, sitekey, timeout)
            if token:
                return token
        
        logger.error("[CAPTCHA] All solvers failed or not configured")
        return None
    
    def _solve_with_local_api(self, url, sitekey, timeout):
        """Solve using local API"""
        try:
            payload = {
                "api_key": self.local_api_key,
                "url": url,
                "sitekey": sitekey,
                "type": "turnstile"  # Explicitly specify Turnstile type
            }
            
            logger.info(f"[CAPTCHA] Sending request to local API: {self.local_api_url}")
            logger.info(f"[CAPTCHA] URL: {url}, Sitekey: {sitekey}")
            
            response = requests.post(self.local_api_url, json=payload, timeout=timeout)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"[CAPTCHA] Local API response: {data}")
                
                # Check various response formats
                if data.get("success") and data.get("token"):
                    token = data.get("token")
                    logger.info("[CAPTCHA] Local API solved successfully")
                    logger.info(f"[CAPTCHA] Token: {token[:50]}...")
                    return token
                elif data.get("solution"):
                    token = data.get("solution")
                    logger.info("[CAPTCHA] Local API solved successfully")
                    logger.info(f"[CAPTCHA] Token: {token[:50]}...")
                    return token
                else:
                    logger.warning(f"[CAPTCHA] Local API returned no token: {data}")
            else:
                logger.warning(f"[CAPTCHA] Local API failed: {response.status_code} - {response.text}")
        except requests.exceptions.ConnectionError:
            logger.warning("[CAPTCHA] Local API not reachable (service not running at localhost:5000)")
        except Exception as e:
            logger.warning(f"[CAPTCHA] Local API error: {e}")
        
        return None
    
    def _solve_with_nextcaptcha(self, url, sitekey, timeout):
        """Solve using NextCaptcha API"""
        try:
            # Create task
            create_url = f"{self.nextcaptcha_api_url}/createTask"
            task_payload = {
                "clientKey": self.nextcaptcha_client_key,
                "task": {
                    "type": "TurnstileTaskProxyLess",
                    "websiteURL": url,
                    "websiteKey": sitekey
                }
            }
            
            logger.info("[CAPTCHA] Creating NextCaptcha task...")
            response = requests.post(create_url, json=task_payload, timeout=30)
            
            if response.status_code != 200:
                logger.error(f"[CAPTCHA] NextCaptcha create task failed: {response.status_code}")
                return None
            
            data = response.json()
            if data.get("errorId") != 0:
                logger.error(f"[CAPTCHA] NextCaptcha error: {data.get('errorDescription')}")
                return None
            
            task_id = data.get("taskId")
            if not task_id:
                logger.error("[CAPTCHA] No taskId received from NextCaptcha")
                return None
            
            logger.info(f"[CAPTCHA] Task created: {task_id}, polling for result...")
            
            # Poll for result
            result_url = f"{self.nextcaptcha_api_url}/getTaskResult"
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                time.sleep(3)
                
                result_payload = {
                    "clientKey": self.nextcaptcha_client_key,
                    "taskId": task_id
                }
                
                result_response = requests.post(result_url, json=result_payload, timeout=30)
                
                if result_response.status_code != 200:
                    continue
                
                result_data = result_response.json()
                
                if result_data.get("status") == "ready":
                    token = result_data.get("solution", {}).get("token")
                    if token:
                        logger.info("[CAPTCHA] NextCaptcha solved successfully")
                        return token
                elif result_data.get("status") == "processing":
                    logger.info("[CAPTCHA] Still processing...")
                    continue
                else:
                    logger.warning(f"[CAPTCHA] Unexpected status: {result_data}")
                    break
            
            logger.error("[CAPTCHA] NextCaptcha timeout")
        except Exception as e:
            logger.error(f"[CAPTCHA] NextCaptcha error: {e}")
        
        return None

    def solve_recaptcha_v2(self, url, sitekey, timeout=120):
        """Solve reCAPTCHA v2"""
        if self.local_api_key:
            logger.info("[CAPTCHA] Trying local solver for reCAPTCHA v2...")
            try:
                payload = {
                    "api_key": self.local_api_key,
                    "url": url,
                    "sitekey": sitekey,
                    "type": "recaptcha_v2"
                }
                response = requests.post(self.local_api_url, json=payload, timeout=timeout)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success") or data.get("token"):
                        return data.get("token") or data.get("solution")
            except Exception as e:
                logger.warning(f"[CAPTCHA] Local API reCAPTCHA v2 error: {e}")
        
        if self.nextcaptcha_client_key:
            logger.info("[CAPTCHA] Trying NextCaptcha for reCAPTCHA v2...")
            try:
                create_url = f"{self.nextcaptcha_api_url}/createTask"
                task_payload = {
                    "clientKey": self.nextcaptcha_client_key,
                    "task": {
                        "type": "RecaptchaV2TaskProxyless",
                        "websiteURL": url,
                        "websiteKey": sitekey
                    }
                }
                response = requests.post(create_url, json=task_payload, timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    task_id = data.get("taskId")
                    if task_id:
                        return self._poll_nextcaptcha_result(task_id, timeout)
            except Exception as e:
                logger.warning(f"[CAPTCHA] NextCaptcha reCAPTCHA v2 error: {e}")
        
        return None
    
    def _poll_nextcaptcha_result(self, task_id, timeout):
        """Poll NextCaptcha for task result"""
        result_url = f"{self.nextcaptcha_api_url}/getTaskResult"
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            time.sleep(3)
            try:
                payload = {
                    "clientKey": self.nextcaptcha_client_key,
                    "taskId": task_id
                }
                response = requests.post(result_url, json=payload, timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "ready":
                        return data.get("solution", {}).get("gRecaptchaResponse")
            except Exception:
                continue
        
        return None
