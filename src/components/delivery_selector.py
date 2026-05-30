# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from src.config import get_db_path
from src.delivery_challan import DeliveryChallanApp

def open_dc_hub(root_window):
    """Ye Delivery Challan ka History/Converter Hub hai"""
    
    # Popup Window
    hub = tk.Toplevel(root_window)
    hub.title("Delivery Challan Manager")
    hub.geometry("900x650")
    
    def on_hub_close():
        root_window.deiconify()
        hub.destroy()
    hub.protocol("WM_DELETE_WINDOW", on_hub_close)

    lbl = tk.Label(hub, text="Delivery Challan Manager", font=("Segoe UI", 16, "bold"), fg="#e67e22")
    lbl.pack(pady=10)

    # --- TABS (History, Quote Convert, Invoice Convert) ---
    tabs = ttk.Notebook(hub)
    tabs.pack(fill='both', expand=True, padx=10, pady=5)

    # ==================================
    # TAB 1: Delivery Challan History
    # ==================================
    tab1 = ttk.Frame(tabs)
    tabs.add(tab1, text="📂 Saved DC History")
    
    cols = ("ID", "DC No", "Client", "Date")
    tree = ttk.Treeview(tab1, columns=cols, show='headings', height=10)
    tree.heading("ID", text="ID"); tree.column("ID", width=40, anchor="center")
    tree.heading("DC No", text="DC No"); tree.column("DC No", width=80)
    tree.heading("Client", text="Client Name"); tree.column("Client", width=200)
    tree.heading("Date", text="Date"); tree.column("Date", width=100)
    
    sb = ttk.Scrollbar(tab1, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=sb.set)
    tree.pack(side='left', fill='both', expand=True)
    sb.pack(side='right', fill='y')

    def load_history():
        for i in tree.get_children(): 
            tree.delete(i)
        try:
            conn = sqlite3.connect(get_db_path("DeliveryChallan_Manager.db"))
            cur = conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='delivery_challans'")
            if cur.fetchone():
                cur.execute("SELECT id, ref_no, client_name, date FROM delivery_challans ORDER BY id DESC")
                for row in cur.fetchall():
                    tree.insert("", "end", values=row)
            conn.close()
        except Exception as e:
            print("DB Error:", e)

    load_history()

    def open_selected():
        sel = tree.selection()
        if not sel: 
            messagebox.showwarning("Warning", "Select a Delivery Challan first!")
            return
        id_ = tree.item(sel[0])['values'][0]
        try:
            conn = sqlite3.connect(get_db_path("DeliveryChallan_Manager.db"))
            cur = conn.cursor()
            cur.execute("SELECT full_data FROM delivery_challans WHERE id=?", (id_,))
            row = cur.fetchone()
            conn.close()
            if row:
                hub.destroy()
                new_win = tk.Toplevel(root_window)
                new_win.geometry("1200x800")
                new_win.protocol("WM_DELETE_WINDOW", lambda: safe_close_dc(new_win))
                app = DeliveryChallanApp(new_win, original_root=root_window, from_quotation_data=row[0])
                app.current_db_id = id_  # Existing ID for Update
        except Exception as e: 
            messagebox.showerror("Error", str(e))
    
    tree.bind("<Double-1>", lambda event: open_selected())
    ttk.Button(tab1, text="📂 Open Selected DC", command=open_selected).pack(fill='x', padx=50, pady=10)

    # ==================================
    # TAB 2: Convert Quotation to DC
    # ==================================
    tab2 = ttk.Frame(tabs)
    tabs.add(tab2, text="🔄 Convert Quote to DC")
    
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

    def convert_quote_to_dc():
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
                new_win.geometry("1200x800")
                new_win.protocol("WM_DELETE_WINDOW", lambda: safe_close_dc(new_win))
                DeliveryChallanApp(new_win, original_root=root_window, from_quotation_data=row[0])
        except Exception as e:
            messagebox.showerror("Error", str(e))

    tree2.bind("<Double-1>", lambda event: convert_quote_to_dc())
    ttk.Button(tab2, text="⬇ Load Quote into Delivery Challan", command=convert_quote_to_dc).pack(fill='x', padx=50, pady=10)

    # ==================================
    # TAB 3: Convert Sales Tax Invoice to DC
    # ==================================
    tab3 = ttk.Frame(tabs)
    tabs.add(tab3, text="🔄 Convert Sales Tax Invoice to DC")
    
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

    def convert_sales_invoice_to_dc():
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
                new_win.geometry("1200x800")
                new_win.protocol("WM_DELETE_WINDOW", lambda: safe_close_dc(new_win))
                DeliveryChallanApp(new_win, original_root=root_window, from_quotation_data=row[0])
        except Exception as e:
            messagebox.showerror("Error", str(e))

    tree3.bind("<Double-1>", lambda event: convert_sales_invoice_to_dc())
    ttk.Button(tab3, text="⬇ Load Sales Invoice into Delivery Challan", command=convert_sales_invoice_to_dc).pack(fill='x', padx=50, pady=10)

    # ==================================
    # TAB 4: Convert Commercial Invoice to DC
    # ==================================
    tab4 = ttk.Frame(tabs)
    tabs.add(tab4, text="🔄 Convert Commercial Invoice to DC")
    
    cols4 = ("ID", "Inv No", "Client", "Amount")
    tree4 = ttk.Treeview(tab4, columns=cols4, show='headings', height=10)
    tree4.heading("ID", text="ID"); tree4.column("ID", width=40, anchor="center")
    tree4.heading("Inv No", text="Inv No"); tree4.column("Inv No", width=100)
    tree4.heading("Client", text="Client Name"); tree4.column("Client", width=200)
    tree4.heading("Amount", text="Total"); tree4.column("Amount", width=100)
    
    sb4 = ttk.Scrollbar(tab4, orient="vertical", command=tree4.yview)
    tree4.configure(yscrollcommand=sb4.set)
    tree4.pack(side='left', fill='both', expand=True)
    sb4.pack(side='right', fill='y')

    try:
        conn = sqlite3.connect(get_db_path("CommercialInvoice_Manager.db"))
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='commercial_invoices'")
        if cur.fetchone():
            cur.execute("SELECT id, ref_no, client_name, grand_total FROM commercial_invoices ORDER BY id DESC")
            for row in cur.fetchall():
                tree4.insert("", "end", values=row)
        conn.close()
    except: 
        pass

    def convert_commercial_invoice_to_dc():
        sel = tree4.selection()
        if not sel: 
            messagebox.showwarning("Warning", "Select a Commercial Invoice first!")
            return
        inv_id = tree4.item(sel[0])['values'][0]
        try:
            conn = sqlite3.connect(get_db_path("CommercialInvoice_Manager.db"))
            cur = conn.cursor()
            cur.execute("SELECT full_data FROM commercial_invoices WHERE id=?", (inv_id,))
            row = cur.fetchone()
            conn.close()
            if row:
                hub.destroy()
                new_win = tk.Toplevel(root_window)
                new_win.geometry("1200x800")
                new_win.protocol("WM_DELETE_WINDOW", lambda: safe_close_dc(new_win))
                DeliveryChallanApp(new_win, original_root=root_window, from_quotation_data=row[0])
        except Exception as e:
            messagebox.showerror("Error", str(e))

    tree4.bind("<Double-1>", lambda event: convert_commercial_invoice_to_dc())
    ttk.Button(tab4, text="⬇ Load Commercial Invoice into Delivery Challan", command=convert_commercial_invoice_to_dc).pack(fill='x', padx=50, pady=10)

    # ==================================
    # Create New Blank
    # ==================================
    ttk.Separator(hub, orient='horizontal').pack(fill='x', padx=10, pady=5)
    
    def open_new():
        hub.destroy()
        new_win = tk.Toplevel(root_window)
        new_win.geometry("1200x800")
        new_win.protocol("WM_DELETE_WINDOW", lambda: safe_close_dc(new_win))
        DeliveryChallanApp(new_win, original_root=root_window)

    ttk.Button(hub, text="➕ Create Fresh Blank DC", command=open_new).pack(fill='x', padx=20, pady=10)

def safe_close_dc(win):
    """Delivery Challan window properly close karega without polluting main app"""
    try:
        if win.master:
            win.master.deiconify()
        print("✅ DC window closed cleanly")
    except:
        pass
    finally:
        win.destroy()