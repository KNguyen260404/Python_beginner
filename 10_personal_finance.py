import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import datetime
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Database class for SQLite operations
class Database:
    def __init__(self, db_file):
        import sqlite3
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()
    
    def execute_query(self, query, params=()):
        self.cursor.execute(query, params)
        self.connection.commit()
        return self.cursor.fetchall()
    
    def close(self):
        self.connection.close()

# Category class to manage income and expense categories
class Category:
    INCOME_CATEGORIES = [
        "Salary",
        "Business",
        "Investments",
        "Gifts",
        "Other Income"
    ]
    
    EXPENSE_CATEGORIES = [
        "Food",
        "Housing",
        "Transportation",
        "Utilities",
        "Insurance",
        "Healthcare",
        "Entertainment",
        "Other Expenses"
    ]

# Main application class
class PersonalFinanceApp:
    def __init__(self):
        # Initialize database
        self.db = Database("finance_manager.db")
        
        # Initialize main window
        self.root = tk.Tk()
        self.root.title("💰 Personal Finance Manager")
        self.root.geometry("900x700")
        
        # Define colors
        self.colors = {
            'primary': '#007bff',
            'success': '#28a745',
            'danger': '#dc3545',
            'warning': '#ffc107',
            'info': '#17a2b8',
            'light': '#f8f9fa',
            'dark': '#343a40',
            'muted': '#6c757d',
            'white': '#ffffff',
            'black': '#000000'
        }
        
        # Configure grid layout
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=4)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=3)
        
        # Title label
        self.title_label = tk.Label(self.root, text="💰 Personal Finance Manager", 
                                    font=('Arial', 24, 'bold'), fg=self.colors['primary'])
        self.title_label.grid(row=0, column=0, columnspan=2, pady=10)
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=1, column=0, columnspan=2, sticky="nsew")
        
        # Create tabs
        self.create_dashboard_tab()
        self.create_transactions_tab()
        self.create_budget_tab()
        self.create_goals_tab()
        self.create_reports_tab()
        
        # Bind events
        self.bind_events()
        
        # Initialize data
        self.refresh_data()
    
    def create_dashboard_tab(self):
        # Dashboard tab
        self.dashboard_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.dashboard_tab, text="Dashboard")
        
        # Dashboard content
        tk.Label(self.dashboard_tab, text="Dashboard", font=('Arial', 18, 'bold')).pack(pady=10)
        
        # Income, Expense, Balance labels
        self.income_label = tk.Label(self.dashboard_tab, text="0 VNĐ", font=('Arial', 16))
        self.income_label.pack(pady=5)
        
        self.expense_label = tk.Label(self.dashboard_tab, text="0 VNĐ", font=('Arial', 16))
        self.expense_label.pack(pady=5)
        
        self.balance_label = tk.Label(self.dashboard_tab, text="0 VNĐ", font=('Arial', 16))
        self.balance_label.pack(pady=5)
        
        # Recent transactions treeview
        self.recent_tree = ttk.Treeview(self.dashboard_tab, columns=("date", "type", "category", "amount", "description"), show="headings")
        self.recent_tree.heading("date", text="Date")
        self.recent_tree.heading("type", text="Type")
        self.recent_tree.heading("category", text="Category")
        self.recent_tree.heading("amount", text="Amount")
        self.recent_tree.heading("description", text="Description")
        self.recent_tree.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Style treeview
        self.style_treeview(self.recent_tree)
    
    def create_transactions_tab(self):
        # Transactions tab
        self.transactions_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.transactions_tab, text="Transactions")
        
        # Transactions content
        tk.Label(self.transactions_tab, text="Transactions", font=('Arial', 18, 'bold')).pack(pady=10)
        
        # Filter frame
        filter_frame = tk.Frame(self.transactions_tab)
        filter_frame.pack(pady=10)
        
        tk.Label(filter_frame, text="Filter by month:").grid(row=0, column=0, padx=5)
        self.filter_month_var = tk.StringVar()
        self.filter_month_entry = ttk.Combobox(filter_frame, textvariable=self.filter_month_var, width=10)
        self.filter_month_entry['values'] = [datetime.date.today().strftime('%Y-%m')]
        self.filter_month_entry.grid(row=0, column=1, padx=5)
        
        filter_button = tk.Button(filter_frame, text="Filter", command=self.refresh_transactions)
        filter_button.grid(row=0, column=2, padx=5)
        
        # Transactions treeview
        self.trans_tree = ttk.Treeview(self.transactions_tab, columns=("id", "date", "type", "category", "amount", "description"), show="headings")
        self.trans_tree.heading("id", text="ID")
        self.trans_tree.heading("date", text="Date")
        self.trans_tree.heading("type", text="Type")
        self.trans_tree.heading("category", text="Category")
        self.trans_tree.heading("amount", text="Amount")
        self.trans_tree.heading("description", text="Description")
        self.trans_tree.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Style treeview
        self.style_treeview(self.trans_tree)
    
    def create_budget_tab(self):
        # Budget tab
        self.budget_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.budget_tab, text="Budget")
        
        # Budget content
        tk.Label(self.budget_tab, text="Budget", font=('Arial', 18, 'bold')).pack(pady=10)
        
        # Budget form
        form_frame = tk.Frame(self.budget_tab)
        form_frame.pack(pady=10)
        
        tk.Label(form_frame, text="Category:").grid(row=0, column=0, padx=5)
        self.budget_category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(form_frame, textvariable=self.budget_category_var)
        self.category_combo['values'] = Category.EXPENSE_CATEGORIES
        self.category_combo.grid(row=0, column=1, padx=5)
        
        tk.Label(form_frame, text="Month:").grid(row=1, column=0, padx=5)
        self.budget_month_var = tk.StringVar()
        self.budget_month_entry = ttk.Combobox(form_frame, textvariable=self.budget_month_var, width=10)
        self.budget_month_entry['values'] = [datetime.date.today().strftime('%Y-%m')]
        self.budget_month_entry.grid(row=1, column=1, padx=5)
        
        tk.Label(form_frame, text="Limit:").grid(row=2, column=0, padx=5)
        self.budget_limit_var = tk.StringVar()
        self.budget_limit_entry = ttk.Entry(form_frame, textvariable=self.budget_limit_var)
        self.budget_limit_entry.grid(row=2, column=1, padx=5)
        
        set_budget_button = tk.Button(form_frame, text="Set Budget", command=self.set_budget)
        set_budget_button.grid(row=3, column=0, columnspan=2, pady=10)
        
        # Budget treeview
        self.budget_tree = ttk.Treeview(self.budget_tab, columns=("category", "limit", "spent", "remaining", "status"), show="headings")
        self.budget_tree.heading("category", text="Category")
        self.budget_tree.heading("limit", text="Monthly Limit")
        self.budget_tree.heading("spent", text="Spent")
        self.budget_tree.heading("remaining", text="Remaining")
        self.budget_tree.heading("status", text="Status")
        self.budget_tree.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Style treeview
        self.style_treeview(self.budget_tree)
    
    def create_goals_tab(self):
        # Goals tab
        self.goals_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.goals_tab, text="Goals")
        
        # Goals content
        tk.Label(self.goals_tab, text="Goals", font=('Arial', 18, 'bold')).pack(pady=10)
        
        # Goals form
        goals_form_frame = tk.Frame(self.goals_tab)
        goals_form_frame.pack(pady=10)
        
        tk.Label(goals_form_frame, text="Goal Name:").grid(row=0, column=0, padx=5)
        self.goal_name_var = tk.StringVar()
        self.goal_name_entry = ttk.Entry(goals_form_frame, textvariable=self.goal_name_var)
        self.goal_name_entry.grid(row=0, column=1, padx=5)
        
        tk.Label(goals_form_frame, text="Target Amount:").grid(row=1, column=0, padx=5)
        self.goal_target_var = tk.StringVar()
        self.goal_target_entry = ttk.Entry(goals_form_frame, textvariable=self.goal_target_var)
        self.goal_target_entry.grid(row=1, column=1, padx=5)
        
        tk.Label(goals_form_frame, text="Target Date:").grid(row=2, column=0, padx=5)
        self.goal_date_var = tk.StringVar()
        self.goal_date_entry = ttk.Entry(goals_form_frame, textvariable=self.goal_date_var)
        self.goal_date_entry.grid(row=2, column=1, padx=5)
        
        add_goal_button = tk.Button(goals_form_frame, text="Add Goal", command=self.add_goal)
        add_goal_button.grid(row=3, column=0, columnspan=2, pady=10)
        
        # Goals treeview
        self.goals_tree = ttk.Treeview(self.goals_tab, columns=("name", "target", "current", "progress", "target_date", "status"), show="headings")
        self.goals_tree.heading("name", text="Goal Name")
        self.goals_tree.heading("target", text="Target Amount")
        self.goals_tree.heading("current", text="Current Amount")
        self.goals_tree.heading("progress", text="Progress")
        self.goals_tree.heading("target_date", text="Target Date")
        self.goals_tree.heading("status", text="Status")
        self.goals_tree.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Style treeview
        self.style_treeview(self.goals_tree)
    
    def create_reports_tab(self):
        # Reports tab
        self.reports_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.reports_tab, text="Reports")
        
        # Reports content
        tk.Label(self.reports_tab, text="Reports", font=('Arial', 18, 'bold')).pack(pady=10)
        
        # Report period frame
        report_period_frame = tk.Frame(self.reports_tab)
        report_period_frame.pack(pady=10)
        
        tk.Label(report_period_frame, text="Report period:").grid(row=0, column=0, padx=5)
        self.report_period_var = tk.StringVar()
        self.report_period_entry = ttk.Combobox(report_period_frame, textvariable=self.report_period_var, width=15)
        self.report_period_entry['values'] = ["This Month", "Last Month", "This Year"]
        self.report_period_entry.grid(row=0, column=1, padx=5)
        
        generate_report_button = tk.Button(report_period_frame, text="Generate Report", command=self.generate_report)
        generate_report_button.grid(row=0, column=2, padx=5)
        
        # Chart frame
        self.chart_frame = tk.Frame(self.reports_tab)
        self.chart_frame.pack(fill=tk.BOTH, expand=True, pady=10)
    
    def style_treeview(self, treeview):
        # Style configuration for treeviews
        style = ttk.Style()
        style.configure("Treeview",
                        background=self.colors['light'],
                        foreground=self.colors['black'],
                        rowheight=25,
                        fieldbackground=self.colors['white'])
        style.configure("Treeview.Heading",
                        background=self.colors['primary'],
                        foreground=self.colors['white'],
                        font=('Arial', 10, 'bold'))
        style.map("Treeview.Heading",
                  background=[('active', self.colors['primary'])])
        
        treeview.tag_configure('oddrow', background=self.colors['light'])
        treeview.tag_configure('evenrow', background=self.colors['white'])
    
    def bind_events(self):
        # Bind events to update UI components
        self.type_var = tk.StringVar()
        self.category_var = tk.StringVar()
        self.amount_var = tk.StringVar()
        self.description_var = tk.StringVar()
        self.date_var = tk.StringVar(value=datetime.date.today().strftime('%Y-%m-%d'))
        
        # Transaction type radio buttons
        tk.Radiobutton(self.transactions_tab, text="Income", variable=self.type_var, value="income", command=self.on_type_change).pack(anchor=tk.W, padx=10)
        tk.Radiobutton(self.transactions_tab, text="Expense", variable=self.type_var, value="expense", command=self.on_type_change).pack(anchor=tk.W, padx=10)
        
        # Date entry
        tk.Label(self.transactions_tab, text="Date:").pack(anchor=tk.W, padx=10)
        tk.Entry(self.transactions_tab, textvariable=self.date_var).pack(fill=tk.X, padx=10, pady=5)
        
        # Category combobox
        tk.Label(self.transactions_tab, text="Category:").pack(anchor=tk.W, padx=10)
        self.category_combo = ttk.Combobox(self.transactions_tab, textvariable=self.category_var)
        self.category_combo.pack(fill=tk.X, padx=10, pady=5)
        
        # Amount entry
        tk.Label(self.transactions_tab, text="Amount:").pack(anchor=tk.W, padx=10)
        tk.Entry(self.transactions_tab, textvariable=self.amount_var).pack(fill=tk.X, padx=10, pady=5)
        
        # Description entry
        tk.Label(self.transactions_tab, text="Description:").pack(anchor=tk.W, padx=10)
        tk.Entry(self.transactions_tab, textvariable=self.description_var).pack(fill=tk.X, padx=10, pady=5)
        
        # Add transaction button
        add_button = tk.Button(self.transactions_tab, text="Add Transaction", command=self.add_transaction)
        add_button.pack(pady=10)
        
        # Delete transaction button
        delete_button = tk.Button(self.transactions_tab, text="Delete Transaction", command=self.delete_transaction)
        delete_button.pack(pady=10)
    
    def on_type_change(self, event=None):
        trans_type = self.type_var.get()
        if trans_type == 'income':
            self.category_combo['values'] = Category.INCOME_CATEGORIES
        elif trans_type == 'expense':
            self.category_combo['values'] = Category.EXPENSE_CATEGORIES
        self.category_var.set('')
    
    def add_transaction(self):
        try:
            date = self.date_var.get()
            trans_type = self.type_var.get()
            category = self.category_var.get()
            amount = float(self.amount_var.get())
            description = self.description_var.get()
            
            if not all([date, trans_type, category, amount]):
                messagebox.showerror("Error", "Please fill all required fields!")
                return
            
            # Validate date format
            datetime.datetime.strptime(date, '%Y-%m-%d')
            
            # Insert transaction
            query = '''
                INSERT INTO transactions (date, type, category, amount, description)
                VALUES (?, ?, ?, ?, ?)
            '''
            self.db.execute_query(query, (date, trans_type, category, amount, description))
            
            # Clear form
            self.date_var.set(datetime.date.today().strftime('%Y-%m-%d'))
            self.type_var.set('')
            self.category_var.set('')
            self.amount_var.set('')
            self.description_var.set('')
            
            messagebox.showinfo("Success", "Transaction added successfully!")
            self.refresh_data()
            
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add transaction: {str(e)}")
    
    def delete_transaction(self):
        selected = self.trans_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a transaction to delete!")
            return
        
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this transaction?"):
            try:
                item = self.trans_tree.item(selected[0])
                trans_id = item['values'][0]
                
                query = "DELETE FROM transactions WHERE id = ?"
                self.db.execute_query(query, (trans_id,))
                
                messagebox.showinfo("Success", "Transaction deleted successfully!")
                self.refresh_data()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete transaction: {str(e)}")
    
    def set_budget(self):
        try:
            category = self.budget_category_var.get()
            month_str = self.budget_month_var.get()
            limit = float(self.budget_limit_var.get())
            
            if not all([category, month_str, limit]):
                messagebox.showerror("Error", "Please fill all fields!")
                return
            
            year, month = map(int, month_str.split('-'))
            
            # Insert or update budget
            query = '''
                INSERT OR REPLACE INTO budgets (category, monthly_limit, year, month)
                VALUES (?, ?, ?, ?)
            '''
            self.db.execute_query(query, (category, limit, year, month))
            
            messagebox.showinfo("Success", "Budget set successfully!")
            self.refresh_budget()
            
        except ValueError:
            messagebox.showerror("Error", "Invalid input format!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to set budget: {str(e)}")
    
    def add_goal(self):
        try:
            name = self.goal_name_var.get()
            target = float(self.goal_target_var.get())
            target_date = self.goal_date_var.get()
            
            if not all([name, target]):
                messagebox.showerror("Error", "Please fill required fields!")
                return
            
            if target_date:
                datetime.datetime.strptime(target_date, '%Y-%m-%d')
            
            query = '''
                INSERT INTO goals (name, target_amount, target_date)
                VALUES (?, ?, ?)
            '''
            self.db.execute_query(query, (name, target, target_date or None))
            
            # Clear form
            self.goal_name_var.set('')
            self.goal_target_var.set('')
            self.goal_date_var.set('')
            
            messagebox.showinfo("Success", "Goal added successfully!")
            self.refresh_goals()
            
        except ValueError:
            messagebox.showerror("Error", "Invalid input format!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add goal: {str(e)}")
    
    def update_goal_progress(self):
        selected = self.goals_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a goal!")
            return
        
        try:
            amount = float(self.goal_add_var.get())
            if amount <= 0:
                messagebox.showerror("Error", "Amount must be positive!")
                return
            
            item = self.goals_tree.item(selected[0])
            goal_name = item['values'][0]
            
            # Update current amount
            query = '''
                UPDATE goals 
                SET current_amount = current_amount + ?
                WHERE name = ?
            '''
            self.db.execute_query(query, (amount, goal_name))
            
            self.goal_add_var.set('')
            messagebox.showinfo("Success", f"Added {amount:,.0f} VNĐ to goal!")
            self.refresh_goals()
            
        except ValueError:
            messagebox.showerror("Error", "Invalid amount!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update goal: {str(e)}")
    
    def refresh_data(self):
        self.refresh_dashboard()
        self.refresh_transactions()
        self.refresh_budget()
        self.refresh_goals()
    
    def refresh_dashboard(self):
        # Get current month data
        current_month = datetime.date.today().strftime('%Y-%m')
        
        # Total income this month
        income_query = '''
            SELECT COALESCE(SUM(amount), 0) FROM transactions 
            WHERE type = 'income' AND strftime('%Y-%m', date) = ?
        '''
        income = self.db.execute_query(income_query, (current_month,))[0][0]
        
        # Total expenses this month
        expense_query = '''
            SELECT COALESCE(SUM(amount), 0) FROM transactions 
            WHERE type = 'expense' AND strftime('%Y-%m', date) = ?
        '''
        expenses = self.db.execute_query(expense_query, (current_month,))[0][0]
        
        # Update labels
        self.income_label.config(text=f"{income:,.0f} VNĐ")
        self.expense_label.config(text=f"{expenses:,.0f} VNĐ")
        
        balance = income - expenses
        self.balance_label.config(text=f"{balance:,.0f} VNĐ")
        
        # Update balance card color
        if balance > 0:
            self.balance_label.master.config(bg=self.colors['success'])
            self.balance_label.config(bg=self.colors['success'])
        elif balance < 0:
            self.balance_label.master.config(bg=self.colors['danger'])
            self.balance_label.config(bg=self.colors['danger'])
        else:
            self.balance_label.master.config(bg=self.colors['primary'])
            self.balance_label.config(bg=self.colors['primary'])
        
        # Recent transactions
        recent_query = '''
            SELECT date, type, category, amount, description 
            FROM transactions 
            ORDER BY date DESC, created_at DESC 
            LIMIT 10
        '''
        recent_transactions = self.db.execute_query(recent_query)
        
        # Clear existing items
        for item in self.recent_tree.get_children():
            self.recent_tree.delete(item)
        
        # Add recent transactions
        for trans in recent_transactions:
            date, trans_type, category, amount, description = trans
            type_symbol = "💰" if trans_type == "income" else "💸"
            amount_str = f"{amount:,.0f} VNĐ"
            
            self.recent_tree.insert('', 'end', values=(
                date, f"{type_symbol} {trans_type.title()}", 
                category, amount_str, description or ""
            ))
    
    def refresh_transactions(self):
        # Clear existing items
        for item in self.trans_tree.get_children():
            self.trans_tree.delete(item)
        
        # Build query based on filter
        query = '''
            SELECT id, date, type, category, amount, description 
            FROM transactions
        '''
        params = []
        
        if self.filter_month_var.get():
            query += " WHERE strftime('%Y-%m', date) = ?"
            params.append(self.filter_month_var.get())
        
        query += " ORDER BY date DESC, created_at DESC"
        
        transactions = self.db.execute_query(query, tuple(params))
        
        # Add transactions to tree
        for trans in transactions:
            trans_id, date, trans_type, category, amount, description = trans
            type_symbol = "💰" if trans_type == "income" else "💸"
            amount_str = f"{amount:,.0f} VNĐ"
            
            self.trans_tree.insert('', 'end', values=(
                trans_id, date, f"{type_symbol} {trans_type.title()}", 
                category, amount_str, description or ""
            ))
    
    def refresh_budget(self):
        # Clear existing items
        for item in self.budget_tree.get_children():
            self.budget_tree.delete(item)
        
        current_month = datetime.date.today().strftime('%Y-%m')
        year, month = map(int, current_month.split('-'))
        
        # Get budgets for current month
        budget_query = '''
            SELECT category, monthly_limit 
            FROM budgets 
            WHERE year = ? AND month = ?
        '''
        budgets = self.db.execute_query(budget_query, (year, month))
        
        for category, limit in budgets:
            # Get spent amount for this category
            spent_query = '''
                SELECT COALESCE(SUM(amount), 0) 
                FROM transactions 
                WHERE type = 'expense' AND category = ? AND strftime('%Y-%m', date) = ?
            '''
            spent = self.db.execute_query(spent_query, (category, current_month))[0][0]
            
            remaining = limit - spent
            percentage = (spent / limit * 100) if limit > 0 else 0
            
            # Status
            if percentage > 100:
                status = "🔴 Over Budget"
            elif percentage > 80:
                status = "🟡 Warning"
            else:
                status = "🟢 On Track"
            
            self.budget_tree.insert('', 'end', values=(
                category,
                f"{limit:,.0f} VNĐ",
                f"{spent:,.0f} VNĐ",
                f"{remaining:,.0f} VNĐ",
                status
            ))
    
    def refresh_goals(self):
        # Clear existing items
        for item in self.goals_tree.get_children():
            self.goals_tree.delete(item)
        
        # Get all goals
        goals_query = '''
            SELECT name, target_amount, current_amount, target_date 
            FROM goals 
            ORDER BY target_date
        '''
        goals = self.db.execute_query(goals_query)
        
        for name, target, current, target_date in goals:
            progress = (current / target * 100) if target > 0 else 0
            
            # Status based on progress and date
            if progress >= 100:
                status = "🎉 Completed"
            elif target_date:
                target_dt = datetime.datetime.strptime(target_date, '%Y-%m-%d').date()
                if target_dt < datetime.date.today():
                    status = "⏰ Overdue"
                else:
                    days_left = (target_dt - datetime.date.today()).days
                    status = f"📅 {days_left} days left"
            else:
                status = "🔄 In Progress"
            
            self.goals_tree.insert('', 'end', values=(
                name,
                f"{target:,.0f} VNĐ",
                f"{current:,.0f} VNĐ",
                f"{progress:.1f}%",
                target_date or "No deadline",
                status
            ))
    
    def generate_report(self):
        try:
            # Clear previous charts
            for widget in self.chart_frame.winfo_children():
                widget.destroy()
            
            period = self.report_period_var.get()
            
            # Determine date range
            if period == "This Month":
                start_date = datetime.date.today().replace(day=1)
                end_date = datetime.date.today()
            elif period == "Last Month":
                today = datetime.date.today()
                start_date = (today.replace(day=1) - datetime.timedelta(days=1)).replace(day=1)
                end_date = today.replace(day=1) - datetime.timedelta(days=1)
            elif period == "This Year":
                start_date = datetime.date.today().replace(month=1, day=1)
                end_date = datetime.date.today()
            else:
                # For now, default to this month
                start_date = datetime.date.today().replace(day=1)
                end_date = datetime.date.today()
            
            # Create matplotlib figure
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 8))
            fig.suptitle(f'Financial Report - {period}', fontsize=16, fontweight='bold')
            
            # 1. Income vs Expenses
            income_query = '''
                SELECT COALESCE(SUM(amount), 0) FROM transactions 
                WHERE type = 'income' AND date BETWEEN ? AND ?
            '''
            expense_query = '''
                SELECT COALESCE(SUM(amount), 0) FROM transactions 
                WHERE type = 'expense' AND date BETWEEN ? AND ?
            '''
            
            income_total = self.db.execute_query(income_query, (start_date, end_date))[0][0]
            expense_total = self.db.execute_query(expense_query, (start_date, end_date))[0][0]
            
            ax1.bar(['Income', 'Expenses'], [income_total, expense_total], 
                   color=['#4CAF50', '#F44336'])
            ax1.set_title('Income vs Expenses')
            ax1.set_ylabel('Amount (VNĐ)')
            
            # 2. Expense by Category
            category_query = '''
                SELECT category, SUM(amount) FROM transactions 
                WHERE type = 'expense' AND date BETWEEN ? AND ?
                GROUP BY category
                ORDER BY SUM(amount) DESC
            '''
            categories = self.db.execute_query(category_query, (start_date, end_date))
            
            if categories:
                cat_names = [cat[0] for cat in categories]
                cat_amounts = [cat[1] for cat in categories]
                
                ax2.pie(cat_amounts, labels=cat_names, autopct='%1.1f%%', startangle=90)
                ax2.set_title('Expenses by Category')
            else:
                ax2.text(0.5, 0.5, 'No expense data', ha='center', va='center')
                ax2.set_title('Expenses by Category')
            
            # 3. Daily Balance Trend
            daily_query = '''
                SELECT date, 
                       SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END) -
                       SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END) as daily_balance
                FROM transactions 
                WHERE date BETWEEN ? AND ?
                GROUP BY date
                ORDER BY date
            '''
            daily_data = self.db.execute_query(daily_query, (start_date, end_date))
            
            if daily_data:
                dates = [datetime.datetime.strptime(row[0], '%Y-%m-%d').date() for row in daily_data]
                balances = [row[1] for row in daily_data]
                
                # Calculate cumulative balance
                cumulative_balance = []
                total = 0
                for balance in balances:
                    total += balance
                    cumulative_balance.append(total)
                
                ax3.plot(dates, cumulative_balance, marker='o', linewidth=2, markersize=4)
                ax3.set_title('Cumulative Balance Trend')
                ax3.set_ylabel('Balance (VNĐ)')
                ax3.tick_params(axis='x', rotation=45)
            else:
                ax3.text(0.5, 0.5, 'No data available', ha='center', va='center')
                ax3.set_title('Cumulative Balance Trend')
            
            # 4. Budget Performance
            current_month = datetime.date.today().strftime('%Y-%m')
            year, month = map(int, current_month.split('-'))
            
            budget_performance_query = '''
                SELECT b.category, b.monthly_limit,
                       COALESCE(SUM(t.amount), 0) as spent
                FROM budgets b
                LEFT JOIN transactions t ON b.category = t.category 
                    AND t.type = 'expense' 
                    AND strftime('%Y-%m', t.date) = ?
                WHERE b.year = ? AND b.month = ?
                GROUP BY b.category, b.monthly_limit
            '''
            
            budget_data = self.db.execute_query(budget_performance_query, (current_month, year, month))
            
            if budget_data:
                categories = [row[0] for row in budget_data]
                budgets = [row[1] for row in budget_data]
                spent = [row[2] for row in budget_data]
                
                x = range(len(categories))
                width = 0.35
                
                ax4.bar([i - width/2 for i in x], budgets, width, label='Budget', color='#2196F3')
                ax4.bar([i + width/2 for i in x], spent, width, label='Spent', color='#F44336')
                
                ax4.set_title('Budget vs Actual Spending')
                ax4.set_ylabel('Amount (VNĐ)')
                ax4.set_xticks(x)
                ax4.set_xticklabels([cat.replace('🍔 ', '').replace('🏠 ', '').replace('🚗 ', '')[:8] for cat in categories])
                ax4.legend()
                ax4.tick_params(axis='x', rotation=45)
            else:
                ax4.text(0.5, 0.5, 'No budget data', ha='center', va='center')
                ax4.set_title('Budget vs Actual Spending')
            
            plt.tight_layout()
            
            # Add to tkinter
            canvas = FigureCanvasTkAgg(fig, self.chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {str(e)}")
    
    def export_to_csv(self):
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
            
            if filename:
                # Export all transactions
                query = '''
                    SELECT date, type, category, amount, description 
                    FROM transactions 
                    ORDER BY date DESC
                '''
                transactions = self.db.execute_query(query)
                
                # Create DataFrame and save
                df = pd.DataFrame(transactions, columns=['Date', 'Type', 'Category', 'Amount', 'Description'])
                df.to_csv(filename, index=False, encoding='utf-8')
                
                messagebox.showinfo("Success", f"Data exported to {filename}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export data: {str(e)}")
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    try:
        # Check if required modules are available
        import matplotlib.pyplot as plt
        import pandas as pd
        
        app = PersonalFinanceApp()
        app.run()
        
    except ImportError as e:
        print(f"❌ Missing required module: {e}")
        print("Please install required packages:")
        print("pip install matplotlib pandas")
        
        # Fallback: run without charts
        print("Running in basic mode without charts...")
        
        # Create a simple version without matplotlib
        import tkinter as tk
        from tkinter import messagebox
        
        root = tk.Tk()
        root.title("💰 Personal Finance Manager (Basic Mode)")
        root.geometry("800x600")
        
        tk.Label(root, text="💰 Personal Finance Manager", 
                font=('Arial', 20, 'bold')).pack(pady=20)
        
        tk.Label(root, text="⚠️ Charts not available - missing matplotlib/pandas", 
                font=('Arial', 12), fg='orange').pack(pady=10)
        
        tk.Label(root, text="Please install: pip install matplotlib pandas", 
                font=('Arial', 10)).pack(pady=5)
        
        tk.Button(root, text="Install and Restart", 
                 command=lambda: messagebox.showinfo("Info", "Run: pip install matplotlib pandas")).pack(pady=10)
        
        tk.Button(root, text="Exit", command=root.quit).pack(pady=10)
        
        root.mainloop()