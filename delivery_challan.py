import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import datetime
# import sqlite3
import sqlite3
import os
import copy
from PIL import Image, ImageTk  
# ✅ Lazy Imports (Moved inside functions for speed)

# Parent Class Import
from quotation import QuotationApp 

class DeliveryChallanApp(QuotationApp):
    def __init__(self, root, original_root=None, from_quotation_data=None):
        self.root = root 
        self.root.title("Delivery Challan")
        self.original_root = original_root
        self.is_invoice_window = True 
        
        # 1) Invoice Specific Vars
        self.left_header_title = tk.StringVar(value="Client  - Data")
        self.right_header_title = tk.StringVar(value="Orient Marketing - Data")

        self.client_stn_var = tk.StringVar()
        self.client_ntn_var = tk.StringVar()
        self.delivery_date_var = tk.StringVar(value=datetime.date.today().strftime("%Y-%m-%d"))
        self.delivered_through_var = tk.StringVar()
        self.mill_code_var = tk.StringVar()
        self.demand_no_var = tk.StringVar()
        
        self.ref_quot_no_var = tk.StringVar() 
        self.dc_no_var = tk.StringVar()
        self.vendor_stn_var = tk.StringVar()
        self.vendor_ntn_var = tk.StringVar()
        self.vendor_pra_var = tk.StringVar() 
        self.vendor_email_var = tk.StringVar() 
         

        # --- YAHAN PASTE KAREIN (Variables Section mein) ---
        self.trans_by_var = tk.StringVar()
        self.trans_date_var = tk.StringVar(value=datetime.date.today().strftime("%d-%b-%Y"))
        self.gate_person_var = tk.StringVar()
        self.vehicle_num_var = tk.StringVar()

        # --- YAHAN PASTE KAREIN (Variables Section mein) ---
        self.trans_by_var = tk.StringVar() # Used as Transport Name
        self.trans_date_var = tk.StringVar(value=datetime.date.today().strftime("%d-%b-%Y"))
        self.vehicle_num_var = tk.StringVar()
        
        # --- NEW VARIABLES FOR COMPLEX LAYOUT ---
        self.bilty_no_var = tk.StringVar()
        self.booking_date_var = tk.StringVar()
        self.trans_charges_var = tk.StringVar()
        self.cargo_address_var = tk.StringVar()
        self.driver_cnic_var = tk.StringVar()
        
        # Checkboxes State (0 or 1)
        self.purpose_sale_var = tk.IntVar()
        self.purpose_job_var = tk.IntVar()
        self.purpose_ret_var = tk.IntVar()
        self.purpose_nonret_var = tk.IntVar()
        
        self.source_public_var = tk.IntVar()
        self.source_special_var = tk.IntVar()
        self.source_other_var = tk.IntVar()
        
        self.mode_cargo_var = tk.IntVar()
        self.mode_courier_var = tk.IntVar()
        self.mode_rail_var = tk.IntVar()
        self.mode_air_var = tk.IntVar()
        
        # Ye list extra fields (jo user add karega) store karegi
        self.extra_transport_fields = []
        self.add_custom_field_func = None # Safe default
        
        # self.init_database() # Removed redundant call, handled by parent super().__init__
        self.current_db_id = None
        self.auto_save_timer = None # Ensure timer var exists
        self.root.after(10000, self.auto_save_loop) # Increased delay
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # --------------------------------------------------- 
        # Logo Paths
        self.header_logo_right_path = None
        # --- LOGO & FOOTER VARIABLES (UPDATED) ---
        self.header_logo_path = None
        self.header_logo_right_path = None
        
        # Logo 1: Box ke andar wala
        self.delivered_logo_path = None 
        
        # Logo 2: Page ke neeche wala (Sticker)
        self.footer_logo_path = None 
        self.f_logo_size_var = tk.DoubleVar(value=1.2)
        self.footer_align_var = tk.StringVar(value="Center") # Left, Center, Right
        self.footer_text_var = tk.StringVar()
        # 2) Parent init
        super().__init__(root) 
        
        # Override some parent settings for Challan specific needs
        self.auto_save_enabled.set(True)
        # 3) Invoice-specific overrides
        self.header_rows = [] 
       
        self.doc_title_var.set("Delivery Chalan") 
        self.quotation_no_var.set("55")
        self.approved_by_var.set("Manager Accounts")

        if from_quotation_data:
            self.load_from_quotation_data(from_quotation_data)

        # Enable all-column editing via parent's comprehensive method
        if hasattr(self, 'tree'):
            self.tree.bind("<Double-1>", self.on_tree_double_click)
            
        self._init_default_widths()

    def _init_default_widths(self):
        # ✅ Override Default Column Widths for Delivery Challan (PDF Optimized)
        # Optimized balance for Challan layout.
        opt_widths = {'sno': 25, 'uom': 35, 'qty': 40, 'price': 60, 'amount': 70, 'gst': 50, 'total': 80, 'desc': 220}
        for col in self.columns_config:
            if col['id'] in opt_widths:
                col['width'] = opt_widths[col['id']]

    def load_from_quotation_data(self, json_str):
        try:
            data = json.loads(json_str)
            
            # Restore Header Data
            h = data.get("header", {})
            self.client_name_var.set(h.get("client_name", ""))
            self.client_addr_var.set(h.get("client_addr", ""))
            self.client_contact_var.set(h.get("client_contact", ""))
            self.client_email_var.set(h.get("client_email", ""))
            self.client_designation_var.set(h.get("client_desig", ""))
            self.rfq_no_var.set(h.get("rfq", ""))
            
            # Map Quotation No to Ref Quote
            self.ref_quot_no_var.set(h.get("quot_no", ""))
            self.dc_no_var.set("DC-NEW") 
            
            # Restore Items & Colors
            self.items_data = data.get("items", [])
            self.row_colors = {int(k): v for k, v in data.get("colors", {}).items()}
            
            self.refresh_tree()
            if hasattr(self, 'total_lbl'):
                self.recalc_all()
                
        except Exception as e:
            messagebox.showerror("Load Error", f"Failed to restore data: {e}")


    # ✅ LOAD LOGO FUNCTION
    def load_logo(self, which):
        try:
            path = filedialog.askopenfilename(parent=self.root, filetypes=[("Images", "*.png;*.jpg;*.jpeg")])
            if not path: return

            lbl = None
            if which == "header":
                self.header_logo_path = path; lbl = self.header_logo_lbl
            elif which == "header_right":
                self.header_logo_right_path = path; lbl = self.header_logo_right_lbl
            
            # ✅ Logo 1: Box ke andar (Delivered By)
            elif which == "delivered":
                self.delivered_logo_path = path; lbl = self.delivered_logo_lbl
            
            # ✅ Logo 2: Footer Sticker (Page Bottom)
            elif which == "footer":
                self.footer_logo_path = path; lbl = self.footer_logo_lbl
            
            if lbl:
                img = Image.open(path); img.thumbnail((40, 40))
                photo = ImageTk.PhotoImage(img)
                lbl.config(image=photo, text=""); lbl.image = photo 
        except Exception as e:
            messagebox.showerror("Error", f"Image Load Error: {e}")

    def on_closing(self):
        """Optimized closing: Instantly restores dashboard and saves in background"""
        try:
            # 1. Restore dashboard immediately for instant feel
            if hasattr(self, 'original_root') and self.original_root:
                try: self.original_root.deiconify()
                except: pass
            
            # 2. Save in background thread so it doesn't block UI closure
            if self.client_name_var.get().strip():
                import threading
                threading.Thread(target=lambda: self.save_to_database(silent=True), daemon=True).start()
                
            print("✅ Challan closure initiated")
        except Exception as e:
            print(f"Close warning (non-critical): {e}")
        finally:
            try: self.root.destroy()
            except: pass

    def _init_standard_header_rows(self):
        self.header_rows = []

    
    
    # --- DATABASE FUNCTIONS FOR CHALLAN ---
    # Using parent's init_database (SQLite) now for speed
    def init_database(self):
        super().init_database()

    def auto_save_loop(self):
        """Optimized auto-save loop to avoid UI hangs"""
        try:
            if not self.root.winfo_exists(): return
        except: return

        if self.client_name_var.get().strip() and len(self.items_data) > 0:
             import threading
             # Pre-fetch data to avoid variable access in thread
             try:
                 data_to_save = {
                     'ref_no': self.quotation_no_var.get(),
                     'client_name': self.client_name_var.get(),
                     'date': self.doc_date_var.get(),
                     'items': copy.deepcopy(self.items_data)
                 }
             except: data_to_save = None

             if data_to_save:
                 threading.Thread(target=lambda: self.save_to_database(silent=True), daemon=True).start()
             
        try:
            if self.root.winfo_exists():
                self.auto_save_timer = self.root.after(10000, self.auto_save_loop)
        except: pass

    def go_to_dashboard(self):
        self.on_closing() 

    # =========================================================
    #  3. HEADER GUI
    # =========================================================
    def _build_header_section(self, parent):
        main_box = ttk.Frame(parent)
        main_box.pack(fill='x', pady=5)

        # 1. Action Buttons
        btn_fr = ttk.Frame(main_box)
        btn_fr.pack(fill='x', pady=2)
        ttk.Button(btn_fr, text="💾 Save Invoice", command=self.save_to_database).pack(side='left', padx=5)
        ttk.Button(btn_fr, text="📊 Back to Dashboard", command=self.go_to_dashboard).pack(side='left', padx=5)
        # --- IMPORT SECTION ---
        ttk.Label(btn_fr, text="| Load: ").pack(side='left', padx=(10, 2))
        
        # ✅ NEW BUTTON: Saved DCs dekhne ke liye
        ttk.Button(btn_fr, text="📂 Load Saved DC", 
                   command=lambda: self.open_import_dialog("delivery_challans")).pack(side='left', padx=2)

        # Other Import Buttons
        ttk.Button(btn_fr, text="📄 Commercial Inv", 
                   command=lambda: self.open_import_dialog("commercial_invoices")).pack(side='left', padx=2)
        ttk.Button(btn_fr, text="📑 Tax Inv", 
                   command=lambda: self.open_import_dialog("tax_invoices")).pack(side='left', padx=2)
        # ----------------------
        

        # ✅ FIXED: "Manage Header Rows" Button Restored
        ttk.Button(btn_fr, text="📑 Manage Header Rows", command=self.open_header_manager).pack(side='left', padx=5)
        
        ttk.Button(btn_fr, text="🛠 Manage Columns", command=self.open_column_manager).pack(side='right', padx=5)

        # 2. TOP HEADER GRID
        top_grid = ttk.Frame(main_box)
        top_grid.pack(fill='x', pady=10, padx=10)
        top_grid.columnconfigure(1, weight=1) 

        # --- LEFT LOGO ---
        logo_fr = ttk.Frame(top_grid)
        logo_fr.grid(row=0, column=0, sticky='w')
        ttk.Button(logo_fr, text="Insert Left Logo", width=15, command=lambda: self.load_logo("header")).pack(side='left')
        ttk.Button(logo_fr, text="Reset", width=6, command=lambda: self.reset_logo("header")).pack(side='left', padx=2)
        self.header_logo_lbl = tk.Label(logo_fr, text="", bg="#f0f0f0") 
        self.header_logo_lbl.pack(side='left', padx=2)

        # --- CENTER: TITLE ---
        tk.Label(top_grid, text="Delivery Challan", font=("Arial", 26, "bold", "underline"), bg="white").grid(row=0, column=1)

        # --- INVOICE NO & DATE ---
        meta_fr = ttk.Frame(top_grid)
        meta_fr.grid(row=0, column=2, sticky='e', padx=(10,0))
        tk.Label(meta_fr, text="Invoice No:", font=("Arial", 9, "bold")).grid(row=0, column=0, sticky='e', padx=5)
        ttk.Entry(meta_fr, textvariable=self.quotation_no_var, width=15).grid(row=0, column=1, sticky='e')
        tk.Label(meta_fr, text="Date:", font=("Arial", 9, "bold")).grid(row=1, column=0, sticky='e', padx=5, pady=5)
        ttk.Entry(meta_fr, textvariable=self.doc_date_var, width=15).grid(row=1, column=1, sticky='e', pady=5)

        # --- RIGHT LOGO ---
        r_logo_fr = ttk.Frame(top_grid)
        r_logo_fr.grid(row=0, column=3, sticky='e', padx=(20,0))
        ttk.Button(r_logo_fr, text="Insert Right Logo", width=15, command=lambda: self.load_logo("header_right")).pack(side='left')
        ttk.Button(r_logo_fr, text="Reset", width=6, command=lambda: self.reset_logo("header_right")).pack(side='left', padx=2)
        self.header_logo_right_lbl = tk.Label(r_logo_fr, text="", bg="#f0f0f0") 
        self.header_logo_right_lbl.pack(side='left', padx=2)


        # 3. DETAILS TABLES
        details_frame = ttk.Frame(main_box)
        details_frame.pack(fill='x', expand=True, pady=5, padx=5)
        details_frame.columnconfigure(0, weight=6) 
        details_frame.columnconfigure(1, weight=4) 

        # Left Table
        left_lf = tk.LabelFrame(details_frame, bd=2, relief="groove", bg="white")
        left_lf.grid(row=0, column=0, sticky='nsew', padx=2)
        tk.Entry(left_lf, textvariable=self.left_header_title, font=("Arial", 11, "bold"), justify='center', bg="#e6f2ff", bd=0).pack(fill='x', pady=1)
        lg = tk.Frame(left_lf, bg="white")
        lg.pack(fill='both', expand=True, padx=2, pady=2)
        lg.columnconfigure(1, weight=1); lg.columnconfigure(3, weight=1)

        def l_row(idx, l1, v1, l2=None, v2=None):
            tk.Label(lg, text=l1, font=("Arial", 9, "bold"), bg="white", anchor='w').grid(row=idx, column=0, sticky='nsew', padx=1, pady=1)
            tk.Entry(lg, textvariable=v1, bd=1, relief="solid").grid(row=idx, column=1, sticky='nsew', padx=1, pady=1)
            if l2:
                tk.Label(lg, text=l2, font=("Arial", 9, "bold"), bg="white", anchor='w').grid(row=idx, column=2, sticky='nsew', padx=1, pady=1)
                tk.Entry(lg, textvariable=v2, bd=1, relief="solid").grid(row=idx, column=3, sticky='nsew', padx=1, pady=1)

        l_row(0, "Dc No:", self.quotation_no_var, "PO No.", self.rfq_no_var)
        l_row(1, "Customer:", self.client_name_var, "S.T.N. NO:", self.client_stn_var)
        l_row(2, "Address:", self.client_addr_var, "NTN:", self.client_ntn_var)
        l_row(3, "Contact person:", self.client_contact_var, "Delivery date:", self.delivery_date_var)
        l_row(4, "Designation:", self.client_designation_var, "Delivered Through:", self.delivered_through_var)
        tk.Label(lg, text="email:", font=("Arial", 9, "bold"), bg="white", anchor='w').grid(row=5, column=0, sticky='nsew', padx=1, pady=1)
        tk.Entry(lg, textvariable=self.client_email_var, bd=1, relief="solid").grid(row=5, column=1, columnspan=3, sticky='nsew', padx=1, pady=1)

        # Right Table
        right_lf = tk.LabelFrame(details_frame, bd=2, relief="groove", bg="white")
        right_lf.grid(row=0, column=1, sticky='nsew', padx=2)
        tk.Entry(right_lf, textvariable=self.right_header_title, font=("Arial", 11, "bold"), justify='center', bg="white", bd=0).pack(fill='x', pady=1)
        rg = tk.Frame(right_lf, bg="white")
        rg.pack(fill='both', expand=True, padx=2, pady=2)
        rg.columnconfigure(1, weight=1)

        def r_row(idx, l1, v1):
            tk.Label(rg, text=l1, font=("Arial", 9, "bold"), bg="#e6f7ff", anchor='w').grid(row=idx, column=0, sticky='nsew', padx=1, pady=1)
            tk.Entry(rg, textvariable=v1, bd=1, relief="solid").grid(row=idx, column=1, sticky='nsew', padx=1, pady=1)

        r_row(0, "Quotation No.", self.ref_quot_no_var)
        r_row(1, "DC No", self.dc_no_var)
        r_row(2, "S.T.N. No.", self.vendor_stn_var)
        r_row(3, "NTN:", self.vendor_ntn_var)
        r_row(4, "PRA:", self.vendor_pra_var)
        tk.Label(rg, text="email:", font=("Arial", 9, "bold"), bg="white", anchor='e').grid(row=5, column=0, sticky='nsew', padx=1, pady=1)
        tk.Entry(rg, textvariable=self.vendor_email_var, bd=0, relief="flat", fg="blue", bg="white").grid(row=5, column=1, sticky='nsew', padx=1, pady=1)

    def _build_bottom_section(self, parent):
        bot = ttk.Frame(parent, padding=10)
        bot.pack(fill='both', expand=True, pady=10)
        bot.columnconfigure(0, weight=7); bot.columnconfigure(1, weight=3)

        # --- LEFT: DYNAMIC INPUTS ---
        left_frame = ttk.LabelFrame(bot, text="Transport & Logistics Details")
        left_frame.grid(row=0, column=0, sticky="nsew", padx=5)

        # 1. Purpose
        p_frame = tk.Frame(left_frame); p_frame.pack(fill='x', pady=2)
        tk.Label(p_frame, text="Purpose:", font=("bold")).pack(side='left')
        tk.Checkbutton(p_frame, text="Sale", variable=self.purpose_sale_var).pack(side='left')
        tk.Checkbutton(p_frame, text="Job Work", variable=self.purpose_job_var).pack(side='left')
        tk.Checkbutton(p_frame, text="Returnable", variable=self.purpose_ret_var).pack(side='left')
        tk.Checkbutton(p_frame, text="Non-Returnable", variable=self.purpose_nonret_var).pack(side='left')
        # 2. Source Selection (Triggers)
        src_frame = tk.Frame(left_frame, bg="#eef"); src_frame.pack(fill='x', pady=5, padx=2)
        tk.Label(src_frame, text="Source of Transport:", font=("bold"), bg="#eef").pack(side='left', padx=5)
        
        # Update UI on click
        tk.Checkbutton(src_frame, text="Public", variable=self.source_public_var, bg="#eef", command=self.update_ui_visibility).pack(side='left')
        tk.Checkbutton(src_frame, text="Special", variable=self.source_special_var, bg="#eef", command=self.update_ui_visibility).pack(side='left')
        tk.Checkbutton(src_frame, text="Other", variable=self.source_other_var, bg="#eef").pack(side='left')

        # --- DYNAMIC FRAMES ---
        
        # A. PUBLIC TRANSPORT SECTION
        self.public_section_frame = tk.Frame(left_frame, bd=1, relief="groove")
        
        # Mode Selection (Triggers Details)
        mode_fr = tk.Frame(self.public_section_frame); mode_fr.pack(fill='x', pady=2)
        tk.Label(mode_fr, text="Mode:", font=("bold")).pack(side='left', padx=5)
        
        # ✅ FIX: Sab buttons par command laga di hai
        tk.Checkbutton(mode_fr, text="Cargo", variable=self.mode_cargo_var, command=self.update_ui_visibility).pack(side='left')
        tk.Checkbutton(mode_fr, text="Courier", variable=self.mode_courier_var, command=self.update_ui_visibility).pack(side='left')
        tk.Checkbutton(mode_fr, text="Rail/Air", variable=self.mode_rail_var, command=self.update_ui_visibility).pack(side='left')
        tk.Checkbutton(mode_fr, text="Other", variable=self.mode_air_var, command=self.update_ui_visibility).pack(side='left')

        # Transport Details (Common Input Area)
        self.cargo_details_frame = tk.Frame(self.public_section_frame, bg="#f9f9f9")
        
        def entry_row(parent, lbl_txt, var, width=15):
            f = tk.Frame(parent, bg="#f9f9f9"); f.pack(side='left', padx=5, pady=2)
            tk.Label(f, text=lbl_txt, font=("Arial", 8), bg="#f9f9f9").pack(anchor='w')
            tk.Entry(f, textvariable=var, width=width).pack()

        row1 = tk.Frame(self.cargo_details_frame, bg="#f9f9f9"); row1.pack(fill='x')
        entry_row(row1, "Transport Name", self.trans_by_var, 25)
        entry_row(row1, "Bilty/Receipt No", self.bilty_no_var, 15)
        entry_row(row1, "Booking Date", self.booking_date_var, 12)
        entry_row(row1, "Charges", self.trans_charges_var, 10)
        
        row2 = tk.Frame(self.cargo_details_frame, bg="#f9f9f9"); row2.pack(fill='x')
        entry_row(row2, "Cargo Address", self.cargo_address_var, 60)

        # B. SPECIAL VEHICLE SECTION
        self.special_section_frame = tk.Frame(left_frame, bd=1, relief="groove", bg="#fff8e1")
        tk.Label(self.special_section_frame, text="Special Vehicle Details", font=("bold"), bg="#fff8e1").pack(anchor='w', padx=5)
        
        sp_row = tk.Frame(self.special_section_frame, bg="#fff8e1"); sp_row.pack(fill='x', pady=2)
        def sp_entry(lbl, var, w):
            f = tk.Frame(sp_row, bg="#fff8e1"); f.pack(side='left', padx=5)
            tk.Label(f, text=lbl, bg="#fff8e1").pack(side='left')
            tk.Entry(f, textvariable=var, width=w).pack(side='left', padx=2)

        sp_entry("Vehicle No:", self.vehicle_num_var, 12)
        sp_entry("Date:", self.trans_date_var, 12)
        sp_entry("Driver/CNIC:", self.driver_cnic_var, 20)

        # Initialize Visibility
        self.update_ui_visibility()

        # --- RIGHT SIDE (Logos) ---
        right_frame = ttk.Frame(bot)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=10)
        
        self.terms_txt = tk.Text(right_frame, height=0, width=0); self.terms_txt.pack(side='top', pady=0) 
        fin_box = ttk.Frame(right_frame); fin_box.pack(fill='x', pady=(0, 10))
        self.total_lbl = ttk.Label(fin_box, text="Net Amount: 0.00", font=("Segoe UI", 12, "bold"), foreground="blue"); self.total_lbl.pack(side='right')

        # Box Logo
        box_logo_fr = ttk.LabelFrame(right_frame, text="1. 'Delivered By' Box Logo")
        box_logo_fr.pack(fill='x', pady=5)
        b1 = ttk.Frame(box_logo_fr); b1.pack(fill='x', pady=5)
        ttk.Button(b1, text="Upload Box Logo", command=lambda: self.load_logo("delivered")).pack(side='left', padx=5)
        ttk.Button(b1, text="Reset", width=6, command=lambda: self.reset_logo("delivered")).pack(side='left', padx=2)
        self.delivered_logo_lbl = ttk.Label(b1, text="(None)", foreground="grey"); self.delivered_logo_lbl.pack(side='left')

        # Footer Sticker
        foot_logo_fr = ttk.LabelFrame(right_frame, text="2. Page Footer Logo (Sticker)")
        foot_logo_fr.pack(fill='x', pady=5)
        b2 = ttk.Frame(foot_logo_fr); b2.pack(fill='x', pady=5)
        ttk.Button(b2, text="Upload Sticker", command=lambda: self.load_logo("footer")).pack(side='left', padx=5)
        ttk.Button(b2, text="Reset", width=6, command=lambda: self.reset_logo("footer")).pack(side='left', padx=2)
        self.footer_logo_lbl = ttk.Label(b2, text="(None)", foreground="grey"); self.footer_logo_lbl.pack(side='left')
        
        sett_row = ttk.Frame(foot_logo_fr); sett_row.pack(fill='x', pady=5, padx=5)
        ttk.Label(sett_row, text="Align:").pack(side='left')
        ttk.Combobox(sett_row, textvariable=self.footer_align_var, values=["Left", "Center", "Right"], width=8, state="readonly").pack(side='left', padx=5)
        ttk.Label(sett_row, text="Size:").pack(side='left', padx=(10,0))
        ttk.Scale(sett_row, variable=self.f_logo_size_var, from_=1.0, to=5.0, length=60).pack(side='left', padx=5)
        
        # Restore Missing Footer Text & Settings
        ft_txt_fr = ttk.Frame(foot_logo_fr); ft_txt_fr.pack(fill='x', pady=5, padx=5)
        ttk.Label(ft_txt_fr, text="Footer Text:").pack(side='left')
        ttk.Entry(ft_txt_fr, textvariable=self.footer_text_var).pack(side='left', fill='x', expand=True, padx=5)
        
        ft_opt_fr = ttk.Frame(foot_logo_fr); ft_opt_fr.pack(fill='x', pady=2, padx=5)
        ttk.Checkbutton(ft_opt_fr, text="Pin to Bottom", variable=self.footer_pin_to_bottom_var).pack(side='left', padx=5)
        ttk.Checkbutton(ft_opt_fr, text="Full Width", variable=self.footer_full_width_var).pack(side='left', padx=5)

        ttk.Button(right_frame, text="👁 PREVIEW PDF", style="Action.TButton", command=self.on_preview_click).pack(fill='x', ipady=10, pady=20)

    def on_preview_click(self):
        """PDF Preview logic for Delivery Challan (Robust Threading)"""
        import threading
        
        # 1. Pre-fetch ALL data from UI thread (CRITICAL for thread safety)
        # try:
        #     ui_data = {
        #         "quotation_no": self.quotation_no_var.get(),
        #         "doc_date": self.doc_date_var.get(),
        #         "rfq_no": self.rfq_no_var.get(),
        #         "ref_quot_no": self.ref_quot_no_var.get(),
        #         "client_name": self.client_name_var.get(),
        #         "client_stn": self.client_stn_var.get(),
        #         "dc_no": self.dc_no_var.get(),
        #         "client_addr": self.client_addr_var.get(),
        #         "client_ntn": self.client_ntn_var.get(),
        #         "vendor_stn": self.vendor_stn_var.get(),
        #         "client_contact": self.client_contact_var.get(),
        #         "delivery_date": self.delivery_date_var.get(),
        #         "vendor_ntn": self.vendor_ntn_var.get(),
        #         "client_designation": self.client_designation_var.get(),
        #         "delivered_through": self.delivered_through_var.get(),
        #         "vendor_pra": self.vendor_pra_var.get(),
        #         "client_email": self.client_email_var.get(),
        #         "vendor_email": self.vendor_email_var.get(),
        #         "left_header": self.left_header_title.get(),
        #         "right_header": self.right_header_title.get(),
        #         "tagged_terms": self._get_tagged_text(),
        #         "footer_logo_size": self.f_logo_size_var.get(),
        #         "footer_align": self.footer_align_var.get(),
        #         "items_data": copy.deepcopy(self.items_data)
        #         "header_logo_path": self.header_logo_path,
        #         "header_logo_right_path": self.header_logo_right_path,
        #         "delivered_logo_path": self.delivered_logo_path,
        #         "footer_logo_path": self.footer_logo_path
        #     }
        try:
            ui_data = {
                "quotation_no": self.quotation_no_var.get(),
                "doc_date": self.doc_date_var.get(),
                "rfq_no": self.rfq_no_var.get(),
                "ref_quot_no": self.ref_quot_no_var.get(),
                "client_name": self.client_name_var.get(),
                "client_stn": self.client_stn_var.get(),
                "dc_no": self.dc_no_var.get(),
                "client_addr": self.client_addr_var.get(),
                "client_ntn": self.client_ntn_var.get(),
                "vendor_stn": self.vendor_stn_var.get(),
                "client_contact": self.client_contact_var.get(),
                "delivery_date": self.delivery_date_var.get(),
                "vendor_ntn": self.vendor_ntn_var.get(),
                "client_designation": self.client_designation_var.get(),
                "delivered_through": self.delivered_through_var.get(),
                "vendor_pra": self.vendor_pra_var.get(),
                "client_email": self.client_email_var.get(),
                "vendor_email": self.vendor_email_var.get(),
                "left_header": self.left_header_title.get(),
                "right_header": self.right_header_title.get(),
                "tagged_terms": self._get_tagged_text(),
                "footer_logo_size": self.f_logo_size_var.get(),
                "footer_align": self.footer_align_var.get(),
                "items_data": copy.deepcopy(self.items_data),
                
                # --- YE CHAR LINES ADD KAREIN ---
                "header_logo_path": self.header_logo_path,
                "header_logo_right_path": self.header_logo_right_path,
                "delivered_logo_path": self.delivered_logo_path,
                "footer_logo_path": self.footer_logo_path
            }
        except Exception as e:
            messagebox.showerror("UI Data Error", f"Failed to read UI fields: {e}")
            return

        # 2. Show Waiting Window
        wait = tk.Toplevel(self.root)
        wait.title("Please Wait")
        wait.geometry("350x120")
        wait.resizable(False, False)
        wait.transient(self.root)
        # ✅ FIX: Don't use grab_set - it blocks the UI
        # wait.grab_set()
        
        try:
            root_x = self.root.winfo_x()
            root_y = self.root.winfo_y()
            root_w = self.root.winfo_width()
            root_h = self.root.winfo_height()
            wait.geometry(f"+{root_x + (root_w//2) - 175}+{root_y + (root_h//2) - 60}")
        except: pass

        tk.Label(wait, text="🔄 Generating Delivery Challan PDF...", font=("Arial", 12, "bold"), fg="#2c3e50").pack(pady=10)
        tk.Label(wait, text="This might take a few seconds...", font=("Arial", 9), fg="grey").pack()
        self.root.update()

        def worker():
            try:
                import tempfile
                fd, tmp_path = tempfile.mkstemp(suffix=".pdf")
                os.close(fd)
                
                # Use pre-fetched data inside _generate_pdf
                self._generate_pdf(tmp_path, ui_data_payload=ui_data) 
                
                def finish():
                    # ✅ RESTORED: Call confirmation popup with Save As options
                    if os.path.exists(tmp_path):
                        self._show_preview_confirm(tmp_path, wait)
                    else:
                        try:
                            if wait.winfo_exists(): wait.destroy()
                        except: pass
                        messagebox.showerror("Error", "Preview file could not be created.")
                        
                self.root.after(0, finish)
            except Exception as e:
                err_msg = str(e)
                def on_err():
                    try:
                        if wait.winfo_exists():
                            wait.destroy()
                    except: pass
                    messagebox.showerror("Preview Error", f"Failed to generate PDF:\n{err_msg}")
                self.root.after(0, on_err)

        threading.Thread(target=worker, daemon=True).start()

    def _open_pdf(self, path):
        try:
            if os.name == 'nt':
                os.startfile(path)
            else:
                import webbrowser
                webbrowser.open("file://" + path)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open PDF: {e}")

    # ✅ LOGIC UPDATE: Check ALL modes
    def load_logo(self, which):
        """Override parent's load_logo to handle Delivery Challan specific logos"""
        from tkinter import filedialog
        from PIL import Image, ImageTk
        
        # Use parent=self.root to keep dialog attached to window
        # And raise window after selection to prevent it going behind
        path = filedialog.askopenfilename(parent=self.root, filetypes=[("Images", "*.png;*.jpg;*.jpeg")])
        
        # Force window to top after closing dialog
        self.root.lift()
        self.root.focus_force()
        
        if not path: return
        
        # Map logo types to their paths and labels
        lbl = None
        if which == "header":
            self.header_logo_path = path
            lbl = self.header_logo_lbl if hasattr(self, 'header_logo_lbl') else None
        elif which == "header_right":
            self.header_logo_right_path = path
            # Right header usually doesn't have a preview label in this UI context, 
            # but if it does, add logic here. For now, assume None.
            lbl = None  
        elif which == "delivered":
            self.delivered_logo_path = path
            lbl = self.delivered_logo_lbl
        elif which == "footer":
            self.footer_logo_path = path
            lbl = self.footer_logo_lbl
        else:
            # Fallback to parent implementation for standard types
            super().load_logo(which)
            return
        
        # Update label with thumbnail preview
        if lbl:
            try:
                img = Image.open(path)
                img.thumbnail((30, 30)) # Slightly smaller thumbnail
                photo = ImageTk.PhotoImage(img)
                lbl.config(image=photo, text="")
                lbl.image = photo  # Keep reference
            except Exception as e:
                lbl.config(text=f"✓ Loaded", foreground="green")

    def reset_logo(self, which):
        """Reset the specified logo."""
        lbl = None
        if which == "header":
            self.header_logo_path = None
            lbl = self.header_logo_lbl
        elif which == "header_right":
            self.header_logo_right_path = None
            lbl = self.header_logo_right_lbl
        elif which == "delivered":
            self.delivered_logo_path = None
            lbl = self.delivered_logo_lbl
        elif which == "footer":
            self.footer_logo_path = None
            lbl = self.footer_logo_lbl
        
        if lbl:
            lbl.config(image='', text="(None)")
            lbl.image = None
    
    def update_ui_visibility(self):
        if self.source_public_var.get():
            self.public_section_frame.pack(fill='x', pady=5, padx=5)
            
            # ✅ LOGIC FIX: Check if ANY mode is selected
            any_mode_selected = (
                self.mode_cargo_var.get() or 
                self.mode_courier_var.get() or 
                self.mode_rail_var.get() or 
                self.mode_air_var.get()
            )
            
            if any_mode_selected:
                self.cargo_details_frame.pack(fill='x', pady=5, padx=5)
            else:
                self.cargo_details_frame.pack_forget()
        else:
            self.public_section_frame.pack_forget()

        # 2. Special Logic
        if self.source_special_var.get():
            self.special_section_frame.pack(fill='x', pady=5, padx=5)
        else:
            self.special_section_frame.pack_forget()


    # Recalc Override
    def recalc_all(self):
        # Ye line crash rokegi agar total_lbl abhi screen pe nahi bana
        if not hasattr(self, 'total_lbl'): return 
        
        super().recalc_all()
        
        # Calculate Net Amount for display
        net_total = 0.0
        for i in self.items_data:
            net_total += i.get('total', 0.0)
        
        curr = (hasattr(self, 'currency_symbol_var') and self.currency_symbol_var.get()) or "PKR"
        self.total_lbl.config(text=f"Net Amount: {curr} {net_total:,.2f}")
    # ... (Upar wale functions) ...

    def _get_scaled_image(self, path, width_inch):
        # Agar path khali hai ya file exist nahi karti to wapis jao
        if not path or not os.path.exists(path): return None
        
        try:
            from reportlab.lib.units import inch
            from reportlab.platypus import Image as RLImage
            
            # 1. PIL use karke Image ka size lo (Ye method ziyada pakka hai)
            pil_img = Image.open(path)
            iw, ih = pil_img.size
            
            # 2. Aspect Ratio calculation
            aspect = ih / float(iw)
            w = width_inch * inch
            h = w * aspect
            
            # 3. ReportLab Image Object return karo
            return RLImage(path, width=w, height=h)
        except Exception as e:
            # Agar koi error aye to console main print karo taake pata chale
            print(f"Logo Error ({path}): {e}")
            return None
    
    

    #     doc.build(elements, onFirstPage=canvas_setup, onLaterPages=canvas_setup)
    def _generate_pdf(self, path, pre_fetched_terms=None, ui_data_payload=None):
        if not os.path.dirname(path): return

        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage, KeepTogether
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT, TA_JUSTIFY
        from reportlab.lib.units import inch
        from reportlab.lib import colors

        # Use pre-fetched data if provided (thread-safe), otherwise fall back to self
        if ui_data_payload:
            d = ui_data_payload
        else:
            # Fallback: read from self
            d = {
                "quotation_no": self.quotation_no_var.get(),
                "doc_date": self.doc_date_var.get(),
                "rfq_no": self.rfq_no_var.get(),
                "ref_quot_no": self.ref_quot_no_var.get(),
                "client_name": self.client_name_var.get(),
                "client_stn": self.client_stn_var.get(),
                "dc_no": self.dc_no_var.get(),
                "client_addr": self.client_addr_var.get(),
                "client_ntn": self.client_ntn_var.get(),
                "vendor_stn": self.vendor_stn_var.get(),
                "client_contact": self.client_contact_var.get(),
                "delivery_date": self.delivery_date_var.get(),
                "vendor_ntn": self.vendor_ntn_var.get(),
                "client_designation": self.client_designation_var.get(),
                "delivered_through": self.delivered_through_var.get(),
                "vendor_pra": self.vendor_pra_var.get(),
                "client_email": self.client_email_var.get(),
                "vendor_email": self.vendor_email_var.get(),
                "left_header": self.left_header_title.get(),
                "right_header": self.right_header_title.get(),
                "tagged_terms": pre_fetched_terms or "",
                "footer_logo_size": self.f_logo_size_var.get(),
                "footer_align": self.footer_align_var.get(),
                "items_data": self.items_data,
                # Logos paths added to fallback for safety
                "header_logo_path": self.header_logo_path,
                "header_logo_right_path": self.header_logo_right_path
            }

        # ✅ 1. STYLES
        styles = getSampleStyleSheet()
        norm_style = styles['Normal']
        
        head_style = ParagraphStyle('HeadStyle', parent=norm_style, fontName='Helvetica-Bold', fontSize=9, alignment=TA_CENTER)
        item_norm = ParagraphStyle('ItemNorm', parent=norm_style, fontSize=9, leading=11)
        item_num = ParagraphStyle('ItemNum', parent=norm_style, fontSize=9, alignment=TA_RIGHT)
        red_note_style = ParagraphStyle('RedNote', parent=norm_style, fontSize=8, alignment=TA_CENTER, 
                                        textColor=colors.red, fontName='Helvetica-Bold')

        # 2. TEMPLATE SETUP
        MARGIN = 20 
        doc = SimpleDocTemplate(path, pagesize=A4, rightMargin=MARGIN, leftMargin=MARGIN, 
                                topMargin=0.4*inch, bottomMargin=80) 
        elements = []
        
        # --- 3. HEADER SECTION (Corrected to use d.get) ---
        img_left = self._get_scaled_image(d.get('header_logo_path'), 1.2)
        img_right = self._get_scaled_image(d.get('header_logo_right_path'), 1.2)
        
        center_html = f"""<font size="24" name="Helvetica-Bold">DELIVERY CHALLAN</font><br/>
                          <font size="10" name="Helvetica"><b>Invoice No:</b> {d['quotation_no']} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Date:</b> {d['doc_date']}</font>"""
        center_style = ParagraphStyle('Center', parent=norm_style, alignment=TA_CENTER, leading=25)
        
        cw = 540
        t_head = Table([[img_left if img_left else "", Paragraph(center_html, center_style), img_right if img_right else ""]], 
                         colWidths=[cw*0.20, cw*0.60, cw*0.20])
        t_head.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('ALIGN', (1,0), (1,0), 'CENTER'), ('TOPPADDING', (1,0), (1,0), 5)]))
        elements.append(t_head)
        elements.append(Spacer(1, 15))

        # --- 4. CONSOLIDATED INFO TABLE ---
        def mk_b(txt): return Paragraph(f"<b>{txt}</b>", ParagraphStyle('b', parent=norm_style, fontSize=8))
        def mk_n(txt): return Paragraph(str(txt or ""), ParagraphStyle('n', parent=norm_style, fontSize=8))
        title_b = ParagraphStyle('tb', parent=norm_style, fontSize=10, alignment=TA_CENTER, fontName='Helvetica-Bold')

        # info_widths = [65, 120, 65, 95, 75, 120] 
        
        # info_data = [
        #     [Paragraph(d['left_header'], title_b), "", "", "", Paragraph(d['right_header'], title_b), ""],
        #     [mk_b("DC No:"), mk_n(d['quotation_no']), mk_b("PO No."), mk_n(d['rfq_no']), mk_b("Quotation No."), mk_n(d['ref_quot_no'])],
        #     [mk_b("Customer:"), mk_n(d['client_name']), mk_b("S.T.N. NO:"), mk_n(d['client_stn']), mk_b("DC No"), mk_n(d['dc_no'])],
        #     [mk_b("Address:"), mk_n(d['client_addr']), mk_b("NTN:"), mk_n(d['client_ntn']), mk_b("S.T.N. No."), mk_n(d['vendor_stn'])],
        #     [mk_b("Contact person:"), mk_n(d['client_contact']), mk_b("Delivery date:"), mk_n(d['delivery_date']), mk_b("NTN:"), mk_n(d['vendor_ntn'])],
        #     [mk_b("Designation:"), mk_n(d['client_designation']), mk_b("Delivered Through:"), mk_n(d['delivered_through']), mk_b("PRA:"), mk_n(d['vendor_pra'])],
        #     [mk_b("email:"), mk_n(d['client_email']), "", "", mk_b("email:"), mk_n(d['vendor_email'])]
        # ]
        
        # t_info = Table(info_data, colWidths=info_widths)
        # t_info.setStyle(TableStyle([
        #     ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        #     ('SPAN', (0,0), (3,0)), 
        #     ('SPAN', (4,0), (5,0)), 
        #     ('SPAN', (1,6), (3,6)),
        #     ('BACKGROUND', (0,0), (3,0), colors.whitesmoke), 
        #     ('BACKGROUND', (4,0), (5,0), colors.whitesmoke), 
        #     ('BACKGROUND', (0,1), (0,-1), colors.whitesmoke), 
        #     ('BACKGROUND', (2,1), (2,-2), colors.whitesmoke), 
        #     ('BACKGROUND', (4,1), (4,-1), colors.whitesmoke), 
        #     ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        #     ('ALIGN', (0,0), (-1,0), 'CENTER'),
        # ]))
        # elements.append(t_info)
        # elements.append(Spacer(1, 15))

        # Weights: [LabelL, ValL, LabelL2, ValL2, LabelR, ValR]
        # Total Content Width (CW) = 540
        info_widths = [65, 120, 65, 95, 75, 120] # Sum = 540
        
        info_data = [
            # Row 0: Headers
            [Paragraph(d['left_header'], title_b), "", "", "", Paragraph(d['right_header'], title_b), ""],
            # Row 1: DC No, PO No, Quot No
            [mk_b("DC No:"), mk_n(d['quotation_no']), mk_b("PO No."), mk_n(d['rfq_no']), mk_b("Quotation No."), mk_n(d['ref_quot_no'])],
            # Row 2: Customer, STN, DC No (Vendor)
            [mk_b("Customer:"), mk_n(d['client_name']), mk_b("S.T.N. NO:"), mk_n(d['client_stn']), mk_b("DC No"), mk_n(d['dc_no'])],
            # Row 3: Address, NTN, STN (Vendor)
            [mk_b("Address:"), mk_n(d['client_addr']), mk_b("NTN:"), mk_n(d['client_ntn']), mk_b("S.T.N. No."), mk_n(d['vendor_stn'])],
            # Row 4: Contact, Del Date, NTN (Vendor)
            [mk_b("Contact person:"), mk_n(d['client_contact']), mk_b("Delivery date:"), mk_n(d['delivery_date']), mk_b("NTN:"), mk_n(d['vendor_ntn'])],
            # Row 5: Designation, Through, PRA
            [mk_b("Designation:"), mk_n(d['client_designation']), mk_b("Delivered Through:"), mk_n(d['delivered_through']), mk_b("PRA:"), mk_n(d['vendor_pra'])],
            # Row 6: email (Client), email (Vendor)
            [mk_b("email:"), mk_n(d['client_email']), "", "", mk_b("email:"), mk_n(d['vendor_email'])]
        ]
        
        t_info = Table(info_data, colWidths=info_widths)
        t_info.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            # Spans for Headers
            ('SPAN', (0,0), (3,0)), # Client Header
            ('SPAN', (4,0), (5,0)), # Vendor Header
            # Span for email
            ('SPAN', (1,6), (3,6)),
            # Stylish backgrounds
            ('BACKGROUND', (0,0), (3,0), colors.whitesmoke), # Client Header BG
            ('BACKGROUND', (4,0), (5,0), colors.whitesmoke), # Vendor Header BG
            # Label backgrounds
            ('BACKGROUND', (0,1), (0,-1), colors.whitesmoke), # Col 0 labels
            ('BACKGROUND', (2,1), (2,-2), colors.whitesmoke), # Col 2 labels 
            ('BACKGROUND', (4,1), (4,-1), colors.whitesmoke), # Col 4 labels
            # Alignments
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ]))
        elements.append(t_info)
        elements.append(Spacer(1, 15))

        # --- 5. ITEMS TABLE ---
        print_cols = [c for c in self.columns_config if c.get('printable', True)]
        data = [[Paragraph(f"<b>{c['label']}</b>", head_style) for c in print_cols]]
        for item in d['items_data']:
            row = []
            for c in print_cols:
                val = item.get(c['id'], "")
                p_style = item_norm
                if c['type'] in ['number', 'calc', 'global_pct']:
                    try: val = f"{float(val):,.2f}"; p_style = item_num
                    except: pass
                # Leading adjust kiya
                p_style.leading = 9
                row.append(Paragraph(str(val).replace("\n", "<br/>"), p_style))
            data.append(row)
        
        if len(print_cols) > 0:
            # DYNAMIC COLUMN WIDTH LOGIC: PROPORTIONAL SCALING
            CW = 540 # Total Page Content Width (7.5 inch approx)
            
            # 1. Get Raw Widths from Config
            raw_widths = [float(c.get('width', 50)) for c in print_cols]
            total_raw = sum(raw_widths)
            
            # 2. Calculate Scale Factor
            if total_raw == 0: total_raw = 1 
            scale_factor = CW / total_raw
            
            # 3. Apply Scale Factor to create PDF Widths
            pdf_col_widths = [w * scale_factor for w in raw_widths]
            
            t_items = Table(data, colWidths=pdf_col_widths, repeatRows=1)
            t_items.setStyle(TableStyle([
                ('GRID', (0,0), (-1,-1), 0.5, colors.black), 
                ('BACKGROUND', (0,0), (-1,0), colors.lightgrey), 
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('TOPPADDING', (0,0), (-1,-1), 4),
                ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ]))
            elements.append(t_items)
        
        elements.append(Spacer(1, 15))

        # ✅ 6. TRANSPORT & SIGNATURES (SPECIAL MODE FIX & TICK MARK)
        # Yahan hum KeepTogether hatayeinge taake tables separate pages pe split ho sakein
        grid_style = [('GRID', (0,0), (-1,-1), 0.5, colors.black), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('LEFTPADDING', (0,0), (-1,-1), 5)]
        
        def get_tick(val):
            # Symbol font use kar ke Tick mark dikhayen
            mark = "<b>&#x2713;</b>" if val else "" 
            return Paragraph(f'<font name="Helvetica-Bold" size="10" color="green">[ {mark} ]</font> ', item_norm)

        # Purpose, Declaration, Source Tables... (Same as before)
        elements.append(Table([[mk_b("Purpose:"), 
                               Paragraph(f"{get_tick(self.purpose_sale_var.get()).text} Sale", item_norm), 
                               Paragraph(f"{get_tick(self.purpose_job_var.get()).text} Job", item_norm), 
                               Paragraph(f"{get_tick(self.purpose_ret_var.get()).text} Returnable", item_norm), 
                               Paragraph(f"{get_tick(self.purpose_nonret_var.get()).text} Non-Returnable", item_norm)]], 
                             colWidths=[1.4*inch, 1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch], style=grid_style))
        
        elements.append(Table([[mk_b("Declaration:"), Paragraph("Goods delivered in good condition.", item_norm)]], colWidths=[1.4*inch, 6.0*inch], style=grid_style))
        
        elements.append(Table([[mk_b("Source:"), 
                               Paragraph(f"{get_tick(self.source_public_var.get()).text} Public", item_norm), 
                               Paragraph(f"{get_tick(self.source_special_var.get()).text} Special", item_norm), 
                               Paragraph(f"{get_tick(self.source_other_var.get()).text} Other", item_norm), ""]], 
                             colWidths=[1.4*inch, 1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch], style=grid_style))

        # ✅ SPECIAL VEHICLE DATA (Fixing the crash)
        if self.source_special_var.get():
            v_data = [[mk_b("Special Vehicle:"), 
                       mk_n(f"Vehicle No: {self.vehicle_num_var.get()}"), 
                       mk_n(f"Date: {self.trans_date_var.get()}"), 
                       mk_n(f"Driver: {self.driver_cnic_var.get()}")]]
            # Split allowed=True is important here
            t_veh = Table(v_data, colWidths=[1.4*inch, 2.0*inch, 1.2*inch, 2.8*inch], splitByRow=True)
            t_veh.setStyle(TableStyle(grid_style + [('BACKGROUND', (0,0), (-1,-1), colors.whitesmoke)]))
            elements.append(t_veh)

        # ✅ PUBLIC MODE DATA
        if self.source_public_var.get():
            c_h = ["", mk_b("Transport Name"), mk_b("Bilty #"), mk_b("Date"), mk_b("Charges"), mk_b("Address")]
            c_v = ["", mk_n(self.trans_by_var.get()), mk_n(self.bilty_no_var.get()), mk_n(self.booking_date_var.get()), mk_n(self.trans_charges_var.get()), mk_n(self.cargo_address_var.get())]
            t_cargo = Table([c_h, c_v], colWidths=[0.1*inch, 1.4*inch, 1.2*inch, 1.2*inch, 0.8*inch, 2.7*inch], splitByRow=True)
            t_cargo.setStyle(TableStyle(grid_style + [('BACKGROUND', (0,0), (-1,0), colors.whitesmoke)]))
            elements.append(t_cargo)

        # Signatures section (Use pre-fetched logo path)
        sig_hd = [mk_b("Received By"), mk_b("Signature"), mk_b("Delivered By"), mk_b("Admin Signature")]
        delivered_logo = self._get_scaled_image(d.get('delivered_logo_path'), 1.2) if d.get('delivered_logo_path') else Spacer(1, 30)
        # sig_ct = [Spacer(1, 45), Spacer(1, 45), delivered_logo, Spacer(1, 45)]
        sig_ct = [Spacer(1, 45), Spacer(1, 45), delivered_logo, Spacer(1, 45)]
        t_sig = Table([sig_hd, sig_ct], colWidths=[1.85*inch]*4, style=[('GRID', (0,0), (-1,-1), 0.5, colors.black), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('ALIGN', (0,0), (-1,-1), 'CENTER'), ('BACKGROUND', (0,0), (-1,0), colors.whitesmoke)])
        
        # Wrapping signatures in KeepTogether to keep them on one page
        from reportlab.platypus import KeepTogether
        elements.append(KeepTogether([t_sig, Spacer(1, 8), Paragraph("Note: This is a system generated document so no need to sign.", red_note_style)]))

        # ✅ 7. CANVAS SETUP (QR & Social Links) - Use pre-fetched footer logo path
        # (Aapka maujooda canvas_setup logic...)
        qr_link = "https://www.orientmarketing.com.pk/"
        qr_img = self._generate_qr_code(qr_link, size_inch=0.4) 
        # footer_logo_obj = self._get_scaled_image(d.get('footer_logo_path'), d['footer_logo_size']) if d.get('footer_logo_path') else None
        footer_logo_path = d.get('footer_logo_path')
        footer_logo_obj = self._get_scaled_image(footer_logo_path, d['footer_logo_size']) if footer_logo_path else None
        def canvas_setup(canvas, doc):
            canvas.saveState()
            if qr_img:
                qx, qy = A4[0]-MARGIN-0.4*inch, 15
                qr_img.drawOn(canvas, qx, qy)
                canvas.linkURL(qr_link, (qx, qy, qx+0.4*inch, qy+0.4*inch), relative=0)
            
            # Social Links Logic...
            social_links = [('#0066cc', 'W', 'https://www.orientmarketing.com.pk/'), ('#FF0000', 'Y', 'https://www.youtube.com/@Antarc-Technologies'), ('#1877F2', 'f', 'https://www.facebook.com/orientmarketing.com.pk'), ('#E4405F', 'I', 'https://www.instagram.com/orientmarketinghvac/')]
            for idx, (color, sym, url) in enumerate(social_links):
                x, y = MARGIN + idx*17, 15
                canvas.setFillColor(color); canvas.rect(x, y, 12, 12, fill=1, stroke=0)
                canvas.setFillColor(colors.white); canvas.setFont("Helvetica-Bold", 8); canvas.drawString(x+3, y+3, sym)
                canvas.linkURL(url, (x, y, x+12, y+12), relative=0)

            if footer_logo_obj:
                w = footer_logo_obj.drawWidth
                align = d['footer_align']
                x_pos = (A4[0]-w)/2 if align == "Center" else (A4[0]-MARGIN-w if align == "Right" else MARGIN)
                footer_logo_obj.drawOn(canvas, x_pos, 10)
            canvas.restoreState()

        doc.build(elements, onFirstPage=canvas_setup, onLaterPages=canvas_setup)
    # --- Save & Utils ---
    def check_license(self): pass 
    def check_user_login(self): pass
    # --- 3. SAVE LOGIC (Delivery Challan) ---
    def save_to_database(self, silent=False):
        if not hasattr(self, 'cursor'): self.init_database()
        
        import json
        data_packet = {
            "header": {
                "ref_no": self.dc_no_var.get(), # Verify variable name
                "date": self.doc_date_var.get(),
                "client_name": self.client_name_var.get()
            },
            "items": self.items_data
        }
        json_str = json.dumps(data_packet)
        
        # Challan ki amount usually 0 hoti hai, ya agar aap calculate karte hain to wo variable lein
        val = 0.0 

        try:
            # Table: delivery_challans
            if self.current_db_id:
                self.cursor.execute("""
                    UPDATE delivery_challans
                    SET ref_no=?, client_name=?, date=?, grand_total=?, full_data=?
                    WHERE id=?
                """, (self.dc_no_var.get(), self.client_name_var.get(), self.doc_date_var.get(), val, json_str, self.current_db_id))
            else:
                self.cursor.execute("""
                    INSERT INTO delivery_challans (ref_no, client_name, date, grand_total, full_data)
                    VALUES (?,?,?,?,?)
                """, (self.dc_no_var.get(), self.client_name_var.get(), self.doc_date_var.get(), val, json_str))
                
                self.current_db_id = self.cursor.lastrowid
            
            self.conn.commit()
            if not silent: messagebox.showinfo("Saved", "Challan Database Updated!")
            
        except Exception as e:
            if not silent: messagebox.showerror("DB Error", str(e))
   


    # =========================================================
    #  IMPORT LOGIC (SQL Server Version)
    # =========================================================

    def open_import_dialog(self, table_name):
        """SQL Server se data fetch karke list dikhata hai."""
        
        # 1. Dialog Window Banao
        top = tk.Toplevel(self.root)
        top.title(f"Select from {table_name.replace('_', ' ').title()}")
        top.geometry("700x400")
        
        # Use make_scrollable Utility
        scrollable_content = self.make_scrollable(top)

        # 2. Treeview (List) Banao
        cols = ("ID", "Inv No", "Client", "Date", "Total")
        tree = ttk.Treeview(scrollable_content, columns=cols, show='headings', selectmode='browse', height=10)
        
        tree.heading("ID", text="ID"); tree.column("ID", width=50)
        tree.heading("Inv No", text="Doc No"); tree.column("Inv No", width=120)
        tree.heading("Client", text="Client Name"); tree.column("Client", width=250)
        tree.heading("Date", text="Date"); tree.column("Date", width=100)
        tree.heading("Total", text="Amount"); tree.column("Total", width=100)
        
        tree.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 3. SQL Server se Data Lao
        try:
            # Connect to SQLite
            db_name = "QuotationManager_Final.db"
            conn = sqlite3.connect(db_name)
            cursor = conn.cursor()
            
            # ✅ COLUMN FIX: Table ke hisaab se column name chuno
            col_inv = "inv_no"
            col_date = "date"
            
            if table_name == "delivery_challans":
                col_inv = "dc_no"   # DC table main iska naam dc_no hai
                col_date = "dc_date" # DC table main iska naam dc_date hai
            
            # Query
            query = f"SELECT id, {col_inv}, client_name, {col_date}, grand_total FROM {table_name} ORDER BY id DESC"
            
            cursor.execute(query)
            rows = cursor.fetchall()
            
            for r in rows:
                # r[0]=id, r[1]=No, r[2]=client, r[3]=date, r[4]=total
                tree.insert("", "end", values=(r[0], r[1], r[2], r[3], r[4]))
                
            conn.close()
            
        except Exception as e:
            messagebox.showerror("DB Error", f"Could not fetch data.\nMake sure '{table_name}' exists in SQLite.\n\nError: {e}")
            top.destroy()
            return

        # 4. Select Button Logic
        def on_select():
            sel = tree.selection()
            if not sel: return
            item = tree.item(sel[0])
            selected_id = item['values'][0]
            
            # Data Load function call karein
            self.load_invoice_by_id(table_name, selected_id)
            top.destroy()

        ttk.Button(scrollable_content, text="Import/Load Selected Data", command=on_select).pack(pady=10)



    def load_invoice_by_id(self, table_name, inv_id):
        """ID ke zariye SQLite se full JSON data fetch karke form fill karta hai."""
        try:
            db_name = "QuotationManager_Final.db"
            conn = sqlite3.connect(db_name)
            cursor = conn.cursor()
            
            # Query
            cursor.execute(f"SELECT full_data FROM {table_name} WHERE id=?", (inv_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                json_str = row[0]
                data = json.loads(json_str)
                
                # --- DATA MAPPING (Data wapis form mein bharna) ---
                
                # 1. Header Details
                h = data.get("header", {})
                self.client_name_var.set(h.get("client", ""))
                self.client_addr_var.set(h.get("client_addr", "") or h.get("address", ""))
                self.client_contact_var.set(h.get("client_contact", "") or h.get("contact", ""))
                self.client_email_var.set(h.get("client_email", "") or h.get("email", ""))
                
                # Import wali invoice ka number hum 'Ref Quote' ya 'PO' mein dal dete hain
                self.ref_quot_no_var.set(h.get("inv_no", ""))
                self.rfq_no_var.set(h.get("po_no", "")) 
                
                # 2. Items Transfer
                self.items_data = []
                inv_items = data.get("items", [])
                
                for item in inv_items:
                    new_item = {
                        "sno": item.get("sno", ""),
                        "desc": item.get("desc", ""),
                        "uom": item.get("uom", ""),
                        "qty": item.get("qty", 0),
                        "price": item.get("price", 0),
                        "amount": item.get("amount", 0),
                        "tax_rate": item.get("tax_rate", 0),
                        "tax_amt": item.get("tax_amt", 0),
                        "total": item.get("total", 0)
                    }
                    self.items_data.append(new_item)
                
                # 3. Refresh Screen
                self.refresh_tree()
                self.recalc_all()
                
                messagebox.showinfo("Success", f"Data Imported from {table_name}!")
                
        except Exception as e:
            messagebox.showerror("Import Error", f"Failed to load data: {e}")   
    def restore_data(self, json_str):
        # Parent ka restore call karein taake items aur header load ho jayein
        super().restore_data(json_str)
        
        data = json.loads(json_str)
        
        # Ab Transport Data wapis layen
        trans = data.get("transport", {})
        self.trans_by_var.set(trans.get("trans_by", ""))
        self.trans_date_var.set(trans.get("trans_date", ""))
        self.gate_person_var.set(trans.get("gate_person", ""))
        self.vehicle_num_var.set(trans.get("vehicle", ""))

        # Custom fields ko clear karke dobara banayen
        for widget in self.trans_inner.winfo_children():
            # Sirf custom frames udayen (Standard walon ko skip karna thora mushkil hai isliye
            # behtar hai self.extra_transport_fields list ko use karein)
            pass 
        
        # Asan tareeqa: Pehle UI clear karein, phir se standard aur custom banayen.
        # Lekin kyunke humne UI pehle hi bana li hai, hum sirf custom fields append karenge.
        
        # Purane custom fields remove karein
        for item in self.extra_transport_fields:
            item['frame'].destroy()
        self.extra_transport_fields = []

        # Saved custom fields add karein
        saved_extras = trans.get("custom_fields", [])
        if hasattr(self, 'add_custom_field_func') and self.add_custom_field_func:
            for lbl, val in saved_extras:
                self.add_custom_field_func(lbl, val)

if __name__ == "__main__":
    root = ttk.Window(themename="lumen")

    app = DeliveryChallanApp(root) 
    root.mainloop()