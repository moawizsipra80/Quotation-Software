import tkinter as tk
from tkinter import ttk  
root = tk.Tk()           
root.title("Quotation Generator")
root.geometry("400x200")  
frame = ttk.LabelFrame(root, text="Customer Info")
frame.pack(fill="x", padx=10, pady=10)

tk.Label(frame, text="Name:").grid(row=0, column=0, sticky="w")
name_var = tk.StringVar()
tk.Entry(frame, textvariable=name_var).grid(row=0, column=1, sticky="w")

tk.Label(frame, text="Email:").grid(row=1, column=0, sticky="w")
email_var = tk.StringVar()
tk.Entry(frame, textvariable=email_var).grid(row=1, column=1, sticky="w")

tk.Label(frame,text="Address").grid(row=2,column=0,sticky="w")
address_var=tk.StringVar()
tk.Entry(frame,textvariable=address_var).grid(row=2,column=1,sticky="w")

root.mainloop()
