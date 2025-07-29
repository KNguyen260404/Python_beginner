import tkinter as tk
from tkinter import messagebox, simpledialog, Menu, Frame, Label, Button
import sqlite3
import datetime
import os
import chess # type: ignore
import chess.svg # type: ignore
from PIL import Image, ImageTk # type: ignore
from cairosvg import svg2png # type: ignore
from io import BytesIO

class ChessGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Chess Game")
        self.root.geometry("800x700")
        self.root.configure(bg="#2c3e50")
        
        # Initialize the chess board
        self.board = chess.Board()
        self.selected_square = None
        self.game_over = False
        self.white_player = "Player 1"
        self.black_player = "Player 2"
        self.moves_history = []
        
        # Create database if it doesn't exist
        self.create_database()
        
        # Create UI components
        self.create_menu()
        self.create_main_frame()
        self.create_info_frame()
        self.create_moves_frame()
        
        # Draw the initial board
        self.update_board()
    
    def create_database(self):
        """Create SQLite database to store game history"""
        try:
            # Ensure the database directory exists
            os.makedirs('chess_data', exist_ok=True)
            
            self.conn = sqlite3.connect('chess_data/chess_games.db')
            self.cursor = self.conn.cursor()
            
            # Create tables if they don't exist
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS players (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE
                )
            ''')
            
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS games (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    white_player_id INTEGER,
                    black_player_id INTEGER,
                    date TEXT,
                    result TEXT,
                    moves TEXT,
                    final_position TEXT,
                    FOREIGN KEY (white_player_id) REFERENCES players (id),
                    FOREIGN KEY (black_player_id) REFERENCES players (id)
                )
            ''')
            
            self.conn.commit()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to create database: {e}")
    
    def create_menu(self):
        """Create the application menu"""
        menu_bar = Menu(self.root)
        
        # Game menu
        game_menu = Menu(menu_bar, tearoff=0)
        game_menu.add_command(label="New Game", command=self.new_game)
        game_menu.add_command(label="Set Players", command=self.set_players)
        game_menu.add_separator()
        game_menu.add_command(label="Save Game", command=self.save_game)
        game_menu.add_command(label="Load Game", command=self.load_game_list)
        game_menu.add_separator()
        game_menu.add_command(label="Exit", command=self.root.quit)
        menu_bar.add_cascade(label="Game", menu=game_menu)
        
        # Help menu
        help_menu = Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="Rules", command=self.show_rules)
        help_menu.add_command(label="About", command=self.show_about)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menu_bar)
    
    def create_main_frame(self):
        """Create the main frame containing the chess board"""
        self.main_frame = Frame(self.root, bg="#2c3e50", padx=20, pady=20)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Chess board canvas
        self.board_size = 480
        self.square_size = self.board_size // 8
        
        self.canvas = tk.Canvas(self.main_frame, width=self.board_size, height=self.board_size, 
                               bg="#2c3e50", highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Bind click events
        self.canvas.bind("<Button-1>", self.on_square_clicked)
    
    def create_info_frame(self):
        """Create the info frame showing game status"""
        self.info_frame = Frame(self.main_frame, bg="#34495e", width=250)
        self.info_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=10, pady=10)
        
        # Current turn label
        self.turn_label = Label(self.info_frame, text="Current turn: White", 
                               font=("Arial", 12), bg="#34495e", fg="white")
        self.turn_label.pack(pady=10)
        
        # Players info
        self.white_label = Label(self.info_frame, text=f"White: {self.white_player}", 
                                font=("Arial", 12), bg="#34495e", fg="white")
        self.white_label.pack(pady=5)
        
        self.black_label = Label(self.info_frame, text=f"Black: {self.black_player}", 
                                font=("Arial", 12), bg="#34495e", fg="white")
        self.black_label.pack(pady=5)
        
        # Buttons
        self.undo_button = Button(self.info_frame, text="Undo Move", 
                                 command=self.undo_move, bg="#3498db", fg="white")
        self.undo_button.pack(pady=10, fill=tk.X, padx=20)
        
        self.resign_button = Button(self.info_frame, text="Resign", 
                                   command=self.resign_game, bg="#e74c3c", fg="white")
        self.resign_button.pack(pady=10, fill=tk.X, padx=20)
        
        self.new_game_button = Button(self.info_frame, text="New Game", 
                                     command=self.new_game, bg="#2ecc71", fg="white")
        self.new_game_button.pack(pady=10, fill=tk.X, padx=20)
    
    def create_moves_frame(self):
        """Create the frame showing move history"""
        self.moves_frame = Frame(self.root, bg="#34495e", height=150)
        self.moves_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=10)
        
        # Title
        Label(self.moves_frame, text="Move History", 
             font=("Arial", 12, "bold"), bg="#34495e", fg="white").pack(pady=5)
        
        # Scrollable text widget for moves
        self.moves_text = tk.Text(self.moves_frame, height=5, width=50, bg="#ecf0f1")
        self.moves_text.pack(padx=10, pady=5, fill=tk.X)
        self.moves_text.config(state=tk.DISABLED)
    
    def update_board(self):
        """Update the chess board display"""
        # Generate SVG representation of the board
        svg_data = chess.svg.board(board=self.board, size=self.board_size)
        
        # Convert SVG to PNG using cairosvg
        png_data = svg2png(bytestring=svg_data.encode('utf-8'))
        
        # Create a PIL Image from the PNG data
        image = Image.open(BytesIO(png_data))
        
        # Convert to PhotoImage for Tkinter
        self.board_image = ImageTk.PhotoImage(image)
        
        # Display the image on canvas
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.board_image)
        
        # Update turn label
        turn_text = "White" if self.board.turn else "Black"
        self.turn_label.config(text=f"Current turn: {turn_text}")
        
        # Check for game over conditions
        if self.board.is_checkmate():
            winner = "Black" if self.board.turn else "White"
            messagebox.showinfo("Game Over", f"Checkmate! {winner} wins!")
            self.game_over = True
        elif self.board.is_stalemate():
            messagebox.showinfo("Game Over", "Stalemate! The game is a draw.")
            self.game_over = True
        elif self.board.is_insufficient_material():
            messagebox.showinfo("Game Over", "Draw due to insufficient material.")
            self.game_over = True
    
    def on_square_clicked(self, event):
        """Handle clicks on the chess board"""
        if self.game_over:
            return
        
        # Convert pixel coordinates to chess square
        file_idx = event.x // self.square_size
        rank_idx = 7 - (event.y // self.square_size)
        square = chess.square(file_idx, rank_idx)
        
        if self.selected_square is None:
            # First click - select a piece
            piece = self.board.piece_at(square)
            if piece and piece.color == self.board.turn:
                self.selected_square = square
                # Highlight possible moves (in a real implementation)
        else:
            # Second click - try to make a move
            move = chess.Move(self.selected_square, square)
            
            # Check for promotion
            if (self.board.piece_at(self.selected_square) and
                self.board.piece_at(self.selected_square).piece_type == chess.PAWN and
                ((rank_idx == 7 and self.board.turn) or (rank_idx == 0 and not self.board.turn))):
                move = chess.Move(self.selected_square, square, promotion=chess.QUEEN)
            
            # Try to make the move
            if move in self.board.legal_moves:
                # Record the move in algebraic notation
                move_san = self.board.san(move)
                self.moves_history.append(move_san)
                
                # Make the move
                self.board.push(move)
                
                # Update the move history display
                self.update_moves_display()
                
                # Update the board
                self.update_board()
            
            # Reset selection
            self.selected_square = None
    
    def update_moves_display(self):
        """Update the moves history text widget"""
        self.moves_text.config(state=tk.NORMAL)
        self.moves_text.delete(1.0, tk.END)
        
        for i, move in enumerate(self.moves_history):
            if i % 2 == 0:
                move_text = f"{(i//2)+1}. {move} "
            else:
                move_text = f"{move} "
            self.moves_text.insert(tk.END, move_text)
        
        self.moves_text.config(state=tk.DISABLED)
    
    def undo_move(self):
        """Undo the last move"""
        if len(self.board.move_stack) > 0:
            self.board.pop()
            if self.moves_history:
                self.moves_history.pop()
            self.update_moves_display()
            self.update_board()
    
    def new_game(self):
        """Start a new chess game"""
        if len(self.board.move_stack) > 0:
            if not messagebox.askyesno("New Game", "Are you sure you want to start a new game?"):
                return
        
        self.board = chess.Board()
        self.selected_square = None
        self.game_over = False
        self.moves_history = []
        
        self.update_moves_display()
        self.update_board()
    
    def set_players(self):
        """Set player names"""
        white = simpledialog.askstring("Player Names", "Enter White player name:", 
                                      initialvalue=self.white_player)
        if white:
            self.white_player = white
        
        black = simpledialog.askstring("Player Names", "Enter Black player name:", 
                                      initialvalue=self.black_player)
        if black:
            self.black_player = black
        
        # Update labels
        self.white_label.config(text=f"White: {self.white_player}")
        self.black_label.config(text=f"Black: {self.black_player}")
    
    def resign_game(self):
        """Current player resigns the game"""
        if self.game_over:
            return
        
        if messagebox.askyesno("Resign", "Are you sure you want to resign?"):
            winner = "Black" if self.board.turn else "White"
            messagebox.showinfo("Game Over", f"{winner} wins by resignation!")
            self.game_over = True
    
    def save_game(self):
        """Save the current game to the database"""
        if len(self.board.move_stack) == 0:
            messagebox.showinfo("Save Game", "No moves to save!")
            return
        
        try:
            # Get or create player IDs
            self.cursor.execute("INSERT OR IGNORE INTO players (name) VALUES (?)", (self.white_player,))
            self.cursor.execute("SELECT id FROM players WHERE name = ?", (self.white_player,))
            white_id = self.cursor.fetchone()[0]
            
            self.cursor.execute("INSERT OR IGNORE INTO players (name) VALUES (?)", (self.black_player,))
            self.cursor.execute("SELECT id FROM players WHERE name = ?", (self.black_player,))
            black_id = self.cursor.fetchone()[0]
            
            # Determine result
            if self.game_over:
                if self.board.is_checkmate():
                    result = "0-1" if self.board.turn else "1-0"
                else:
                    result = "1/2-1/2"  # Draw
            else:
                result = "*"  # Game in progress
            
            # Save game
            date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            moves = " ".join(self.moves_history)
            final_position = self.board.fen()
            
            self.cursor.execute('''
                INSERT INTO games (white_player_id, black_player_id, date, result, moves, final_position)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (white_id, black_id, date, result, moves, final_position))
            
            self.conn.commit()
            messagebox.showinfo("Save Game", "Game saved successfully!")
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to save game: {e}")
    
    def load_game_list(self):
        """Show a list of saved games to load"""
        try:
            self.cursor.execute('''
                SELECT g.id, p1.name, p2.name, g.date, g.result
                FROM games g
                JOIN players p1 ON g.white_player_id = p1.id
                JOIN players p2 ON g.black_player_id = p2.id
                ORDER BY g.date DESC
                LIMIT 50
            ''')
            
            games = self.cursor.fetchall()
            
            if not games:
                messagebox.showinfo("Load Game", "No saved games found!")
                return
            
            # Create a new window to display games
            load_window = tk.Toplevel(self.root)
            load_window.title("Load Game")
            load_window.geometry("600x400")
            
            # Create a listbox to display games
            listbox = tk.Listbox(load_window, width=70, height=15)
            listbox.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)
            
            # Add games to the listbox
            for game in games:
                game_id, white, black, date, result = game
                listbox.insert(tk.END, f"{game_id}: {white} vs {black} - {date} - Result: {result}")
            
            # Button to load the selected game
            def load_selected_game():
                selection = listbox.curselection()
                if not selection:
                    messagebox.showinfo("Load Game", "Please select a game to load!")
                    return
                
                game_id = int(listbox.get(selection[0]).split(":")[0])
                self.load_game(game_id)
                load_window.destroy()
            
            load_button = Button(load_window, text="Load Selected Game", command=load_selected_game)
            load_button.pack(pady=10)
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to load games: {e}")
    
    def load_game(self, game_id):
        """Load a specific game from the database"""
        try:
            self.cursor.execute('''
                SELECT p1.name, p2.name, g.moves, g.final_position
                FROM games g
                JOIN players p1 ON g.white_player_id = p1.id
                JOIN players p2 ON g.black_player_id = p2.id
                WHERE g.id = ?
            ''', (game_id,))
            
            game_data = self.cursor.fetchone()
            if not game_data:
                messagebox.showerror("Load Game", "Game not found!")
                return
            
            white, black, moves, final_position = game_data
            
            # Set player names
            self.white_player = white
            self.black_player = black
            self.white_label.config(text=f"White: {self.white_player}")
            self.black_label.config(text=f"Black: {self.black_player}")
            
            # Reset the board and replay moves
            self.board = chess.Board()
            self.selected_square = None
            self.game_over = False
            
            # Parse moves
            self.moves_history = moves.split() if moves else []
            
            # Apply moves to reach the final position
            for move_san in self.moves_history:
                try:
                    move = self.board.parse_san(move_san)
                    self.board.push(move)
                except ValueError:
                    # If there's an error parsing a move, just set the final position
                    self.board = chess.Board(final_position)
                    break
            
            # Update display
            self.update_moves_display()
            self.update_board()
            
            messagebox.showinfo("Load Game", "Game loaded successfully!")
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to load game: {e}")
    
    def show_rules(self):
        """Show chess rules"""
        rules_text = """
        Chess Rules:
        
        1. The game is played on an 8x8 board with alternating light and dark squares.
        2. Each player starts with 16 pieces: 1 king, 1 queen, 2 rooks, 2 knights, 2 bishops, and 8 pawns.
        3. White always moves first.
        4. The goal is to checkmate your opponent's king.
        5. Each piece moves differently:
           - King: One square in any direction
           - Queen: Any number of squares diagonally, horizontally, or vertically
           - Rook: Any number of squares horizontally or vertically
           - Bishop: Any number of squares diagonally
           - Knight: Moves in an L-shape (2 squares in one direction, then 1 square perpendicular)
           - Pawn: Moves forward one square, or two on first move, captures diagonally
        6. Special moves include castling, en passant, and pawn promotion.
        """
        messagebox.showinfo("Chess Rules", rules_text)
    
    def show_about(self):
        """Show about information"""
        about_text = """
        Chess Game v1.0
        
        A simple chess game with database functionality to save and load games.
        
        Required libraries:
        - tkinter
        - python-chess
        - Pillow (PIL)
        - cairosvg
        
        Created for Python Beginners project.
        """
        messagebox.showinfo("About", about_text)
    
    def __del__(self):
        """Close database connection when the object is destroyed"""
        if hasattr(self, 'conn'):
            self.conn.close()

def main():
    # Check for required libraries
    try:
        import chess # type: ignore
        import cairosvg # type: ignore
    except ImportError:
        print("Required libraries not found. Please install them using:")
        print("pip install python-chess pillow cairosvg")
        return
    
    root = tk.Tk()
    app = ChessGame(root)
    root.mainloop()

if __name__ == "__main__":
    main() 