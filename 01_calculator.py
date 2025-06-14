def add(x, y):
    return x + y

def subtract(x, y):
    return x - y

def multiply(x, y):
    return x * y

def divide(x, y):
    if y != 0:
        return x / y
    else:
        return "Không thể chia cho 0!"

def calculator():
    print("=== MÁY TÍNH ĐƠN GIẢN ===")
    print("1. Cộng (+)")
    print("2. Trừ (-)")
    print("3. Nhân (×)")
    print("4. Chia (÷)")
    
    while True:
        choice = input("\nChọn phép tính (1-4) hoặc 'q' để thoát: ")
        
        if choice.lower() == 'q':
            print("Cám ơn bạn đã sử dụng!")
            break
            
        if choice in ['1', '2', '3', '4']:
            try:
                num1 = float(input("Nhập số thứ nhất: "))
                num2 = float(input("Nhập số thứ hai: "))
                
                if choice == '1':
                    print(f"Kết quả: {num1} + {num2} = {add(num1, num2)}")
                elif choice == '2':
                    print(f"Kết quả: {num1} - {num2} = {subtract(num1, num2)}")
                elif choice == '3':
                    print(f"Kết quả: {num1} × {num2} = {multiply(num1, num2)}")
                elif choice == '4':
                    result = divide(num1, num2)
                    print(f"Kết quả: {num1} ÷ {num2} = {result}")
                    
            except ValueError:
                print("Vui lòng nhập số hợp lệ!")
        else:
            print("Lựa chọn không hợp lệ!")

if __name__ == "__main__":
    calculator()
