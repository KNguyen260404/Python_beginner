import random

def guess_number_game():
    print("=== GAME ĐOÁN SỐ ===")
    print("Tôi đã nghĩ ra một số từ 1 đến 100!")
    print("Hãy thử đoán xem!")
    
    secret_number = random.randint(1, 100)
    attempts = 0
    max_attempts = 7
    
    while attempts < max_attempts:
        try:
            guess = int(input(f"\nLần đoán {attempts + 1}/{max_attempts}: "))
            attempts += 1
            
            if guess == secret_number:
                print(f"🎉 Chúc mừng! Bạn đã đoán đúng số {secret_number}!")
                print(f"Bạn đã thắng trong {attempts} lần đoán!")
                break
            elif guess < secret_number:
                print("📈 Số bạn đoán nhỏ hơn! Thử số lớn hơn.")
            else:
                print("📉 Số bạn đoán lớn hơn! Thử số nhỏ hơn.")
                
            if attempts == max_attempts:
                print(f"💔 Bạn đã hết lượt! Số đúng là: {secret_number}")
                
        except ValueError:
            print("Vui lòng nhập một số nguyên hợp lệ!")
            attempts -= 1
    
    play_again = input("\nBạn có muốn chơi lại không? (y/n): ")
    if play_again.lower() == 'y':
        guess_number_game()
    else:
        print("Cảm ơn bạn đã chơi!")

if __name__ == "__main__":
    guess_number_game()
