#!/usr/bin/env python3
"""
Test file để kiểm tra chức năng Expression Dialog
"""

import tkinter as tk
from tkinter import messagebox

def test_expression_dialog():
    """Test dialog"""
    root = tk.Tk()
    root.title("Test Expression Dialog")
    root.geometry("400x200")
    
    # Tạo nút để mở dialog
    def open_dialog():
        messagebox.showinfo("Test", "Nút Expression đã được nhấn!\n\nTrong ứng dụng chính:\n1. Nhấn nút '📝 Expression' màu xanh trên toolbar\n2. Hoặc dùng menu Tools > Expression to Circuit\n3. Hoặc nhấn Ctrl+E\n\nTrong dialog sẽ có nút 'Generate Circuit' màu xanh")
    
    tk.Label(root, text="Kiểm tra chức năng Expression", 
             font=("Arial", 14, "bold")).pack(pady=20)
    
    tk.Button(root, text="📝 Expression Test", 
              bg="#4CAF50", fg="white", font=("Arial", 12, "bold"),
              command=open_dialog, width=20, height=2).pack(pady=20)
    
    tk.Label(root, text="Trong ứng dụng chính, nút này sẽ mở dialog\nvới nút 'Generate Circuit' để tạo mạch", 
             font=("Arial", 10)).pack(pady=10)
    
    root.mainloop()

if __name__ == "__main__":
    test_expression_dialog() 