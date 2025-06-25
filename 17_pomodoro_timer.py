import tkinter as tk
from tkinter import ttk, messagebox
import time
import threading
import json
import os
from datetime import datetime

class PomodoroTimer:
    def __init__(self, root):
        self.root = root
        self.root.title("Pomodoro Timer")
        self.root.geometry("400x500")
        self.root.resizable(False, False)
        self.root.configure(bg="#f0f0f0")
        
        # Default settings
        self.pomodoro_time = 25 * 60  # 25 minutes in seconds
        self.short_break_time = 5 * 60  # 5 minutes in seconds
        self.long_break_time = 15 * 60  # 15 minutes in seconds
        self.pomodoros_until_long_break = 4
        self.auto_start_breaks = True
        self.auto_start_pomodoros = False
        
        # State variables
        self.timer_running = False
        self.timer_paused = False
        self.current_timer_type = "pomodoro"  # "pomodoro", "short_break", "long_break"
        self.remaining_time = self.pomodoro_time
        self.pomodoro_count = 0
        self.timer_thread = None
        self.history = []
        
        # Load settings and history
        self.load_settings()
        self.load_history()
        
        # Create UI components
        self.create_header()
        self.create_timer_display()
        self.create_control_buttons()
        self.create_timer_type_buttons()
        self.create_history_display()
        self.create_settings_button()
        
        # Set up protocol for window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def create_header(self):
        """Create the header with logo and title"""
        header_frame = tk.Frame(self.root, bg="#f0f0f0")
        header_frame.pack(pady=10)
        
        title_label = tk.Label(header_frame, text="Pomodoro Timer", 
                              font=("Arial", 20, "bold"), bg="#f0f0f0", fg="#d95550")
        title_label.pack()
        
        subtitle_label = tk.Label(header_frame, text="Stay focused and productive", 
                                 font=("Arial", 10), bg="#f0f0f0", fg="#666666")
        subtitle_label.pack()
    
    def create_timer_display(self):
        """Create the main timer display"""
        self.timer_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.timer_frame.pack(pady=20)
        
        self.time_display = tk.Label(self.timer_frame, text=self.format_time(self.remaining_time), 
                                    font=("Arial", 48), bg="#f0f0f0", fg="#d95550")
        self.time_display.pack()
        
        self.timer_type_label = tk.Label(self.timer_frame, text="POMODORO", 
                                       font=("Arial", 12), bg="#f0f0f0", fg="#666666")
        self.timer_type_label.pack()
        
        self.pomodoro_counter_label = tk.Label(self.timer_frame, text=f"Pomodoro #{self.pomodoro_count}", 
                                             font=("Arial", 10), bg="#f0f0f0", fg="#666666")
        self.pomodoro_counter_label.pack(pady=5)
    
    def create_control_buttons(self):
        """Create start, pause, and reset buttons"""
        control_frame = tk.Frame(self.root, bg="#f0f0f0")
        control_frame.pack(pady=10)
        
        button_style = {"font": ("Arial", 12), "width": 8, "bd": 0, "pady": 5}
        
        self.start_button = tk.Button(control_frame, text="Start", bg="#d95550", fg="white", 
                                     command=self.start_timer, **button_style)
        self.start_button.grid(row=0, column=0, padx=5)
        
        self.pause_button = tk.Button(control_frame, text="Pause", bg="#666666", fg="white", 
                                     command=self.pause_timer, state=tk.DISABLED, **button_style)
        self.pause_button.grid(row=0, column=1, padx=5)
        
        self.reset_button = tk.Button(control_frame, text="Reset", bg="#666666", fg="white", 
                                     command=self.reset_timer, **button_style)
        self.reset_button.grid(row=0, column=2, padx=5)
    
    def create_timer_type_buttons(self):
        """Create buttons to switch between timer types"""
        timer_type_frame = tk.Frame(self.root, bg="#f0f0f0")
        timer_type_frame.pack(pady=10)
        
        button_style = {"font": ("Arial", 10), "bd": 0, "pady": 3, "padx": 10}
        
        self.pomodoro_button = tk.Button(timer_type_frame, text="Pomodoro", bg="#d95550", fg="white", 
                                       command=lambda: self.switch_timer_type("pomodoro"), **button_style)
        self.pomodoro_button.grid(row=0, column=0, padx=3)
        
        self.short_break_button = tk.Button(timer_type_frame, text="Short Break", bg="#4c9195", fg="white", 
                                          command=lambda: self.switch_timer_type("short_break"), **button_style)
        self.short_break_button.grid(row=0, column=1, padx=3)
        
        self.long_break_button = tk.Button(timer_type_frame, text="Long Break", bg="#457ca3", fg="white", 
                                         command=lambda: self.switch_timer_type("long_break"), **button_style)
        self.long_break_button.grid(row=0, column=2, padx=3)
    
    def create_history_display(self):
        """Create a display for pomodoro history"""
        history_frame = tk.Frame(self.root, bg="#f0f0f0")
        history_frame.pack(pady=10, fill=tk.BOTH, expand=True)
        
        history_label = tk.Label(history_frame, text="Today's Pomodoros", 
                               font=("Arial", 12, "bold"), bg="#f0f0f0", fg="#666666")
        history_label.pack(pady=5)
        
        # Create a frame with scrollbar for history
        history_container = tk.Frame(history_frame, bg="#f0f0f0")
        history_container.pack(fill=tk.BOTH, expand=True)
        
        self.history_canvas = tk.Canvas(history_container, bg="#f0f0f0", highlightthickness=0)
        scrollbar = ttk.Scrollbar(history_container, orient=tk.VERTICAL, command=self.history_canvas.yview)
        
        self.history_list_frame = tk.Frame(self.history_canvas, bg="#f0f0f0")
        
        self.history_list_frame.bind(
            "<Configure>",
            lambda e: self.history_canvas.configure(scrollregion=self.history_canvas.bbox("all"))
        )
        
        self.history_canvas.create_window((0, 0), window=self.history_list_frame, anchor="nw")
        self.history_canvas.configure(yscrollcommand=scrollbar.set)
        
        self.history_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Display history items
        self.update_history_display()
    
    def create_settings_button(self):
        """Create a button to open settings"""
        settings_frame = tk.Frame(self.root, bg="#f0f0f0")
        settings_frame.pack(pady=10)
        
        settings_button = tk.Button(settings_frame, text="⚙️ Settings", bg="#f0f0f0", fg="#666666",
                                  font=("Arial", 10), bd=0, command=self.open_settings)
        settings_button.pack()
    
    def format_time(self, seconds):
        """Format seconds into MM:SS"""
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    def start_timer(self):
        """Start the timer"""
        if self.timer_paused:
            self.timer_paused = False
        else:
            # If starting a new timer
            if not self.timer_running:
                if self.current_timer_type == "pomodoro":
                    self.pomodoro_counter_label.config(text=f"Pomodoro #{self.pomodoro_count + 1}")
        
        self.timer_running = True
        self.start_button.config(state=tk.DISABLED)
        self.pause_button.config(state=tk.NORMAL)
        
        # Start timer in a separate thread
        if self.timer_thread is None or not self.timer_thread.is_alive():
            self.timer_thread = threading.Thread(target=self.run_timer)
            self.timer_thread.daemon = True
            self.timer_thread.start()
    
    def pause_timer(self):
        """Pause the timer"""
        self.timer_paused = True
        self.start_button.config(state=tk.NORMAL, text="Resume")
        self.pause_button.config(state=tk.DISABLED)
    
    def reset_timer(self):
        """Reset the timer to its initial state"""
        self.timer_running = False
        self.timer_paused = False
        
        # Set the appropriate time based on current timer type
        if self.current_timer_type == "pomodoro":
            self.remaining_time = self.pomodoro_time
        elif self.current_timer_type == "short_break":
            self.remaining_time = self.short_break_time
        else:  # long_break
            self.remaining_time = self.long_break_time
        
        # Update the display
        self.time_display.config(text=self.format_time(self.remaining_time))
        self.start_button.config(state=tk.NORMAL, text="Start")
        self.pause_button.config(state=tk.DISABLED)
    
    def run_timer(self):
        """Run the timer countdown"""
        while self.timer_running and self.remaining_time > 0:
            if not self.timer_paused:
                # Update the time display
                self.time_display.config(text=self.format_time(self.remaining_time))
                self.remaining_time -= 1
                
                # Update window title with remaining time
                self.root.title(f"Pomodoro Timer - {self.format_time(self.remaining_time)}")
            
            # Sleep for 1 second
            time.sleep(1)
        
        # Check if timer completed naturally (not reset or paused)
        if self.timer_running and not self.timer_paused and self.remaining_time <= 0:
            self.timer_completed()
    
    def timer_completed(self):
        """Handle timer completion"""
        self.timer_running = False
        self.time_display.config(text="00:00")
        self.start_button.config(state=tk.NORMAL, text="Start")
        self.pause_button.config(state=tk.DISABLED)
        
        # Determine what happens next based on the completed timer type
        if self.current_timer_type == "pomodoro":
            # Increment pomodoro count and add to history
            self.pomodoro_count += 1
            self.add_to_history()
            
            # Play sound and show notification
            self.show_notification("Pomodoro completed!", "Time for a break!")
            
            # Determine if it's time for a long break or short break
            if self.pomodoro_count % self.pomodoros_until_long_break == 0:
                next_timer = "long_break"
                message = "Time for a long break!"
            else:
                next_timer = "short_break"
                message = "Time for a short break!"
            
            # Auto-start break if enabled
            if self.auto_start_breaks:
                self.switch_timer_type(next_timer)
                self.start_timer()
            else:
                self.switch_timer_type(next_timer)
        
        elif self.current_timer_type in ["short_break", "long_break"]:
            # Play sound and show notification
            self.show_notification("Break completed!", "Time to focus!")
            
            # Auto-start next pomodoro if enabled
            if self.auto_start_pomodoros:
                self.switch_timer_type("pomodoro")
                self.start_timer()
            else:
                self.switch_timer_type("pomodoro")
    
    def switch_timer_type(self, timer_type):
        """Switch between pomodoro, short break, and long break"""
        self.current_timer_type = timer_type
        
        # Reset the timer
        self.timer_running = False
        self.timer_paused = False
        
        # Update button colors
        self.pomodoro_button.config(bg="#666666" if timer_type != "pomodoro" else "#d95550")
        self.short_break_button.config(bg="#666666" if timer_type != "short_break" else "#4c9195")
        self.long_break_button.config(bg="#666666" if timer_type != "long_break" else "#457ca3")
        
        # Update timer display color and text
        if timer_type == "pomodoro":
            self.remaining_time = self.pomodoro_time
            self.time_display.config(fg="#d95550")
            self.timer_type_label.config(text="POMODORO")
        elif timer_type == "short_break":
            self.remaining_time = self.short_break_time
            self.time_display.config(fg="#4c9195")
            self.timer_type_label.config(text="SHORT BREAK")
        else:  # long_break
            self.remaining_time = self.long_break_time
            self.time_display.config(fg="#457ca3")
            self.timer_type_label.config(text="LONG BREAK")
        
        # Update time display
        self.time_display.config(text=self.format_time(self.remaining_time))
        
        # Reset buttons
        self.start_button.config(state=tk.NORMAL, text="Start")
        self.pause_button.config(state=tk.DISABLED)
    
    def add_to_history(self):
        """Add completed pomodoro to history"""
        now = datetime.now()
        entry = {
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M:%S"),
            "duration": self.pomodoro_time // 60,  # Duration in minutes
            "type": "pomodoro"
        }
        
        self.history.append(entry)
        self.save_history()
        self.update_history_display()
    
    def update_history_display(self):
        """Update the history display with current history data"""
        # Clear existing history display
        for widget in self.history_list_frame.winfo_children():
            widget.destroy()
        
        # Filter history for today
        today = datetime.now().strftime("%Y-%m-%d")
        today_history = [entry for entry in self.history if entry["date"] == today]
        
        if not today_history:
            no_history_label = tk.Label(self.history_list_frame, text="No pomodoros completed today", 
                                      font=("Arial", 10), bg="#f0f0f0", fg="#666666")
            no_history_label.pack(pady=5)
            return
        
        # Display each history entry
        for i, entry in enumerate(reversed(today_history)):
            entry_frame = tk.Frame(self.history_list_frame, bg="#f0f0f0", bd=1, relief=tk.SOLID)
            entry_frame.pack(fill=tk.X, padx=5, pady=3)
            
            time_label = tk.Label(entry_frame, text=entry["time"], 
                                font=("Arial", 9), bg="#f0f0f0", fg="#666666")
            time_label.pack(side=tk.LEFT, padx=5)
            
            duration_label = tk.Label(entry_frame, text=f"{entry['duration']} min", 
                                    font=("Arial", 9, "bold"), bg="#f0f0f0", fg="#d95550")
            duration_label.pack(side=tk.RIGHT, padx=5)
    
    def open_settings(self):
        """Open settings dialog"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("300x400")
        settings_window.resizable(False, False)
        settings_window.configure(bg="#f0f0f0")
        settings_window.grab_set()  # Make the window modal
        
        # Create settings form
        settings_frame = tk.Frame(settings_window, bg="#f0f0f0", padx=20, pady=20)
        settings_frame.pack(fill=tk.BOTH, expand=True)
        
        # Timer durations
        tk.Label(settings_frame, text="Timer Durations (minutes)", font=("Arial", 12, "bold"), 
               bg="#f0f0f0", fg="#666666").grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))
        
        tk.Label(settings_frame, text="Pomodoro:", bg="#f0f0f0", fg="#666666").grid(row=1, column=0, sticky="w")
        pomodoro_entry = tk.Entry(settings_frame, width=5)
        pomodoro_entry.insert(0, str(self.pomodoro_time // 60))
        pomodoro_entry.grid(row=1, column=1, sticky="w")
        
        tk.Label(settings_frame, text="Short Break:", bg="#f0f0f0", fg="#666666").grid(row=2, column=0, sticky="w")
        short_break_entry = tk.Entry(settings_frame, width=5)
        short_break_entry.insert(0, str(self.short_break_time // 60))
        short_break_entry.grid(row=2, column=1, sticky="w")
        
        tk.Label(settings_frame, text="Long Break:", bg="#f0f0f0", fg="#666666").grid(row=3, column=0, sticky="w")
        long_break_entry = tk.Entry(settings_frame, width=5)
        long_break_entry.insert(0, str(self.long_break_time // 60))
        long_break_entry.grid(row=3, column=1, sticky="w")
        
        # Pomodoros until long break
        tk.Label(settings_frame, text="Pomodoros until long break:", bg="#f0f0f0", fg="#666666").grid(
            row=4, column=0, sticky="w", pady=(10, 0))
        pomodoros_until_long_break_entry = tk.Entry(settings_frame, width=5)
        pomodoros_until_long_break_entry.insert(0, str(self.pomodoros_until_long_break))
        pomodoros_until_long_break_entry.grid(row=4, column=1, sticky="w", pady=(10, 0))
        
        # Auto-start options
        tk.Label(settings_frame, text="Auto-start Options", font=("Arial", 12, "bold"), 
               bg="#f0f0f0", fg="#666666").grid(row=5, column=0, columnspan=2, sticky="w", pady=(20, 10))
        
        auto_start_breaks_var = tk.BooleanVar(value=self.auto_start_breaks)
        auto_start_breaks_check = tk.Checkbutton(settings_frame, text="Auto-start breaks", 
                                              variable=auto_start_breaks_var, bg="#f0f0f0")
        auto_start_breaks_check.grid(row=6, column=0, columnspan=2, sticky="w")
        
        auto_start_pomodoros_var = tk.BooleanVar(value=self.auto_start_pomodoros)
        auto_start_pomodoros_check = tk.Checkbutton(settings_frame, text="Auto-start pomodoros", 
                                                 variable=auto_start_pomodoros_var, bg="#f0f0f0")
        auto_start_pomodoros_check.grid(row=7, column=0, columnspan=2, sticky="w")
        
        # Save button
        def save_settings():
            try:
                # Get and validate values
                pomodoro_min = int(pomodoro_entry.get())
                short_break_min = int(short_break_entry.get())
                long_break_min = int(long_break_entry.get())
                pomodoros_until_long = int(pomodoros_until_long_break_entry.get())
                
                if pomodoro_min <= 0 or short_break_min <= 0 or long_break_min <= 0 or pomodoros_until_long <= 0:
                    raise ValueError("Values must be positive")
                
                # Update settings
                self.pomodoro_time = pomodoro_min * 60
                self.short_break_time = short_break_min * 60
                self.long_break_time = long_break_min * 60
                self.pomodoros_until_long_break = pomodoros_until_long
                self.auto_start_breaks = auto_start_breaks_var.get()
                self.auto_start_pomodoros = auto_start_pomodoros_var.get()
                
                # Save settings to file
                self.save_settings()
                
                # Reset current timer if needed
                self.reset_timer()
                
                # Close settings window
                settings_window.destroy()
                
            except ValueError as e:
                messagebox.showerror("Invalid Input", "Please enter valid positive numbers for all time values.")
        
        save_button = tk.Button(settings_frame, text="Save", bg="#d95550", fg="white", 
                              command=save_settings, font=("Arial", 12), bd=0, pady=5, padx=20)
        save_button.grid(row=8, column=0, columnspan=2, pady=20)
    
    def show_notification(self, title, message):
        """Show a notification when timer completes"""
        # Play a sound (beep) - could be replaced with a custom sound
        self.root.bell()
        
        # Show messagebox
        messagebox.showinfo(title, message)
    
    def save_settings(self):
        """Save settings to a JSON file"""
        settings = {
            "pomodoro_time": self.pomodoro_time,
            "short_break_time": self.short_break_time,
            "long_break_time": self.long_break_time,
            "pomodoros_until_long_break": self.pomodoros_until_long_break,
            "auto_start_breaks": self.auto_start_breaks,
            "auto_start_pomodoros": self.auto_start_pomodoros
        }
        
        # Create pomodoro_data directory if it doesn't exist
        os.makedirs("pomodoro_data", exist_ok=True)
        
        with open("pomodoro_data/settings.json", "w") as f:
            json.dump(settings, f)
    
    def load_settings(self):
        """Load settings from a JSON file"""
        try:
            with open("pomodoro_data/settings.json", "r") as f:
                settings = json.load(f)
            
            self.pomodoro_time = settings.get("pomodoro_time", self.pomodoro_time)
            self.short_break_time = settings.get("short_break_time", self.short_break_time)
            self.long_break_time = settings.get("long_break_time", self.long_break_time)
            self.pomodoros_until_long_break = settings.get("pomodoros_until_long_break", self.pomodoros_until_long_break)
            self.auto_start_breaks = settings.get("auto_start_breaks", self.auto_start_breaks)
            self.auto_start_pomodoros = settings.get("auto_start_pomodoros", self.auto_start_pomodoros)
            
            # Update remaining time based on current timer type
            if self.current_timer_type == "pomodoro":
                self.remaining_time = self.pomodoro_time
            elif self.current_timer_type == "short_break":
                self.remaining_time = self.short_break_time
            else:  # long_break
                self.remaining_time = self.long_break_time
                
        except (FileNotFoundError, json.JSONDecodeError):
            # Use default settings if file doesn't exist or is invalid
            pass
    
    def save_history(self):
        """Save pomodoro history to a JSON file"""
        # Create pomodoro_data directory if it doesn't exist
        os.makedirs("pomodoro_data", exist_ok=True)
        
        with open("pomodoro_data/history.json", "w") as f:
            json.dump(self.history, f)
    
    def load_history(self):
        """Load pomodoro history from a JSON file"""
        try:
            with open("pomodoro_data/history.json", "r") as f:
                self.history = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # Use empty history if file doesn't exist or is invalid
            self.history = []
    
    def on_close(self):
        """Handle window close event"""
        # Stop the timer thread
        self.timer_running = False
        
        # Save settings and history
        self.save_settings()
        self.save_history()
        
        # Close the window
        self.root.destroy()

def main():
    root = tk.Tk()
    app = PomodoroTimer(root)
    root.mainloop()

if __name__ == "__main__":
    main() 