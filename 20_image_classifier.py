import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import numpy as np
import os
import json
import threading
import time
from datetime import datetime

# Check for machine learning libraries
try:
    import tensorflow as tf
    from tensorflow.keras.applications import MobileNetV2
    from tensorflow.keras.applications.mobilenet_v2 import preprocess_input, decode_predictions
    HAS_TENSORFLOW = True
except ImportError:
    HAS_TENSORFLOW = False

class ImageClassifier:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Classifier")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # Model variables
        self.model = None
        self.is_model_loaded = False
        self.is_loading_model = False
        self.prediction_history = []
        
        # UI variables
        self.current_image_path = None
        self.current_image = None
        self.current_image_display = None
        
        # Create UI
        self.create_menu()
        self.create_main_layout()
        
        # Check for TensorFlow
        if not HAS_TENSORFLOW:
            messagebox.showwarning(
                "Library Missing", 
                "TensorFlow is not installed. Please install TensorFlow to use the image classification features.\n\n"
                "You can install it with: pip install tensorflow"
            )
        else:
            # Load model in background
            self.load_model_async()
        
        # Load prediction history
        self.load_history()
    
    def create_menu(self):
        menu_bar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Open Image", command=self.open_image)
        file_menu.add_command(label="Save Predictions", command=self.save_history)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menu_bar.add_cascade(label="File", menu=file_menu)
        
        # Model menu
        model_menu = tk.Menu(menu_bar, tearoff=0)
        model_menu.add_command(label="Load Model", command=self.load_model_async)
        model_menu.add_command(label="Model Info", command=self.show_model_info)
        menu_bar.add_cascade(label="Model", menu=model_menu)
        
        # Help menu
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="Help", command=self.show_help)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menu_bar)
    
    def create_main_layout(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create a PanedWindow for resizable sections
        paned_window = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True)
        
        # Left panel for image display
        self.left_panel = ttk.Frame(paned_window, width=600)
        paned_window.add(self.left_panel, weight=3)
        
        # Right panel for predictions and controls
        self.right_panel = ttk.Frame(paned_window, width=300)
        paned_window.add(self.right_panel, weight=1)
        
        # Create the components for each panel
        self.create_left_panel()
        self.create_right_panel()
    
    def create_left_panel(self):
        # Image display section
        image_frame = ttk.LabelFrame(self.left_panel, text="Image", padding="10")
        image_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Canvas for image display
        self.image_canvas = tk.Canvas(image_frame, bg="white")
        self.image_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Initial message
        self.canvas_text = self.image_canvas.create_text(
            300, 200, 
            text="Open an image to classify", 
            font=("Arial", 14)
        )
        
        # Controls frame
        controls_frame = ttk.Frame(self.left_panel)
        controls_frame.pack(fill=tk.X, pady=5)
        
        # Open image button
        open_button = ttk.Button(controls_frame, text="Open Image", command=self.open_image)
        open_button.pack(side=tk.LEFT, padx=5)
        
        # Classify button
        self.classify_button = ttk.Button(controls_frame, text="Classify Image", command=self.classify_image)
        self.classify_button.pack(side=tk.LEFT, padx=5)
        self.classify_button.config(state=tk.DISABLED)
        
        # Save results button
        save_button = ttk.Button(controls_frame, text="Save Results", command=self.save_results)
        save_button.pack(side=tk.LEFT, padx=5)
    
    def create_right_panel(self):
        # Prediction section
        prediction_frame = ttk.LabelFrame(self.right_panel, text="Predictions", padding="10")
        prediction_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Prediction results
        self.prediction_text = tk.Text(prediction_frame, wrap=tk.WORD, width=30, height=15)
        self.prediction_text.pack(fill=tk.BOTH, expand=True)
        self.prediction_text.config(state=tk.DISABLED)
        
        # Model status
        status_frame = ttk.LabelFrame(self.right_panel, text="Model Status", padding="10")
        status_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.status_var = tk.StringVar(value="Model not loaded")
        status_label = ttk.Label(status_frame, textvariable=self.status_var)
        status_label.pack(fill=tk.X)
        
        self.progress_bar = ttk.Progressbar(status_frame, mode="indeterminate")
        
        # History section
        history_frame = ttk.LabelFrame(self.right_panel, text="Prediction History", padding="10")
        history_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(history_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # History list
        self.history_list = tk.Listbox(history_frame, yscrollcommand=scrollbar.set)
        self.history_list.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.history_list.yview)
        
        # Bind selection event
        self.history_list.bind("<<ListboxSelect>>", self.on_history_select)
        
        # Clear history button
        clear_button = ttk.Button(history_frame, text="Clear History", command=self.clear_history)
        clear_button.pack(fill=tk.X, pady=(5, 0))
    
    def open_image(self):
        """Open an image file"""
        file_types = [
            ("Image files", "*.jpg *.jpeg *.png *.bmp *.gif"),
            ("All files", "*.*")
        ]
        
        file_path = filedialog.askopenfilename(
            title="Open Image",
            filetypes=file_types
        )
        
        if not file_path:
            return
        
        try:
            # Open and display the image
            self.load_image(file_path)
            
            # Enable classify button if model is loaded
            if self.is_model_loaded:
                self.classify_button.config(state=tk.NORMAL)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open image: {str(e)}")
    
    def load_image(self, file_path):
        """Load and display an image"""
        # Open image with PIL
        image = Image.open(file_path)
        
        # Store the image path and original image
        self.current_image_path = file_path
        self.current_image = image
        
        # Resize image to fit canvas while maintaining aspect ratio
        canvas_width = self.image_canvas.winfo_width()
        canvas_height = self.image_canvas.winfo_height()
        
        # Use default size if canvas is not yet drawn
        if canvas_width <= 1:
            canvas_width = 600
        if canvas_height <= 1:
            canvas_height = 400
        
        # Calculate new dimensions
        img_width, img_height = image.size
        ratio = min(canvas_width / img_width, canvas_height / img_height)
        new_width = int(img_width * ratio)
        new_height = int(img_height * ratio)
        
        # Resize image
        resized_image = image.resize((new_width, new_height), Image.LANCZOS)
        
        # Convert to PhotoImage
        photo = ImageTk.PhotoImage(resized_image)
        
        # Clear canvas
        self.image_canvas.delete("all")
        
        # Display image
        self.image_canvas.create_image(canvas_width // 2, canvas_height // 2, image=photo)
        self.current_image_display = photo  # Keep a reference to prevent garbage collection
        
        # Update window title
        self.root.title(f"Image Classifier - {os.path.basename(file_path)}")
    
    def load_model_async(self):
        """Load the model in a background thread"""
        if not HAS_TENSORFLOW:
            self.status_var.set("TensorFlow not installed")
            return
        
        if self.is_loading_model:
            return
        
        self.is_loading_model = True
        self.status_var.set("Loading model...")
        self.progress_bar.pack(fill=tk.X, pady=(5, 0))
        self.progress_bar.start()
        
        # Start loading thread
        thread = threading.Thread(target=self.load_model)
        thread.daemon = True
        thread.start()
    
    def load_model(self):
        """Load the MobileNetV2 model"""
        try:
            # Load pre-trained MobileNetV2 model
            self.model = MobileNetV2(weights='imagenet')
            self.is_model_loaded = True
            
            # Update UI in main thread
            self.root.after(0, self.on_model_loaded)
        except Exception as e:
            # Update UI in main thread
            self.root.after(0, lambda: self.on_model_load_error(str(e)))
    
    def on_model_loaded(self):
        """Called when model is successfully loaded"""
        self.status_var.set("Model loaded: MobileNetV2")
        self.progress_bar.stop()
        self.progress_bar.pack_forget()
        self.is_loading_model = False
        
        # Enable classify button if an image is loaded
        if self.current_image:
            self.classify_button.config(state=tk.NORMAL)
    
    def on_model_load_error(self, error_message):
        """Called when model loading fails"""
        self.status_var.set(f"Error loading model")
        self.progress_bar.stop()
        self.progress_bar.pack_forget()
        self.is_loading_model = False
        messagebox.showerror("Error", f"Failed to load model: {error_message}")
    
    def classify_image(self):
        """Classify the current image"""
        if not self.current_image or not self.is_model_loaded:
            return
        
        try:
            # Prepare image for model
            img = self.current_image.resize((224, 224))
            img_array = np.array(img)
            
            # Handle grayscale images
            if len(img_array.shape) == 2:
                img_array = np.stack((img_array,) * 3, axis=-1)
            
            # Handle RGBA images
            if img_array.shape[2] == 4:
                img_array = img_array[:, :, :3]
            
            # Preprocess image
            img_array = np.expand_dims(img_array, axis=0)
            img_array = preprocess_input(img_array)
            
            # Make prediction
            predictions = self.model.predict(img_array)
            results = decode_predictions(predictions, top=5)[0]
            
            # Format results
            formatted_results = []
            for i, (imagenet_id, label, score) in enumerate(results):
                formatted_results.append(f"{i+1}. {label.title()}: {score*100:.2f}%")
            
            # Display results
            self.prediction_text.config(state=tk.NORMAL)
            self.prediction_text.delete("1.0", tk.END)
            self.prediction_text.insert(tk.END, "Top Predictions:\n\n")
            self.prediction_text.insert(tk.END, "\n".join(formatted_results))
            self.prediction_text.config(state=tk.DISABLED)
            
            # Add to history
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            filename = os.path.basename(self.current_image_path)
            top_prediction = results[0][1].title()
            confidence = results[0][2] * 100
            
            history_item = {
                "timestamp": timestamp,
                "filename": filename,
                "filepath": self.current_image_path,
                "top_prediction": top_prediction,
                "confidence": confidence,
                "all_predictions": [(label, score) for _, label, score in results]
            }
            
            self.prediction_history.append(history_item)
            self.update_history_list()
            
        except Exception as e:
            messagebox.showerror("Error", f"Classification failed: {str(e)}")
    
    def update_history_list(self):
        """Update the history listbox"""
        self.history_list.delete(0, tk.END)
        
        for item in reversed(self.prediction_history):
            confidence = item["confidence"]
            display_text = f"{item['filename']} - {item['top_prediction']} ({confidence:.2f}%)"
            self.history_list.insert(tk.END, display_text)
    
    def on_history_select(self, event):
        """Handle selection in history list"""
        selection = self.history_list.curselection()
        if not selection:
            return
        
        # Get the selected history item (in reverse order)
        index = len(self.prediction_history) - 1 - selection[0]
        item = self.prediction_history[index]
        
        # Load the image if it still exists
        if os.path.exists(item["filepath"]):
            self.load_image(item["filepath"])
            
            # Display the predictions
            self.prediction_text.config(state=tk.NORMAL)
            self.prediction_text.delete("1.0", tk.END)
            self.prediction_text.insert(tk.END, f"Predictions for {item['filename']}:\n\n")
            
            for i, (label, score) in enumerate(item["all_predictions"]):
                self.prediction_text.insert(tk.END, f"{i+1}. {label.title()}: {score*100:.2f}%\n")
            
            self.prediction_text.config(state=tk.DISABLED)
        else:
            messagebox.showwarning("File Not Found", "The image file no longer exists.")
    
    def clear_history(self):
        """Clear prediction history"""
        if messagebox.askyesno("Confirm", "Are you sure you want to clear the prediction history?"):
            self.prediction_history = []
            self.update_history_list()
    
    def save_results(self):
        """Save current prediction results"""
        if not self.current_image_path or not self.prediction_history:
            messagebox.showinfo("Info", "No predictions to save")
            return
        
        file_types = [
            ("Text files", "*.txt"),
            ("All files", "*.*")
        ]
        
        file_path = filedialog.asksaveasfilename(
            title="Save Results",
            filetypes=file_types,
            defaultextension=".txt"
        )
        
        if not file_path:
            return
        
        try:
            # Get the most recent prediction for the current image
            current_predictions = None
            for item in reversed(self.prediction_history):
                if item["filepath"] == self.current_image_path:
                    current_predictions = item
                    break
            
            if not current_predictions:
                messagebox.showinfo("Info", "No predictions found for this image")
                return
            
            with open(file_path, "w") as f:
                f.write(f"Image Classification Results\n")
                f.write(f"=========================\n\n")
                f.write(f"Image: {current_predictions['filename']}\n")
                f.write(f"Date: {current_predictions['timestamp']}\n")
                f.write(f"Model: MobileNetV2\n\n")
                f.write(f"Top Predictions:\n")
                
                for i, (label, score) in enumerate(current_predictions["all_predictions"]):
                    f.write(f"{i+1}. {label.title()}: {score*100:.2f}%\n")
            
            messagebox.showinfo("Success", f"Results saved to {file_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save results: {str(e)}")
    
    def save_history(self):
        """Save prediction history to JSON file"""
        if not self.prediction_history:
            messagebox.showinfo("Info", "No prediction history to save")
            return
        
        file_types = [
            ("JSON files", "*.json"),
            ("All files", "*.*")
        ]
        
        file_path = filedialog.asksaveasfilename(
            title="Save History",
            filetypes=file_types,
            defaultextension=".json"
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, "w") as f:
                json.dump(self.prediction_history, f, indent=2)
            
            messagebox.showinfo("Success", f"History saved to {file_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save history: {str(e)}")
    
    def load_history(self):
        """Load prediction history from JSON file"""
        history_file = "image_classifier_history.json"
        
        if os.path.exists(history_file):
            try:
                with open(history_file, "r") as f:
                    self.prediction_history = json.load(f)
                self.update_history_list()
            except:
                # If error loading history, start with empty history
                self.prediction_history = []
    
    def show_model_info(self):
        """Show information about the loaded model"""
        if not self.is_model_loaded:
            messagebox.showinfo("Model Info", "No model is currently loaded.")
            return
        
        info_text = """Model Information:
        
Name: MobileNetV2
Type: Convolutional Neural Network
Purpose: Image Classification
Classes: 1000 ImageNet categories
Input Size: 224x224 pixels
        
MobileNetV2 is a lightweight convolutional neural network architecture designed for mobile and embedded vision applications. It uses inverted residuals with linear bottlenecks to achieve high accuracy while maintaining efficiency.
        
The model is pre-trained on the ImageNet dataset, which contains over a million images across 1000 categories.
"""
        
        messagebox.showinfo("Model Info", info_text)
    
    def show_about(self):
        """Show about dialog"""
        about_text = """Image Classifier
Version 1.0

An application for classifying images using deep learning.
Created with Python, TensorFlow, and Tkinter.

© 2023 Python Beginner Project
"""
        messagebox.showinfo("About", about_text)
    
    def show_help(self):
        """Show help dialog"""
        help_text = """How to use the Image Classifier:

1. Wait for the model to load (this may take a few moments)
2. Click "Open Image" to select an image file
3. Click "Classify Image" to analyze the image
4. View the top predictions in the right panel
5. Previous predictions are saved in the history list
6. Click on a history item to view those predictions again
7. Use "Save Results" to save the current predictions to a text file

Supported image formats: JPEG, PNG, BMP, GIF

Note: This application requires TensorFlow to be installed.
You can install it with: pip install tensorflow
"""
        
        help_window = tk.Toplevel(self.root)
        help_window.title("Help")
        help_window.geometry("600x400")
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


def main():
    # Create root window
    root = tk.Tk()
    
    # Create application
    app = ImageClassifier(root)
    
    # Start main loop
    root.mainloop()
    
    # Save history on exit
    if hasattr(app, 'prediction_history') and app.prediction_history:
        try:
            with open("image_classifier_history.json", "w") as f:
                json.dump(app.prediction_history, f, indent=2)
        except:
            pass


if __name__ == "__main__":
    main() 