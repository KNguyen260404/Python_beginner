import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import sympy as sp
from sympy.parsing.sympy_parser import parse_expr
from sympy.solvers import solve
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random

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
        
        # Create notebook for main tabs
        self.main_notebook = ttk.Notebook(self.root)
        self.main_notebook.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Create equation solver tab
        self.equation_frame = ttk.Frame(self.main_notebook)
        self.main_notebook.add(self.equation_frame, text="Giải phương trình")
        
        # Create calculus tab
        self.calculus_frame = ttk.Frame(self.main_notebook)
        self.main_notebook.add(self.calculus_frame, text="Tích phân & Nguyên hàm")
        
        # Create number conversion tab
        self.conversion_frame = ttk.Frame(self.main_notebook)
        self.main_notebook.add(self.conversion_frame, text="Chuyển đổi hệ cơ số")
        
        # Create matrix calculation tab
        self.matrix_frame = ttk.Frame(self.main_notebook)
        self.main_notebook.add(self.matrix_frame, text="Tính toán ma trận")
        
        # Create function plotter tab
        self.plotter_frame = ttk.Frame(self.main_notebook)
        self.main_notebook.add(self.plotter_frame, text="Vẽ đồ thị hàm số")
        
        # Create widgets for equation solver tab
        self.create_equation_widgets()
        
        # Create widgets for calculus tab
        self.create_calculus_widgets()
        
        # Create widgets for number conversion tab
        self.create_conversion_widgets()
        
        # Create widgets for matrix calculation tab
        self.create_matrix_widgets()
        
        # Create widgets for function plotter tab
        self.create_plotter_widgets()
        
    def create_equation_widgets(self):
        # Title
        title_label = tk.Label(self.equation_frame, text="Giải Phương Trình", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Main frame
        main_frame = ttk.Frame(self.equation_frame)
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
        self.equation_notebook = ttk.Notebook(main_frame)
        self.equation_notebook.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Result frame
        result_frame = ttk.Frame(self.equation_notebook)
        self.equation_notebook.add(result_frame, text="Kết quả")
        
        # Result text
        self.result_text = tk.Text(result_frame, height=20, width=80, font=("Courier New", 12))
        self.result_text.pack(side=tk.LEFT, fill="both", expand=True, pady=5, padx=5)
        
        # Scrollbar for result text
        scrollbar = ttk.Scrollbar(result_frame, command=self.result_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_text.config(yscrollcommand=scrollbar.set)
        
        # Graph frame
        graph_frame = ttk.Frame(self.equation_notebook)
        self.equation_notebook.add(graph_frame, text="Đồ thị")
        
        # Create matplotlib figure
        self.figure = plt.Figure(figsize=(6, 4), dpi=100)
        self.plot = self.figure.add_subplot(111)
        
        # Create canvas for matplotlib figure
        self.canvas = FigureCanvasTkAgg(self.figure, graph_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def create_calculus_widgets(self):
        # Title
        title_label = tk.Label(self.calculus_frame, text="Tích phân & Nguyên hàm", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Main frame
        main_frame = ttk.Frame(self.calculus_frame)
        main_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Input frame
        input_frame = ttk.LabelFrame(main_frame, text="Nhập biểu thức")
        input_frame.pack(side=tk.TOP, fill="x", padx=10, pady=5)
        
        # Function input
        function_label = ttk.Label(input_frame, text="Nhập hàm số f(x):", font=("Arial", 12))
        function_label.grid(row=0, column=0, sticky="w", pady=5, padx=5)
        
        self.function_var = tk.StringVar()
        self.function_entry = ttk.Entry(input_frame, textvariable=self.function_var, font=("Arial", 12), width=50)
        self.function_entry.grid(row=0, column=1, pady=5, padx=5, sticky="we")
        self.function_entry.insert(0, "x^2 + 2*x + 1")
        
        # Example label
        example_label = ttk.Label(input_frame, text="Ví dụ: x^2 + 2*x + 1, sin(x), e^x, ln(x), 1/x", 
                                 font=("Arial", 10), foreground="gray")
        example_label.grid(row=1, column=0, columnspan=2, sticky="w", pady=5, padx=5)
        
        # Integration limits frame
        limits_frame = ttk.Frame(input_frame)
        limits_frame.grid(row=2, column=0, columnspan=2, sticky="w", pady=5, padx=5)
        
        # Lower limit
        lower_label = ttk.Label(limits_frame, text="Giới hạn dưới a:", font=("Arial", 12))
        lower_label.grid(row=0, column=0, sticky="w", pady=5, padx=5)
        
        self.lower_var = tk.StringVar()
        self.lower_entry = ttk.Entry(limits_frame, textvariable=self.lower_var, font=("Arial", 12), width=10)
        self.lower_entry.grid(row=0, column=1, pady=5, padx=5)
        self.lower_entry.insert(0, "0")
        
        # Upper limit
        upper_label = ttk.Label(limits_frame, text="Giới hạn trên b:", font=("Arial", 12))
        upper_label.grid(row=0, column=2, sticky="w", pady=5, padx=5)
        
        self.upper_var = tk.StringVar()
        self.upper_entry = ttk.Entry(limits_frame, textvariable=self.upper_var, font=("Arial", 12), width=10)
        self.upper_entry.grid(row=0, column=3, pady=5, padx=5)
        self.upper_entry.insert(0, "1")
        
        # Variable label
        var_label = ttk.Label(limits_frame, text="Biến tích phân:", font=("Arial", 12))
        var_label.grid(row=0, column=4, sticky="w", pady=5, padx=5)
        
        self.var_var = tk.StringVar(value="x")
        self.var_entry = ttk.Entry(limits_frame, textvariable=self.var_var, font=("Arial", 12), width=5)
        self.var_entry.grid(row=0, column=5, pady=5, padx=5)
        
        # Buttons frame
        buttons_frame = ttk.Frame(input_frame)
        buttons_frame.grid(row=3, column=0, columnspan=2, pady=10, padx=5, sticky="w")
        
        # Calculate buttons
        antiderivative_button = ttk.Button(buttons_frame, text="Tìm nguyên hàm", command=self.find_antiderivative)
        antiderivative_button.grid(row=0, column=0, padx=5)
        
        definite_integral_button = ttk.Button(buttons_frame, text="Tính tích phân xác định", command=self.calculate_definite_integral)
        definite_integral_button.grid(row=0, column=1, padx=5)
        
        indefinite_integral_button = ttk.Button(buttons_frame, text="Tính tích phân bất định", command=self.calculate_indefinite_integral)
        indefinite_integral_button.grid(row=0, column=2, padx=5)
        
        plot_button = ttk.Button(buttons_frame, text="Vẽ đồ thị hàm số", command=self.plot_function)
        plot_button.grid(row=0, column=3, padx=5)
        
        clear_button = ttk.Button(buttons_frame, text="Xóa", command=self.clear_calculus)
        clear_button.grid(row=0, column=4, padx=5)
        
        # Example buttons
        example_frame = ttk.Frame(input_frame)
        example_frame.grid(row=4, column=0, columnspan=2, pady=5, padx=5, sticky="w")
        
        example1_button = ttk.Button(example_frame, text="x^2", 
                                   command=lambda: self.set_function_example("x^2"))
        example1_button.grid(row=0, column=0, padx=5)
        
        example2_button = ttk.Button(example_frame, text="sin(x)", 
                                   command=lambda: self.set_function_example("sin(x)"))
        example2_button.grid(row=0, column=1, padx=5)
        
        example3_button = ttk.Button(example_frame, text="e^x", 
                                   command=lambda: self.set_function_example("exp(x)"))
        example3_button.grid(row=0, column=2, padx=5)
        
        example4_button = ttk.Button(example_frame, text="1/x", 
                                   command=lambda: self.set_function_example("1/x"))
        example4_button.grid(row=0, column=3, padx=5)
        
        example5_button = ttk.Button(example_frame, text="ln(x)", 
                                   command=lambda: self.set_function_example("ln(x)"))
        example5_button.grid(row=0, column=4, padx=5)
        
        # Create notebook for results and graph
        self.calculus_notebook = ttk.Notebook(main_frame)
        self.calculus_notebook.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Result frame
        calculus_result_frame = ttk.Frame(self.calculus_notebook)
        self.calculus_notebook.add(calculus_result_frame, text="Kết quả")
        
        # Result text
        self.calculus_result_text = tk.Text(calculus_result_frame, height=20, width=80, font=("Courier New", 12))
        self.calculus_result_text.pack(side=tk.LEFT, fill="both", expand=True, pady=5, padx=5)
        
        # Scrollbar for result text
        calc_scrollbar = ttk.Scrollbar(calculus_result_frame, command=self.calculus_result_text.yview)
        calc_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.calculus_result_text.config(yscrollcommand=calc_scrollbar.set)
        
        # Graph frame
        calculus_graph_frame = ttk.Frame(self.calculus_notebook)
        self.calculus_notebook.add(calculus_graph_frame, text="Đồ thị")
        
        # Create matplotlib figure
        self.calculus_figure = plt.Figure(figsize=(6, 4), dpi=100)
        self.calculus_plot = self.calculus_figure.add_subplot(111)
        
        # Create canvas for matplotlib figure
        self.calculus_canvas = FigureCanvasTkAgg(self.calculus_figure, calculus_graph_frame)
        self.calculus_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def create_conversion_widgets(self):
        """Create widgets for number conversion tab"""
        # Title
        title_label = tk.Label(self.conversion_frame, text="Chuyển đổi hệ cơ số", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Main frame
        main_frame = ttk.Frame(self.conversion_frame)
        main_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Input frame
        input_frame = ttk.LabelFrame(main_frame, text="Nhập số cần chuyển đổi")
        input_frame.pack(side=tk.TOP, fill="x", padx=10, pady=5)
        
        # Number input
        number_label = ttk.Label(input_frame, text="Nhập số:", font=("Arial", 12))
        number_label.grid(row=0, column=0, sticky="w", pady=5, padx=5)
        
        self.number_var = tk.StringVar()
        self.number_entry = ttk.Entry(input_frame, textvariable=self.number_var, font=("Arial", 12), width=50)
        self.number_entry.grid(row=0, column=1, pady=5, padx=5, sticky="we")
        self.number_entry.insert(0, "1010")
        
        # Input base selection
        base_label = ttk.Label(input_frame, text="Hệ cơ số đầu vào:", font=("Arial", 12))
        base_label.grid(row=1, column=0, sticky="w", pady=5, padx=5)
        
        self.input_base_var = tk.StringVar(value="2")
        input_base_frame = ttk.Frame(input_frame)
        input_base_frame.grid(row=1, column=1, sticky="w", pady=5, padx=5)
        
        ttk.Radiobutton(input_base_frame, text="Nhị phân (2)", variable=self.input_base_var, value="2").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(input_base_frame, text="Bát phân (8)", variable=self.input_base_var, value="8").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(input_base_frame, text="Thập phân (10)", variable=self.input_base_var, value="10").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(input_base_frame, text="Thập lục phân (16)", variable=self.input_base_var, value="16").pack(side=tk.LEFT, padx=5)
        
        # Output base selection
        output_base_label = ttk.Label(input_frame, text="Chuyển sang hệ cơ số:", font=("Arial", 12))
        output_base_label.grid(row=2, column=0, sticky="w", pady=5, padx=5)
        
        self.output_base_var = tk.StringVar(value="10")
        output_base_frame = ttk.Frame(input_frame)
        output_base_frame.grid(row=2, column=1, sticky="w", pady=5, padx=5)
        
        ttk.Radiobutton(output_base_frame, text="Nhị phân (2)", variable=self.output_base_var, value="2").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(output_base_frame, text="Bát phân (8)", variable=self.output_base_var, value="8").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(output_base_frame, text="Thập phân (10)", variable=self.output_base_var, value="10").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(output_base_frame, text="Thập lục phân (16)", variable=self.output_base_var, value="16").pack(side=tk.LEFT, padx=5)
        
        # Buttons frame
        buttons_frame = ttk.Frame(input_frame)
        buttons_frame.grid(row=3, column=0, columnspan=2, pady=10, padx=5, sticky="w")
        
        # Convert button
        convert_button = ttk.Button(buttons_frame, text="Chuyển đổi", command=self.convert_number)
        convert_button.grid(row=0, column=0, padx=5)
        
        # Clear button
        clear_button = ttk.Button(buttons_frame, text="Xóa", command=self.clear_conversion)
        clear_button.grid(row=0, column=1, padx=5)
        
        # Example buttons
        example_binary_button = ttk.Button(buttons_frame, text="Ví dụ nhị phân", 
                                         command=lambda: self.set_conversion_example("1010", "2"))
        example_binary_button.grid(row=0, column=2, padx=5)
        
        example_decimal_button = ttk.Button(buttons_frame, text="Ví dụ thập phân", 
                                          command=lambda: self.set_conversion_example("255", "10"))
        example_decimal_button.grid(row=0, column=3, padx=5)
        
        example_hex_button = ttk.Button(buttons_frame, text="Ví dụ thập lục phân", 
                                       command=lambda: self.set_conversion_example("1A", "16"))
        example_hex_button.grid(row=0, column=4, padx=5)
        
        # Result frame
        result_frame = ttk.LabelFrame(main_frame, text="Kết quả chuyển đổi")
        result_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Result text
        self.conversion_result_text = tk.Text(result_frame, height=20, width=80, font=("Courier New", 12))
        self.conversion_result_text.pack(side=tk.LEFT, fill="both", expand=True, pady=5, padx=5)
        
        # Scrollbar for result text
        scrollbar = ttk.Scrollbar(result_frame, command=self.conversion_result_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.conversion_result_text.config(yscrollcommand=scrollbar.set)
        
        # Explanation frame
        explanation_frame = ttk.LabelFrame(main_frame, text="Giải thích")
        explanation_frame.pack(fill="x", padx=10, pady=5)
        
        # Explanation text
        explanation_text = (
            "Hệ nhị phân (cơ số 2): Sử dụng các chữ số 0, 1\n"
            "Hệ bát phân (cơ số 8): Sử dụng các chữ số 0-7\n"
            "Hệ thập phân (cơ số 10): Sử dụng các chữ số 0-9\n"
            "Hệ thập lục phân (cơ số 16): Sử dụng các chữ số 0-9 và chữ cái A-F (A=10, B=11, ..., F=15)\n\n"
            "Ví dụ:\n"
            "- Số nhị phân 1010 = 1×2³ + 0×2² + 1×2¹ + 0×2⁰ = 8 + 0 + 2 + 0 = 10 (thập phân)\n"
            "- Số thập phân 42 = 101010 (nhị phân) = 52 (bát phân) = 2A (thập lục phân)"
        )
        
        explanation_label = ttk.Label(explanation_frame, text=explanation_text, font=("Arial", 10), justify=tk.LEFT)
        explanation_label.pack(pady=5, padx=5, anchor="w")
    
    def create_matrix_widgets(self):
        """Create widgets for matrix calculation tab"""
        # Title
        title_label = tk.Label(self.matrix_frame, text="Tính toán ma trận", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Main frame
        main_frame = ttk.Frame(self.matrix_frame)
        main_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Create notebook for matrix operations
        self.matrix_notebook = ttk.Notebook(main_frame)
        self.matrix_notebook.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Create tab for single matrix operations
        self.single_matrix_frame = ttk.Frame(self.matrix_notebook)
        self.matrix_notebook.add(self.single_matrix_frame, text="Phép toán ma trận đơn")
        
        # Create tab for two matrix operations
        self.two_matrix_frame = ttk.Frame(self.matrix_notebook)
        self.matrix_notebook.add(self.two_matrix_frame, text="Phép toán hai ma trận")
        
        # Create tab for system of linear equations
        self.linear_system_frame = ttk.Frame(self.matrix_notebook)
        self.matrix_notebook.add(self.linear_system_frame, text="Hệ phương trình tuyến tính")
        
        # Create widgets for single matrix operations
        self.create_single_matrix_widgets()
        
        # Create widgets for two matrix operations
        self.create_two_matrix_widgets()
        
        # Create widgets for system of linear equations
        self.create_linear_system_widgets()
    
    def create_single_matrix_widgets(self):
        """Create widgets for single matrix operations"""
        # Input frame
        input_frame = ttk.LabelFrame(self.single_matrix_frame, text="Nhập ma trận")
        input_frame.pack(side=tk.TOP, fill="x", padx=10, pady=5)
        
        # Matrix input
        matrix_label = ttk.Label(input_frame, text="Nhập ma trận (mỗi hàng trên một dòng, các phần tử cách nhau bởi dấu cách):", font=("Arial", 12))
        matrix_label.grid(row=0, column=0, sticky="w", pady=5, padx=5)
        
        self.single_matrix_var = tk.Text(input_frame, height=5, width=50, font=("Courier New", 12))
        self.single_matrix_var.grid(row=1, column=0, pady=5, padx=5, sticky="we")
        self.single_matrix_var.insert("1.0", "1 2 3\n4 5 6\n7 8 9")
        
        # Operations frame
        operations_frame = ttk.LabelFrame(input_frame, text="Phép toán")
        operations_frame.grid(row=2, column=0, pady=5, padx=5, sticky="w")
        
        # Operation buttons
        determinant_button = ttk.Button(operations_frame, text="Định thức", 
                                       command=lambda: self.calculate_single_matrix("determinant"))
        determinant_button.grid(row=0, column=0, padx=5, pady=5)
        
        inverse_button = ttk.Button(operations_frame, text="Ma trận nghịch đảo", 
                                   command=lambda: self.calculate_single_matrix("inverse"))
        inverse_button.grid(row=0, column=1, padx=5, pady=5)
        
        transpose_button = ttk.Button(operations_frame, text="Ma trận chuyển vị", 
                                     command=lambda: self.calculate_single_matrix("transpose"))
        transpose_button.grid(row=0, column=2, padx=5, pady=5)
        
        rank_button = ttk.Button(operations_frame, text="Hạng ma trận", 
                                command=lambda: self.calculate_single_matrix("rank"))
        rank_button.grid(row=0, column=3, padx=5, pady=5)
        
        # Example buttons
        examples_frame = ttk.Frame(input_frame)
        examples_frame.grid(row=3, column=0, pady=5, padx=5, sticky="w")
        
        identity_button = ttk.Button(examples_frame, text="Ma trận đơn vị", 
                                    command=lambda: self.set_matrix_example("identity"))
        identity_button.grid(row=0, column=0, padx=5, pady=5)
        
        diagonal_button = ttk.Button(examples_frame, text="Ma trận đường chéo", 
                                    command=lambda: self.set_matrix_example("diagonal"))
        diagonal_button.grid(row=0, column=1, padx=5, pady=5)
        
        # Result frame
        result_frame = ttk.LabelFrame(self.single_matrix_frame, text="Kết quả")
        result_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Result text
        self.single_matrix_result_text = tk.Text(result_frame, height=15, width=80, font=("Courier New", 12))
        self.single_matrix_result_text.pack(side=tk.LEFT, fill="both", expand=True, pady=5, padx=5)
        
        # Scrollbar for result text
        scrollbar = ttk.Scrollbar(result_frame, command=self.single_matrix_result_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.single_matrix_result_text.config(yscrollcommand=scrollbar.set)
    
    def create_two_matrix_widgets(self):
        """Create widgets for two matrix operations"""
        # Input frame
        input_frame = ttk.LabelFrame(self.two_matrix_frame, text="Nhập hai ma trận")
        input_frame.pack(side=tk.TOP, fill="x", padx=10, pady=5)
        
        # Matrix A frame
        matrix_a_frame = ttk.LabelFrame(input_frame, text="Ma trận A")
        matrix_a_frame.grid(row=0, column=0, pady=5, padx=5, sticky="nw")
        
        matrix_a_label = ttk.Label(matrix_a_frame, text="Nhập ma trận A:", font=("Arial", 12))
        matrix_a_label.pack(anchor="w", pady=5, padx=5)
        
        self.matrix_a_var = tk.Text(matrix_a_frame, height=5, width=30, font=("Courier New", 12))
        self.matrix_a_var.pack(fill="both", expand=True, pady=5, padx=5)
        self.matrix_a_var.insert("1.0", "1 2\n3 4")
        
        # Matrix B frame
        matrix_b_frame = ttk.LabelFrame(input_frame, text="Ma trận B")
        matrix_b_frame.grid(row=0, column=1, pady=5, padx=5, sticky="nw")
        
        matrix_b_label = ttk.Label(matrix_b_frame, text="Nhập ma trận B:", font=("Arial", 12))
        matrix_b_label.pack(anchor="w", pady=5, padx=5)
        
        self.matrix_b_var = tk.Text(matrix_b_frame, height=5, width=30, font=("Courier New", 12))
        self.matrix_b_var.pack(fill="both", expand=True, pady=5, padx=5)
        self.matrix_b_var.insert("1.0", "5 6\n7 8")
        
        # Operations frame
        operations_frame = ttk.LabelFrame(input_frame, text="Phép toán")
        operations_frame.grid(row=1, column=0, columnspan=2, pady=5, padx=5, sticky="w")
        
        # Operation buttons
        add_button = ttk.Button(operations_frame, text="A + B", 
                               command=lambda: self.calculate_two_matrices("add"))
        add_button.grid(row=0, column=0, padx=5, pady=5)
        
        subtract_button = ttk.Button(operations_frame, text="A - B", 
                                    command=lambda: self.calculate_two_matrices("subtract"))
        subtract_button.grid(row=0, column=1, padx=5, pady=5)
        
        multiply_button = ttk.Button(operations_frame, text="A × B", 
                                    command=lambda: self.calculate_two_matrices("multiply"))
        multiply_button.grid(row=0, column=2, padx=5, pady=5)
        
        # Result frame
        result_frame = ttk.LabelFrame(self.two_matrix_frame, text="Kết quả")
        result_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Result text
        self.two_matrix_result_text = tk.Text(result_frame, height=15, width=80, font=("Courier New", 12))
        self.two_matrix_result_text.pack(side=tk.LEFT, fill="both", expand=True, pady=5, padx=5)
        
        # Scrollbar for result text
        scrollbar = ttk.Scrollbar(result_frame, command=self.two_matrix_result_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.two_matrix_result_text.config(yscrollcommand=scrollbar.set)
    
    def create_linear_system_widgets(self):
        """Create widgets for system of linear equations"""
        # Input frame
        input_frame = ttk.LabelFrame(self.linear_system_frame, text="Nhập hệ phương trình tuyến tính")
        input_frame.pack(side=tk.TOP, fill="x", padx=10, pady=5)
        
        # System input
        system_label = ttk.Label(input_frame, text="Nhập ma trận hệ số A:", font=("Arial", 12))
        system_label.grid(row=0, column=0, sticky="w", pady=5, padx=5)
        
        self.system_a_var = tk.Text(input_frame, height=5, width=30, font=("Courier New", 12))
        self.system_a_var.grid(row=1, column=0, pady=5, padx=5, sticky="we")
        self.system_a_var.insert("1.0", "1 1 1\n2 1 3\n1 2 3")
        
        # Constants input
        constants_label = ttk.Label(input_frame, text="Nhập vector hằng số b:", font=("Arial", 12))
        constants_label.grid(row=0, column=1, sticky="w", pady=5, padx=5)
        
        self.system_b_var = tk.Text(input_frame, height=5, width=10, font=("Courier New", 12))
        self.system_b_var.grid(row=1, column=1, pady=5, padx=5, sticky="we")
        self.system_b_var.insert("1.0", "6\n13\n14")
        
        # Solve button
        solve_button = ttk.Button(input_frame, text="Giải hệ phương trình", 
                                 command=self.solve_linear_system)
        solve_button.grid(row=2, column=0, columnspan=2, pady=5, padx=5)
        
        # Result frame
        result_frame = ttk.LabelFrame(self.linear_system_frame, text="Kết quả")
        result_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Result text
        self.linear_system_result_text = tk.Text(result_frame, height=15, width=80, font=("Courier New", 12))
        self.linear_system_result_text.pack(side=tk.LEFT, fill="both", expand=True, pady=5, padx=5)
        
        # Scrollbar for result text
        scrollbar = ttk.Scrollbar(result_frame, command=self.linear_system_result_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.linear_system_result_text.config(yscrollcommand=scrollbar.set)

    def calculate_matrix(self):
        # Implementation of matrix calculation method
        pass

    def clear_matrix(self):
        # Implementation of clear matrix method
        pass

    def set_example(self, example):
        """Set an example equation in the entry field"""
        self.equation_var.set(example)
        
    def set_function_example(self, example):
        """Set an example function in the entry field"""
        self.function_var.set(example)
        
    def clear_input(self):
        """Clear the equation input field"""
        self.equation_var.set("")
        self.result_text.delete(1.0, tk.END)
        self.plot.clear()
        self.canvas.draw()
        
    def clear_calculus(self):
        """Clear the calculus input fields"""
        self.function_var.set("")
        self.lower_var.set("")
        self.upper_var.set("")
        self.calculus_result_text.delete(1.0, tk.END)
        self.calculus_plot.clear()
        self.calculus_canvas.draw()
        
    def solve_equation(self):
        try:
            equation_str = self.equation_var.get().strip()
            
            if not equation_str:
                messagebox.showwarning("Cảnh báo", "Vui lòng nhập phương trình!")
                return
            
            # Replace ^ with ** for exponentiation
            equation_str = equation_str.replace("^", "**")
            
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
            self.equation_notebook.select(0)
                
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
                self.equation_notebook.select(1)
                
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

    # Calculus methods
    def find_antiderivative(self):
        """Find the antiderivative (primitive) of a function"""
        try:
            # Get function expression
            func_str = self.function_var.get().strip()
            if not func_str:
                messagebox.showwarning("Cảnh báo", "Vui lòng nhập hàm số!")
                return
            
            # Replace ^ with ** for exponentiation
            func_str = func_str.replace("^", "**")
            
            # Parse the function
            var_name = self.var_var.get().strip() or "x"
            var = sp.Symbol(var_name)
            func = parse_expr(func_str)
            
            # Find the antiderivative
            antiderivative = sp.integrate(func, var)
            
            # Display the results
            self.calculus_result_text.delete(1.0, tk.END)
            self.calculus_result_text.insert(tk.END, f"Hàm số: f({var_name}) = {sp.pretty(func)}\n\n")
            self.calculus_result_text.insert(tk.END, f"Nguyên hàm: F({var_name}) = {sp.pretty(antiderivative)} + C\n\n")
            
            # Show steps for simple functions
            self.show_antiderivative_steps(func, var, antiderivative)
            
            # Switch to results tab
            self.calculus_notebook.select(0)
            
            # Store for plotting
            self.current_function = func
            self.current_antiderivative = antiderivative
            
        except Exception as e:
            self.calculus_result_text.delete(1.0, tk.END)
            self.calculus_result_text.insert(tk.END, f"Lỗi: {str(e)}\n\n")
            self.calculus_result_text.insert(tk.END, "Vui lòng kiểm tra định dạng hàm số và thử lại.")
    
    def calculate_indefinite_integral(self):
        """Calculate the indefinite integral of a function"""
        # This is essentially the same as finding the antiderivative
        self.find_antiderivative()
        
        # Add the integral notation
        if hasattr(self, 'current_function') and self.current_function is not None:
            var_name = self.var_var.get().strip() or "x"
            var = sp.Symbol(var_name)
            self.calculus_result_text.insert(tk.END, f"\nTích phân bất định: ∫ {sp.pretty(self.current_function)} d{var_name} = {sp.pretty(self.current_antiderivative)} + C\n")
    
    def calculate_definite_integral(self):
        """Calculate the definite integral of a function"""
        try:
            # Get function expression
            func_str = self.function_var.get().strip()
            if not func_str:
                messagebox.showwarning("Cảnh báo", "Vui lòng nhập hàm số!")
                return
            
            # Replace ^ with ** for exponentiation
            func_str = func_str.replace("^", "**")
            
            # Get integration limits
            lower_str = self.lower_var.get().strip()
            upper_str = self.upper_var.get().strip()
            
            if not lower_str or not upper_str:
                messagebox.showwarning("Cảnh báo", "Vui lòng nhập giới hạn tích phân!")
                return
            
            # Parse the function and limits
            var_name = self.var_var.get().strip() or "x"
            var = sp.Symbol(var_name)
            
            func = parse_expr(func_str)
            lower_limit = parse_expr(lower_str)
            upper_limit = parse_expr(upper_str)
            
            # Find the antiderivative
            antiderivative = sp.integrate(func, var)
            
            # Calculate the definite integral
            result = sp.integrate(func, (var, lower_limit, upper_limit))
            
            # Display the results
            self.calculus_result_text.delete(1.0, tk.END)
            self.calculus_result_text.insert(tk.END, f"Hàm số: f({var_name}) = {sp.pretty(func)}\n\n")
            self.calculus_result_text.insert(tk.END, f"Giới hạn tích phân: từ {lower_limit} đến {upper_limit}\n\n")
            self.calculus_result_text.insert(tk.END, f"Tích phân xác định: ∫({lower_limit},{upper_limit}) {sp.pretty(func)} d{var_name} = {sp.pretty(result)}\n\n")
            
            # Show numerical approximation if result is symbolic
            if isinstance(result, sp.Expr) and not result.is_number:
                numerical = float(result.evalf())
                self.calculus_result_text.insert(tk.END, f"Giá trị số: {numerical:.6f}\n\n")
            
            # Show steps for the definite integral
            self.show_definite_integral_steps(func, var, antiderivative, lower_limit, upper_limit, result)
            
            # Switch to results tab
            self.calculus_notebook.select(0)
            
            # Store for plotting
            self.current_function = func
            self.current_antiderivative = antiderivative
            self.current_lower_limit = lower_limit
            self.current_upper_limit = upper_limit
            
            # Plot the function and the area under the curve
            self.plot_definite_integral()
            
        except Exception as e:
            self.calculus_result_text.delete(1.0, tk.END)
            self.calculus_result_text.insert(tk.END, f"Lỗi: {str(e)}\n\n")
            self.calculus_result_text.insert(tk.END, "Vui lòng kiểm tra định dạng hàm số và giới hạn tích phân, sau đó thử lại.")
    
    def show_antiderivative_steps(self, func, var, antiderivative):
        """Show steps for finding the antiderivative"""
        self.calculus_result_text.insert(tk.END, "Các bước tìm nguyên hàm:\n")
        
        # Check if the function is a sum
        if func.is_Add:
            terms = func.args
            self.calculus_result_text.insert(tk.END, "1. Phân tách thành tổng các hạng tử:\n")
            for i, term in enumerate(terms):
                self.calculus_result_text.insert(tk.END, f"   f_{i+1}({var}) = {sp.pretty(term)}\n")
            
            self.calculus_result_text.insert(tk.END, "\n2. Tìm nguyên hàm của từng hạng tử:\n")
            for i, term in enumerate(terms):
                term_antiderivative = sp.integrate(term, var)
                self.calculus_result_text.insert(tk.END, f"   F_{i+1}({var}) = ∫ {sp.pretty(term)} d{var} = {sp.pretty(term_antiderivative)}\n")
            
            self.calculus_result_text.insert(tk.END, "\n3. Tổng các nguyên hàm:\n")
            self.calculus_result_text.insert(tk.END, f"   F({var}) = {sp.pretty(antiderivative)} + C\n")
            
        else:
            # Handle common patterns
            if func.has(var**2):
                self.calculus_result_text.insert(tk.END, f"1. Áp dụng công thức: ∫ {var}^n d{var} = {var}^(n+1)/(n+1) + C với n=2\n")
            elif func.has(var):
                self.calculus_result_text.insert(tk.END, f"1. Áp dụng công thức: ∫ {var}^n d{var} = {var}^(n+1)/(n+1) + C với n=1\n")
            elif func.has(sp.sin(var)):
                self.calculus_result_text.insert(tk.END, f"1. Áp dụng công thức: ∫ sin({var}) d{var} = -cos({var}) + C\n")
            elif func.has(sp.cos(var)):
                self.calculus_result_text.insert(tk.END, f"1. Áp dụng công thức: ∫ cos({var}) d{var} = sin({var}) + C\n")
            elif func.has(sp.exp(var)):
                self.calculus_result_text.insert(tk.END, f"1. Áp dụng công thức: ∫ e^{var} d{var} = e^{var} + C\n")
            elif func.has(1/var):
                self.calculus_result_text.insert(tk.END, f"1. Áp dụng công thức: ∫ 1/{var} d{var} = ln|{var}| + C\n")
            else:
                self.calculus_result_text.insert(tk.END, "1. Sử dụng các công thức tích phân cơ bản\n")
            
            self.calculus_result_text.insert(tk.END, f"\n2. Kết quả nguyên hàm:\n")
            self.calculus_result_text.insert(tk.END, f"   F({var}) = {sp.pretty(antiderivative)} + C\n")
            
        self.calculus_result_text.insert(tk.END, "\nGhi chú: C là hằng số tích phân\n")
    
    def show_definite_integral_steps(self, func, var, antiderivative, lower, upper, result):
        """Show steps for calculating the definite integral"""
        self.calculus_result_text.insert(tk.END, "\nCác bước tính tích phân xác định:\n")
        
        self.calculus_result_text.insert(tk.END, f"1. Tìm nguyên hàm F({var}):\n")
        self.calculus_result_text.insert(tk.END, f"   F({var}) = {sp.pretty(antiderivative)}\n\n")
        
        self.calculus_result_text.insert(tk.END, f"2. Áp dụng công thức Newton-Leibniz:\n")
        self.calculus_result_text.insert(tk.END, f"   ∫({lower},{upper}) {sp.pretty(func)} d{var} = F({upper}) - F({lower})\n\n")
        
        # Calculate F(upper) and F(lower)
        f_upper = antiderivative.subs(var, upper)
        f_lower = antiderivative.subs(var, lower)
        
        self.calculus_result_text.insert(tk.END, f"3. Thay giá trị giới hạn:\n")
        self.calculus_result_text.insert(tk.END, f"   F({upper}) = {sp.pretty(f_upper)}\n")
        self.calculus_result_text.insert(tk.END, f"   F({lower}) = {sp.pretty(f_lower)}\n\n")
        
        self.calculus_result_text.insert(tk.END, f"4. Tính hiệu số:\n")
        self.calculus_result_text.insert(tk.END, f"   F({upper}) - F({lower}) = {sp.pretty(f_upper)} - ({sp.pretty(f_lower)}) = {sp.pretty(result)}\n")
    
    def plot_function(self):
        """Plot the function"""
        try:
            # Get function expression
            func_str = self.function_var.get().strip()
            if not func_str:
                messagebox.showwarning("Cảnh báo", "Vui lòng nhập hàm số!")
                return
            
            # Replace ^ with ** for exponentiation
            func_str = func_str.replace("^", "**")
            
            # Parse the function
            var_name = self.var_var.get().strip() or "x"
            var = sp.Symbol(var_name)
            func = parse_expr(func_str)
            
            # Convert sympy expression to numpy function for plotting
            f = sp.lambdify(var, func, 'numpy')
            
            # Clear previous plot
            self.calculus_plot.clear()
            
            # Get limits if available
            try:
                lower = float(parse_expr(self.lower_var.get().strip()).evalf())
                upper = float(parse_expr(self.upper_var.get().strip()).evalf())
                x_min = lower - (upper - lower) * 0.5
                x_max = upper + (upper - lower) * 0.5
            except:
                # Default range if no valid limits
                x_min, x_max = -10, 10
            
            # Generate x values
            x_vals = np.linspace(x_min, x_max, 1000)
            
            try:
                # Calculate y values
                y_vals = f(x_vals)
                
                # Plot the function
                self.calculus_plot.plot(x_vals, y_vals, 'b-', label=f'f({var_name}) = {sp.pretty(func)}')
                
                # Plot x-axis
                self.calculus_plot.axhline(y=0, color='k', linestyle='-', alpha=0.3)
                
                # Plot y-axis
                self.calculus_plot.axvline(x=0, color='k', linestyle='-', alpha=0.3)
                
                # Set labels and title
                self.calculus_plot.set_xlabel(var_name)
                self.calculus_plot.set_ylabel(f'f({var_name})')
                self.calculus_plot.set_title(f'Đồ thị hàm số f({var_name}) = {sp.pretty(func)}')
                self.calculus_plot.grid(True, alpha=0.3)
                self.calculus_plot.legend()
                
                # Update the canvas
                self.calculus_canvas.draw()
                
                # Switch to graph tab
                self.calculus_notebook.select(1)
                
            except Exception as e:
                messagebox.showerror("Lỗi vẽ đồ thị", f"Không thể vẽ đồ thị: {str(e)}")
                
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi: {str(e)}")
    
    def plot_definite_integral(self):
        """Plot the function and the area under the curve for a definite integral"""
        try:
            var_name = self.var_var.get().strip() or "x"
            var = sp.Symbol(var_name)
            func = self.current_function
            
            # Convert sympy expression to numpy function for plotting
            f = sp.lambdify(var, func, 'numpy')
            
            # Clear previous plot
            self.calculus_plot.clear()
            
            # Get limits
            lower = float(self.current_lower_limit.evalf())
            upper = float(self.current_upper_limit.evalf())
            
            # Determine x range for plotting
            padding = (upper - lower) * 0.2
            x_min = lower - padding
            x_max = upper + padding
            
            # Generate x values
            x_vals = np.linspace(x_min, x_max, 1000)
            
            # Calculate y values
            y_vals = f(x_vals)
            
            # Plot the function
            self.calculus_plot.plot(x_vals, y_vals, 'b-', label=f'f({var_name}) = {sp.pretty(func)}')
            
            # Fill the area under the curve
            x_fill = np.linspace(lower, upper, 200)
            y_fill = f(x_fill)
            
            # Only fill the area between the curve and x-axis
            self.calculus_plot.fill_between(x_fill, y_fill, 0, alpha=0.3, color='green', 
                                          label=f'∫({lower},{upper}) {sp.pretty(func)} d{var_name}')
            
            # Plot x-axis
            self.calculus_plot.axhline(y=0, color='k', linestyle='-', alpha=0.3)
            
            # Plot y-axis
            self.calculus_plot.axvline(x=0, color='k', linestyle='-', alpha=0.3)
            
            # Mark the integration limits
            self.calculus_plot.axvline(x=lower, color='r', linestyle='--', alpha=0.5)
            self.calculus_plot.axvline(x=upper, color='r', linestyle='--', alpha=0.5)
            
            # Add text for limits
            self.calculus_plot.text(lower, 0, f'a={lower}', fontsize=10, verticalalignment='bottom')
            self.calculus_plot.text(upper, 0, f'b={upper}', fontsize=10, verticalalignment='bottom')
            
            # Set labels and title
            self.calculus_plot.set_xlabel(var_name)
            self.calculus_plot.set_ylabel(f'f({var_name})')
            self.calculus_plot.set_title(f'Tích phân xác định: ∫({lower},{upper}) {sp.pretty(func)} d{var_name}')
            self.calculus_plot.grid(True, alpha=0.3)
            self.calculus_plot.legend()
            
            # Update the canvas
            self.calculus_canvas.draw()
            
            # Switch to graph tab
            self.calculus_notebook.select(1)
            
        except Exception as e:
            messagebox.showerror("Lỗi vẽ đồ thị", f"Không thể vẽ đồ thị tích phân: {str(e)}")
    
    def set_conversion_example(self, number, base):
        """Set an example for number conversion"""
        self.number_var.set(number)
        self.input_base_var.set(base)
        
        # Set output base to a different value than input
        if base == "2":
            self.output_base_var.set("10")
        elif base == "10":
            self.output_base_var.set("2")
        elif base == "16":
            self.output_base_var.set("10")
    
    def clear_conversion(self):
        """Clear the conversion input and results"""
        self.number_var.set("")
        self.conversion_result_text.delete(1.0, tk.END)
    
    def convert_number(self):
        """Convert a number between different bases"""
        try:
            # Get input values
            number_str = self.number_var.get().strip().upper()  # Convert to uppercase for hex
            input_base = int(self.input_base_var.get())
            output_base = int(self.output_base_var.get())
            
            if not number_str:
                messagebox.showwarning("Cảnh báo", "Vui lòng nhập số cần chuyển đổi!")
                return
            
            # Validate input based on the selected base
            self.validate_number_for_base(number_str, input_base)
            
            # Convert to decimal first (as an intermediate step)
            decimal_value = int(number_str, input_base)
            
            # Convert from decimal to target base
            if output_base == 2:
                result = bin(decimal_value)[2:]  # Remove '0b' prefix
                result_name = "nhị phân"
            elif output_base == 8:
                result = oct(decimal_value)[2:]  # Remove '0o' prefix
                result_name = "bát phân"
            elif output_base == 10:
                result = str(decimal_value)
                result_name = "thập phân"
            elif output_base == 16:
                result = hex(decimal_value)[2:].upper()  # Remove '0x' prefix and convert to uppercase
                result_name = "thập lục phân"
            else:
                # For any other base (though we don't offer this in the UI)
                result = ""
                n = decimal_value
                digits = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                while n > 0:
                    result = digits[n % output_base] + result
                    n //= output_base
                result_name = f"cơ số {output_base}"
            
            # Display the results
            self.conversion_result_text.delete(1.0, tk.END)
            
            # Get base names for display
            input_base_name = self.get_base_name(input_base)
            output_base_name = self.get_base_name(output_base)
            
            self.conversion_result_text.insert(tk.END, f"Số {input_base_name}: {number_str}\n\n")
            self.conversion_result_text.insert(tk.END, f"Chuyển sang {output_base_name}: {result}\n\n")
            
            # Show conversion steps
            self.show_conversion_steps(number_str, input_base, decimal_value, result, output_base)
            
        except ValueError as e:
            self.conversion_result_text.delete(1.0, tk.END)
            self.conversion_result_text.insert(tk.END, f"Lỗi: {str(e)}\n\n")
            self.conversion_result_text.insert(tk.END, "Vui lòng kiểm tra định dạng số và thử lại.")
        except Exception as e:
            self.conversion_result_text.delete(1.0, tk.END)
            self.conversion_result_text.insert(tk.END, f"Lỗi: {str(e)}\n\n")
            self.conversion_result_text.insert(tk.END, "Đã xảy ra lỗi không xác định.")
    
    def validate_number_for_base(self, number_str, base):
        """Validate that the number string contains only valid digits for the given base"""
        valid_chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"[:base]
        for char in number_str.upper():
            if char not in valid_chars:
                raise ValueError(f"Ký tự '{char}' không hợp lệ cho hệ cơ số {base}")
    
    def get_base_name(self, base):
        """Get the Vietnamese name for a number base"""
        if base == 2:
            return "nhị phân (cơ số 2)"
        elif base == 8:
            return "bát phân (cơ số 8)"
        elif base == 10:
            return "thập phân (cơ số 10)"
        elif base == 16:
            return "thập lục phân (cơ số 16)"
        else:
            return f"cơ số {base}"
    
    def show_conversion_steps(self, number_str, input_base, decimal_value, result, output_base):
        """Show the steps for converting between number bases"""
        self.conversion_result_text.insert(tk.END, "Các bước chuyển đổi:\n\n")
        
        # Step 1: Convert to decimal (if not already decimal)
        if input_base != 10:
            self.conversion_result_text.insert(tk.END, f"1. Chuyển từ hệ cơ số {input_base} sang hệ thập phân (cơ số 10):\n")
            
            # Show calculation steps
            digits = list(number_str.upper())
            total = 0
            
            for i, digit in enumerate(reversed(digits)):
                # Convert digit to decimal value
                if '0' <= digit <= '9':
                    digit_value = int(digit)
                else:
                    digit_value = ord(digit) - ord('A') + 10
                
                # Calculate contribution of this digit
                contribution = digit_value * (input_base ** i)
                total += contribution
                
                # Show calculation
                position = len(digits) - i - 1
                self.conversion_result_text.insert(tk.END, f"   {digit} × {input_base}^{i} = {digit} × {input_base**i} = {contribution}\n")
            
            self.conversion_result_text.insert(tk.END, f"   Tổng: {decimal_value} (hệ thập phân)\n\n")
        else:
            self.conversion_result_text.insert(tk.END, f"1. Số đã ở dạng thập phân: {decimal_value}\n\n")
        
        # Step 2: Convert from decimal to target base (if not decimal)
        if output_base != 10:
            self.conversion_result_text.insert(tk.END, f"2. Chuyển từ hệ thập phân (cơ số 10) sang hệ cơ số {output_base}:\n")
            self.conversion_result_text.insert(tk.END, f"   Phương pháp: Chia liên tiếp cho {output_base} và lấy số dư\n\n")
            
            # Show division steps
            n = decimal_value
            steps = []
            
            while n > 0:
                remainder = n % output_base
                # Convert remainder to character representation
                if remainder < 10:
                    remainder_char = str(remainder)
                else:
                    remainder_char = chr(ord('A') + remainder - 10)
                
                steps.append((n, n // output_base, remainder, remainder_char))
                n //= output_base
            
            # Display steps in correct order
            for i, (dividend, quotient, remainder, remainder_char) in enumerate(steps):
                self.conversion_result_text.insert(tk.END, f"   {dividend} ÷ {output_base} = {quotient} dư {remainder} → {remainder_char}\n")
            
            # Show how to read the result
            self.conversion_result_text.insert(tk.END, f"\n   Đọc các số dư từ dưới lên: {result} (hệ cơ số {output_base})\n")
        else:
            self.conversion_result_text.insert(tk.END, f"2. Kết quả ở dạng thập phân: {result}\n")

    def calculate_matrix(self):
        # Implementation of matrix calculation method
        pass

    def clear_matrix(self):
        # Implementation of clear matrix method
        pass

    def calculate_single_matrix(self, operation):
        """Calculate single matrix operations"""
        try:
            # Get matrix from input
            matrix_text = self.single_matrix_var.get("1.0", tk.END).strip()
            matrix = self.parse_matrix(matrix_text)
            
            # Clear result text
            self.single_matrix_result_text.delete("1.0", tk.END)
            
            # Perform operation
            if operation == "determinant":
                self.calculate_determinant(matrix)
            elif operation == "inverse":
                self.calculate_inverse(matrix)
            elif operation == "transpose":
                self.calculate_transpose(matrix)
            elif operation == "rank":
                self.calculate_rank(matrix)
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi tính toán: {str(e)}")
    
    def parse_matrix(self, matrix_text):
        """Parse matrix from text input"""
        rows = matrix_text.strip().split('\n')
        matrix = []
        
        for row in rows:
            elements = row.split()
            if not elements:
                continue
            try:
                # Convert elements to float
                row_values = [float(element) for element in elements]
                matrix.append(row_values)
            except ValueError:
                raise ValueError("Ma trận chứa giá trị không hợp lệ")
        
        # Check if matrix is valid (all rows have same number of elements)
        if not matrix:
            raise ValueError("Ma trận trống")
        
        row_lengths = [len(row) for row in matrix]
        if min(row_lengths) != max(row_lengths):
            raise ValueError("Các hàng của ma trận phải có cùng số phần tử")
        
        return np.array(matrix)
    
    def format_matrix(self, matrix):
        """Format matrix for display"""
        result = ""
        for row in matrix:
            result += " ".join(f"{element:8.4f}" for element in row) + "\n"
        return result
    
    def calculate_determinant(self, matrix):
        """Calculate determinant of a matrix"""
        # Check if matrix is square
        rows, cols = matrix.shape
        if rows != cols:
            self.single_matrix_result_text.insert(tk.END, "Không thể tính định thức của ma trận không vuông\n")
            return
        
        # Calculate determinant
        det = np.linalg.det(matrix)
        
        # Display result
        self.single_matrix_result_text.insert(tk.END, f"Ma trận nhập vào:\n{self.format_matrix(matrix)}\n")
        self.single_matrix_result_text.insert(tk.END, f"Định thức: {det:.6f}\n")
        
        # Show steps for 2x2 and 3x3 matrices
        if rows == 2:
            self.single_matrix_result_text.insert(tk.END, "\nCách tính định thức ma trận 2x2:\n")
            self.single_matrix_result_text.insert(tk.END, f"det(A) = {matrix[0,0]} × {matrix[1,1]} - {matrix[0,1]} × {matrix[1,0]}\n")
            self.single_matrix_result_text.insert(tk.END, f"det(A) = {matrix[0,0] * matrix[1,1]} - {matrix[0,1] * matrix[1,0]}\n")
            self.single_matrix_result_text.insert(tk.END, f"det(A) = {det:.6f}\n")
        elif rows == 3:
            self.single_matrix_result_text.insert(tk.END, "\nCách tính định thức ma trận 3x3 (quy tắc Sarrus):\n")
            self.single_matrix_result_text.insert(tk.END, f"det(A) = {matrix[0,0]}×{matrix[1,1]}×{matrix[2,2]} + {matrix[0,1]}×{matrix[1,2]}×{matrix[2,0]} + {matrix[0,2]}×{matrix[1,0]}×{matrix[2,1]}\n")
            self.single_matrix_result_text.insert(tk.END, f"       - {matrix[0,2]}×{matrix[1,1]}×{matrix[2,0]} - {matrix[0,0]}×{matrix[1,2]}×{matrix[2,1]} - {matrix[0,1]}×{matrix[1,0]}×{matrix[2,2]}\n")
            
            term1 = matrix[0,0] * matrix[1,1] * matrix[2,2]
            term2 = matrix[0,1] * matrix[1,2] * matrix[2,0]
            term3 = matrix[0,2] * matrix[1,0] * matrix[2,1]
            term4 = matrix[0,2] * matrix[1,1] * matrix[2,0]
            term5 = matrix[0,0] * matrix[1,2] * matrix[2,1]
            term6 = matrix[0,1] * matrix[1,0] * matrix[2,2]
            
            self.single_matrix_result_text.insert(tk.END, f"det(A) = {term1:.4f} + {term2:.4f} + {term3:.4f} - {term4:.4f} - {term5:.4f} - {term6:.4f}\n")
            self.single_matrix_result_text.insert(tk.END, f"det(A) = {term1 + term2 + term3 - term4 - term5 - term6:.6f}\n")
    
    def calculate_inverse(self, matrix):
        """Calculate inverse of a matrix"""
        # Check if matrix is square
        rows, cols = matrix.shape
        if rows != cols:
            self.single_matrix_result_text.insert(tk.END, "Không thể tính ma trận nghịch đảo của ma trận không vuông\n")
            return
        
        # Check if determinant is zero
        det = np.linalg.det(matrix)
        if abs(det) < 1e-10:
            self.single_matrix_result_text.insert(tk.END, "Không thể tính ma trận nghịch đảo vì định thức bằng 0\n")
            return
        
        # Calculate inverse
        inverse = np.linalg.inv(matrix)
        
        # Display result
        self.single_matrix_result_text.insert(tk.END, f"Ma trận nhập vào:\n{self.format_matrix(matrix)}\n\n")
        self.single_matrix_result_text.insert(tk.END, f"Ma trận nghịch đảo:\n{self.format_matrix(inverse)}\n\n")
        
        # Verify result
        product = np.matmul(matrix, inverse)
        self.single_matrix_result_text.insert(tk.END, f"Kiểm tra: A × A^(-1) = I\n{self.format_matrix(product)}\n")
        
        # Show steps for 2x2 matrices
        if rows == 2:
            self.single_matrix_result_text.insert(tk.END, "\nCách tính ma trận nghịch đảo 2x2:\n")
            self.single_matrix_result_text.insert(tk.END, f"A = [{matrix[0,0]} {matrix[0,1]}; {matrix[1,0]} {matrix[1,1]}]\n")
            self.single_matrix_result_text.insert(tk.END, f"det(A) = {matrix[0,0]} × {matrix[1,1]} - {matrix[0,1]} × {matrix[1,0]} = {det:.6f}\n")
            self.single_matrix_result_text.insert(tk.END, f"A^(-1) = (1/det(A)) × [{matrix[1,1]} {-matrix[0,1]}; {-matrix[1,0]} {matrix[0,0]}]\n")
            self.single_matrix_result_text.insert(tk.END, f"A^(-1) = (1/{det:.6f}) × [{matrix[1,1]} {-matrix[0,1]}; {-matrix[1,0]} {matrix[0,0]}]\n")
            self.single_matrix_result_text.insert(tk.END, f"A^(-1) = [{inverse[0,0]:.6f} {inverse[0,1]:.6f}; {inverse[1,0]:.6f} {inverse[1,1]:.6f}]\n")
    
    def calculate_transpose(self, matrix):
        """Calculate transpose of a matrix"""
        # Calculate transpose
        transpose = np.transpose(matrix)
        
        # Display result
        self.single_matrix_result_text.insert(tk.END, f"Ma trận nhập vào:\n{self.format_matrix(matrix)}\n\n")
        self.single_matrix_result_text.insert(tk.END, f"Ma trận chuyển vị:\n{self.format_matrix(transpose)}\n")
        
        # Show explanation
        self.single_matrix_result_text.insert(tk.END, "\nGiải thích:\n")
        self.single_matrix_result_text.insert(tk.END, "Ma trận chuyển vị được tạo bằng cách đổi hàng thành cột và cột thành hàng.\n")
        self.single_matrix_result_text.insert(tk.END, f"Kích thước ban đầu: {matrix.shape[0]}×{matrix.shape[1]}\n")
        self.single_matrix_result_text.insert(tk.END, f"Kích thước sau khi chuyển vị: {transpose.shape[0]}×{transpose.shape[1]}\n")
    
    def calculate_rank(self, matrix):
        """Calculate rank of a matrix"""
        # Calculate rank
        rank = np.linalg.matrix_rank(matrix)
        
        # Display result
        self.single_matrix_result_text.insert(tk.END, f"Ma trận nhập vào:\n{self.format_matrix(matrix)}\n\n")
        self.single_matrix_result_text.insert(tk.END, f"Hạng của ma trận: {rank}\n\n")
        
        # Show explanation
        self.single_matrix_result_text.insert(tk.END, "Giải thích:\n")
        self.single_matrix_result_text.insert(tk.END, "Hạng của ma trận là số hàng (hoặc cột) độc lập tuyến tính tối đa của ma trận.\n")
        self.single_matrix_result_text.insert(tk.END, f"Kích thước ma trận: {matrix.shape[0]}×{matrix.shape[1]}\n")
        
        if rank == min(matrix.shape):
            self.single_matrix_result_text.insert(tk.END, "Ma trận có hạng đầy đủ.\n")
        else:
            self.single_matrix_result_text.insert(tk.END, "Ma trận không có hạng đầy đủ.\n")
            
    def set_matrix_example(self, example_type):
        """Set example matrix"""
        if example_type == "identity":
            size = 3
            matrix = np.eye(size)
            matrix_text = "\n".join([" ".join([str(int(element)) for element in row]) for row in matrix])
            self.single_matrix_var.delete("1.0", tk.END)
            self.single_matrix_var.insert("1.0", matrix_text)
        elif example_type == "diagonal":
            matrix_text = "2 0 0\n0 5 0\n0 0 9"
            self.single_matrix_var.delete("1.0", tk.END)
            self.single_matrix_var.insert("1.0", matrix_text)

    def calculate_two_matrices(self, operation):
        """Calculate operations with two matrices"""
        try:
            # Get matrices from input
            matrix_a_text = self.matrix_a_var.get("1.0", tk.END).strip()
            matrix_b_text = self.matrix_b_var.get("1.0", tk.END).strip()
            
            matrix_a = self.parse_matrix(matrix_a_text)
            matrix_b = self.parse_matrix(matrix_b_text)
            
            # Clear result text
            self.two_matrix_result_text.delete("1.0", tk.END)
            
            # Perform operation
            if operation == "add":
                self.add_matrices(matrix_a, matrix_b)
            elif operation == "subtract":
                self.subtract_matrices(matrix_a, matrix_b)
            elif operation == "multiply":
                self.multiply_matrices(matrix_a, matrix_b)
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi tính toán: {str(e)}")
    
    def add_matrices(self, matrix_a, matrix_b):
        """Add two matrices"""
        # Check if matrices have same dimensions
        if matrix_a.shape != matrix_b.shape:
            self.two_matrix_result_text.insert(tk.END, "Không thể cộng hai ma trận có kích thước khác nhau\n")
            self.two_matrix_result_text.insert(tk.END, f"Kích thước ma trận A: {matrix_a.shape[0]}×{matrix_a.shape[1]}\n")
            self.two_matrix_result_text.insert(tk.END, f"Kích thước ma trận B: {matrix_b.shape[0]}×{matrix_b.shape[1]}\n")
            return
        
        # Calculate sum
        result = matrix_a + matrix_b
        
        # Display result
        self.two_matrix_result_text.insert(tk.END, f"Ma trận A:\n{self.format_matrix(matrix_a)}\n")
        self.two_matrix_result_text.insert(tk.END, f"Ma trận B:\n{self.format_matrix(matrix_b)}\n")
        self.two_matrix_result_text.insert(tk.END, f"A + B:\n{self.format_matrix(result)}\n")
        
        # Show explanation
        self.two_matrix_result_text.insert(tk.END, "\nGiải thích:\n")
        self.two_matrix_result_text.insert(tk.END, "Phép cộng hai ma trận thực hiện bằng cách cộng các phần tử tương ứng.\n")
        
        # Show detailed calculation for small matrices
        if matrix_a.shape[0] <= 3 and matrix_a.shape[1] <= 3:
            self.two_matrix_result_text.insert(tk.END, "\nChi tiết tính toán:\n")
            for i in range(matrix_a.shape[0]):
                for j in range(matrix_a.shape[1]):
                    self.two_matrix_result_text.insert(tk.END, f"({matrix_a[i,j]}) + ({matrix_b[i,j]}) = {result[i,j]}\n")
    
    def subtract_matrices(self, matrix_a, matrix_b):
        """Subtract two matrices"""
        # Check if matrices have same dimensions
        if matrix_a.shape != matrix_b.shape:
            self.two_matrix_result_text.insert(tk.END, "Không thể trừ hai ma trận có kích thước khác nhau\n")
            self.two_matrix_result_text.insert(tk.END, f"Kích thước ma trận A: {matrix_a.shape[0]}×{matrix_a.shape[1]}\n")
            self.two_matrix_result_text.insert(tk.END, f"Kích thước ma trận B: {matrix_b.shape[0]}×{matrix_b.shape[1]}\n")
            return
        
        # Calculate difference
        result = matrix_a - matrix_b
        
        # Display result
        self.two_matrix_result_text.insert(tk.END, f"Ma trận A:\n{self.format_matrix(matrix_a)}\n")
        self.two_matrix_result_text.insert(tk.END, f"Ma trận B:\n{self.format_matrix(matrix_b)}\n")
        self.two_matrix_result_text.insert(tk.END, f"A - B:\n{self.format_matrix(result)}\n")
        
        # Show explanation
        self.two_matrix_result_text.insert(tk.END, "\nGiải thích:\n")
        self.two_matrix_result_text.insert(tk.END, "Phép trừ hai ma trận thực hiện bằng cách trừ các phần tử tương ứng.\n")
        
        # Show detailed calculation for small matrices
        if matrix_a.shape[0] <= 3 and matrix_a.shape[1] <= 3:
            self.two_matrix_result_text.insert(tk.END, "\nChi tiết tính toán:\n")
            for i in range(matrix_a.shape[0]):
                for j in range(matrix_a.shape[1]):
                    self.two_matrix_result_text.insert(tk.END, f"({matrix_a[i,j]}) - ({matrix_b[i,j]}) = {result[i,j]}\n")
    
    def multiply_matrices(self, matrix_a, matrix_b):
        """Multiply two matrices"""
        # Check if matrices can be multiplied
        if matrix_a.shape[1] != matrix_b.shape[0]:
            self.two_matrix_result_text.insert(tk.END, "Không thể nhân hai ma trận này\n")
            self.two_matrix_result_text.insert(tk.END, f"Kích thước ma trận A: {matrix_a.shape[0]}×{matrix_a.shape[1]}\n")
            self.two_matrix_result_text.insert(tk.END, f"Kích thước ma trận B: {matrix_b.shape[0]}×{matrix_b.shape[1]}\n")
            self.two_matrix_result_text.insert(tk.END, "Để nhân hai ma trận, số cột của ma trận A phải bằng số hàng của ma trận B\n")
            return
        
        # Calculate product
        result = np.matmul(matrix_a, matrix_b)
        
        # Display result
        self.two_matrix_result_text.insert(tk.END, f"Ma trận A:\n{self.format_matrix(matrix_a)}\n")
        self.two_matrix_result_text.insert(tk.END, f"Ma trận B:\n{self.format_matrix(matrix_b)}\n")
        self.two_matrix_result_text.insert(tk.END, f"A × B:\n{self.format_matrix(result)}\n")
        
        # Show explanation
        self.two_matrix_result_text.insert(tk.END, "\nGiải thích:\n")
        self.two_matrix_result_text.insert(tk.END, "Phép nhân hai ma trận A và B tạo ra ma trận C, trong đó:\n")
        self.two_matrix_result_text.insert(tk.END, "C[i,j] = Tổng(A[i,k] * B[k,j]) với k chạy từ 0 đến n-1\n")
        self.two_matrix_result_text.insert(tk.END, f"Kích thước ma trận kết quả: {result.shape[0]}×{result.shape[1]}\n")
        
        # Show detailed calculation for small matrices
        if matrix_a.shape[0] <= 3 and matrix_b.shape[1] <= 3:
            self.two_matrix_result_text.insert(tk.END, "\nChi tiết tính toán:\n")
            for i in range(result.shape[0]):
                for j in range(result.shape[1]):
                    self.two_matrix_result_text.insert(tk.END, f"C[{i},{j}] = ")
                    terms = []
                    for k in range(matrix_a.shape[1]):
                        terms.append(f"{matrix_a[i,k]} × {matrix_b[k,j]}")
                    self.two_matrix_result_text.insert(tk.END, " + ".join(terms) + f" = {result[i,j]}\n")

    def solve_linear_system(self):
        """Solve system of linear equations"""
        try:
            # Get coefficient matrix and constants vector
            matrix_a_text = self.system_a_var.get("1.0", tk.END).strip()
            matrix_b_text = self.system_b_var.get("1.0", tk.END).strip()
            
            matrix_a = self.parse_matrix(matrix_a_text)
            matrix_b = np.array([float(x) for x in matrix_b_text.split('\n') if x.strip()])
            
            # Check dimensions
            if matrix_a.shape[0] != len(matrix_b):
                raise ValueError("Số hàng của ma trận hệ số phải bằng số phần tử của vector hằng số")
            
            # Clear result text
            self.linear_system_result_text.delete("1.0", tk.END)
            
            # Display the system
            self.display_linear_system(matrix_a, matrix_b)
            
            # Check if system has a solution
            rank_a = np.linalg.matrix_rank(matrix_a)
            augmented = np.column_stack((matrix_a, matrix_b))
            rank_augmented = np.linalg.matrix_rank(augmented)
            
            if rank_a != rank_augmented:
                self.linear_system_result_text.insert(tk.END, "\nHệ phương trình vô nghiệm\n")
                self.linear_system_result_text.insert(tk.END, f"Hạng của ma trận hệ số: {rank_a}\n")
                self.linear_system_result_text.insert(tk.END, f"Hạng của ma trận mở rộng: {rank_augmented}\n")
                return
            
            # Check if system has unique solution
            if rank_a < matrix_a.shape[1]:
                self.linear_system_result_text.insert(tk.END, "\nHệ phương trình có vô số nghiệm\n")
                self.linear_system_result_text.insert(tk.END, f"Hạng của ma trận hệ số: {rank_a}\n")
                self.linear_system_result_text.insert(tk.END, f"Số ẩn: {matrix_a.shape[1]}\n")
                
                # Try to find a particular solution
                self.linear_system_result_text.insert(tk.END, "\nMột nghiệm riêng:\n")
                try:
                    # Use least squares to find a solution
                    solution, residuals, rank, s = np.linalg.lstsq(matrix_a, matrix_b, rcond=None)
                    self.display_solution(solution)
                    
                    # Explain that this is just one solution
                    self.linear_system_result_text.insert(tk.END, "\nLưu ý: Đây chỉ là một nghiệm riêng. Hệ có vô số nghiệm.\n")
                except:
                    self.linear_system_result_text.insert(tk.END, "Không thể tìm nghiệm riêng.\n")
                return
            
            # Solve the system
            try:
                solution = np.linalg.solve(matrix_a, matrix_b)
                self.linear_system_result_text.insert(tk.END, "\nNghiệm của hệ phương trình:\n")
                self.display_solution(solution)
                
                # Verify the solution
                self.verify_solution(matrix_a, matrix_b, solution)
                
                # Show solution steps for small systems
                if matrix_a.shape[0] <= 3 and matrix_a.shape[1] <= 3:
                    self.show_solution_steps(matrix_a, matrix_b)
            except np.linalg.LinAlgError:
                self.linear_system_result_text.insert(tk.END, "\nKhông thể giải hệ phương trình bằng phương pháp ma trận.\n")
                self.linear_system_result_text.insert(tk.END, "Ma trận hệ số có thể không khả nghịch.\n")
        
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi giải hệ phương trình: {str(e)}")
            
    def display_linear_system(self, matrix_a, matrix_b):
        """Display the linear system in a readable format"""
        self.linear_system_result_text.insert(tk.END, "Hệ phương trình tuyến tính:\n")
        
        for i in range(matrix_a.shape[0]):
            equation = ""
            for j in range(matrix_a.shape[1]):
                if j == 0:
                    if matrix_a[i,j] == 1:
                        equation += f"x{j+1}"
                    elif matrix_a[i,j] == -1:
                        equation += f"-x{j+1}"
                    elif matrix_a[i,j] != 0:
                        equation += f"{matrix_a[i,j]}x{j+1}"
                else:
                    if matrix_a[i,j] == 0:
                        continue
                    elif matrix_a[i,j] == 1:
                        equation += f" + x{j+1}"
                    elif matrix_a[i,j] == -1:
                        equation += f" - x{j+1}"
                    elif matrix_a[i,j] > 0:
                        equation += f" + {matrix_a[i,j]}x{j+1}"
                    else:
                        equation += f" - {abs(matrix_a[i,j])}x{j+1}"
            
            equation += f" = {matrix_b[i]}"
            self.linear_system_result_text.insert(tk.END, equation + "\n")
    
    def display_solution(self, solution):
        """Display the solution of the linear system"""
        for i, value in enumerate(solution):
            self.linear_system_result_text.insert(tk.END, f"x{i+1} = {value:.6f}\n")

    def verify_solution(self, matrix_a, matrix_b, solution):
        """Verify the solution by substituting back into the equations"""
        self.linear_system_result_text.insert(tk.END, "\nKiểm tra nghiệm:\n")
        
        # Calculate Ax
        ax = np.matmul(matrix_a, solution)
        
        for i in range(len(matrix_b)):
            self.linear_system_result_text.insert(tk.END, f"Phương trình {i+1}: {ax[i]:.6f} ≈ {matrix_b[i]:.6f}\n")
        
        # Calculate error
        error = np.linalg.norm(ax - matrix_b)
        self.linear_system_result_text.insert(tk.END, f"\nSai số: {error:.10f}\n")
    
    def show_solution_steps(self, matrix_a, matrix_b):
        """Show step-by-step solution using Gaussian elimination"""
        self.linear_system_result_text.insert(tk.END, "\nCác bước giải bằng phương pháp khử Gauss:\n")
        
        # Create augmented matrix
        augmented = np.column_stack((matrix_a, matrix_b))
        
        # Display initial augmented matrix
        self.linear_system_result_text.insert(tk.END, "\nMa trận mở rộng ban đầu:\n")
        self.display_augmented_matrix(augmented)
        
        # Forward elimination
        n = matrix_a.shape[0]  # Number of rows
        m = matrix_a.shape[1]  # Number of columns
        
        for i in range(min(n, m)):
            # Find pivot
            max_row = i
            for j in range(i + 1, n):
                if abs(augmented[j, i]) > abs(augmented[max_row, i]):
                    max_row = j
            
            # Swap rows if needed
            if max_row != i:
                augmented[[i, max_row]] = augmented[[max_row, i]]
                self.linear_system_result_text.insert(tk.END, f"\nHoán đổi hàng {i+1} và {max_row+1}:\n")
                self.display_augmented_matrix(augmented)
            
            # Skip if pivot is zero
            if abs(augmented[i, i]) < 1e-10:
                continue
            
            # Normalize the pivot row
            pivot = augmented[i, i]
            augmented[i] = augmented[i] / pivot
            self.linear_system_result_text.insert(tk.END, f"\nChuẩn hóa hàng {i+1} (chia cho {pivot:.6f}):\n")
            self.display_augmented_matrix(augmented)
            
            # Eliminate below
            for j in range(i + 1, n):
                factor = augmented[j, i]
                if abs(factor) < 1e-10:
                    continue
                augmented[j] = augmented[j] - factor * augmented[i]
                self.linear_system_result_text.insert(tk.END, f"\nTrừ {factor:.6f} lần hàng {i+1} từ hàng {j+1}:\n")
                self.display_augmented_matrix(augmented)
        
        # Back substitution
        self.linear_system_result_text.insert(tk.END, "\nThực hiện thế ngược:\n")
        
        # Create solution vector
        solution = np.zeros(m)
        
        # Start from the last row
        for i in range(min(n, m) - 1, -1, -1):
            solution[i] = augmented[i, -1]
            for j in range(i + 1, m):
                solution[i] -= augmented[i, j] * solution[j]
            
            self.linear_system_result_text.insert(tk.END, f"x{i+1} = {solution[i]:.6f}\n")
        
        # Display final solution
        self.linear_system_result_text.insert(tk.END, "\nNghiệm cuối cùng:\n")
        for i in range(m):
            self.linear_system_result_text.insert(tk.END, f"x{i+1} = {solution[i]:.6f}\n")
    
    def display_augmented_matrix(self, augmented):
        """Display augmented matrix with vertical line before last column"""
        rows, cols = augmented.shape
        
        for i in range(rows):
            row_str = ""
            for j in range(cols):
                if j == cols - 1:
                    row_str += f"| {augmented[i,j]:8.4f}"
                else:
                    row_str += f"{augmented[i,j]:8.4f} "
            self.linear_system_result_text.insert(tk.END, row_str + "\n")

    def create_plotter_widgets(self):
        """Create widgets for function plotter tab"""
        # Title
        title_label = tk.Label(self.plotter_frame, text="Vẽ đồ thị hàm số", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Main frame
        main_frame = ttk.Frame(self.plotter_frame)
        main_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Left panel for inputs
        left_panel = ttk.LabelFrame(main_frame, text="Nhập hàm số")
        left_panel.pack(side=tk.LEFT, fill="y", padx=5, pady=5)
        
        # Function input
        function_label = ttk.Label(left_panel, text="Nhập hàm số f(x):", font=("Arial", 12))
        function_label.pack(anchor="w", pady=5, padx=5)
        
        input_frame = ttk.Frame(left_panel)
        input_frame.pack(fill="x", pady=5, padx=5)
        
        self.function_var = tk.StringVar()
        function_entry = ttk.Entry(input_frame, textvariable=self.function_var, width=30)
        function_entry.pack(side=tk.LEFT, fill="x", expand=True)
        
        add_button = ttk.Button(input_frame, text="Thêm", command=self.add_function)
        add_button.pack(side=tk.RIGHT, padx=5)
        
        # Function list
        list_label = ttk.Label(left_panel, text="Danh sách hàm số:", font=("Arial", 12))
        list_label.pack(anchor="w", pady=5, padx=5)
        
        # Create a frame for the function list
        self.functions_frame = ttk.Frame(left_panel)
        self.functions_frame.pack(fill="both", expand=True, pady=5, padx=5)
        
        # Dictionary to store function entries and their colors
        self.function_entries = {}
        self.function_colors = {}
        
        # Range settings
        range_frame = ttk.LabelFrame(left_panel, text="Phạm vi đồ thị")
        range_frame.pack(fill="x", pady=5, padx=5)
        
        x_range_frame = ttk.Frame(range_frame)
        x_range_frame.pack(fill="x", pady=5, padx=5)
        
        x_min_label = ttk.Label(x_range_frame, text="X min:")
        x_min_label.grid(row=0, column=0, padx=5)
        
        self.x_min_var = tk.StringVar(value="-10")
        x_min_entry = ttk.Entry(x_range_frame, textvariable=self.x_min_var, width=5)
        x_min_entry.grid(row=0, column=1, padx=5)
        
        x_max_label = ttk.Label(x_range_frame, text="X max:")
        x_max_label.grid(row=0, column=2, padx=5)
        
        self.x_max_var = tk.StringVar(value="10")
        x_max_entry = ttk.Entry(x_range_frame, textvariable=self.x_max_var, width=5)
        x_max_entry.grid(row=0, column=3, padx=5)
        
        y_range_frame = ttk.Frame(range_frame)
        y_range_frame.pack(fill="x", pady=5, padx=5)
        
        y_min_label = ttk.Label(y_range_frame, text="Y min:")
        y_min_label.grid(row=0, column=0, padx=5)
        
        self.y_min_var = tk.StringVar(value="-10")
        y_min_entry = ttk.Entry(y_range_frame, textvariable=self.y_min_var, width=5)
        y_min_entry.grid(row=0, column=1, padx=5)
        
        y_max_label = ttk.Label(y_range_frame, text="Y max:")
        y_max_label.grid(row=0, column=2, padx=5)
        
        self.y_max_var = tk.StringVar(value="10")
        y_max_entry = ttk.Entry(y_range_frame, textvariable=self.y_max_var, width=5)
        y_max_entry.grid(row=0, column=3, padx=5)
        
        # Plot button
        plot_button = ttk.Button(left_panel, text="Vẽ đồ thị", command=self.plot_functions)
        plot_button.pack(fill="x", pady=10, padx=5)
        
        # Clear all button
        clear_button = ttk.Button(left_panel, text="Xóa tất cả", command=self.clear_all_functions)
        clear_button.pack(fill="x", pady=5, padx=5)
        
        # Example buttons
        examples_frame = ttk.LabelFrame(left_panel, text="Ví dụ")
        examples_frame.pack(fill="x", pady=5, padx=5)
        
        example1_button = ttk.Button(examples_frame, text="y = x^2", 
                                    command=lambda: self.set_function_example("x**2"))
        example1_button.grid(row=0, column=0, padx=5, pady=5)
        
        example2_button = ttk.Button(examples_frame, text="y = sin(x)", 
                                    command=lambda: self.set_function_example("sin(x)"))
        example2_button.grid(row=0, column=1, padx=5, pady=5)
        
        example3_button = ttk.Button(examples_frame, text="y = e^x", 
                                    command=lambda: self.set_function_example("exp(x)"))
        example3_button.grid(row=1, column=0, padx=5, pady=5)
        
        example4_button = ttk.Button(examples_frame, text="y = ln(x)", 
                                    command=lambda: self.set_function_example("log(x)"))
        example4_button.grid(row=1, column=1, padx=5, pady=5)
        
        # Right panel for plot
        right_panel = ttk.LabelFrame(main_frame, text="Đồ thị")
        right_panel.pack(side=tk.RIGHT, fill="both", expand=True, padx=5, pady=5)
        
        # Create figure and canvas for the plot
        self.fig, self.ax = plt.subplots(figsize=(6, 5))
        self.canvas = FigureCanvasTkAgg(self.fig, master=right_panel)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # Initialize plot
        self.initialize_plot()

    def initialize_plot(self):
        """Initialize the plot with axes and grid"""
        self.ax.clear()
        self.ax.axhline(y=0, color='k', linestyle='-', alpha=0.3)
        self.ax.axvline(x=0, color='k', linestyle='-', alpha=0.3)
        self.ax.grid(True, linestyle='--', alpha=0.7)
        self.ax.set_title("Đồ thị hàm số")
        self.ax.set_xlabel("x")
        self.ax.set_ylabel("y")
        
        # Set initial range
        try:
            x_min = float(self.x_min_var.get())
            x_max = float(self.x_max_var.get())
            y_min = float(self.y_min_var.get())
            y_max = float(self.y_max_var.get())
            
            self.ax.set_xlim(x_min, x_max)
            self.ax.set_ylim(y_min, y_max)
        except ValueError:
            self.ax.set_xlim(-10, 10)
            self.ax.set_ylim(-10, 10)
        
        self.canvas.draw()
    
    def add_function(self):
        """Add a function to the list"""
        function_text = self.function_var.get().strip()
        if not function_text:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập hàm số!")
            return
        
        # Try to parse the function to check if it's valid
        try:
            # Replace ^ with ** for exponentiation
            function_text = function_text.replace("^", "**")
            x = sp.symbols('x')
            expr = parse_expr(function_text)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Hàm số không hợp lệ: {str(e)}")
            return
        
        # Generate a random color for this function (avoiding very light colors)
        color = "#{:02x}{:02x}{:02x}".format(
            random.randint(20, 200), 
            random.randint(20, 200), 
            random.randint(20, 200)
        )
        
        # Create a frame for this function
        function_frame = ttk.Frame(self.functions_frame)
        function_frame.pack(fill="x", pady=2)
        
        # Create a colored label to show the function color
        color_label = tk.Label(function_frame, text="   ", background=color)
        color_label.pack(side=tk.LEFT, padx=5)
        
        # Create a label to show the function
        function_label = ttk.Label(function_frame, text=f"y = {function_text}")
        function_label.pack(side=tk.LEFT, fill="x", expand=True)
        
        # Create a delete button
        delete_button = ttk.Button(
            function_frame, 
            text="×", 
            width=2,
            command=lambda f=function_frame, ft=function_text: self.remove_function(f, ft)
        )
        delete_button.pack(side=tk.RIGHT, padx=5)
        
        # Store the function and its color
        self.function_entries[function_text] = function_frame
        self.function_colors[function_text] = color
        
        # Clear the entry
        self.function_var.set("")
        
        # Plot the functions
        self.plot_functions()
    
    def remove_function(self, function_frame, function_text):
        """Remove a function from the list"""
        function_frame.destroy()
        if function_text in self.function_entries:
            del self.function_entries[function_text]
        if function_text in self.function_colors:
            del self.function_colors[function_text]
        
        # Update the plot
        self.plot_functions()
    
    def clear_all_functions(self):
        """Clear all functions from the list"""
        for frame in self.functions_frame.winfo_children():
            frame.destroy()
        
        self.function_entries.clear()
        self.function_colors.clear()
        
        # Reset the plot
        self.initialize_plot()
    
    def plot_functions(self):
        """Plot all functions in the list"""
        try:
            # Get the x range
            x_min = float(self.x_min_var.get())
            x_max = float(self.x_max_var.get())
            y_min = float(self.y_min_var.get())
            y_max = float(self.y_max_var.get())
            
            # Clear the plot
            self.ax.clear()
            
            # Add axes and grid
            self.ax.axhline(y=0, color='k', linestyle='-', alpha=0.3)
            self.ax.axvline(x=0, color='k', linestyle='-', alpha=0.3)
            self.ax.grid(True, linestyle='--', alpha=0.7)
            self.ax.set_title("Đồ thị hàm số")
            self.ax.set_xlabel("x")
            self.ax.set_ylabel("y")
            
            # Set the range
            self.ax.set_xlim(x_min, x_max)
            self.ax.set_ylim(y_min, y_max)
            
            # If no functions, just draw the empty plot
            if not self.function_entries:
                self.canvas.draw()
                return
            
            # Create x values for plotting
            x_values = np.linspace(x_min, x_max, 1000)
            
            # Plot each function
            for function_text, color in self.function_colors.items():
                try:
                    # Create a lambda function from the expression
                    x = sp.symbols('x')
                    expr = parse_expr(function_text)
                    f = sp.lambdify(x, expr, "numpy")
                    
                    # Calculate y values
                    y_values = []
                    for x_val in x_values:
                        try:
                            y_val = f(x_val)
                            # Check if y value is within range
                            if y_val > y_max * 10 or y_val < y_min * 10:
                                y_val = np.nan
                            y_values.append(y_val)
                        except:
                            y_values.append(np.nan)
                    
                    # Plot the function
                    self.ax.plot(x_values, y_values, color=color, label=f"y = {function_text}")
                    
                except Exception as e:
                    print(f"Error plotting function {function_text}: {str(e)}")
            
            # Add legend
            self.ax.legend(loc='upper right')
            
            # Draw the plot
            self.canvas.draw()
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi vẽ đồ thị: {str(e)}")
    
    def set_function_example(self, example):
        """Set an example function in the entry field"""
        self.function_var.set(example)

if __name__ == "__main__":
    root = tk.Tk()
    app = MathEquationSolver(root)
    root.mainloop() 