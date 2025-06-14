import tkinter as tk
from tkinter import messagebox, ttk
import random
import json
import os
from enum import Enum
from typing import List, Tuple, Dict
import threading
import time

class Direction(Enum):
    UP = (-1, 0)
    DOWN = (1, 0)
    LEFT = (0, -1)
    RIGHT = (0, 1)

class GameState(Enum):
    MENU = 1
    PLAYING = 2
    PAUSED = 3
    GAME_OVER = 4
    HIGH_SCORES = 5

class SnakeGame:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🐍 Snake Game Advanced")
        self.root.resizable(False, False)
        
        # Game settings
        self.BOARD_WIDTH = 20
        self.BOARD_HEIGHT = 20
        self.CELL_SIZE = 25
        self.GAME_SPEED = 150  # milliseconds
        
        # Game state
        self.state = GameState.MENU
        self.snake = [(10, 10)]
        self.direction = Direction.RIGHT
        self.food = None
        self.score = 0
        self.level = 1
        self.high_scores = self.load_high_scores()
        
        # Colors
        self.COLORS = {
            'background': '#1a1a1a',
            'snake_head': '#4CAF50',
            'snake_body': '#8BC34A',
            'food': '#F44336',
            'special_food': '#FFD700',
            'text': '#FFFFFF',
            'button': '#2196F3'
        }
        
        self.setup_gui()
        self.create_menu()
    
    def setup_gui(self):
        # Main frame
        self.main_frame = tk.Frame(self.root, bg=self.COLORS['background'])
        self.main_frame.pack(padx=10, pady=10)
        
        # Title
        self.title_label = tk.Label(
            self.main_frame,
            text="🐍 SNAKE GAME ADVANCED",
            font=('Arial', 24, 'bold'),
            fg=self.COLORS['text'],
            bg=self.COLORS['background']
        )
        self.title_label.pack(pady=10)
        
        # Game canvas
        canvas_width = self.BOARD_WIDTH * self.CELL_SIZE
        canvas_height = self.BOARD_HEIGHT * self.CELL_SIZE
        
        self.canvas = tk.Canvas(
            self.main_frame,
            width=canvas_width,
            height=canvas_height,
            bg=self.COLORS['background'],
            highlightthickness=2,
            highlightcolor=self.COLORS['snake_head']
        )
        
        # Info frame
        self.info_frame = tk.Frame(self.main_frame, bg=self.COLORS['background'])
        
        self.score_label = tk.Label(
            self.info_frame,
            text="Score: 0",
            font=('Arial', 14, 'bold'),
            fg=self.COLORS['text'],
            bg=self.COLORS['background']
        )
        self.score_label.pack(side=tk.LEFT, padx=10)
        
        self.level_label = tk.Label(
            self.info_frame,
            text="Level: 1",
            font=('Arial', 14, 'bold'),
            fg=self.COLORS['text'],
            bg=self.COLORS['background']
        )
        self.level_label.pack(side=tk.LEFT, padx=10)
        
        self.speed_label = tk.Label(
            self.info_frame,
            text="Speed: Normal",
            font=('Arial', 14, 'bold'),
            fg=self.COLORS['text'],
            bg=self.COLORS['background']
        )
        self.speed_label.pack(side=tk.LEFT, padx=10)
        
        # Controls frame
        self.controls_frame = tk.Frame(self.main_frame, bg=self.COLORS['background'])
        
        controls_text = "🎮 Controls: ↑↓←→ to move, SPACE to pause, R to restart"
        self.controls_label = tk.Label(
            self.controls_frame,
            text=controls_text,
            font=('Arial', 10),
            fg=self.COLORS['text'],
            bg=self.COLORS['background']
        )
        self.controls_label.pack()
        
        # Bind keys
        self.root.bind('<Key>', self.on_key_press)
        self.root.focus_set()
    
    def create_menu(self):
        self.menu_frame = tk.Frame(self.main_frame, bg=self.COLORS['background'])
        
        # Game modes
        tk.Label(
            self.menu_frame,
            text="🎮 Select Game Mode:",
            font=('Arial', 16, 'bold'),
            fg=self.COLORS['text'],
            bg=self.COLORS['background']
        ).pack(pady=10)
        
        modes = [
            ("🐌 Easy (Slow)", 200),
            ("🐍 Normal", 150),
            ("⚡ Hard (Fast)", 100),
            ("🚀 Extreme", 50)
        ]
        
        for mode_name, speed in modes:
            btn = tk.Button(
                self.menu_frame,
                text=mode_name,
                font=('Arial', 12),
                bg=self.COLORS['button'],
                fg='white',
                width=20,
                command=lambda s=speed: self.start_game(s)
            )
            btn.pack(pady=5)
        
        # High scores button
        tk.Button(
            self.menu_frame,
            text="🏆 High Scores",
            font=('Arial', 12),
            bg='#FF9800',
            fg='white',
            width=20,
            command=self.show_high_scores
        ).pack(pady=5)
        
        # Quit button
        tk.Button(
            self.menu_frame,
            text="🚪 Quit",
            font=('Arial', 12),
            bg='#F44336',
            fg='white',
            width=20,
            command=self.root.quit
        ).pack(pady=5)
        
        self.menu_frame.pack(pady=20)
    
    def start_game(self, speed):
        self.GAME_SPEED = speed
        self.state = GameState.PLAYING
        self.reset_game()
        
        # Hide menu, show game
        self.menu_frame.pack_forget()
        if hasattr(self, 'high_score_frame'):
            self.high_score_frame.pack_forget()
        
        self.canvas.pack(pady=10)
        self.info_frame.pack()
        self.controls_frame.pack(pady=5)
        
        self.generate_food()
        self.game_loop()
    
    def reset_game(self):
        self.snake = [(10, 10)]
        self.direction = Direction.RIGHT
        self.score = 0
        self.level = 1
        self.food = None
        self.special_food = None
        self.update_display()
    
    def generate_food(self):
        while True:
            food_pos = (
                random.randint(0, self.BOARD_WIDTH - 1),
                random.randint(0, self.BOARD_HEIGHT - 1)
            )
            if food_pos not in self.snake:
                self.food = food_pos
                
                # 10% chance for special food (worth more points)
                self.special_food = random.random() < 0.1
                break
    
    def move_snake(self):
        if self.state != GameState.PLAYING:
            return
        
        head = self.snake[0]
        dy, dx = self.direction.value
        new_head = (head[0] + dy, head[1] + dx)
        
        # Check collisions
        if (new_head[0] < 0 or new_head[0] >= self.BOARD_HEIGHT or
            new_head[1] < 0 or new_head[1] >= self.BOARD_WIDTH or
            new_head in self.snake):
            self.game_over()
            return
        
        self.snake.insert(0, new_head)
        
        # Check food consumption
        if new_head == self.food:
            points = 20 if self.special_food else 10
            self.score += points * self.level
            
            # Level up every 100 points
            new_level = (self.score // 100) + 1
            if new_level > self.level:
                self.level = new_level
                self.GAME_SPEED = max(50, self.GAME_SPEED - 10)  # Increase speed
            
            self.generate_food()
        else:
            self.snake.pop()  # Remove tail if no food eaten
        
        self.update_display()
    
    def update_display(self):
        self.canvas.delete("all")
        
        # Draw snake
        for i, (y, x) in enumerate(self.snake):
            color = self.COLORS['snake_head'] if i == 0 else self.COLORS['snake_body']
            x1, y1 = x * self.CELL_SIZE, y * self.CELL_SIZE
            x2, y2 = x1 + self.CELL_SIZE, y1 + self.CELL_SIZE
            
            self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline='white')
            
            # Add eyes to head
            if i == 0:
                eye_size = 4
                eye_offset = 6
                if self.direction == Direction.RIGHT:
                    eye1_x, eye1_y = x1 + eye_offset, y1 + eye_offset
                    eye2_x, eye2_y = x1 + eye_offset, y2 - eye_offset - eye_size
                elif self.direction == Direction.LEFT:
                    eye1_x, eye1_y = x2 - eye_offset - eye_size, y1 + eye_offset
                    eye2_x, eye2_y = x2 - eye_offset - eye_size, y2 - eye_offset - eye_size
                elif self.direction == Direction.UP:
                    eye1_x, eye1_y = x1 + eye_offset, y2 - eye_offset - eye_size
                    eye2_x, eye2_y = x2 - eye_offset - eye_size, y2 - eye_offset - eye_size
                else:  # DOWN
                    eye1_x, eye1_y = x1 + eye_offset, y1 + eye_offset
                    eye2_x, eye2_y = x2 - eye_offset - eye_size, y1 + eye_offset
                
                self.canvas.create_oval(eye1_x, eye1_y, eye1_x + eye_size, eye1_y + eye_size, fill='white')
                self.canvas.create_oval(eye2_x, eye2_y, eye2_x + eye_size, eye2_y + eye_size, fill='white')
        
        # Draw food
        if self.food:
            y, x = self.food
            x1, y1 = x * self.CELL_SIZE, y * self.CELL_SIZE
            x2, y2 = x1 + self.CELL_SIZE, y1 + self.CELL_SIZE
            
            color = self.COLORS['special_food'] if self.special_food else self.COLORS['food']
            self.canvas.create_oval(x1 + 2, y1 + 2, x2 - 2, y2 - 2, fill=color, outline='white', width=2)
            
            # Add sparkle effect for special food
            if self.special_food:
                center_x, center_y = (x1 + x2) // 2, (y1 + y2) // 2
                sparkle_points = [
                    center_x, center_y - 8,
                    center_x + 3, center_y - 3,
                    center_x + 8, center_y,
                    center_x + 3, center_y + 3,
                    center_x, center_y + 8,
                    center_x - 3, center_y + 3,
                    center_x - 8, center_y,
                    center_x - 3, center_y - 3
                ]
                self.canvas.create_polygon(sparkle_points, fill='white', outline='')
        
        # Update labels
        self.score_label.config(text=f"Score: {self.score}")
        self.level_label.config(text=f"Level: {self.level}")
        
        speed_text = "Extreme" if self.GAME_SPEED <= 50 else "Hard" if self.GAME_SPEED <= 100 else "Normal" if self.GAME_SPEED <= 150 else "Easy"
        self.speed_label.config(text=f"Speed: {speed_text}")
    
    def game_loop(self):
        if self.state == GameState.PLAYING:
            self.move_snake()
            self.root.after(self.GAME_SPEED, self.game_loop)
    
    def game_over(self):
        self.state = GameState.GAME_OVER
        
        # Check if it's a high score
        is_high_score = self.is_high_score(self.score)
        
        message = f"🎮 Game Over!\n\n🏆 Final Score: {self.score}\n📊 Level Reached: {self.level}"
        if is_high_score:
            message += "\n\n🎉 New High Score!"
            name = tk.simpledialog.askstring("High Score!", "Enter your name:")
            if name:
                self.save_high_score(name, self.score, self.level)
        
        choice = messagebox.askyesno("Game Over", message + "\n\nPlay again?")
        
        if choice:
            self.start_game(self.GAME_SPEED)
        else:
            self.back_to_menu()
    
    def on_key_press(self, event):
        key = event.keysym
        
        if self.state == GameState.PLAYING:
            if key == 'Up' and self.direction != Direction.DOWN:
                self.direction = Direction.UP
            elif key == 'Down' and self.direction != Direction.UP:
                self.direction = Direction.DOWN
            elif key == 'Left' and self.direction != Direction.RIGHT:
                self.direction = Direction.LEFT
            elif key == 'Right' and self.direction != Direction.LEFT:
                self.direction = Direction.RIGHT
            elif key == 'space':
                self.toggle_pause()
            elif key == 'r':
                self.start_game(self.GAME_SPEED)
        
        elif key == 'Escape':
            self.back_to_menu()
    
    def toggle_pause(self):
        if self.state == GameState.PLAYING:
            self.state = GameState.PAUSED
            self.canvas.create_text(
                self.BOARD_WIDTH * self.CELL_SIZE // 2,
                self.BOARD_HEIGHT * self.CELL_SIZE // 2,
                text="⏸️ PAUSED\nPress SPACE to continue",
                fill=self.COLORS['text'],
                font=('Arial', 16, 'bold'),
                justify=tk.CENTER,
                tags="pause"
            )
        elif self.state == GameState.PAUSED:
            self.state = GameState.PLAYING
            self.canvas.delete("pause")
            self.game_loop()
    
    def load_high_scores(self) -> List[Dict]:
        try:
            if os.path.exists("snake_scores.json"):
                with open("snake_scores.json", 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        return []
    
    def save_high_score(self, name: str, score: int, level: int):
        score_entry = {
            'name': name,
            'score': score,
            'level': level,
            'date': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        self.high_scores.append(score_entry)
        self.high_scores.sort(key=lambda x: x['score'], reverse=True)
        self.high_scores = self.high_scores[:10]  # Keep top 10
        
        try:
            with open("snake_scores.json", 'w', encoding='utf-8') as f:
                json.dump(self.high_scores, f, indent=2, ensure_ascii=False)
        except:
            pass
    
    def is_high_score(self, score: int) -> bool:
        if len(self.high_scores) < 10:
            return True
        return score > self.high_scores[-1]['score']
    
    def show_high_scores(self):
        self.menu_frame.pack_forget()
        
        self.high_score_frame = tk.Frame(self.main_frame, bg=self.COLORS['background'])
        
        tk.Label(
            self.high_score_frame,
            text="🏆 HIGH SCORES",
            font=('Arial', 20, 'bold'),
            fg=self.COLORS['text'],
            bg=self.COLORS['background']
        ).pack(pady=10)
        
        if self.high_scores:
            for i, score_data in enumerate(self.high_scores, 1):
                score_text = f"{i:2d}. {score_data['name']:<15} Score: {score_data['score']:>6} Level: {score_data['level']:>2} ({score_data['date']})"
                tk.Label(
                    self.high_score_frame,
                    text=score_text,
                    font=('Courier', 10),
                    fg=self.COLORS['text'],
                    bg=self.COLORS['background']
                ).pack()
        else:
            tk.Label(
                self.high_score_frame,
                text="No high scores yet!",
                font=('Arial', 12),
                fg=self.COLORS['text'],
                bg=self.COLORS['background']
            ).pack(pady=20)
        
        tk.Button(
            self.high_score_frame,
            text="🔙 Back to Menu",
            font=('Arial', 12),
            bg=self.COLORS['button'],
            fg='white',
            command=self.back_to_menu
        ).pack(pady=20)
        
        self.high_score_frame.pack()
    
    def back_to_menu(self):
        self.state = GameState.MENU
        
        # Hide all game elements
        self.canvas.pack_forget()
        self.info_frame.pack_forget()
        self.controls_frame.pack_forget()
        if hasattr(self, 'high_score_frame'):
            self.high_score_frame.pack_forget()
        
        # Show menu
        self.menu_frame.pack(pady=20)
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    # Import thư viện cần thiết cho dialog
    try:
        import tkinter.simpledialog as simpledialog
        tk.simpledialog = simpledialog
    except ImportError:
        pass
    
    game = SnakeGame()
    game.run()
