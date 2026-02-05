import tkinter as tk
from tkinter import ttk

# --- COLORS (Fixed for Dark Dashboard) ---
BG_MAIN  = "#121212"      
BG_SIDE  = "#000000"      
BG_CARD  = "#1e1e1e"      
ACCENT   = "#00e676"      
TEXT     = "#ffffff"      
TEXT_DIM = "#b0bec5"      

# --- FONTS ---
FONT_H1 = ("Segoe UI", 22, "bold")
FONT_H2 = ("Segoe UI", 16, "bold")
FONT_NORMAL = ("Segoe UI", 10)
FONT_BTN = ("Segoe UI", 11)

def apply_theme_to_root(root):
    # Root ka color change nahi karenge taake baqi windows kharab na hon
    pass 

def style_sidebar_button(btn, active_color=ACCENT):
    btn.configure(
        bg=BG_SIDE,
        fg=TEXT,
        activebackground="#2c2c2c",
        activeforeground=active_color,
        bd=0,
        relief="flat",
        cursor="hand2",
        font=FONT_BTN,
        anchor="w",
        padx=20,
        pady=12
    )
    def on_enter(e):
        e.widget['bg'] = '#1a1a1a'
        e.widget['fg'] = active_color
    def on_leave(e):
        e.widget['bg'] = BG_SIDE 
        e.widget['fg'] = TEXT
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)

def apply_treeview_style():
    """ 
    Ye function zabardasti Table ko Dark banayega 
    chahe poori app White (Lumen) kyun na ho.
    """
    style = ttk.Style()
    
    # Hum ek nayi style banayenge 'Dark.Treeview'
    style.layout("Dark.Treeview", style.layout("Treeview")) # Layout copy
    
    style.configure("Dark.Treeview",
                    background=BG_CARD,
                    foreground=TEXT,
                    fieldbackground=BG_CARD,
                    rowheight=30,
                    borderwidth=0,
                    font=("Segoe UI", 10))
    
    style.configure("Dark.Treeview.Heading",
                    background="#333333",
                    foreground="white", # Heading text white
                    relief="flat",
                    font=("Segoe UI", 10, "bold"))
    
    style.map("Dark.Treeview",
              background=[('selected', ACCENT)],
              foreground=[('selected', 'black')])

def create_card(parent):
    return tk.Frame(parent, bg=BG_CARD, bd=1, relief="solid", highlightbackground="#333", highlightthickness=1)