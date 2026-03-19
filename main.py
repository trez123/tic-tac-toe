import tkinter as tk
from tkinter import font
from typing import NamedTuple
from itertools import cycle
import os
from PIL import Image, ImageTk

# Configure paths to PNG assets
ASSETS_PATH = os.path.join(os.path.dirname(__file__), "assets")
BACKGROUND_PNG = os.path.join(ASSETS_PATH, "Background.png")
BOARD_CELL_PNG = os.path.join(ASSETS_PATH, "Board.png")
X_PIECE_PNG = os.path.join(ASSETS_PATH, "X.png")
O_PIECE_PNG = os.path.join(ASSETS_PATH, "O.png")

class ScoreTracker:
    """Track game scores"""
    def __init__(self):
        self.x_wins = 0
        self.o_wins = 0
        self.ties = 0
    
    def update_score(self, winner):
        if winner == "X":
            self.x_wins += 1
        elif winner == "O":
            self.o_wins += 1
        else:
            self.ties += 1
    
    def display_score(self):
        return f"X: {self.x_wins}   |   O: {self.o_wins}   |   Ties: {self.ties}"

class Player(NamedTuple):
    """Represents a player with label and color"""
    label: str
    color: str

class Move(NamedTuple):
    """Represents a move on the board"""
    row: int
    col: int
    label: str = ""

BOARD_SIZE = 3
DEFAULT_PLAYERS = (
    Player(label="X", color="#2ECC71"),  # Green
    Player(label="O", color="#3498DB"),  # Blue
)

class TicTacToeGame:
    """Manages the game logic and state"""
    
    def __init__(self, players=DEFAULT_PLAYERS, board_size=BOARD_SIZE):
        self._players = cycle(players)
        self.board_size = board_size
        self.current_player = next(self._players)
        self.winner_combo = []
        self._current_moves = []
        self._has_winner = False
        self._winning_combos = []
        self._setup_board()
    
    def _setup_board(self):
        """Initialize the game board with empty moves"""
        self._current_moves = [
            [Move(row, col) for col in range(self.board_size)]
            for row in range(self.board_size)
        ]
        self._winning_combos = self._get_winning_combos()
    
    def _get_winning_combos(self):
        """Calculate all possible winning combinations"""
        rows = [
            [(move.row, move.col) for move in row]
            for row in self._current_moves
        ]
        columns = [list(col) for col in zip(*rows)]
        first_diagonal = [row[i] for i, row in enumerate(rows)]
        second_diagonal = [col[j] for j, col in enumerate(reversed(columns))]
        return rows + columns + [first_diagonal, second_diagonal]
    
    def is_valid_move(self, move):
        """Check if a move is valid"""
        row, col = move.row, move.col
        move_was_not_played = self._current_moves[row][col].label == ""
        no_winner = not self._has_winner
        return no_winner and move_was_not_played
    
    def process_move(self, move):
        """Process a player's move and check for win"""
        row, col = move.row, move.col
        self._current_moves[row][col] = move
        
        for combo in self._winning_combos:
            results = set(
                self._current_moves[n][m].label
                for n, m in combo
            )
            is_win = (len(results) == 1) and ("" not in results)
            if is_win:
                self._has_winner = True
                self.winner_combo = combo
                break
    
    def has_winner(self):
        """Check if game has a winner"""
        return self._has_winner
    
    def is_tied(self):
        """Check if game is tied"""
        no_winner = not self._has_winner
        played_moves = (
            move.label for row in self._current_moves for move in row
        )
        return no_winner and all(played_moves)
    
    def toggle_player(self):
        """Switch to the next player"""
        self.current_player = next(self._players)
    
    def reset_game(self):
        """Reset the game state"""
        for row, row_content in enumerate(self._current_moves):
            for col, _ in enumerate(row_content):
                row_content[col] = Move(row, col)
        self._has_winner = False
        self.winner_combo = []
        self._players = cycle(DEFAULT_PLAYERS)
        self.current_player = next(self._players)

