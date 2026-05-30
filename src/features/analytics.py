import datetime as _dt
import sqlite3

def _safe_amount(val):
    try:
        if isinstance(val, str):
            val = val.replace(',', '')
        return float(val) if val is not None else 0.0
    except Exception:
        return 0.0

def get_analytics_data(conn, user=None):
    """
    Robust Analytics: Fetches data for Quotations, Invoices, and Delivery Challans.
    Dynamically connects to decoupled manager databases to merge statistics accurately.
    Uses Pandas for grouping and date sorting.
    """
    try:
        data = []

        # Tables, Labels, and their respective database manager files
        config = {
            "quotations": ("Quotation", "QuotationManager_Final.db"),
            "tax_invoices": ("Tax Invoice", "TaxInvoice_Manager.db"),
            "commercial_invoices": ("Commercial Inv", "CommercialInvoice_Manager.db"),
            "delivery_challans": ("Delivery Challan", "DeliveryChallan_Manager.db")
        }
        
        for table, (label, db_file) in config.items():
            try:
                from src.config import get_db_path
                # Establish temporary connection to the separate database file
                temp_conn = sqlite3.connect(get_db_path(db_file))
                temp_cursor = temp_conn.cursor()
                
                # Check if table exists
                temp_cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
                if not temp_cursor.fetchone():
                    temp_conn.close()
                    continue
                
                # Dynamic column detection
                temp_cursor.execute(f"PRAGMA table_info({table})")
                cols = [c[1] for c in temp_cursor.fetchall()]
                if not cols: 
                    temp_conn.close()
                    continue
                
                d_col = 'date' if 'date' in cols else ('created_at' if 'created_at' in cols else None)
                a_col = 'grand_total' if 'grand_total' in cols else ('total_amount' if 'total_amount' in cols else None)
                u_col = 'created_by' if 'created_by' in cols else None
                
                if d_col and a_col:
                    query = f"SELECT {d_col}, {a_col} FROM {table} WHERE {d_col} IS NOT NULL"
                    params = []
                    
                    if user and user.lower() != 'admin' and u_col:
                        query += f" AND {u_col} = ?"
                        params.append(user)
                    
                    temp_cursor.execute(query, params)
                    rows = temp_cursor.fetchall()
                    for d, amt in rows:
                        if d:
                            data.append({"date": str(d), "grand_total": _safe_amount(amt), "source": table})
                temp_conn.close()
            except Exception as tbl_err:
                print(f"Error fetching from {table} inside {db_file}: {tbl_err}")

        if not data:
            return None

        # Lazy load pandas
        import pandas as pd
        df = pd.DataFrame(data)
        
        # Robust Date Parsing
        def parse_dates(s):
            for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%d-%b-%Y"):
                try: return pd.to_datetime(s, format=fmt)
                except: continue
            return pd.to_datetime(s, errors='coerce')

        df["date"] = df["date"].apply(parse_dates)
        df = df.dropna(subset=["date"])

        if df.empty:
            return None

        # Sort and Group
        df["month_idx"] = df["date"].dt.month
        df["month_name"] = df["date"].dt.strftime("%b")
        
        # Pivot Table
        pivot = df.pivot_table(
            index=["month_idx", "month_name"],
            columns="source",
            values="grand_total",
            aggfunc="sum",
            fill_value=0.0
        ).reset_index()

        # Sort by month_idx then rename columns for compatibility with dashboard.py
        pivot = pivot.sort_values("month_idx").drop(columns="month_idx").rename(columns={"month_name": "month"})

        return pivot

    except Exception as e:
        print(f"Analytics Critical Error: {e}")
        return None