from google import genai

client = genai.Client(api_key="AIzaSyC96RgLZEOIO0sIbu3Ijs1uoo6yY4sA9wE")

print("Fetching list from Google... (Please wait)")

try:
    for m in client.models.list():
        print(f"- {m.name}")
        
except Exception as e:
    print(f"Error: {e}")

print("\nDone! Copy one of the names above.")