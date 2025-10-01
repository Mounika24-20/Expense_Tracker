import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
import os
import subprocess


conn = sqlite3.connect("expenses.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item TEXT NOT NULL,
    amount REAL NOT NULL,
    category TEXT NOT NULL
)
""")
conn.commit()

categories = ["Food", "Travel", "Bills", "Shopping", "Other"]


def add_expense():
    item = entry_item.get().strip()
    amount = entry_amount.get().strip()
    category = category_var.get()
    if item == "" or amount == "" or category == "":
        messagebox.showwarning("Input Error", "Please fill all fields")
        return
    try:
        amount = float(amount)
    except:
        messagebox.showwarning("Input Error", "Amount must be a number")
        return
    cursor.execute("INSERT INTO expenses (item, amount, category) VALUES (?, ?, ?)", (item, amount, category))
    conn.commit()
    entry_item.delete(0, tk.END)
    entry_amount.delete(0, tk.END)
    show_expenses()

def delete_expense():
    try:
        selected = listbox.get(listbox.curselection())
        expense_id = selected.split(" | ")[0]
        cursor.execute("DELETE FROM expenses WHERE id=?", (expense_id,))
        conn.commit()
        show_expenses()
    except:
        messagebox.showwarning("Selection Error", "Please select an expense to delete")

def show_expenses():
    listbox.delete(0, tk.END)
    cursor.execute("SELECT * FROM expenses")
    rows = cursor.fetchall()
    total = 0
    for row in rows:
        listbox.insert(tk.END, f"{row[0]:<3} | {row[1]:<15} | ₹{row[2]:>8} | {row[3]}")
        total += row[2]
    listbox.insert(tk.END, "-"*50)
    listbox.insert(tk.END, f"Total: ₹{total:>36}")
    draw_charts()

def draw_charts():
    cursor.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
    data = cursor.fetchall()
    categories_list = [d[0] for d in data]
    amounts_list = [d[1] for d in data]

    for widget in chart_frame.winfo_children():
        widget.destroy()

    if not data:
        return

    fig1 = plt.Figure(figsize=(4,2.5), dpi=100)
    ax1 = fig1.add_subplot(111)
    ax1.bar(categories_list, amounts_list, color="#00e676")
    ax1.set_title("Expenses by Category (Bar)", color="white")
    ax1.set_facecolor("#121212")
    fig1.patch.set_facecolor("#121212")
    ax1.tick_params(colors="white", labelsize=9)
    ax1.set_ylabel("Amount ₹", color="white")
    canvas1 = FigureCanvasTkAgg(fig1, master=chart_frame)
    canvas1.draw()
    canvas1.get_tk_widget().pack(side=tk.LEFT, padx=5)

   
    fig2 = plt.Figure(figsize=(4,2.5), dpi=100)
    ax2 = fig2.add_subplot(111)
    ax2.pie(amounts_list, labels=categories_list, autopct="%1.1f%%", textprops={'color':'white'})
    ax2.set_title("Expenses by Category (Pie)", color="white")
    fig2.patch.set_facecolor("#121212")
    canvas2 = FigureCanvasTkAgg(fig2, master=chart_frame)
    canvas2.draw()
    canvas2.get_tk_widget().pack(side=tk.RIGHT, padx=5)

def export_and_open_excel():
    cursor.execute("SELECT * FROM expenses")
    data = cursor.fetchall()
    if not data:
        messagebox.showwarning("No Data", "No expenses to export!")
        return

    df = pd.DataFrame(data, columns=["ID", "Item", "Amount", "Category"])
    today = datetime.now().strftime("%Y-%m-%d")
    file_name = f"Expenses_{today}.xlsx"
    file_path = os.path.join(os.getcwd(), file_name)
    df.to_excel(file_path, index=False)

    try:
        if os.name == 'nt':  
            os.startfile(file_path)
        elif os.name == 'posix':  
            subprocess.call(('open', file_path))
        else:
            messagebox.showinfo("Exported", f"Expenses exported to:\n{file_path}")
            return
        messagebox.showinfo("Exported", f"Expenses exported and opened:\n{file_path}")
    except Exception as e:
        messagebox.showinfo("Exported", f"Expenses exported to:\n{file_path}\nCould not open automatically: {e}")

def on_closing():
    conn.close()
    root.destroy()

root = tk.Tk()
root.title("💸 Professional Expense Tracker")
root.geometry("950x700")
root.config(bg="#121212")
root.resizable(False, False)


header = tk.Label(root, text="Professional Expense Tracker", font=("Arial", 18, "bold"), bg="#121212", fg="#00e676")
header.pack(pady=10)


frame = tk.Frame(root, bg="#121212")
frame.pack(pady=10)

tk.Label(frame, text="Item:", font=("Arial", 12), bg="#121212", fg="#ffffff").grid(row=0, column=0, padx=5, pady=5, sticky="e")
entry_item = tk.Entry(frame, font=("Arial", 12), width=20, bg="#1e1e1e", fg="#ffffff", insertbackground="white")
entry_item.grid(row=0, column=1, padx=5, pady=5)

tk.Label(frame, text="Amount:", font=("Arial", 12), bg="#121212", fg="#ffffff").grid(row=0, column=2, padx=5, pady=5, sticky="e")
entry_amount = tk.Entry(frame, font=("Arial", 12), width=15, bg="#1e1e1e", fg="#ffffff", insertbackground="white")
entry_amount.grid(row=0, column=3, padx=5, pady=5)

tk.Label(frame, text="Category:", font=("Arial", 12), bg="#121212", fg="#ffffff").grid(row=0, column=4, padx=5, pady=5, sticky="e")
category_var = tk.StringVar()
category_dropdown = ttk.Combobox(frame, textvariable=category_var, values=categories, state="readonly", width=15)
category_dropdown.grid(row=0, column=5, padx=5, pady=5)
category_dropdown.current(0)

btn_frame = tk.Frame(root, bg="#121212")
btn_frame.pack(pady=10)

tk.Button(btn_frame, text="Add", font=("Arial", 12), bg="#00e676", fg="#121212", width=12, command=add_expense).grid(row=0, column=0, padx=5)
tk.Button(btn_frame, text="Delete", font=("Arial", 12), bg="#ff3d00", fg="#ffffff", width=12, command=delete_expense).grid(row=0, column=1, padx=5)
tk.Button(btn_frame, text="Refresh", font=("Arial", 12), bg="#2979ff", fg="#ffffff", width=12, command=show_expenses).grid(row=0, column=2, padx=5)
tk.Button(btn_frame, text="Export Excel", font=("Arial", 12), bg="#ffa000", fg="#121212", width=15, command=export_and_open_excel).grid(row=0, column=3, padx=5)


listbox = tk.Listbox(root, font=("Courier", 12), width=70, height=12, bg="#1e1e1e", fg="#ffffff", selectbackground="#00b0ff")
listbox.pack(pady=10)

chart_frame = tk.Frame(root, bg="#121212")
chart_frame.pack(pady=10)

show_expenses()
root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()