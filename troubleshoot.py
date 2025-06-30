#!/usr/bin/env python3
"""
Instagram Scraper Troubleshooting Tool
This script helps diagnose and fix common issues with Instagram scraping.
"""

import os
import sys
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def check_chrome_driver():
    """Check if ChromeDriver is properly installed and accessible"""
    print("🔍 Checking ChromeDriver...")
    try:
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        
        # Try to get ChromeDriver automatically
        driver_path = ChromeDriverManager().install()
        print(f"✅ ChromeDriver found at: {driver_path}")
        return True
    except Exception as e:
        print(f"❌ ChromeDriver issue: {e}")
        print("💡 Solution: Install ChromeDriver manually or use webdriver-manager")
        return False

def check_chrome_browser():
    """Check if Chrome browser is installed"""
    print("🔍 Checking Chrome browser...")
    try:
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        driver = webdriver.Chrome(options=options)
        version = driver.capabilities['browserVersion']
        driver.quit()
        print(f"✅ Chrome browser found, version: {version}")
        return True
    except Exception as e:
        print(f"❌ Chrome browser issue: {e}")
        print("💡 Solution: Install or update Chrome browser")
        return False

def test_instagram_access():
    """Test basic Instagram access"""
    print("🔍 Testing Instagram access...")
    try:
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        driver = webdriver.Chrome(options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        driver.get("https://www.instagram.com/")
        time.sleep(5)
        
        # Check if we can access Instagram
        title = driver.title
        if "Instagram" in title:
            print("✅ Instagram access successful")
            
            # Check for login page
            try:
                login_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Log In') or contains(text(), 'Sign Up')]")
                if login_elements:
                    print("ℹ️  Instagram login page detected (normal)")
                else:
                    print("ℹ️  Instagram feed detected (already logged in)")
            except:
                pass
                
            driver.quit()
            return True
        else:
            print(f"❌ Unexpected page title: {title}")
            driver.quit()
            return False
            
    except Exception as e:
        print(f"❌ Instagram access failed: {e}")
        return False

def check_cookies():
    """Check if saved cookies exist and are valid"""
    print("🔍 Checking saved cookies...")
    cookies_file = 'insta_cookies.json'
    
    if not os.path.exists(cookies_file):
        print("ℹ️  No saved cookies found (normal for first run)")
        return False
    
    try:
        with open(cookies_file, 'r') as f:
            cookies = json.load(f)
        
        if cookies:
            print(f"✅ Found {len(cookies)} saved cookies")
            
            # Check if cookies are recent (less than 30 days old)
            import datetime
            file_time = os.path.getmtime(cookies_file)
            file_date = datetime.datetime.fromtimestamp(file_time)
            days_old = (datetime.datetime.now() - file_date).days
            
            if days_old < 30:
                print(f"✅ Cookies are {days_old} days old (likely still valid)")
                return True
            else:
                print(f"⚠️  Cookies are {days_old} days old (may be expired)")
                return False
        else:
            print("ℹ️  Cookie file is empty")
            return False
            
    except Exception as e:
        print(f"❌ Error reading cookies: {e}")
        return False

def test_authentication():
    """Test Instagram authentication with saved cookies"""
    print("🔍 Testing authentication...")
    
    if not check_cookies():
        print("ℹ️  No cookies to test with")
        return False
    
    try:
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        driver = webdriver.Chrome(options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # Load cookies
        driver.get("https://www.instagram.com/")
        time.sleep(3)
        
        with open('insta_cookies.json', 'r') as f:
            cookies = json.load(f)
        
        for cookie in cookies:
            if 'expiry' in cookie:
                cookie['expiry'] = int(cookie['expiry'])
            try:
                driver.add_cookie(cookie)
            except Exception:
                continue
        
        driver.refresh()
        time.sleep(5)
        
        # Check if we're logged in
        try:
            login_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Log In') or contains(text(), 'Sign Up')]")
            if login_elements:
                print("❌ Authentication failed - still on login page")
                driver.quit()
                return False
            else:
                print("✅ Authentication successful - logged in")
                driver.quit()
                return True
        except:
            print("❌ Could not determine authentication status")
            driver.quit()
            return False
            
    except Exception as e:
        print(f"❌ Authentication test failed: {e}")
        return False

def check_verification_challenges():
    """Check for common verification challenges"""
    print("🔍 Checking for verification challenges...")
    
    try:
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        driver = webdriver.Chrome(options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        driver.get("https://www.instagram.com/")
        time.sleep(5)
        
        # Check for various verification challenges
        challenges = {
            "2FA": ["Two-Factor", "2FA", "verification code", "authentication code"],
            "Phone/Email": ["phone", "email", "verify", "verification"],
            "Suspicious Activity": ["suspicious", "unusual", "security", "safety"],
            "CAPTCHA": ["captcha", "robot", "human verification"],
            "Account Lock": ["locked", "suspended", "disabled", "restricted"]
        }
        
        found_challenges = []
        for challenge_type, keywords in challenges.items():
            for keyword in keywords:
                try:
                    elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{keyword}')]")
                    if elements:
                        found_challenges.append(challenge_type)
                        break
                except:
                    continue
        
        if found_challenges:
            print(f"⚠️  Found potential challenges: {', '.join(found_challenges)}")
            print("💡 Solution: Complete verification manually in browser")
        else:
            print("✅ No verification challenges detected")
        
        driver.quit()
        return len(found_challenges) == 0
        
    except Exception as e:
        print(f"❌ Error checking verification challenges: {e}")
        return False

def check_network_connectivity():
    """Check network connectivity"""
    print("🔍 Checking network connectivity...")
    
    try:
        import urllib.request
        urllib.request.urlopen('https://www.instagram.com', timeout=10)
        print("✅ Network connectivity to Instagram is good")
        return True
    except Exception as e:
        print(f"❌ Network connectivity issue: {e}")
        print("💡 Solution: Check your internet connection and firewall settings")
        return False

def generate_report():
    """Generate a comprehensive troubleshooting report"""
    print("=" * 60)
    print("🔧 INSTAGRAM SCRAPER TROUBLESHOOTING REPORT")
    print("=" * 60)
    
    checks = [
        ("ChromeDriver", check_chrome_driver),
        ("Chrome Browser", check_chrome_browser),
        ("Network Connectivity", check_network_connectivity),
        ("Instagram Access", test_instagram_access),
        ("Cookies", check_cookies),
        ("Authentication", test_authentication),
        ("Verification Challenges", check_verification_challenges)
    ]
    
    results = {}
    for name, check_func in checks:
        print(f"\n📋 {name} Check:")
        try:
            results[name] = check_func()
        except Exception as e:
            print(f"❌ Error during {name} check: {e}")
            results[name] = False
    
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    
    passed = sum(results.values())
    total = len(results)
    
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 All checks passed! Your setup should work correctly.")
    else:
        print("\n⚠️  Some issues detected. Please address the failed checks above.")
        print("\n💡 Quick fixes:")
        print("1. Install/update Chrome and ChromeDriver")
        print("2. Enable 2FA on your Instagram account")
        print("3. Complete any pending Instagram verifications")
        print("4. Check your internet connection")
        print("5. Run the scraper in headed mode first time")

def main():
    """Main troubleshooting function"""
    if len(sys.argv) > 1 and sys.argv[1] == '--quick':
        # Quick check mode
        print("🔍 Quick troubleshooting check...")
        if check_chrome_driver() and check_chrome_browser() and test_instagram_access():
            print("✅ Basic setup looks good!")
        else:
            print("❌ Basic setup has issues. Run full check: python troubleshoot.py")
    else:
        # Full check mode
        generate_report()

if __name__ == '__main__':
    main() 