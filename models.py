from google import genai

# آپ کی API Key
client = genai.Client(api_key="AIzaSyC96RgLZEOIO0sIbu3Ijs1uoo6yY4sA9wE")

print("Fetching list from Google... (Please wait)")

try:
    # سادہ لسٹ پرنٹ کریں
    for m in client.models.list():
        # ماڈل کا اصل نام (ID) دکھائیں
        print(f"- {m.name}")
        
except Exception as e:
    print(f"Error: {e}")

print("\nDone! Copy one of the names above.")