# Instagram Comment Scraper Setup Guide

## Overview
This guide will help you set up the Instagram comment scraper with proper authentication and anti-detection measures to avoid proxy and 2FA issues.

## Prerequisites
- Python 3.7+
- Chrome browser installed
- ChromeDriver compatible with your Chrome version
- Instagram account with 2FA enabled (recommended)

## Installation

1. **Clone or download the project**
2. **Install dependencies:**
   ```bash
    pip install -r requirements.txt
    ```

3. **Set up Google Sheets integration:**
   - Create a Google Cloud Project
   - Enable Google Sheets API
   - Download credentials JSON file as `creds.json`
   - Place it in the project root

## Configuration

### 1. Google Sheets Setup
- Update `config.py` with your Google Sheet ID
- Ensure your sheet has the required columns:
  - `Post Urls`: Instagram post URLs to scrape
  - `Status`: Current status of scraping
  - `Comments Count`: Number of comments found
  - `Comments Link`: Path to saved comments file

### 2. Instagram Account Setup

#### **IMPORTANT: 2FA Setup (Required to Prevent Proxy Issues)**

1. **Enable 2FA on your Instagram account:**
   - Go to Instagram Settings → Security → Two-Factor Authentication
   - Enable "Text Message" or "Authentication App"
   - Save backup codes

2. **Use a verified phone number:**
   - Ensure your Instagram account has a verified phone number
   - This helps prevent suspicious activity flags

3. **Account verification:**
   - Complete any pending account verifications
   - Add profile picture and bio if not already done

## Running the Scraper

### First Time Setup

1. **Run the scraper:**
   ```bash
    python main.py
   ```

2. **Handle initial authentication:**
   - A Chrome browser will open
   - Log in to Instagram manually
   - **If 2FA is required, complete it manually**
   - Wait for the script to detect and handle verification challenges
   - Press Enter when you see your Instagram feed

3. **Cookies will be saved for future use**

### Subsequent Runs

- The scraper will use saved cookies
- If cookies expire, you'll be prompted to log in again
- 2FA challenges will be handled automatically with manual intervention

## Anti-Detection Features

The updated scraper includes several features to prevent proxy and detection issues:

### 1. **Enhanced Browser Configuration**
- Mobile emulation to mimic mobile devices
- Random user agent rotation
- Disabled automation flags
- WebDriver property masking

### 2. **Human-like Behavior**
- Random delays between actions
- Natural scrolling patterns
- Varied timing for interactions

### 3. **Verification Challenge Handling**
- Automatic detection of 2FA prompts
- Phone/email verification detection
- Suspicious activity warning handling
- Manual intervention prompts

### 4. **Session Management**
- Cookie persistence
- Automatic session renewal
- Graceful handling of expired sessions

## Troubleshooting

### Common Issues and Solutions

#### 1. **Proxy/2FA Issues**
**Problem:** Instagram blocks access or requires 2FA
**Solution:**
- Ensure 2FA is enabled on your account
- Use a verified phone number
- Complete manual verification when prompted
- Wait for the script to detect and handle challenges

#### 2. **"Suspicious Activity" Warnings**
**Problem:** Instagram flags the account for suspicious activity
**Solution:**
- Complete the security check manually
- Verify your phone number/email
- Add profile information if missing
- Wait 24-48 hours before retrying

#### 3. **Rate Limiting**
**Problem:** Too many requests too quickly
**Solution:**
- The scraper now includes random delays between posts
- Reduce `SCROLL_COUNT` in `config.py` if needed
- Run during off-peak hours

#### 4. **Login Issues**
**Problem:** Can't log in or cookies don't work
**Solution:**
- Clear browser cache and cookies
- Try logging in manually first
- Ensure no CAPTCHA or verification is pending
- Check if account is temporarily restricted

#### 5. **Chrome/ChromeDriver Issues**
**Problem:** Browser won't start or crashes
**Solution:**
- Update Chrome to latest version
- Download matching ChromeDriver version
- Ensure ChromeDriver is in PATH
- Try running in headed mode (not headless)

### Manual Verification Steps

When the scraper detects verification challenges:

1. **2FA Challenge:**
   - Enter the verification code from your phone/app
   - Click "Confirm" or "Verify"
   - Wait for the page to load completely

2. **Phone/Email Verification:**
   - Choose your preferred verification method
   - Enter the code sent to your phone/email
   - Complete any additional security steps

3. **Suspicious Activity Warning:**
   - Click "This Was Me" if it was you
   - Complete any security questions
   - Verify your identity as prompted

4. **After completing verification:**
   - Press Enter in the terminal to continue
   - The scraper will resume automatically

## Best Practices

### 1. **Account Management**
- Use a dedicated Instagram account for scraping
- Keep the account active with regular posts
- Maintain a good follower/following ratio
- Avoid following/unfollowing too quickly

### 2. **Scraping Strategy**
- Don't scrape too many posts at once
- Use reasonable delays between sessions
- Avoid scraping during peak hours
- Monitor for any account restrictions

### 3. **Technical Setup**
- Keep Chrome and ChromeDriver updated
- Use a stable internet connection
- Run on a machine with sufficient resources
- Monitor system resources during scraping

### 4. **Data Management**
- Regularly backup scraped data
- Clean up old comment files
- Monitor disk space usage
- Validate scraped data quality

## Monitoring and Maintenance

### 1. **Check Account Status**
- Regularly log in to Instagram manually
- Check for any account warnings
- Monitor for unusual activity notifications

### 2. **Update Dependencies**
- Keep Python packages updated
- Update Chrome and ChromeDriver regularly
- Monitor for Instagram interface changes

### 3. **Data Quality**
- Verify scraped comment counts
- Check for missing or incomplete data
- Validate comment content quality

## Support

If you encounter persistent issues:

1. **Check the debug screenshot:** `debug_screenshot.png` shows what the scraper sees
2. **Review console output:** Look for specific error messages
3. **Verify Instagram changes:** Instagram may have updated their interface
4. **Contact support:** Provide specific error messages and steps to reproduce

## Security Notes

- Never share your Instagram credentials
- Keep your `creds.json` file secure
- Don't commit sensitive files to version control
- Use environment variables for sensitive configuration
- Regularly rotate passwords and 2FA codes

---

**Remember:** Instagram's terms of service should be reviewed before using this tool. This scraper is for educational and research purposes only. 