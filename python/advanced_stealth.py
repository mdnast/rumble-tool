"""
Advanced Stealth Module - Nâng cao bypass bot detection
Includes: Bezier mouse movement, typo simulation, advanced fingerprinting
"""

import random
import time
import math
import logging
from typing import List, Tuple

logger = logging.getLogger(__name__)

class BezierCurve:
    """Generate smooth Bezier curve for mouse movement"""
    
    @staticmethod
    def bernstein_poly(i, n, t):
        """Bernstein polynomial"""
        return math.comb(n, i) * (t ** i) * ((1 - t) ** (n - i))
    
    @staticmethod
    def bezier_curve(points: List[Tuple[float, float]], num_steps: int = 50) -> List[Tuple[int, int]]:
        """
        Generate Bezier curve from control points
        Args:
            points: List of (x, y) control points
            num_steps: Number of points in the curve
        Returns:
            List of (x, y) coordinates
        """
        n = len(points) - 1
        curve = []
        
        for step in range(num_steps + 1):
            t = step / num_steps
            x = y = 0
            
            for i, (px, py) in enumerate(points):
                b = BezierCurve.bernstein_poly(i, n, t)
                x += b * px
                y += b * py
            
            curve.append((int(x), int(y)))
        
        return curve

class HumanBehaviorAdvanced:
    """Advanced human behavior simulation"""
    
    @staticmethod
    def generate_mouse_path(start_x: int, start_y: int, end_x: int, end_y: int) -> List[Tuple[int, int]]:
        """
        Generate natural mouse movement path using Bezier curve
        """
        # Generate random control points
        distance = math.sqrt((end_x - start_x)**2 + (end_y - start_y)**2)
        num_control_points = random.randint(2, 4) if distance > 200 else 2
        
        control_points = [(start_x, start_y)]
        
        for i in range(num_control_points - 1):
            # Random offset from straight line
            t = (i + 1) / num_control_points
            mid_x = start_x + (end_x - start_x) * t
            mid_y = start_y + (end_y - start_y) * t
            
            # Add randomness perpendicular to line
            offset_x = random.randint(-50, 50)
            offset_y = random.randint(-50, 50)
            
            control_points.append((mid_x + offset_x, mid_y + offset_y))
        
        control_points.append((end_x, end_y))
        
        # Generate smooth curve
        num_steps = int(distance / 10) + random.randint(20, 40)
        curve = BezierCurve.bezier_curve(control_points, num_steps)
        
        return curve
    
    @staticmethod
    def human_mouse_move(driver, element):
        """
        Move mouse to element with natural Bezier curve
        """
        try:
            from selenium.webdriver.common.action_chains import ActionChains
            
            # Get element position
            location = element.location
            size = element.size
            
            # Target center of element with slight randomness
            target_x = location['x'] + size['width'] // 2 + random.randint(-10, 10)
            target_y = location['y'] + size['height'] // 2 + random.randint(-10, 10)
            
            # Current position (assume starting from random position)
            start_x = random.randint(100, 500)
            start_y = random.randint(100, 300)
            
            # Generate path
            path = HumanBehaviorAdvanced.generate_mouse_path(start_x, start_y, target_x, target_y)
            
            # Move along path with variable speed
            actions = ActionChains(driver)
            
            for i, (x, y) in enumerate(path):
                if i % 5 == 0:  # Update every 5 points to avoid too many actions
                    # Variable speed - slower at start and end
                    t = i / len(path)
                    speed_factor = 1 - abs(2 * t - 1) * 0.5  # Parabola
                    delay = random.uniform(0.001, 0.003) / speed_factor
                    
                    time.sleep(delay)
            
            # Final move to element
            actions.move_to_element_with_offset(element, 
                random.randint(-5, 5), 
                random.randint(-5, 5)
            )
            actions.perform()
            
            # Small delay after arriving
            time.sleep(random.uniform(0.1, 0.3))
            
            logger.debug(f"Mouse moved naturally to element")
            
        except Exception as e:
            logger.debug(f"Human mouse move failed: {e}")
    
    @staticmethod
    def human_type_with_mistakes(element, text: str, mistake_probability: float = 0.15):
        """
        Type text with occasional typos and corrections
        """
        element.clear()
        time.sleep(random.uniform(0.1, 0.3))
        
        typed_text = ""
        i = 0
        
        while i < len(text):
            char = text[i]
            
            # Random typo
            if random.random() < mistake_probability and i > 0:
                # Type wrong char
                wrong_chars = 'qwertyuiopasdfghjklzxcvbnm'
                wrong_char = random.choice(wrong_chars)
                element.send_keys(wrong_char)
                typed_text += wrong_char
                
                # Delay before realizing mistake
                time.sleep(random.uniform(0.2, 0.5))
                
                # Backspace to fix
                element.send_keys('\b')
                typed_text = typed_text[:-1]
                time.sleep(random.uniform(0.1, 0.2))
            
            # Type correct char
            element.send_keys(char)
            typed_text += char
            
            # Variable typing speed
            if char == ' ':
                delay = random.uniform(0.1, 0.2)
            elif char.isupper() or char in '!@#$%':
                delay = random.uniform(0.15, 0.25)  # Slower for special chars
            else:
                delay = random.uniform(0.05, 0.15)
            
            time.sleep(delay)
            i += 1
        
        # Small pause after typing
        time.sleep(random.uniform(0.3, 0.8))
        
        logger.debug(f"Typed with human behavior: {text}")
    
    @staticmethod
    def random_reading_pause(min_sec: float = 1.5, max_sec: float = 4.0):
        """Simulate reading/thinking pause"""
        pause = random.uniform(min_sec, max_sec)
        logger.debug(f"Reading pause: {pause:.2f}s")
        time.sleep(pause)
    
    @staticmethod
    def scroll_naturally(driver):
        """Natural scrolling with acceleration and deceleration"""
        try:
            # Random scroll amount
            total_scroll = random.randint(100, 400)
            direction = random.choice([1, -1])
            
            # Divide into steps with variable speed
            steps = random.randint(5, 10)
            
            for i in range(steps):
                # Acceleration/deceleration curve
                t = i / steps
                # Ease in-out cubic
                if t < 0.5:
                    factor = 4 * t * t * t
                else:
                    factor = 1 - pow(-2 * t + 2, 3) / 2
                
                step_scroll = int(total_scroll / steps * (0.5 + factor * 0.5))
                driver.execute_script(f"window.scrollBy(0, {step_scroll * direction});")
                
                time.sleep(random.uniform(0.02, 0.05))
            
            # Small pause after scroll
            time.sleep(random.uniform(0.3, 0.7))
            
            logger.debug(f"Natural scroll: {total_scroll * direction}px")
            
        except Exception as e:
            logger.debug(f"Scroll failed: {e}")

