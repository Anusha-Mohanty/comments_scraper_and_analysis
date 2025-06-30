from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
import time
from typing import List, Optional
import os
import random
import re
from selenium.webdriver.common.action_chains import ActionChains

def clean_comment_text(text: str) -> str:
    """Cleans comment text by removing trailing '... more' and extra whitespace."""
    # This regex looks for '...' followed by optional whitespace and 'more' at the end of the string.
    # It is case-insensitive and handles multiline strings.
    cleaned_text = re.sub(r'\s*\.\.\.\s*more$', '', text.strip(), flags=re.IGNORECASE | re.DOTALL)
    return cleaned_text.strip()

def get_comments_from_post(url: str, scrolls: int = 50, driver: Optional[webdriver.Chrome] = None) -> List[str]:
    """Scrapes only top-level comments from an Instagram post using mobile emulation and the comments icon."""
    close_driver = False
    if driver is None:
        mobile_emulation = {
            "deviceMetrics": {"width": 414, "height": 896, "pixelRatio": 3},
            "userAgent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1"
        }
        options = webdriver.ChromeOptions()
        options.add_experimental_option("mobileEmulation", mobile_emulation)
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--window-size=430,930') # Set a specific window size to better match a mobile device
        
        # Enhanced anti-detection measures
        options.add_argument('--disable-web-security')
        options.add_argument('--allow-running-insecure-content')
        options.add_argument('--disable-features=VizDisplayCompositor')
        options.add_argument('--disable-extensions')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Add random user agent rotation
        user_agents = [
            "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1"
        ]
        options.add_argument(f'--user-agent={random.choice(user_agents)}')
        
        headless_env = os.environ.get('HEADLESS', '0').lower()
        if headless_env not in ['0', 'false']:
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            print("[INFO] Running in headless mode.")
        else:
            print("[INFO] Running in headed (UI) mode.")
        
        driver = webdriver.Chrome(options=options)
        
        # Remove webdriver properties to avoid detection
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        close_driver = True

    comments = set()
    try:
        # Add random delay before navigation
        time.sleep(random.uniform(2, 5))
        
        driver.get(url)
        # On mobile, clicking comments navigates to a new page, so we don't need to do anything special here
        # if the URL already contains /comments/. If not, we will click the icon.
        if "/comments/" not in driver.current_url:
            if close_driver:
                print("Please manually handle the login in the browser window if required. Waiting for 30 seconds...")
                time.sleep(30)
            else:
                time.sleep(random.uniform(3, 6))  # Random delay for page load

            # --- UPDATED: Handle potential popups by clicking the 'Close' button ---
            try:
                close_button = WebDriverWait(driver, 7).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'svg[aria-label="Close"]'))
                )
                print("[INFO] Popup detected. Attempting to click the close button...")
                close_button.click()
                time.sleep(2) # Give time for the popup to disappear
                print("[INFO] Popup dismissed.")
            except TimeoutException:
                print("[INFO] No popup detected. Proceeding.")

            # --- DEBUG: Save a screenshot to see what the page looks like ---
            screenshot_path = "debug_screenshot.png"
            driver.save_screenshot(screenshot_path)
            print(f"[DEBUG] Screenshot saved to {screenshot_path}")

            # Click the comments icon to navigate to the comments page
            try:
                print("Looking for comments icon...")
                comment_icon = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'svg[aria-label="Comment"]'))
                )
                driver.execute_script("arguments[0].parentNode.click();", comment_icon)
                print("Clicked comments icon. Waiting for comments page to load...")
                # Wait for the URL to change, confirming navigation
                WebDriverWait(driver, 10).until(EC.url_contains("/comments/"))
                print("[INFO] Navigated to comments page.")
            except Exception as e:
                print(f"Could not find or click comments icon, or failed to navigate: {e}")
                # If it fails, maybe we are on a page without comments, so we can stop.
                return []
        else:
             print("[INFO] Already on a comments page. Proceeding to scrape.")

        # --- FINALIZED SCRAPING LOGIC (REVERTED TO PROVEN COMMENT FINDING) ---
        try:
            # 1. Wait for comment containers to be present.
            wait_selector = "div.x1lliihq"
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, wait_selector))
            )
            print("[INFO] Comment containers detected. Starting scrape and scroll process.")
            
            # 2. Main loop: Scrape first, then decide to scroll.
            max_stalls = 3
            stall_count = 0
            total_scrolls = 0

            while stall_count < max_stalls:
                last_unique_comment_count = len(comments)

                # Scrape all visible comment divs using the proven selectors.
                comment_divs = driver.find_elements(By.CSS_SELECTOR, wait_selector)

                for div in comment_divs:
                    try:
                        spans = div.find_elements(By.CSS_SELECTOR, 'span._ap3a')
                        if not spans: continue
                        target_span = spans[-1]
                        target_span.find_element(By.XPATH, './ancestor::a')
                    except NoSuchElementException:
                        comment_text = target_span.text.strip()
                        cleaned_text = clean_comment_text(comment_text)
                        if cleaned_text:
                            comments.add(cleaned_text)
                    except Exception:
                        continue
                print(f"After scraping visible content, found {len(comments)} unique comments.")

                if len(comments) == last_unique_comment_count:
                    stall_count += 1
                    print(f"[INFO] No new unique comments found. Stall count: {stall_count}/{max_stalls}")
                else:
                    stall_count = 0
                if stall_count >= max_stalls:
                    print("[INFO] Reached max stall count. Ending scroll.")
                    break

                # Programmatically find the scrollable container by its functional properties.
                container = None
                try:
                    # This JavaScript finds the most likely scrollable comments container
                    # by checking its computed style and scrollable height. This is the most
                    # robust method as it does not depend on unstable class names or IDs.
                    js_find_scroll_container = """
                        const allDivs = document.querySelectorAll('div');
                        for (let i = 0; i < allDivs.length; i++) {
                            const style = window.getComputedStyle(allDivs[i]);
                            if (style.getPropertyValue('overflow-y') === 'scroll' && allDivs[i].scrollHeight > allDivs[i].clientHeight) {
                                return allDivs[i];
                            }
                        }
                        // Fallback for different layouts: find the last scrollable div in a dialog.
                        const dialogDivs = document.querySelectorAll("div[role='dialog'] div");
                         for (let i = dialogDivs.length - 1; i >= 0; i--) {
                             if (dialogDivs[i].scrollHeight > dialogDivs[i].clientHeight) {
                                return dialogDivs[i];
                            }
                        }
                        return null; // No container found
                    """
                    container = driver.execute_script(js_find_scroll_container)

                    if container:
                        print("[INFO] Programmatically located the scrollable comments container.")
                        for _ in range(30):
                            scroll_script = """
                            arguments[0].scrollTop = arguments[0].scrollHeight;
                            var event = new Event('scroll', { bubbles: true });
                            arguments[0].dispatchEvent(event);
                            """
                            driver.execute_script(scroll_script, container)
                            time.sleep(0.7)
                    else:
                        raise Exception("Could not programmatically find a scrollable container.")

                except Exception as e:
                    print(f"[ERROR] Failed during programmatic scroll container search: {e}")
                
                total_scrolls += 1
                print(f"[INFO] Performed {total_scrolls} scroll-to-bottom cycles on detected drawer.")
                # Wait for new comments to load (dynamic wait)
                try:
                    WebDriverWait(driver, 10).until(
                        lambda d: len(d.find_elements(By.CSS_SELECTOR, wait_selector)) > len(comment_divs)
                    )
                    print("[INFO] New comments loaded after scroll.")
                except TimeoutException:
                    print("[INFO] Waited 10s after scroll, no new comments loaded.")
                time.sleep(1.5)

                # 5. Click all 'load more' buttons before scraping
                click_load_more_buttons(driver)

            print(f"Finished loading comments after {total_scrolls} scrolls.")

        except Exception as e:
            print(f"[ERROR] A critical error occurred during the scrape process: {e}")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if close_driver:
            driver.quit()

    unique_comments = list(comments)
    if unique_comments:
        # 5. Restore the simple and effective caption removal heuristic.
        unique_comments = unique_comments[1:]
    print(f"Found {len(unique_comments)} unique top-level comments (excluding caption).")
    return unique_comments

