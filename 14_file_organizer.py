import os
import shutil
import datetime
import time
import json
import re
from typing import Dict, List, Tuple, Optional, Set, Callable

class FileOrganizer:
    def __init__(self):
        self.config_file = "file_organizer_config.json"
        self.log_file = "file_organizer_log.txt"
        self.config = self.load_config()
        
    def load_config(self) -> Dict:
        """Load configuration from file or create default"""
        default_config = {
            "file_types": {
                "images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp"],
                "documents": [".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".xls", ".xlsx", ".ppt", ".pptx"],
                "audio": [".mp3", ".wav", ".ogg", ".flac", ".aac", ".wma", ".m4a"],
                "video": [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm", ".m4v"],
                "archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"],
                "code": [".py", ".js", ".html", ".css", ".java", ".c", ".cpp", ".php", ".rb", ".go", ".ts"]
            },
            "date_formats": ["yyyy-mm-dd", "yyyy_mm_dd", "dd-mm-yyyy", "mm-dd-yyyy"],
            "custom_rules": []
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as file:
                    return json.load(file)
            except json.JSONDecodeError:
                return default_config
        else:
            # Create default config file
            with open(self.config_file, 'w', encoding='utf-8') as file:
                json.dump(default_config, file, indent=4)
            return default_config
    
    def save_config(self):
        """Save configuration to file"""
        with open(self.config_file, 'w', encoding='utf-8') as file:
            json.dump(self.config, file, indent=4)
    
    def log_action(self, message: str):
        """Log action to log file"""
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(self.log_file, 'a', encoding='utf-8') as file:
            file.write(f"[{timestamp}] {message}\n")
    
    def create_directory(self, path: str) -> bool:
        """Create directory if it doesn't exist"""
        if not os.path.exists(path):
            try:
                os.makedirs(path)
                return True
            except Exception as e:
                self.log_action(f"Lỗi khi tạo thư mục {path}: {e}")
                return False
        return True
    
    def move_file(self, source: str, destination: str) -> bool:
        """Move file from source to destination"""
        try:
            # Create destination directory if it doesn't exist
            dest_dir = os.path.dirname(destination)
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)
                
            # If destination file exists, add a number to the filename
            if os.path.exists(destination):
                filename, extension = os.path.splitext(destination)
                counter = 1
                while os.path.exists(f"{filename}_{counter}{extension}"):
                    counter += 1
                destination = f"{filename}_{counter}{extension}"
                
            shutil.move(source, destination)
            self.log_action(f"Di chuyển: {source} -> {destination}")
            return True
        except Exception as e:
            self.log_action(f"Lỗi khi di chuyển file {source}: {e}")
            return False
    
    def get_file_type(self, filename: str) -> str:
        """Get file type category based on extension"""
        _, extension = os.path.splitext(filename.lower())
        
        for category, extensions in self.config["file_types"].items():
            if extension in extensions:
                return category
                
        return "other"
    
    def get_file_date(self, file_path: str, date_type: str = "modified") -> datetime.datetime:
        """Get file date (created, modified, accessed)"""
        if date_type == "created":
            timestamp = os.path.getctime(file_path)
        elif date_type == "accessed":
            timestamp = os.path.getatime(file_path)
        else:  # modified (default)
            timestamp = os.path.getmtime(file_path)
            
        return datetime.datetime.fromtimestamp(timestamp)
    
    def format_date(self, date: datetime.datetime, format_str: str) -> str:
        """Format date according to specified format"""
        if format_str == "yyyy-mm-dd":
            return date.strftime('%Y-%m-%d')
        elif format_str == "yyyy_mm_dd":
            return date.strftime('%Y_%m_%d')
        elif format_str == "dd-mm-yyyy":
            return date.strftime('%d-%m-%Y')
        elif format_str == "mm-dd-yyyy":
            return date.strftime('%m-%d-%Y')
        else:
            return date.strftime('%Y-%m-%d')  # Default
    
    def organize_by_type(self, source_dir: str, target_dir: str) -> Tuple[int, int]:
        """Organize files by type"""
        if not os.path.isdir(source_dir):
            self.log_action(f"Thư mục nguồn không tồn tại: {source_dir}")
            return 0, 0
            
        self.create_directory(target_dir)
        
        files_moved = 0
        errors = 0
        
        for filename in os.listdir(source_dir):
            source_path = os.path.join(source_dir, filename)
            
            # Skip directories
            if os.path.isdir(source_path):
                continue
                
            file_type = self.get_file_type(filename)
            type_dir = os.path.join(target_dir, file_type)
            self.create_directory(type_dir)
            
            destination = os.path.join(type_dir, filename)
            
            if self.move_file(source_path, destination):
                files_moved += 1
            else:
                errors += 1
                
        return files_moved, errors
    
    def organize_by_date(self, source_dir: str, target_dir: str, date_type: str = "modified", 
                        date_format: str = "yyyy-mm-dd") -> Tuple[int, int]:
        """Organize files by date"""
        if not os.path.isdir(source_dir):
            self.log_action(f"Thư mục nguồn không tồn tại: {source_dir}")
            return 0, 0
            
        self.create_directory(target_dir)
        
        files_moved = 0
        errors = 0
        
        for filename in os.listdir(source_dir):
            source_path = os.path.join(source_dir, filename)
            
            # Skip directories
            if os.path.isdir(source_path):
                continue
                
            file_date = self.get_file_date(source_path, date_type)
            date_str = self.format_date(file_date, date_format)
            
            date_dir = os.path.join(target_dir, date_str)
            self.create_directory(date_dir)
            
            destination = os.path.join(date_dir, filename)
            
            if self.move_file(source_path, destination):
                files_moved += 1
            else:
                errors += 1
                
        return files_moved, errors
    
    def organize_by_name(self, source_dir: str, target_dir: str, pattern: str) -> Tuple[int, int]:
        """Organize files by name pattern"""
        if not os.path.isdir(source_dir):
            self.log_action(f"Thư mục nguồn không tồn tại: {source_dir}")
            return 0, 0
            
        self.create_directory(target_dir)
        
        files_moved = 0
        errors = 0
        
        try:
            regex = re.compile(pattern)
        except re.error:
            self.log_action(f"Mẫu regex không hợp lệ: {pattern}")
            return 0, 0
        
        for filename in os.listdir(source_dir):
            source_path = os.path.join(source_dir, filename)
            
            # Skip directories
            if os.path.isdir(source_path):
                continue
                
            match = regex.search(filename)
            if match:
                # Use the first group as folder name, or "matched" if no group
                folder_name = match.group(1) if match.groups() else "matched"
                folder_dir = os.path.join(target_dir, folder_name)
                self.create_directory(folder_dir)
                
                destination = os.path.join(folder_dir, filename)
                
                if self.move_file(source_path, destination):
                    files_moved += 1
                else:
                    errors += 1
                    
        return files_moved, errors
    
    def organize_by_size(self, source_dir: str, target_dir: str) -> Tuple[int, int]:
        """Organize files by size"""
        if not os.path.isdir(source_dir):
            self.log_action(f"Thư mục nguồn không tồn tại: {source_dir}")
            return 0, 0
            
        self.create_directory(target_dir)
        
        # Size categories in bytes
        size_categories = {
            "tiny": 1024 * 10,        # 0-10KB
            "small": 1024 * 100,      # 10KB-100KB
            "medium": 1024 * 1024,    # 100KB-1MB
            "large": 1024 * 1024 * 10,  # 1MB-10MB
            "huge": float('inf')      # >10MB
        }
        
        files_moved = 0
        errors = 0
        
        for filename in os.listdir(source_dir):
            source_path = os.path.join(source_dir, filename)
            
            # Skip directories
            if os.path.isdir(source_path):
                continue
                
            # Get file size
            file_size = os.path.getsize(source_path)
            
            # Determine size category
            category = "tiny"
            for cat, size_limit in size_categories.items():
                if file_size <= size_limit:
                    category = cat
                    break
                    
            size_dir = os.path.join(target_dir, category)
            self.create_directory(size_dir)
            
            destination = os.path.join(size_dir, filename)
            
            if self.move_file(source_path, destination):
                files_moved += 1
            else:
                errors += 1
                
        return files_moved, errors
    
    def add_custom_rule(self, name: str, pattern: str, target_folder: str):
        """Add custom organization rule"""
        self.config["custom_rules"].append({
            "name": name,
            "pattern": pattern,
            "target_folder": target_folder
        })
        self.save_config()
        self.log_action(f"Đã thêm quy tắc tùy chỉnh: {name}")
    
    def remove_custom_rule(self, index: int) -> bool:
        """Remove custom rule by index"""
        if 0 <= index < len(self.config["custom_rules"]):
            removed = self.config["custom_rules"].pop(index)
            self.save_config()
            self.log_action(f"Đã xóa quy tắc: {removed['name']}")
            return True
        return False
    
    def apply_custom_rules(self, source_dir: str) -> Tuple[int, int]:
        """Apply all custom rules to source directory"""
        if not self.config["custom_rules"]:
            return 0, 0
            
        files_moved = 0
        errors = 0
        
        for rule in self.config["custom_rules"]:
            try:
                pattern = rule["pattern"]
                target = rule["target_folder"]
                
                moved, errs = self.organize_by_name(source_dir, target, pattern)
                files_moved += moved
                errors += errs
                
            except Exception as e:
                self.log_action(f"Lỗi khi áp dụng quy tắc {rule['name']}: {e}")
                errors += 1
                
        return files_moved, errors
    
    def show_statistics(self, source_dir: str):
        """Show statistics about files in directory"""
        if not os.path.isdir(source_dir):
            print(f"Thư mục không tồn tại: {source_dir}")
            return
            
        stats = {
            "total_files": 0,
            "total_size": 0,
            "by_type": {},
            "newest_file": None,
            "oldest_file": None,
            "largest_file": None,
            "smallest_file": None
        }
        
        newest_time = 0
        oldest_time = float('inf')
        largest_size = 0
        smallest_size = float('inf')
        
        for filename in os.listdir(source_dir):
            file_path = os.path.join(source_dir, filename)
            
            if os.path.isdir(file_path):
                continue
                
            # Get file info
            file_size = os.path.getsize(file_path)
            mod_time = os.path.getmtime(file_path)
            file_type = self.get_file_type(filename)
            
            # Update statistics
            stats["total_files"] += 1
            stats["total_size"] += file_size
            
            # Update type statistics
            if file_type not in stats["by_type"]:
                stats["by_type"][file_type] = {"count": 0, "size": 0}
            stats["by_type"][file_type]["count"] += 1
            stats["by_type"][file_type]["size"] += file_size
            
            # Update newest/oldest
            if mod_time > newest_time:
                newest_time = mod_time
                stats["newest_file"] = (filename, mod_time)
                
            if mod_time < oldest_time:
                oldest_time = mod_time
                stats["oldest_file"] = (filename, mod_time)
                
            # Update largest/smallest
            if file_size > largest_size:
                largest_size = file_size
                stats["largest_file"] = (filename, file_size)
                
            if file_size < smallest_size:
                smallest_size = file_size
                stats["smallest_file"] = (filename, file_size)
        
        # Display statistics
        print("\n" + "=" * 50)
        print(f"📊 THỐNG KÊ THƯ MỤC: {source_dir}")
        print("=" * 50)
        
        print(f"\n📁 Tổng số tệp: {stats['total_files']}")
        print(f"💾 Tổng dung lượng: {self.format_size(stats['total_size'])}")
        
        print("\n📋 THỐNG KÊ THEO LOẠI:")
        for file_type, type_stats in stats["by_type"].items():
            print(f"  - {file_type}: {type_stats['count']} tệp ({self.format_size(type_stats['size'])})")
            
        if stats["newest_file"]:
            newest_name, newest_time = stats["newest_file"]
            print(f"\n🆕 Tệp mới nhất: {newest_name} ({datetime.datetime.fromtimestamp(newest_time).strftime('%Y-%m-%d %H:%M:%S')})")
            
        if stats["oldest_file"]:
            oldest_name, oldest_time = stats["oldest_file"]
            print(f"🔙 Tệp cũ nhất: {oldest_name} ({datetime.datetime.fromtimestamp(oldest_time).strftime('%Y-%m-%d %H:%M:%S')})")
            
        if stats["largest_file"]:
            largest_name, largest_size = stats["largest_file"]
            print(f"📈 Tệp lớn nhất: {largest_name} ({self.format_size(largest_size)})")
            
        if stats["smallest_file"]:
            smallest_name, smallest_size = stats["smallest_file"]
            print(f"📉 Tệp nhỏ nhất: {smallest_name} ({self.format_size(smallest_size)})")
            
        print("\n" + "=" * 50)
    
    def format_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes/1024:.2f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes/(1024*1024):.2f} MB"
        else:
            return f"{size_bytes/(1024*1024*1024):.2f} GB"
    
    def show_log(self, lines: int = 10):
        """Show last n lines of log"""
        if not os.path.exists(self.log_file):
            print("Chưa có nhật ký hoạt động.")
            return
            
        with open(self.log_file, 'r', encoding='utf-8') as file:
            log_lines = file.readlines()
            
        print("\n=== NHẬT KÝ HOẠT ĐỘNG GẦN ĐÂY ===")
        for line in log_lines[-lines:]:
            print(line.strip())
    
    def run_cli(self):
        """Run the file organizer CLI"""
        print("\n📁 TRÌNH SẮP XẾP TỆP 📂")
        print("Công cụ sắp xếp và tổ chức tệp tự động")
        
        while True:
            print("\n" + "=" * 50)
            print("1. Sắp xếp theo loại tệp")
            print("2. Sắp xếp theo ngày")
            print("3. Sắp xếp theo kích thước")
            print("4. Sắp xếp theo tên (mẫu regex)")
            print("5. Thêm quy tắc tùy chỉnh")
            print("6. Xem quy tắc tùy chỉnh")
            print("7. Xóa quy tắc tùy chỉnh")
            print("8. Áp dụng tất cả quy tắc tùy chỉnh")
            print("9. Xem thống kê thư mục")
            print("10. Xem nhật ký hoạt động")
            print("11. Thoát")
            
            choice = input("\nChọn một tùy chọn (1-11): ")
            
            if choice == "1":
                source = input("Nhập đường dẫn thư mục nguồn: ")
                target = input("Nhập đường dẫn thư mục đích: ")
                
                if os.path.isdir(source):
                    moved, errors = self.organize_by_type(source, target)
                    print(f"\n✅ Đã di chuyển {moved} tệp ({errors} lỗi)")
                else:
                    print("❌ Thư mục nguồn không tồn tại!")
                    
            elif choice == "2":
                source = input("Nhập đường dẫn thư mục nguồn: ")
                target = input("Nhập đường dẫn thư mục đích: ")
                
                print("\nLoại ngày:")
                print("1. Ngày sửa đổi")
                print("2. Ngày tạo")
                print("3. Ngày truy cập")
                date_choice = input("Chọn loại ngày (1-3): ")
                
                date_type = "modified"
                if date_choice == "2":
                    date_type = "created"
                elif date_choice == "3":
                    date_type = "accessed"
                
                print("\nĐịnh dạng ngày:")
                for i, fmt in enumerate(self.config["date_formats"], 1):
                    print(f"{i}. {fmt}")
                fmt_choice = input(f"Chọn định dạng (1-{len(self.config['date_formats'])}): ")
                
                try:
                    fmt_idx = int(fmt_choice) - 1
                    if 0 <= fmt_idx < len(self.config["date_formats"]):
                        date_format = self.config["date_formats"][fmt_idx]
                    else:
                        date_format = "yyyy-mm-dd"
                except ValueError:
                    date_format = "yyyy-mm-dd"
                
                if os.path.isdir(source):
                    moved, errors = self.organize_by_date(source, target, date_type, date_format)
                    print(f"\n✅ Đã di chuyển {moved} tệp ({errors} lỗi)")
                else:
                    print("❌ Thư mục nguồn không tồn tại!")
                    
            elif choice == "3":
                source = input("Nhập đường dẫn thư mục nguồn: ")
                target = input("Nhập đường dẫn thư mục đích: ")
                
                if os.path.isdir(source):
                    moved, errors = self.organize_by_size(source, target)
                    print(f"\n✅ Đã di chuyển {moved} tệp ({errors} lỗi)")
                else:
                    print("❌ Thư mục nguồn không tồn tại!")
                    
            elif choice == "4":
                source = input("Nhập đường dẫn thư mục nguồn: ")
                target = input("Nhập đường dẫn thư mục đích: ")
                pattern = input("Nhập mẫu regex (sử dụng nhóm bắt buộc để tạo thư mục): ")
                
                if os.path.isdir(source):
                    moved, errors = self.organize_by_name(source, target, pattern)
                    print(f"\n✅ Đã di chuyển {moved} tệp ({errors} lỗi)")
                else:
                    print("❌ Thư mục nguồn không tồn tại!")
                    
            elif choice == "5":
                name = input("Nhập tên cho quy tắc: ")
                pattern = input("Nhập mẫu regex: ")
                target = input("Nhập thư mục đích: ")
                
                self.add_custom_rule(name, pattern, target)
                print(f"✅ Đã thêm quy tắc '{name}'")
                
            elif choice == "6":
                if not self.config["custom_rules"]:
                    print("Chưa có quy tắc tùy chỉnh nào!")
                else:
                    print("\n=== QUY TẮC TÙY CHỈNH ===")
                    for i, rule in enumerate(self.config["custom_rules"], 1):
                        print(f"{i}. {rule['name']}")
                        print(f"   - Mẫu: {rule['pattern']}")
                        print(f"   - Thư mục: {rule['target_folder']}")
                        
            elif choice == "7":
                if not self.config["custom_rules"]:
                    print("Chưa có quy tắc tùy chỉnh nào!")
                else:
                    print("\n=== QUY TẮC TÙY CHỈNH ===")
                    for i, rule in enumerate(self.config["custom_rules"], 1):
                        print(f"{i}. {rule['name']}")
                        
                    idx = input("\nNhập số thứ tự quy tắc muốn xóa: ")
                    try:
                        idx = int(idx) - 1
                        if self.remove_custom_rule(idx):
                            print("✅ Đã xóa quy tắc thành công!")
                        else:
                            print("❌ Số thứ tự không hợp lệ!")
                    except ValueError:
                        print("❌ Vui lòng nhập một số!")
                        
            elif choice == "8":
                source = input("Nhập đường dẫn thư mục nguồn: ")
                
                if not self.config["custom_rules"]:
                    print("Chưa có quy tắc tùy chỉnh nào!")
                elif os.path.isdir(source):
                    moved, errors = self.apply_custom_rules(source)
                    print(f"\n✅ Đã di chuyển {moved} tệp ({errors} lỗi)")
                else:
                    print("❌ Thư mục nguồn không tồn tại!")
                    
            elif choice == "9":
                source = input("Nhập đường dẫn thư mục cần phân tích: ")
                if os.path.isdir(source):
                    self.show_statistics(source)
                else:
                    print("❌ Thư mục không tồn tại!")
                    
            elif choice == "10":
                lines = input("Số dòng nhật ký muốn xem (mặc định 10): ")
                try:
                    lines = int(lines)
                except ValueError:
                    lines = 10
                self.show_log(lines)
                
            elif choice == "11":
                print("Cảm ơn bạn đã sử dụng trình sắp xếp tệp!")
                break
                
            else:
                print("❌ Lựa chọn không hợp lệ!")

if __name__ == "__main__":
    organizer = FileOrganizer()
    organizer.run_cli()