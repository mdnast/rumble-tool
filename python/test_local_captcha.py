# -*- coding: utf-8 -*-
"""Test local CAPTCHA solver API"""
import requests
import json

print("Testing local CAPTCHA solver API...")
print("="*60)

# Test 1: Check if service is running
try:
    print("\n[1] Checking if service is running on http://localhost:5000...")
    r = requests.get("http://localhost:5000", timeout=3)
    print(f"[OK] Service is running! Status: {r.status_code}")
    if r.text:
        print(f"Response: {r.text[:200]}")
except requests.exceptions.ConnectionError:
    print("[FAIL] Service is NOT running on localhost:5000")
    print("       Please start your CAPTCHA solver service first!")
    exit(1)
except Exception as e:
    print(f"[ERROR] {e}")
    exit(1)

# Test 2: Test solve endpoint
print("\n[2] Testing /solve endpoint...")
test_data = {
    "api_key": "YOUR_KEY",
    "url": "https://www.google.com/recaptcha/api2/demo",
    "sitekey": "6Le-wvkSAAAAAPBMRTvw0Q4Muexq9bi0DJwx_mJ-"
}

try:
    r = requests.post("http://localhost:5000/solve", json=test_data, timeout=60)
    print(f"[OK] Status Code: {r.status_code}")
    
    try:
        result = r.json()
        print(f"[OK] Response JSON:")
        print(json.dumps(result, indent=2))
        
        if 'token' in result or 'solution' in result:
            print("\n[SUCCESS] API is working and returns token!")
        else:
            print("\n[WARN] API responded but no token found")
            
    except:
        print(f"[WARN] Response is not JSON: {r.text[:200]}")
        
except requests.exceptions.Timeout:
    print("[FAIL] Request timeout (>60s)")
except Exception as e:
    print(f"[ERROR] {e}")

print("\n" + "="*60)
print("Test completed")
