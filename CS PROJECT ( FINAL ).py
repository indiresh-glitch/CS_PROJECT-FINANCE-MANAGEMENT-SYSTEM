import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from datetime import datetime
import matplotlib.pyplot as plt
from collections import defaultdict

# ------------------ Database setup ------------------
try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="<YOUR_PASS>",
        autocommit=True
    )
    cursor = conn.cursor()
    print("Database connection successful!")
except mysql.connector.Error as e:
    print(f"Database connection failed: {e}")
    exit()

# Create database
cursor.execute("CREATE DATABASE IF NOT EXISTS finance_manager")
cursor.execute("USE finance_manager")

# Create or update tables
cursor.execute("""
    CREATE TABLE IF NOT EXISTS transaction_desc (
        transaction_id INT AUTO_INCREMENT PRIMARY KEY,
        txn_date DATETIME,
        category VARCHAR(50),
        description VARCHAR(255),
        txn_type VARCHAR(20),
        payment_type VARCHAR(50),
        gross_amt FLOAT,
        tax VARCHAR(20),
        net_amt FLOAT
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS transaction_summary (
        summary_id INT AUTO_INCREMENT PRIMARY KEY,
        transaction_id INT,
        category VARCHAR(50),
        txn_type VARCHAR(20),
        payment_type VARCHAR(50),
        gross_amt FLOAT,
        net_amt FLOAT,
        FOREIGN KEY (transaction_id) REFERENCES transaction_desc(transaction_id) ON DELETE CASCADE
    )
""")

# New table: trans_classification
cursor.execute("""
    CREATE TABLE IF NOT EXISTS trans_classification (
        class_id INT AUTO_INCREMENT PRIMARY KEY,
        transaction_id INT,
        category VARCHAR(50),
        description VARCHAR(255),
        txn_type VARCHAR(20),
        payment_type VARCHAR(50),
        FOREIGN KEY (transaction_id) REFERENCES transaction_desc(transaction_id) ON DELETE CASCADE
    )
""")

# New table: net_trans
cursor.execute("""
    CREATE TABLE IF NOT EXISTS net_trans (
        net_id INT AUTO_INCREMENT PRIMARY KEY,
        transaction_id INT,
        txn_type VARCHAR(20),
        payment_type VARCHAR(50),
        net_amt FLOAT,
        FOREIGN KEY (transaction_id) REFERENCES transaction_desc(transaction_id) ON DELETE CASCADE
    )
""")

print("All tables ready!")

# ------------------ Helper & Validation ------------------
def validate_tax_input(tax_value):
    """Validates that tax is either numeric or one of NIL/nil/Nil."""
    tax_value = tax_value.strip()
    if tax_value in ["NIL", "nil", "Nil"]:
        return True
    try:
        float(tax_value)
        return True
    except ValueError:
        return False


def calculate_net_amount(txn_type, gross_amt, tax_value):
    """Calculates net amount based on transaction type and tax."""
    tax_value = tax_value.strip()
    if tax_value in ["NIL", "nil", "Nil", "0", "0.0"]:
        return gross_amt

    try:
        tax_percent = float(tax_value)
    except ValueError:
        tax_percent = 0

    if txn_type == "Income":
        # Tax is reduced from gross
        return gross_amt - (gross_amt * tax_percent / 100)
    elif txn_type == "Expense":
        # Tax is added to gross
        return gross_amt + (gross_amt * tax_percent / 100)
    elif txn_type == "Savings":
        # Gross and net remain same
        return gross_amt
    else:
        return gross_amt


