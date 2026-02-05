import pandas as pd
import datetime as _dt
import sqlite3

def _safe_amount(val):
    try:
        # Paison mein comma (,) handle karne ke liye
        if isinstance(val, str):
            val = val.replace(',', '')
        return float(val) if val is not None else 0.0
    except Exception:
        return 0.0

def get_analytics_data(conn):
    """
    Dashboard ke liye Monthly Bar Chart ka data taiyar karta hai (2026 Year focus).
    """
    try:
        cursor = conn.cursor()
        data = []

        # Sab tables ki list aur unke possible column names
        # Hum check karenge ke table mein 'date' hai ya 'date_created'
        config = {
            "quotations": {"date": ["date", "created_at"], "amount": ["grand_total"]},
            "tax_invoices": {"date": ["date", "date_created"], "amount": ["grand_total", "total_amount"]},
            "commercial_invoices": {"date": ["date", "date_created"], "amount": ["grand_total", "total_amount"]}
        }

        for table, cols in config.items():
            try:
                # Pehle check karein ke table exist karti hai
                cursor.execute(f"PRAGMA table_info({table})")
                existing_cols = [c[1] for c in cursor.fetchall()]
                if not existing_cols: continue

                # Sahi column ka intekhab (Date aur Amount ke liye)
                d_col = next((c for c in cols['date'] if c in existing_cols), None)
                a_col = next((c for c in cols['amount'] if c in existing_cols), None)

                if d_col and a_col:
                    cursor.execute(f"SELECT {d_col}, {a_col} FROM {table} WHERE {d_col} IS NOT NULL")
                    rows = cursor.fetchall()
                    for d, amt in rows:
                        if d:
                            data.append((d, _safe_amount(amt), table))
            except Exception as tbl_err:
                print(f"Error fetching from {table}: {tbl_err}")

        if not data:
            print("Analytics: No data found in any table.")
            return None

        # DataFrame Processing
        df = pd.DataFrame(data, columns=["date", "grand_total", "source"])
        
        # Date conversion (Robust parsing)
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.dropna(subset=["date"])

        # Sirf Mojooda Saal (Current Year) ka data dikhayen
        current_year = _dt.date.today().year
        df = df[df["date"].dt.year == current_year]
        
        if df.empty:
            print(f"Analytics: No data for the year {current_year}")
            return None

        # Monthly Grouping
        df["month"] = df["date"].dt.strftime("%b") # e.g. 'Jan', 'Feb'
        
        # Pivot Table for Bar Chart (Stacked or Grouped)
        pivot = df.pivot_table(
            index="month",
            columns="source",
            values="grand_total",
            aggfunc="sum",
            fill_value=0.0
        )

        # Mahino ko sahi tarteeb (Chronological order) mein lane ke liye
        month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        pivot = pivot.reindex(month_order).dropna(how='all').fillna(0)

        return pivot.reset_index()

    except Exception as e:
        print(f"Analytics Critical Error: {e}")
        return None