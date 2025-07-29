#!/bin/bash

echo "Math Equation Solver - Giải Phương Trình, Tích Phân và Chuyển Đổi Hệ Cơ Số"
echo "========================================================================="
echo

echo "Installing required packages..."
pip3 install numpy sympy matplotlib
echo

echo "Starting application..."
python3 21_math_equation_solver.py
echo 