from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import os
import random
import urllib.parse
from selenium.webdriver.common.action_chains import ActionChains

def send_messages(file_path, message_text, attachment_path=None):
    # 1. File Read & Validation
    try:
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)
        print(f"✅ File Loaded. Total Rows: {len(df)}")
    except Exception as e:
        return f"Error reading file: {e}"

    # --- SMART AUTO-DETECTION ---
    phone_col = None
    priority_keywords = ['phone', 'mobile', 'contact', 'whatsapp', 'cell', 'number','phone number','mobile number', 'contact number' , 'cell number' , 'phone no' ,'mobile no','contact no', 'cell no','whatsapp number','whatsapp no','whatsapp_no','phone_no','contact_no','mobile_no','cell_no']
    
    # Strip spaces from column names
    df.columns = [str(c).strip() for c in df.columns]
    
    # Priority 1: Search by Header Keywords
    for col in df.columns:
        if any(key in col.lower() for key in priority_keywords):
            phone_col = col
            break
            
    # Priority 2: Data Scan (If Keywords Not Found)
    if not phone_col:
        for col in df.columns:
            valid_samples = 0
            # Scan first 5 rows
            for val in df[col].head(5):
                cleaned = "".join(filter(str.isdigit, str(val)))
                if 10 <= len(cleaned) <= 11: 
                    valid_samples += 1
            
            if valid_samples >= 2: # Significant match
                phone_col = col
                break
                
    if not phone_col:
        return "Error: Could not detect a 'Phone Number' column. Please name it correctly or provide valid data."
    
    print(f"🎯 Auto-detected '{phone_col}' as your Phone Number column.")

    # 2. Browser Setup
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
    options.add_experimental_option("detach", True) 

    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        wait = WebDriverWait(driver, 45)

        print("Opening WhatsApp Web...")
        driver.get("https://web.whatsapp.com")
        
        try:
            print("Please Scan QR Code within 60 seconds...")
            # Wait for the search box (indicating main interface is loaded)
            wait.until(EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]')))
            
            # Extra wait to ensure "Loading Chats" is gone and interface is stable
            print("✅ Login Detected. Waiting for chats to sync...")
            time.sleep(10) 
            
        except:
            print("⚠️ Timeout: Assuming logged in or session active.")
            time.sleep(5)

        sent_count = 0
        failed_count = 0
        
        # 4. Main Loop
        for index, row in df.iterrows():
            try:
                raw_number = str(row[phone_col]).strip()
                if raw_number.endswith('.0'): raw_number = raw_number[:-2]
                
                name = str(row.get('Company Name', 'Client'))
                
                # --- EXTRACT DIGITS ONLY ---
                number = "".join(filter(str.isdigit, raw_number))
                
                if len(number) < 10:
                    print(f"Skipping Invalid Number: {name} ({raw_number})")
                    failed_count += 1
                    continue

                # Pakistan specific normalization (03xx -> 923xx)
                if number.startswith("03") and len(number) == 11: 
                    number = "92" + number[1:]
                elif len(number) == 10 and not number.startswith("92"): 
                    number = "92" + number
                    
                print(f"[{index+1}/{len(df)}] Sending to: {name} ({number})...")

                # --- OPEN CHAT ---
                encoded_msg = urllib.parse.quote(message_text)
                link = f"https://web.whatsapp.com/send?phone={number}&text={encoded_msg}"
                driver.get(link)
                
                try:
                    WebDriverWait(driver, 5).until(EC.alert_is_present())
                    driver.switch_to.alert.accept()
                except: pass

                # --- CHECK FOR INVALID NUMBER OR CHAT LOAD ---
                try:
                    # We wait for EITHER the Input Box OR the Invalid Number Popup
                    # Since we can't easily wait for "one of two" with simple EC, we split the logic.
                    
                    # 1. Quick check for Invalid Number Popup (approx 5-10s wait)
                    try:
                        err_popup = WebDriverWait(driver, 8).until(
                            EC.presence_of_element_located((By.XPATH, '//div[contains(text(), "phone number shared via url is invalid")]'))
                        )
                        if err_popup:
                            print(f"   -> ❌ Skipped: Invalid WhatsApp Number.")
                            failed_count += 1
                            # Create an action chain to close the popup if there's an OK button, or just continue which loads next URL
                            # Usually hitting ESC closes it
                            try:
                                ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                            except: pass
                            
                            time.sleep(2)
                            continue # Skip to next number
                    except:
                        # No error popup found, proceed to normal chat loading
                        pass

                    # 2. Wait for Chat Input
                    input_box = wait.until(
                        EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]'))
                    )
                    time.sleep(2) # Stabilize
                    
                    # Safety check: if box is empty, type message manually
                    current_text = input_box.text.strip()
                    if not current_text:
                        print("   -> ⌨️ Manual Typing (URL fail)")
                        # Clear any existing text first (safety)
                        input_box.send_keys(Keys.CONTROL + "a")
                        input_box.send_keys(Keys.BACKSPACE)
                        input_box.send_keys(message_text)
                        time.sleep(1)

                    input_box.send_keys(Keys.ENTER)
                    print(f"   -> ✅ Text Sent")
                    time.sleep(2) 

                    # --- ATTACHMENT LOGIC ---
                    if attachment_path and os.path.exists(attachment_path):
                        try:
                            print("   -> 📎 Starting attachment process...")
                            time.sleep(2)

                            # 1. Click Attach Button (Clip or Plus) - Essential for DOM to be ready
                            try:
                                # Common selectors for Attach button (Clip or Plus icon)
                                attach_xpath = '//div[@title="Attach"] | //span[@data-icon="clip"] | //span[@data-icon="plus"]'
                                attach_btn = wait.until(EC.element_to_be_clickable((By.XPATH, attach_xpath)))
                                attach_btn.click()
                                time.sleep(1.5) # Wait for menu
                            except Exception as btn_err:
                                print(f"   -> ⚠️ Warning: Attach button click failed ({btn_err}). Trying direct input...")

                            # 2. Identify File Type
                            _, file_extension = os.path.splitext(attachment_path)
                            ext = file_extension.lower()
                            is_image = ext in ['.jpg', '.jpeg', '.png', '.mp4', '.3gp', '.gif']
                            
                            # 3. Find Hidden Input
                            if is_image:
                                type_msg = "Image/Video"
                                # Try specific input for images (using contains for robustness)
                                input_xpath = '//input[contains(@accept, "image")]'
                            else:
                                type_msg = "Document"
                                input_xpath = '//input[contains(@accept, "*")]'

                            try:
                                # Try specific input first
                                file_input = driver.find_element(By.XPATH, input_xpath)
                            except:
                                # Fallback to generic file input
                                file_input = driver.find_element(By.XPATH, '//input[@type="file"]')

                            # Send Absolute Path
                            file_input.send_keys(os.path.abspath(attachment_path))
                            
                            # 4. Wait for Preview & Click Send
                            print(f"   -> 📎 Uploaded. Waiting for preview...")
                            
                            # Wait for send button (Green circle with plane)
                            send_btn_xpath = '//span[@data-icon="send"]'
                            
                            # Wait longer for images to process
                            send_doc_btn = wait.until(EC.element_to_be_clickable((By.XPATH, send_btn_xpath)))
                            time.sleep(1) # Extra buffer
                            send_doc_btn.click()
                            
                            print(f"   -> 📎 {type_msg} Sent Successfully")
                            time.sleep(3) # Wait for transfer
                            
                        except Exception as file_err:
                            print(f"   -> ❌ Attachment Error: {file_err}")
                            # Close attachment menu if stuck open
                            try:
                                ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                            except: pass

                    sent_count += 1
                    
                    # --- RANDOMIZED DELAY (HUMAN BEHAVIOR) ---
                    # 15 to 25 seconds is a safe "human" window
                    delay = random.randint(11, 15) 
                    print(f"   -> Humanizing: Waiting {delay}s...")
                    time.sleep(delay)

                except Exception as e:
                    print(f"   -> ❌ FAILED: Invalid Number or Timeout.")
                    failed_count += 1
                    continue

            except Exception as e:
                print(f"Loop Error: {e}")
                failed_count += 1

        print("🎉 Process Complete!")
        return f"Campaign Finished!\n✅ Sent: {sent_count}\n❌ Failed: {failed_count}"

    except Exception as main_e:
        return f"Critical Error: {main_e}"