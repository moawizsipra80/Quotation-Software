import os

path = "e:/quotation/quotation.py"
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

start_marker = '        main_fr = ttk.Frame(container, padding=30)'
end_marker = '                   bootstyle="secondary-outline", width=25).pack(pady=5)'

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

if start_idx != -1 and end_idx != -1:
    end_idx += len(end_marker)
    
    new_code = r'''        # 1. LOGO
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
        # Helper for styled entry
        def create_styled_entry(parent, label_text, show_char=None):
            tk.Label(parent, text=label_text, font=("Segoe UI", 10, "bold"), fg=ACCENT_COLOR, bg=CARD_BG).pack(anchor='w', pady=(10, 5))
            
            # Entry Container for padding/border look
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
        tk.Label(login_win, text="© 2026 ODM Online System", font=("Segoe UI", 8), fg=BORDER_COLOR, bg=BG_COLOR).place(relx=0.5, rely=0.95, anchor='center')'''

    new_content = content[:start_idx] + new_code + content[end_idx:]
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("SUCCESS")
else:
    print("MARKERS NOT FOUND")
    print(f"Start: {start_idx}, End: {end_idx}")
