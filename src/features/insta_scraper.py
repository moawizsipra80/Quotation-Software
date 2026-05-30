import time
import random
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

# --- GLOBAL VARIABLES ---
driver = None
wait = None

def start_driver():
    """Browser launch karega"""
    global driver, wait
    
    # Agar purana session zinda hai to wahi use karein
    if driver is not None:
        try:
            driver.current_url 
            return # Sab theek hai
        except:
            driver = None # Dead session, naya banayenge

    print("🚀 Launching Browser...")
    options = webdriver.ChromeOptions()
    options.add_argument("--log-level=3")
    options.add_argument("--disable-notifications")
    options.add_argument("--start-maximized")
    
    # Detach option zaroori hai taake browser band na ho
    options.add_experimental_option("detach", True)
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 20)

def open_login_page():
    """Login Page Kholega"""
    global driver
    if not driver: start_driver()
    try:
        driver.get("https://www.instagram.com/accounts/login/")
    except:
        # Agar browser crash ho gaya ho to restart karein
        driver = None
        start_driver()
        driver.get("https://www.instagram.com/accounts/login/")

def get_active_users(target_handle, limit=30):
    """
    Target account ke 1st/2nd/3rd post se likers nikalta hai.

    Returns (usernames, is_private_flag).
    """
    global driver, wait
    users = []
    is_private = False

    if driver is None:
        start_driver()

    try:
        url = f"https://www.instagram.com/{target_handle}/"
        print(f"🚀 Going to Target: {url}")
        driver.get(url)
        time.sleep(6)

        # --- PRIVATE ACCOUNT CHECK ---
        try:
            driver.find_element(
                By.XPATH, "//*[contains(text(), 'This account is private')]"
            )
            print("❌ Account private hai, scraping possible nahi.")
            is_private = True
            return [], is_private
        except Exception:
            pass

        # --- POSTS LIST (Try 1st, 2nd, 3rd) ---
        posts = driver.find_elements(By.XPATH, "//article//a[contains(@href, '/p/')]")
        posts = posts[:3]

        if not posts:
            print("❌ Koi posts nahi mili.")
            return [], is_private

        for idx, post in enumerate(posts, start=1):
            print(f"▶ Trying post #{idx} ...")
            try:
                post.click()
                time.sleep(4)
            except Exception:
                print(f"   ⚠ Post #{idx} open nahi ho saki.")
                continue

            # Try to open likes list for this post
            print("   🔎 Opening Likes List...")
            likes_btn = None
            try:
                likes_btn = driver.find_element(
                    By.XPATH, "//a[contains(@href, '/liked_by/')]"
                )
            except Exception:
                try:
                    likes_btn = driver.find_element(
                        By.XPATH, "//span[contains(text(), 'likes')]"
                    )
                except Exception:
                    likes_btn = None

            if not likes_btn:
                print("   ❌ Likes hidden ya button nahi mila, next post try karte hain.")
                driver.back()
                time.sleep(3)
                continue

            likes_btn.click()
            time.sleep(4)

            # Scroll & scrape inside modal
            scroll_count = 0
            while len(users) < limit and scroll_count < 15:
                elements = driver.find_elements(
                    By.XPATH, "//div[@role='dialog']//a[@title]"
                )

                for elem in elements:
                    u = elem.get_attribute("title")
                    if u and u not in users and u != target_handle:
                        users.append(u)
                        if len(users) >= limit:
                            break

                if not elements:
                    break

                try:
                    driver.execute_script(
                        "arguments[0].scrollIntoView();", elements[-1]
                    )
                    time.sleep(2)
                except Exception:
                    break

                scroll_count += 1

            # Agar is post se kuch users mil gaye to doosri posts ki zaroorat nahi
            if users:
                break

            # Modal/ post se back aajayein
            driver.back()
            time.sleep(2)

    except Exception as e:
        print(f"Error while fetching active users: {e}")

    print(f"✅ Extracted {len(users)} active users.")
    return users, is_private

def send_dm_with_image(username, message, image_path=None):
    """User ko DM aur Image bhejega"""
    global driver
    status = "Failed"
    
    try:
        print(f"👉 Going to user: {username}")
        driver.get(f"https://www.instagram.com/{username}/")
        time.sleep(random.randint(5, 8))

        # Message Button Click
        try:
            msg_btn = driver.find_element(By.XPATH, "//div[text()='Message']")
            msg_btn.click()
            time.sleep(8) 
            
            try: 
                driver.find_element(By.XPATH, "//button[text()='Not Now']").click()
                time.sleep(2)
            except: pass

            # IMAGE
            if image_path and os.path.exists(image_path):
                print("   📸 Uploading Image...")
                try:
                    file_input = driver.find_element(By.XPATH, '//input[@type="file"]')
                    file_input.send_keys(image_path)
                    time.sleep(6)
                except: pass

            # TEXT
            print(f"   💬 Typing Message...")
            try:
                text_box = driver.find_element(By.XPATH, "//div[@contenteditable='true']")
                text_box.click()
                for char in message:
                    text_box.send_keys(char)
                    time.sleep(random.uniform(0.05, 0.2))
                time.sleep(2)
                text_box.send_keys(Keys.ENTER)
                status = "Sent"
                print("   ✅ Message Sent!")
            except: pass

        except:
            status = "Skipped"

    except Exception as e:
        print(f"Error processing {username}: {e}")

    return status

def close_driver():
    global driver
    if driver:
        try: driver.quit()
        except: pass
        driver = None