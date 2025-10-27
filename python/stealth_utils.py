"""
Stealth utilities for bypassing bot detection
"""
import random
import time
import logging

logger = logging.getLogger(__name__)

# Advanced stealth scripts
STEALTH_JS = """
// Override the navigator.webdriver property
Object.defineProperty(navigator, 'webdriver', {
    get: () => undefined
});

// Override permissions API
const originalQuery = window.navigator.permissions.query;
window.navigator.permissions.query = (parameters) => (
    parameters.name === 'notifications' ?
        Promise.resolve({ state: Notification.permission }) :
        originalQuery(parameters)
);

// Override plugins to look like a real browser
Object.defineProperty(navigator, 'plugins', {
    get: () => [
        {
            0: {type: "application/x-google-chrome-pdf", suffixes: "pdf", description: "Portable Document Format", enabledPlugin: Plugin},
            description: "Portable Document Format",
            filename: "internal-pdf-viewer",
            length: 1,
            name: "Chrome PDF Plugin"
        },
        {
            0: {type: "application/pdf", suffixes: "pdf", description: "", enabledPlugin: Plugin},
            description: "",
            filename: "mhjfbmdgcfjbbpaeojofohoefgiehjai",
            length: 1,
            name: "Chrome PDF Viewer"
        },
        {
            0: {type: "application/x-nacl", suffixes: "", description: "Native Client Executable", enabledPlugin: Plugin},
            1: {type: "application/x-pnacl", suffixes: "", description: "Portable Native Client Executable", enabledPlugin: Plugin},
            description: "",
            filename: "internal-nacl-plugin",
            length: 2,
            name: "Native Client"
        }
    ]
});

// Override languages
Object.defineProperty(navigator, 'languages', {
    get: () => ['en-US', 'en']
});

// Override chrome runtime
window.chrome = {
    runtime: {}
};

// Override Notification permissions
const originalNotificationPermission = Notification.permission;
Object.defineProperty(Notification, 'permission', {
    get: () => originalNotificationPermission === 'denied' ? 'default' : originalNotificationPermission
});

// Canvas fingerprint protection
const getImageData = CanvasRenderingContext2D.prototype.getImageData;
CanvasRenderingContext2D.prototype.getImageData = function() {
    const imageData = getImageData.apply(this, arguments);
    for (let i = 0; i < imageData.data.length; i += 4) {
        imageData.data[i] = imageData.data[i] + Math.floor(Math.random() * 10) - 5;
        imageData.data[i+1] = imageData.data[i+1] + Math.floor(Math.random() * 10) - 5;
        imageData.data[i+2] = imageData.data[i+2] + Math.floor(Math.random() * 10) - 5;
    }
    return imageData;
};

// WebGL fingerprint protection
const getParameter = WebGLRenderingContext.prototype.getParameter;
WebGLRenderingContext.prototype.getParameter = function(parameter) {
    if (parameter === 37445) {
        return 'Intel Inc.';
    }
    if (parameter === 37446) {
        return 'Intel Iris OpenGL Engine';
    }
    return getParameter.apply(this, arguments);
};

// Screen properties
Object.defineProperty(screen, 'availWidth', {get: () => screen.width});
Object.defineProperty(screen, 'availHeight', {get: () => screen.height});

// Battery API
navigator.getBattery = () => Promise.resolve({
    charging: true,
    chargingTime: 0,
    dischargingTime: Infinity,
    level: 1
});

// Connection API
Object.defineProperty(navigator, 'connection', {
    get: () => ({
        effectiveType: '4g',
        rtt: 100,
        downlink: 10,
        saveData: false
    })
});

// Media devices
navigator.mediaDevices.enumerateDevices = () => Promise.resolve([
    {deviceId: "default", kind: "audioinput", label: "Default - Microphone", groupId: "1"},
    {deviceId: "default", kind: "audiooutput", label: "Default - Speaker", groupId: "1"},
    {deviceId: "default", kind: "videoinput", label: "Default - Camera", groupId: "2"}
]);

// Hardware concurrency
Object.defineProperty(navigator, 'hardwareConcurrency', {
    get: () => 8
});

// Device memory
Object.defineProperty(navigator, 'deviceMemory', {
    get: () => 8
});

// Mouse and touch events to appear human-like
['mousemove', 'mousedown', 'mouseup', 'click'].forEach(eventType => {
    window.addEventListener(eventType, () => {}, true);
});

console.log('🥷 Stealth mode activated');
"""

