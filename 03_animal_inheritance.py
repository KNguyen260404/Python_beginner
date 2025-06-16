"""
Bài 3: Hệ thống động vật
Chủ đề: Kế thừa (Inheritance) và đa hình (Polymorphism)

Mục tiêu: Học cách tạo lớp cha, lớp con và override phương thức
"""

class Animal:
    """Lớp cha - Động vật"""
    
    def __init__(self, name, species, age, weight):
        self.name = name
        self.species = species
        self.age = age
        self.weight = weight
        self.energy = 100
        self.hunger = 0
        self.happiness = 100
    
    def make_sound(self):
        """Phương thức trừu tượng - sẽ được override ở lớp con"""
        return "Động vật đang kêu..."
    
    def eat(self, food_amount=20):
        """Ăn để tăng năng lượng"""
        self.energy = min(100, self.energy + food_amount)
        self.hunger = max(0, self.hunger - food_amount)
        self.happiness = min(100, self.happiness + 5)
        print(f"{self.name} đã ăn và cảm thấy no hơn! 🍽️")
    
    def sleep(self, hours=8):
        """Ngủ để phục hồi năng lượng"""
        energy_gain = hours * 10
        self.energy = min(100, self.energy + energy_gain)
        self.happiness = min(100, self.happiness + 10)
        print(f"{self.name} đã ngủ {hours} giờ và cảm thấy tươi tỉnh! 😴")
    
    def play(self):
        """Chơi để tăng hạnh phúc nhưng giảm năng lượng"""
        if self.energy >= 20:
            self.energy -= 20
            self.happiness = min(100, self.happiness + 25)
            self.hunger = min(100, self.hunger + 10)
            print(f"{self.name} đang chơi và rất vui! 🎾")
        else:
            print(f"{self.name} quá mệt để chơi! 😴")
    
    def get_status(self):
        """Hiển thị trạng thái hiện tại"""
        print(f"\n🐾 Trạng thái của {self.name}:")
        print(f"   Loài: {self.species}")
        print(f"   Tuổi: {self.age} tuổi")
        print(f"   Cân nặng: {self.weight} kg")
        print(f"   Năng lượng: {self.energy}/100")
        print(f"   Đói: {self.hunger}/100")
        print(f"   Hạnh phúc: {self.happiness}/100")
        
        # Đánh giá tổng quan
        if self.happiness >= 80 and self.energy >= 60:
            mood = "😊 Rất vui vẻ"
        elif self.happiness >= 60:
            mood = "🙂 Khá vui"
        elif self.happiness >= 40:
            mood = "😐 Bình thường"
        else:
            mood = "😢 Buồn"
        
        print(f"   Tâm trạng: {mood}")

class Dog(Animal):
    """Lớp con - Chó"""
    
    def __init__(self, name, breed, age, weight):
        super().__init__(name, "Chó", age, weight)
        self.breed = breed
        self.loyalty = 100
        self.tricks = []
    
    def make_sound(self):
        """Override phương thức từ lớp cha"""
        sounds = ["Gâu gâu! 🐕", "Woof woof!", "Gow gow!"]
        import random
        return random.choice(sounds)
    
    def bark(self):
        """Phương thức đặc biệt của chó"""
        print(f"{self.name}: {self.make_sound()}")
        self.energy -= 5
        self.happiness += 5
    
    def fetch(self):
        """Chơi ném bóng"""
        if self.energy >= 25:
            self.energy -= 25
            self.happiness += 30
            self.loyalty = min(100, self.loyalty + 5)
            print(f"{self.name} đã chạy đi lấy bóng và mang về! 🎾")
        else:
            print(f"{self.name} quá mệt để chạy lấy bóng! 😴")
    
    def learn_trick(self, trick):
        """Học thủ thuật mới"""
        if trick not in self.tricks:
            self.tricks.append(trick)
            self.happiness += 20
            print(f"{self.name} đã học được thủ thuật: {trick}! 🎭")
        else:
            print(f"{self.name} đã biết thủ thuật này rồi!")
    
    def show_trick(self):
        """Biểu diễn thủ thuật"""
        if self.tricks:
            import random
            trick = random.choice(self.tricks)
            print(f"{self.name} đang biểu diễn: {trick}! ⭐")
            self.happiness += 15
            self.energy -= 10
        else:
            print(f"{self.name} chưa biết thủ thuật nào cả!")

