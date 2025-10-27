"""
Quick run script - Chạy nhanh với config đơn giản
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import argparse
from main_ultimate import RumbleUltimateBypass

def main():
    parser = argparse.ArgumentParser(description='Rumble Bot Bypass - Quick Run')
    parser.add_argument('--proxy', type=str, help='Proxy URL (e.g., http://user:pass@host:port)', default=None)
    parser.add_argument('--headless', action='store_true', help='Run in headless mode')
    parser.add_argument('--count', type=int, default=1, help='Number of registration attempts')
    
    args = parser.parse_args()
    
    print("="*60)
    print("RUMBLE BOT BYPASS - QUICK RUN")
    print("="*60)
    print(f"Configuration:")
    print(f"  Proxy: {args.proxy or 'None'}")
    print(f"  Headless: {args.headless}")
    print(f"  Attempts: {args.count}")
    print("="*60)
    
    success_count = 0
    fail_count = 0
    
    for i in range(args.count):
        print(f"\n{'='*60}")
        print(f">>> Attempt {i+1}/{args.count}")
        print(f"{'='*60}")
        
        bot = None
        try:
            bot = RumbleUltimateBypass(proxy=args.proxy, headless=args.headless)
            
            if not bot.driver:
                print("❌ Failed to initialize browser")
                fail_count += 1
                continue
            
            # Check balance
            try:
                balance = bot.captcha_api.get_balance()
                print(f"NextCaptcha balance: {balance}")
            except:
                pass
            
            # Run registration
            success = bot.run_registration()
            
            if success:
                success_count += 1
                print(f"\n[SUCCESS] Attempt {i+1} SUCCEEDED")
            else:
                fail_count += 1
                print(f"\n[FAILED] Attempt {i+1} FAILED")
            
        except KeyboardInterrupt:
            print("\n[STOP] Interrupted by user")
            break
        except Exception as e:
            print(f"\n[ERROR] Error: {e}")
            fail_count += 1
        finally:
            if bot:
                bot.close()
        
        # Delay between attempts
        if i < args.count - 1:
            import time
            delay = 10
            print(f"\n[WAIT] Waiting {delay} seconds before next attempt...")
            time.sleep(delay)
    
    # Final summary
    print(f"\n{'='*60}")
    print("FINAL SUMMARY")
    print(f"{'='*60}")
    print(f"[OK] Success: {success_count}")
    print(f"[FAIL] Failed: {fail_count}")
    print(f"Success rate: {success_count/(success_count+fail_count)*100:.1f}%")
    print("="*60)

if __name__ == "__main__":
    main()
