"""
Bài 7: Hệ thống quản lý file với Context Managers và Decorators
Chủ đề: Context Managers, Decorators, Property Descriptors, Metaclasses

Mục tiêu: Học các kỹ thuật Python nâng cao và magic methods
"""

import os
import time
import hashlib
import shutil
import json
import threading
import functools
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from contextlib import contextmanager
from abc import ABC, abstractmethod

# DECORATOR PATTERNS
def timing_decorator(func):
    """Decorator để đo thời gian thực thi"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            end_time = time.time()
            execution_time = end_time - start_time
            print(f"⏱️ {func.__name__} executed in {execution_time:.4f} seconds")
            return result
        except Exception as e:
            end_time = time.time()
            execution_time = end_time - start_time
            print(f"❌ {func.__name__} failed after {execution_time:.4f} seconds: {e}")
            raise
    return wrapper

def log_operations(log_file: str = "file_operations.log"):
    """Decorator để ghi log các thao tác file"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            timestamp = datetime.now().isoformat()
            operation = f"{timestamp} - {func.__name__}"
            
            if args:
                # Lấy self (nếu là method) và các tham số
                if hasattr(args[0], '__class__'):
                    operation += f" on {args[0].__class__.__name__}"
                    if len(args) > 1:
                        operation += f" with args: {args[1:]}"
                else:
                    operation += f" with args: {args}"
            
            try:
                result = func(*args, **kwargs)
                operation += " - SUCCESS"
                
                # Ghi log thành công
                with open(log_file, "a", encoding="utf-8") as f:
                    f.write(operation + "\n")
                
                return result
            except Exception as e:
                operation += f" - ERROR: {str(e)}"
                
                # Ghi log lỗi
                with open(log_file, "a", encoding="utf-8") as f:
                    f.write(operation + "\n")
                
                raise
        return wrapper
    return decorator

