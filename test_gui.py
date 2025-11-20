"""Test if tkinter works"""
import tkinter as tk
from tkinter import messagebox

print("Creating window...")
root = tk.Tk()
root.title("Test GUI")
root.geometry("300x200")

label = tk.Label(root, text="GUI Test - Nếu bạn thấy cửa sổ này, tkinter hoạt động!", wraplength=250)
label.pack(pady=50)

button = tk.Button(root, text="Click me!", command=lambda: messagebox.showinfo("Test", "Button works!"))
button.pack()

print("Starting mainloop...")
root.mainloop()
print("Window closed")

