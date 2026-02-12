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
    Uses Pandas for grouping and date sorting.
    """
    try:
        cursor = conn.cursor()
        data = []

        # Tables to include in analytics
        config = {
            "quotations": "Quotation",
            "tax_invoices": "Tax Invoice",
            "commercial_invoices": "Commercial Inv",
            "delivery_challans": "Delivery Challan"
        }
        
        for table, label in config.items():
            try:
                # Check if table exists
                cursor.execute(f"PRAGMA table_info({table})")
                cols = [c[1] for c in cursor.fetchall()]
                if not cols: continue
                
                # Dynamic column detection
                d_col = 'date' if 'date' in cols else ('created_at' if 'created_at' in cols else None)
                a_col = 'grand_total' if 'grand_total' in cols else ('total_amount' if 'total_amount' in cols else None)
                u_col = 'created_by' if 'created_by' in cols else None
                
                if d_col and a_col:
                    query = f"SELECT {d_col}, {a_col} FROM {table} WHERE {d_col} IS NOT NULL"
                    params = []
                    
                    if user and user.lower() != 'admin' and u_col:
                        query += f" AND {u_col} = ?"
                        params.append(user)
                    
                    cursor.execute(query, params)
                    rows = cursor.fetchall()
                    for d, amt in rows:
                        if d:
                            data.append({"date": str(d), "grand_total": _safe_amount(amt), "source": table})
            except Exception as tbl_err:
                print(f"Error fetching from {table}: {tbl_err}")

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