class Cat(Animal):
    """Lớp con - Mèo"""
    
    def __init__(self, name, color, age, weight):
        super().__init__(name, "Mèo", age, weight)
        self.color = color
        self.independence = 80
        self.curiosity = 100
    
    def make_sound(self):
        """Override phương thức từ lớp cha"""
        sounds = ["Meow meow! 🐱", "Meo meo!", "Nyan nyan~"]
        import random
        return random.choice(sounds)
    
    def meow(self):
        """Phương thức đặc biệt của mèo"""
        print(f"{self.name}: {self.make_sound()}")
        self.energy -= 3
        self.happiness += 3
    
    def hunt(self):
        """Săn mồi (bản năng tự nhiên)"""
        if self.energy >= 30:
            self.energy -= 30
            self.happiness += 25
            self.curiosity = min(100, self.curiosity + 10)
            print(f"{self.name} đã đi săn và bắt được con chuột! 🐭")
            # Có 50% cơ hội tìm được đồ chơi
            import random
            if random.random() < 0.5:
                toys = ["bóng len", "chuột đồ chơi", "lông vũ"]
                toy = random.choice(toys)
                print(f"{self.name} đã tìm thấy {toy}! 🎀")
        else:
            print(f"{self.name} quá mệt để đi săn! 😴")
    
    def climb(self):
        """Leo trèo"""
        if self.energy >= 20:
            self.energy -= 20
            self.happiness += 20
            self.curiosity = min(100, self.curiosity + 15)
            print(f"{self.name} đã leo lên cây và khám phá xung quanh! 🌳")
        else:
            print(f"{self.name} quá mệt để leo trèo! 😴")
    
    def purr(self):
        """Kêu rung rung khi hài lòng"""
        if self.happiness >= 70:
            print(f"{self.name} đang kêu rung rung hài lòng... Purrrr~ 😸")
            self.happiness += 5
        else:
            print(f"{self.name} không có tâm trạng để kêu rung rung!")

class Bird(Animal):
    """Lớp con - Chim"""
    
    def __init__(self, name, species, age, weight, can_fly=True):
        super().__init__(name, species, age, weight)
        self.can_fly = can_fly
        self.songs = []
        self.flight_distance = 0
    
    def make_sound(self):
        """Override phương thức từ lớp cha"""
        sounds = ["Tweet tweet! 🐦", "Chip chip!", "Tỉnh tỉnh!"]
        import random
        return random.choice(sounds)
    
    def sing(self):
        """Hát"""
        print(f"{self.name}: {self.make_sound()}")
        if self.songs:
            import random
            song = random.choice(self.songs)
            print(f"   Đang hát: {song} 🎵")
        self.happiness += 15
        self.energy -= 5
    
    def fly(self, distance=100):
        """Bay (nếu có thể)"""
        if not self.can_fly:
            print(f"{self.name} không thể bay! 🚫")
            return
        
        if self.energy >= distance // 10:
            self.energy -= distance // 10
            self.flight_distance += distance
            self.happiness += 20
            print(f"{self.name} đã bay được {distance} mét! Tổng cộng đã bay: {self.flight_distance} mét 🕊️")
        else:
            print(f"{self.name} quá mệt để bay! 😴")
    
    def learn_song(self, song):
        """Học bài hát mới"""
        if song not in self.songs:
            self.songs.append(song)
            self.happiness += 25
            print(f"{self.name} đã học được bài hát: {song}! 🎶")
        else:
            print(f"{self.name} đã biết bài hát này rồi!")
    
    def build_nest(self):
        """Làm tổ"""
        if self.energy >= 40:
            self.energy -= 40
            self.happiness += 35
            print(f"{self.name} đã làm một cái tổ đẹp! 🏠")
        else:
            print(f"{self.name} quá mệt để làm tổ! 😴")

