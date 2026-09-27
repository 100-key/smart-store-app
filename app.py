import tkinter as tk
from tkinter import ttk, messagebox

from database import (
    add_customer,
    get_invoice_details,
    init_db,
    list_customers,
    list_invoices,
    list_products,
    save_invoice,
    search_customers,
)


class SmartStoreApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Store POS")
        self.root.geometry("1280x820")
        self.root.minsize(1100, 720)

        self.selected_customer_id = None
        self.selected_customer_name = ""
        self.basket = []

        self.style = ttk.Style(self.root)
        self.style.theme_use("clam")

        self.style.configure("TFrame", background="#f2f5f8")
        self.style.configure("TLabel", background="#f2f5f8", foreground="#1f2937")
        self.style.configure("TEntry", padding=4)
        self.style.configure("Primary.TButton", background="#1d4ed8", foreground="white", font=("Segoe UI", 10, "bold"))
        self.style.map("Primary.TButton", background=[("active", "#2563eb")])
        self.style.configure("Danger.TButton", background="#dc2626", foreground="white", font=("Segoe UI", 10, "bold"))
        self.style.map("Danger.TButton", background=[("active", "#ef4444")])
        self.style.configure("Success.TButton", background="#16a34a", foreground="white", font=("Segoe UI", 10, "bold"))
        self.style.map("Success.TButton", background=[("active", "#22c55e")])
        self.style.configure("Header.TLabel", background="#0f172a", foreground="white", font=("Segoe UI", 14, "bold"))
        self.style.configure("Card.TFrame", background="#ffffff")

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.sales_tab = ttk.Frame(self.notebook)
        self.customers_tab = ttk.Frame(self.notebook)
        self.invoices_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.sales_tab, text="Sales")
        self.notebook.add(self.customers_tab, text="Customers")
        self.notebook.add(self.invoices_tab, text="Invoices")

        self.build_sales_tab()
        self.build_customers_tab()
        self.build_invoices_tab()

        init_db()
        self.load_customers()
        self.load_products()
        self.load_invoices()

    def build_sales_tab(self):
        self.sales_tab.columnconfigure(0, weight=2)
        self.sales_tab.columnconfigure(1, weight=1)
        self.sales_tab.rowconfigure(0, weight=1)

        left_panel = ttk.Frame(self.sales_tab, padding=12)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        right_panel = ttk.Frame(self.sales_tab, padding=12)
        right_panel.grid(row=0, column=1, sticky="nsew")

        customer_card = ttk.LabelFrame(left_panel, text="Customer Search")
        customer_card.pack(fill="x", pady=(0, 12))

        search_row = ttk.Frame(customer_card)
        search_row.pack(fill="x", padx=10, pady=10)

        self.customer_search_var = tk.StringVar()
        ttk.Entry(search_row, textvariable=self.customer_search_var, width=30).pack(side="left", fill="x", expand=True)
        ttk.Button(search_row, text="Search", command=self.load_customers, style="Primary.TButton").pack(side="left", padx=(8, 0))

        self.customer_table = ttk.Treeview(customer_card, columns=("id", "name", "phone"), show="headings", height=8)
        self.customer_table.heading("id", text="ID")
        self.customer_table.heading("name", text="Name")
        self.customer_table.heading("phone", text="Phone")
        self.customer_table.column("id", width=60, anchor="center")
        self.customer_table.column("name", width=180)
        self.customer_table.column("phone", width=150)
        self.customer_table.pack(fill="x", padx=10, pady=(0, 10))
        self.customer_table.bind("<<TreeviewSelect>>", self.on_customer_select)

        selected_customer_frame = ttk.LabelFrame(left_panel, text="Selected Customer")
        selected_customer_frame.pack(fill="x", pady=(0, 12))

        self.selected_customer_label = ttk.Label(selected_customer_frame, text="No customer selected", font=("Segoe UI", 11, "bold"))
        self.selected_customer_label.pack(anchor="w", padx=10, pady=12)

        product_card = ttk.LabelFrame(left_panel, text="Products")
        product_card.pack(fill="both", expand=True)

        self.product_table = ttk.Treeview(product_card, columns=("id", "name", "category", "price", "stock"), show="headings", height=12)
        self.product_table.heading("id", text="ID")
        self.product_table.heading("name", text="Product")
        self.product_table.heading("category", text="Category")
        self.product_table.heading("price", text="Price")
        self.product_table.heading("stock", text="Stock")
        self.product_table.column("id", width=50, anchor="center")
        self.product_table.column("name", width=170)
        self.product_table.column("category", width=130)
        self.product_table.column("price", width=90, anchor="center")
        self.product_table.column("stock", width=80, anchor="center")
        self.product_table.pack(fill="both", expand=True, padx=10, pady=10)

        controls = ttk.Frame(product_card)
        controls.pack(fill="x", padx=10, pady=(0, 8))

        self.qty_var = tk.IntVar(value=1)
        ttk.Label(controls, text="Qty:").pack(side="left")
        ttk.Entry(controls, textvariable=self.qty_var, width=8).pack(side="left", padx=(6, 12))
        ttk.Button(controls, text="Add to Basket", command=self.add_to_basket, style="Primary.TButton").pack(side="left")

        basket_card = ttk.LabelFrame(right_panel, text="Basket")
        basket_card.pack(fill="both", expand=True)

        self.basket_table = ttk.Treeview(basket_card, columns=("product", "qty", "unit", "total"), show="headings", height=12)
        self.basket_table.heading("product", text="Product")
        self.basket_table.heading("qty", text="Qty")
        self.basket_table.heading("unit", text="Unit")
        self.basket_table.heading("total", text="Total")
        self.basket_table.column("product", width=170)
        self.basket_table.column("qty", width=60, anchor="center")
        self.basket_table.column("unit", width=90, anchor="center")
        self.basket_table.column("total", width=100, anchor="center")
        self.basket_table.pack(fill="both", expand=True, padx=10, pady=10)

        basket_controls = ttk.Frame(basket_card)
        basket_controls.pack(fill="x", padx=10, pady=(0, 10))
        ttk.Button(basket_controls, text="Remove Item", command=self.remove_basket_item, style="Danger.TButton").pack(side="left", padx=(0, 8))
        ttk.Button(basket_controls, text="Clear Basket", command=self.clear_basket, style="Danger.TButton").pack(side="left")

        totals_frame = ttk.LabelFrame(right_panel, text="Checkout")
        totals_frame.pack(fill="x", pady=(12, 0))

        ttk.Label(totals_frame, text="Total:").grid(row=0, column=0, padx=(12, 6), pady=8, sticky="w")
        self.total_label = ttk.Label(totals_frame, text="0.00 SR", font=("Segoe UI", 13, "bold"))
        self.total_label.grid(row=0, column=1, padx=(0, 12), pady=8, sticky="w")

        ttk.Label(totals_frame, text="Cash:").grid(row=1, column=0, padx=(12, 6), pady=(0, 8), sticky="w")
        self.cash_var = tk.StringVar(value="0")
        ttk.Entry(totals_frame, textvariable=self.cash_var, width=18).grid(row=1, column=1, padx=(0, 12), pady=(0, 8), sticky="w")

        ttk.Button(totals_frame, text="Create Invoice", command=self.create_invoice, style="Success.TButton").grid(row=2, column=0, columnspan=2, sticky="ew", padx=12, pady=(0, 12))

    def build_customers_tab(self):
        main = ttk.Frame(self.customers_tab, padding=14)
        main.pack(fill="both", expand=True)

        form_frame = ttk.LabelFrame(main, text="Add New Customer")
        form_frame.pack(fill="x", pady=(0, 12))

        fields = [
            ("Name", "customer_name"),
            ("Phone", "customer_phone"),
            ("Email", "customer_email"),
            ("Notes", "customer_notes"),
        ]

        self.customer_form_vars = {}
        for label, key in fields:
            row = ttk.Frame(form_frame)
            row.pack(fill="x", padx=10, pady=8)
            ttk.Label(row, text=label + ":").pack(side="left", padx=(0, 8))
            var = tk.StringVar()
            self.customer_form_vars[key] = var
            ttk.Entry(row, textvariable=var, width=40).pack(side="left", fill="x", expand=True)

        ttk.Button(form_frame, text="Save Customer", command=self.save_customer, style="Primary.TButton").pack(anchor="e", padx=10, pady=(0, 10))

        list_frame = ttk.LabelFrame(main, text="Customer List")
        list_frame.pack(fill="both", expand=True)

        self.customer_list_table = ttk.Treeview(list_frame, columns=("id", "name", "phone", "email", "notes"), show="headings", height=16)
        self.customer_list_table.heading("id", text="ID")
        self.customer_list_table.heading("name", text="Name")
        self.customer_list_table.heading("phone", text="Phone")
        self.customer_list_table.heading("email", text="Email")
        self.customer_list_table.heading("notes", text="Notes")
        self.customer_list_table.column("id", width=60, anchor="center")
        self.customer_list_table.column("name", width=180)
        self.customer_list_table.column("phone", width=140)
        self.customer_list_table.column("email", width=180)
        self.customer_list_table.column("notes", width=220)
        self.customer_list_table.pack(fill="both", expand=True, padx=10, pady=10)

    def build_invoices_tab(self):
        main = ttk.Frame(self.invoices_tab, padding=14)
        main.pack(fill="both", expand=True)

        table_frame = ttk.LabelFrame(main, text="Invoice History")
        table_frame.pack(fill="both", expand=True)

        self.invoice_table = ttk.Treeview(table_frame, columns=("id", "customer", "total", "cash", "change", "created_at"), show="headings", height=18)
        self.invoice_table.heading("id", text="Invoice ID")
        self.invoice_table.heading("customer", text="Customer")
        self.invoice_table.heading("total", text="Total")
        self.invoice_table.heading("cash", text="Cash")
        self.invoice_table.heading("change", text="Change")
        self.invoice_table.heading("created_at", text="Date")
        self.invoice_table.column("id", width=80, anchor="center")
        self.invoice_table.column("customer", width=200)
        self.invoice_table.column("total", width=120, anchor="center")
        self.invoice_table.column("cash", width=120, anchor="center")
        self.invoice_table.column("change", width=120, anchor="center")
        self.invoice_table.column("created_at", width=180)
        self.invoice_table.pack(fill="both", expand=True, padx=10, pady=10)
        self.invoice_table.bind("<<TreeviewSelect>>", self.on_invoice_select)

        actions = ttk.Frame(main)
        actions.pack(fill="x", pady=(12, 0))

        ttk.Button(actions, text="View Details", command=self.show_invoice_details, style="Primary.TButton").pack(side="left", padx=(0, 10))
        ttk.Button(actions, text="Delete Invoice", command=self.delete_selected_invoice, style="Danger.TButton").pack(side="left")

        self.invoice_detail_text = tk.Text(main, height=12, wrap="word", font=("Segoe UI", 10))
        self.invoice_detail_text.pack(fill="both", expand=True, pady=(12, 0))

    def load_customers(self):
        query = self.customer_search_var.get().strip()
        if query:
            rows = search_customers(query)
        else:
            rows = list_customers()

        for item in self.customer_table.get_children():
            self.customer_table.delete(item)

        for row in rows:
            self.customer_table.insert("", "end", values=(row["id"], row["name"], row["phone"]))

        for item in self.customer_list_table.get_children():
            self.customer_list_table.delete(item)

        for row in list_customers():
            self.customer_list_table.insert(
                "",
                "end",
                values=(row["id"], row["name"], row["phone"], row["email"], row["notes"]),
            )

    def load_products(self):
        for item in self.product_table.get_children():
            self.product_table.delete(item)

        for row in list_products():
            self.product_table.insert("", "end", values=(row["id"], row["name"], row["category"], row["price"], row["stock"]))

    def load_invoices(self):
        for item in self.invoice_table.get_children():
            self.invoice_table.delete(item)

        for row in list_invoices():
            customer_name = row["customer_name"] or row["customer_db_name"] or "Unknown"
            self.invoice_table.insert(
                "",
                "end",
                values=(row["id"], customer_name, f"{row['total']:.2f}", f"{row['cash']:.2f}", f"{row['change']:.2f}", row["created_at"]),
            )

    def on_customer_select(self, event):
        selected = self.customer_table.selection()
        if not selected:
            return
        values = self.customer_table.item(selected[0], "values")
        self.selected_customer_id = values[0]
        self.selected_customer_name = values[1]
        self.selected_customer_label.config(text=f"{values[1]} | {values[2]}")

    def add_to_basket(self):
        if self.selected_customer_id is None:
            messagebox.showwarning("Warning", "Please select a customer first.")
            return

        selected = self.product_table.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a product.")
            return

        qty = self.qty_var.get()
        if qty <= 0:
            messagebox.showwarning("Warning", "Quantity must be greater than zero.")
            return

        product_values = self.product_table.item(selected[0], "values")
        product_id = int(product_values[0])
        product_name = product_values[1]
        unit_price = float(product_values[3])
        stock = int(product_values[4])

        if qty > stock:
            messagebox.showwarning("Warning", f"Only {stock} items available for {product_name}.")
            return

        for item in self.basket:
            if item["product_id"] == product_id:
                new_qty = item["quantity"] + qty
                if new_qty > stock:
                    messagebox.showwarning("Warning", f"Total quantity exceeds available stock: {stock}.")
                    return
                item["quantity"] = new_qty
                item["total"] = new_qty * unit_price
                self.refresh_basket()
                self.update_totals()
                return

        self.basket.append({
            "product_id": product_id,
            "product_name": product_name,
            "quantity": qty,
            "unit_price": unit_price,
            "total": qty * unit_price,
        })
        self.refresh_basket()
        self.update_totals()

    def refresh_basket(self):
        for item in self.basket_table.get_children():
            self.basket_table.delete(item)

        for item in self.basket:
            self.basket_table.insert(
                "",
                "end",
                values=(item["product_name"], item["quantity"], f"{item['unit_price']:.2f}", f"{item['total']:.2f}"),
            )

    def remove_basket_item(self):
        selected = self.basket_table.selection()
        if not selected:
            return

        item_index = self.basket_table.index(selected[0])
        del self.basket[item_index]
        self.refresh_basket()
        self.update_totals()

    def clear_basket(self):
        self.basket = []
        self.refresh_basket()
        self.update_totals()

    def update_totals(self):
        total = sum(item["total"] for item in self.basket)
        self.total_label.config(text=f"{total:.2f} SR")

    def create_invoice(self):
        if self.selected_customer_id is None:
            messagebox.showwarning("Warning", "Please select a customer before creating an invoice.")
            return

        if not self.basket:
            messagebox.showwarning("Warning", "Basket is empty.")
            return

        try:
            cash = float(self.cash_var.get())
        except ValueError:
            messagebox.showwarning("Warning", "Cash value is invalid.")
            return

        total = sum(item["total"] for item in self.basket)
        if cash < total:
            messagebox.showwarning("Warning", "Cash value is less than the total amount.")
            return

        invoice_id = save_invoice(self.selected_customer_id, self.selected_customer_name, self.basket, cash)
        if invoice_id is None:
            messagebox.showerror("Error", "Unable to create invoice.")
            return

        self.clear_basket()
        self.cash_var.set("0")
        self.load_invoices()
        self.load_products()
        messagebox.showinfo("Success", f"Invoice created successfully with ID: {invoice_id}")

    def save_customer(self):
        name = self.customer_form_vars["customer_name"].get().strip()
        phone = self.customer_form_vars["customer_phone"].get().strip()
        email = self.customer_form_vars["customer_email"].get().strip()
        notes = self.customer_form_vars["customer_notes"].get().strip()

        if not name:
            messagebox.showwarning("Warning", "Customer name is required.")
            return

        add_customer(name, phone, email, notes)
        self.clear_customer_form()
        self.load_customers()
        messagebox.showinfo("Success", "Customer saved successfully.")

    def clear_customer_form(self):
        for key in self.customer_form_vars:
            self.customer_form_vars[key].set("")

    def on_invoice_select(self, event):
        selected = self.invoice_table.selection()
        if selected:
            self.selected_invoice_id = self.invoice_table.item(selected[0], "values")[0]

    def show_invoice_details(self):
        selected = self.invoice_table.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an invoice first.")
            return

        invoice_id = int(self.invoice_table.item(selected[0], "values")[0])
        invoice, items = get_invoice_details(invoice_id)

        if not invoice:
            messagebox.showwarning("Warning", "Invoice not found.")
            return

        text = [
            "Smart Store Invoice\n",
            "===========================\n",
            f"Invoice ID: {invoice['id']}\n",
            f"Customer: {invoice['customer_name'] or invoice['customer_db_name'] or 'Unknown'}\n",
            f"Date: {invoice['created_at']}\n",
            "\nItems:\n",
        ]

        for item in items:
            text.append(f"- {item['product_name']} | Qty: {item['quantity']} | Unit: {item['unit_price']:.2f} | Total: {item['total']:.2f}\n")

        text.append("\n")
        text.append(f"Total: {invoice['total']:.2f}\n")
        text.append(f"Cash: {invoice['cash']:.2f}\n")
        text.append(f"Change: {invoice['change']:.2f}\n")

        self.invoice_detail_text.delete("1.0", tk.END)
        self.invoice_detail_text.insert(tk.END, "".join(text))

    def delete_selected_invoice(self):
        selected = self.invoice_table.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an invoice to delete.")
            return

        invoice_id = int(self.invoice_table.item(selected[0], "values")[0])
        confirm = messagebox.askyesno("Confirm", f"Delete invoice #{invoice_id}?")
        if not confirm:
            return

        from database import delete_invoice
        delete_invoice(invoice_id)
        self.load_invoices()
        self.invoice_detail_text.delete("1.0", tk.END)
        messagebox.showinfo("Success", "Invoice deleted successfully.")


def main():
    root = tk.Tk()
    app = SmartStoreApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()






















































































































































































































































































































































































































































































































































































































































































































