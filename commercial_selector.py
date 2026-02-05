import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from commercial import CommercialApp  # Aapki commercial.py file

def open_commercial_hub(root_window):
    """Ye Commercial Invoices ka History/Converter Hub hai"""
    
    # Popup Window
    hub = tk.Toplevel(root_window)
    hub.title("Commercial Invoice Manager")
    hub.geometry("900x650") # Thora size barha diya
    # hub.transient(root_window) # Removed to allow maximize/minimize
    
    lbl = tk.Label(hub, text="Commercial Invoice Manager", font=("Segoe UI", 16, "bold"), fg="#d35400")
    lbl.pack(pady=10)

    # --- TABS (History, Quote Convert, Invoice Convert) ---
    tabs = ttk.Notebook(hub)
    tabs.pack(fill='both', expand=True, padx=10, pady=5)

    # =========================================================
    # TAB 1: EXISTING COMMERCIAL INVOICES (History)
    # =========================================================
    tab1 = ttk.Frame(tabs)
    tabs.add(tab1, text="📂 Saved Commercial History")

    cols = ("ID", "Inv No", "Client", "Date", "Amount")
    tree = ttk.Treeview(tab1, columns=cols, show='headings', height=10)
    tree.heading("ID", text="ID"); tree.column("ID", width=40)
    tree.heading("Inv No", text="Inv No"); tree.column("Inv No", width=80)
    tree.heading("Client", text="Client Name"); tree.column("Client", width=200)
    tree.heading("Date", text="Date"); tree.column("Date", width=100)
    tree.heading("Amount", text="Total"); tree.column("Amount", width=100)
    
    sb = ttk.Scrollbar(tab1, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=sb.set)
    tree.pack(side='left', fill='both', expand=True)
    sb.pack(side='right', fill='y')

    def load_history():
        for i in tree.get_children(): tree.delete(i)
        try:
            conn = sqlite3.connect("quotation.db")
            cur = conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='commercial_table'")
            if cur.fetchone():
                cur.execute("SELECT id, inv_no, client_name, inv_date, grand_total FROM commercial_table ORDER BY id DESC")
                for row in cur.fetchall():
                    amt = f"{row[4]:,.0f}" if row[4] else "0"
                    tree.insert("", "end", values=(row[0], row[1], row[2], row[3], amt))
            conn.close()
        except Exception as e:
            print("DB Error:", e)

    load_history()

    def open_selected_invoice():
        sel = tree.selection()
        if not sel: return
        inv_id = tree.item(sel[0])['values'][0]
        try:
            conn = sqlite3.connect("quotation.db")
            cur = conn.cursor()
            cur.execute("SELECT full_data FROM commercial_table WHERE id=?", (inv_id,))
            row = cur.fetchone()
            conn.close()
            if row:
                hub.destroy()
                new_win = tk.Toplevel(root_window)
                new_win.geometry("1200x800")
                app = CommercialApp(new_win, from_quotation_data=row[0])
                app.current_db_id = inv_id # Existing ID for Update
        except Exception as e:
            messagebox.showerror("Error", str(e))

    ttk.Button(tab1, text="📂 Open Selected Commercial Invoice", command=open_selected_invoice).pack(fill='x', padx=50, pady=10)


    # =========================================================
    # TAB 2: CONVERT QUOTATION (New from Quote)
    # =========================================================
    tab2 = ttk.Frame(tabs)
    tabs.add(tab2, text="🔄 Convert Quotation")
    
    cols2 = ("ID", "Quot No", "Client", "Amount")
    tree2 = ttk.Treeview(tab2, columns=cols2, show='headings', height=10)
    tree2.heading("ID", text="ID"); tree2.column("ID", width=40)
    tree2.heading("Quot No", text="Ref No"); tree2.column("Quot No", width=100)
    tree2.heading("Client", text="Client Name"); tree2.column("Client", width=200)
    tree2.heading("Amount", text="Total"); tree2.column("Amount", width=100)
    
    sb2 = ttk.Scrollbar(tab2, orient="vertical", command=tree2.yview)
    tree2.configure(yscrollcommand=sb2.set)
    tree2.pack(side='left', fill='both', expand=True)
    sb2.pack(side='right', fill='y')

    try:
        conn = sqlite3.connect("quotation.db")
        cur = conn.cursor()
        cur.execute("SELECT id, quot_no, client_name, grand_total FROM quotes ORDER BY id DESC")
        for row in cur.fetchall():
            tree2.insert("", "end", values=row)
        conn.close()
    except: pass

    def convert_quote():
        sel = tree2.selection()
        if not sel: return
        q_id = tree2.item(sel[0])['values'][0]
        try:
            conn = sqlite3.connect("quotation.db")
            cur = conn.cursor()
            cur.execute("SELECT full_data FROM quotes WHERE id=?", (q_id,))
            row = cur.fetchone()
            conn.close()
            if row:
                hub.destroy()
                new_win = tk.Toplevel(root_window)
                new_win.geometry("1200x800")
                CommercialApp(new_win, from_quotation_data=row[0])
        except Exception as e:
            messagebox.showerror("Error", str(e))

    ttk.Button(tab2, text="⬇ Load Quotation into Commercial Invoice", command=convert_quote).pack(fill='x', padx=50, pady=10)


    # =========================================================
    # TAB 3: CONVERT SALES TAX INVOICE (New from Invoice) - NEW ADDITION
    # =========================================================
    tab3 = ttk.Frame(tabs)
    tabs.add(tab3, text="🔄 Convert Sales Tax Invoice")
    
    cols3 = ("ID", "Inv No", "Client", "Amount")
    tree3 = ttk.Treeview(tab3, columns=cols3, show='headings', height=10)
    tree3.heading("ID", text="ID"); tree3.column("ID", width=40)
    tree3.heading("Inv No", text="Inv No"); tree3.column("Inv No", width=100)
    tree3.heading("Client", text="Client Name"); tree3.column("Client", width=200)
    tree3.heading("Amount", text="Total"); tree3.column("Amount", width=100)
    
    sb3 = ttk.Scrollbar(tab3, orient="vertical", command=tree3.yview)
    tree3.configure(yscrollcommand=sb3.set)
    tree3.pack(side='left', fill='both', expand=True)
    sb3.pack(side='right', fill='y')

    try:
        conn = sqlite3.connect("quotation.db")
        cur = conn.cursor()
        # Yahan hum 'invoices' table se data utha rahe hain (Sales Tax Invoices)
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='invoices'")
        if cur.fetchone():
            cur.execute("SELECT id, inv_no, client_name, grand_total FROM invoices ORDER BY id DESC")
            for row in cur.fetchall():
                tree3.insert("", "end", values=row)
        conn.close()
    except: pass

    def convert_sales_invoice():
        sel = tree3.selection()
        if not sel: return
        inv_id = tree3.item(sel[0])['values'][0]
        try:
            conn = sqlite3.connect("quotation.db")
            cur = conn.cursor()
            cur.execute("SELECT full_data FROM invoices WHERE id=?", (inv_id,))
            row = cur.fetchone()
            conn.close()
            if row:
                hub.destroy()
                new_win = tk.Toplevel(root_window)
                new_win.geometry("1200x800")
                # Data wahi pass hoga, format same hai
                CommercialApp(new_win, from_quotation_data=row[0])
        except Exception as e:
            messagebox.showerror("Error", str(e))

    ttk.Button(tab3, text="⬇ Load Sales Invoice into Commercial Invoice", command=convert_sales_invoice).pack(fill='x', padx=50, pady=10)


    # --- FOOTER: Create Blank ---
    ttk.Separator(hub, orient='horizontal').pack(fill='x', padx=10, pady=5)
    def open_blank():
        hub.destroy()
        new_win = tk.Toplevel(root_window)
        new_win.geometry("1200x800")
        CommercialApp(new_win)

    ttk.Button(hub, text="➕ Create Fresh Blank Commercial Invoice", command=open_blank).pack(fill='x', padx=20, pady=10)