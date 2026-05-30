import os

path = "e:/quotation/quotation.py"
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# We need to insert the missing perform_login method.
# It was likely overwritten or lost during previous edits.
# We will insert it before the initialization block or after perform_setup
# perform_setup ends around line 726 in recent view.
# We will look for the end of perform_setup and append perform_login.

# Identifying the end of perform_setup
end_of_setup_marker = '    # ========================================================================='
# or specifically before DATABASE METHODS section
start_idx = content.find(end_of_setup_marker)

if start_idx != -1:
    # Insert perform_login before the separator
    login_code = r'''
    def perform_login(self, user_data=None):
        if user_data:
            self.root.deiconify()
            self.current_username = user_data[1]
            
            # Load Profile Pic Path if available
            try:
                self.cursor.execute("SELECT profile_pic_path, theme_preference FROM users WHERE username=?", (self.current_username,))
                urow = self.cursor.fetchone()
                if urow:
                    self.current_user_pic_path = urow[0]
                    theme = urow[1] if urow[1] else "cosmo"
                    self.style = ThemeManager.apply_theme(self.root, theme)
            except Exception as e:
                print(f"Login data fetch error: {e}")
                self.current_user_pic_path = None

            # Initialize Dashboard
            from dashboard import DashboardPanel
            # If dashboard already exists destroy it to be safe
            if self.current_dashboard:
                try: 
                    if hasattr(self.current_dashboard, 'destroy'): self.current_dashboard.destroy()
                    elif hasattr(self.current_dashboard, 'frame'): self.current_dashboard.frame.destroy()
                except: pass
            
            self.current_dashboard = DashboardPanel(self)
            return 

        self.root.withdraw()
        
        # --- NEW PROFESSIONAL LOGIN DESIGN ---
        login_win = tk.Toplevel(self.root)
        login_win.title("ODM Secure Login")
        login_win.state('zoomed')
        login_win.protocol("WM_DELETE_WINDOW", lambda: sys.exit())

        # Colors (Matching Splash)
        BG_COLOR = "#0f172a"
        CARD_BG = "#1e293b"
        ACCENT_COLOR = "#38bdf8"
        TEXT_WHITE = "#f8fafc"
        TEXT_GREY = "#94a3b8"
        INPUT_BG = "#334155"
        BORDER_COLOR = "#475569"

        login_win.configure(bg=BG_COLOR)

        # Main Container (Center)
        container = tk.Frame(login_win, bg=BG_COLOR)
        container.place(relx=0.5, rely=0.5, anchor='center')

        # Card
        card = tk.Frame(container, bg=CARD_BG, highlightthickness=1, highlightbackground=BORDER_COLOR, padx=40, pady=40)
        card.pack()

        # 1. LOGO
        script_dir = os.path.dirname(os.path.abspath(__file__))
        candidates = ["splash_logo.png", "logo.png", "logo.jpg", "logo.jpeg", "logo.ico"]
        found_logo = None
        for c in candidates:
            p = os.path.join(script_dir, c)
            if os.path.exists(p):
                found_logo = p
                break
        
        if found_logo:
            try:
                pil_img = Image.open(found_logo)
                pil_img.thumbnail((80, 80), Image.Resampling.LANCZOS)
                logo_img = ImageTk.PhotoImage(pil_img)
                l = tk.Label(card, image=logo_img, bg=CARD_BG)
                l.image = logo_img
                l.pack(pady=(0, 20))
            except: pass

        # 2. HEADER
        tk.Label(card, text="WELCOME BACK", font=("Segoe UI", 24, "bold"), fg=TEXT_WHITE, bg=CARD_BG).pack(pady=(0, 5))
        tk.Label(card, text="Login to your account to continue", font=("Segoe UI", 10), fg=TEXT_GREY, bg=CARD_BG).pack(pady=(0, 30))

        # 3. INPUT FIELDS
        def create_styled_entry(parent, label_text, show_char=None):
            tk.Label(parent, text=label_text, font=("Segoe UI", 10, "bold"), fg=ACCENT_COLOR, bg=CARD_BG).pack(anchor='w', pady=(10, 5))
            e_frame = tk.Frame(parent, bg=INPUT_BG, highlightthickness=1, highlightbackground=BORDER_COLOR)
            e_frame.pack(fill='x', ipady=5)
            ent = tk.Entry(e_frame, bg=INPUT_BG, fg="white", font=("Segoe UI", 11), relief='flat', insertbackground='white')
            if show_char: ent.config(show=show_char)
            ent.pack(fill='x', padx=10, pady=3)
            return ent

        u_ent = create_styled_entry(card, "USERNAME")
        p_ent = create_styled_entry(card, "PASSWORD", "*")

        # 4. REMEMBER ME & FORGOT PASS ROW
        opts_frame = tk.Frame(card, bg=CARD_BG)
        opts_frame.pack(fill='x', pady=20)

        self.remember_me_var = tk.BooleanVar(value=False)
        rem_file = os.path.join(os.getenv('APPDATA'), "odm_remember.json")

        cb = tk.Checkbutton(opts_frame, text="Remember Me", variable=self.remember_me_var, 
                            bg=CARD_BG, fg=TEXT_GREY, selectcolor=BG_COLOR, activebackground=CARD_BG, activeforeground=TEXT_WHITE, font=("Segoe UI", 9))
        cb.pack(side='left')

        lbl_forgot = tk.Label(opts_frame, text="Forgot Password?", font=("Segoe UI", 9, "bold"), fg=ACCENT_COLOR, bg=CARD_BG, cursor="hand2")
        lbl_forgot.pack(side='right')
        lbl_forgot.bind("<Button-1>", lambda e: self.forgot_password_flow(u_ent.get().strip(), login_win))

        # 5. LOADING SAVED CREDENTIALS
        try:
            if os.path.exists(rem_file):
                with open(rem_file, 'r') as f:
                    saved = json.load(f)
                    u_ent.insert(0, saved.get('user', ''))
                    p_ent.insert(0, saved.get('pass', ''))
                    self.remember_me_var.set(True)
        except: pass

        # 6. ACTION BUTTONS
        def on_enter(e): btn_login.config(bg="#0ea5e9") 
        def on_leave(e): btn_login.config(bg=ACCENT_COLOR)

        def try_login():
            username = u_ent.get().strip()
            password = p_ent.get().strip()
            
            # Visual Feedback
            btn_login.config(text="VERIFYING...", state='disabled')
            login_win.update()

            self.cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
            row = self.cursor.fetchone()
            
            if row:
                try:
                    if self.remember_me_var.get():
                        with open(rem_file, 'w') as f: json.dump({'user': username, 'pass': password}, f)
                    elif os.path.exists(rem_file):
                        os.remove(rem_file)
                except: pass
                
                login_win.destroy()
                self.perform_login(row)
            else:
                btn_login.config(text="LOGIN", state='normal')
                messagebox.showerror("Login Failed", "Invalid Username or Password", parent=login_win)
                btn_login.config(text="LOGIN", state='normal')

        btn_login = tk.Button(card, text="LOGIN", font=("Segoe UI", 12, "bold"), bg=ACCENT_COLOR, fg=BG_COLOR, 
                              relief='flat', cursor="hand2", command=try_login)
        btn_login.pack(fill='x', pady=(10, 20), ipady=5)
        btn_login.bind("<Enter>", on_enter)
        btn_login.bind("<Leave>", on_leave)

        # 7. FOOTER ACTIONS (Trial & Setup)
        license_path = os.path.join(os.getenv('APPDATA'), "ODM_Quotation_Gen", "license.key")
        if not os.path.exists(license_path):
            count = self.get_trial_count()
            rem = 2 - count
            tk.Label(card, text=f"⚠️ TRIAL MODE: {rem} Quotations Left", fg="#fbbf24", bg=CARD_BG, font=("Segoe UI", 9, "bold")).pack(pady=(0, 15))

        tk.Label(card, text="Don't have a profile?", fg=TEXT_GREY, bg=CARD_BG, font=("Segoe UI", 9)).pack(pady=(10, 5))
        
        btn_setup = tk.Label(card, text="Setup New Profile", font=("Segoe UI", 10, "bold"), fg=ACCENT_COLOR, bg=CARD_BG, cursor="hand2")
        btn_setup.pack()
        btn_setup.bind("<Button-1>", lambda e: [login_win.destroy(), self.perform_setup()])

        # Footer Copyright
        tk.Label(login_win, text="© 2026 ODM Online System", font=("Segoe UI", 8), fg=BORDER_COLOR, bg=BG_COLOR).place(relx=0.5, rely=0.95, anchor='center')

'''
    new_content = content[:start_idx] + login_code + content[start_idx:]
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("SUCCESS: perform_login restored.")
else:
    print("MARKER NOT FOUND - Insertion failed")
