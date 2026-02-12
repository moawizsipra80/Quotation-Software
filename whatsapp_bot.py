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
    priority_keywords = ['phone', 'mobile', 'contact', 'whatsapp', 'cell', 'number']
    
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
        
        # 3. Login Wait
        try:
            print("Please Scan QR Code within 60 seconds...")
            wait.until(EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]')))
            print("✅ Login Successful!")
            time.sleep(2)
        except:
            print("⚠️ Timeout: Assuming logged in.")
            time.sleep(3)

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

                # --- WAIT FOR LOAD & SEND TEXT ---
                try:
                    # Target the main chat input
                    input_box = wait.until(
                        EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]'))
                    )
                    time.sleep(3) # Wait for URL text to populate
                    
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
                            # 1. Identify File Type
                            _, file_extension = os.path.splitext(attachment_path)
                            ext = file_extension.lower()
                            is_image = ext in ['.jpg', '.jpeg', '.png', '.mp4', '.3gp']
                            
                            # 2. Find Hidden Input (More reliable than clicking Attach button)
                            if is_image:
                                input_xpath = '//input[@accept="image/*,video/mp4,video/3gpp,video/quicktime"]'
                                type_msg = "Image/Video"
                            else:
                                input_xpath = '//input[@accept="*"]'
                                type_msg = "Document"

                            file_input = wait.until(EC.presence_of_element_located((By.XPATH, input_xpath)))
                            file_input.send_keys(os.path.abspath(attachment_path))
                            
                            # 3. Wait for Preview & Click Send
                            time.sleep(3) # Wait for preview to render
                            send_btn_xpath = '//span[@data-icon="send"]'
                            send_doc_btn = wait.until(EC.element_to_be_clickable((By.XPATH, send_btn_xpath)))
                            send_doc_btn.click()
                            
                            print(f"   -> 📎 {type_msg} Sent")
                            time.sleep(3) # Wait for transfer
                            
                        except Exception as file_err:
                            print(f"   -> ❌ Attachment Error: {file_err}. (Reason: WhatsApp UI might have changed or file input was hidden)")

                    sent_count += 1
                    
                    delay = random.randint(8, 15)
                    print(f"   -> Waiting {delay}s...")
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