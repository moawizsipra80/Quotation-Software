import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from src.config import get_db_path
from src.commercial import CommercialApp  # Aapki commercial.py file

def set_centered_geometry(win, width_pct, height_pct, max_w, max_h):
    screen_w = win.winfo_screenwidth()
    screen_h = win.winfo_screenheight()
    w = min(max_w, int(screen_w * width_pct))
    h = min(max_h, int(screen_h * height_pct))
    x = (screen_w - w) // 2
    y = (screen_h - h) // 2
    win.geometry(f"{w}x{h}+{x}+{y}")

def open_commercial_hub(root_window):
    """Ye Commercial Invoices ka History/Converter Hub hai"""
    
    # Popup Window
    hub = tk.Toplevel(root_window)
    hub.title("Commercial Invoice Manager")
    set_centered_geometry(hub, 0.75, 0.75, 950, 680)
    
    def on_hub_close():
        root_window.deiconify()
        try: root_window.state('zoomed')
        except: pass
        hub.destroy()
    hub.protocol("WM_DELETE_WINDOW", on_hub_close)
    
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
    tree.heading("ID", text="ID"); tree.column("ID", width=40, anchor="center")
    tree.heading("Inv No", text="Inv No"); tree.column("Inv No", width=80)
    tree.heading("Client", text="Client Name"); tree.column("Client", width=200)
    tree.heading("Date", text="Date"); tree.column("Date", width=100)
    tree.heading("Amount", text="Total"); tree.column("Amount", width=100)
    
    sb = ttk.Scrollbar(tab1, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=sb.set)
    tree.pack(side='left', fill='both', expand=True)
    sb.pack(side='right', fill='y')

    def load_history():
        for i in tree.get_children(): 
            tree.delete(i)
        try:
            conn = sqlite3.connect(get_db_path("CommercialInvoice_Manager.db"))
            cur = conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='commercial_invoices'")
            if cur.fetchone():
                cur.execute("SELECT id, ref_no, client_name, date, grand_total FROM commercial_invoices ORDER BY id DESC")
                for row in cur.fetchall():
                    amt = f"{row[4]:,.0f}" if row[4] else "0"
                    tree.insert("", "end", values=(row[0], row[1], row[2], row[3], amt))
            conn.close()
        except Exception as e:
            print("DB Error:", e)

    load_history()

    def open_selected_invoice():
        sel = tree.selection()
        if not sel: 
            messagebox.showwarning("Warning", "Select a Commercial Invoice first!")
            return
        inv_id = tree.item(sel[0])['values'][0]
        try:
            conn = sqlite3.connect(get_db_path("CommercialInvoice_Manager.db"))
            cur = conn.cursor()
            cur.execute("SELECT full_data FROM commercial_invoices WHERE id=?", (inv_id,))
            row = cur.fetchone()
            conn.close()
            if row:
                hub.destroy()
                new_win = tk.Toplevel(root_window)
                set_centered_geometry(new_win, 0.85, 0.85, 1250, 820)
                new_win.protocol("WM_DELETE_WINDOW", lambda: safe_close_commercial(new_win))
                app = CommercialApp(new_win, original_root=root_window, from_quotation_data=row[0])
                app.current_db_id = inv_id  # Existing ID for Update
        except Exception as e:
            messagebox.showerror("Error", str(e))

    tree.bind("<Double-1>", lambda event: open_selected_invoice())
    ttk.Button(tab1, text="📂 Open Selected Commercial Invoice", command=open_selected_invoice).pack(fill='x', padx=50, pady=10)

    # =========================================================
    # TAB 2: CONVERT QUOTATION (New from Quote)
    # =========================================================
    tab2 = ttk.Frame(tabs)
    tabs.add(tab2, text="🔄 Convert Quotation")
    
    cols2 = ("ID", "Quot No", "Client", "Amount")
    tree2 = ttk.Treeview(tab2, columns=cols2, show='headings', height=10)
    tree2.heading("ID", text="ID"); tree2.column("ID", width=40, anchor="center")
    tree2.heading("Quot No", text="Ref No"); tree2.column("Quot No", width=100)
    tree2.heading("Client", text="Client Name"); tree2.column("Client", width=200)
    tree2.heading("Amount", text="Total"); tree2.column("Amount", width=100)
    
    sb2 = ttk.Scrollbar(tab2, orient="vertical", command=tree2.yview)
    tree2.configure(yscrollcommand=sb2.set)
    tree2.pack(side='left', fill='both', expand=True)
    sb2.pack(side='right', fill='y')

    try:
        conn = sqlite3.connect(get_db_path("QuotationManager_Final.db"))
        cur = conn.cursor()
        cur.execute("SELECT id, ref_no, client_name, grand_total FROM quotations ORDER BY id DESC")
        for row in cur.fetchall():
            tree2.insert("", "end", values=row)
        conn.close()
    except: 
        pass

    def convert_quote():
        sel = tree2.selection()
        if not sel: 
            messagebox.showwarning("Warning", "Select a Quotation first!")
            return
        q_id = tree2.item(sel[0])['values'][0]
        try:
            conn = sqlite3.connect(get_db_path("QuotationManager_Final.db"))
            cur = conn.cursor()
            cur.execute("SELECT full_data FROM quotations WHERE id=?", (q_id,))
            row = cur.fetchone()
            conn.close()
            if row:
                hub.destroy()
                new_win = tk.Toplevel(root_window)
                set_centered_geometry(new_win, 0.85, 0.85, 1250, 820)
                new_win.protocol("WM_DELETE_WINDOW", lambda: safe_close_commercial(new_win))
                CommercialApp(new_win, original_root=root_window, from_quotation_data=row[0])
        except Exception as e:
            messagebox.showerror("Error", str(e))

    tree2.bind("<Double-1>", lambda event: convert_quote())
    ttk.Button(tab2, text="⬇ Load Quotation into Commercial Invoice", command=convert_quote).pack(fill='x', padx=50, pady=10)

    # =========================================================
    # TAB 3: CONVERT SALES TAX INVOICE (New from Invoice)
    # =========================================================
    tab3 = ttk.Frame(tabs)
    tabs.add(tab3, text="🔄 Convert Sales Tax Invoice")
    
    cols3 = ("ID", "Inv No", "Client", "Amount")
    tree3 = ttk.Treeview(tab3, columns=cols3, show='headings', height=10)
    tree3.heading("ID", text="ID"); tree3.column("ID", width=40, anchor="center")
    tree3.heading("Inv No", text="Inv No"); tree3.column("Inv No", width=100)
    tree3.heading("Client", text="Client Name"); tree3.column("Client", width=200)
    tree3.heading("Amount", text="Total"); tree3.column("Amount", width=100)
    
    sb3 = ttk.Scrollbar(tab3, orient="vertical", command=tree3.yview)
    tree3.configure(yscrollcommand=sb3.set)
    tree3.pack(side='left', fill='both', expand=True)
    sb3.pack(side='right', fill='y')

    try:
        conn = sqlite3.connect(get_db_path("TaxInvoice_Manager.db"))
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tax_invoices'")
        if cur.fetchone():
            cur.execute("SELECT id, ref_no, client_name, grand_total FROM tax_invoices ORDER BY id DESC")
            for row in cur.fetchall():
                tree3.insert("", "end", values=row)
        conn.close()
    except: 
        pass

    def convert_sales_invoice():
        sel = tree3.selection()
        if not sel: 
            messagebox.showwarning("Warning", "Select a Sales Tax Invoice first!")
            return
        inv_id = tree3.item(sel[0])['values'][0]
        try:
            conn = sqlite3.connect(get_db_path("TaxInvoice_Manager.db"))
            cur = conn.cursor()
            cur.execute("SELECT full_data FROM tax_invoices WHERE id=?", (inv_id,))
            row = cur.fetchone()
            conn.close()
            if row:
                hub.destroy()
                new_win = tk.Toplevel(root_window)
                set_centered_geometry(new_win, 0.85, 0.85, 1250, 820)
                new_win.protocol("WM_DELETE_WINDOW", lambda: safe_close_commercial(new_win))
                CommercialApp(new_win, original_root=root_window, from_quotation_data=row[0])
        except Exception as e:
            messagebox.showerror("Error", str(e))

    tree3.bind("<Double-1>", lambda event: convert_sales_invoice())
    ttk.Button(tab3, text="⬇ Load Sales Invoice into Commercial Invoice", command=convert_sales_invoice).pack(fill='x', padx=50, pady=10)

    # --- FOOTER: Create Blank ---
    ttk.Separator(hub, orient='horizontal').pack(fill='x', padx=10, pady=5)
    
    def open_blank():
        hub.destroy()
        new_win = tk.Toplevel(root_window)
        set_centered_geometry(new_win, 0.85, 0.85, 1250, 820)
        new_win.protocol("WM_DELETE_WINDOW", lambda: safe_close_commercial(new_win))
        CommercialApp(new_win, original_root=root_window)

    ttk.Button(hub, text="➕ Create Fresh Blank Commercial Invoice", command=open_blank).pack(fill='x', padx=20, pady=10)

def safe_close_commercial(win):
    """Commercial window properly close karega without polluting main app"""
    try:
        if win.master:
            win.master.deiconify()
            try: win.master.state('zoomed')
            except: pass
        print("✅ Commercial window closed cleanly")
    except:
        pass
    finally:
        win.destroy()