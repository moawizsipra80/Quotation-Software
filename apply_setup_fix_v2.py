import os

path = "e:/quotation/quotation.py"
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

start_marker = '    def perform_setup(self):'
end_marker = '    # def perform_login(self, user_data):'
# The end marker in the previous view seemed to be the commented out login function, 
# BUT in the most recent view (lines 1000-1300), I see:
# 1041:         btn_reset_profile = ttk.Button(f, text="Forgot Answers? Setup New Profile", command=fallback_reset, style="danger.Outline.TButton")
# 1042: 
# 1043:     # =========================================================================

# The perform_setup function I wrote in the LAST step ended with `btn_save.pack(...)`.
# I need to find the START of perform_setup I recently wrote and replace it.

# Let's use a unique string from my last edit to identify the start/end if possible, 
# or just rely on indentation.

# My last edit had: "        # 1. HEADER\n        tk.Label(card, text=\"SETUP YOUR PROFILE\"..."
# and ended with "btn_save.bind(\"<Leave>\", on_leave)"

# Let's search for the function definition and the next function definition.
start_idx = content.find('    def perform_setup(self):')
end_idx = content.find('    # =========================================================================', start_idx)

# If the comment separator isn't found or is too far, look for init_database
if end_idx == -1:
    end_idx = content.find('    def init_database(self):', start_idx)

