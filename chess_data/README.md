# ♟️ Chess Game

A chess game application with GUI and database functionality to save game history.

## 📋 Features

- ♟️ Full chess game with graphical interface
- 🎮 Two-player gameplay (local)
- 💾 Save and load games
- 📊 Track move history
- 👥 Manage player information
- ⏪ Undo move functionality
- 🏆 Win/draw detection

## 🔧 Installation

### Prerequisites
- Python 3.8+
- Tkinter (usually comes with Python)
- SQLite3 (built-in)

### Required Libraries
Install the required libraries using pip:

```bash
pip install -r requirements.txt
```

Or install them individually:

```bash
pip install python-chess pillow cairosvg
```

## 🚀 Usage

Run the game from the main directory:

```bash
python 16_chess_game.py
```

### 🎮 Game Controls

- **Mouse**: Click on a piece to select it, then click on a destination square to move
- **Menu**: Use the menu bar for additional options (New Game, Save, Load, etc.)

## 🗄️ Database

The game automatically creates a SQLite database to store:
- Player information
- Game history with complete move records
- Final positions for replay

The database is stored in the `chess_data` directory.

## 💡 Tips

1. **Setting Player Names**: Use the "Set Players" option in the Game menu
2. **Saving Games**: Save your game at any point using "Save Game" in the Game menu
3. **Loading Games**: Browse and load saved games from the "Load Game" option
4. **Undoing Moves**: Use the "Undo Move" button to take back the last move

## 🛠️ Troubleshooting

If you encounter issues with the cairosvg library:

### On Windows:
```bash
pip install --upgrade pip
pip install cairosvg
```

### On Linux:
```bash
sudo apt-get install libcairo2-dev
pip install cairosvg
```

### On macOS:
```bash
brew install cairo
pip install cairosvg
```

## 📚 Learn More

This project demonstrates:
- Tkinter GUI development
- SQLite database management
- Chess game logic implementation
- SVG rendering in Python
- Object-oriented design principles 