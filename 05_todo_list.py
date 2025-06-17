import json
import os
from datetime import datetime

class TodoList:
    def __init__(self, filename="todos.json"):
        self.filename = filename
        self.todos = self.load_todos()
    
    def load_todos(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as file:
                    return json.load(file)
            except:
                return []
        return []
    
    def save_todos(self):
        with open(self.filename, 'w', encoding='utf-8') as file:
            json.dump(self.todos, file, ensure_ascii=False, indent=2)
    
    def add_todo(self, task, priority="medium"):
        todo = {
            "id": len(self.todos) + 1,
            "task": task,
            "completed": False,
            "priority": priority,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.todos.append(todo)
        self.save_todos()
        print(f"✅ Đã thêm: {task}")
    
    def view_todos(self):
        if not self.todos:
            print("📝 Danh sách trống!")
            return
        
        print("\n=== DANH SÁCH CÔNG VIỆC ===")
        for todo in self.todos:
            status = "✅" if todo["completed"] else "❌"
            priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}
            emoji = priority_emoji.get(todo["priority"], "⚪")
            print(f"{todo['id']}. {status} {emoji} {todo['task']} ({todo['priority']})")
    
    def complete_todo(self, todo_id):
        for todo in self.todos:
            if todo["id"] == todo_id:
                todo["completed"] = True
                self.save_todos()
                print(f"🎉 Đã hoàn thành: {todo['task']}")
                return
        print("Không tìm thấy công việc!")
    
    def delete_todo(self, todo_id):
        for i, todo in enumerate(self.todos):
            if todo["id"] == todo_id:
                removed = self.todos.pop(i)
                # Cập nhật lại ID
                for j, remaining_todo in enumerate(self.todos):
                    remaining_todo["id"] = j + 1
                self.save_todos()
                print(f"🗑️ Đã xóa: {removed['task']}")
                return
        print("Không tìm thấy công việc!")
    
    def run(self):
        print("=== TODO LIST ===")
        
        while True:
            print("\n1. Xem danh sách")
            print("2. Thêm công việc")
            print("3. Hoàn thành công việc")
            print("4. Xóa công việc")
            print("5. Thoát")
            
            choice = input("\nChọn chức năng (1-5): ")
            
            if choice == '1':
                self.view_todos()
                
            elif choice == '2':
                task = input("Nhập công việc: ")
                print("Mức độ ưu tiên:")
                print("1. Cao (high)")
                print("2. Trung bình (medium)")
                print("3. Thấp (low)")
                priority_choice = input("Chọn mức độ (1-3, mặc định 2): ") or "2"
                priority_map = {"1": "high", "2": "medium", "3": "low"}
                priority = priority_map.get(priority_choice, "medium")
                self.add_todo(task, priority)
                
            elif choice == '3':
                self.view_todos()
                try:
                    todo_id = int(input("Nhập ID công việc cần hoàn thành: "))
                    self.complete_todo(todo_id)
                except ValueError:
                    print("ID không hợp lệ!")
                    
            elif choice == '4':
                self.view_todos()
                try:
                    todo_id = int(input("Nhập ID công việc cần xóa: "))
                    self.delete_todo(todo_id)
                except ValueError:
                    print("ID không hợp lệ!")
                    
            elif choice == '5':
                print("Tạm biệt!")
                break
            else:
                print("Lựa chọn không hợp lệ!")

if __name__ == "__main__":
    todo_app = TodoList()
    todo_app.run()
