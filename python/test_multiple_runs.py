"""
Test script to run multiple registration attempts and detect form type
"""

import sys
import time
import subprocess
import re

def run_single_test(run_number):
    """Run a single test and check result"""
    print(f"\n{'='*60}")
    print(f"RUN {run_number}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            ['python', 'main_ultimate_final.py'],
            capture_output=True,
            text=True,
            timeout=180,
            cwd=r'C:\rumble-tool\python'
        )
        
        output = result.stdout + result.stderr
        
        # Check for form type
        has_username = 'Username:' in output and 'FORM] Username:' in output
        has_gender = 'Gender' in output and ('Gender set' in output or 'Gender completed' in output)
        has_country = 'Country' in output and ('Country set' in output or 'Country completed' in output)
        
        form_type = "LONG" if (has_username or has_gender or has_country) else "SHORT"
        
        # Check result
        if "SUCCESS" in output and "succeeded" in output:
            result_status = "[SUCCESS]"
        elif "Bot detected" in output or "not available" in output:
            result_status = "[BOT DETECTED]"
        elif "CAPTCHA" in output:
            result_status = "[CAPTCHA ISSUE]"
        else:
            result_status = "[UNKNOWN]"
        
        print(f"Form Type: {form_type}")
        print(f"Result: {result_status}")
        
        # Extract key info
        if has_username:
            username_match = re.search(r'\[FORM\] Username: (\S+)', output)
            if username_match:
                print(f"  Username: {username_match.group(1)}")
        
        if has_gender:
            gender_match = re.search(r'Gender.*?: (\w+)', output)
            if gender_match:
                print(f"  Gender: {gender_match.group(1)}")
        
        if has_country:
            print(f"  Country: Detected")
        
        return {
            'run': run_number,
            'form_type': form_type,
            'status': result_status,
            'has_username': has_username,
            'has_gender': has_gender,
            'has_country': has_country,
            'output': output
        }
        
    except subprocess.TimeoutExpired:
        print("[TIMEOUT]")
        return {
            'run': run_number,
            'form_type': 'TIMEOUT',
            'status': '[TIMEOUT]',
            'has_username': False,
            'has_gender': False,
            'has_country': False,
            'output': ''
        }
    except Exception as e:
        print(f"[ERROR]: {e}")
        return {
            'run': run_number,
            'form_type': 'ERROR',
            'status': f'[ERROR]: {e}',
            'has_username': False,
            'has_gender': False,
            'has_country': False,
            'output': ''
        }

def main():
    num_runs = 1  # Test 1 lần để xem long form
    results = []
    
    print("="*60)
    print("MULTIPLE REGISTRATION TEST")
    print("Testing to detect LONG FORM appearance")
    print("="*60)
    
    for i in range(1, num_runs + 1):
        result = run_single_test(i)
        results.append(result)
        
        # If long form detected, save output and stop
        if result['form_type'] == 'LONG':
            print("\n" + "!"*60)
            print("LONG FORM DETECTED!")
            print("!"*60)
            
            # Save full output
            with open('logs/long_form_detected.log', 'w', encoding='utf-8') as f:
                f.write(result['output'])
            print("Full output saved to: logs/long_form_detected.log")
            
            # Alert user
            print("\nStopping tests - Long form found!")
            print("Please review the log and fix the code.")
            break
        
        # Delay between runs
        if i < num_runs:
            print(f"\nWaiting 5 seconds before next run...")
            time.sleep(5)
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    short_forms = sum(1 for r in results if r['form_type'] == 'SHORT')
    long_forms = sum(1 for r in results if r['form_type'] == 'LONG')
    errors = sum(1 for r in results if r['form_type'] in ['ERROR', 'TIMEOUT'])
    
    print(f"Total runs: {len(results)}")
    print(f"Short forms: {short_forms}")
    print(f"Long forms: {long_forms}")
    print(f"Errors/Timeouts: {errors}")
    
    if long_forms > 0:
        print("\n[WARNING] LONG FORM DETECTED - Needs fixing!")
    else:
        print("\n[OK] All forms were SHORT - Looking good!")

if __name__ == "__main__":
    main()
