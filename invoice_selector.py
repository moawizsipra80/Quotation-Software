import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from invoice import InvoiceApp 



def open_invoice_hub(root_window):
    """Ye function Dashboard se call hoga"""
    
    # Popup Window
    hub = tk.Toplevel(root_window)
    hub.title("Invoice Manager")
    hub.geometry("700x600")
    
    def on_hub_close():
        root_window.deiconify()
        hub.destroy()
    hub.protocol("WM_DELETE_WINDOW", on_hub_close)
    # hub.transient(root_window) # Removed to allow maximize/minimize
    
    ttk.Label(hub, text="Create Commercial Invoice", font=("Segoe UI", 14, "bold")).pack(pady=15)
    
    # Option 1: Create New Blank
    def open_blank():
        hub.destroy()
        new_win = tk.Toplevel(root_window)
        new_win.title("Commercial Sales Invoice Generator")
        new_win.geometry("1200x800")
        # ✅ NEW: Proper close handler for clean exit
        new_win.protocol("WM_DELETE_WINDOW", lambda: safe_close_invoice(new_win))
        app = InvoiceApp(new_win)  # Blank Invoice
    
    btn_new = ttk.Button(hub, text="➕ Create New Blank Invoice",
                         command=open_blank)
    btn_new.pack(fill='x', padx=50, pady=5)
    
    ttk.Separator(hub, orient='horizontal').pack(fill='x', padx=20, pady=15)
    
    # Option 2: Convert from Quotation
    ttk.Label(hub, text="OR Convert Existing Quotation:", font=("Segoe UI", 10)).pack()
    
    # List of Quotations (Searchable List)
    frame_list = ttk.Frame(hub)
    frame_list.pack(fill='both', expand=True, padx=20, pady=5)
    
    cols = ("ID", "Quot No", "Client", "Amount")
    tree = ttk.Treeview(frame_list, columns=cols, show='headings', height=8)
    tree.heading("ID", text="ID"); tree.column("ID", width=40)
    tree.heading("Quot No", text="Ref No"); tree.column("Quot No", width=100)
    tree.heading("Client", text="Client Name"); tree.column("Client", width=150)
    tree.heading("Amount", text="Total"); tree.column("Amount", width=80)
    
    sb = ttk.Scrollbar(frame_list, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=sb.set)
    tree.pack(side='left', fill='both', expand=True)
    sb.pack(side='right', fill='y')
    
    # Load Data from DB
    conn = sqlite3.connect("quotation.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, quot_no, client_name, grand_total FROM quotes ORDER BY id DESC")
    for row in cursor.fetchall():
        tree.insert("", "end", values=row)
    conn.close()
    
    def convert_selected():
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("Warning", "Please select a Quotation to convert!")
            return
        
        quot_id = tree.item(sel[0])['values'][0]
        
        # Fetch Full Data
        conn = sqlite3.connect("quotation.db")
        cur = conn.cursor()
        cur.execute("SELECT full_data FROM quotes WHERE id=?", (quot_id,))
        record = cur.fetchone()
        conn.close()
        
        if record:
            hub.destroy()
            new_win = tk.Toplevel(root_window)
            new_win.title("Commercial Sales Invoice Generator")
            new_win.geometry("1200x800")
            
            new_win.protocol("WM_DELETE_WINDOW", lambda: safe_close_invoice(new_win))
            # Yahan hum Data pass kar rahe hain InvoiceApp ko
            app = InvoiceApp(new_win, from_quotation_data=record[0])
    
    btn_convert = ttk.Button(hub, text="⬇ Load & Convert to Invoice",
                             command=convert_selected)
    btn_convert.pack(fill='x', padx=50, pady=20)

# ✅ NEW GLOBAL FUNCTION: Clean invoice window close
def safe_close_invoice(win):
    """Invoice window properly close karega without polluting main app"""
    try:
        # ✅ RESTORE DASHBOARD
        if win.master:
            win.master.deiconify()
        print("✅ Invoice window closed cleanly")
    except:
        pass
    finally:
        win.destroy()
