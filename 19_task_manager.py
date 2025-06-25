import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
from datetime import datetime, timedelta

class Task:
    def __init__(self, title, description="", due_date=None, priority="Medium", completed=False):
        self.title = title
        self.description = description
        self.due_date = due_date
        self.priority = priority
        self.completed = completed
        self.created_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def to_dict(self):
        return {
            "title": self.title,
            "description": self.description,
            "due_date": self.due_date,
            "priority": self.priority,
            "completed": self.completed,
            "created_date": self.created_date
        }
    
    @classmethod
    def from_dict(cls, data):
        task = cls(data["title"], data["description"], data["due_date"], data["priority"], data["completed"])
        task.created_date = data["created_date"]
        return task

class TaskManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Task Manager")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        # Task data
        self.tasks = []
        self.current_filter = "All"
        self.current_sort = "Due Date"
        
        # Create UI
        self.create_menu()
        self.create_main_layout()
        
        # Load tasks
        self.load_tasks()
        
        # Set up protocol for window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def create_menu(self):
        menu_bar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="New Task", command=self.add_task)
        file_menu.add_command(label="Save Tasks", command=self.save_tasks)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_close)
        menu_bar.add_cascade(label="File", menu=file_menu)
        
        # View menu
        view_menu = tk.Menu(menu_bar, tearoff=0)
        view_menu.add_command(label="Refresh", command=self.refresh_tasks)
        
        # Filter submenu
        filter_menu = tk.Menu(view_menu, tearoff=0)
        filter_menu.add_command(label="All Tasks", command=lambda: self.filter_tasks("All"))
        filter_menu.add_command(label="Pending Tasks", command=lambda: self.filter_tasks("Pending"))
        filter_menu.add_command(label="Completed Tasks", command=lambda: self.filter_tasks("Completed"))
        filter_menu.add_command(label="Due Today", command=lambda: self.filter_tasks("Due Today"))
        filter_menu.add_command(label="Overdue", command=lambda: self.filter_tasks("Overdue"))
        view_menu.add_cascade(label="Filter", menu=filter_menu)
        
        # Sort submenu
        sort_menu = tk.Menu(view_menu, tearoff=0)
        sort_menu.add_command(label="By Due Date", command=lambda: self.sort_tasks("Due Date"))
        sort_menu.add_command(label="By Priority", command=lambda: self.sort_tasks("Priority"))
        sort_menu.add_command(label="By Created Date", command=lambda: self.sort_tasks("Created Date"))
        view_menu.add_cascade(label="Sort", menu=sort_menu)
        
        menu_bar.add_cascade(label="View", menu=view_menu)
        
        # Help menu
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menu_bar)
    
    def create_main_layout(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Top frame for controls
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Add task button
        add_button = ttk.Button(top_frame, text="Add Task", command=self.add_task)
        add_button.pack(side=tk.LEFT, padx=5)
        
        # Edit task button
        edit_button = ttk.Button(top_frame, text="Edit Task", command=self.edit_task)
        edit_button.pack(side=tk.LEFT, padx=5)
        
        # Delete task button
        delete_button = ttk.Button(top_frame, text="Delete Task", command=self.delete_task)
        delete_button.pack(side=tk.LEFT, padx=5)
        
        # Mark as complete button
        complete_button = ttk.Button(top_frame, text="Mark Complete", command=self.toggle_complete)
        complete_button.pack(side=tk.LEFT, padx=5)
        
        # Filter combobox
        ttk.Label(top_frame, text="Filter:").pack(side=tk.LEFT, padx=(20, 5))
        self.filter_var = tk.StringVar(value="All")
        filter_combo = ttk.Combobox(top_frame, textvariable=self.filter_var, 
                                   values=["All", "Pending", "Completed", "Due Today", "Overdue"],
                                   width=12, state="readonly")
        filter_combo.pack(side=tk.LEFT, padx=5)
        filter_combo.bind("<<ComboboxSelected>>", lambda e: self.filter_tasks(self.filter_var.get()))
        
        # Sort combobox
        ttk.Label(top_frame, text="Sort:").pack(side=tk.LEFT, padx=(20, 5))
        self.sort_var = tk.StringVar(value="Due Date")
        sort_combo = ttk.Combobox(top_frame, textvariable=self.sort_var, 
                                 values=["Due Date", "Priority", "Created Date"],
                                 width=12, state="readonly")
        sort_combo.pack(side=tk.LEFT, padx=5)
        sort_combo.bind("<<ComboboxSelected>>", lambda e: self.sort_tasks(self.sort_var.get()))
        
        # Task list frame
        list_frame = ttk.LabelFrame(main_frame, text="Tasks")
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Task treeview
        columns = ("title", "due_date", "priority", "status")
        self.task_tree = ttk.Treeview(list_frame, columns=columns, show="headings", yscrollcommand=scrollbar.set)
        
        # Define headings
        self.task_tree.heading("title", text="Title")
        self.task_tree.heading("due_date", text="Due Date")
        self.task_tree.heading("priority", text="Priority")
        self.task_tree.heading("status", text="Status")
        
        # Define columns
        self.task_tree.column("title", width=300)
        self.task_tree.column("due_date", width=150)
        self.task_tree.column("priority", width=100)
        self.task_tree.column("status", width=100)
        
        # Pack treeview
        self.task_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configure scrollbar
        scrollbar.config(command=self.task_tree.yview)
        
        # Bind double click to view task details
        self.task_tree.bind("<Double-1>", lambda e: self.view_task_details())
        
        # Status bar
        self.status_var = tk.StringVar()
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, pady=(10, 0))
        
        # Set initial status
        self.update_status()
    
    def add_task(self):
        # Create a dialog for adding a task
        dialog = TaskDialog(self.root, "Add New Task")
        self.root.wait_window(dialog)
        
        if dialog.result:
            # Create a new task
            task = Task(
                dialog.result["title"],
                dialog.result["description"],
                dialog.result["due_date"],
                dialog.result["priority"]
            )
            
            # Add to task list
            self.tasks.append(task)
            
            # Refresh the view
            self.refresh_tasks()
            
            # Save tasks
            self.save_tasks()
    
    def edit_task(self):
        # Get selected task
        selected_id = self.task_tree.selection()
        if not selected_id:
            messagebox.showinfo("Info", "Please select a task to edit")
            return
        
        # Get task index
        task_idx = int(selected_id[0])
        task = self.tasks[task_idx]
        
        # Create dialog with task data
        dialog = TaskDialog(self.root, "Edit Task", task.to_dict())
        self.root.wait_window(dialog)
        
        if dialog.result:
            # Update task
            task.title = dialog.result["title"]
            task.description = dialog.result["description"]
            task.due_date = dialog.result["due_date"]
            task.priority = dialog.result["priority"]
            
            # Refresh the view
            self.refresh_tasks()
            
            # Save tasks
            self.save_tasks()
    
    def delete_task(self):
        # Get selected task
        selected_id = self.task_tree.selection()
        if not selected_id:
            messagebox.showinfo("Info", "Please select a task to delete")
            return
        
        # Confirm deletion
        if not messagebox.askyesno("Confirm", "Are you sure you want to delete this task?"):
            return
        
        # Get task index and remove
        task_idx = int(selected_id[0])
        del self.tasks[task_idx]
        
        # Refresh the view
        self.refresh_tasks()
        
        # Save tasks
        self.save_tasks()
    
    def toggle_complete(self):
        # Get selected task
        selected_id = self.task_tree.selection()
        if not selected_id:
            messagebox.showinfo("Info", "Please select a task to mark as complete")
            return
        
        # Get task index
        task_idx = int(selected_id[0])
        task = self.tasks[task_idx]
        
        # Toggle completion status
        task.completed = not task.completed
        
        # Refresh the view
        self.refresh_tasks()
        
        # Save tasks
        self.save_tasks()
    
    def view_task_details(self):
        # Get selected task
        selected_id = self.task_tree.selection()
        if not selected_id:
            return
        
        # Get task index
        task_idx = int(selected_id[0])
        task = self.tasks[task_idx]
        
        # Show task details
        details = f"Title: {task.title}\n\n"
        details += f"Description: {task.description}\n\n"
        details += f"Due Date: {task.due_date if task.due_date else 'None'}\n\n"
        details += f"Priority: {task.priority}\n\n"
        details += f"Status: {'Completed' if task.completed else 'Pending'}\n\n"
        details += f"Created: {task.created_date}"
        
        messagebox.showinfo("Task Details", details)
    
    def filter_tasks(self, filter_type):
        self.current_filter = filter_type
        self.refresh_tasks()
    
    def sort_tasks(self, sort_type):
        self.current_sort = sort_type
        self.refresh_tasks()
    
    def refresh_tasks(self):
        # Clear the treeview
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)
        
        # Filter tasks
        filtered_tasks = self.get_filtered_tasks()
        
        # Sort tasks
        sorted_tasks = self.get_sorted_tasks(filtered_tasks)
        
        # Add tasks to treeview
        for i, task in enumerate(sorted_tasks):
            status = "Completed" if task.completed else "Pending"
            
            # Determine if task is overdue
            if not task.completed and task.due_date:
                try:
                    due_date = datetime.strptime(task.due_date, "%Y-%m-%d").date()
                    today = datetime.now().date()
                    if due_date < today:
                        status = "Overdue"
                except:
                    pass
            
            self.task_tree.insert("", "end", iid=str(self.tasks.index(task)), 
                                values=(task.title, task.due_date, task.priority, status))
        
        # Update status
        self.update_status()
    
    def get_filtered_tasks(self):
        if self.current_filter == "All":
            return self.tasks
        
        if self.current_filter == "Pending":
            return [task for task in self.tasks if not task.completed]
        
        if self.current_filter == "Completed":
            return [task for task in self.tasks if task.completed]
        
        if self.current_filter == "Due Today":
            today = datetime.now().date().strftime("%Y-%m-%d")
            return [task for task in self.tasks if task.due_date == today and not task.completed]
        
        if self.current_filter == "Overdue":
            today = datetime.now().date()
            overdue = []
            for task in self.tasks:
                if not task.completed and task.due_date:
                    try:
                        due_date = datetime.strptime(task.due_date, "%Y-%m-%d").date()
                        if due_date < today:
                            overdue.append(task)
                    except:
                        pass
            return overdue
        
        return self.tasks
    
    def get_sorted_tasks(self, tasks):
        if self.current_sort == "Due Date":
            # Sort by due date (None values at the end)
            return sorted(tasks, key=lambda x: datetime.strptime(x.due_date, "%Y-%m-%d").date() if x.due_date else datetime.max.date())
        
        if self.current_sort == "Priority":
            # Define priority order
            priority_order = {"High": 0, "Medium": 1, "Low": 2}
            return sorted(tasks, key=lambda x: priority_order.get(x.priority, 3))
        
        if self.current_sort == "Created Date":
            return sorted(tasks, key=lambda x: x.created_date)
        
        return tasks
    
    def update_status(self):
        total = len(self.tasks)
        completed = sum(1 for task in self.tasks if task.completed)
        pending = total - completed
        
        self.status_var.set(f"Total Tasks: {total} | Completed: {completed} | Pending: {pending}")
    
    def load_tasks(self):
        try:
            if os.path.exists("tasks.json"):
                with open("tasks.json", "r") as f:
                    tasks_data = json.load(f)
                    self.tasks = [Task.from_dict(task_data) for task_data in tasks_data]
                    self.refresh_tasks()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load tasks: {str(e)}")
    
    def save_tasks(self):
        try:
            with open("tasks.json", "w") as f:
                tasks_data = [task.to_dict() for task in self.tasks]
                json.dump(tasks_data, f, indent=2)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save tasks: {str(e)}")
    
    def show_about(self):
        about_text = """Task Manager
Version 1.0

A simple application to manage your tasks.
Created with Python and Tkinter.

© 2023 Python Beginner Project
"""
        messagebox.showinfo("About", about_text)
    
    def on_close(self):
        # Save tasks before closing
        self.save_tasks()
        self.root.destroy()


