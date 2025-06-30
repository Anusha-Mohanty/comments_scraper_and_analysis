import os
import re
import json
from collections import defaultdict

from config import *
from scrapers.instagram_scraper import get_comments_from_post, handle_verification_challenges
from utils.sheet_handler import get_gspread_client, get_all_tabs, get_all_posts, update_status_for_post
from utils.file_utils import sanitize_filename

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import random
import glob

COOKIES_FILE = 'insta_cookies.json'

def save_cookies(driver, path=COOKIES_FILE):
    cookies = driver.get_cookies()
    with open(path, 'w') as f:
        json.dump(cookies, f)
    print(f"Cookies saved to {path}")

def load_cookies(driver, path=COOKIES_FILE):
    if not os.path.exists(path):
        return False
    with open(path, 'r') as f:
        cookies = json.load(f)
    for cookie in cookies:
        if 'expiry' in cookie:
            cookie['expiry'] = int(cookie['expiry'])
        try:
            driver.add_cookie(cookie)
        except Exception:
            continue
    print(f"Cookies loaded from {path}")
    return True

def setup_driver():
    """Setup Chrome driver with enhanced anti-detection measures"""
    print("Launching Chrome browser for Selenium (mobile emulation)...")
    mobile_emulation = {
        "deviceMetrics": {"width": 414, "height": 896, "pixelRatio": 3},
        "userAgent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1"
    }
    options = webdriver.ChromeOptions()
    options.add_experimental_option("mobileEmulation", mobile_emulation)
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--window-size=430,930')
    
    # Enhanced anti-detection measures
    options.add_argument('--disable-web-security')
    options.add_argument('--allow-running-insecure-content')
    options.add_argument('--disable-features=VizDisplayCompositor')
    options.add_argument('--disable-extensions')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    user_agents = [
        "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1"
    ]
    options.add_argument(f'--user-agent={random.choice(user_agents)}')
    
    headless_env = os.environ.get('HEADLESS', '0').lower()
    if headless_env in ['1', 'true', 'yes']:
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        print("[INFO] Running in headless mode.")
    else:
        print("[INFO] Running in headed (UI) mode.")
    
    try:
        driver = webdriver.Chrome(options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        print("Chrome browser launched successfully.")
        return driver
    except Exception as e:
        print(f"Failed to launch Chrome browser: {e}")
        return None

def handle_common_popups(driver):
    """Handles common pop-ups that appear after login."""
    popups = {
        "Save login info": "//div[@role='dialog']//*[text()='Not now' or text()='Not Now']",
        "Turn on notifications": "//div[@role='dialog']//button[text()='Not Now']"
    }
    for desc, selector in popups.items():
        try:
            button = WebDriverWait(driver, 7).until(EC.element_to_be_clickable((By.XPATH, selector)))
            print(f"[INFO] '{desc}' popup detected. Clicking 'Not now'...")
            button.click()
            time.sleep(2)
            print(f"[INFO] Popup dismissed.")
        except TimeoutException:
            pass
        except Exception as e:
            print(f"[WARNING] Could not dismiss '{desc}' popup: {e}")

def authenticate_session(driver):
    """Handle authentication, popups, and verification challenges."""
    print("Setting up Instagram session...")
    driver.get("https://www.instagram.com/")
    time.sleep(random.uniform(2, 4))
    
    if not load_cookies(driver):
        print("\n--- MANUAL LOGIN REQUIRED ---")
        print("No saved cookies found. Please complete the login in the browser window.")
        input("--> After you have logged in, press Enter here...")
        handle_common_popups(driver)
        handle_verification_challenges(driver)
        save_cookies(driver)
    else:
        print("Logged in using saved cookies. Refreshing session...")
        driver.refresh()
        time.sleep(random.uniform(3, 5))
        handle_common_popups(driver)
        handle_verification_challenges(driver)
    print("Authentication setup completed.")

def main():
    print("Starting Instagram comment scraping and sentiment analysis...")

    client = get_gspread_client()
    if not client:
        return
        
    tabs = get_all_tabs(client)
    if not tabs:
        print("No tabs found in the Google Sheet. Exiting.")
        return

    driver = setup_driver()
    if not driver:
        return

    try:
        authenticate_session(driver)

        for sheet in tabs:
            brand_name = sheet.title
            print(f"\n--- Processing Brand/Campaign: {brand_name} ---")

            posts_to_scrape = get_all_posts(sheet)
            if not posts_to_scrape:
                print(f"No posts found for '{brand_name}' in the sheet.")
                continue

            all_brand_comments = []
            data_dir = "social_sentiment_analyzer/data"
            os.makedirs(data_dir, exist_ok=True)

            for i, post in enumerate(posts_to_scrape):
                url = post.get(URL_COLUMN)
                if not url:
                    continue

                print(f"\nScraping comments from: {url}")
                try:
                    comments = get_comments_from_post(url, driver=driver)
                    all_brand_comments.extend(comments)
                    
                    # Save comments for this post to a unique file
                    sanitized_url = sanitize_filename(url)
                    comments_filename = f"comments_{sanitize_filename(brand_name)}_{sanitized_url}.json"
                    comments_filepath = os.path.join(data_dir, comments_filename)
                    with open(comments_filepath, 'w', encoding='utf-8') as f:
                        json.dump(comments, f, ensure_ascii=False, indent=4)
                    
                    print(f"Saved {len(comments)} comments to {comments_filepath}")
                    update_status_for_post(sheet, i + 2, "Success", len(comments), comments_filepath)

                except Exception as e:
                    print(f"Failed to scrape {url}: {e}")
                    update_status_for_post(sheet, i + 2, f"Error: {e}")
                
                # Add a random delay between scraping posts to avoid rate-limiting
                if i < len(posts_to_scrape) - 1:
                    delay = random.uniform(15, 30)
                    print(f"Waiting for {delay:.2f} seconds before next post...")
                    time.sleep(delay)

            if not all_brand_comments:
                print(f"No comments collected for brand '{brand_name}'. Skipping report generation.")
                continue

            # --- Save all comments for the brand to a single file ---
            all_comments_filename = f"{sanitize_filename(brand_name)}_all_comments.json"
            all_comments_filepath = os.path.join(data_dir, all_comments_filename)
            with open(all_comments_filepath, 'w', encoding='utf-8') as f:
                json.dump(all_brand_comments, f, ensure_ascii=False, indent=4)
            print(f"Saved all {len(all_brand_comments)} comments for '{brand_name}' to {all_comments_filepath}")

    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
    finally:
        if driver:
            driver.quit()
        print("\nScraping complete. All comments have been saved.")
        print("To analyze the comments, run the API and send a request to the /analyze endpoint for each brand.")

if __name__ == "__main__":
    main()