class AdvancedFingerprint:
    """Advanced browser fingerprint randomization"""
    
    TIMEZONES = [
        'America/New_York', 'America/Chicago', 'America/Los_Angeles',
        'America/Denver', 'America/Phoenix', 'America/Anchorage',
        'Pacific/Honolulu', 'Europe/London', 'Europe/Paris', 'Asia/Tokyo'
    ]
    
    SCREEN_RESOLUTIONS = [
        (1920, 1080), (1366, 768), (1536, 864), (1440, 900),
        (1280, 720), (1600, 900), (1280, 1024), (1920, 1200)
    ]
    
    @staticmethod
    def get_fingerprint_script() -> str:
        """Generate advanced fingerprint randomization script"""
        
        timezone = random.choice(AdvancedFingerprint.TIMEZONES)
        screen_width, screen_height = random.choice(AdvancedFingerprint.SCREEN_RESOLUTIONS)
        
        # Random but realistic values
        device_memory = random.choice([4, 8, 16])
        hardware_concurrency = random.choice([4, 8, 12, 16])
        max_touch_points = random.choice([0, 1, 5, 10])
        
        # Random canvas noise
        canvas_noise = random.uniform(-0.0001, 0.0001)
        
        script = f"""
        // Timezone
        Object.defineProperty(Intl.DateTimeFormat.prototype, 'resolvedOptions', {{
            value: function() {{
                return {{
                    timeZone: '{timezone}',
                    locale: 'en-US',
                    calendar: 'gregory',
                    numberingSystem: 'latn'
                }};
            }}
        }});
        
        // Override Date.getTimezoneOffset
        Date.prototype.getTimezoneOffset = function() {{
            // Offset for {timezone}
            return {random.randint(-420, 300)};
        }};
        
        // Screen properties
        Object.defineProperty(screen, 'width', {{get: () => {screen_width}}});
        Object.defineProperty(screen, 'height', {{get: () => {screen_height}}});
        Object.defineProperty(screen, 'availWidth', {{get: () => {screen_width}}});
        Object.defineProperty(screen, 'availHeight', {{get: () => {screen_height - random.randint(30, 80)}}});
        Object.defineProperty(screen, 'colorDepth', {{get: () => 24}});
        Object.defineProperty(screen, 'pixelDepth', {{get: () => 24}});
        
        // Device memory
        Object.defineProperty(navigator, 'deviceMemory', {{get: () => {device_memory}}});
        Object.defineProperty(navigator, 'hardwareConcurrency', {{get: () => {hardware_concurrency}}});
        Object.defineProperty(navigator, 'maxTouchPoints', {{get: () => {max_touch_points}}});
        
        // WebGL Vendor
        const getParameter = WebGLRenderingContext.prototype.getParameter;
        WebGLRenderingContext.prototype.getParameter = function(parameter) {{
            const vendors = ['Intel Inc.', 'NVIDIA Corporation', 'AMD'];
            const renderers = [
                'Intel Iris OpenGL Engine',
                'NVIDIA GeForce GTX 1060',
                'AMD Radeon RX 580',
                'Intel(R) UHD Graphics 620'
            ];
            
            if (parameter === 37445) {{
                return vendors[Math.floor(Math.random() * vendors.length)];
            }}
            if (parameter === 37446) {{
                return renderers[Math.floor(Math.random() * renderers.length)];
            }}
            return getParameter.apply(this, arguments);
        }};
        
        // Canvas fingerprint with noise
        const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
        HTMLCanvasElement.prototype.toDataURL = function(type) {{
            const context = this.getContext('2d');
            if (context) {{
                const imageData = context.getImageData(0, 0, this.width, this.height);
                for (let i = 0; i < imageData.data.length; i += 4) {{
                    imageData.data[i] = imageData.data[i] + {canvas_noise};
                }}
                context.putImageData(imageData, 0, 0);
            }}
            return originalToDataURL.apply(this, arguments);
        }};
        
        // Audio context fingerprint
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        if (AudioContext) {{
            const originalCreateOscillator = AudioContext.prototype.createOscillator;
            AudioContext.prototype.createOscillator = function() {{
                const oscillator = originalCreateOscillator.apply(this, arguments);
                const originalStart = oscillator.start;
                oscillator.start = function() {{
                    this.frequency.value += Math.random() * 0.001;
                    return originalStart.apply(this, arguments);
                }};
                return oscillator;
            }};
        }}
        
        // WebRTC IP leak protection
        const originalRTCPeerConnection = window.RTCPeerConnection;
        window.RTCPeerConnection = function(...args) {{
            const pc = new originalRTCPeerConnection(...args);
            const originalCreateOffer = pc.createOffer;
            pc.createOffer = function() {{
                return Promise.reject('WebRTC disabled for privacy');
            }};
            return pc;
        }};
        
        // Media devices
        navigator.mediaDevices.enumerateDevices = () => Promise.resolve([
            {{deviceId: 'default', kind: 'audioinput', label: 'Microphone', groupId: '1'}},
            {{deviceId: 'default', kind: 'audiooutput', label: 'Speaker', groupId: '1'}},
            {{deviceId: 'camera1', kind: 'videoinput', label: 'HD Webcam', groupId: '2'}}
        ]);
        
        // Battery API with random values
        navigator.getBattery = () => Promise.resolve({{
            charging: {random.choice(['true', 'false'])},
            chargingTime: {random.randint(0, 7200)},
            dischargingTime: {random.randint(3600, 36000)},
            level: {random.uniform(0.2, 1.0):.2f}
        }});
        
        // Connection API
        Object.defineProperty(navigator, 'connection', {{
            get: () => ({{
                effectiveType: '{random.choice(['4g', '3g', 'wifi'])}',
                rtt: {random.randint(20, 100)},
                downlink: {random.uniform(5, 50):.1f},
                saveData: false
            }})
        }});
        
        console.log('🔒 Advanced fingerprint protection active');
        """
        
        return script
    
    @staticmethod
    def inject_fingerprint(driver):
        """Inject advanced fingerprint script"""
        try:
            script = AdvancedFingerprint.get_fingerprint_script()
            driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': script
            })
            logger.info("✅ Advanced fingerprint injected")
        except Exception as e:
            logger.warning(f"⚠️ Fingerprint injection failed: {e}")