class TaskDialog:
    def __init__(self, parent, title, task_data=None):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("500x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.result = None
        
        # Create form
        self.create_form(task_data)
    
    def create_form(self, task_data):
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        ttk.Label(main_frame, text="Title:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.title_var = tk.StringVar(value=task_data["title"] if task_data else "")
        title_entry = ttk.Entry(main_frame, textvariable=self.title_var, width=40)
        title_entry.grid(row=0, column=1, sticky=tk.W+tk.E, pady=5)
        
        # Description
        ttk.Label(main_frame, text="Description:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.description_text = tk.Text(main_frame, width=40, height=5)
        self.description_text.grid(row=1, column=1, sticky=tk.W+tk.E, pady=5)
        if task_data and task_data["description"]:
            self.description_text.insert("1.0", task_data["description"])
        
        # Due date
        ttk.Label(main_frame, text="Due Date:").grid(row=2, column=0, sticky=tk.W, pady=5)
        
        date_frame = ttk.Frame(main_frame)
        date_frame.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        self.due_date_var = tk.StringVar(value=task_data["due_date"] if task_data and task_data["due_date"] else "")
        due_date_entry = ttk.Entry(date_frame, textvariable=self.due_date_var, width=15)
        due_date_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Label(date_frame, text="(YYYY-MM-DD)").pack(side=tk.LEFT)
        
        # Priority
        ttk.Label(main_frame, text="Priority:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.priority_var = tk.StringVar(value=task_data["priority"] if task_data else "Medium")
        priority_combo = ttk.Combobox(main_frame, textvariable=self.priority_var, 
                                    values=["High", "Medium", "Low"],
                                    width=15, state="readonly")
        priority_combo.grid(row=3, column=1, sticky=tk.W, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        save_button = ttk.Button(button_frame, text="Save", command=self.save)
        save_button.pack(side=tk.LEFT, padx=5)
        
        cancel_button = ttk.Button(button_frame, text="Cancel", command=self.cancel)
        cancel_button.pack(side=tk.LEFT, padx=5)
        
        # Configure grid
        main_frame.columnconfigure(1, weight=1)
    
    def save(self):
        # Validate input
        title = self.title_var.get().strip()
        if not title:
            messagebox.showerror("Error", "Title is required")
            return
        
        # Get values
        description = self.description_text.get("1.0", tk.END).strip()
        due_date = self.due_date_var.get().strip()
        priority = self.priority_var.get()
        
        # Validate date format
        if due_date:
            try:
                datetime.strptime(due_date, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Error", "Invalid date format. Please use YYYY-MM-DD")
                return
        
        # Set result
        self.result = {
            "title": title,
            "description": description,
            "due_date": due_date,
            "priority": priority
        }
        
        # Close dialog
        self.dialog.destroy()
    
    def cancel(self):
        self.dialog.destroy()


def main():
    root = tk.Tk()
    app = TaskManager(root)
    root.mainloop()


if __name__ == "__main__":
    main() 