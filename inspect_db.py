import sqlite3
import pandas as pd

conn = sqlite3.connect("QuotationManager_Final.db")
cursor = conn.cursor()

tables = ["quotations", "tax_invoices", "commercial_invoices", "delivery_challans"]
for table in tables:
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"Table {table}: {count} rows")
        if count > 0:
            cursor.execute(f"SELECT date, grand_total FROM {table} LIMIT 5")
            rows = cursor.fetchall()
            for r in rows:
                print(f"  Sample: {r}")
    except Exception as e:
        print(f"Error checking {table}: {e}")

conn.close()