def retry(max_attempts: int = 3, delay: float = 1.0):
    """Decorator để thử lại khi gặp lỗi"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        print(f"🔄 Attempt {attempt + 1} failed, retrying in {delay}s...")
                        time.sleep(delay)
                    else:
                        print(f"❌ All {max_attempts} attempts failed")
            
            raise last_exception
        return wrapper
    return decorator

# PROPERTY DESCRIPTORS
class ValidatedProperty:
    """Descriptor để validate property"""
    
    def __init__(self, name: str, validator: Callable[[Any], bool], error_message: str):
        self.name = name
        self.validator = validator
        self.error_message = error_message
    
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, f"_{self.name}", None)
    
    def __set__(self, obj, value):
        if not self.validator(value):
            raise ValueError(f"{self.error_message}: {value}")
        setattr(obj, f"_{self.name}", value)
    
    def __delete__(self, obj):
        delattr(obj, f"_{self.name}")

class FileSize:
    """Descriptor để quản lý kích thước file"""
    
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        if obj.path and os.path.exists(obj.path):
            return os.path.getsize(obj.path)
        return 0
    
    def __set__(self, obj, value):
        raise AttributeError("Cannot set file size directly")

class FileModifiedTime:
    """Descriptor để lấy thời gian sửa đổi file"""
    
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        if obj.path and os.path.exists(obj.path):
            timestamp = os.path.getmtime(obj.path)
            return datetime.fromtimestamp(timestamp)
        return None
    
    def __set__(self, obj, value):
        raise AttributeError("Cannot set file modified time directly")

# METACLASS
class FileSystemMeta(type):
    """Metaclass để tự động đăng ký các loại file system objects"""
    
    _registry = {}
    
    def __new__(mcs, name, bases, attrs):
        cls = super().__new__(mcs, name, bases, attrs)
        
        # Tự động đăng ký class
        if name != 'FileSystemObject':
            mcs._registry[name.lower()] = cls
            print(f"🔧 Registered {name} in FileSystemMeta registry")
        
        return cls
    
    @classmethod
    def get_registered_classes(mcs):
        return mcs._registry.copy()

# CONTEXT MANAGERS
class FileManager:
    """Context manager để quản lý file operations"""
    
    def __init__(self, file_path: str, mode: str = 'r', encoding: str = 'utf-8'):
        self.file_path = file_path
        self.mode = mode
        self.encoding = encoding
        self.file_obj = None
        self.backup_path = None
    
    def __enter__(self):
        # Tạo backup nếu file tồn tại và mode là write
        if os.path.exists(self.file_path) and 'w' in self.mode:
            self.backup_path = f"{self.file_path}.backup_{int(time.time())}"
            shutil.copy2(self.file_path, self.backup_path)
            print(f"📋 Created backup: {self.backup_path}")
        
        self.file_obj = open(self.file_path, self.mode, encoding=self.encoding)
        print(f"📂 Opened file: {self.file_path}")
        return self.file_obj
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.file_obj:
            self.file_obj.close()
            print(f"📂 Closed file: {self.file_path}")
        
        # Nếu có lỗi và có backup, restore từ backup
        if exc_type is not None and self.backup_path:
            print(f"❌ Error occurred, restoring from backup")
            shutil.copy2(self.backup_path, self.file_path)
        
        # Xóa backup file nếu thành công
        elif self.backup_path and os.path.exists(self.backup_path):
            os.remove(self.backup_path)
            print(f"🗑️ Removed backup: {self.backup_path}")
        
        # Không suppress exception
        return False

@contextmanager
def directory_context(dir_path: str, create_if_not_exists: bool = True):
    """Context manager để làm việc với thư mục"""
    original_cwd = os.getcwd()
    created_dir = False
    
    try:
        if not os.path.exists(dir_path):
            if create_if_not_exists:
                os.makedirs(dir_path)
                created_dir = True
                print(f"📁 Created directory: {dir_path}")
            else:
                raise FileNotFoundError(f"Directory not found: {dir_path}")
        
        os.chdir(dir_path)
        print(f"📁 Changed to directory: {dir_path}")
        yield dir_path
        
    finally:
        os.chdir(original_cwd)
        print(f"📁 Restored to original directory: {original_cwd}")
        
        # Xóa thư mục nếu đã tạo và rỗng
        if created_dir and os.path.exists(dir_path):
            try:
                os.rmdir(dir_path)
                print(f"🗑️ Removed empty directory: {dir_path}")
            except OSError:
                print(f"📁 Directory not empty, keeping: {dir_path}")

# BASE CLASS với Metaclass
class FileSystemObject(metaclass=FileSystemMeta):
    """Base class cho tất cả file system objects"""
    
    # Sử dụng descriptors
    size = FileSize()
    modified_time = FileModifiedTime()
    
    def __init__(self, path: str):
        self.path = Path(path)
        self.created_at = datetime.now()
        self.access_count = 0
        self._locked = False
    
    def __str__(self):
        return f"{self.__class__.__name__}({self.path})"
    
    def __repr__(self):
        return f"{self.__class__.__name__}(path='{self.path}', size={self.size}, exists={self.exists})"
    
    @property
    def exists(self) -> bool:
        return self.path.exists()
    
    @property
    def name(self) -> str:
        return self.path.name
    
    @property
    def parent(self) -> str:
        return str(self.path.parent)
    
    def lock(self):
        """Khóa object để tránh thay đổi"""
        self._locked = True
        print(f"🔒 Locked {self}")
    
    def unlock(self):
        """Mở khóa object"""
        self._locked = False
        print(f"🔓 Unlocked {self}")
    
    def _check_locked(self):
        """Kiểm tra xem object có bị khóa không"""
        if self._locked:
            raise PermissionError(f"Object is locked: {self}")
    
    @abstractmethod
    def get_info(self) -> Dict:
        """Lấy thông tin chi tiết object"""
        pass

class FileObject(FileSystemObject):
    """Class đại diện cho file"""
    
    # Validated properties
    encoding = ValidatedProperty(
        "encoding", 
        lambda x: isinstance(x, str) and x in ['utf-8', 'ascii', 'latin-1'],
        "Invalid encoding"
    )
    
    def __init__(self, path: str, encoding: str = 'utf-8'):
        super().__init__(path)
        self.encoding = encoding
        self.content_hash = None
        self.content_cache = None
        self.cache_timestamp = None
    
    @timing_decorator
    @log_operations()
    def read(self, use_cache: bool = True) -> str:
        """Đọc nội dung file"""
        self._check_locked()
        self.access_count += 1
        
        if not self.exists:
            raise FileNotFoundError(f"File not found: {self.path}")
        
        # Kiểm tra cache
        if use_cache and self.content_cache and self.cache_timestamp:
            if self.modified_time <= self.cache_timestamp:
                print(f"📋 Using cached content for {self.name}")
                return self.content_cache
        
        with FileManager(str(self.path), 'r', self.encoding) as f:
            content = f.read()
            
            # Cập nhật cache
            self.content_cache = content
            self.cache_timestamp = datetime.now()
            
            return content
    
    @timing_decorator
    @log_operations()
    @retry(max_attempts=3, delay=0.5)
    def write(self, content: str, append: bool = False):
        """Ghi nội dung vào file"""
        self._check_locked()
        
        mode = 'a' if append else 'w'
        
        with FileManager(str(self.path), mode, self.encoding) as f:
            f.write(content)
        
        # Cập nhật hash và cache
        self.content_hash = self.calculate_hash()
        self.content_cache = None  # Invalidate cache
        self.cache_timestamp = None
        
        print(f"✅ {'Appended to' if append else 'Wrote'} file: {self.name}")
    
    @timing_decorator
    def calculate_hash(self, algorithm: str = 'md5') -> str:
        """Tính hash của file"""
        if not self.exists:
            return None
        
        hash_obj = hashlib.new(algorithm)
        
        with open(self.path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hash_obj.update(chunk)
        
        return hash_obj.hexdigest()
    
    @log_operations()
    def copy(self, destination: str, overwrite: bool = False):
        """Sao chép file"""
        self._check_locked()
        
        dest_path = Path(destination)
        
        if dest_path.exists() and not overwrite:
            raise FileExistsError(f"Destination already exists: {destination}")
        
        shutil.copy2(self.path, dest_path)
        print(f"📋 Copied {self.name} to {destination}")
        
        return FileObject(str(dest_path), self.encoding)
    
    @log_operations()
    def move(self, destination: str):
        """Di chuyển file"""
        self._check_locked()
        
        dest_path = Path(destination)
        shutil.move(self.path, dest_path)
        
        old_path = self.path
        self.path = dest_path
        
        print(f"📦 Moved {old_path.name} to {destination}")
    
    @log_operations()
    def delete(self):
        """Xóa file"""
        self._check_locked()
        
        if self.exists:
            os.remove(self.path)
            print(f"🗑️ Deleted file: {self.name}")
        else:
            print(f"⚠️ File not found: {self.name}")
    
    def get_info(self) -> Dict:
        """Lấy thông tin chi tiết file"""
        return {
            'name': self.name,
            'path': str(self.path),
            'size': self.size,
            'encoding': self.encoding,
            'exists': self.exists,
            'modified_time': self.modified_time.isoformat() if self.modified_time else None,
            'created_at': self.created_at.isoformat(),
            'access_count': self.access_count,
            'content_hash': self.content_hash,
            'is_locked': self._locked
        }

class DirectoryObject(FileSystemObject):
    """Class đại diện cho thư mục"""
    
    def __init__(self, path: str):
        super().__init__(path)
        self.file_count = 0
        self.subdirectory_count = 0
        self.total_size = 0
    
    @timing_decorator
    @log_operations()
    def create(self, parents: bool = True):
        """Tạo thư mục"""
        self._check_locked()
        
        if not self.exists:
            if parents:
                self.path.mkdir(parents=True, exist_ok=True)
            else:
                self.path.mkdir()
            print(f"📁 Created directory: {self.name}")
        else:
            print(f"📁 Directory already exists: {self.name}")
    
    @timing_decorator
    def scan(self, recursive: bool = False) -> Dict[str, List]:
        """Quét nội dung thư mục"""
        if not self.exists:
            raise FileNotFoundError(f"Directory not found: {self.path}")
        
        files = []
        directories = []
        total_size = 0
        
        if recursive:
            for item in self.path.rglob('*'):
                if item.is_file():
                    files.append(str(item))
                    total_size += item.stat().st_size
                elif item.is_dir():
                    directories.append(str(item))
        else:
            for item in self.path.iterdir():
                if item.is_file():
                    files.append(str(item))
                    total_size += item.stat().st_size
                elif item.is_dir():
                    directories.append(str(item))
        
        self.file_count = len(files)
        self.subdirectory_count = len(directories)
        self.total_size = total_size
        
        return {
            'files': files,
            'directories': directories,
            'file_count': self.file_count,
            'subdirectory_count': self.subdirectory_count,
            'total_size': total_size
        }
    
    @log_operations()
    def copy(self, destination: str, overwrite: bool = False):
        """Sao chép thư mục"""
        self._check_locked()
        
        dest_path = Path(destination)
        
        if dest_path.exists() and not overwrite:
            raise FileExistsError(f"Destination already exists: {destination}")
        
        if dest_path.exists():
            shutil.rmtree(dest_path)
        
        shutil.copytree(self.path, dest_path)
        print(f"📋 Copied directory {self.name} to {destination}")
        
        return DirectoryObject(str(dest_path))
    
    @log_operations()
    def delete(self, force: bool = False):
        """Xóa thư mục"""
        self._check_locked()
        
        if not self.exists:
            print(f"⚠️ Directory not found: {self.name}")
            return
        
        if force:
            shutil.rmtree(self.path)
            print(f"🗑️ Force deleted directory: {self.name}")
        else:
            try:
                self.path.rmdir()  # Chỉ xóa thư mục rỗng
                print(f"🗑️ Deleted empty directory: {self.name}")
            except OSError:
                print(f"❌ Directory not empty: {self.name}")
                raise
    
    def get_info(self) -> Dict:
        """Lấy thông tin chi tiết thư mục"""
        return {
            'name': self.name,
            'path': str(self.path),
            'exists': self.exists,
            'modified_time': self.modified_time.isoformat() if self.modified_time else None,
            'created_at': self.created_at.isoformat(),
            'access_count': self.access_count,
            'file_count': self.file_count,
            'subdirectory_count': self.subdirectory_count,
            'total_size': self.total_size,
            'is_locked': self._locked
        }

class FileSystemManager:
    """Manager cho các file system operations"""
    
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.objects = {}
        self.operation_history = []
        self._lock = threading.Lock()
    
    def register_object(self, obj: FileSystemObject):
        """Đăng ký object để quản lý"""
        with self._lock:
            self.objects[str(obj.path)] = obj
            print(f"📝 Registered {obj}")
    
    def get_object(self, path: str) -> Optional[FileSystemObject]:
        """Lấy object theo path"""
        return self.objects.get(str(Path(path)))
    
    @contextmanager
    def batch_operations(self, description: str = "Batch operations"):
        """Context manager cho batch operations"""
        start_time = time.time()
        operations_before = len(self.operation_history)
        
        print(f"🔄 Starting batch operations: {description}")
        
        try:
            yield self
            
            end_time = time.time()
            operations_count = len(self.operation_history) - operations_before
            execution_time = end_time - start_time
            
            print(f"✅ Batch operations completed: {operations_count} operations in {execution_time:.4f}s")
            
        except Exception as e:
            end_time = time.time()
            execution_time = end_time - start_time
            print(f"❌ Batch operations failed after {execution_time:.4f}s: {e}")
            raise
    
    def create_file(self, path: str, content: str = "", encoding: str = 'utf-8') -> FileObject:
        """Tạo file mới"""
        file_obj = FileObject(path, encoding)
        
        if content:
            file_obj.write(content)
        
        self.register_object(file_obj)
        return file_obj
    
    def create_directory(self, path: str, parents: bool = True) -> DirectoryObject:
        """Tạo thư mục mới"""
        dir_obj = DirectoryObject(path)
        dir_obj.create(parents)
        
        self.register_object(dir_obj)
        return dir_obj
    
    def get_system_stats(self) -> Dict:
        """Lấy thống kê hệ thống"""
        files = sum(1 for obj in self.objects.values() if isinstance(obj, FileObject))
        directories = sum(1 for obj in self.objects.values() if isinstance(obj, DirectoryObject))
        total_size = sum(obj.size for obj in self.objects.values() if isinstance(obj, FileObject))
        
        return {
            'total_objects': len(self.objects),
            'files': files,
            'directories': directories,
            'total_size': total_size,
            'operation_history_count': len(self.operation_history),
            'registered_classes': FileSystemMeta.get_registered_classes()
        }

def main():
    print("🗂️ HỆ THỐNG QUẢN LÝ FILE VỚI PYTHON NÂNG CAO 🗂️")
    
    # Tạo manager
    fs_manager = FileSystemManager("test_workspace")
    
    print(f"\n🏭 KIỂM TRA METACLASS REGISTRY:")
    print("=" * 50)
    
    # Hiển thị các class đã đăng ký
    registered = FileSystemMeta.get_registered_classes()
    for name, cls in registered.items():
        print(f"📋 {name}: {cls}")
    
    print(f"\n📁 TẠO VÀ QUẢN LÝ THƯ MỤC:")
    print("=" * 40)
    
    # Sử dụng context manager để tạo workspace
    with directory_context("test_workspace"):
        
        # Sử dụng batch operations
        with fs_manager.batch_operations("Creating test files and directories"):
            
            # Tạo thư mục
            docs_dir = fs_manager.create_directory("documents")
            images_dir = fs_manager.create_directory("images")
            backup_dir = fs_manager.create_directory("backup")
            
            # Tạo files
            readme_file = fs_manager.create_file(
                "documents/README.md",
                "# Test Project\n\nThis is a test project for file management system.\n",
                "utf-8"
            )
            
            config_file = fs_manager.create_file(
                "documents/config.json",
                json.dumps({"version": "1.0", "debug": True}, indent=2),
                "utf-8"
            )
            
            # Test file với encoding khác
            try:
                test_file = FileObject("test_latin.txt", "latin-1")
                test_file.write("Test content with special chars: áéíóú")
                fs_manager.register_object(test_file)
            except Exception as e:
                print(f"❌ Error with latin-1 encoding: {e}")
            
            # Test invalid encoding
            try:
                invalid_file = FileObject("test.txt", "invalid-encoding")
            except ValueError as e:
                print(f"✅ Validation worked: {e}")
    
    print(f"\n📖 ĐỌC VÀ GHI FILE:")
    print("=" * 30)
    
    # Đọc file với cache
    content1 = readme_file.read(use_cache=True)
    print(f"📄 Content length: {len(content1)} chars")
    
    # Đọc lại để test cache
    content2 = readme_file.read(use_cache=True)
    
    # Ghi thêm nội dung
    readme_file.write("\n## New Section\n\nAdded content.", append=True)
    
    # Đọc lại sau khi ghi
    content3 = readme_file.read(use_cache=True)
    
    print(f"\n🔐 KIỂM TRA LOCK MECHANISM:")
    print("=" * 40)
    
    # Test lock mechanism
    config_file.lock()
    
    try:
        config_file.write("This should fail")
    except PermissionError as e:
        print(f"✅ Lock working: {e}")
    
    config_file.unlock()
    config_file.write('{"version": "1.1", "debug": false}')
    
    print(f"\n📊 THỐNG KÊ VÀ THÔNG TIN:")
    print("=" * 40)
    
    # Quét thư mục
    docs_scan = docs_dir.scan(recursive=True)
    print(f"📁 Documents directory:")
    print(f"   Files: {docs_scan['file_count']}")
    print(f"   Directories: {docs_scan['subdirectory_count']}")
    print(f"   Total size: {docs_scan['total_size']} bytes")
    
    # Hiển thị thông tin chi tiết
    print(f"\n📋 CHI TIẾT CÁC OBJECT:")
    print("=" * 35)
    
    for obj in [readme_file, config_file, docs_dir]:
        info = obj.get_info()
        print(f"\n{obj.__class__.__name__}: {obj.name}")
        for key, value in info.items():
            print(f"   {key}: {value}")
    
    print(f"\n🔧 TÍNH TOÁN HASH:")
    print("=" * 25)
    
    # Tính hash
    readme_hash = readme_file.calculate_hash('md5')
    config_hash = config_file.calculate_hash('sha256')
    
    print(f"📄 README.md MD5: {readme_hash}")
    print(f"📄 config.json SHA256: {config_hash}")
    
    print(f"\n📋 SAO CHÉP VÀ DI CHUYỂN:")
    print("=" * 35)
    
    # Sao chép file
    readme_copy = readme_file.copy("documents/README_backup.md")
    fs_manager.register_object(readme_copy)
    
    # Sao chép thư mục
    docs_backup = docs_dir.copy("documents_backup")
    fs_manager.register_object(docs_backup)
    
    print(f"\n🗂️ THỐNG KÊ HỆ THỐNG:")
    print("=" * 30)
    
    # Thống kê hệ thống
    stats = fs_manager.get_system_stats()
    print(f"📊 System Statistics:")
    for key, value in stats.items():
        if key == 'registered_classes':
            print(f"   {key}: {len(value)} classes")
        else:
            print(f"   {key}: {value}")
    
    print(f"\n🧹 DỌN DẸP:")
    print("=" * 20)
    
    # Dọn dẹp
    try:
        # Xóa file backup
        readme_copy.delete()
        
        # Xóa thư mục backup (force delete)
        docs_backup.delete(force=True)
        
        # Xóa thư mục rỗng
        backup_dir.delete()
        
    except Exception as e:
        print(f"❌ Cleanup error: {e}")
    
    # Thống kê cuối
    final_stats = fs_manager.get_system_stats()
    print(f"\n📊 FINAL STATISTICS:")
    print(f"   Total objects managed: {final_stats['total_objects']}")
    print(f"   Files: {final_stats['files']}")
    print(f"   Directories: {final_stats['directories']}")

if __name__ == "__main__":
    main()