if start_idx != -1 and end_idx != -1:
    new_code = r'''    def perform_setup(self):
        self.root.withdraw()
        setup_win = tk.Toplevel(self.root)
        setup_win.title("First Time Setup - Create Profile")
        setup_win.state('zoomed')
        
        # Colors (Matching Login/Splash)
        BG_COLOR = "#0f172a"
        CARD_BG = "#1e293b"
        ACCENT_COLOR = "#38bdf8"
        TEXT_WHITE = "#f8fafc"
        TEXT_GREY = "#94a3b8"
        INPUT_BG = "#334155"
        BORDER_COLOR = "#475569"

        setup_win.configure(bg=BG_COLOR)
        
        def on_setup_close():
            try:
                self.cursor.execute("SELECT COUNT(*) FROM users")
                if self.cursor.fetchone()[0] > 0:
                    setup_win.destroy()
                    self.perform_login(None)
                else:
                    sys.exit()
            except:
                sys.exit()

        setup_win.protocol("WM_DELETE_WINDOW", on_setup_close) 

        # Scrollable Container - FIXING WHITE BACKGROUND
        # Pass bg to make_scrollable so internal frame matches
        scrollable_content = self.make_scrollable(setup_win, bg=BG_COLOR)
        
        # Ensure the canvas (parent of scrollable_content) also has the bg
        try:
            scrollable_content.master.configure(bg=BG_COLOR)
        except: pass

        # Main Container - Center it with some padding
        container = tk.Frame(scrollable_content, bg=BG_COLOR)
        container.pack(fill='both', expand=True, padx=40, pady=40)
        
        # Center Card - Increased Padding/Width ("Khola karo")
        card = tk.Frame(container, bg=CARD_BG, highlightthickness=1, highlightbackground=BORDER_COLOR, padx=50, pady=50)
        card.pack(anchor='center', ipadx=20, ipady=20) 

        # 1. HEADER
        tk.Label(card, text="SETUP YOUR PROFILE", font=("Segoe UI", 28, "bold"), fg=TEXT_WHITE, bg=CARD_BG).pack(pady=(0, 10))
        tk.Label(card, text="Create a new admin profile to get started", font=("Segoe UI", 11), fg=TEXT_GREY, bg=CARD_BG).pack(pady=(0, 30))

        # 2. TOP ACTIONS (Login / Restore) & SEPARATOR
        top_act_fr = tk.Frame(card, bg=CARD_BG)
        top_act_fr.pack(fill='x', pady=(0, 30))

        def go_to_login():
             self.cursor.execute("SELECT COUNT(*) FROM users")
             if self.cursor.fetchone()[0] == 0:
                 messagebox.showwarning("No Profile", "No profile found. Please Create Profile first.", parent=setup_win)
                 return
             setup_win.destroy()
             self.perform_login(None)

        ttk.Button(top_act_fr, text="Already have an account? Login", command=go_to_login, bootstyle="link").pack(side='right')
        
        ttk.Button(top_act_fr, text="♻️ Restore from Backup", 
                   command=lambda: self.restore_database(parent_win=setup_win), 
                   bootstyle="info-outline").pack(side='left')

        ttk.Separator(card, orient='horizontal').pack(fill='x', pady=(0, 30))

        # 3. COLUMNS
        cols_fr = tk.Frame(card, bg=CARD_BG)
        cols_fr.pack(fill='both', expand=True)

        # Re-usable Entry Helper with MORE PADDING
        def create_styled_entry(parent, label_text, show_char=None):
            tk.Label(parent, text=label_text, font=("Segoe UI", 10, "bold"), fg=ACCENT_COLOR, bg=CARD_BG).pack(anchor='w', pady=(15, 5))
            e_frame = tk.Frame(parent, bg=INPUT_BG, highlightthickness=1, highlightbackground=BORDER_COLOR)
            e_frame.pack(fill='x', ipady=6) # Increased interactive height
            ent = tk.Entry(e_frame, bg=INPUT_BG, fg="white", font=("Segoe UI", 11), relief='flat', insertbackground='white')
            if show_char: ent.config(show=show_char)
            ent.pack(fill='x', padx=10, pady=5)
            return ent

        # --- LEFT COLUMN: CREDENTIALS ---
        left_col = tk.Frame(cols_fr, bg=CARD_BG)
        left_col.pack(side='left', fill='both', expand=True, padx=(0, 30))

        tk.Label(left_col, text="User Credentials", font=("Segoe UI", 14, "bold", "underline"), fg=TEXT_WHITE, bg=CARD_BG).pack(anchor='w', pady=(0, 15))

        name_ent = create_styled_entry(left_col, "FULL NAME")
        user_ent = create_styled_entry(left_col, "USERNAME")
        pass_ent = create_styled_entry(left_col, "PASSWORD", "*")

        # Profile Pic
        tk.Label(left_col, text="PROFILE PICTURE", font=("Segoe UI", 10, "bold"), fg=ACCENT_COLOR, bg=CARD_BG).pack(anchor='w', pady=(20, 10))
        pic_row = tk.Frame(left_col, bg=CARD_BG)
        pic_row.pack(fill='x')
        
        self.preview_img_lbl = tk.Label(pic_row, text="No Image", bg=INPUT_BG, fg=TEXT_GREY, width=12, height=6)
        self.preview_img_lbl.pack(side='left', padx=(0, 15))
        
        self.setup_pic_path = None
        
        def choose_pic():
            p = filedialog.askopenfilename(parent=setup_win, filetypes=[("Images", "*.png;*.jpg;*.jpeg")])
            if p:
                self.setup_pic_path = p
                try:
                    load = Image.open(p)
                    load.thumbnail((80, 80), Image.Resampling.LANCZOS)
                    self.setup_preview_photo = ImageTk.PhotoImage(load)
                    self.preview_img_lbl.config(image=self.setup_preview_photo, text="", width=80, height=80) 
                    self.preview_img_lbl.config(image=self.setup_preview_photo)
                except Exception as e:
                    messagebox.showerror("Error", f"Invalid Image: {e}")

        btn_pic = tk.Button(pic_row, text="Browse Image...", command=choose_pic, bg=INPUT_BG, fg=TEXT_WHITE, relief='flat', font=("Segoe UI", 9))
        btn_pic.pack(side='left', fill='x', expand=True, ipady=8)


        # --- RIGHT COLUMN: SECURITY ---
        right_col = tk.Frame(cols_fr, bg=CARD_BG)
        right_col.pack(side='right', fill='both', expand=True, padx=(30, 0))

        tk.Label(right_col, text="Security Recovery", font=("Segoe UI", 14, "bold", "underline"), fg=TEXT_WHITE, bg=CARD_BG).pack(anchor='w', pady=(0, 15))
        tk.Label(right_col, text="Required for password reset.", font=("Segoe UI", 9), fg="#fbbf24", bg=CARD_BG).pack(anchor='w', pady=(0, 5))

        q1_ent = create_styled_entry(right_col, "Question 1")
        a1_ent = create_styled_entry(right_col, "Answer 1")
        
        q2_ent = create_styled_entry(right_col, "Question 2")
        a2_ent = create_styled_entry(right_col, "Answer 2")

        q3_ent = create_styled_entry(right_col, "Question 3")
        a3_ent = create_styled_entry(right_col, "Answer 3")

        # 4. SUBMIT BUTTON
        def save_user():
            # Strip extra spaces
            full_name = name_ent.get().strip()
            username = user_ent.get().strip()
            password = pass_ent.get().strip()
            
            # Security
            q1, a1 = q1_ent.get().strip(), a1_ent.get().strip()
            q2, a2 = q2_ent.get().strip(), a2_ent.get().strip()
            q3, a3 = q3_ent.get().strip(), a3_ent.get().strip()

            if not (full_name and username and password and q1 and a1 and q2 and a2 and q3 and a3):
                messagebox.showwarning("Input", "All fields (Credentials & 3 Q/A) are required!", parent=setup_win)
                return

            try:
                # Save to DB
                self.cursor.execute("""
                    INSERT INTO users (full_name, username, password, q1, a1, q2, a2, q3, a3, profile_pic_path, is_premium)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
                """, (full_name, username, password, q1, a1, q2, a2, q3, a3, self.setup_pic_path))
                
                self.conn.commit()
                messagebox.showinfo("Success", "Profile Created Successfully! Login to continue.", parent=setup_win)
                setup_win.destroy()
                self.perform_login(None) 
            except Exception as e:
                messagebox.showerror("Error", f"Error saving profile: {e}", parent=setup_win)
                if "UNIQUE constraint" in str(e):
                    messagebox.showerror("Error", "Username already taken.", parent=setup_win)

        tk.Frame(card, height=40, bg=CARD_BG).pack() # Larger Spacer

        def on_enter(e): btn_save.config(bg="#22c55e")
        def on_leave(e): btn_save.config(bg="#16a34a") 

        btn_save = tk.Button(card, text="SAVE & START SYSTEM", font=("Segoe UI", 12, "bold"), bg="#16a34a", fg="white", 
                             relief='flat', cursor="hand2", command=save_user)
        btn_save.pack(fill='x', pady=20, ipady=10)
        btn_save.bind("<Enter>", on_enter)
        btn_save.bind("<Leave>", on_leave)

'''
    new_content = content[:start_idx] + new_code + content[end_idx:]
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("SUCCESS")
else:
    print("MARKERS NOT FOUND")
