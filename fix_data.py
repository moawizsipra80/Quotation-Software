import sqlite3
import json

def fix_revenue():
    conn = sqlite3.connect("QuotationManager_Final.db")
    cursor = conn.cursor()
    tables = ["quotations", "tax_invoices", "commercial_invoices"]
    fixed_count = 0
    
    for tbl in tables:
        print(f"Checking table: {tbl}")
        cursor.execute(f"SELECT id, full_data FROM {tbl}")
        rows = cursor.fetchall()
        for rid, fd in rows:
            if fd:
                try:
                    data = json.loads(fd)
                    items = data.get("items", [])
                    # Sum up item totals
                    gt = sum(float(i.get('total', 0)) for i in items)
                    
                    if gt > 0:
                        cursor.execute(f"UPDATE {tbl} SET grand_total=? WHERE id=?", (gt, rid))
                        print(f"  Fixed ID {rid}: Total settled to {gt}")
                        fixed_count += 1
                except Exception as e:
                    print(f"  Error parsing ID {rid}: {e}")
    
    conn.commit()
    conn.close()
    print(f"Success! Fixed {fixed_count} records.")

if __name__ == "__main__":
    fix_revenue()
