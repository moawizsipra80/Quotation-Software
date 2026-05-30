from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import urllib.parse
import os
import re

def find_clients(area, city, category):
    # 1. Browser Setup
    options = webdriver.ChromeOptions()
    options.add_argument("--log-level=3")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
    
    print("🚀 Launching Browser for Unlimited Deep Scraping...")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    wait = WebDriverWait(driver, 20) 
    
    leads = []
    
    try:
        # --- PHASE 1: COLLECT ALL LINKS (Infinite Scroll) ---
        full_location = f"{area} {city}"
        search_term = f"{category} in {full_location}"
        
        print(f"🔍 Searching for: '{search_term}'")
        
        base_url = "https://www.google.com/maps/search/"
        query = urllib.parse.quote(search_term)
        driver.get(f"{base_url}{query}")
        
        time.sleep(5) 

        # Google Maps ka scrollable feed dhundo
        try:
            feed = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[role="feed"]')))
        except:
            return "Error: Could not find the results feed. Try checking your internet connection."

        all_links = set()
        last_count = 0
        scroll_attempts = 0

        print("🔄 Scrolling until the end of Google Maps results...")

        # Infinite Loop jab tak Google results dena band na kare
        while True:
            driver.execute_script("arguments[0].scrollBy(0, 4000);", feed)
            time.sleep(3) # Load hone ka waqt
            
            # Naye links nikalna
            link_elements = driver.find_elements(By.CSS_SELECTOR, "a[href*='/maps/place/']")
            for elem in link_elements:
                link = elem.get_attribute("href")
                if link:
                    all_links.add(link)
            
            print(f"📊 Collected {len(all_links)} links so far...")

            # --- END OF RESULTS DETECTION ---
            # 1. Check if "End of list" text appears in the source
            page_content = driver.page_source
            if "You've reached the end of the list" in page_content or "End of list" in page_content:
                print("🏁 Reached the end of Google Maps results.")
                break

            # 2. Safety Check: Agar 7 baar scroll ke baad bhi naye links nahi mile
            if len(all_links) == last_count:
                scroll_attempts += 1
                if scroll_attempts >= 7: 
                    print("🏁 No more new results found. Finalizing list.")
                    break
            else:
                scroll_attempts = 0
            
            last_count = len(all_links)

        final_links = list(all_links)
        print(f"🎯 Total Leads Found: {len(final_links)}. Starting Deep Data Extraction...")

        # --- PHASE 2: EXTRACT DATA ---
        for index, link in enumerate(final_links):
            try:
                print(f"📦 Processing {index+1}/{len(final_links)}: {link[:50]}...")
                driver.get(link)
                
                # Name load hone ka wait karein
                wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
                time.sleep(1.5) 
                
                # 1. NAME
                try: name = driver.find_element(By.TAG_NAME, "h1").text
                except: name = "N/A"

                # 2. PHONE (Enhanced Logic)
                phone = "Not Found"
                try:
                    # Method A: Data Attribute
                    phone_btn = driver.find_element(By.XPATH, '//button[contains(@data-item-id, "phone:")]')
                    phone = phone_btn.get_attribute("aria-label").replace("Phone:", "").strip()
                except:
                    # Method B: Regex Search
                    page_source = driver.page_source
                    phone_match = re.search(r'((\+92|0092|92)?\s?3\d{2}\s?\d{7})|(0\d{2,3}\s?\d{6,7})', page_source)
                    if phone_match: phone = phone_match.group(0)

                # 3. ADDRESS
                address = "Not Found"
                try:
                    addr_btn = driver.find_element(By.XPATH, '//button[contains(@data-item-id, "address")]')
                    address = addr_btn.get_attribute("aria-label").replace("Address:", "").strip()
                except:
                    pass

                if name != "N/A":
                    leads.append({
                        "Company Name": name,
                        "Phone Number": phone,
                        "Address": address,
                        "City": city,
                        "Area": area,
                        "Category": category,
                        "Maps Link": link
                    })
                    
            except Exception:
                print(f"⚠️ Error loading shop at index {index+1}. Skipping...")
                continue

        # --- PHASE 3: SAVE TO EXCEL ---
        if leads:
            df = pd.DataFrame(leads)
            downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
            # Filename mein special characters clean karein
            clean_cat = re.sub(r'[^\w\s-]', '', category)
            filename = f"{clean_cat}_{city}_FullLeads_{int(time.time())}.xlsx"
            full_path = os.path.join(downloads_folder, filename)
            
            df.to_excel(full_path, index=False)
            return f"✅ Success! {len(leads)} leads saved at: {full_path}"
        
        return "❌ No data could be extracted."

    except Exception as e:
        return f"Error: {str(e)}"
    finally:
        driver.quit()

if __name__ == "__main__":
    print("--- Google Maps Deep Scraper ---")
    u_area = input("Area (e.g. Gulberg): ")
    u_city = input("City (e.g. Lahore): ")
    u_cat = input("Category (e.g. Software House): ")
    
    result = find_clients(u_area, u_city, u_cat)
    print(result)