class SessionWarmup:
    """Warm up browser session before registration"""
    
    @staticmethod
    def warmup(driver, target_site: str = "https://rumble.com"):
        """
        Perform warmup activities on the site
        """
        try:
            logger.info("[WARMUP] Starting session warmup...")
            
            # 1. Visit homepage
            logger.info("[WARMUP] Visiting homepage...")
            driver.get(target_site)
            
            # Wait for page to load
            time.sleep(random.uniform(3, 5))
            
            # Check if page loaded
            try:
                driver.execute_script("return document.readyState")
                logger.info("[WARMUP] Homepage loaded")
            except:
                logger.warning("[WARMUP] Could not verify page state")
            
            # 2. Scroll around (simple version to avoid errors)
            try:
                HumanBehaviorAdvanced.scroll_naturally(driver)
                time.sleep(random.uniform(1, 2))
                
                HumanBehaviorAdvanced.scroll_naturally(driver)
                time.sleep(random.uniform(1, 2))
            except Exception as scroll_error:
                logger.debug(f"[WARMUP] Scroll error: {scroll_error}")
                # Fallback to simple scroll
                try:
                    driver.execute_script("window.scrollTo(0, 200);")
                    time.sleep(1)
                except:
                    pass
            
            # 3. Try to click on a video (if available) - simplified
            try:
                from selenium.webdriver.common.by import By
                videos = driver.find_elements(By.CSS_SELECTOR, "a[href*='/v/']")
                if videos and len(videos) > 0:
                    logger.info("[WARMUP] Found videos, skipping click to avoid timeout")
                    # Skip video click to avoid timeout issues
                    pass
            except Exception as e:
                logger.debug(f"[WARMUP] Video check error: {e}")
            
            # 4. Final simple scroll
            try:
                driver.execute_script("window.scrollTo(0, 100);")
                time.sleep(random.uniform(1, 2))
            except:
                pass
            
            logger.info("[WARMUP] Session warmed up successfully")
            return True
            
        except Exception as e:
            logger.warning(f"[WARMUP] Error during warmup: {e}")
            # Continue anyway, warmup is optional
            return False
