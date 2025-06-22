import re
import string
import json
import os
from collections import Counter
from typing import Dict, List, Tuple

class TextAnalyzer:
    def __init__(self):
        self.text = ""
        self.words = []
        self.sentences = []
        self.paragraphs = []
        self.word_count = 0
        self.sentence_count = 0
        self.paragraph_count = 0
        self.char_count = 0
        self.history_file = "text_analysis_history.json"
        self.history = self.load_history()
        
    def load_history(self) -> List[Dict]:
        """Load analysis history from file"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r", encoding="utf-8") as file:
                    return json.load(file)
            except json.JSONDecodeError:
                return []
        return []
    
    def save_history(self, title: str, summary: Dict):
        """Save analysis to history"""
        self.history.append({
            "title": title,
            "summary": summary
        })
        
        # Keep only last 10 analyses
        if len(self.history) > 10:
            self.history = self.history[-10:]
            
        with open(self.history_file, "w", encoding="utf-8") as file:
            json.dump(self.history, file, indent=4)
    
    def load_text(self, text: str):
        """Load text for analysis"""
        self.text = text
        
        # Split into paragraphs
        self.paragraphs = [p for p in text.split("\n\n") if p.strip()]
        self.paragraph_count = len(self.paragraphs)
        
        # Split into sentences
        self.sentences = re.split(r'[.!?]+', text)
        self.sentences = [s.strip() for s in self.sentences if s.strip()]
        self.sentence_count = len(self.sentences)
        
        # Split into words
        self.words = re.findall(r'\b[a-zA-Z0-9_\u00C0-\u1EF9]+\b', text.lower())
        self.word_count = len(self.words)
        
        # Count characters
        self.char_count = len(text)
    
    def load_from_file(self, file_path: str):
        """Load text from file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                self.load_text(file.read())
            return True
        except Exception as e:
            print(f"Lỗi khi đọc file: {e}")
            return False
    
    def get_word_frequency(self, limit: int = 10) -> List[Tuple[str, int]]:
        """Get word frequency"""
        # Remove common stop words
        stop_words = {"và", "là", "của", "có", "trong", "cho", "không", "với", "này", "đó", "các", "những"}
        filtered_words = [word for word in self.words if word not in stop_words and len(word) > 1]
        
        # Count word frequency
        word_counts = Counter(filtered_words)
        return word_counts.most_common(limit)
    
    def calculate_readability(self) -> Dict:
        """Calculate readability metrics"""
        if not self.words or not self.sentences:
            return {
                "flesch_reading_ease": 0,
                "difficulty": "N/A"
            }
        
        # Average words per sentence
        avg_words_per_sentence = self.word_count / max(1, self.sentence_count)
        
        # Average syllables per word (rough estimation for Vietnamese)
        syllable_count = 0
        for word in self.words:
            # Simple estimation: count vowel groups
            vowels = "aeiouyàáâãèéêìíòóôõùúýăâêôơưưởợộếềểễốồổỗớờởợụủứừửữ"
            syllable_count += len(re.findall(r'[' + vowels + ']+', word))
        
        avg_syllables_per_word = syllable_count / max(1, self.word_count)
        
        # Flesch Reading Ease (adapted)
        # Higher score = easier to read (0-100)
        flesch = 206.835 - (1.015 * avg_words_per_sentence) - (84.6 * avg_syllables_per_word)
        flesch = max(0, min(100, flesch))
        
        # Determine difficulty
        if flesch >= 90:
            difficulty = "Rất dễ đọc"
        elif flesch >= 80:
            difficulty = "Dễ đọc"
        elif flesch >= 70:
            difficulty = "Khá dễ đọc"
        elif flesch >= 60:
            difficulty = "Trung bình"
        elif flesch >= 50:
            difficulty = "Khá khó đọc"
        elif flesch >= 30:
            difficulty = "Khó đọc"
        else:
            difficulty = "Rất khó đọc"
            
        return {
            "flesch_reading_ease": round(flesch, 2),
            "avg_words_per_sentence": round(avg_words_per_sentence, 2),
            "avg_syllables_per_word": round(avg_syllables_per_word, 2),
            "difficulty": difficulty
        }
    
    def estimate_sentiment(self) -> Dict:
        """Estimate text sentiment (very simple approach)"""
        # Simple sentiment dictionary (would be expanded in real application)
        positive_words = {"tốt", "hay", "tuyệt", "vui", "thích", "yêu", "thành công", "hạnh phúc", 
                         "xinh", "đẹp", "giỏi", "thông minh", "tuyệt vời", "xuất sắc"}
        negative_words = {"tệ", "buồn", "ghét", "thất bại", "kém", "xấu", "khó", "sai", 
                         "chán", "tồi", "dở", "hỏng", "đáng sợ", "kinh khủng"}
        
        positive_count = sum(1 for word in self.words if word in positive_words)
        negative_count = sum(1 for word in self.words if word in negative_words)
        
        # Calculate sentiment score (-1 to 1)
        total = positive_count + negative_count
        if total == 0:
            sentiment_score = 0
        else:
            sentiment_score = (positive_count - negative_count) / total
            
        # Determine sentiment category
        if sentiment_score >= 0.5:
            sentiment = "Tích cực"
        elif sentiment_score >= 0.1:
            sentiment = "Hơi tích cực"
        elif sentiment_score > -0.1:
            sentiment = "Trung lập"
        elif sentiment_score > -0.5:
            sentiment = "Hơi tiêu cực"
        else:
            sentiment = "Tiêu cực"
            
        return {
            "sentiment_score": round(sentiment_score, 2),
            "sentiment": sentiment,
            "positive_words": positive_count,
            "negative_words": negative_count
        }
    
    def analyze(self, title: str = "Untitled") -> Dict:
        """Perform full text analysis"""
        if not self.text:
            return {"error": "Không có văn bản để phân tích"}
            
        # Basic statistics
        basic_stats = {
            "word_count": self.word_count,
            "sentence_count": self.sentence_count,
            "paragraph_count": self.paragraph_count,
            "character_count": self.char_count
        }
        
        # Word frequency
        word_freq = self.get_word_frequency(10)
        
        # Readability
        readability = self.calculate_readability()
        
        # Sentiment
        sentiment = self.estimate_sentiment()
        
        # Compile results
        results = {
            "title": title,
            "basic_stats": basic_stats,
            "word_frequency": dict(word_freq),
            "readability": readability,
            "sentiment": sentiment
        }
        
        # Save to history
        self.save_history(title, results)
        
        return results
    
    def display_results(self, results: Dict):
        """Display analysis results"""
        print("\n" + "=" * 50)
        print(f"📊 KẾT QUẢ PHÂN TÍCH VĂN BẢN: {results['title']}")
        print("=" * 50)
        
        # Basic stats
        stats = results["basic_stats"]
        print("\n📝 THỐNG KÊ CƠ BẢN:")
        print(f"📊 Số từ: {stats['word_count']}")
        print(f"📊 Số câu: {stats['sentence_count']}")
        print(f"📊 Số đoạn: {stats['paragraph_count']}")
        print(f"📊 Số ký tự: {stats['character_count']}")
        
        # Word frequency
        print("\n📈 TẦN SUẤT TỪ (TOP 10):")
        for word, count in results["word_frequency"].items():
            print(f"   {word}: {count}")
        
        # Readability
        read = results["readability"]
        print("\n📖 ĐỘ KHÓ VĂN BẢN:")
        print(f"📊 Điểm đọc Flesch: {read['flesch_reading_ease']}")
        print(f"📊 Độ khó: {read['difficulty']}")
        print(f"📊 Trung bình từ/câu: {read.get('avg_words_per_sentence', 'N/A')}")
        print(f"📊 Trung bình âm tiết/từ: {read.get('avg_syllables_per_word', 'N/A')}")
        
        # Sentiment
        sent = results["sentiment"]
        print("\n😊 PHÂN TÍCH CẢM XÚC:")
        print(f"📊 Điểm cảm xúc: {sent['sentiment_score']}")
        print(f"📊 Đánh giá: {sent['sentiment']}")
        print(f"📊 Từ tích cực: {sent['positive_words']}")
        print(f"📊 Từ tiêu cực: {sent['negative_words']}")
        
        print("\n" + "=" * 50)
    
    def show_history(self):
        """Display analysis history"""
        if not self.history:
            print("Chưa có lịch sử phân tích nào!")
            return
            
        print("\n=== LỊCH SỬ PHÂN TÍCH ===")
        for i, entry in enumerate(self.history, 1):
            stats = entry["summary"]["basic_stats"]
            sentiment = entry["summary"]["sentiment"]["sentiment"]
            print(f"{i}. {entry['title']} - {stats['word_count']} từ - Cảm xúc: {sentiment}")
    
    def run_cli(self):
        """Run the text analyzer CLI"""
        print("\n🔍 PHÂN TÍCH VĂN BẢN 📊")
        print("Công cụ phân tích văn bản tiếng Việt")
        
        while True:
            print("\n" + "=" * 50)
            print("1. Nhập văn bản trực tiếp")
            print("2. Đọc văn bản từ file")
            print("3. Xem lịch sử phân tích")
            print("4. Thoát")
            
            choice = input("\nChọn một tùy chọn (1-4): ")
            
            if choice == "1":
                print("\nNhập văn bản của bạn (nhấn Enter hai lần để kết thúc):")
                lines = []
                while True:
                    line = input()
                    if not line and lines and not lines[-1]:
                        break
                    lines.append(line)
                
                text = "\n".join(lines)
                if text.strip():
                    title = input("Nhập tiêu đề cho phân tích này: ")
                    self.load_text(text)
                    results = self.analyze(title)
                    self.display_results(results)
                else:
                    print("Văn bản trống!")
                    
            elif choice == "2":
                file_path = input("Nhập đường dẫn đến file văn bản: ")
                if self.load_from_file(file_path):
                    title = input("Nhập tiêu đề cho phân tích này: ")
                    results = self.analyze(title)
                    self.display_results(results)
                    
            elif choice == "3":
                self.show_history()
                
                if self.history:
                    view_details = input("\nXem chi tiết phân tích? Nhập số thứ tự (hoặc 0 để quay lại): ")
                    try:
                        idx = int(view_details) - 1
                        if 0 <= idx < len(self.history):
                            self.display_results(self.history[idx]["summary"])
                    except ValueError:
                        pass
                    
            elif choice == "4":
                print("Cảm ơn bạn đã sử dụng công cụ phân tích văn bản!")
                break
                
            else:
                print("Lựa chọn không hợp lệ!")

if __name__ == "__main__":
    analyzer = TextAnalyzer()
    analyzer.run_cli() 