def handle_verification_challenges(driver):
    """Smarter handling of Instagram verification challenges. Only prompts for input if a VISIBLE challenge is detected."""
    print("[INFO] Checking for verification challenges...")
    challenge_detected = False

    def is_element_visible(selector):
        try:
            elements = driver.find_elements(By.XPATH, selector)
            return any(e.is_displayed() for e in elements)
        except:
            return False

    # Check for 2FA challenge
    if is_element_visible("//input[@name='verificationCode'] | //h1[contains(text(), 'Two-Factor')] | //h2[contains(text(), 'Enter Security Code')]"):
        challenge_detected = True
        print("[WARNING] 2FA challenge detected! Please complete 2FA verification manually.")
        input("Press Enter after completing 2FA verification...")
        time.sleep(3)
    
    # Check for phone/email verification
    if is_element_visible("//button[contains(text(), 'Send confirmation code')] | //h2[contains(text(), 'Verify Your Account')]"):
        challenge_detected = True
        print("[WARNING] Phone/Email verification detected! Please complete verification manually.")
        input("Press Enter after completing verification...")
        time.sleep(3)

    # Check for suspicious activity warning
    if is_element_visible("//h2[contains(text(), 'Suspicious Login')] | //button[contains(text(), 'This Was Me')]"):
        challenge_detected = True
        print("[WARNING] Suspicious activity warning detected! Please handle manually.")
        input("Press Enter after resolving the warning...")
        time.sleep(3)
    
    if not challenge_detected:
        print("[INFO] No active verification challenges detected.")
    else:
        print("[INFO] Verification check completed.")

def click_load_more_buttons(driver):
    """Clicks all visible 'View more comments', 'Load more', or 'View more' buttons on the page."""
    button_texts = ["View more comments", "Load more", "View more"]
    buttons_clicked = 0
    for text in button_texts:
        # Find all buttons or spans with the target text
        elements = driver.find_elements(By.XPATH, f"//span[contains(text(), '{text}')] | //button[contains(text(), '{text}')]" )
        for el in elements:
            try:
                if el.is_displayed() and el.is_enabled():
                    driver.execute_script("arguments[0].scrollIntoView(true);", el)
                    el.click()
                    buttons_clicked += 1
                    time.sleep(random.uniform(1, 2)) # Pause for realism and loading
            except Exception as e:
                print(f"[DEBUG] Could not click '{text}' button: {e}")
    if buttons_clicked:
        print(f"[INFO] Clicked {buttons_clicked} 'load more' buttons.")
    return buttons_clicked 
