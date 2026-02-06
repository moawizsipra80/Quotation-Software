import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import datetime
# import sqlite3
import sqlite3
import os
import copy
from PIL import Image, ImageTk  
# ✅ REPORTLAB IMPORTS
import reportlab
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage, KeepTogether
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT, TA_JUSTIFY
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing

# Parent Class Import
from quotation import QuotationApp 

class InvoiceApp(QuotationApp):
    def __init__(self, root, from_quotation_data=None):
        self.root = root
        self.original_root = root
        self.is_invoice_window = True 
        self.root.state('zoomed') 
        self.root.lift()
        self.root.focus_force() 
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

        # Logo Paths
        self.header_logo_right_path = None
        
       
        self.current_db_id = None
        
        # 2) DB Init First (to be used by parent)
        self.init_database()
        
        # 3) Parent init
        super().__init__(root) 

        # 4) Invoice-specific overrides
        self.root.resizable(True, True)
        self.root.lift()
        self.root.focus_force()

        # 3) Invoice-specific overrides
        self.header_rows = [] 
        
        self.root.title(" Sales TAX Invoice ")
        self.doc_title_var.set("Sales Tax Invoice") 
        self.quotation_no_var.set("55")
        self.approved_by_var.set("Manager Accounts")

        if from_quotation_data:
            self.load_from_quotation_data(from_quotation_data)

        # Use parent's comprehensive editing method that allows editing ALL columns
        self.tree.bind("<Double-1>", self.on_tree_double_click)
        
        self._init_default_widths_invoice()
        
    def _init_default_widths_invoice(self):
        # Optimized default widths for Sales Tax Invoice
        opt_widths = {'sno': 25, 'uom': 35, 'qty': 45, 'price': 65, 'amount': 85, 'gst': 65, 'total': 95, 'desc': 125}
        for col in self.columns_config:
            if col['id'] in opt_widths:
                col['width'] = opt_widths[col['id']]

    #  LOAD LOGO FUNCTION
    def load_logo(self, which):
        try:
            path = filedialog.askopenfilename(
                parent=self.root, 
                filetypes=[("Images", "*.png;*.jpg;*.jpeg")]
            )
            self.root.lift() 
            self.root.focus_force() 

            if not path: return

            lbl = None
            if which == "header":
                self.header_logo_path = path
                lbl = self.header_logo_lbl
            elif which == "header_right":
                self.header_logo_right_path = path
                lbl = self.header_logo_right_lbl
            elif which == "footer":
                self.footer_logo_path = path
                lbl = self.footer_logo_lbl 
            
            if lbl:
                img = Image.open(path)
                img.thumbnail((40, 40))
                photo = ImageTk.PhotoImage(img)
                lbl.config(image=photo, text="")
                lbl.image = photo 
        except Exception as e:
            messagebox.showerror("Image Error", f"Failed to load image: {e}", parent=self.root)

    def on_closing(self):
        try:
            self.save_to_database(silent=True) 
            # ✅ RESTORE DASHBOARD
            if self.root.master:
                self.root.master.deiconify()
                self.root.master.lift()
                self.root.master.focus_force()
            print("✅ Invoice saved & closed cleanly")
        except Exception as e:
            print(f"Close warning (non-critical): {e}")
        finally:
            self.root.destroy() 

    def _init_standard_header_rows(self):
        self.header_rows = []

    
    def init_database(self):
        try:
            import sqlite3
            db_name = "QuotationManager_Final.db"
            self.conn = sqlite3.connect(db_name)
            self.cursor = self.conn.cursor()
        except Exception as e:
            print(f"DB Connection Error: {e}")

    def auto_save_loop(self):
        # Har 5 second baad save kare
        if hasattr(self, 'client_name_var') and self.client_name_var.get().strip():
             self.save_to_database(silent=True)
        self.root.after(5000, self.auto_save_loop)

    def go_to_dashboard(self):
        self.on_closing() 

    def _build_header_section(self, parent):
        main_box = ttk.Frame(parent)
        main_box.pack(fill='x', pady=5)
        self.items_section_frame = main_box
        # 1. Action Buttons
        btn_fr = ttk.Frame(main_box)
        btn_fr.pack(fill='x', pady=2)
        ttk.Button(btn_fr, text="💾 Save Invoice", command=self.save_to_database).pack(side='left', padx=5)
        ttk.Button(btn_fr, text="📊 Back to Dashboard", command=self.go_to_dashboard).pack(side='left', padx=5)
        
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
        ttk.Button(logo_fr, text="Insert Left Logo", width=15, command=lambda: self.load_logo("header")).pack(anchor='w')
        self.header_logo_lbl = tk.Label(logo_fr, text="", bg="#f0f0f0") 
        self.header_logo_lbl.pack(anchor='w', pady=2)

        # --- CENTER: TITLE ---
        tk.Label(top_grid, text="Sales Tax Invoice", font=("Arial", 26, "bold", "underline"), bg="white").grid(row=0, column=1)

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
        ttk.Button(r_logo_fr, text="Insert Right Logo", width=15, command=lambda: self.load_logo("header_right")).pack(anchor='e')
        self.header_logo_right_lbl = tk.Label(r_logo_fr, text="", bg="#f0f0f0") 
        self.header_logo_right_lbl.pack(anchor='e', pady=2)


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

        l_row(0, "Sale Tax Invoice No:", self.quotation_no_var, "PO No.", self.rfq_no_var)
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

    def refresh_items_ui_structure(self):
        super().refresh_items_ui_structure()
        # Naye Treeview par binding dobara apply karein
        if hasattr(self, 'tree'):
            self.tree.bind("<Double-1>", self.on_tree_double_click)
    # =========================================================
    #  4. BOTTOM SECTION
    # =========================================================
    def _build_bottom_section(self, parent):
        bot = ttk.Frame(parent, padding=10)
        bot.pack(fill='both', expand=True, pady=10)
        bot.columnconfigure(0, weight=1); bot.columnconfigure(1, weight=1); bot.columnconfigure(2, weight=1)

        # Col 1: Financial Settings (New)
        col1 = ttk.Labelframe(bot, text="Financial Settings", bootstyle="info", padding=15)
        col1.grid(row=0, column=0, sticky="nsew", padx=5)

        # Currency & Tax Rate
        r1 = ttk.Frame(col1)
        r1.pack(fill='x', pady=5)
        ttk.Label(r1, text="Currency:").pack(side='left')
        ttk.Combobox(r1, textvariable=self.currency_var, values=["PKR", "USD", "EUR", "GBP"], width=5).pack(side='left', padx=5)
        self.currency_var.trace('w', self.update_currency_symbol)
        
        ttk.Label(r1, text="Global Tax %:").pack(side='left', padx=(10, 5))
        gst_e = ttk.Entry(r1, textvariable=self.gst_rate_var, width=6)
        gst_e.pack(side='left')
        gst_e.bind('<FocusOut>', lambda e: self.recalc_all())

        # --- FINANCIAL SUMMARY ---
        ttk.Separator(col1, bootstyle="secondary").pack(fill='x', pady=10)
        
        def add_sum_row(parent, label, val_var, chk_var, is_bold=False):
            f = ttk.Frame(parent)
            f.pack(fill='x', pady=2)
            ttk.Checkbutton(f, variable=chk_var, bootstyle="round-toggle").pack(side='left', padx=(0,5))
            font = ("Segoe UI", 10, "bold") if is_bold else ("Segoe UI", 10)
            ttk.Label(f, text=label, width=12, font=font).pack(side='left')
            e = ttk.Entry(f, textvariable=val_var, justify='right', font=font, width=15)
            e.pack(side='right', fill='x', expand=True)
            return e

        add_sum_row(col1, "Sub Total:", self.subtotal_var, self.print_subtotal_var)
        add_sum_row(col1, "Total Tax:", self.tax_total_var, self.print_tax_var)
        add_sum_row(col1, "Grand Total:", self.grand_total_var, self.print_grand_total_var, is_bold=True)
        
        # Extra Fields Container
        ttk.Separator(col1, bootstyle="secondary").pack(fill='x', pady=10)
        ttk.Button(col1, text="+ Add Extra Field", bootstyle="secondary-outline", command=self.add_extra_field).pack(anchor='w', fill='x')
        self.extra_cont = ttk.Frame(col1)
        self.extra_cont.pack(fill='x', pady=5)

        # Col 2: Terms
        col2 = ttk.LabelFrame(bot, text="Terms")
        col2.grid(row=0, column=1, sticky="nsew", padx=5)
        tb = ttk.Frame(col2); tb.pack(fill='x')
        ttk.Button(tb, text="B", width=3, command=self.toggle_bold).pack(side='left')
        self.terms_txt = tk.Text(col2, height=8, width=30, font=('Segoe UI', 9))
        self.terms_txt.pack(fill='both', expand=True)
        self.terms_txt.insert('1.0', "1. Payment: 100% Advance.\n2. Goods once sold will not be returned.")

        # Col 3: Footer
        col3 = ttk.Frame(bot)
        col3.grid(row=0, column=2, sticky="nsew", padx=5)
        
        ft_box = ttk.LabelFrame(col3, text="Footer Settings")
        ft_box.pack(fill='x', pady=(0,10))
        
        r_logo = ttk.Frame(ft_box); r_logo.pack(fill='x', pady=2)
        ttk.Button(r_logo, text="+ Footer Logo", width=12, command=lambda: self.load_logo("footer")).pack(side='left')
        
        self.footer_logo_lbl = tk.Label(r_logo, text="", bg="#f0f0f0")
        self.footer_logo_lbl.pack(side='left', padx=5)

        tk.Label(r_logo, text="Size:").pack(side='left', padx=2)
        ttk.Scale(r_logo, variable=self.f_logo_size_var, from_=1.0, to=7.5).pack(side='left', fill='x', expand=True)
        
        r_txt = ttk.Frame(ft_box); r_txt.pack(fill='x', pady=2)
        tk.Label(r_txt, text="Text:").pack(side='left')
        ttk.Entry(r_txt, textvariable=self.footer_text_var).pack(side='left', fill='x', expand=True, padx=(0,5))
        
        # New Row for Options (Full Width & Pin Bottom)
        r_opt = ttk.Frame(ft_box); r_opt.pack(fill='x', pady=2)
        ttk.Checkbutton(r_opt, text="Full Width", variable=self.footer_full_width_var).pack(side='left', padx=5)
        ttk.Checkbutton(r_opt, text="Pin to Bottom", variable=self.footer_pin_to_bottom_var).pack(side='left', padx=5)
        
        r_aln = ttk.Frame(ft_box); r_aln.pack(fill='x', pady=2)
        tk.Label(r_aln, text="Align:").pack(side='left')
        ttk.Radiobutton(r_aln, text="L", variable=self.footer_align_var, value="Left").pack(side='left')
        ttk.Radiobutton(r_aln, text="C", variable=self.footer_align_var, value="Center").pack(side='left')
        ttk.Radiobutton(r_aln, text="R", variable=self.footer_align_var, value="Right").pack(side='left')

        sig_box = ttk.LabelFrame(col3, text="Signatures")
        sig_box.pack(fill='x', pady=5)
        tk.Label(sig_box, text="Manager Accounts:", font=("bold")).pack(anchor='w', pady=(5,0))
        ttk.Entry(sig_box, textvariable=self.approved_by_var).pack(fill='x', pady=2)

        ttk.Button(col3, text="👁 PREVIEW PDF", style="Action.TButton", command=self.on_preview_click).pack(fill='x', ipady=10, pady=10)

    # Recalc Override
    def recalc_all(self):
        super().recalc_all() 
        total_tax = 0.0
        net_total = 0.0
        for i in self.items_data:
            total_tax += i.get('gst', 0.0)
            net_total += i.get('total', 0.0)
        curr = self.currency_symbol_var.get()
        if hasattr(self, 'tax_lbl'):
            self.tax_lbl.config(text=f"Total Tax: {curr} {total_tax:,.2f}")
        if hasattr(self, 'total_lbl'):
            self.total_lbl.config(text=f"Net Amount: {curr} {net_total:,.2f}")

    # =========================================================
    #  5. PDF GENERATOR
    # =========================================================
    def _generate_pdf(self, path):
        if not os.path.dirname(path): return

        MARGIN = 20 
        # Footer Pre-calculation for Dynamically Adjusted Margin
        f_h_pts = 0
        t_foot = None
        if self.footer_text_var.get() or self.footer_logo_path:
             styles = getSampleStyleSheet(); norm_style = styles['Normal']
             f_txt = Paragraph(self.footer_text_var.get(), norm_style) 
             t_style = [('VALIGN', (0,0), (-1,-1), 'MIDDLE')]
             align_val = {"Left": 'LEFT', "Right": 'RIGHT', "Center": 'CENTER'}.get(self.footer_align_var.get(), 'CENTER')
             t_style.append(('ALIGN', (0,0), (-1,-1), align_val))
             
             if self.footer_logo_path:
                 target_w = 540 / inch if self.footer_full_width_var.get() else self.f_logo_size_var.get()
                 img = self._get_scaled_image(self.footer_logo_path, target_w)
                 t_foot = Table([[f_txt], [img]], colWidths=[540])
             else:
                 t_foot = Table([[f_txt]], colWidths=[540])
             
             t_foot.setStyle(TableStyle(t_style))
             t_foot.wrapOn(None, 540, A4[1])
             f_h_pts = getattr(t_foot, '_height', 40) + 10

        doc = SimpleDocTemplate(path, pagesize=A4, rightMargin=MARGIN, leftMargin=MARGIN, 
                                topMargin=1.0*inch, bottomMargin=max(1.5*inch, MARGIN + f_h_pts))
        elements = []
        styles = getSampleStyleSheet()
        norm_style = styles['Normal']
        
        # Description Style: Text ko automatic next line par bhejne ke liye
        desc_style = ParagraphStyle('desc', parent=norm_style, fontSize=9, leading=11)
        
        # --- HEADER SECTION ---
        styles = getSampleStyleSheet()
        norm_style = styles['Normal']
        
        img_left = self._get_scaled_image(self.header_logo_path, 1.2) if self.header_logo_path else ""
        img_right = self._get_scaled_image(self.header_logo_right_path, 1.2) if self.header_logo_right_path else ""
        
        title_style = ParagraphStyle('Title', parent=norm_style, fontName='Helvetica-Bold', fontSize=22, alignment=TA_CENTER)
        title_p = Paragraph("Sales Tax Invoice", title_style)
        
        cw = 540 
        h_data = [[img_left, title_p, img_right]]
        t_head = Table(h_data, colWidths=[cw*0.25, cw*0.5, cw*0.25])
        t_head.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN', (0,0), (0,0), 'LEFT'),
            ('ALIGN', (1,0), (1,0), 'CENTER'),
            ('ALIGN', (2,0), (2,0), 'RIGHT'),
            ('TOPPADDING', (1,0), (1,0), 5),#previous value is 45
        ]))
        elements.append(t_head)
        elements.append(Spacer(1, 0.3*inch))

        # --- INFO TABLE SECTION ---
        def mk_b(txt): return Paragraph(f"<b>{txt}</b>", ParagraphStyle('b', parent=norm_style, fontSize=9))
        def mk_n(txt): return Paragraph(f"{txt}", ParagraphStyle('n', parent=norm_style, fontSize=9))
        
        l_data = [
            [mk_b("Sales Tax Invoice No"), mk_n(self.quotation_no_var.get()), mk_b("PO No."), mk_n(self.rfq_no_var.get())],
            [mk_b("Customer"), mk_n(self.client_name_var.get()), mk_b("S.T.N. NO:"), mk_n(self.client_stn_var.get())],
            [mk_b("Address"), mk_n(self.client_addr_var.get()), mk_b("NTN:"), mk_n(self.client_ntn_var.get())],
            [mk_b("Contact person"), mk_n(self.client_contact_var.get()), mk_b("Delivery date"), mk_n(self.delivery_date_var.get())],
            [mk_b("Designation"), mk_n(self.client_designation_var.get()), mk_b("Delivered Through"), mk_n(self.delivered_through_var.get())],
            [mk_b("email"), mk_n(self.client_email_var.get()), "", ""]
        ]
        r_data = [
            [mk_b("Quotation No."), mk_n(self.ref_quot_no_var.get())],
            [mk_b("DC No"), mk_n(self.dc_no_var.get())],
            [mk_b("S.T.N. No."), mk_n(self.vendor_stn_var.get())],
            [mk_b("NTN:"), mk_n(self.vendor_ntn_var.get())],
            [mk_b("PRA"), mk_n(self.vendor_pra_var.get())],
            [mk_b("email"), mk_n(self.vendor_email_var.get())]
        ]

        t_left = Table(l_data, colWidths=[85, 120, 75, 95]) # Sum = 375
        t_left.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BACKGROUND', (0,0), (0,-1), colors.whitesmoke), 
            ('BACKGROUND', (2,0), (2,-2), colors.whitesmoke),
            ('SPAN', (1,5), (3,5)) 
        ]))

        t_right = Table(r_data, colWidths=[70, 95]) # Sum = 165. Total 375 + 165 = 540.
        t_right.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BACKGROUND', (0,0), (0,-1), colors.whitesmoke)
        ]))

        l_title = Paragraph(f"<b>{self.left_header_title.get()}</b>", ParagraphStyle('c', alignment=TA_CENTER, fontSize=11))
        r_title = Paragraph(f"<b>{self.right_header_title.get()}</b>", ParagraphStyle('c', alignment=TA_CENTER, fontSize=11))
        
        t_main = Table([[l_title, r_title],[t_left, t_right]], colWidths=[375, 165]) # Exact 540 Total Content Width
        t_main.setStyle(TableStyle([
            ('BOX', (0,0), (-1,-1), 1, colors.black), 
            ('LINEBELOW', (0,0), (-1,0), 1, colors.black),
            ('LINEAFTER', (0,0), (0,-1), 1, colors.black), 
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('ALIGN', (0,0), (-1,0), 'CENTER'),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ]))
        elements.append(t_main)
        elements.append(Spacer(1, 15))

        # 3. ITEMS TABLE
        print_cols = [c for c in self.columns_config if c.get('printable', True)]
        # Dynamic Font Size logic
        base_font_size = 8 if len(print_cols) > 7 else 10
        
        # Styles for the table
        item_norm_style = ParagraphStyle('ItemNorm', parent=norm_style, fontSize=base_font_size, leading=base_font_size*1.2)
        item_head_style = ParagraphStyle('ItemHead', parent=item_norm_style, fontName='Helvetica-Bold', alignment=TA_CENTER)
        item_num_style = ParagraphStyle('ItemNum', parent=item_norm_style, alignment=TA_RIGHT)

        headers = [Paragraph(f"<b>{c['label']}</b>", item_head_style) for c in print_cols]
        data = [headers]
        total_tax_calc = 0.0

        # DYNAMIC COLUMN WIDTH LOGIC: PROPORTIONAL SCALING
        # Treats user-defined widths in 'Manage Columns' as weights
        CW = 540 # Content Width
        
        # 1. Get Raw Widths from Config
        raw_widths = [float(c.get('width', 50)) for c in print_cols]
        total_raw = sum(raw_widths)
        
        # 2. Calculate Scale Factor
        if total_raw == 0: total_raw = 1 
        scale_factor = CW / total_raw
        
        # 3. Apply Scale Factor
        pdf_col_widths = [w * scale_factor for w in raw_widths]
        
        for item in self.items_data:
            total_tax_calc += item.get('gst', 0.0)
            row = []
            for c in print_cols:
                val = item.get(c['id'], "")
                p_style = item_norm_style
                if c['type'] in ['number', 'calc', 'global_pct']:
                    try: 
                        val = f"{float(val):,.2f}"
                        p_style = item_num_style
                    except: pass
                
                # Use Paragraph to ensure wrapping and no overlapping
                row.append(Paragraph(str(val).replace("\n", "<br/>"), p_style))
            data.append(row)
        
        t_items = Table(data, colWidths=pdf_col_widths, repeatRows=1, splitByRow=True)
        t_items.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
            ('BOX', (0,0), (-1,-1), 1, colors.black),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))
        elements.append(t_items)
        elements.append(Spacer(1, 10))

        # --- FINANCIAL SUMMARY TABLE (Conditional) ---
        summary_data = []
        curr = self.currency_symbol_var.get()
        
        # We need to access the variables from the parent or self if they exist
        # Since InvoiceApp inherits QuotationApp, it should have them if initialized correctly.
        # However, InvoiceApp might be using its own 'recalc' logic or might need to ensure variables are present.
        # Assuming variables are available from QuotationApp.__init__ or we need to gracefully fallback.
        
        # Sub Total
        if hasattr(self, 'print_subtotal_var') and self.print_subtotal_var.get():
            val = self.subtotal_var.get() if hasattr(self, 'subtotal_var') else "0.00"
            summary_data.append([
                Paragraph("<b>Total Amount (Excl. Tax):</b>", ParagraphStyle('SL', parent=norm_style, alignment=TA_RIGHT)),
                Paragraph(f"<b>{curr} {val}</b>", ParagraphStyle('SV', parent=norm_style, alignment=TA_RIGHT))
            ])
            
        # Tax Total
        if hasattr(self, 'print_tax_var') and self.print_tax_var.get():
            val = self.tax_total_var.get() if hasattr(self, 'tax_total_var') else "0.00"
            summary_data.append([
                Paragraph("<b>Total Sales Tax:</b>", ParagraphStyle('SL', parent=norm_style, alignment=TA_RIGHT)),
                Paragraph(f"<b>{curr} {val}</b>", ParagraphStyle('SV', parent=norm_style, alignment=TA_RIGHT))
            ])
            
        # Grand Total
        if hasattr(self, 'print_grand_total_var') and self.print_grand_total_var.get():
            val = self.grand_total_var.get() if hasattr(self, 'grand_total_var') else "0.00"
            summary_data.append([
                Paragraph("<b>Grand Total:</b>", ParagraphStyle('SL', parent=norm_style, alignment=TA_RIGHT, fontSize=11)),
                Paragraph(f"<b>{curr} {val}</b>", ParagraphStyle('SV', parent=norm_style, alignment=TA_RIGHT, fontSize=11))
            ])
            
        if summary_data:
             t_sum = Table(summary_data, colWidths=[CW*0.25, CW*0.15])
             t_sum.setStyle(TableStyle([
                ('LINEABOVE', (0,0), (-1,0), 1, colors.black),
                ('ALIGN', (0,0), (-1,-1), 'RIGHT'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
             ]))
             wrapper = Table([[ "", t_sum ]], colWidths=[CW*0.6, CW*0.4])
             wrapper.setStyle(TableStyle([('ALIGN', (1,0), (1,0), 'RIGHT')]))
             elements.append(wrapper)

        elements.append(Spacer(1, 20))

        # --- SIGNATURES & TAX SECTION ---
        from reportlab.platypus import KeepTogether
        footer_elements = []

        curr = self.currency_symbol_var.get()
        tax_str = f"{curr} {total_tax_calc:,.2f}"

        tax_para = Paragraph(f"<b>Total Sales Tax:</b> <font color='#c0392b'>{tax_str}</font>", norm_style)
        footer_elements.append(tax_para)
        footer_elements.append(Spacer(1, 40))

        # --- TERMS & SIGNATURES BLOCK (KeepTogether protection) ---
        footer_elements = []
        footer_elements.append(Spacer(1, 15))
        
        # Terms & Conditions (RESTORED)
        footer_elements.append(Paragraph("<b>Terms & Conditions:</b>", ParagraphStyle('BT', parent=norm_style, fontSize=10)))
        footer_elements.append(Paragraph(self._get_tagged_text(), ParagraphStyle('BC', parent=norm_style, fontSize=9)))
        footer_elements.append(Spacer(1, 40))

        # Prepared / Approved By with Red Note
        footer_elements.append(Spacer(1, 50))
        
        # Create styles for signature block
        sig_style_left = ParagraphStyle('SigL', parent=norm_style, fontSize=10, alignment=TA_LEFT)
        sig_style_right = ParagraphStyle('SigR', parent=norm_style, fontSize=10, alignment=TA_RIGHT)
        sig_style_center = ParagraphStyle('SigC', parent=norm_style, fontSize=9, alignment=TA_CENTER)
        
        sig_data = [[
            Paragraph("_________________<br/><b>Prepared By</b>", sig_style_left),
            Paragraph("<b><font color='red'>Note:</font></b> This is a system generated document so no need to sign.", sig_style_center),
            Paragraph("_________________<br/><b>Approved By</b>", sig_style_right)
        ]]
        
        # Reduce gap: 25% + 50% + 25% layout
        t_sig = Table(sig_data, colWidths=[CW*0.25, CW*0.5, CW*0.25])
        t_sig.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'BOTTOM'),
            ('ALIGN', (0,0), (0,0), 'LEFT'),
            ('ALIGN', (1,0), (1,0), 'CENTER'),
            ('ALIGN', (2,0), (2,0), 'RIGHT'),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ]))
        footer_elements.append(t_sig)
        
        sys_gen_style = ParagraphStyle('SysGen', parent=styles['Normal'], fontSize=8, alignment=TA_CENTER, textColor=colors.grey)
        # footer_elements.append(Paragraph("This is a system generated document so no need to sign.", sys_gen_style))
        
        elements.append(KeepTogether(footer_elements))

        elements.append(Spacer(1, 10))

        # --- QR CODE & SOCIAL ICONS SETUP ---
        website_link = "https://www.orientmarketing.com.pk/"
        qr_string = f"Invoice No: {self.quotation_no_var.get()}\nDate: {self.doc_date_var.get()}\nClient: {self.client_name_var.get()}\nNet Amount: {self.grand_total_var.get()}\n{website_link}"
        qr_img = self._generate_qr_code(qr_string, size_inch=0.5)

        
        # Pinned Footer Logic
        t_foot = None
        if self.footer_text_var.get() or self.footer_logo_path:
             f_txt = Paragraph(self.footer_text_var.get(), norm_style) 
             t_style = [('VALIGN', (0,0), (-1,-1), 'MIDDLE')]
             align_val = {"Left": 'LEFT', "Right": 'RIGHT', "Center": 'CENTER'}.get(self.footer_align_var.get(), 'CENTER')
             t_style.append(('ALIGN', (0,0), (-1,-1), align_val))
             
             if self.footer_logo_path:
                 target_w = 540 / inch if self.footer_full_width_var.get() else self.f_logo_size_var.get()
                 img = self._get_scaled_image(self.footer_logo_path, target_w)
                 t_foot = Table([[f_txt], [img]], colWidths=[540])
             else:
                 t_foot = Table([[f_txt]], colWidths=[540])
             
             t_foot.setStyle(TableStyle(t_style))
             t_foot.wrapOn(None, 540, A4[1])

        def canvas_setup(canvas, doc):
            self.last_pdf_pages = canvas.getPageNumber()
            page_width, page_height = A4
            
            if t_foot and self.footer_pin_to_bottom_var.get():
                t_foot.drawOn(canvas, MARGIN, MARGIN + 0.9*inch)
            
            if qr_img:
                qr_img.drawOn(canvas, page_width - MARGIN - 0.5*inch, 20)

            
            try:
                icon_size = 16
                social_x, social_y = 20, 25 
                colors_list = [
                    ('#0066cc', 'W', 'https://www.orientmarketing.com.pk/'),
                    ('#FF0000', 'Y', 'https://www.youtube.com/@Antarc-Technologies'),
                    ('#1877F2', 'f', 'https://www.facebook.com/orientmarketing.com.pk'),
                    ('#E4405F', 'I', 'https://www.instagram.com/orientmarketinghvac/')
                ]
                for idx, (color, symbol, url) in enumerate(colors_list):
                    x_pos = social_x + idx * (icon_size + 4)
                    canvas.setFillColor(color)
                    canvas.rect(x_pos, social_y, icon_size, icon_size, fill=1, stroke=0)
                    canvas.setFillColor(colors.white)
                    canvas.setFont("Helvetica-Bold", 10)
                    canvas.drawString(x_pos + 4, social_y + 4, symbol)
                    canvas.linkURL(url, (x_pos, social_y, x_pos + icon_size, social_y + icon_size), relative=0)

            except Exception as e:
                print(f"Social icons error: {e}")

        doc.build(elements, onFirstPage=canvas_setup, onLaterPages=canvas_setup)

    def _generate_qr_code(self, data, size_inch=0.6):
        """Generate a QR code image and return a ReportLab Image object."""
        try:
            import qrcode
            qr_gen = qrcode.QRCode(version=1, box_size=10, border=1)
            qr_gen.add_data(data)
            qr_gen.make(fit=True)
            img = qr_gen.make_image(fill_color="black", back_color="white")
            
            import tempfile
            tmp_dir = tempfile.gettempdir()
            tmp = os.path.join(tmp_dir, f"temp_qr_{os.getpid()}.png")
            img.save(tmp)
            return RLImage(tmp, width=size_inch*inch, height=size_inch*inch)
        except Exception as e:
            print(f"QR Code generation error: {e}")
            return None

    def on_preview_click(self):
        """PDF Preview logic for Invoice"""
        try:
            import tempfile
            fd, tmp_path = tempfile.mkstemp(suffix=".pdf")
            os.close(fd)
            
            self._generate_pdf(tmp_path)
            
            if os.path.exists(tmp_path):
                if os.name == 'nt':
                    os.startfile(tmp_path)
                else:
                    import webbrowser
                    webbrowser.open("file://" + tmp_path)
            else:
                messagebox.showerror("Error", "Preview file could not be created.")
        except Exception as e:
            messagebox.showerror("Preview Error", f"Could not generate preview.\nDetails: {str(e)}")

    # --- Save & Utils ---
    def check_license(self): pass 
    def check_user_login(self): pass
    
    def save_to_database(self, silent=False):
        # Agar connection nahi hai to wapis
        if not hasattr(self, 'cursor'): self.init_database()
        
        # Data Pack
        import json
        data_packet = {
            "header": {
                # YAHAN CHANGE KIYA HAI: inv_no_var -> quotation_no_var
                "ref_no": self.quotation_no_var.get(),
                "date": self.doc_date_var.get(),
                "client_name": self.client_name_var.get(),
            },
            "items": self.items_data
        }
        json_str = json.dumps(data_packet)
        
        # Total Value Calculate
        try:
            import re
            txt = self.total_lbl.cget("text")
            val = float(re.search(r"[\d,]+\.?\d*", txt).group().replace(',',''))
        except: val = 0.0

        try:
            # Table: tax_invoices
            if self.current_db_id:
                self.cursor.execute("""
                    UPDATE tax_invoices 
                    SET ref_no=?, client_name=?, date=?, grand_total=?, full_data=?
                    WHERE id=?
                """, (self.quotation_no_var.get(), self.client_name_var.get(), self.doc_date_var.get(), val, json_str, self.current_db_id))
            else:
                self.cursor.execute("""
                    INSERT INTO tax_invoices (ref_no, client_name, date, grand_total, full_data)
                    VALUES (?,?,?,?,?)
                """, (self.quotation_no_var.get(), self.client_name_var.get(), self.doc_date_var.get(), val, json_str))
                
                self.current_db_id = self.cursor.lastrowid
            
            self.conn.commit()
            if not silent: messagebox.showinfo("Saved", "Invoice Database Updated!")
            
        except Exception as e:
            if not silent: messagebox.showerror("DB Error", str(e))
    
     
    def load_from_quotation_data(self, json_data):
        try:
            data = json.loads(json_data)
            h = data.get("header", {})
            self.rfq_no_var.set(h.get("quot_no", "")) 
            
            # ✅ FIX: Use actual Ref No from data if available, instead of hardcoded 55
            doc_no = h.get("ref_no") or h.get("quot_no") or "55"
            self.quotation_no_var.set(doc_no) 
            
            self.client_name_var.set(h.get("client_name", ""))
            self.client_addr_var.set(h.get("client_addr", ""))
            self.client_contact_var.set(h.get("client_contact", ""))
            self.client_email_var.set(h.get("client_email", ""))
            self.client_designation_var.set(h.get("client_desig", ""))
            self.rfq_no_var.set(h.get("rfq", "")) 
            self.left_header_title.set(f"{h.get('client_name', 'Client')} - Data")
            self.right_header_title.set("Orient Marketing - Data")
            self.ref_quot_no_var.set(h.get("quot_no", ""))
            self.items_data = data.get("items", [])
            self.row_colors = {int(k): v for k, v in data.get("colors", {}).items()}
            self.refresh_tree()
            self.recalc_all()
        except Exception as e:
            print(f"Error loading history data: {e}")

if __name__ == "__main__":
    root = ttk.Window(themename="lumen")
    app = InvoiceApp(root)
    root.mainloop()