class TicTacToeBoard(tk.Tk):
    """PNG-based tic-tac-toe board"""
    
    def __init__(self, game):
        super().__init__()
        self.title("Tic-Tac-Toe Game")
        self._game = game
        self.score_tracker = ScoreTracker()
        self._cells = {}
        
        # Load PNG assets
        self._load_images()
        
        # Set up the window
        self.configure(bg='#F0F0F0')
        self.resizable(False, False)
        
        # Create UI components
        self._create_menu()
        self._create_board_display()
        self._create_board_grid()
        
        # Set window size based on background
        self.geometry(f"{self.background.width()}x{self.background.height() + 100}")
    
    def _load_images(self):
        """Load and prepare all PNG images"""
        try:
            # Load background
            bg_pil = Image.open(BACKGROUND_PNG)
            self.background = ImageTk.PhotoImage(bg_pil)
            
            # Load board cell
            cell_pil = Image.open(BOARD_CELL_PNG)
            self.board_cell = ImageTk.PhotoImage(cell_pil)
            
            # Load X and O pieces
            x_pil = Image.open(X_PIECE_PNG)
            self.x_piece = ImageTk.PhotoImage(x_pil)
            
            o_pil = Image.open(O_PIECE_PNG)
            self.o_piece = ImageTk.PhotoImage(o_pil)
            
            # Store cell size from image
            self.cell_size = cell_pil.size
            
        except Exception as e:
            print(f"Error loading images: {e}")
            print("Please ensure all PNG files exist in the assets folder.")
            raise
    
    def _create_menu(self):
        """Create the game menu"""
        menu_bar = tk.Menu(master=self)
        self.config(menu=menu_bar)
        
        file_menu = tk.Menu(master=menu_bar, tearoff=0)
        file_menu.add_command(
            label="New Game",
            command=self.reset_board,
            accelerator="Cmd+N"
        )
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        
        menu_bar.add_cascade(label="Game", menu=file_menu)
        self.bind_all("<Command-n>", lambda e: self.reset_board())
    
    def _create_board_display(self):
        """Create the game status display"""
        display_frame = tk.Frame(master=self, bg='#F0F0F0')
        display_frame.pack(fill=tk.X, pady=(15, 10))
        
        title_label = tk.Label(
            master=display_frame,
            text="Tic-Tac-Toe",
            font=font.Font(size=16, weight="bold"),
            bg='#F0F0F0',
            fg='#2C3E50'
        )
        title_label.pack()
        
        self.display = tk.Label(
            master=display_frame,
            text="Ready to play!",
            font=font.Font(size=14),
            bg='#F0F0F0',
            fg='#34495E'
        )
        self.display.pack(pady=(5, 0))
        
        self.score_display = tk.Label(
            master=display_frame,
            text=self.score_tracker.display_score(),
            font=font.Font(size=12),
            bg='#F0F0F0',
            fg='#7F8C8D'
        )
        self.score_display.pack(pady=(5, 0))
    
    def _create_board_grid(self):
        """Create the game board grid on top of background"""
        # Create a canvas for the background
        self.canvas = tk.Canvas(
            master=self,
            width=self.background.width(),
            height=self.background.height(),
            highlightthickness=0,
            bg='#F0F0F0'
        )
        self.canvas.pack(pady=(0, 20))
        
        # Place background image
        self.canvas.create_image(0, 0, image=self.background, anchor='nw')
        
        # Calculate grid positioning
        cell_width, cell_height = self.cell_size
        start_x = (self.background.width() - (cell_width * 3)) // 2
        start_y = (self.background.height() - (cell_height * 3)) // 2
        
        # Create grid of buttons
        for row in range(self._game.board_size):
            for col in range(self._game.board_size):
                x = start_x + (col * cell_width)
                y = start_y + (row * cell_height)
                
                # Create button with transparent background
                button = tk.Button(
                    master=self.canvas,
                    image=self.board_cell,
                    borderwidth=0,
                    highlightthickness=0,
                    relief='flat',
                    bg='#F0F0F0',
                    activebackground='#F0F0F0',
                    cursor='hand2'
                )
                
                # Store button reference and position
                self._cells[button] = (row, col)
                
                # Place button on canvas
                self.canvas.create_window(x, y, window=button, anchor='nw')
                
                # Bind click event
                button.bind("<ButtonPress-1>", self.play)
    
    def play(self, event):
        """Handle player moves"""
        clicked_btn = event.widget
        row, col = self._cells[clicked_btn]
        
        move = Move(row, col, self._game.current_player.label)
        
        if self._game.is_valid_move(move):
            # Update button with player's piece
            piece = self.x_piece if move.label == "X" else self.o_piece
            clicked_btn.config(image=piece)
            
            # Process game logic
            self._game.process_move(move)
            
            # Check game state
            if self._game.is_tied():
                self.score_tracker.update_score("tie")
                self._update_display("Game Tied!", "#E74C3C")
            elif self._game.has_winner():
                self.score_tracker.update_score(self._game.current_player.label)
                self._highlight_winning_cells()
                msg = f'Player {self._game.current_player.label} Wins!'
                self._update_display(msg, self._game.current_player.color)
            else:
                self._game.toggle_player()
                self._update_display(f"{self._game.current_player.label}'s turn")
            
            self.score_display.config(text=self.score_tracker.display_score())
    
    def _highlight_winning_cells(self):
        """Highlight winning cells by adding a border effect"""
        for button, coordinates in self._cells.items():
            if coordinates in self._game.winner_combo:
                # Add a highlight effect by changing relief
                button.config(relief='solid', borderwidth=3, highlightbackground='#F1C40F')
    
    def _update_display(self, msg, color="#34495E"):
        """Update the game status display"""
        self.display.config(text=msg, fg=color)
    
    def reset_board(self, event=None):
        """Reset the game board"""
        self._game.reset_game()
        
        for button in self._cells.keys():
            button.config(image=self.board_cell, relief='flat', borderwidth=0)
        
        self._update_display("Ready to play!")
        self.score_display.config(text=self.score_tracker.display_score())

def main():
    """Initialize and run the game"""
    # Verify assets exist
    for png_file in [BACKGROUND_PNG, BOARD_CELL_PNG, X_PIECE_PNG, O_PIECE_PNG]:
        if not os.path.exists(png_file):
            print(f"Error: PNG file not found: {png_file}")
            print("Please ensure all PNG files are in the assets folder.")
            return
    
    # Create game instance
    game = TicTacToeGame()
    
    # Create board instance
    board = TicTacToeBoard(game)
    
    # Center the window
    board.update_idletasks()
    x = (board.winfo_screenwidth() // 2) - (board.winfo_width() // 2)
    y = (board.winfo_screenheight() // 2) - (board.winfo_height() // 2)
    board.geometry(f'+{x}+{y}')
    
    # Start the game
    board.mainloop()

if __name__ == "__main__":
    main()