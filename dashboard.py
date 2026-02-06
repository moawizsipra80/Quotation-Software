import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import analytics
import os
import datetime
import pyodbc
import ui_styles as style  
import pywinstyles
from theme_manager import ThemeManager
from PIL import Image, ImageTk
class DashboardPanel:

    def __init__(self, main_app):
        self.app = main_app
        self.root = main_app.root

        # Dark Title Bar (Windows 10/11)
        try:
            import pywinstyles
            pywinstyles.apply_style(self.root, "dark") 
        except: pass

        # Window Setup / Theme application via centralized ThemeManager
        try:
            # Derive current theme from the main app's style, falling back to 'cosmo'
            current_theme = "cosmo"
            try:
                # ttkbootstrap exposes current theme via theme.name or theme_use()
                current_theme = getattr(getattr(self.app.style, "theme", None), "name", None) or self.app.style.theme_use()
            except Exception:
                pass
            ThemeManager.apply_theme(self.root, current_theme)
        except Exception:
            pass

        self.frame = tk.Frame(self.root, bg=style.BG_MAIN) 
        self.frame.place(x=0, y=0, relwidth=1, relheight=1)
        
        # Theme selection variable (initialized from current app style/theme)
        try:
            initial_theme = getattr(getattr(self.app.style, "theme", None), "name", None) or self.app.style.theme_use()
        except Exception:
            initial_theme = "cosmo"
        self.theme_var = tk.StringVar(value=initial_theme)

        # Data fetching...
        try:
            self.monthly_data = analytics.get_analytics_data(self.app.conn)
        except: self.monthly_data = None

        self._build_ui()

    def launch_module(self, name):
        """Directly opens the module window without any intermediate selector popups."""
        try:
            if name == "invoice":
                from invoice import InvoiceApp
           #     self.app.root.withdraw() # Dashboard chupao
                win = tk.Toplevel(self.app.root)
                InvoiceApp(win) # Direct Invoice App kholo
                
            elif name == "commercial":
                from commercial import CommercialApp
            #    self.app.root.withdraw() # Dashboard chupao
                win = tk.Toplevel(self.app.root)
                CommercialApp(win) # Direct Commercial App kholo
                
            elif name == "delivery":
                from delivery_challan import DeliveryChallanApp
             #   self.app.root.withdraw() # Dashboard chupao
                win = tk.Toplevel(self.app.root)
                DeliveryChallanApp(win) # Direct Delivery Challan kholo

        except Exception as e:
            messagebox.showerror("Module Error", f"Could not launch {name}: {e}")
            self.app.root.deiconify() # Error ki surat mein dashboard wapis lao    
    
    def open_insta_miner(self):
        # --- UI WINDOW SETUP ---
        sw = tk.Toplevel(self.root)
        sw.title("Instagram Auto-DM Bot")
        sw.geometry("500x550")
        sw.transient(self.root)
        
        tk.Label(sw, text="Instagram Sniper Bot", font=("Segoe UI", 14, "bold"), fg="#E1306C").pack(pady=10)
        
        # 1. Target Account
        tk.Label(sw, text="Target Competitor Username (e.g. outfitters_pk):").pack(anchor='w', padx=20)
        target_ent = tk.Entry(sw, width=40)
        target_ent.pack(pady=5)
        
        # 2. Message Text
        tk.Label(sw, text="DM Message (Spam se bachne ke liye short rakhein):").pack(anchor='w', padx=20)
        msg_txt = tk.Text(sw, height=5, width=40, font=("Arial", 10))
        msg_txt.pack(pady=5)
        msg_txt.insert("1.0", "Hi! Saw your interest in fashion. Check out our profile! 🔥")
        
        # 3. Image Selection
        tk.Label(sw, text="Attach Image (Optional):").pack(anchor='w', padx=20)
        img_path_var = tk.StringVar()
        
        def browse_img():
            p = filedialog.askopenfilename(filetypes=[("Images", "*.jpg;*.png;*.jpeg")])
            if p: img_path_var.set(p)
            
        btn_fr = tk.Frame(sw)
        btn_fr.pack(pady=5)
        tk.Entry(btn_fr, textvariable=img_path_var, width=30).pack(side='left')
        tk.Button(btn_fr, text="Browse", command=browse_img).pack(side='left', padx=5)

        # --- EXECUTION LOGIC ---
        def start_process():
            target = target_ent.get()
            message = msg_txt.get("1.0", "end-1c")
            img_path = img_path_var.get()
            
            if not target or not message.strip():
                messagebox.showerror("Error", "Target Username and Message are required!")
                return
            
            sw.destroy() # Window band karein
            
            try:
                import insta_scraper
                import importlib
                importlib.reload(insta_scraper)
                
                # 1. Launch Browser
                insta_scraper.start_driver()
                
                # 2. Open Login Page
                insta_scraper.open_login_page()
                
                # 3. --- MANUAL LOGIN WAIT (YEH HAI SOLUTION) ---
                # Code yahan ruk jayega jab tak aap OK nahi dabate
                messagebox.showinfo("Action Required", 
                                    "Browser is open.\n\n"
                                    "1. Please LOG IN manually.\n"
                                    "2. Handle any 2FA or Popups.\n"
                                    "3. Once you are on the Home Feed, Click OK here.")
                
                # 4. Start Mining
                messagebox.showinfo("Running", f"Bot is starting on @{target}...\nDon't touch the mouse.")
                
                active_users = insta_scraper.get_active_users(target)
                
                count = 0
                sent_count = 0
                
                for user in active_users:
                    if count >= 20: # Safety Limit
                        break
                    
                    status = insta_scraper.send_dm_with_image(user, message, img_path)
                    
                    if status == "Sent":
                        sent_count += 1
                        
                    count += 1
                    
                    # Random Sleep (Safety)
                    import time
                    import random
                    if count < len(active_users):
                        sleep_time = random.randint(30, 60) # Fast mode for demo, increase for real use
                        print(f"Sleeping {sleep_time}s...")
                        time.sleep(sleep_time)

                insta_scraper.close_driver()
                messagebox.showinfo("Done", f"Campaign Finished!\nSent to: {sent_count} users.")

            except Exception as e:
                messagebox.showerror("Error", f"Bot Failed: {e}")

        tk.Button(sw, text="🚀 START BOT", bg="#E1306C", fg="white", font=("bold"), 
                  command=start_process).pack(pady=20, ipadx=20, ipady=5)  
    def _build_ui(self):
        # Stats Calculation
        total_count = 0; total_value = 0.0
        # --- PRIVACY LOGIC ---
        user = getattr(self.app, 'current_username', 'Admin')
        
        try:
            if user == "admin": 
                query_count = "SELECT COUNT(*) FROM quotations"
                query_sum = "SELECT SUM(grand_total) FROM quotations"
                params = ()
            else:
                query_count = "SELECT COUNT(*) FROM quotations WHERE created_by = ?"
                query_sum = "SELECT SUM(grand_total) FROM quotations WHERE created_by = ?"
                params = (user,)

            self.app.cursor.execute(query_count, params)
            total_count = self.app.cursor.fetchone()[0]
            
            self.app.cursor.execute(query_sum, params)
            val = self.app.cursor.fetchone()[0]
            if val: total_value = val
        except: pass

        # --- LEFT PANEL (SIDEBAR) ---
        left_panel = tk.Frame(self.frame, bg=style.BG_SIDE, width=260)
        left_panel.pack(side='left', fill='y')
        left_panel.pack_propagate(False) 
        
        # --- RIGHT PANEL (CONTENT) ---
        right_panel = tk.Frame(self.frame, bg=style.BG_MAIN)
        right_panel.pack(side='right', fill='both', expand=True)
        
        # Logo Text
        tk.Label(left_panel, text="ODM V6", font=style.FONT_H1, fg=style.ACCENT, bg=style.BG_SIDE).pack(pady=(40, 40))
        
        # Sidebar Buttons
        self._make_menu_btn(left_panel, "🏠 Dashboard", lambda: None) 
        self._make_menu_btn(left_panel, "➕ Create Quotation", self.open_new_quotation)
        self._make_menu_btn(left_panel, "📂 View History", self.app.load_history_window)
        
        tk.Label(left_panel, text="MODULES", bg=style.BG_SIDE, fg="grey", font=("Arial", 8, "bold")).pack(anchor='w', padx=20, pady=(20, 5))

        self._make_menu_btn(left_panel, "🚚 Delivery Challan", lambda: self.launch_module("delivery"))
        self._make_menu_btn(left_panel, "📄 Tax Invoice", lambda: self.launch_module("invoice"))
        self._make_menu_btn(left_panel, "🧾 Commercial Inv", lambda: self.launch_module("commercial"))        
        
        tk.Label(left_panel, text="SYSTEM", bg=style.BG_SIDE, fg="grey", font=("Arial", 8, "bold")).pack(anchor='w', padx=20, pady=(20, 5))
        self._make_menu_btn(left_panel, "⚙️ Settings / Backup", self.open_settings_window)

        # Version Footer
        tk.Label(left_panel, text="v5.2 Stable", fg="#7f8c8d", bg="#2c3e50", font=("Arial", 8)).pack(side="bottom", pady=20)

        # 1. Header Area
        header = tk.Frame(right_panel, bg="#f4f6f9", height=80)
        header.pack(fill='x', padx=30, pady=20)
        
        tk.Label(header, text="Business Dashboard", font=("Segoe UI", 20, "bold"), fg="#2c3e50", bg="#f4f6f9").pack(side='left')

        # Theme selector (right side, before welcome label)
        theme_box = tk.Frame(header, bg="#f4f6f9")
        theme_box.pack(side='right', padx=(0, 0), pady=10)

        ttk.Label(theme_box, text="🎨 Theme:", background="#f4f6f9").pack(side='left', padx=(0, 5))
        theme_combo = ttk.Combobox(
            theme_box,
            textvariable=self.theme_var,
            values=ThemeManager.get_themes(),
            state="readonly",
            width=14,
        )
        theme_combo.pack(side='left')
        theme_combo.bind("<<ComboboxSelected>>", self.app.update_app_theme)

        # Profile Picture
        pic_path = getattr(self.app, 'current_user_pic_path', None)
        if pic_path and os.path.exists(pic_path):
            try:
                pil_img = Image.open(pic_path)
                pil_img = pil_img.resize((45, 45), Image.Resampling.LANCZOS)
                self.profile_icon = ImageTk.PhotoImage(pil_img) 
                tk.Label(header, image=self.profile_icon, bg="#f4f6f9").pack(side='right', padx=(5, 5))
            except Exception as e:
                print(f"Profile Pic Error: {e}")

        tk.Label(header, text=f"Welcome, {user}", font=("Segoe UI", 12), fg="grey", bg="#f4f6f9").pack(side='right', padx=(10, 0), pady=10)

        # 2. KPI Cards Area
        cards_fr = tk.Frame(right_panel, bg="#f4f6f9")
        cards_fr.pack(fill='x', padx=30, pady=10)
        
        try:
            curr = self.app.currency_symbol_var.get()
        except:
            curr = "Rs."

        self._draw_kpi_card(cards_fr, "TOTAL QUOTATIONS", str(total_count), "#2980b9", "left")
        self._draw_kpi_card(cards_fr, "TOTAL REVENUE", f"{curr} {total_value:,.0f}", "#27ae60", "left")

        # --- 3. QUICK LAUNCH BUTTONS (YE MISSING THA) ---
        q_frame = tk.Frame(right_panel, bg="#f4f6f9")
        q_frame.pack(fill='x', padx=30, pady=5)
        
        tk.Label(q_frame, text="Quick Actions:", font=("Segoe UI", 10, "bold"), bg="#f4f6f9", fg="#7f8c8d").pack(side='left', padx=(0,10))
        
        # Scraper Button
        btn_scraper = tk.Button(q_frame, text="🔍 Find New Clients", bg="#27ae60", fg="white", font=("Segoe UI", 9, "bold"),
                                relief="flat", cursor="hand2", command=self.open_scraper_popup)
        btn_scraper.pack(side='left', padx=5, ipady=5, ipadx=10)

        # WhatsApp Button
        btn_wa = tk.Button(q_frame, text="💬 WhatsApp Marketing", bg="#25D366", fg="white", font=("Segoe UI", 9, "bold"),
                           relief="flat", cursor="hand2", command=self.open_whatsapp_popup)
        btn_wa.pack(side='left', padx=5, ipady=5, ipadx=10)

        # Insta Miner Button
        btn_insta = tk.Button(q_frame, text="📸 Insta Lead Miner", bg="#E1306C", fg="white", font=("Segoe UI", 9, "bold"),
                           relief="flat", cursor="hand2", command=self.open_insta_miner)
        btn_insta.pack(side='left', padx=5, ipady=5, ipadx=10) 
   
        btn_sum = tk.Button(q_frame, text="📊 Client Summary", bg="#8e44ad", fg="white", font=("Segoe UI", 9, "bold"),
                           relief="flat", cursor="hand2", command=self.open_client_summary_cards)
        btn_sum.pack(side='left', padx=5, ipady=5, ipadx=10)
        

        # 4. Charts & Tables Area
        content_area = tk.Frame(right_panel, bg="#f4f6f9")
        content_area.pack(fill='both', expand=True, padx=30, pady=(10,5))
        
        # Graph (Left)
        chart_frame = tk.LabelFrame(content_area, text=" Sales Performance ", bg="white", font=("Segoe UI", 10, "bold"), bd=0, highlightthickness=1)
        chart_frame.pack(side='left', fill='both', expand=True, padx=(0, 15))
        
        if self.monthly_data is not None and not self.monthly_data.empty:
            self._draw_chart(chart_frame)
        else:
            tk.Label(chart_frame, text="No Data Available for Graph", bg="white", fg="grey").pack(expand=True)

        # Recent Table (Right)
        table_frame = tk.LabelFrame(content_area, text=" Recent Activity ", bg="white", font=("Segoe UI", 10, "bold"), bd=0, highlightthickness=1)
        table_frame.pack(side='right', fill='both', expand=True)
        self._draw_recent_table(table_frame)
        
        # Footer
        footer_frame = tk.Frame(right_panel, bg="#2c3e50", height=35)
        footer_frame.pack(side='bottom', fill='x', pady=(0, 0)) 

        tk.Label(footer_frame, text="Professional Quotation Generator V5.2", bg="#2c3e50", fg="white", font=("Segoe UI", 9, "bold")).pack(side="left", padx=20, pady=8)
        tk.Label(footer_frame, text="Made by Muhammad Moawiz Sipra", bg="#2c3e50", fg="#bdc3c7", font=("Segoe UI", 9, "italic")).pack(side="right", padx=20, pady=8)

    # --- HELPER UI FUNCTIONS ---

    def _make_menu_btn(self, parent, text, cmd, color="#34495e"):
        # Frame for padding
        btn_frame = tk.Frame(parent, bg="#2c3e50")
        btn_frame.pack(fill='x', pady=1)

        # Button Create
        btn = tk.Button(btn_frame, text=text, font=("Segoe UI", 11), 
                        bg="#34495e", fg="white", 
                        activebackground="#2980b9", activeforeground="white",
                        bd=0, cursor="hand2", anchor="w", padx=20, pady=12, command=cmd)
        btn.pack(fill='x')

        btn.default_bg = "#34495e"
        
        def on_enter(e):
            # Jab mouse aye to Light Blue
            e.widget['bg'] = "#2980b9"
            
        def on_leave(e):
            # Jab mouse jaye to wapis Dark Blue (Fixed)
            e.widget['bg'] = e.widget.default_bg

        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

    def _draw_kpi_card(self, parent, title, value, color, side):
        # Card Container (Shadow Effect ke liye Border)
        card = tk.Frame(parent, bg="white", highlightbackground="#dcdcdc", highlightthickness=1)
        card.pack(side=side, fill='x', expand=True, padx=10, ipady=5)
        
        # Left Side Color Strip
        strip = tk.Frame(card, bg=color, width=6)
        strip.pack(side='left', fill='y')
        
        # Content Frame
        content = tk.Frame(card, bg="white", padx=15, pady=10)
        content.pack(side='left', fill='both', expand=True)
        
        # Icon Selection based on Title
        icon = "📊"
        if "REVENUE" in title: icon = "💰"
        elif "QUOTATIONS" in title: icon = "📄"
        
        # Title with Icon
        header_frame = tk.Frame(content, bg="white")
        header_frame.pack(anchor='w', fill='x')
        
        tk.Label(header_frame, text=icon, font=("Segoe UI", 14), bg="white", fg=color).pack(side='left')
        tk.Label(header_frame, text=f" {title}", font=("Segoe UI", 9, "bold"), fg="#7f8c8d", bg="white").pack(side='left', pady=2)
        
        # Value (Big Text)
        tk.Label(content, text=value, font=("Segoe UI", 22, "bold"), fg="#2c3e50", bg="white").pack(anchor='w', pady=(5,0))

    def _draw_chart(self, parent):
        """Dashboard ke liye professional Dark Compact Bar Chart."""
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        from analytics import get_analytics_data

        # 1. Purane graph widgets saaf karein
        for widget in parent.winfo_children():
            widget.destroy()

        try:
            df = get_analytics_data(self.app.conn)
        except:
            df = None

        if df is None or df.empty:
            tk.Label(parent, text="No Data Available", bg="#002b36", fg="grey").pack(expand=True)
            return

        try:
            # ✅ FIGSIZE mazeed choti (Height 2.2) aur Background match
            # Dashboard ka dark color #002b36 hai
            fig, ax = plt.subplots(figsize=(5, 2.2), dpi=100)
            fig.patch.set_facecolor('#002b36') 
            ax.set_facecolor('#002b36')

            months = df['month']
            # Neon/Bright colors jo dark background pe uthen
            colors = {'quotations': '#268bd2', 'tax_invoices': '#859900', 'commercial_invoices': '#b58900'}

            bottom_val = [0] * len(df)
            for col in ['quotations', 'tax_invoices', 'commercial_invoices']:
                if col in df.columns:
                    ax.bar(months, df[col], bottom=bottom_val, label=col.title(), 
                           color=colors.get(col, '#93a1a1'), width=0.6)
                    bottom_val = [i + j for i, j in zip(bottom_val, df[col])]

            # ✅ STYLING: White/Light grey text taake dark pe nazar aaye
            ax.set_title("Monthly Sales Summary", fontsize=8, color='#93a1a1', fontweight='bold')
            ax.legend(fontsize=6, loc='upper left', facecolor='#073642', labelcolor='white', framealpha=0.5)
            
            # Grids aur Spines set karein
            ax.tick_params(axis='x', rotation=0, labelsize=7, colors='#93a1a1')
            ax.tick_params(axis='y', labelsize=7, colors='#93a1a1')
            for spine in ax.spines.values():
                spine.set_color('#586e75')
            
            # ✅ MARGINS: Space bachane ke liye bilkul tight
            plt.subplots_adjust(left=0.12, right=0.98, top=0.88, bottom=0.18)

            canvas = FigureCanvasTkAgg(fig, master=parent)
            canvas.draw()
            
            # ✅ PACKING: Expand False taake footer ke liye jagah bache
            canvas.get_tk_widget().pack(fill='x', expand=False, padx=2, pady=0)

        except Exception as e:
            tk.Label(parent, text=f"Graph Error", fg="red", bg="#002b36").pack()
     
    def _draw_recent_table(self, parent):
        cols = ("Date", "Client", "Amount")
        
        # 1. Style Load (Agar style file use kar rahay hain)
        
        try:
            import ui_styles as style
            style.apply_treeview_style()
            tree = ttk.Treeview(parent, columns=cols, show='headings', height=10, style="Dark.Treeview")
        except:
            # Fallback agar style file na ho
            tree = ttk.Treeview(parent, columns=cols, show='headings', height=10)

        try:
            user = self.app.current_username
            
            # Detect DB Type to decide syntax (LIMIT vs TOP)
            db_type = str(self.app.conn.__class__).lower()
            is_sqlite = "sqlite" in db_type
            
            if user == "admin":
                if is_sqlite:
                    sql = "SELECT date, client_name, grand_total FROM quotations ORDER BY id DESC LIMIT 15"
                else:
                    sql = "SELECT TOP 15 date, client_name, grand_total FROM quotations ORDER BY id DESC"
                
                self.app.cursor.execute(sql)
            else:
                if is_sqlite:
                    sql = "SELECT date, client_name, grand_total FROM quotations WHERE created_by = ? ORDER BY id DESC LIMIT 15"
                else:
                    sql = "SELECT TOP 15 date, client_name, grand_total FROM quotations WHERE created_by = ? ORDER BY id DESC"
                
                self.app.cursor.execute(sql, (user,))    

            rows = self.app.cursor.fetchall()
            currency = self.app.currency_symbol_var.get()
            
            for r in rows:
                # r[0]=Date, r[1]=Client, r[2]=Amount
                d_str = r[0] # Date usually string hi hoti hai
                client = r[1] if r[1] else "Unknown"
                amt = r[2] if r[2] else 0.0
                
                # Agar Amount None ho to 0 kar do
                a_str = f"{currency} {amt:,.0f}"
                
                tree.insert("", "end", values=(d_str, client, a_str))

        except Exception as e:
            print(f"Table Data Error: {e}")
    def close_dashboard(self):
        self.frame.destroy()
        self.app.current_dashboard = None
    def open_new_quotation(self):

        self.close_dashboard()

        try:
            
            self.app.root.title("Professional Quotation Generator")
            
            # Basic header vars clear
            self.app.doc_title_var.set("QUOTATION")
            self.app.quotation_no_var.set("")
            self.app.client_name_var.set("")
            self.app.client_addr_var.set("")
            self.app.client_contact_var.set("")
            self.app.client_email_var.set("")
            self.app.client_designation_var.set("")

            # Items / totals clear
            self.app.items_data = []
            self.app.row_colors = {}
            self.app.current_db_id = None
            self.app.refresh_tree()
            self.app.recalc_all()
            
            print("✅ Quotation reset successful!") 
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not reset quotation: {e}")
            print(f"Reset error: {e}")  # Console log
    

    def open_client_summary_cards(self):
        """Ledger-style client summary with monthly filters and per-client chart."""
        win = tk.Toplevel(self.root)
        win.title("Client Summary - Monthly Ledger")
        win.geometry("950x650")

        from datetime import date

        # Header / filters
        top = tk.Frame(win, bg="white")
        top.pack(fill="x", padx=10, pady=10)

        tk.Label(
            top,
            text="Client Khata (Monthly Summary)",
            font=("Segoe UI", 16, "bold"),
            bg="white",
            fg="#2c3e50",
        ).pack(side="left", padx=10)

        filt = tk.Frame(top, bg="white")
        filt.pack(side="right", padx=10)

        today = date.today()
        self.cs_year_var = tk.IntVar(value=today.year)
        self.cs_month_var = tk.IntVar(value=today.month)

        tk.Label(filt, text="Year:", bg="white").pack(side="left", padx=(0, 2))
        year_ent = tk.Entry(filt, width=6, textvariable=self.cs_year_var)
        year_ent.pack(side="left", padx=(0, 6))

        tk.Label(filt, text="Month (1-12):", bg="white").pack(side="left", padx=(0, 2))
        month_ent = tk.Entry(filt, width=4, textvariable=self.cs_month_var)
        month_ent.pack(side="left", padx=(0, 6))

        btn_reload = tk.Button(
            filt,
            text="Reload",
            bg="#3498db",
            fg="white",
            font=("Segoe UI", 9, "bold"),
        )
        btn_reload.pack(side="left")

        # Tree area
        # Bottom controls (Pack FIRST or with side=bottom to ensure visibility)
        bottom = tk.Frame(win, bg="white")
        bottom.pack(side='bottom', fill="x", padx=10, pady=10)

        # Tree area (Pack AFTER bottom if using default side, or just ensure proper expansion)
        mid = tk.Frame(win, bg="#ecf0f1")
        mid.pack(side='top', fill="both", expand=True, padx=10, pady=(0, 10))

        cols = ("client", "quotations", "tax_invoices", "comm_invoices")
        tree = ttk.Treeview(mid, columns=cols, show="headings", height=18)
        tree.heading("client", text="Client Name")
        tree.heading("quotations", text="Quotations")
        tree.heading("tax_invoices", text="Tax Invoices")
        tree.heading("comm_invoices", text="Comm Invoices")

        tree.column("client", width=320, anchor="w")
        tree.column("quotations", width=120, anchor="center")
        tree.column("tax_invoices", width=120, anchor="center")
        tree.column("comm_invoices", width=130, anchor="center")

        vsb = ttk.Scrollbar(mid, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        
        # --- BUTTONS IN BOTTOM FRAME ---
        def on_view_chart():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("Select", "Select a client first.", parent=win)
                return
            client_name = tree.item(sel[0])["values"][0]
            self.show_client_month_chart(client_name)

        def on_view_history():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("Select", "Select a client first.", parent=win)
                return
            client_name = tree.item(sel[0])["values"][0]
            self.show_client_details_popup(client_name)

        tk.Button(
            bottom,
            text="📊 View Client Chart",
            bg="#8e44ad",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            command=on_view_chart,
        ).pack(side="left", padx=(0, 10), ipadx=10, ipady=3)

        tk.Button(
            bottom,
            text="📂 View Full History",
            bg="#34495e",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            command=on_view_history,
        ).pack(side="left", ipadx=10, ipady=3)

        tk.Button(bottom, text="Close", command=win.destroy).pack(
            side="right", ipadx=10, ipady=3
        )

        def load_summary():
            # Clear
            for iid in tree.get_children():
                tree.delete(iid)

            try:
                year = int(self.cs_year_var.get())
                month = int(self.cs_month_var.get())
                if month < 1 or month > 12:
                    raise ValueError
            except Exception:
                messagebox.showerror(
                    "Invalid Date", "Year/Month invalid. Example: Year 2026, Month 2."
                )
                return

            month_key = f"{year:04d}-{month:02d}%"  # matches 'YYYY-MM-%'

            stats = {}  # client -> {'q': int, 'tax': int, 'comm': int}

            def ensure(c):
                if c not in stats:
                    stats[c] = {"q": 0, "tax": 0, "comm": 0}
                return stats[c]

            try:
                # Quotations
                self.app.cursor.execute(
                    "SELECT client_name, COUNT(*) FROM quotations WHERE date LIKE ? GROUP BY client_name",
                    (month_key,),
                )
                for c_name, cnt in self.app.cursor.fetchall():
                    if not c_name:
                        continue
                    ensure(c_name)["q"] += int(cnt or 0)

                # Tax invoices
                try:
                    self.app.cursor.execute(
                        "SELECT client_name, COUNT(*) FROM tax_invoices WHERE date LIKE ? GROUP BY client_name",
                        (month_key,),
                    )
                    for c_name, cnt in self.app.cursor.fetchall():
                        if not c_name:
                            continue
                        ensure(c_name)["tax"] += int(cnt or 0)
                except Exception:
                    pass

                # Commercial invoices
                try:
                    self.app.cursor.execute(
                        "SELECT client_name, COUNT(*) FROM commercial_invoices WHERE date LIKE ? GROUP BY client_name",
                        (month_key,),
                    )
                    for c_name, cnt in self.app.cursor.fetchall():
                        if not c_name:
                            continue
                        ensure(c_name)["comm"] += int(cnt or 0)
                except Exception:
                    pass

            except Exception as e:
                messagebox.showerror("DB Error", str(e), parent=win)
                return

            # Insert sorted by total docs
            sorted_items = sorted(
                stats.items(),
                key=lambda kv: (kv[1]["q"] + kv[1]["tax"] + kv[1]["comm"]),
                reverse=True,
            )

            if not sorted_items:
                tree.insert(
                    "",
                    "end",
                    values=("No data for selected month", 0, 0, 0),
                )
                return

            for client, v in sorted_items:
                tree.insert(
                    "",
                    "end",
                    values=(client, v["q"], v["tax"], v["comm"]),
                )

        btn_reload.configure(command=load_summary)

        # Double-click row to open chart directly
        def on_double_click(event):
            sel = tree.selection()
            if not sel:
                return
            client_name = tree.item(sel[0])["values"][0]
            self.show_client_month_chart(client_name)

        tree.bind("<Double-1>", on_double_click)

        # Initial load
        load_summary()

    # --- 2. CLIENT HISTORY POPUP (UNION QUERY) ---
    def show_client_details_popup(self, client_name):
        d_win = tk.Toplevel(self.root)
        d_win.title(f"History: {client_name}")
        d_win.geometry("900x600")
        
        tk.Label(d_win, text=f"Documents for: {client_name}", font=("Segoe UI", 14, "bold"), fg="#2c3e50").pack(pady=15)
        
        cols = ("type", "ref", "date", "amt")
        tv = ttk.Treeview(d_win, columns=cols, show='headings')
        tv.heading("type", text="Doc Type")
        tv.heading("ref", text="Ref No")
        tv.heading("date", text="Date")
        tv.heading("amt", text="Amount")
        
        tv.column("type", width=120)
        tv.column("ref", width=150)
        tv.column("date", width=100)
        tv.column("amt", width=120)
        tv.pack(fill='both', expand=True, padx=20, pady=5)
        
        try:
            # UNION ALL Query to fetch everything
            query = """
                SELECT 'Quotation', ref_no, date, grand_total FROM quotations WHERE client_name=?
                UNION ALL
                SELECT 'Tax Invoice', ref_no, date, grand_total FROM tax_invoices WHERE client_name=?
                UNION ALL
                SELECT 'Comm Invoice', ref_no, date, grand_total FROM commercial_invoices WHERE client_name=?
                UNION ALL
                SELECT 'Deliv Challan', ref_no, date, grand_total FROM delivery_challans WHERE client_name=?
                ORDER BY date DESC
            """
            self.app.cursor.execute(query, (client_name, client_name, client_name, client_name))
            rows = self.app.cursor.fetchall()
            currency = self.app.currency_symbol_var.get()
            
            for r in rows:
                # r[0]=Type, r[1]=Ref, r[2]=Date, r[3]=Amt
                amt = r[3] if r[3] else 0.0
                tv.insert("", "end", values=(r[0], r[1], r[2], f"{currency} {amt:,.0f}"))
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load: {e}")

        # Load Selected Function
        def load_selected_quote():
            sel = tv.selection()
            if not sel:
                messagebox.showwarning("Error", "Select a record first!", parent=d_win)
                return
            
            ref_no = tv.item(sel[0])['values'][0]
            try:
                # Wapis main screen par load karein
                self.app.cursor.execute("SELECT id, full_data FROM quotations WHERE ref_no=?", (ref_no,))
                row = self.app.cursor.fetchone()
                if row:
                    self.app.restore_data(row[1])
                    self.app.current_db_id = row[0]
                    self.app.root.title(f"Quotation Generator - [Loaded: {ref_no}]")
                    d_win.destroy()
                    self.close_dashboard() # Dashboard hata dein
                    messagebox.showinfo("Success", f"Quotation {ref_no} Loaded!")
            except Exception as e:
                messagebox.showerror("Error", f"Could not load: {e}")

        btn_fr = tk.Frame(d_win, pady=10)
        btn_fr.pack(fill='x')
        tk.Button(btn_fr, text="📂 Load Selected Quotation", bg="#2980b9", fg="white", font=("bold"), 
                  command=load_selected_quote).pack(pady=5)

    def show_client_month_chart(self, client_name):
        """Show per-document counts for a client for the selected month/year."""
        from datetime import date

        # Use current Client Summary filters if available, otherwise default to today.
        try:
            year = int(getattr(self, "cs_year_var", None) or date.today().year)
            month = int(getattr(self, "cs_month_var", None) or date.today().month)
        except Exception:
            year, month = date.today().year, date.today().month

        month_key = f"{year:04d}-{month:02d}%"

        q_c = t_c = c_c = 0

        try:
            # Quotations
            self.app.cursor.execute(
                "SELECT COUNT(*) FROM quotations WHERE client_name=? AND date LIKE ?",
                (client_name, month_key),
            )
            q_c = int(self.app.cursor.fetchone()[0] or 0)

            # Tax invoices
            try:
                self.app.cursor.execute(
                    "SELECT COUNT(*) FROM tax_invoices WHERE client_name=? AND date LIKE ?",
                    (client_name, month_key),
                )
                t_c = int(self.app.cursor.fetchone()[0] or 0)
            except Exception:
                t_c = 0

            # Commercial invoices
            try:
                self.app.cursor.execute(
                    "SELECT COUNT(*) FROM commercial_invoices WHERE client_name=? AND date LIKE ?",
                    (client_name, month_key),
                )
                c_c = int(self.app.cursor.fetchone()[0] or 0)
            except Exception:
                c_c = 0
        except Exception as e:
            messagebox.showerror("Error", f"Count load failed: {e}")
            return

        # Create chart window
        win = tk.Toplevel(self.root)
        win.title(f"Monthly Mix - {client_name}")
        win.geometry("600x400")

        fig = Figure(figsize=(5.5, 3.2), dpi=100)
        ax = fig.add_subplot(111)

        labels = ["Quotations", "Tax Invoices", "Comm Invoices"]
        values = [q_c, t_c, c_c]
        colors = ["#3498db", "#e74c3c", "#f1c40f"]

        x = list(range(len(labels)))
        ax.bar(x, values, color=colors, width=0.6)
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=15)
        ax.set_ylabel("Count")
        ax.set_title(f"{year}-{month:02d} Summary for {client_name}")

        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=win)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

        tk.Button(win, text="Close", command=win.destroy).pack(pady=5)

    def open_settings_window(self):
        """Compact 2-column settings window (700x600)."""
        sw = tk.Toplevel(self.root)
        sw.title("Settings & Database Maintenance")
        sw.geometry("700x600")
        sw.transient(self.root)
        sw.resizable(False, False)

        # Main container with 2 columns
        container = tk.Frame(sw, bg="#f4f6f9")
        container.pack(fill="both", expand=True, padx=15, pady=15)
        container.columnconfigure(0, weight=1)
        container.columnconfigure(1, weight=1)

        # Header row
        tk.Label(
            container,
            text="Settings",
            font=("Segoe UI", 16, "bold"),
            fg="#2c3e50",
            bg="#f4f6f9",
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))

        # --- LEFT COLUMN: Database Backup/Restore ---
        db_frame = tk.LabelFrame(
            container,
            text="Database Backup & Restore",
            fg="blue",
            font=("Segoe UI", 10, "bold"),
        )
        db_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 8), pady=(0, 10))
        tk.Label(db_frame, text="Save your data to avoid loss.", fg="grey").pack(pady=5)
        btn_fr = tk.Frame(db_frame)
        btn_fr.pack(pady=5)

        def perform_backup():
            try:
                backup_dir = r"C:\Quotation_Backups"
                if not os.path.exists(backup_dir):
                    os.makedirs(backup_dir)

                timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                filename = f"QuotationDB_Backup_{timestamp}.bak"
                full_path = os.path.join(backup_dir, filename)

                server = r".\SQLEXPRESS"
                database = "master"
                conn_str = (
                    f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};"
                    f"DATABASE={database};Trusted_Connection=yes;"
                )

                cn = pyodbc.connect(conn_str, autocommit=True)
                cur = cn.cursor()

                query = (
                    "BACKUP DATABASE QuotationDB TO DISK = ? "
                    "WITH FORMAT, NAME = 'Full Backup of QuotationDB';"
                )
                cur.execute(query, (full_path,))
                while cur.nextset():
                    pass
                cn.close()

                msg = f"Backup Successful!\n\nFile Saved at:\n{full_path}"
                messagebox.showinfo("Success", msg)

                try:
                    os.startfile(backup_dir)
                except Exception:
                    pass

            except Exception as e:
                messagebox.showerror(
                    "Backup Failed",
                    f"Error: {e}\n\nTry running Python as Administrator.",
                    parent=sw,
                )

        def perform_restore():
            path = filedialog.askopenfilename(
                initialdir=r"C:\Quotation_Backups",
                filetypes=[("SQL Backup", "*.bak")],
                title="Select Backup File to Restore",
            )
            if not path:
                return

            if not messagebox.askyesno(
                "WARNING",
                "Restoring will REPLACE all current data with this backup!\nAre you sure?",
                parent=sw,
            ):
                return

            try:
                server = r".\SQLEXPRESS"
                database = "master"
                conn_str = (
                    f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};"
                    f"DATABASE={database};Trusted_Connection=yes;"
                )

                cn = pyodbc.connect(conn_str, autocommit=True)
                cur = cn.cursor()

                kill_query = """
                    DECLARE @kill varchar(8000) = '';  
                    SELECT @kill = @kill + 'kill ' + CONVERT(varchar(5), session_id) + ';'  
                    FROM sys.dm_exec_sessions
                    WHERE database_id  = db_id('QuotationDB')
                    EXEC(@kill);
                """
                try:
                    cur.execute(kill_query)
                except Exception:
                    pass

                restore_q = "RESTORE DATABASE QuotationDB FROM DISK = ? WITH REPLACE;"
                cur.execute(restore_q, (path,))
                while cur.nextset():
                    pass
                cn.close()

                messagebox.showinfo(
                    "Success",
                    "Database Restored Successfully!\nApplication will now close.",
                    parent=sw,
                )
                self.root.quit()
            except Exception as e:
                messagebox.showerror("Restore Failed", f"Error: {e}", parent=sw)

        tk.Button(
            btn_fr,
            text="💾 Auto Backup (1-Click)",
            bg="#27ae60",
            fg="white",
            font=("bold"),
            width=22,
            command=perform_backup,
        ).pack(pady=2)
        tk.Button(
            btn_fr,
            text="♻ Restore from Backup",
            bg="#e67e22",
            fg="white",
            font=("bold"),
            width=22,
            command=perform_restore,
        ).pack(pady=4)

        # --- RIGHT COLUMN: License / Premium Info ---
        lic_frame = tk.LabelFrame(
            container,
            text="License / Premium",
            padx=10,
            pady=10,
        )
        lic_frame.grid(row=1, column=1, sticky="nsew", padx=(8, 0), pady=(0, 10))

        is_premium = False
        try:
            self.app.cursor.execute("SELECT MAX(is_premium) FROM users")
            row = self.app.cursor.fetchone()
            if row and row[0] == 1:
                is_premium = True
        except Exception:
            pass

        if is_premium:
            tk.Label(
                lic_frame,
                text="✅ Premium Features Unlocked",
                fg="green",
                font=("Segoe UI", 10, "bold"),
            ).pack(pady=(0, 6))
        else:
            tk.Label(
                lic_frame,
                text="Status: Free Version (Restricted)",
                fg="red",
                font=("Segoe UI", 10),
            ).pack(pady=(0, 8))

            def activate_license():
                from tkinter.simpledialog import askstring

                code = askstring(
                    "Activate", "Enter License Key provided by ODM-ONLINE:"
                )
                if not code:
                    return
                if code == "HVACR-PRO-786":
                    try:
                        self.app.cursor.execute("UPDATE users SET is_premium=1")
                        self.app.conn.commit()
                        messagebox.showinfo(
                            "Success",
                            "BRAVO! Premium Features Unlocked!\nPlease RESTART the software.",
                            parent=sw,
                        )
                        sw.destroy()
                    except Exception as e:
                        messagebox.showerror("Error", str(e), parent=sw)
                else:
                    messagebox.showerror("Failed", "Invalid License Key!", parent=sw)

            tk.Button(
                lic_frame,
                text="Enter License Key",
                bg="#2980b9",
                fg="white",
                font=("Segoe UI", 10, "bold"),
                cursor="hand2",
                command=activate_license,
            ).pack(fill="x", ipady=4)

        # --- BOTTOM ROW: Danger Zone (left) + Logout/Close (right) ---
        bottom = tk.Frame(container, bg="#f4f6f9")
        bottom.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        bottom.columnconfigure(0, weight=1)
        bottom.columnconfigure(1, weight=0)

        danger_frame = tk.LabelFrame(
            bottom, text="Danger Zone", fg="red", padx=10, pady=10
        )
        danger_frame.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        tk.Label(
            danger_frame,
            text="Delete your account and reset setup?",
        ).pack()

        def delete_account_logic():
            ans = messagebox.askyesno(
                "WARNING",
                "Are you sure?\nThis will DELETE your account permanently.",
                parent=sw,
            )
            if not ans:
                return
            try:
                self.app.cursor.execute("DELETE FROM users")
                self.app.conn.commit()
                messagebox.showinfo(
                    "Reset", "Account Deleted. Restarting Setup.", parent=sw
                )
                sw.destroy()
                self.close_dashboard()
                self.app.root.withdraw()
                self.app.check_user_login()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete: {e}", parent=sw)

        tk.Button(
            danger_frame,
            text="🗑 DELETE MY ACCOUNT",
            font=("Arial", 10, "bold"),
            bg="#c0392b",
            fg="white",
            cursor="hand2",
            command=delete_account_logic,
        ).pack(pady=6, fill="x")

        right_bottom = tk.Frame(bottom, bg="#f4f6f9")
        right_bottom.grid(row=0, column=1, sticky="ne")

        def do_logout():
            if messagebox.askyesno(
                "Confirm", "Are you sure you want to Logout?", parent=sw
            ):
                sw.destroy()
                self.close_dashboard()
                self.app.root.withdraw()
                self.app.perform_login(None)

        tk.Button(
            right_bottom,
            text="🚪 LOGOUT",
            bg="#95a5a6",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            width=16,
            command=do_logout,
        ).pack(pady=(0, 6), fill="x")

        tk.Button(
            right_bottom,
            text="Close",
            width=16,
            command=sw.destroy,
        ).pack(fill="x")

    # --- SCRAPER POPUP ---
    def open_scraper_popup(self):
        # --- PREMIUM LOCK ---
        is_allowed = False
        try:
            self.app.cursor.execute("SELECT MAX(is_premium) FROM users")
            row = self.app.cursor.fetchone()
            if row and row[0] == 1: is_allowed = True
        except: pass

        if not is_allowed:
            messagebox.showwarning("Locked", "Premium Feature! Enter License Key in Settings.")
            return
       

        sw = tk.Toplevel(self.root)
        sw.title("AI Client Finder (Deep Search)")
        sw.geometry("550x450")
        sw.transient(self.root)
        
        tk.Label(sw, text="Find Clients with Phone Numbers", font=("Segoe UI", 12, "bold"), fg="#2980b9").pack(pady=15)
        
        # 1. Area Input
        tk.Label(sw, text="Area (e.g. Gulberg, DHA):").pack()
        area_ent = tk.Entry(sw, width=35, relief="solid", bd=1)
        area_ent.pack(pady=5)
        
        # 2. City Input
        tk.Label(sw, text="City").pack()
        city_ent = tk.Entry(sw, width=35, relief="solid", bd=1)
        city_ent.pack(pady=5)
        city_ent.insert(0, "Lahore")

        # 3. Category Input
        tk.Label(sw, text="Category (e.g. Textile Mills, Hospitals):").pack()
        cat_ent = tk.Entry(sw, width=35, relief="solid", bd=1)
        cat_ent.pack(pady=5)

        status_lbl = tk.Label(sw, text="Ready to Extract...", fg="grey")
        status_lbl.pack(pady=10)

        def run_scraper():
            area = area_ent.get()
            city = city_ent.get()
            cat = cat_ent.get()
            
            if not area or not city or not cat:
                messagebox.showerror("Error", "Please fill ALL 3 fields!")
                return
            
            status_lbl.config(text="Running Deep Scan... (This takes time)", fg="blue")
            sw.update()
            
            import scrapper
            try:
                # 3 cheezain bhej rahe hain
                res = scrapper.find_clients(area, city, cat)
                status_lbl.config(text="Done!", fg="green")
                messagebox.showinfo("Report", res)
            except Exception as e:
                status_lbl.config(text="Error", fg="red")
                messagebox.showerror("Error", str(e))

        tk.Button(sw, text="🔍 START DEEP EXTRACTION", bg="#27ae60", fg="white", font=("bold"),
                  command=run_scraper).pack(pady=10, ipadx=10)  
        
        # --- WHATSAPP POPUP ---
    # --- WHATSAPP POPUP (UPDATED FOR DOCUMENTS) ---
    def open_whatsapp_popup(self):
        # Premium Check
        is_allowed = False
        try:
            self.app.cursor.execute("SELECT MAX(is_premium) FROM users")
            row = self.app.cursor.fetchone()
            if row and row[0] == 1: is_allowed = True
        except: pass

        if not is_allowed:
            messagebox.showwarning("Locked", "Premium Feature! Please unlock in Settings.")
            return

        sw = tk.Toplevel(self.root)
        sw.title("WhatsApp Marketing Bot")
        sw.geometry("500x550") 
        sw.transient(self.root)
        
        tk.Label(sw, text="Bulk WhatsApp Sender", font=("Segoe UI", 14, "bold"), fg="#2ecc71").pack(pady=10)
        
        # 1. Excel List Selection
        tk.Label(sw, text="Step 1: Select Contact List (Excel)").pack(pady=2)
        file_path_var = tk.StringVar()
        
        def browse_excel():
            path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx;*.csv")])
            if path: file_path_var.set(path)
        
        f_frame = tk.Frame(sw)
        f_frame.pack()
        tk.Entry(f_frame, textvariable=file_path_var, width=30).pack(side='left')
        tk.Button(f_frame, text="Browse Excel", command=browse_excel).pack(side='left', padx=5)

        # 2. Attachment Selection (UPDATED FOR ALL FILES)
        tk.Label(sw, text="Step 2: Select Attachment (Image / PDF / Doc)").pack(pady=(10, 2))
        img_path_var = tk.StringVar()
        
        def browse_attachment():
            # Yahan ab humne *.* allow kar diya hai
            path = filedialog.askopenfilename(filetypes=[
                ("All Files", "*.*"),
                ("Images", "*.jpg;*.jpeg;*.png"),
                ("Documents", "*.pdf;*.docx;*.xlsx;*.txt")
            ])
            if path: img_path_var.set(path)
            
        i_frame = tk.Frame(sw)
        i_frame.pack()
        tk.Entry(i_frame, textvariable=img_path_var, width=30).pack(side='left')
        tk.Button(i_frame, text="Browse File", command=browse_attachment).pack(side='left', padx=5)

        # 3. Message Text
        tk.Label(sw, text="Step 3: Type Message").pack(pady=10)
        msg_text = tk.Text(sw, height=5, width=40, font=("Arial", 10))
        msg_text.pack(pady=5)
        msg_text.insert("1.0", "Asalam-o-Alaikum,\nCheck our services!")

        # 4. Start Button
        def start_bot():
            path = file_path_var.get()
            attach_path = img_path_var.get() # Attachment path
            msg = msg_text.get("1.0", "end-1c")
            
            if not path or not os.path.exists(path):
                messagebox.showerror("Error", "Please select a valid Excel file!")
                return
            
            if not msg.strip():
                messagebox.showerror("Error", "Message cannot be empty!")
                return

            ans = messagebox.askyesno("Confirm", 
                "⚠️ ANTI-BAN MODE ENABLED\n"
                "Messages will be sent with RANDOM delays (15-25 sec).\n"
                "Do not close Chrome manually.\n\nStart Campaign?")
            
            if ans:
                import whatsapp_bot
                sw.destroy()
                try:
                    # File path ab bheja ja raha hai
                    result = whatsapp_bot.send_messages(path, msg, attach_path)
                    messagebox.showinfo("Report", result)
                except Exception as e:
                    messagebox.showerror("Error", str(e))

        tk.Button(sw, text="🚀 START CAMPAIGN", bg="#27ae60", fg="white", font=("bold"), 
                  command=start_bot).pack(pady=15, ipadx=10, ipady=5)