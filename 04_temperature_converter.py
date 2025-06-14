def celsius_to_fahrenheit(celsius):
    return (celsius * 9/5) + 32

def fahrenheit_to_celsius(fahrenheit):
    return (fahrenheit - 32) * 5/9

def celsius_to_kelvin(celsius):
    return celsius + 273.15

def kelvin_to_celsius(kelvin):
    return kelvin - 273.15

def fahrenheit_to_kelvin(fahrenheit):
    celsius = fahrenheit_to_celsius(fahrenheit)
    return celsius_to_kelvin(celsius)

def kelvin_to_fahrenheit(kelvin):
    celsius = kelvin_to_celsius(kelvin)
    return celsius_to_fahrenheit(celsius)

def temperature_converter():
    print("=== CHUYỂN ĐỔI NHIỆT ĐỘ ===")
    print("1. Celsius sang Fahrenheit")
    print("2. Fahrenheit sang Celsius")
    print("3. Celsius sang Kelvin")
    print("4. Kelvin sang Celsius")
    print("5. Fahrenheit sang Kelvin")
    print("6. Kelvin sang Fahrenheit")
    
    while True:
        choice = input("\nChọn phép chuyển đổi (1-6) hoặc 'q' để thoát: ")
        
        if choice.lower() == 'q':
            print("Cảm ơn bạn đã sử dụng!")
            break
            
        if choice in ['1', '2', '3', '4', '5', '6']:
            try:
                if choice == '1':
                    temp = float(input("Nhập nhiệt độ Celsius: "))
                    result = celsius_to_fahrenheit(temp)
                    print(f"{temp}°C = {result:.2f}°F")
                    
                elif choice == '2':
                    temp = float(input("Nhập nhiệt độ Fahrenheit: "))
                    result = fahrenheit_to_celsius(temp)
                    print(f"{temp}°F = {result:.2f}°C")
                    
                elif choice == '3':
                    temp = float(input("Nhập nhiệt độ Celsius: "))
                    result = celsius_to_kelvin(temp)
                    print(f"{temp}°C = {result:.2f}K")
                    
                elif choice == '4':
                    temp = float(input("Nhập nhiệt độ Kelvin: "))
                    if temp < 0:
                        print("Nhiệt độ Kelvin không thể âm!")
                        continue
                    result = kelvin_to_celsius(temp)
                    print(f"{temp}K = {result:.2f}°C")
                    
                elif choice == '5':
                    temp = float(input("Nhập nhiệt độ Fahrenheit: "))
                    result = fahrenheit_to_kelvin(temp)
                    print(f"{temp}°F = {result:.2f}K")
                    
                elif choice == '6':
                    temp = float(input("Nhập nhiệt độ Kelvin: "))
                    if temp < 0:
                        print("Nhiệt độ Kelvin không thể âm!")
                        continue
                    result = kelvin_to_fahrenheit(temp)
                    print(f"{temp}K = {result:.2f}°F")
                    
            except ValueError:
                print("Vui lòng nhập số hợp lệ!")
        else:
            print("Lựa chọn không hợp lệ!")

if __name__ == "__main__":
    temperature_converter()
