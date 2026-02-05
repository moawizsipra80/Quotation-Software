# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from delivery_challan import DeliveryChallanApp

def open_dc_hub(root_window):
    hub = tk.Toplevel(root_window)
    hub.title("Delivery Challan Manager")
    hub.geometry("800x600")
    
    def on_hub_close():
        root_window.deiconify()
        hub.destroy()
    hub.protocol("WM_DELETE_WINDOW", on_hub_close)
    # hub.transient(root_window) # Removed to allow maximize/minimize

    lbl = tk.Label(hub, text="Delivery Challan Manager", font=("Segoe UI", 16, "bold"), fg="#e67e22")
    lbl.pack(pady=10)

    tabs = ttk.Notebook(hub)
    tabs.pack(fill='both', expand=True, padx=10, pady=5)

    # ==================================
    # TAB 1: Delivery Challan History
    # ==================================
    tab1 = ttk.Frame(tabs); tabs.add(tab1, text="[FOLDER] DC History")
    
    cols = ("ID", "DC No", "Client", "Date")
    tree = ttk.Treeview(tab1, columns=cols, show='headings', height=12)
    tree.heading("ID", text="ID"); tree.column("ID", width=40)
    tree.heading("DC No", text="DC No"); tree.column("DC No", width=80)
    tree.heading("Client", text="Client Name"); tree.column("Client", width=200)
    tree.heading("Date", text="Date"); tree.column("Date", width=100)
    
    sb = ttk.Scrollbar(tab1, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=sb.set)
    tree.pack(side='left', fill='both', expand=True)
    sb.pack(side='right', fill='y')

    def load_history():
        for i in tree.get_children(): tree.delete(i)
        try:
            conn = sqlite3.connect("quotation.db")
            cur = conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='delivery_challans'")
            if cur.fetchone():
                cur.execute("SELECT id, dc_no, client_name, dc_date FROM delivery_challans ORDER BY id DESC")
                for row in cur.fetchall():
                    tree.insert("", "end", values=row)
            conn.close()
        except: pass
    load_history()

    def open_selected():
        sel = tree.selection()
        if not sel: return
        id_ = tree.item(sel[0])['values'][0]
        try:
            conn = sqlite3.connect("quotation.db")
            cur = conn.cursor()
            cur.execute("SELECT full_data FROM delivery_challans WHERE id=?", (id_,))
            row = cur.fetchone()
            conn.close()
            if row:
                hub.destroy()
                new_win = tk.Toplevel(root_window)
                new_win.geometry("1200x800")
                app = DeliveryChallanApp(new_win, from_quotation_data=row[0])
                app.current_db_id = id_
        except Exception as e: messagebox.showerror("Error", str(e))
    
    ttk.Button(tab1, text="[OPEN] Open Selected DC", command=open_selected).pack(fill='x', padx=50, pady=10)

    # ==================================
    # TAB 2: Convert Quotation to DC
    # ==================================
    tab2 = ttk.Frame(tabs); tabs.add(tab2, text="[SYNC] Convert Quote to DC")
    
    cols2 = ("ID", "Quot No", "Client", "Amount")
    tree2 = ttk.Treeview(tab2, columns=cols2, show='headings', height=12)
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

    def convert_quote_to_dc():
        sel = tree2.selection()
        if not sel: 
            messagebox.showwarning("Warning", "Select a quotation first!")
            return
        
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
                # Data pass kar rahe hain DC App ko
                DeliveryChallanApp(new_win, from_quotation_data=row[0])
        except Exception as e:
            messagebox.showerror("Error", str(e))

    ttk.Button(tab2, text="[DOWN] Load Quote into Delivery Challan", command=convert_quote_to_dc).pack(fill='x', padx=50, pady=10)

    # ==================================
    # Create New Blank
    # ==================================
    ttk.Separator(hub, orient='horizontal').pack(fill='x', padx=10, pady=5)
    def open_new():
        hub.destroy()
        new_win = tk.Toplevel(root_window)
        new_win.geometry("1200x800")
        DeliveryChallanApp(new_win)

    ttk.Button(hub, text="[PLUS] Create Fresh Blank DC", command=open_new).pack(fill='x', padx=20, pady=10)