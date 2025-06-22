import random
import os
import json
from typing import List, Dict, Optional

class HangmanGame:
    def __init__(self):
        self.categories = {
            "animals": ["cat", "dog", "elephant", "tiger", "giraffe", "monkey", "zebra", "penguin", "kangaroo", "dolphin"],
            "fruits": ["apple", "banana", "orange", "grape", "watermelon", "strawberry", "pineapple", "mango", "kiwi", "peach"],
            "countries": ["vietnam", "japan", "france", "brazil", "australia", "canada", "egypt", "india", "mexico", "sweden"]
        }
        self.word = ""
        self.guessed_letters = set()
        self.attempts_left = 6
        self.category = ""
        self.scores_file = "hangman_scores.json"
        self.scores = self.load_scores()
        
    def load_scores(self) -> Dict:
        """Load high scores from file"""
        if os.path.exists(self.scores_file):
            try:
                with open(self.scores_file, "r") as file:
                    return json.load(file)
            except json.JSONDecodeError:
                return {"high_scores": []}
        return {"high_scores": []}
    
    def save_score(self, player_name: str, word: str, category: str, attempts_left: int):
        """Save score to file"""
        score = len(set(word)) + attempts_left * 2
        
        self.scores["high_scores"].append({
            "player": player_name,
            "word": word,
            "category": category,
            "score": score,
            "attempts_left": attempts_left
        })
        
        # Sort scores and keep top 10
        self.scores["high_scores"] = sorted(
            self.scores["high_scores"], 
            key=lambda x: x["score"], 
            reverse=True
        )[:10]
        
        with open(self.scores_file, "w") as file:
            json.dump(self.scores, file, indent=4)
    
    def select_category(self) -> str:
        """Let user select a category"""
        print("\n=== CHỌN CHỦ ĐỀ ===")
        for i, category in enumerate(self.categories.keys(), 1):
            print(f"{i}. {category.title()}")
        
        while True:
            try:
                choice = int(input("\nNhập số tương ứng với chủ đề (1-3): "))
                if 1 <= choice <= len(self.categories):
                    return list(self.categories.keys())[choice-1]
                else:
                    print("Lựa chọn không hợp lệ!")
            except ValueError:
                print("Vui lòng nhập một số!")
    
    def choose_word(self, category: str) -> str:
        """Choose a random word from the selected category"""
        return random.choice(self.categories[category])
    
    def display_word(self) -> str:
        """Display the word with guessed letters revealed"""
        return ' '.join([letter if letter in self.guessed_letters else '_' for letter in self.word])
    
    def display_hangman(self):
        """Display the hangman based on attempts left"""
        stages = [
            # Final state: head, torso, both arms, both legs
            '''
               --------
               |      |
               |      O
               |     \\|/
               |      |
               |     / \\
               -
            ''',
            # Head, torso, both arms, one leg
            '''
               --------
               |      |
               |      O
               |     \\|/
               |      |
               |     / 
               -
            ''',
            # Head, torso, both arms
            '''
               --------
               |      |
               |      O
               |     \\|/
               |      |
               |      
               -
            ''',
            # Head, torso, one arm
            '''
               --------
               |      |
               |      O
               |     \\|
               |      |
               |     
               -
            ''',
            # Head and torso
            '''
               --------
               |      |
               |      O
               |      |
               |      |
               |     
               -
            ''',
            # Head
            '''
               --------
               |      |
               |      O
               |    
               |      
               |     
               -
            ''',
            # Initial empty state
            '''
               --------
               |      |
               |      
               |    
               |      
               |     
               -
            '''
        ]
        print(stages[self.attempts_left])
    
    def show_high_scores(self):
        """Display high scores"""
        print("\n=== BẢNG XẾP HẠNG ĐIỂM CAO ===")
        if not self.scores["high_scores"]:
            print("Chưa có điểm nào được ghi nhận!")
            return
            
        print(f"{'Hạng':<5}{'Người chơi':<15}{'Từ':<15}{'Chủ đề':<15}{'Điểm':<10}{'Lượt còn lại':<15}")
        print("-" * 70)
        
        for i, score in enumerate(self.scores["high_scores"], 1):
            print(f"{i:<5}{score['player']:<15}{score['word']:<15}{score['category']:<15}{score['score']:<10}{score['attempts_left']:<15}")
    
    def play(self):
        """Main game loop"""
        print("\n🎮 CHÀO MỪNG ĐẾN VỚI GAME HANGMAN 🎮")
        print("Hãy đoán từ bí ẩn trước khi người hình nộm bị treo!")
        
        while True:
            # Game setup
            self.category = self.select_category()
            self.word = self.choose_word(self.category)
            self.guessed_letters = set()
            self.attempts_left = 6
            
            print(f"\n=== CHỦ ĐỀ: {self.category.upper()} ===")
            print(f"Từ bí ẩn có {len(self.word)} chữ cái")
            
            # Game loop
            while self.attempts_left > 0:
                print("\n" + "=" * 30)
                self.display_hangman()
                print(f"Từ hiện tại: {self.display_word()}")
                print(f"Các chữ đã đoán: {', '.join(sorted(self.guessed_letters)) if self.guessed_letters else 'Chưa có'}")
                print(f"Số lần đoán còn lại: {self.attempts_left}")
                
                # Get player's guess
                guess = input("\nNhập một chữ cái: ").lower()
                
                # Validate input
                if len(guess) != 1 or not guess.isalpha():
                    print("Vui lòng nhập một chữ cái hợp lệ!")
                    continue
                    
                if guess in self.guessed_letters:
                    print(f"Bạn đã đoán chữ '{guess}' rồi!")
                    continue
                
                # Add to guessed letters
                self.guessed_letters.add(guess)
                
                # Check if guess is correct
                if guess in self.word:
                    print(f"✓ Đúng rồi! Chữ '{guess}' có trong từ.")
                    
                    # Check if player has won
                    if all(letter in self.guessed_letters for letter in self.word):
                        print("\n🎉 CHÚC MỪNG! BẠN ĐÃ THẮNG! 🎉")
                        print(f"Từ bí ẩn là: {self.word.upper()}")
                        
                        player_name = input("Nhập tên của bạn để lưu điểm: ")
                        self.save_score(player_name, self.word, self.category, self.attempts_left)
                        break
                else:
                    self.attempts_left -= 1
                    print(f"✗ Sai rồi! Chữ '{guess}' không có trong từ.")
                    
                    if self.attempts_left == 0:
                        self.display_hangman()
                        print("\n💀 GAME OVER! BẠN ĐÃ THUA 💀")
                        print(f"Từ bí ẩn là: {self.word.upper()}")
            
            # Ask to play again
            self.show_high_scores()
            play_again = input("\nBạn có muốn chơi lại không? (y/n): ").lower()
            if play_again != 'y':
                print("Cảm ơn đã chơi HANGMAN! Tạm biệt! 👋")
                break

if __name__ == "__main__":
    game = HangmanGame()
    game.play() 