# ------------------ Functions ------------------
def add_transaction():
    txn_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    txn_type = type_var.get()
    category = category_entry.get()
    description = description_entry.get()
    payment_type = payment_var.get()
    gross_amt = gross_entry.get()
    tax = tax_entry.get().strip()

    if not category or not gross_amt:
        messagebox.showerror("Input Error", "Category and Gross Amount are required.")
        return

    try:
        gross_amt = float(gross_amt)
    except ValueError:
        messagebox.showerror("Input Error", "Gross Amount must be a number.")
        return

    if not validate_tax_input(tax):
        messagebox.showerror("Input Error", "Tax must be a number or one of: NIL, nil, Nil.")
        return

    net_amt = calculate_net_amount(txn_type, gross_amt, tax)

    try:
        # Insert into main transaction table
        cursor.execute("""
            INSERT INTO transaction_desc (txn_date, category, description, txn_type, payment_type, gross_amt, tax, net_amt)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (txn_date, category, description, txn_type, payment_type, gross_amt, tax, net_amt))
        conn.commit()

        transaction_id = cursor.lastrowid

        # Insert into summary table
        cursor.execute("""
            INSERT INTO transaction_summary (transaction_id, category, txn_type, payment_type, gross_amt, net_amt)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (transaction_id, category, txn_type, payment_type, gross_amt, net_amt))

        # Insert into classification table
        cursor.execute("""
            INSERT INTO trans_classification (transaction_id, category, description, txn_type, payment_type)
            VALUES (%s, %s, %s, %s, %s)
        """, (transaction_id, category, description, txn_type, payment_type))

        # Insert into net transaction table
        cursor.execute("""
            INSERT INTO net_trans (transaction_id, txn_type, payment_type, net_amt)
            VALUES (%s, %s, %s, %s)
        """, (transaction_id, txn_type, payment_type, net_amt))

        conn.commit()
        messagebox.showinfo("Success", f"{txn_type} added successfully!")

    except mysql.connector.Error as e:
        print(f"Error inserting transaction: {e}")
        messagebox.showerror("Database Error", "Failed to add transaction.")
        return

    category_entry.delete(0, tk.END)
    gross_entry.delete(0, tk.END)
    description_entry.delete(0, tk.END)
    tax_entry.delete(0, tk.END)
    payment_var.set("Cash")
    view_transactions()


def view_transactions():
    for row in transaction_table.get_children():
        transaction_table.delete(row)

    try:
        cursor.execute("""
            SELECT transaction_id, txn_date, category, description, txn_type, payment_type, gross_amt, tax, net_amt
            FROM transaction_desc
        """)
        rows = cursor.fetchall()
        for row in rows:
            transaction_table.insert('', tk.END, values=row)
    except mysql.connector.Error as e:
        print(f"Error fetching transactions: {e}")


def show_expense_chart():
    categories = defaultdict(float)
    try:
        cursor.execute("SELECT category, gross_amt FROM transaction_desc WHERE txn_type='Expense'")
        rows = cursor.fetchall()

        for row in rows:
            categories[row[0]] += row[1]

        if not categories:
            messagebox.showinfo("No Data", "No expenses to show.")
            return

        plt.figure(figsize=(6, 6))
        plt.pie(categories.values(), labels=categories.keys(), autopct='%1.1f%%', startangle=140)
        plt.title('Expense Distribution by Category')
        plt.axis('equal')
        plt.tight_layout()
        plt.show()
    except mysql.connector.Error as e:
        print(f"Error generating chart: {e}")


def show_income_expense_savings_chart():
    data = {"Income": 0, "Expense": 0, "Savings": 0}
    try:
        cursor.execute("SELECT txn_type, SUM(gross_amt) FROM transaction_desc GROUP BY txn_type")
        rows = cursor.fetchall()

        for row in rows:
            if row[0] in data:
                data[row[0]] = row[1]

        if all(value == 0 for value in data.values()):
            messagebox.showinfo("No Data", "No transactions to show.")
            return

        plt.figure(figsize=(6, 6))
        plt.pie(data.values(), labels=data.keys(), autopct='%1.1f%%', startangle=140)
        plt.title('Income vs Expense vs Savings Distribution')
        plt.axis('equal')
        plt.tight_layout()
        plt.show()
    except mysql.connector.Error as e:
        print(f"Error generating chart: {e}")


