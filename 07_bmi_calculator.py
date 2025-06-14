def calculate_bmi(weight, height):
    """Tính chỉ số BMI"""
    return weight / (height ** 2)

def get_bmi_category(bmi):
    """Phân loại BMI theo tiêu chuẩn WHO"""
    if bmi < 18.5:
        return "Thiếu cân", "🔵"
    elif 18.5 <= bmi < 25:
        return "Bình thường", "🟢"
    elif 25 <= bmi < 30:
        return "Thừa cân", "🟡"
    elif 30 <= bmi < 35:
        return "Béo phì độ I", "🟠"
    elif 35 <= bmi < 40:
        return "Béo phì độ II", "🔴"
    else:
        return "Béo phì độ III", "🔴"

def get_health_advice(category):
    """Đưa ra lời khuyên sức khỏe"""
    advice = {
        "Thiếu cân": [
            "💡 Tăng cường dinh dưỡng với thực phẩm giàu protein",
            "🏋️ Tập luyện để tăng khối lượng cơ",
            "👨‍⚕️ Tham khảo ý kiến bác sĩ dinh dưỡng"
        ],
        "Bình thường": [
            "✅ Duy trì lối sống hiện tại",
            "🥗 Tiếp tục chế độ ăn cân bằng",
            "🏃 Duy trì hoạt động thể chất đều đặn"
        ],
        "Thừa cân": [
            "🥗 Giảm lượng calo nạp vào",
            "🏃 Tăng cường hoạt động thể chất",
            "⚖️ Theo dõi cân nặng thường xuyên"
        ],
        "Béo phì độ I": [
            "📉 Cần giảm cân nghiêm túc",
            "👨‍⚕️ Tham khảo chuyên gia dinh dưỡng",
            "🏋️ Kết hợp chế độ ăn và tập luyện"
        ],
        "Béo phì độ II": [
            "⚠️ Cần can thiệp y tế",
            "👨‍⚕️ Khám bác sĩ chuyên khoa",
            "📋 Có thể cần chế độ điều trị đặc biệt"
        ],
        "Béo phì độ III": [
            "🚨 Cần can thiệp y tế khẩn cấp",
            "🏥 Liên hệ bác sĩ ngay lập tức",
            "⚕️ Có thể cần phẫu thuật giảm béo"
        ]
    }
    return advice.get(category, [])

def bmi_calculator():
    print("=== TÍNH CHỈ SỐ BMI ===")
    print("BMI (Body Mass Index) - Chỉ số khối cơ thể")
    
    while True:
        try:
            print("\n--- Nhập thông tin ---")
            weight = float(input("Cân nặng (kg): "))
            height = float(input("Chiều cao (m): "))
            
            if weight <= 0 or height <= 0:
                print("❌ Cân nặng và chiều cao phải lớn hơn 0!")
                continue
            
            if height > 3:
                print("⚠️ Bạn có nhập chiều cao bằng cm? Vui lòng nhập bằng mét (vd: 1.70)")
                continue
            
            # Tính BMI
            bmi = calculate_bmi(weight, height)
            category, emoji = get_bmi_category(bmi)
            
            # Hiển thị kết quả
            print(f"\n=== KẾT QUẢ ===")
            print(f"📏 Chiều cao: {height}m")
            print(f"⚖️ Cân nặng: {weight}kg")
            print(f"📊 BMI: {bmi:.1f}")
            print(f"{emoji} Phân loại: {category}")
            
            # Hiển thị bảng tham khảo
            print(f"\n📋 BẢNG THAM KHẢO BMI:")
            print("🔵 Thiếu cân: < 18.5")
            print("🟢 Bình thường: 18.5 - 24.9")
            print("🟡 Thừa cân: 25.0 - 29.9")
            print("🟠 Béo phì độ I: 30.0 - 34.9")
            print("🔴 Béo phì độ II: 35.0 - 39.9")
            print("🔴 Béo phì độ III: ≥ 40.0")
            
            # Lời khuyên sức khỏe
            advice_list = get_health_advice(category)
            if advice_list:
                print(f"\n💡 LỜI KHUYÊN:")
                for advice in advice_list:
                    print(f"   {advice}")
            
            # Tính cân nặng lý tưởng
            ideal_weight_min = 18.5 * (height ** 2)
            ideal_weight_max = 24.9 * (height ** 2)
            print(f"\n🎯 Cân nặng lý tưởng cho bạn: {ideal_weight_min:.1f} - {ideal_weight_max:.1f} kg")
            
            # Hỏi có muốn tính tiếp
            continue_calc = input("\nBạn có muốn tính cho người khác không? (y/n): ")
            if continue_calc.lower() != 'y':
                break
                
        except ValueError:
            print("❌ Vui lòng nhập số hợp lệ!")
        except Exception as e:
            print(f"❌ Có lỗi xảy ra: {e}")
    
    print("Cảm ơn bạn đã sử dụng máy tính BMI! 🙏")

if __name__ == "__main__":
    bmi_calculator()
