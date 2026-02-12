import sqlite3
conn = sqlite3.connect('QuotationManager_Final.db')
cursor = conn.cursor()
print("--- USERS ---")
cursor.execute("SELECT id, username FROM users")
print(cursor.fetchall())

print("\n--- QUOTATIONS ---")
cursor.execute("SELECT id, client_name, grand_total, created_by FROM quotations")
rows = cursor.fetchall()
for row in rows:
    print(row)

conn.close()