class HumanBehavior:
    """Simulate human-like behavior"""
    
    @staticmethod
    def random_delay(min_seconds=0.5, max_seconds=2.0):
        """Random delay between actions"""
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
        return delay
    
    @staticmethod
    def typing_delay():
        """Random delay between keystrokes"""
        return random.uniform(0.05, 0.15)
    
    @staticmethod
    def human_type(element, text, driver=None):
        """Type like a human with random delays"""
        element.clear()
        for char in text:
            element.send_keys(char)
            time.sleep(HumanBehavior.typing_delay())
        
        # Randomly add extra behaviors
        if random.random() < 0.3:
            time.sleep(random.uniform(0.3, 0.8))
    
    @staticmethod
    def random_mouse_movement(driver):
        """Simulate random mouse movements using JavaScript"""
        try:
            # Random positions
            x = random.randint(100, 800)
            y = random.randint(100, 600)
            
            js_script = f"""
            var event = new MouseEvent('mousemove', {{
                'view': window,
                'bubbles': true,
                'cancelable': true,
                'clientX': {x},
                'clientY': {y}
            }});
            document.dispatchEvent(event);
            """
            driver.execute_script(js_script)
            logger.debug(f"Mouse moved to ({x}, {y})")
        except Exception as e:
            logger.debug(f"Mouse movement failed: {e}")
    
    @staticmethod
    def random_scroll(driver):
        """Random scroll to simulate reading"""
        try:
            scroll_amount = random.randint(100, 400)
            direction = random.choice(['down', 'up'])
            
            if direction == 'down':
                driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
            else:
                driver.execute_script(f"window.scrollBy(0, -{scroll_amount});")
            
            logger.debug(f"Scrolled {direction} {scroll_amount}px")
            time.sleep(random.uniform(0.3, 0.8))
        except Exception as e:
            logger.debug(f"Scroll failed: {e}")
    
    @staticmethod
    def simulate_reading(driver, min_time=2, max_time=5):
        """Simulate reading behavior with scrolls and pauses"""
        read_time = random.uniform(min_time, max_time)
        start_time = time.time()
        
        while time.time() - start_time < read_time:
            if random.random() < 0.4:
                HumanBehavior.random_scroll(driver)
            if random.random() < 0.3:
                HumanBehavior.random_mouse_movement(driver)
            time.sleep(random.uniform(0.5, 1.5))

def apply_stealth(driver):
    """Apply all stealth techniques to driver"""
    try:
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': STEALTH_JS
        })
        logger.info("✅ Stealth JavaScript injected")
    except Exception as e:
        logger.warning(f"⚠️ Could not inject stealth JS: {e}")
    
    try:
        # Additional CDP commands for stealth
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": driver.execute_script("return navigator.userAgent").replace('HeadlessChrome', 'Chrome')
        })
        logger.info("✅ User agent stealth applied")
    except Exception as e:
        logger.warning(f"⚠️ Could not set user agent: {e}")

def get_proxy_config(proxy_string):
    """
    Parse proxy string and return config
    Format: protocol://user:pass@host:port or protocol://host:port
    Example: http://user:pass@proxy.com:8080
    """
    if not proxy_string:
        return None
    
    try:
        from urllib.parse import urlparse
        parsed = urlparse(proxy_string)
        
        config = {
            'proxyType': 'MANUAL',
            'httpProxy': f'{parsed.hostname}:{parsed.port}',
            'sslProxy': f'{parsed.hostname}:{parsed.port}',
        }
        
        if parsed.username and parsed.password:
            config['socksUsername'] = parsed.username
            config['socksPassword'] = parsed.password
        
        logger.info(f"✅ Proxy configured: {parsed.hostname}:{parsed.port}")
        return config
    except Exception as e:
        logger.error(f"❌ Invalid proxy format: {e}")
        return None

def random_viewport():
    """Generate random but realistic viewport size"""
    viewports = [
        {'width': 1920, 'height': 1080},
        {'width': 1366, 'height': 768},
        {'width': 1536, 'height': 864},
        {'width': 1440, 'height': 900},
        {'width': 1280, 'height': 720},
    ]
    return random.choice(viewports)

def get_random_user_agent():
    """Get realistic Chrome user agent"""
    chrome_versions = ['119', '120', '121', '122', '123']
    version = random.choice(chrome_versions)
    
    user_agents = [
        f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version}.0.0.0 Safari/537.36',
        f'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version}.0.0.0 Safari/537.36',
        f'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version}.0.0.0 Safari/537.36',
    ]
    
    return random.choice(user_agents)
