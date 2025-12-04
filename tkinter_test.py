import tkinter as tk

print("Launching minimal Tkinter window...")
root = tk.Tk()
root.title("Tkinter Test Window")
root.geometry("300x150")
label = tk.Label(root, text="If you see this, Tkinter works!", font=("Arial", 14))
label.pack(pady=40)
root.mainloop()
print("Window closed.")
