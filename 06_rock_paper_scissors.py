import random

def get_computer_choice():
    choices = ["rock", "paper", "scissors"]
    return random.choice(choices)

def get_winner(player_choice, computer_choice):
    if player_choice == computer_choice:
        return "tie"
    
    win_conditions = {
        "rock": "scissors",
        "paper": "rock", 
        "scissors": "paper"
    }
    
    if win_conditions[player_choice] == computer_choice:
        return "player"
    else:
        return "computer"

def display_choice(choice):
    emojis = {
        "rock": "🪨",
        "paper": "📄", 
        "scissors": "✂️"
    }
    return f"{choice.capitalize()} {emojis[choice]}"

def rock_paper_scissors():
    print("=== OẰN TÙ TÌ ===")
    print("Chọn: rock (đá), paper (giấy), scissors (kéo)")
    
    player_score = 0
    computer_score = 0
    games_played = 0
    
    while True:
        print(f"\n📊 Tỷ số: Bạn {player_score} - {computer_score} Máy")
        player_input = input("\nNhập lựa chọn (rock/paper/scissors) hoặc 'q' để thoát: ").lower()
        
        if player_input == 'q':
            break
        
        if player_input not in ["rock", "paper", "scissors"]:
            print("Lựa chọn không hợp lệ! Hãy chọn rock, paper, hoặc scissors.")
            continue
        
        computer_choice = get_computer_choice()
        
        print(f"\n🎯 Bạn chọn: {display_choice(player_input)}")
        print(f"🤖 Máy chọn: {display_choice(computer_choice)}")
        
        result = get_winner(player_input, computer_choice)
        games_played += 1
        
        if result == "tie":
            print("🤝 Hòa!")
        elif result == "player":
            print("🎉 Bạn thắng!")
            player_score += 1
        else:
            print("😔 Máy thắng!")
            computer_score += 1
    
    # Hiển thị kết quả cuối game
    print(f"\n=== KẾT QUÁ CUỐI GAME ===")
    print(f"🎮 Tổng số ván: {games_played}")
    print(f"📊 Tỷ số cuối: Bạn {player_score} - {computer_score} Máy")
    
    if player_score > computer_score:
        print("🏆 Chúc mừng! Bạn thắng tổng thể!")
    elif computer_score > player_score:
        print("🤖 Máy thắng tổng thể!")
    else:
        print("🤝 Tổng thể hòa!")
    
    if games_played > 0:
        win_rate = (player_score / games_played) * 100
        print(f"📈 Tỷ lệ thắng của bạn: {win_rate:.1f}%")
    
    print("Cảm ơn bạn đã chơi!")

if __name__ == "__main__":
    rock_paper_scissors()
