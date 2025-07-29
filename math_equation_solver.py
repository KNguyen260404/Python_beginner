import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import sympy as sp
from sympy.parsing.sympy_parser import parse_expr
from sympy.solvers import solve
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class MathEquationSolver:
    def __init__(self, root):
        self.root = root
        self.root.title("Math Equation Solver - Giải Phương Trình")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Set language (default to Vietnamese)
        self.language = "vi"
        
        # Current equation and solutions
        self.current_equation = None
        self.current_solutions = None
        
        self.create_widgets()
        
    def create_widgets(self):
        # Title
        title_label = tk.Label(self.root, text="Math Equation Solver - Giải Phương Trình", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Left frame for input
        input_frame = ttk.LabelFrame(main_frame, text="Nhập phương trình")
        input_frame.pack(side=tk.TOP, fill="x", padx=10, pady=5)
        
        # Equation input
        equation_label = ttk.Label(input_frame, text="Nhập phương trình (sử dụng x làm biến):", font=("Arial", 12))
        equation_label.grid(row=0, column=0, sticky="w", pady=5, padx=5)
        
        self.equation_var = tk.StringVar()
        self.equation_entry = ttk.Entry(input_frame, textvariable=self.equation_var, font=("Arial", 12), width=50)
        self.equation_entry.grid(row=1, column=0, pady=5, padx=5, sticky="we")
        self.equation_entry.insert(0, "x^2 - 5*x + 6 = 0")
        
        # Example label
        example_label = ttk.Label(input_frame, text="Ví dụ: x^2 - 5*x + 6 = 0, 2*x + 3 = 7, x^3 - 6*x^2 + 11*x - 6 = 0", 
                                 font=("Arial", 10), foreground="gray")
        example_label.grid(row=2, column=0, sticky="w", pady=5, padx=5)
        
        # Buttons frame
        buttons_frame = ttk.Frame(input_frame)
        buttons_frame.grid(row=3, column=0, pady=10, padx=5, sticky="w")
        
        # Solve button
        solve_button = ttk.Button(buttons_frame, text="Giải phương trình", command=self.solve_equation)
        solve_button.grid(row=0, column=0, padx=5)
        
        # Clear button
        clear_button = ttk.Button(buttons_frame, text="Xóa", command=self.clear_input)
        clear_button.grid(row=0, column=1, padx=5)
        
        # Graph button
        graph_button = ttk.Button(buttons_frame, text="Vẽ đồ thị", command=self.plot_equation)
        graph_button.grid(row=0, column=2, padx=5)
        
        # Example buttons
        example1_button = ttk.Button(buttons_frame, text="Bậc 1", 
                                    command=lambda: self.set_example("2*x + 3 = 7"))
        example1_button.grid(row=0, column=3, padx=5)
        
        example2_button = ttk.Button(buttons_frame, text="Bậc 2", 
                                    command=lambda: self.set_example("x^2 - 5*x + 6 = 0"))
        example2_button.grid(row=0, column=4, padx=5)
        
        example3_button = ttk.Button(buttons_frame, text="Bậc 3", 
                                    command=lambda: self.set_example("x^3 - 6*x^2 + 11*x - 6 = 0"))
        example3_button.grid(row=0, column=5, padx=5)
        
        example4_button = ttk.Button(buttons_frame, text="Bậc 4", 
                                    command=lambda: self.set_example("x^4 - 1 = 0"))
        example4_button.grid(row=0, column=6, padx=5)
        
        # Create notebook for results and graph
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Result frame
        result_frame = ttk.Frame(self.notebook)
        self.notebook.add(result_frame, text="Kết quả")
        
        # Result text
        self.result_text = tk.Text(result_frame, height=20, width=80, font=("Courier New", 12))
        self.result_text.pack(side=tk.LEFT, fill="both", expand=True, pady=5, padx=5)
        
        # Scrollbar for result text
        scrollbar = ttk.Scrollbar(result_frame, command=self.result_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_text.config(yscrollcommand=scrollbar.set)
        
        # Graph frame
        graph_frame = ttk.Frame(self.notebook)
        self.notebook.add(graph_frame, text="Đồ thị")
        
        # Create matplotlib figure
        self.figure = plt.Figure(figsize=(6, 4), dpi=100)
        self.plot = self.figure.add_subplot(111)
        
        # Create canvas for matplotlib figure
        self.canvas = FigureCanvasTkAgg(self.figure, graph_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def set_example(self, example):
        """Set an example equation in the entry field"""
        self.equation_var.set(example)
        
    def clear_input(self):
        """Clear the input field"""
        self.equation_var.set("")
        self.result_text.delete(1.0, tk.END)
        self.plot.clear()
        self.canvas.draw()
        
    def solve_equation(self):
        try:
            equation_str = self.equation_var.get().strip()
            
            if not equation_str:
                messagebox.showwarning("Cảnh báo", "Vui lòng nhập phương trình!")
                return
            
            # Parse the equation
            if "=" in equation_str:
                left_side, right_side = equation_str.split("=")
                equation = parse_expr(left_side) - parse_expr(right_side)
            else:
                equation = parse_expr(equation_str)
            
            # Store the current equation for plotting
            self.current_equation = equation
            
            # Define the variable
            x = sp.Symbol('x')
            
            # Solve the equation
            solutions = solve(equation, x)
            self.current_solutions = solutions
            
            # Display the results
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"Phương trình: {sp.pretty(equation)} = 0\n\n")
            
            degree = sp.degree(equation, x)
            self.result_text.insert(tk.END, f"Bậc của phương trình: {degree}\n\n")
            self.result_text.insert(tk.END, f"Số nghiệm: {len(solutions)}\n\n")
            
            for i, sol in enumerate(solutions, 1):
                self.result_text.insert(tk.END, f"x{i} = {sol}\n")
                
                # Calculate numerical approximation if solution is complex
                if isinstance(sol, sp.Expr) and not sol.is_real:
                    numerical = complex(sol.evalf())
                    self.result_text.insert(tk.END, f"   ≈ {numerical.real:.6f} + {numerical.imag:.6f}i\n")
                # Calculate numerical approximation if solution is irrational
                elif isinstance(sol, sp.Expr):
                    numerical = float(sol.evalf())
                    self.result_text.insert(tk.END, f"   ≈ {numerical:.6f}\n")
            
            # Show step-by-step solution based on equation degree
            if degree == 1:
                self.show_linear_steps(equation, x)
            elif degree == 2:
                self.show_quadratic_steps(equation, x)
            elif degree == 3:
                self.show_cubic_steps(equation, x)
            elif degree > 3 and degree <= 6:
                self.show_higher_degree_steps(equation, x, degree)
                
            # Switch to results tab
            self.notebook.select(0)
                
        except Exception as e:
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"Lỗi: {str(e)}\n\n")
            self.result_text.insert(tk.END, "Vui lòng kiểm tra định dạng phương trình và thử lại.")
    
    def plot_equation(self):
        """Plot the current equation and its roots"""
        try:
            if self.current_equation is None:
                self.solve_equation()
                if self.current_equation is None:  # If solve_equation failed
                    return
            
            x = sp.Symbol('x')
            equation = self.current_equation
            solutions = self.current_solutions
            
            # Convert sympy expression to numpy function for plotting
            f = sp.lambdify(x, equation, 'numpy')
            
            # Clear previous plot
            self.plot.clear()
            
            # Find real solutions for plotting
            real_solutions = [float(sol.evalf()) for sol in solutions if sol.is_real]
            
            # Determine x range for plotting
            if real_solutions:
                # If there are real solutions, center the plot around them
                min_sol = min(real_solutions)
                max_sol = max(real_solutions)
                padding = max(5, (max_sol - min_sol) * 0.5)
                x_min = min_sol - padding
                x_max = max_sol + padding
            else:
                # Default range if no real solutions
                x_min, x_max = -10, 10
            
            # Generate x values
            x_vals = np.linspace(x_min, x_max, 1000)
            
            try:
                # Calculate y values
                y_vals = f(x_vals)
                
                # Plot the function
                self.plot.plot(x_vals, y_vals, 'b-', label=f'f(x) = {sp.pretty(equation)}')
                
                # Plot x-axis
                self.plot.axhline(y=0, color='k', linestyle='-', alpha=0.3)
                
                # Plot y-axis
                self.plot.axvline(x=0, color='k', linestyle='-', alpha=0.3)
                
                # Mark real roots
                for sol in real_solutions:
                    self.plot.plot(sol, 0, 'ro', markersize=6)
                    self.plot.annotate(f'x = {sol:.4f}', 
                                      xy=(sol, 0), 
                                      xytext=(sol, f(sol+0.1) if abs(f(sol+0.1)) < 10 else 1),
                                      arrowprops=dict(arrowstyle="->", connectionstyle="arc3"))
                
                # Set labels and title
                self.plot.set_xlabel('x')
                self.plot.set_ylabel('f(x)')
                self.plot.set_title(f'Đồ thị hàm số f(x) = {sp.pretty(equation)}')
                self.plot.grid(True, alpha=0.3)
                self.plot.legend()
                
                # Update the canvas
                self.canvas.draw()
                
                # Switch to graph tab
                self.notebook.select(1)
                
            except Exception as e:
                messagebox.showerror("Lỗi vẽ đồ thị", f"Không thể vẽ đồ thị: {str(e)}")
                
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi: {str(e)}")
    
    def show_linear_steps(self, equation, x):
        """Show step-by-step solution for linear equations (ax + b = 0)"""
        self.result_text.insert(tk.END, "\nCác bước giải:\n")
        
        # Get coefficients
        expanded = sp.expand(equation)
        a = expanded.coeff(x, 1)
        b = expanded.subs(x, 0)
        
        self.result_text.insert(tk.END, f"1. Xác định dạng phương trình: {a}x + {b} = 0\n")
        self.result_text.insert(tk.END, f"2. Trừ {b} ở cả hai vế: {a}x = {-b}\n")
        self.result_text.insert(tk.END, f"3. Chia cả hai vế cho {a}: x = {-b/a}\n")
    
    def show_quadratic_steps(self, equation, x):
        """Show step-by-step solution for quadratic equations (ax^2 + bx + c = 0)"""
        self.result_text.insert(tk.END, "\nCác bước giải:\n")
        
        # Get coefficients
        expanded = sp.expand(equation)
        a = expanded.coeff(x, 2)
        b = expanded.coeff(x, 1)
        c = expanded.subs(x, 0)
        
        self.result_text.insert(tk.END, f"1. Xác định dạng phương trình: {a}x² + {b}x + {c} = 0\n")
        
        # Check if factorizable easily
        factors = sp.factor(expanded)
        if factors != expanded:
            self.result_text.insert(tk.END, f"2. Phân tích thừa số: {factors} = 0\n")
            self.result_text.insert(tk.END, f"3. Đặt từng thừa số bằng 0 và giải\n")
        else:
            # Use quadratic formula
            self.result_text.insert(tk.END, f"2. Sử dụng công thức nghiệm bậc hai: x = (-b ± √(b² - 4ac)) / (2a)\n")
            self.result_text.insert(tk.END, f"3. Thay a={a}, b={b}, c={c}\n")
            
            discriminant = b**2 - 4*a*c
            self.result_text.insert(tk.END, f"4. Tính delta: b² - 4ac = {discriminant}\n")
            
            if discriminant > 0:
                self.result_text.insert(tk.END, f"5. Có hai nghiệm thực phân biệt:\n")
                self.result_text.insert(tk.END, f"   x₁ = ({-b} + √{discriminant}) / {2*a} = {(-b + sp.sqrt(discriminant)) / (2*a)}\n")
                self.result_text.insert(tk.END, f"   x₂ = ({-b} - √{discriminant}) / {2*a} = {(-b - sp.sqrt(discriminant)) / (2*a)}\n")
            elif discriminant == 0:
                self.result_text.insert(tk.END, f"5. Có một nghiệm kép:\n")
                self.result_text.insert(tk.END, f"   x = {-b} / {2*a} = {-b / (2*a)}\n")
            else:
                self.result_text.insert(tk.END, f"5. Có hai nghiệm phức:\n")
                self.result_text.insert(tk.END, f"   x₁ = ({-b} + √{discriminant}) / {2*a}\n")
                self.result_text.insert(tk.END, f"   x₂ = ({-b} - √{discriminant}) / {2*a}\n")

    def show_cubic_steps(self, equation, x):
        """Show step-by-step solution for cubic equations (ax^3 + bx^2 + cx + d = 0)"""
        self.result_text.insert(tk.END, "\nCác bước giải:\n")
        
        # Get coefficients
        expanded = sp.expand(equation)
        a = expanded.coeff(x, 3)
        b = expanded.coeff(x, 2)
        c = expanded.coeff(x, 1)
        d = expanded.subs(x, 0)
        
        self.result_text.insert(tk.END, f"1. Xác định dạng phương trình: {a}x³ + {b}x² + {c}x + {d} = 0\n")
        
        # Check if factorizable
        factors = sp.factor(expanded)
        if factors != expanded:
            self.result_text.insert(tk.END, f"2. Phân tích thừa số: {factors} = 0\n")
            self.result_text.insert(tk.END, f"3. Đặt từng thừa số bằng 0 và giải\n")
        else:
            # Try to find a rational root
            self.result_text.insert(tk.END, f"2. Sử dụng phương pháp tìm nghiệm hữu tỷ\n")
            self.result_text.insert(tk.END, f"3. Sau khi tìm được một nghiệm, phân tích phương trình thành tích của một nhân tử bậc 1 và một nhân tử bậc 2\n")
            self.result_text.insert(tk.END, f"4. Giải phương trình bậc 2 còn lại\n")
            
            # Show the general approach for cubic equations
            self.result_text.insert(tk.END, f"\nGhi chú: Phương trình bậc 3 tổng quát có thể giải bằng công thức Cardano-Tartaglia,\n")
            self.result_text.insert(tk.END, f"nhưng công thức phức tạp. Kết quả cuối cùng được tính toán bằng thư viện SymPy.\n")
            
    def show_higher_degree_steps(self, equation, x, degree):
        """Show general approach for higher degree equations"""
        self.result_text.insert(tk.END, f"\nCác bước giải phương trình bậc {degree}:\n")
        
        # Check if factorizable
        factors = sp.factor(equation)
        if factors != equation:
            self.result_text.insert(tk.END, f"1. Phân tích thừa số: {factors} = 0\n")
            self.result_text.insert(tk.END, f"2. Đặt từng thừa số bằng 0 và giải\n")
        else:
            # Special cases
            if degree == 4:
                self.result_text.insert(tk.END, f"1. Phương trình bậc 4 có thể giải bằng phương pháp Ferrari hoặc phân tích thành thừa số\n")
                self.result_text.insert(tk.END, f"2. Trong một số trường hợp, có thể đặt t = x² để chuyển về phương trình bậc 2\n")
            elif degree == 5:
                self.result_text.insert(tk.END, f"1. Phương trình bậc 5 không có công thức nghiệm tổng quát\n")
                self.result_text.insert(tk.END, f"2. Giải bằng phương pháp số hoặc tìm nghiệm hữu tỷ và phân tích thừa số\n")
            elif degree == 6:
                self.result_text.insert(tk.END, f"1. Phương trình bậc 6 không có công thức nghiệm tổng quát\n")
                self.result_text.insert(tk.END, f"2. Trong một số trường hợp, có thể đặt t = x² hoặc t = x³ để chuyển về phương trình bậc thấp hơn\n")
            
            self.result_text.insert(tk.END, f"\nGhi chú: Phương trình bậc cao (>4) không có công thức nghiệm tổng quát.\n")
            self.result_text.insert(tk.END, f"Kết quả được tính toán bằng phương pháp số thông qua thư viện SymPy.\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = MathEquationSolver(root)
    root.mainloop() 