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

    df.columns = [c.strip() for c in df.columns]
    if 'Phone Number' not in df.columns:
        return "Error: Excel file must have 'Phone Number' column!"

    # 2. Browser Setup
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-infobars")
    options.add_experimental_option("detach", True) 

    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        wait = WebDriverWait(driver, 35)

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
                raw_number = str(row['Phone Number'])
                name = str(row.get('Company Name', 'Client'))
                
                if "Found" in raw_number or len(raw_number) < 5:
                    print(f"Skipping Invalid Number: {name}")
                    failed_count += 1
                    continue

                number = raw_number.replace(".0", "").replace("-", "").replace(" ", "").replace("+", "")
                if number.startswith("03"): number = "92" + number[1:]
                elif not number.startswith("92"): number = "92" + number
                    
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
                    input_box = wait.until(
                        EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]'))
                    )
                    time.sleep(2) 
                    input_box.send_keys(Keys.ENTER)
                    print(f"   -> ✅ Text Sent")
                    time.sleep(1) 

                    # --- ATTACHMENT LOGIC (IMAGE vs DOCUMENT) ---
                    if attachment_path and os.path.exists(attachment_path):
                        try:
                            # 1. Click Clip Icon
                            attach_btn = driver.find_element(By.CSS_SELECTOR, 'div[title="Attach"]')
                            attach_btn.click()
                            time.sleep(1)
                            
                            # 2. Check File Type
                            filename, file_extension = os.path.splitext(attachment_path)
                            ext = file_extension.lower()
                            
                            # Decide Input Type
                            if ext in ['.jpg', '.jpeg', '.png', '.mp4', '.3gp']:
                                # IMAGE/VIDEO INPUT
                                file_input = driver.find_element(By.CSS_SELECTOR, 'input[accept="image/*,video/mp4,video/3gpp,video/quicktime"]')
                                type_msg = "Image"
                            else:
                                # DOCUMENT INPUT (PDF, DOCX, XLSX etc)
                                # Usually input[accept='*'] or the default file input
                                file_input = driver.find_element(By.CSS_SELECTOR, 'input[accept="*"]')
                                type_msg = "Document"

                            # 3. Send Path
                            file_input.send_keys(os.path.abspath(attachment_path))
                            
                            # 4. Wait for Preview & Send
                            time.sleep(2)
                            send_doc_btn = wait.until(
                                EC.element_to_be_clickable((By.CSS_SELECTOR, 'span[data-icon="send"]'))
                            )
                            send_doc_btn.click()
                            print(f"   -> 📎 {type_msg} Sent")
                            time.sleep(5) # Wait for upload
                            
                        except Exception as file_err:
                            print(f"   -> ❌ Attachment Error: {file_err}")

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