class Zoo:
    """Sở thú - quản lý nhiều động vật"""
    
    def __init__(self, name):
        self.name = name
        self.animals = []
        self.visitors = 0
    
    def add_animal(self, animal):
        """Thêm động vật vào sở thú"""
        self.animals.append(animal)
        print(f"Đã thêm {animal.name} ({animal.species}) vào sở thú {self.name}! 🎪")
    
    def feed_all_animals(self):
        """Cho tất cả động vật ăn"""
        print(f"\n🍽️ Giờ ăn tại sở thú {self.name}!")
        for animal in self.animals:
            animal.eat()
    
    def animals_show(self):
        """Biểu diễn của các động vật"""
        print(f"\n🎭 CHƯƠNG TRÌNH BIỂU DIỄN TẠI SỞ THÚ {self.name.upper()}!")
        print("=" * 50)
        
        for animal in self.animals:
            print(f"\n🎯 Tiết mục của {animal.name}:")
            
            # Mỗi loài có cách biểu diễn khác nhau (Polymorphism)
            if isinstance(animal, Dog):
                animal.bark()
                animal.show_trick()
                animal.fetch()
            elif isinstance(animal, Cat):
                animal.meow()
                animal.hunt()
                animal.purr()
            elif isinstance(animal, Bird):
                animal.sing()
                if animal.can_fly:
                    animal.fly(50)
            else:
                print(f"{animal.name}: {animal.make_sound()}")
        
        self.visitors += 50
        print(f"\n👏 Chương trình kết thúc! Số khách tham quan hôm nay: {self.visitors}")
    
    def check_all_animals(self):
        """Kiểm tra sức khỏe tất cả động vật"""
        print(f"\n🏥 KIỂM TRA SỨC KHỎE TẠI SỞ THÚ {self.name.upper()}")
        print("=" * 60)
        
        for animal in self.animals:
            animal.get_status()

# Demo chương trình
def main():
    print("🦁 SỞ THÚ ĐỘNG VẬT 🦁")
    
    # Tạo sở thú
    zoo = Zoo("Thảo Cầm Viên Sài Gòn")
    
    # Tạo các động vật
    dog1 = Dog("Buddy", "Golden Retriever", 3, 30)
    dog1.learn_trick("Ngồi")
    dog1.learn_trick("Lăn")
    dog1.learn_trick("Bắt tay")
    
    cat1 = Cat("Whiskers", "Cam", 2, 4)
    
    bird1 = Bird("Tweety", "Chim hoàng anh", 1, 0.5, True)
    bird1.learn_song("Bài ca mùa xuân")
    bird1.learn_song("Tiếng hót chào ngày mới")
    
    bird2 = Bird("Penguin", "Chim cánh cụt", 5, 25, False)  # Không bay được
    
    # Thêm động vật vào sở thú
    zoo.add_animal(dog1)
    zoo.add_animal(cat1)
    zoo.add_animal(bird1)
    zoo.add_animal(bird2)
    
    # Kiểm tra sức khỏe ban đầu
    zoo.check_all_animals()
    
    # Cho động vật ăn
    zoo.feed_all_animals()
    
    # Biểu diễn
    zoo.animals_show()
    
    # Hoạt động cá nhân
    print(f"\n🎮 CÁC HOẠT ĐỘNG CÁ NHÂN:")
    print("=" * 40)
    
    dog1.play()
    cat1.climb()
    bird1.build_nest()
    bird2.sing()  # Chim cánh cụt cũng có thể hát
    
    # Kiểm tra sức khỏe sau hoạt động
    zoo.check_all_animals()
    
    # Nghỉ ngơi
    print(f"\n😴 GIỜ NGHỈ NGƠI:")
    print("=" * 30)
    for animal in zoo.animals:
        animal.sleep(6)
    
    # Kiểm tra cuối ngày
    print(f"\n📊 BÁO CÁO CUỐI NGÀY:")
    zoo.check_all_animals()

if __name__ == "__main__":
    main()
