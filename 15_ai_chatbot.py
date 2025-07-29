import os
import json
import random
import re
import time
import datetime
import threading
from typing import Dict, List, Tuple, Optional, Union, Any

try:
    import pyttsx3 # type: ignore
    import speech_recognition as sr # type: ignore
    VOICE_AVAILABLE = True
except ImportError:
    VOICE_AVAILABLE = False

class AIAssistant:
    def __init__(self):
        self.name = "PyBot"
        self.version = "1.0.0"
        self.creator = "Python Beginner"
        self.data_dir = "chatbot_data"
        self.knowledge_file = os.path.join(self.data_dir, "knowledge_base.json")
        self.conversations_file = os.path.join(self.data_dir, "conversations.json")
        self.settings_file = os.path.join(self.data_dir, "settings.json")
        
        # Ensure data directory exists
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        
        # Load knowledge base, conversations and settings
        self.knowledge_base = self.load_knowledge_base()
        self.conversations = self.load_conversations()
        self.settings = self.load_settings()
        
        # Current conversation
        self.current_conversation_id = None
        self.current_conversation = []
        
        # Voice recognition and synthesis
        self.voice_enabled = self.settings.get("voice_enabled", False) and VOICE_AVAILABLE
        self.voice_engine = None
        self.recognizer = None
        
        if self.voice_enabled:
            self.initialize_voice()
    
    def initialize_voice(self):
        """Initialize voice recognition and synthesis"""
        try:
            self.voice_engine = pyttsx3.init()
            self.recognizer = sr.Recognizer()
            
            # Set voice properties from settings
            voice_id = self.settings.get("voice_id", None)
            if voice_id:
                voices = self.voice_engine.getProperty('voices')
                for voice in voices:
                    if voice.id == voice_id:
                        self.voice_engine.setProperty('voice', voice.id)
                        break
            
            # Set rate and volume
            self.voice_engine.setProperty('rate', self.settings.get("voice_rate", 150))
            self.voice_engine.setProperty('volume', self.settings.get("voice_volume", 1.0))
            
        except Exception as e:
            print(f"Lỗi khi khởi tạo giọng nói: {e}")
            self.voice_enabled = False
    
    def speak(self, text: str):
        """Speak the given text"""
        if self.voice_enabled and self.voice_engine:
            try:
                self.voice_engine.say(text)
                self.voice_engine.runAndWait()
            except Exception as e:
                print(f"Lỗi khi phát giọng nói: {e}")
    
    def listen(self) -> str:
        """Listen for voice input and convert to text"""
        if not self.voice_enabled or not self.recognizer:
            return ""
            
        try:
            with sr.Microphone() as source:
                print("Đang lắng nghe...")
                self.recognizer.adjust_for_ambient_noise(source)
                audio = self.recognizer.listen(source, timeout=5)
                
                try:
                    text = self.recognizer.recognize_google(audio, language="vi-VN")
                    print(f"Bạn nói: {text}")
                    return text
                except sr.UnknownValueError:
                    print("Không nhận diện được giọng nói")
                    return ""
                except sr.RequestError as e:
                    print(f"Lỗi khi nhận diện giọng nói: {e}")
                    return ""
        except Exception as e:
            print(f"Lỗi khi lắng nghe: {e}")
            return ""
    
    def load_knowledge_base(self) -> Dict:
        """Load knowledge base from file or create a new one"""
        default_knowledge = {
            "facts": [
                {"id": 1, "topic": "python", "content": "Python là ngôn ngữ lập trình bậc cao, dễ học và linh hoạt."},
                {"id": 2, "topic": "ai", "content": "AI (Trí tuệ nhân tạo) là khả năng của máy tính mô phỏng trí thông minh con người."},
                {"id": 3, "topic": "chatbot", "content": "Chatbot là chương trình máy tính được thiết kế để tương tác với người dùng thông qua hội thoại."}
            ],
            "commands": [
                {"command": "thời tiết", "description": "Hiển thị thông tin thời tiết", "response": "Tôi không có khả năng truy cập dữ liệu thời tiết thực tế."},
                {"command": "giờ", "description": "Hiển thị thời gian hiện tại", "response": None},
                {"command": "trợ giúp", "description": "Hiển thị danh sách lệnh", "response": None}
            ],
            "responses": {
                "greeting": ["Xin chào!", "Chào bạn!", "Rất vui được gặp bạn!"],
                "farewell": ["Tạm biệt!", "Hẹn gặp lại!", "Chúc một ngày tốt lành!"],
                "thanks": ["Không có gì!", "Rất vui được giúp đỡ!", "Đó là nhiệm vụ của tôi!"],
                "unknown": ["Tôi không hiểu. Bạn có thể nói rõ hơn không?", "Xin lỗi, tôi không hiểu ý bạn.", "Tôi chưa được lập trình để hiểu điều đó."]
            }
        }
        
        if os.path.exists(self.knowledge_file):
            try:
                with open(self.knowledge_file, 'r', encoding='utf-8') as file:
                    return json.load(file)
            except json.JSONDecodeError:
                return default_knowledge
        else:
            # Create default knowledge base
            with open(self.knowledge_file, 'w', encoding='utf-8') as file:
                json.dump(default_knowledge, file, indent=4, ensure_ascii=False)
            return default_knowledge
    
    def load_conversations(self) -> Dict:
        """Load conversations from file or create a new one"""
        default_conversations = {
            "conversations": []
        }
        
        if os.path.exists(self.conversations_file):
            try:
                with open(self.conversations_file, 'r', encoding='utf-8') as file:
                    return json.load(file)
            except json.JSONDecodeError:
                return default_conversations
        else:
            # Create default conversations file
            with open(self.conversations_file, 'w', encoding='utf-8') as file:
                json.dump(default_conversations, file, indent=4, ensure_ascii=False)
            return default_conversations
    
    def load_settings(self) -> Dict:
        """Load settings from file or create a new one"""
        default_settings = {
            "username": "Người dùng",
            "theme": "light",
            "voice_enabled": False,
            "voice_rate": 150,
            "voice_volume": 1.0,
            "voice_id": None,
            "language": "vi-VN",
            "max_conversation_history": 50,
            "auto_save": True
        }
        
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as file:
                    return json.load(file)
            except json.JSONDecodeError:
                return default_settings
        else:
            # Create default settings file
            with open(self.settings_file, 'w', encoding='utf-8') as file:
                json.dump(default_settings, file, indent=4, ensure_ascii=False)
            return default_settings
    
    def save_knowledge_base(self):
        """Save knowledge base to file"""
        with open(self.knowledge_file, 'w', encoding='utf-8') as file:
            json.dump(self.knowledge_base, file, indent=4, ensure_ascii=False)
    
    def save_conversations(self):
        """Save conversations to file"""
        with open(self.conversations_file, 'w', encoding='utf-8') as file:
            json.dump(self.conversations, file, indent=4, ensure_ascii=False)
    
    def save_settings(self):
        """Save settings to file"""
        with open(self.settings_file, 'w', encoding='utf-8') as file:
            json.dump(self.settings, file, indent=4, ensure_ascii=False)
    
    def start_new_conversation(self) -> str:
        """Start a new conversation and return its ID"""
        # Save current conversation if exists
        if self.current_conversation_id and self.current_conversation:
            self.save_current_conversation()
        
        # Create new conversation
        conversation_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        self.current_conversation_id = conversation_id
        self.current_conversation = []
        
        return conversation_id
    
    def save_current_conversation(self):
        """Save current conversation to history"""
        if not self.current_conversation_id or not self.current_conversation:
            return
            
        # Find if conversation already exists
        existing_conv = None
        for conv in self.conversations["conversations"]:
            if conv["id"] == self.current_conversation_id:
                existing_conv = conv
                break
        
        if existing_conv:
            # Update existing conversation
            existing_conv["messages"] = self.current_conversation
            existing_conv["last_updated"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        else:
            # Add new conversation
            self.conversations["conversations"].append({
                "id": self.current_conversation_id,
                "created": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "messages": self.current_conversation
            })
        
        # Limit the number of saved conversations
        max_history = self.settings.get("max_conversation_history", 50)
        if len(self.conversations["conversations"]) > max_history:
            # Sort by last_updated and keep only the latest ones
            self.conversations["conversations"] = sorted(
                self.conversations["conversations"],
                key=lambda x: x["last_updated"],
                reverse=True
            )[:max_history]
        
        # Save to file
        self.save_conversations()
    
    def add_message(self, sender: str, content: str):
        """Add a message to the current conversation"""
        if not self.current_conversation_id:
            self.start_new_conversation()
            
        message = {
            "sender": sender,
            "content": content,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self.current_conversation.append(message)
        
        # Auto-save if enabled
        if self.settings.get("auto_save", True):
            self.save_current_conversation()
    
    def get_conversation_history(self, conversation_id: Optional[str] = None) -> List[Dict]:
        """Get conversation history by ID or current conversation"""
        if conversation_id is None:
            return self.current_conversation
            
        for conv in self.conversations["conversations"]:
            if conv["id"] == conversation_id:
                return conv["messages"]
                
        return []
    
    def list_conversations(self) -> List[Dict]:
        """List all saved conversations"""
        # Return a simplified list with id, created date and message count
        return [
            {
                "id": conv["id"],
                "created": conv["created"],
                "last_updated": conv["last_updated"],
                "message_count": len(conv["messages"])
            }
            for conv in self.conversations["conversations"]
        ]
    
    def load_conversation(self, conversation_id: str) -> bool:
        """Load a conversation by ID"""
        for conv in self.conversations["conversations"]:
            if conv["id"] == conversation_id:
                self.current_conversation_id = conversation_id
                self.current_conversation = conv["messages"]
                return True
                
        return False
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation by ID"""
        for i, conv in enumerate(self.conversations["conversations"]):
            if conv["id"] == conversation_id:
                del self.conversations["conversations"][i]
                
                # If current conversation is deleted, reset it
                if self.current_conversation_id == conversation_id:
                    self.current_conversation_id = None
                    self.current_conversation = []
                
                self.save_conversations()
                return True
                
        return False
    
    def add_knowledge(self, topic: str, content: str) -> int:
        """Add new knowledge to the knowledge base"""
        # Generate new ID
        new_id = 1
        if self.knowledge_base["facts"]:
            new_id = max(fact["id"] for fact in self.knowledge_base["facts"]) + 1
            
        # Add new fact
        self.knowledge_base["facts"].append({
            "id": new_id,
            "topic": topic.lower(),
            "content": content
        })
        
        # Save knowledge base
        self.save_knowledge_base()
        
        return new_id
    
    def get_knowledge(self, topic: str) -> List[Dict]:
        """Get knowledge by topic"""
        return [
            fact for fact in self.knowledge_base["facts"]
            if topic.lower() in fact["topic"].lower()
        ]
    
    def delete_knowledge(self, knowledge_id: int) -> bool:
        """Delete knowledge by ID"""
        for i, fact in enumerate(self.knowledge_base["facts"]):
            if fact["id"] == knowledge_id:
                del self.knowledge_base["facts"][i]
                self.save_knowledge_base()
                return True
                
        return False
    
    def add_command(self, command: str, description: str, response: Optional[str] = None):
        """Add a new command to the knowledge base"""
        # Check if command already exists
        for cmd in self.knowledge_base["commands"]:
            if cmd["command"] == command:
                cmd["description"] = description
                cmd["response"] = response
                self.save_knowledge_base()
                return
        
        # Add new command
        self.knowledge_base["commands"].append({
            "command": command,
            "description": description,
            "response": response
        })
        
        # Save knowledge base
        self.save_knowledge_base()
    
    def get_command(self, command: str) -> Optional[Dict]:
        """Get command by name"""
        for cmd in self.knowledge_base["commands"]:
            if cmd["command"] == command:
                return cmd
                
        return None
    
    def delete_command(self, command: str) -> bool:
        """Delete command by name"""
        for i, cmd in enumerate(self.knowledge_base["commands"]):
            if cmd["command"] == command:
                del self.knowledge_base["commands"][i]
                self.save_knowledge_base()
                return True
                
        return False
    
    def process_command(self, command: str) -> str:
        """Process a command and return the response"""
        # Check built-in commands first
        if command == "giờ":
            return f"Bây giờ là {datetime.datetime.now().strftime('%H:%M:%S')} ngày {datetime.datetime.now().strftime('%d/%m/%Y')}"
            
        elif command == "trợ giúp":
            help_text = "Các lệnh có sẵn:\n"
            for cmd in self.knowledge_base["commands"]:
                help_text += f"- {cmd['command']}: {cmd['description']}\n"
            return help_text
            
        # Check custom commands
        cmd = self.get_command(command)
        if cmd:
            if cmd["response"]:
                return cmd["response"]
            else:
                # Command exists but has no predefined response
                return f"Lệnh '{command}' được nhận diện nhưng không có phản hồi được cấu hình."
                
        return None
    
    def get_response_by_type(self, response_type: str) -> str:
        """Get a random response by type"""
        responses = self.knowledge_base["responses"].get(response_type, [])
        if responses:
            return random.choice(responses)
        return ""
    
    def is_greeting(self, message: str) -> bool:
        """Check if message is a greeting"""
        greetings = ["xin chào", "chào", "hi ", "hello", "hey", "hola"]
        message = message.lower()
        
        for greeting in greetings:
            if greeting in message:
                return True
                
        return False
    
    def is_farewell(self, message: str) -> bool:
        """Check if message is a farewell"""
        farewells = ["tạm biệt", "bye", "goodbye", "gặp lại sau", "hẹn gặp lại"]
        message = message.lower()
        
        for farewell in farewells:
            if farewell in message:
                return True
                
        return False
    
    def is_thanks(self, message: str) -> bool:
        """Check if message is a thank you"""
        thanks = ["cảm ơn", "cám ơn", "thank", "tks", "thanks"]
        message = message.lower()
        
        for thank in thanks:
            if thank in message:
                return True
                
        return False
    
    def is_command(self, message: str) -> Optional[str]:
        """Check if message is a command and return the command name"""
        # Check if message starts with a command prefix
        if message.startswith("/") or message.startswith("!"):
            command = message[1:].strip().lower()
            
            # Check if it's a valid command
            for cmd in self.knowledge_base["commands"]:
                if cmd["command"] == command:
                    return command
        
        # Check if message contains command keywords
        message_lower = message.lower()
        for cmd in self.knowledge_base["commands"]:
            if cmd["command"] in message_lower:
                # Make sure it's a standalone word
                pattern = r'\b' + re.escape(cmd["command"]) + r'\b'
                if re.search(pattern, message_lower):
                    return cmd["command"]
                    
        return None
    
    def search_knowledge_base(self, query: str) -> List[Dict]:
        """Search the knowledge base for relevant information"""
        query = query.lower()
        results = []
        
        # Search in facts
        for fact in self.knowledge_base["facts"]:
            # Check topic
            if query in fact["topic"].lower():
                results.append({
                    "type": "fact",
                    "relevance": 2,  # High relevance for topic match
                    "data": fact
                })
                continue
                
            # Check content
            if query in fact["content"].lower():
                results.append({
                    "type": "fact",
                    "relevance": 1,  # Medium relevance for content match
                    "data": fact
                })
                
        # Sort by relevance
        results.sort(key=lambda x: x["relevance"], reverse=True)
        
        return results
    
    def generate_response(self, message: str) -> str:
        """Generate a response to the user's message"""
        # Check for special message types
        if self.is_greeting(message):
            return self.get_response_by_type("greeting")
            
        if self.is_farewell(message):
            return self.get_response_by_type("farewell")
            
        if self.is_thanks(message):
            return self.get_response_by_type("thanks")
            
        # Check for commands
        command = self.is_command(message)
        if command:
            cmd_response = self.process_command(command)
            if cmd_response:
                return cmd_response
        
        # Search knowledge base
        search_results = self.search_knowledge_base(message)
        if search_results:
            # Return the most relevant fact
            return search_results[0]["data"]["content"]
        
        # If no response generated, return unknown response
        return self.get_response_by_type("unknown")
    
    def chat(self, message: str) -> str:
        """Process a chat message and return a response"""
        # Add user message to conversation
        self.add_message("user", message)
        
        # Generate response
        response = self.generate_response(message)
        
        # Add assistant response to conversation
        self.add_message("assistant", response)
        
        return response
    
    def update_settings(self, new_settings: Dict):
        """Update user settings"""
        self.settings.update(new_settings)
        self.save_settings()
        
        # Reinitialize voice if settings changed
        if "voice_enabled" in new_settings or "voice_id" in new_settings or \
           "voice_rate" in new_settings or "voice_volume" in new_settings:
            self.voice_enabled = self.settings.get("voice_enabled", False) and VOICE_AVAILABLE
            if self.voice_enabled:
                self.initialize_voice()
    
    def run_cli(self):
        """Run the chatbot in CLI mode"""
        print(f"\n🤖 {self.name} v{self.version} - AI Assistant")
        print(f"Được tạo bởi {self.creator}")
        print("\nHãy bắt đầu trò chuyện! (Gõ 'thoát' để kết thúc)")
        
        # Start a new conversation
        self.start_new_conversation()
        
        # Initial greeting
        initial_greeting = f"Xin chào {self.settings.get('username', 'Người dùng')}! Tôi là {self.name}, trợ lý AI của bạn. Tôi có thể giúp gì cho bạn hôm nay?"
        print(f"\n🤖 {self.name}: {initial_greeting}")
        self.speak(initial_greeting)
        self.add_message("assistant", initial_greeting)
        
        # Main chat loop
        while True:
            # Get user input
            if self.voice_enabled:
                print("\nBạn có thể nói hoặc gõ tin nhắn (gõ 'giọng nói' để chuyển đổi chế độ nhập):")
                user_input = input("👤 Bạn: ")
                
                if user_input.lower() == "giọng nói":
                    voice_input = self.listen()
                    if voice_input:
                        user_input = voice_input
                    else:
                        print("Không nhận diện được giọng nói, vui lòng gõ tin nhắn.")
                        continue
            else:
                user_input = input("\n👤 Bạn: ")
            
            # Check for exit command
            if user_input.lower() in ["thoát", "exit", "quit", "bye"]:
                farewell = "Cảm ơn đã trò chuyện! Tạm biệt và hẹn gặp lại!"
                print(f"\n🤖 {self.name}: {farewell}")
                self.speak(farewell)
                break
            
            # Process special commands
            if user_input.startswith("/"):
                parts = user_input[1:].split(" ", 1)
                command = parts[0].lower()
                
                if command == "help":
                    print("\n=== HƯỚNG DẪN ===")
                    print("/help - Hiển thị trợ giúp này")
                    print("/voice - Bật/tắt chế độ giọng nói")
                    print("/history - Xem lịch sử cuộc trò chuyện")
                    print("/clear - Xóa cuộc trò chuyện hiện tại")
                    print("/learn <chủ đề> <nội dung> - Thêm kiến thức mới")
                    print("/forget <id> - Xóa kiến thức")
                    print("/knowledge <chủ đề> - Tìm kiếm kiến thức")
                    print("/settings - Xem cài đặt")
                    print("/name <tên mới> - Đổi tên người dùng")
                    continue
                
                elif command == "voice" and VOICE_AVAILABLE:
                    self.voice_enabled = not self.voice_enabled
                    self.update_settings({"voice_enabled": self.voice_enabled})
                    status = "bật" if self.voice_enabled else "tắt"
                    print(f"\nĐã {status} chế độ giọng nói.")
                    continue
                
                elif command == "history":
                    print("\n=== LỊCH SỬ CUỘC TRÒ CHUYỆN ===")
                    history = self.get_conversation_history()
                    for msg in history:
                        sender = "🤖 Bot" if msg["sender"] == "assistant" else "👤 Bạn"
                        print(f"[{msg['timestamp']}] {sender}: {msg['content']}")
                    continue
                
                elif command == "clear":
                    self.start_new_conversation()
                    print("\nĐã xóa cuộc trò chuyện hiện tại.")
                    continue
                
                elif command == "learn" and len(parts) > 1:
                    try:
                        learn_parts = parts[1].split(" ", 1)
                        topic = learn_parts[0]
                        content = learn_parts[1]
                        knowledge_id = self.add_knowledge(topic, content)
                        print(f"\nĐã thêm kiến thức mới với ID {knowledge_id}.")
                    except IndexError:
                        print("\nCú pháp không đúng. Sử dụng: /learn <chủ đề> <nội dung>")
                    continue
                
                elif command == "forget" and len(parts) > 1:
                    try:
                        knowledge_id = int(parts[1])
                        if self.delete_knowledge(knowledge_id):
                            print(f"\nĐã xóa kiến thức với ID {knowledge_id}.")
                        else:
                            print(f"\nKhông tìm thấy kiến thức với ID {knowledge_id}.")
                    except ValueError:
                        print("\nID không hợp lệ. Sử dụng: /forget <id>")
                    continue
                
                elif command == "knowledge" and len(parts) > 1:
                    topic = parts[1]
                    facts = self.get_knowledge(topic)
                    print(f"\n=== KIẾN THỨC VỀ '{topic}' ===")
                    if facts:
                        for fact in facts:
                            print(f"ID {fact['id']}: {fact['content']}")
                    else:
                        print(f"Không tìm thấy kiến thức về '{topic}'.")
                    continue
                
                elif command == "settings":
                    print("\n=== CÀI ĐẶT ===")
                    for key, value in self.settings.items():
                        print(f"{key}: {value}")
                    continue
                
                elif command == "name" and len(parts) > 1:
                    new_name = parts[1]
                    self.update_settings({"username": new_name})
                    print(f"\nĐã đổi tên người dùng thành '{new_name}'.")
                    continue
            
            # Regular chat message
            if not user_input.strip():
                continue
                
            # Generate and display response
            response = self.chat(user_input)
            print(f"\n🤖 {self.name}: {response}")
            
            # Speak response if voice is enabled
            self.speak(response)
        
        # Save conversation before exiting
        self.save_current_conversation()

if __name__ == "__main__":
    assistant = AIAssistant()
    assistant.run_cli()