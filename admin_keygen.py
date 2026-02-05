import hashlib
import subprocess
import hashlib
# --- SECRET CODE (Ye sirf aapko pata ho, kisi aur ko nahi) ---
SECRET_SALT = "ODM-ONLINE'S_QUOTATION_SYSTEM_2026_SECRET"

def generate_key(machine_id):
    # Machine ID + Secret Code ko mix kar k Key banayen
    raw_data = f"{machine_id.strip()}{SECRET_SALT}"
    
    # Isay Hash (Encrypt) karein taake koi reverse na kar sake
    hashed = hashlib.sha256(raw_data.encode()).hexdigest()
    
    # Pehle 16 characters ko Key bana lein (ABCD-1234-...)
    key = hashed[:16].upper()
    
    # 4-4 k groups main dikhayen taake parhne main asani ho
    formatted_key = f"{key[0:4]}-{key[4:8]}-{key[8:12]}-{key[12:16]}"
    return formatted_key

print("--- ODM-ONLINE'SSOFTWARE KEY GENERATOR ---")
while True:
    u_id = input("\nEnter User's Machine ID: ")
    if u_id:
        print(f"🔑 LICENSE KEY: {generate_key(u_id)}")
        print("-" * 30)