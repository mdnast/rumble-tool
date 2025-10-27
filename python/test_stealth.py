"""
Test stealth capabilities - Kiểm tra xem bot có bị phát hiện không
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import undetected_chromedriver as uc
from stealth_utils import STEALTH_JS, random_viewport, get_random_user_agent

def test_bot_detection():
    """Test trên các trang test bot detection"""
    
    print("="*60)
    print("🧪 TESTING BOT DETECTION BYPASS")
    print("="*60)
    
    # Setup driver
    options = uc.ChromeOptions()
    options.add_argument('--disable-blink-features=AutomationControlled')
    
    viewport = random_viewport()
    options.add_argument(f'--window-size={viewport["width"]},{viewport["height"]}')
    
    user_agent = get_random_user_agent()
    options.add_argument(f'--user-agent={user_agent}')
    
    print(f"🧬 User-Agent: {user_agent[:80]}...")
    print(f"🌐 Viewport: {viewport['width']}x{viewport['height']}")
    
    driver = uc.Chrome(options=options)
    
    # Inject stealth
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': STEALTH_JS
    })
    
    print("\n✅ Driver initialized with stealth")
    
    # Test sites
    test_sites = [
        {
            'name': 'Bot.Sannysoft',
            'url': 'https://bot.sannysoft.com/',
            'success_indicators': ['webdriver: false', 'Chrome is not controlled by automated'],
            'wait': 10
        },
        {
            'name': 'AreYouHeadless',
            'url': 'https://arh.antoinevastel.com/bots/areyouheadless',
            'success_indicators': ['You are not Chrome headless'],
            'wait': 8
        },
        {
            'name': 'InCollegeBot',
            'url': 'https://bot.incolumitas.com/',
            'success_indicators': [],
            'wait': 10
        },
    ]
    
    results = []
    
    for site in test_sites:
        print(f"\n{'='*60}")
        print(f"🌐 Testing: {site['name']}")
        print(f"   URL: {site['url']}")
        print(f"{'='*60}")
        
        try:
            driver.get(site['url'])
            time.sleep(site['wait'])
            
            # Check webdriver property
            is_webdriver = driver.execute_script("return navigator.webdriver")
            print(f"   navigator.webdriver: {is_webdriver}")
            
            # Check plugins
            plugins_length = driver.execute_script("return navigator.plugins.length")
            print(f"   navigator.plugins.length: {plugins_length}")
            
            # Check languages
            languages = driver.execute_script("return navigator.languages")
            print(f"   navigator.languages: {languages}")
            
            # Check user agent
            ua = driver.execute_script("return navigator.userAgent")
            print(f"   navigator.userAgent: {ua[:80]}...")
            
            # Check if headless
            is_headless = driver.execute_script("""
                return (
                    navigator.webdriver ||
                    !navigator.plugins.length ||
                    /HeadlessChrome/.test(window.navigator.userAgent)
                );
            """)
            print(f"   Detected as headless/bot: {is_headless}")
            
            # Page source check
            page_source = driver.page_source.lower()
            
            detected = False
            if 'detected' in page_source or 'bot' in page_source:
                detected = True
            
            # Success check
            success = True
            if is_webdriver is not None:
                success = False
                print(f"   ❌ FAILED: navigator.webdriver is not undefined")
            
            if plugins_length == 0:
                success = False
                print(f"   ❌ FAILED: No plugins detected")
            
            if is_headless:
                success = False
                print(f"   ❌ FAILED: Detected as headless/bot")
            
            if success:
                print(f"   ✅ PASSED: Stealth successful on {site['name']}")
            
            results.append({
                'site': site['name'],
                'success': success,
                'webdriver': is_webdriver,
                'plugins': plugins_length,
                'headless': is_headless
            })
            
            # Screenshot
            filename = f"logs/test_{site['name'].lower().replace('.', '_')}_{int(time.time())}.png"
            driver.save_screenshot(filename)
            print(f"   📸 Screenshot saved: {filename}")
            
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            results.append({
                'site': site['name'],
                'success': False,
                'error': str(e)
            })
    
    # Rumble test
    print(f"\n{'='*60}")
    print("🎯 Testing: Rumble.com")
    print(f"{'='*60}")
    
    try:
        driver.get("https://rumble.com/")
        time.sleep(5)
        
        # Check if blocked
        page_source = driver.page_source.lower()
        
        blocked = False
        if any(keyword in page_source for keyword in ['blocked', 'access denied', 'captcha', 'challenge']):
            blocked = True
            print("   ⚠️ WARNING: May be blocked or challenged")
        else:
            print("   ✅ PASSED: Successfully loaded Rumble.com")
        
        # Screenshot
        filename = f"logs/test_rumble_{int(time.time())}.png"
        driver.save_screenshot(filename)
        print(f"   📸 Screenshot: {filename}")
        
        results.append({
            'site': 'Rumble.com',
            'success': not blocked,
            'blocked': blocked
        })
        
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        results.append({
            'site': 'Rumble.com',
            'success': False,
            'error': str(e)
        })
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 SUMMARY")
    print(f"{'='*60}")
    
    total = len(results)
    passed = sum(1 for r in results if r.get('success', False))
    
    for result in results:
        status = "✅ PASS" if result.get('success', False) else "❌ FAIL"
        print(f"{status} - {result['site']}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Stealth is working perfectly!")
    elif passed >= total * 0.7:
        print("\n✅ GOOD! Most tests passed. Stealth is working well.")
    else:
        print("\n⚠️ WARNING! Many tests failed. May be detected as bot.")
    
    print("\n⏰ Closing browser in 15 seconds...")
    print("   (Press Ctrl+C to close immediately)")
    time.sleep(15)
    
    driver.quit()
    print("✅ Browser closed")

if __name__ == "__main__":
    try:
        test_bot_detection()
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
