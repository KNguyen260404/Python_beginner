import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import json
import os
from datetime import datetime
import re

# Try to import seaborn, but make it optional
try:
    import seaborn as sns
    HAS_SEABORN = True
except ImportError:
    HAS_SEABORN = False
    print("Seaborn not installed. Some visualization features will be limited.")

# Set style for plots
plt.style.use('ggplot')
if HAS_SEABORN:
    sns.set_palette("Set2")

class DataVisualizationDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Data Visualization Dashboard")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # Data variables
        self.data = None
        self.file_path = None
        self.current_plot_type = None
        self.plot_settings = {
            "title": "",
            "x_label": "",
            "y_label": "",
            "color": "#1f77b4",
            "figsize": (10, 6),
            "grid": True,
            "legend": True
        }
        self.recent_files = []
        self.saved_visualizations = []
        
        # Load settings and history
        self.load_settings()
        
        # Create main UI structure
        self.create_menu()
        self.create_main_layout()
        
        # Set up protocol for window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def create_menu(self):
        """Create the application menu"""
        menu_bar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Open Data File", command=self.open_file)
        file_menu.add_command(label="Save Visualization", command=self.save_visualization)
        
        # Recent files submenu
        self.recent_menu = tk.Menu(file_menu, tearoff=0)
        self.update_recent_files_menu()
        file_menu.add_cascade(label="Recent Files", menu=self.recent_menu)
        
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_close)
        menu_bar.add_cascade(label="File", menu=file_menu)
        
        # Visualization menu
        viz_menu = tk.Menu(menu_bar, tearoff=0)
        viz_menu.add_command(label="Bar Chart", command=lambda: self.set_plot_type("bar"))
        viz_menu.add_command(label="Line Chart", command=lambda: self.set_plot_type("line"))
        viz_menu.add_command(label="Scatter Plot", command=lambda: self.set_plot_type("scatter"))
        viz_menu.add_command(label="Histogram", command=lambda: self.set_plot_type("histogram"))
        viz_menu.add_command(label="Box Plot", command=lambda: self.set_plot_type("box"))
        viz_menu.add_command(label="Heatmap", command=lambda: self.set_plot_type("heatmap"))
        viz_menu.add_command(label="Pie Chart", command=lambda: self.set_plot_type("pie"))
        menu_bar.add_cascade(label="Visualizations", menu=viz_menu)
        
        # Settings menu
        settings_menu = tk.Menu(menu_bar, tearoff=0)
        settings_menu.add_command(label="Plot Settings", command=self.open_plot_settings)
        settings_menu.add_command(label="Theme Settings", command=self.open_theme_settings)
        menu_bar.add_cascade(label="Settings", menu=settings_menu)
        
        # Help menu
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="Help", command=self.show_help)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menu_bar)
    
    def create_main_layout(self):
        """Create the main application layout"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create a PanedWindow for resizable sections
        paned_window = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True)
        
        # Left panel for data and controls
        self.left_panel = ttk.Frame(paned_window, width=300)
        paned_window.add(self.left_panel, weight=1)
        
        # Right panel for visualization
        self.right_panel = ttk.Frame(paned_window)
        paned_window.add(self.right_panel, weight=3)
        
        # Create the components for each panel
        self.create_left_panel()
        self.create_right_panel()
    
    def create_left_panel(self):
        """Create the left panel with data and controls"""
        # Data section
        data_frame = ttk.LabelFrame(self.left_panel, text="Data", padding="10")
        data_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Data file info
        self.file_label = ttk.Label(data_frame, text="No file loaded", wraplength=280)
        self.file_label.pack(fill=tk.X, pady=5)
        
        # Open file button
        open_button = ttk.Button(data_frame, text="Open Data File", command=self.open_file)
        open_button.pack(fill=tk.X, pady=5)
        
        # Data preview section
        preview_label = ttk.Label(data_frame, text="Data Preview:")
        preview_label.pack(anchor=tk.W, pady=(10, 5))
        
        # Treeview for data preview
        preview_frame = ttk.Frame(data_frame)
        preview_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbars for treeview
        y_scroll = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL)
        x_scroll = ttk.Scrollbar(preview_frame, orient=tk.HORIZONTAL)
        
        # Create treeview
        self.data_preview = ttk.Treeview(preview_frame, yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        
        # Configure scrollbars
        y_scroll.config(command=self.data_preview.yview)
        x_scroll.config(command=self.data_preview.xview)
        
        # Place widgets
        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        x_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.data_preview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Visualization controls section
        controls_frame = ttk.LabelFrame(self.left_panel, text="Visualization Controls", padding="10")
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # X-axis selection
        ttk.Label(controls_frame, text="X-Axis:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.x_axis_var = tk.StringVar()
        self.x_axis_combo = ttk.Combobox(controls_frame, textvariable=self.x_axis_var, state="readonly")
        self.x_axis_combo.grid(row=0, column=1, sticky=tk.W+tk.E, pady=2)
        self.x_axis_combo.bind("<<ComboboxSelected>>", lambda e: self.update_plot())
        
        # Y-axis selection
        ttk.Label(controls_frame, text="Y-Axis:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.y_axis_var = tk.StringVar()
        self.y_axis_combo = ttk.Combobox(controls_frame, textvariable=self.y_axis_var, state="readonly")
        self.y_axis_combo.grid(row=1, column=1, sticky=tk.W+tk.E, pady=2)
        self.y_axis_combo.bind("<<ComboboxSelected>>", lambda e: self.update_plot())
        
        # Plot type selection
        ttk.Label(controls_frame, text="Plot Type:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.plot_type_var = tk.StringVar(value="bar")
        plot_types = ["bar", "line", "scatter", "histogram", "box", "heatmap", "pie"]
        self.plot_type_combo = ttk.Combobox(controls_frame, textvariable=self.plot_type_var, 
                                          values=plot_types, state="readonly")
        self.plot_type_combo.grid(row=2, column=1, sticky=tk.W+tk.E, pady=2)
        self.plot_type_combo.bind("<<ComboboxSelected>>", lambda e: self.set_plot_type(self.plot_type_var.get()))
        
        # Generate plot button
        generate_button = ttk.Button(controls_frame, text="Generate Plot", command=self.update_plot)
        generate_button.grid(row=3, column=0, columnspan=2, sticky=tk.W+tk.E, pady=10)
        
        # Configure grid
        controls_frame.columnconfigure(1, weight=1)
    
    def create_right_panel(self):
        """Create the right panel for visualization"""
        # Visualization section
        viz_frame = ttk.LabelFrame(self.right_panel, text="Visualization", padding="10")
        viz_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Canvas for matplotlib figure
        self.canvas_frame = ttk.Frame(viz_frame)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        # Initial message
        self.initial_message = ttk.Label(self.canvas_frame, 
                                      text="Open a data file and select visualization options to begin",
                                      font=("Arial", 12))
        self.initial_message.pack(expand=True)
        
        # Visualization options section
        options_frame = ttk.Frame(viz_frame)
        options_frame.pack(fill=tk.X, pady=5)
        
        # Save visualization button
        save_button = ttk.Button(options_frame, text="Save Visualization", command=self.save_visualization)
        save_button.pack(side=tk.LEFT, padx=5)
        
        # Export as image button
        export_button = ttk.Button(options_frame, text="Export as Image", command=self.export_image)
        export_button.pack(side=tk.LEFT, padx=5)
        
        # Plot settings button
        settings_button = ttk.Button(options_frame, text="Plot Settings", command=self.open_plot_settings)
        settings_button.pack(side=tk.LEFT, padx=5)
    
    def open_file(self):
        """Open a data file (CSV, Excel, etc.)"""
        file_types = [
            ("CSV files", "*.csv"),
            ("Excel files", "*.xlsx *.xls"),
            ("JSON files", "*.json"),
            ("All files", "*.*")
        ]
        
        file_path = filedialog.askopenfilename(
            title="Open Data File",
            filetypes=file_types
        )
        
        if not file_path:
            return
        
        try:
            # Determine file type and load data
            if file_path.endswith('.csv'):
                self.data = pd.read_csv(file_path)
            elif file_path.endswith(('.xlsx', '.xls')):
                self.data = pd.read_excel(file_path)
            elif file_path.endswith('.json'):
                self.data = pd.read_json(file_path)
            else:
                messagebox.showerror("Error", "Unsupported file format")
                return
            
            # Update file path and add to recent files
            self.file_path = file_path
            self.add_to_recent_files(file_path)
            
            # Update UI
            self.file_label.config(text=f"File: {os.path.basename(file_path)}")
            self.update_data_preview()
            self.update_column_selectors()
            
            # Clear any existing plot
            self.clear_plot()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {str(e)}")
    
    def update_data_preview(self):
        """Update the data preview treeview with the loaded data"""
        if self.data is None:
            return
        
        # Clear existing data
        for item in self.data_preview.get_children():
            self.data_preview.delete(item)
        
        # Configure columns
        self.data_preview["columns"] = list(self.data.columns)
        self.data_preview["show"] = "headings"
        
        # Set column headings
        for col in self.data.columns:
            self.data_preview.heading(col, text=col)
            # Set a reasonable column width
            self.data_preview.column(col, width=100)
        
        # Add data rows (limit to 100 for performance)
        preview_data = self.data.head(100)
        for i, row in preview_data.iterrows():
            values = [str(row[col]) for col in self.data.columns]
            self.data_preview.insert("", "end", values=values)
    
    def update_column_selectors(self):
        """Update the column selector comboboxes with available columns"""
        if self.data is None:
            return
        
        # Get columns that can be used for plotting
        numeric_cols = self.data.select_dtypes(include=np.number).columns.tolist()
        all_cols = self.data.columns.tolist()
        
        # Update comboboxes
        self.x_axis_combo["values"] = all_cols
        self.y_axis_combo["values"] = numeric_cols
        
        # Set default selections if possible
        if all_cols:
            self.x_axis_var.set(all_cols[0])
        if numeric_cols:
            self.y_axis_var.set(numeric_cols[0])
    
    def set_plot_type(self, plot_type):
        """Set the current plot type and update the plot"""
        self.current_plot_type = plot_type
        self.plot_type_var.set(plot_type)
        
        # Update plot if we have data
        if self.data is not None:
            self.update_plot()
    
    def update_plot(self):
        """Update the plot based on current settings"""
        if self.data is None:
            messagebox.showinfo("Info", "Please load a data file first")
            return
        
        # Get selected columns
        x_col = self.x_axis_var.get()
        y_col = self.y_axis_var.get()
        
        if not x_col or not y_col:
            messagebox.showinfo("Info", "Please select X and Y axis columns")
            return
        
        # Clear any existing plot
        self.clear_plot()
        
        try:
            # Create figure and axis
            fig, ax = plt.subplots(figsize=self.plot_settings["figsize"])
            
            # Create the plot based on the selected type
            if self.current_plot_type == "bar":
                self.create_bar_plot(ax, x_col, y_col)
            elif self.current_plot_type == "line":
                self.create_line_plot(ax, x_col, y_col)
            elif self.current_plot_type == "scatter":
                self.create_scatter_plot(ax, x_col, y_col)
            elif self.current_plot_type == "histogram":
                self.create_histogram(ax, y_col)
            elif self.current_plot_type == "box":
                self.create_box_plot(ax, x_col, y_col)
            elif self.current_plot_type == "heatmap":
                self.create_heatmap(fig, ax)
            elif self.current_plot_type == "pie":
                self.create_pie_chart(ax, x_col, y_col)
            else:
                # Default to bar chart
                self.create_bar_plot(ax, x_col, y_col)
            
            # Apply common settings
            if self.plot_settings["title"]:
                ax.set_title(self.plot_settings["title"])
            
            if self.plot_settings["x_label"]:
                ax.set_xlabel(self.plot_settings["x_label"])
            else:
                ax.set_xlabel(x_col)
                
            if self.plot_settings["y_label"]:
                ax.set_ylabel(self.plot_settings["y_label"])
            else:
                ax.set_ylabel(y_col)
            
            ax.grid(self.plot_settings["grid"])
            
            if self.current_plot_type != "pie" and self.current_plot_type != "heatmap":
                if self.plot_settings["legend"]:
                    ax.legend()
            
            # Adjust layout
            plt.tight_layout()
            
            # Create canvas
            self.display_plot(fig)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create plot: {str(e)}")
            print(f"Error details: {str(e)}")
    
    def create_bar_plot(self, ax, x_col, y_col):
        """Create a bar plot"""
        data = self.data.copy()
        
        # If x column is not categorical, try to bin it
        if data[x_col].dtype.kind in 'fc' and len(data[x_col].unique()) > 20:
            # Too many unique values, use top N values
            top_values = data.groupby(x_col)[y_col].sum().nlargest(10).index
            data = data[data[x_col].isin(top_values)]
        
        # Create the plot
        bars = ax.bar(data[x_col], data[y_col], color=self.plot_settings["color"])
        
        # Add value labels on top of bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}', ha='center', va='bottom')
        
        # Rotate x labels if there are many categories
        if len(data[x_col].unique()) > 5:
            plt.xticks(rotation=45, ha='right')
    
    def create_line_plot(self, ax, x_col, y_col):
        """Create a line plot"""
        # Sort data by x column for proper line plot
        data = self.data.copy().sort_values(by=x_col)
        
        # Create the plot
        ax.plot(data[x_col], data[y_col], marker='o', color=self.plot_settings["color"])
        
        # Rotate x labels if there are many points
        if len(data[x_col].unique()) > 10:
            plt.xticks(rotation=45, ha='right')
    
    def create_scatter_plot(self, ax, x_col, y_col):
        """Create a scatter plot"""
        ax.scatter(self.data[x_col], self.data[y_col], color=self.plot_settings["color"], alpha=0.7)
        
        # Add trend line
        try:
            # Only add trend line if x is numeric
            if pd.api.types.is_numeric_dtype(self.data[x_col]):
                z = np.polyfit(self.data[x_col], self.data[y_col], 1)
                p = np.poly1d(z)
                ax.plot(self.data[x_col], p(self.data[x_col]), "r--", alpha=0.8)
        except:
            # Skip trend line if it can't be calculated
            pass
    
    def create_histogram(self, ax, y_col):
        """Create a histogram"""
        ax.hist(self.data[y_col], bins=20, color=self.plot_settings["color"], alpha=0.7)
        
        # Add a density curve
        if self.data[y_col].dtype.kind in 'fc':  # Only for numeric data
            try:
                if HAS_SEABORN:
                    sns.kdeplot(self.data[y_col], ax=ax, color='red')
                else:
                    # Use numpy to calculate kernel density estimate
                    from scipy import stats
                    import numpy as np
                    density = stats.gaussian_kde(self.data[y_col].dropna())
                    x_range = np.linspace(min(self.data[y_col].dropna()), max(self.data[y_col].dropna()), 100)
                    ax.plot(x_range, density(x_range), color='red')
            except:
                # Skip density plot if it can't be calculated
                pass
    
    def create_box_plot(self, ax, x_col, y_col):
        """Create a box plot"""
        # If x has too many unique values, use top categories
        if len(self.data[x_col].unique()) > 10:
            top_categories = self.data.groupby(x_col)[y_col].median().nlargest(10).index
            plot_data = self.data[self.data[x_col].isin(top_categories)]
        else:
            plot_data = self.data
        
        if HAS_SEABORN:
            sns.boxplot(x=x_col, y=y_col, data=plot_data, ax=ax)
        else:
            # Use matplotlib's boxplot if seaborn is not available
            # Group data by x column
            grouped = plot_data.groupby(x_col)[y_col].apply(list).tolist()
            ax.boxplot(grouped)
            ax.set_xticklabels(plot_data[x_col].unique())
        
        # Rotate x labels if there are many categories
        if len(plot_data[x_col].unique()) > 5:
            plt.xticks(rotation=45, ha='right')
    
    def create_heatmap(self, fig, ax):
        """Create a heatmap of correlations"""
        # Get numeric columns only
        numeric_data = self.data.select_dtypes(include=np.number)
        
        if numeric_data.shape[1] < 2:
            messagebox.showinfo("Info", "Need at least 2 numeric columns for a heatmap")
            return
            
        # Calculate correlation matrix
        corr = numeric_data.corr()
        
        # Create heatmap
        if HAS_SEABORN:
            sns.heatmap(corr, annot=True, cmap='coolwarm', ax=ax)
        else:
            # Use matplotlib's imshow if seaborn is not available
            im = ax.imshow(corr, cmap='coolwarm')
            # Add colorbar
            fig.colorbar(im, ax=ax)
            # Add text annotations
            for i in range(len(corr.columns)):
                for j in range(len(corr.columns)):
                    text = ax.text(j, i, f'{corr.iloc[i, j]:.2f}',
                                ha="center", va="center", color="black")
            # Set tick labels
            ax.set_xticks(np.arange(len(corr.columns)))
            ax.set_yticks(np.arange(len(corr.columns)))
            ax.set_xticklabels(corr.columns)
            ax.set_yticklabels(corr.columns)
            plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
        
        # Adjust figure size based on number of columns
        n_cols = len(corr.columns)
        fig.set_size_inches(max(8, n_cols * 0.8), max(6, n_cols * 0.8))
    
    def create_pie_chart(self, ax, x_col, y_col):
        """Create a pie chart"""
        # Aggregate data by x column
        pie_data = self.data.groupby(x_col)[y_col].sum()
        
        # If too many categories, use top N
        if len(pie_data) > 10:
            pie_data = pie_data.nlargest(10)
            
        # Create pie chart
        ax.pie(pie_data, labels=pie_data.index, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
    
    def clear_plot(self):
        """Clear the current plot"""
        # Remove all widgets from canvas frame
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()
    
    def display_plot(self, fig):
        """Display the matplotlib figure in the canvas frame"""
        # Create canvas
        canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
        canvas.draw()
        
        # Add toolbar
        toolbar = NavigationToolbar2Tk(canvas, self.canvas_frame)
        toolbar.update()
        
        # Pack canvas
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def export_image(self):
        """Export the current plot as an image file"""
        if not hasattr(self, 'canvas'):
            messagebox.showinfo("Info", "Create a plot first")
            return
            
        file_types = [
            ("PNG files", "*.png"),
            ("JPEG files", "*.jpg"),
            ("PDF files", "*.pdf"),
            ("SVG files", "*.svg")
        ]
        
        file_path = filedialog.asksaveasfilename(
            title="Save Image As",
            filetypes=file_types,
            defaultextension=".png"
        )
        
        if not file_path:
            return
            
        try:
            plt.savefig(file_path, dpi=300, bbox_inches='tight')
            messagebox.showinfo("Success", f"Image saved to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save image: {str(e)}")
    
    def save_visualization(self):
        """Save the current visualization settings"""
        if self.data is None:
            messagebox.showinfo("Info", "Load data and create a plot first")
            return
            
        # Get visualization name
        viz_name = simpledialog.askstring("Save Visualization", 
                                        "Enter a name for this visualization:",
                                        parent=self.root)
        
        if not viz_name:
            return
            
        # Create visualization data
        visualization = {
            "name": viz_name,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "file_path": self.file_path,
            "plot_type": self.current_plot_type,
            "x_axis": self.x_axis_var.get(),
            "y_axis": self.y_axis_var.get(),
            "plot_settings": self.plot_settings
        }
        
        # Add to saved visualizations
        self.saved_visualizations.append(visualization)
        
        # Save to file
        self.save_settings()
        
        messagebox.showinfo("Success", f"Visualization '{viz_name}' saved")
    
    def add_to_recent_files(self, file_path):
        """Add a file to the recent files list"""
        # Remove if already exists
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)
            
        # Add to beginning of list
        self.recent_files.insert(0, file_path)
        
        # Keep only the last 10 files
        self.recent_files = self.recent_files[:10]
        
        # Update menu
        self.update_recent_files_menu()
        
        # Save settings
        self.save_settings()
    
    def update_recent_files_menu(self):
        """Update the recent files menu"""
        # Clear existing menu items
        self.recent_menu.delete(0, tk.END)
        
        if not self.recent_files:
            self.recent_menu.add_command(label="No recent files", state=tk.DISABLED)
            return
            
        # Add recent files to menu
        for file_path in self.recent_files:
            file_name = os.path.basename(file_path)
            self.recent_menu.add_command(
                label=file_name,
                command=lambda path=file_path: self.open_recent_file(path)
            )
    
    def open_recent_file(self, file_path):
        """Open a file from the recent files list"""
        if not os.path.exists(file_path):
            messagebox.showerror("Error", f"File not found: {file_path}")
            # Remove from recent files
            self.recent_files.remove(file_path)
            self.update_recent_files_menu()
            self.save_settings()
            return
            
        # Set file path and open
        self.file_path = file_path
        self.open_file()
    
    def open_plot_settings(self):
        """Open a dialog to adjust plot settings"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Plot Settings")
        settings_window.geometry("400x450")
        settings_window.resizable(False, False)
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # Create settings form
        frame = ttk.Frame(settings_window, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        ttk.Label(frame, text="Title:").grid(row=0, column=0, sticky=tk.W, pady=5)
        title_var = tk.StringVar(value=self.plot_settings["title"])
        title_entry = ttk.Entry(frame, textvariable=title_var, width=30)
        title_entry.grid(row=0, column=1, sticky=tk.W+tk.E, pady=5)
        
        # X-axis label
        ttk.Label(frame, text="X-axis Label:").grid(row=1, column=0, sticky=tk.W, pady=5)
        x_label_var = tk.StringVar(value=self.plot_settings["x_label"])
        x_label_entry = ttk.Entry(frame, textvariable=x_label_var, width=30)
        x_label_entry.grid(row=1, column=1, sticky=tk.W+tk.E, pady=5)
        
        # Y-axis label
        ttk.Label(frame, text="Y-axis Label:").grid(row=2, column=0, sticky=tk.W, pady=5)
        y_label_var = tk.StringVar(value=self.plot_settings["y_label"])
        y_label_entry = ttk.Entry(frame, textvariable=y_label_var, width=30)
        y_label_entry.grid(row=2, column=1, sticky=tk.W+tk.E, pady=5)
        
        # Color
        ttk.Label(frame, text="Plot Color:").grid(row=3, column=0, sticky=tk.W, pady=5)
        color_frame = ttk.Frame(frame)
        color_frame.grid(row=3, column=1, sticky=tk.W, pady=5)
        
        color_preview = tk.Canvas(color_frame, width=20, height=20, bg=self.plot_settings["color"])
        color_preview.pack(side=tk.LEFT, padx=(0, 10))
        
        def choose_color():
            color = colorchooser.askcolor(self.plot_settings["color"])[1]
            if color:
                color_preview.config(bg=color)
        
        color_button = ttk.Button(color_frame, text="Choose Color", command=choose_color)
        color_button.pack(side=tk.LEFT)
        
        # Figure size
        ttk.Label(frame, text="Figure Size:").grid(row=4, column=0, sticky=tk.W, pady=5)
        size_frame = ttk.Frame(frame)
        size_frame.grid(row=4, column=1, sticky=tk.W, pady=5)
        
        width_var = tk.DoubleVar(value=self.plot_settings["figsize"][0])
        height_var = tk.DoubleVar(value=self.plot_settings["figsize"][1])
        
        ttk.Label(size_frame, text="Width:").pack(side=tk.LEFT)
        width_spinner = ttk.Spinbox(size_frame, from_=1, to=20, increment=0.5, 
                                  textvariable=width_var, width=5)
        width_spinner.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Label(size_frame, text="Height:").pack(side=tk.LEFT)
        height_spinner = ttk.Spinbox(size_frame, from_=1, to=20, increment=0.5, 
                                   textvariable=height_var, width=5)
        height_spinner.pack(side=tk.LEFT)
        
        # Grid
        grid_var = tk.BooleanVar(value=self.plot_settings["grid"])
        grid_check = ttk.Checkbutton(frame, text="Show Grid", variable=grid_var)
        grid_check.grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Legend
        legend_var = tk.BooleanVar(value=self.plot_settings["legend"])
        legend_check = ttk.Checkbutton(frame, text="Show Legend", variable=legend_var)
        legend_check.grid(row=6, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=7, column=0, columnspan=2, pady=20)
        
        def save_settings():
            self.plot_settings["title"] = title_var.get()
            self.plot_settings["x_label"] = x_label_var.get()
            self.plot_settings["y_label"] = y_label_var.get()
            self.plot_settings["color"] = color_preview.cget("bg")
            self.plot_settings["figsize"] = (width_var.get(), height_var.get())
            self.plot_settings["grid"] = grid_var.get()
            self.plot_settings["legend"] = legend_var.get()
            
            # Update plot if exists
            if self.data is not None and self.current_plot_type is not None:
                self.update_plot()
                
            settings_window.destroy()
        
        save_button = ttk.Button(button_frame, text="Save", command=save_settings)
        save_button.pack(side=tk.LEFT, padx=5)
        
        cancel_button = ttk.Button(button_frame, text="Cancel", command=settings_window.destroy)
        cancel_button.pack(side=tk.LEFT, padx=5)
        
        # Configure grid
        frame.columnconfigure(1, weight=1)
    
    def open_theme_settings(self):
        """Open a dialog to adjust theme settings"""
        theme_window = tk.Toplevel(self.root)
        theme_window.title("Theme Settings")
        theme_window.geometry("300x200")
        theme_window.resizable(False, False)
        theme_window.transient(self.root)
        theme_window.grab_set()
        
        # Create settings form
        frame = ttk.Frame(theme_window, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Theme selection
        ttk.Label(frame, text="Select Theme:").grid(row=0, column=0, sticky=tk.W, pady=10)
        
        # Available themes
        available_themes = [
            "default", "clam", "alt", "vista", "xpnative", "classic"
        ]
        
        theme_var = tk.StringVar()
        theme_combo = ttk.Combobox(frame, textvariable=theme_var, values=available_themes, state="readonly")
        theme_combo.current(0)
        theme_combo.grid(row=0, column=1, sticky=tk.W+tk.E, pady=10)
        
        # Plot style
        ttk.Label(frame, text="Plot Style:").grid(row=1, column=0, sticky=tk.W, pady=10)
        
        # Available plot styles
        plot_styles = plt.style.available
        
        style_var = tk.StringVar(value="ggplot")
        style_combo = ttk.Combobox(frame, textvariable=style_var, values=plot_styles, state="readonly")
        style_combo.grid(row=1, column=1, sticky=tk.W+tk.E, pady=10)
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        def apply_theme():
            # Apply ttk theme
            selected_theme = theme_var.get()
            style = ttk.Style()
            style.theme_use(selected_theme)
            
            # Apply plot style
            selected_style = style_var.get()
            plt.style.use(selected_style)
            
            # Apply seaborn palette if available
            if HAS_SEABORN and selected_style != "default":
                try:
                    sns.set_palette("Set2")
                except:
                    pass
            
            # Update plot if exists
            if self.data is not None and self.current_plot_type is not None:
                self.update_plot()
                
            theme_window.destroy()
        
        apply_button = ttk.Button(button_frame, text="Apply", command=apply_theme)
        apply_button.pack(side=tk.LEFT, padx=5)
        
        cancel_button = ttk.Button(button_frame, text="Cancel", command=theme_window.destroy)
        cancel_button.pack(side=tk.LEFT, padx=5)
        
        # Configure grid
        frame.columnconfigure(1, weight=1)
    
    def show_about(self):
        """Show about dialog"""
        about_text = """Data Visualization Dashboard
Version 1.0

A powerful tool for visualizing and analyzing data.
Created with Python, Tkinter, and Matplotlib.

© 2023 Python Beginner Project
"""
        messagebox.showinfo("About", about_text)
    
    def show_help(self):
        """Show help dialog"""
        help_text = """How to use the Data Visualization Dashboard:

1. Open a data file (CSV, Excel, or JSON) from the File menu or the Open button.
2. Select columns for X and Y axes from the dropdown menus.
3. Choose a plot type from the dropdown or Visualizations menu.
4. Click "Generate Plot" to create the visualization.
5. Adjust plot settings from the Settings menu.
6. Save or export your visualization using the buttons below the plot.

Supported plot types:
- Bar Chart: For categorical comparisons
- Line Chart: For trends over time or sequences
- Scatter Plot: For correlation between variables
- Histogram: For distribution of a single variable
- Box Plot: For statistical distribution and outliers
- Heatmap: For correlation matrix of numeric variables
- Pie Chart: For part-to-whole relationships

For more help, visit the documentation or contact support.
"""
        help_window = tk.Toplevel(self.root)
        help_window.title("Help")
        help_window.geometry("600x500")
        help_window.transient(self.root)
        
        # Create scrollable text widget
        frame = ttk.Frame(help_window, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Text widget
        text = tk.Text(frame, wrap=tk.WORD, yscrollcommand=scrollbar.set)
        text.pack(fill=tk.BOTH, expand=True)
        text.insert(tk.END, help_text)
        text.config(state=tk.DISABLED)
        
        scrollbar.config(command=text.yview)
        
        # Close button
        close_button = ttk.Button(help_window, text="Close", command=help_window.destroy)
        close_button.pack(pady=10)
    
    def load_settings(self):
        """Load settings from file"""
        settings_file = "dashboard_settings.json"
        
        if os.path.exists(settings_file):
            try:
                with open(settings_file, "r") as f:
                    settings = json.load(f)
                    
                    # Load recent files
                    if "recent_files" in settings:
                        self.recent_files = settings["recent_files"]
                        
                    # Load saved visualizations
                    if "saved_visualizations" in settings:
                        self.saved_visualizations = settings["saved_visualizations"]
                        
                    # Load plot settings
                    if "plot_settings" in settings:
                        self.plot_settings.update(settings["plot_settings"])
            except:
                # If error loading settings, use defaults
                pass
    
    def save_settings(self):
        """Save settings to file"""
        settings_file = "dashboard_settings.json"
        
        settings = {
            "recent_files": self.recent_files,
            "saved_visualizations": self.saved_visualizations,
            "plot_settings": self.plot_settings
        }
        
        try:
            with open(settings_file, "w") as f:
                json.dump(settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {str(e)}")
    
    def on_close(self):
        """Handle window close event"""
        # Save settings
        self.save_settings()
        
        # Destroy root window
        self.root.destroy()


def main():
    """Main application entry point"""
    # Create root window
    root = tk.Tk()
    
    # Set application icon
    try:
        # Try to set icon if available
        root.iconbitmap("chart_icon.ico")
    except:
        # Ignore if icon not found
        pass
    
    # Create application
    app = DataVisualizationDashboard(root)
    
    # Start main loop
    root.mainloop()


if __name__ == "__main__":
    main()
