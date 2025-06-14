import random
import string

def generate_password(length=12, include_uppercase=True, include_lowercase=True, 
                     include_numbers=True, include_symbols=True):
    characters = ""
    
    if include_lowercase:
        characters += string.ascii_lowercase
    if include_uppercase:
        characters += string.ascii_uppercase
    if include_numbers:
        characters += string.digits
    if include_symbols:
        characters += "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    if not characters:
        return "Cần chọn ít nhất một loại ký tự!"
    
    password = ''.join(random.choice(characters) for _ in range(length))
    return password

def password_strength(password):
    score = 0
    feedback = []
    
    if len(password) >= 8:
        score += 1
    else:
        feedback.append("Nên có ít nhất 8 ký tự")
    
    if any(c.islower() for c in password):
        score += 1
    else:
        feedback.append("Nên có chữ thường")
        
    if any(c.isupper() for c in password):
        score += 1
    else:
        feedback.append("Nên có chữ hoa")
        
    if any(c.isdigit() for c in password):
        score += 1
    else:
        feedback.append("Nên có số")
        
    if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        score += 1
    else:
        feedback.append("Nên có ký tự đặc biệt")
    
    strength_levels = ["Rất yếu", "Yếu", "Trung bình", "Mạnh", "Rất mạnh"]
    return strength_levels[min(score, 4)], feedback

def main():
    print("=== TRÌNH TẠO MẬT KHẨU ===")
    
    while True:
        print("\n1. Tạo mật khẩu mới")
        print("2. Kiểm tra độ mạnh mật khẩu")
        print("3. Thoát")
        
        choice = input("\nChọn chức năng (1-3): ")
        
        if choice == '1':
            try:
                length = int(input("Độ dài mật khẩu (mặc định 12): ") or 12)
                
                print("\nTùy chọn ký tự (Enter để bỏ qua):")
                uppercase = input("Bao gồm chữ hoa (y/n, mặc định y): ").lower() != 'n'
                lowercase = input("Bao gồm chữ thường (y/n, mặc định y): ").lower() != 'n'
                numbers = input("Bao gồm số (y/n, mặc định y): ").lower() != 'n'
                symbols = input("Bao gồm ký tự đặc biệt (y/n, mặc định y): ").lower() != 'n'
                
                password = generate_password(length, uppercase, lowercase, numbers, symbols)
                print(f"\n🔐 Mật khẩu được tạo: {password}")
                
                strength, tips = password_strength(password)
                print(f"💪 Độ mạnh: {strength}")
                
            except ValueError:
                print("Vui lòng nhập số hợp lệ!")
                
        elif choice == '2':
            password = input("Nhập mật khẩu để kiểm tra: ")
            strength, tips = password_strength(password)
            print(f"\n💪 Độ mạnh: {strength}")
            if tips:
                print("💡 Gợi ý cải thiện:")
                for tip in tips:
                    print(f"   - {tip}")
                    
        elif choice == '3':
            print("Tạm biệt!")
            break
        else:
            print("Lựa chọn không hợp lệ!")

if __name__ == "__main__":
    main()