# ------------------ GUI ------------------
def launch_gui():
    global type_var, category_entry, description_entry, gross_entry, payment_var, transaction_table, tax_entry

    root = tk.Tk()
    root.title("Personal Finance Manager")
    root.geometry("1000x700")

    entry_frame = tk.LabelFrame(root, text="Add Transaction", padx=10, pady=10)
    entry_frame.pack(fill="x", padx=10, pady=10)

    type_var = tk.StringVar(value="Income")
    tk.Label(entry_frame, text="Transaction Type:").grid(row=0, column=0, padx=5, pady=5)
    tk.Radiobutton(entry_frame, text="Income", variable=type_var, value="Income").grid(row=0, column=1)
    tk.Radiobutton(entry_frame, text="Expense", variable=type_var, value="Expense").grid(row=0, column=2)
    tk.Radiobutton(entry_frame, text="Savings", variable=type_var, value="Savings").grid(row=0, column=3)

    tk.Label(entry_frame, text="Category:").grid(row=1, column=0, padx=5, pady=5)
    category_entry = tk.Entry(entry_frame)
    category_entry.grid(row=1, column=1, columnspan=3, sticky="we")

    tk.Label(entry_frame, text="Description:").grid(row=2, column=0, padx=5, pady=5)
    description_entry = tk.Entry(entry_frame)
    description_entry.grid(row=2, column=1, columnspan=3, sticky="we")

    tk.Label(entry_frame, text="Gross Amount:").grid(row=3, column=0, padx=5, pady=5)
    gross_entry = tk.Entry(entry_frame)
    gross_entry.grid(row=3, column=1, columnspan=3, sticky="we")

    tk.Label(entry_frame, text="Tax (% or NIL):").grid(row=4, column=0, padx=5, pady=5)
    tax_entry = tk.Entry(entry_frame)
    tax_entry.grid(row=4, column=1, columnspan=3, sticky="we")

    tk.Label(entry_frame, text="Payment Type:").grid(row=5, column=0, padx=5, pady=5)
    payment_var = tk.StringVar(value="Cash")
    payment_dropdown = ttk.Combobox(entry_frame, textvariable=payment_var,
                                    values=["Cash", "Credit Card", "Debit Card", "Others"], state="readonly")
    payment_dropdown.grid(row=5, column=1, columnspan=3, sticky="we")

    add_btn = tk.Button(entry_frame, text="Add Transaction", command=add_transaction)
    add_btn.grid(row=6, column=0, columnspan=4, pady=10)

    chart_btn = tk.Button(entry_frame, text="Show Expense Chart", command=show_expense_chart)
    chart_btn.grid(row=7, column=0, columnspan=4, pady=5)

    income_expense_chart_btn = tk.Button(entry_frame, text="Show Income vs Expense vs Savings",
                                         command=show_income_expense_savings_chart)
    income_expense_chart_btn.grid(row=8, column=0, columnspan=4, pady=5)

    history_frame = tk.LabelFrame(root, text="Transaction History", padx=10, pady=10)
    history_frame.pack(fill="both", expand=True, padx=10, pady=10)

    columns = ("ID", "Date", "Category", "Description", "Type", "Payment", "Gross Amount", "Tax", "Net Amount")
    transaction_table = ttk.Treeview(history_frame, columns=columns, show='headings')
    for col in columns:
        transaction_table.heading(col, text=col)
        transaction_table.column(col, anchor="center")
    transaction_table.pack(fill="both", expand=True)

    view_transactions()
    root.mainloop()


# ------------------ Menu-driven CLI ------------------
while True:
    print("\n========================= Finance Manager Menu =========================")
    print("1. Show tables in Finance Manager")
    print("2. View table contents")
    print("3. Continue to Add Transactions (GUI)")
    print("4. Delete a record from all tables")
    print("5. Close connection & Exit")
    choice = input("Enter your choice: ")

    if choice == "1":
        cursor.execute("SHOW TABLES")
        print("Tables:", cursor.fetchall())

    elif choice == "2":
        print("Choose table to view:")
        print("1. transaction_summary")
        print("2. transaction_desc")
        print("3. trans_classification")
        print("4. net_trans")
        sub_choice = input("Enter choice: ")

        if sub_choice == "1":
            cursor.execute("SELECT * FROM transaction_summary")
        elif sub_choice == "2":
            cursor.execute("SELECT * FROM transaction_desc")
        elif sub_choice == "3":
            cursor.execute("SELECT * FROM trans_classification")
        elif sub_choice == "4":
            cursor.execute("SELECT * FROM net_trans")
        else:
            print("Invalid choice")
            continue

        rows = cursor.fetchall()
        for row in rows:
            print(row)

    elif choice == "3":
        launch_gui()

    elif choice == "4":
        txn_id = input("Enter Transaction ID to delete: ")
        cursor.execute("SELECT * FROM transaction_desc WHERE transaction_id = %s", (txn_id,))
        record = cursor.fetchone()
        if record:
            print("Deleting Record:", record)
            cursor.execute("DELETE FROM transaction_desc WHERE transaction_id = %s", (txn_id,))
            conn.commit()
            print("Record deleted successfully from all linked tables (CASCADE).")
        else:
            print("No record found with that Transaction ID.")

    elif choice == "5":
        conn.close()
        print("Connection closed. Exiting...")
        break

    else:
        print("Invalid input, try again.")
