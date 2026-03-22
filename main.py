import tkinter as tk
from tkinter import font
from typing import NamedTuple
from itertools import cycle
import os
from PIL import Image, ImageTk
import math

# Configure paths to PNG assets
ASSETS_PATH = os.path.join(os.path.dirname(__file__), "assets")
BACKGROUND_PNG = os.path.join(ASSETS_PATH, "Background.png")
BOARD_CELL_PNG = os.path.join(ASSETS_PATH, "Board.png")
X_PIECE_PNG = os.path.join(ASSETS_PATH, "X.png")
X_GREEN_PNG = os.path.join(ASSETS_PATH, "X-green.png")
O_PIECE_PNG = os.path.join(ASSETS_PATH, "O.png")
O_GREEN_PNG = os.path.join(ASSETS_PATH, "O-green.png")

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
    """Responsive PNG-based tic-tac-toe board with animations"""
    
    def __init__(self, game):
        super().__init__()
        self.title("Tic-Tac-Toe Game")
        self._game = game
        self.score_tracker = ScoreTracker()
        
        # Store canvas item IDs
        self.bg_image_id = None
        self.cell_images = {}  # (row, col) -> cell image ID
        self.piece_images = {}  # (row, col) -> piece image ID
        self.winning_line_id = None
        
        # Original image sizes (reference)
        self.original_images = self._load_original_images()
        
        # Current scaled images
        self.scaled_images = {}

        self.cell_size = (180, 180)  
        self.piece_size = (150, 150)
        
        # Set up the window
        self.configure(bg="#F0F0F0")
        
        # Create UI components
        self._create_menu()
        self._create_top_bar()
        self._create_board_grid()
        
        # Bind resize event
        self.bind("<Configure>", self._on_resize)
        
        # Set minimum window size
        self.minsize(500, 600)
        
        # Center the window
        self._center_window()
        
        # Animation flags
        self.animating = False
    
    def _load_original_images(self):
        """Load original PNG images and store PIL objects"""
        images = {}
        try:
            images['background'] = Image.open(BACKGROUND_PNG)
            images['board_cell'] = Image.open(BOARD_CELL_PNG)
            images['x_piece'] = Image.open(X_PIECE_PNG)
            images['x_green'] = Image.open(X_GREEN_PNG)
            images['o_piece'] = Image.open(O_PIECE_PNG)
            images['o_green'] = Image.open(O_GREEN_PNG)
        except Exception as e:
            print(f"Error loading images: {e}")
            raise
        return images
    
    def _scale_images(self, new_size):
        """Scale all images proportionally"""
        # Calculate scale factor based on background width
        bg_width, bg_height = self.original_images['background'].size
        scale_factor = new_size / bg_width
        
        # Store cell size for grid positioning
        self.cell_size = (
            int(self.original_images['board_cell'].width * scale_factor),
            int(self.original_images['board_cell'].height * scale_factor)
        )

        self.piece_size = (
            int(self.cell_size[0] * 0.85),  # 85% of cell width
            int(self.cell_size[1] * 0.85)   # 85% of cell height
        )
        
        # Scale each image
        self.scaled_images = {}
        for name, img in self.original_images.items():
            # Use piece_size for piece images, scale_factor for others
            if name in ['x_piece', 'o_piece', 'x_green', 'o_green']:
                scaled_pil = img.resize(self.piece_size, Image.Resampling.LANCZOS)
            else:
                new_width = int(img.width * scale_factor)
                new_height = int(img.height * scale_factor)
                scaled_pil = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            self.scaled_images[name] = ImageTk.PhotoImage(scaled_pil)
        
        return scale_factor
    
    def _create_menu(self):
        """Create the game menu"""
        menu_bar = tk.Menu(master=self)
        self.config(menu=menu_bar)
        
        file_menu = tk.Menu(master=menu_bar, tearoff=0)
        file_menu.add_command(
            label="New Game",
            command=self.reset_board,
            accelerator="Cmd+N",
        )
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        
        menu_bar.add_cascade(label="Game", menu=file_menu)
        self.bind_all("<Command-n>", lambda e: self.reset_board())
    
    def _create_top_bar(self):
        """Create the top bar with status, score, and restart button"""
        top_frame = tk.Frame(master=self, bg="#F0F0F0")
        top_frame.pack(fill=tk.X, padx=20, pady=(15, 10))
        
        # Left side - Game status
        status_frame = tk.Frame(master=top_frame, bg="#F0F0F0")
        status_frame.pack(side=tk.LEFT)
        
        title_label = tk.Label(
            master=status_frame,
            text="Tic-Tac-Toe",
            font=font.Font(size=16, weight="bold"),
            bg='#F0F0F0',
            fg='#2C3E50'
        )
        title_label.pack(anchor='w')
        
        self.display = tk.Label(
            master=status_frame,
            text="Ready to play!",
            font=font.Font(size=14),
            bg='#F0F0F0',
            fg='#34495E'
        )
        self.display.pack(anchor='w', pady=(5, 0))
        
        # Center - Score display
        self.score_display = tk.Label(
            master=top_frame,
            text=self.score_tracker.display_score(),
            font=font.Font(size=12, weight="bold"),
            bg='#F0F0F0',
            fg='#7F8C8D'
        )
        self.score_display.pack(side=tk.LEFT, expand=True)
        
        # Right side - Restart button
        restart_btn = tk.Button(
            master=top_frame,
            text="New Game",
            font=font.Font(size=12),
            cursor='hand2',
            command=self.reset_board,
        )
        restart_btn.pack(side=tk.RIGHT)
    
    def _create_board_grid(self):
        """Create the game board grid using only canvas items"""
        # Create a canvas for the background and all game elements
        self.canvas = tk.Canvas(
            master=self,
            highlightthickness=0,
            bg='#F0F0F0',
            cursor='hand2'
        )
        self.canvas.pack(expand=True, fill=tk.BOTH, padx=20, pady=(0, 20))
        
        # Bind click events to the canvas
        self.canvas.bind("<Button-1>", self._on_canvas_click)
        
        # Initial scaling based on window width
        self.canvas.update_idletasks()
        self._scale_board(400)  # Default size
    
    def _scale_board(self, width):
        """Scale and redraw the board using canvas items"""
        # Scale images
        scale_factor = self._scale_images(width)
        
        # Clear canvas
        self.canvas.delete("all")
        self.cell_images = {}
        self.piece_images = {}
        self.winning_line_id = None
        
        # Calculate board position (centered)
        bg_width = self.scaled_images['background'].width()
        bg_height = self.scaled_images['background'].height()
        
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1:  # Canvas not yet sized
            canvas_width = bg_width + 40
            canvas_height = bg_height + 40
        
        self.start_x = (canvas_width - bg_width) // 2
        self.start_y = (canvas_height - bg_height) // 2
        
        # Place background (lowest layer)
        self.bg_image_id = self.canvas.create_image(
            self.start_x, self.start_y,
            image=self.scaled_images['background'],
            anchor='nw',
            tags=("background",)
        )
        
        # Calculate grid position
        cell_width, cell_height = self.cell_size
        piece_width, piece_height = self.piece_size
        
        grid_start_x = self.start_x + (bg_width - (cell_width * 3)) // 2
        grid_start_y = self.start_y + (bg_height - (cell_height * 3)) // 2
        
        # Calculate offset to center piece on cell
        self.piece_offset_x = (cell_width - piece_width) // 2
        self.piece_offset_y = (cell_height - piece_height) // 2
        
        # Store cell positions and centers
        self.cell_positions = {}  # (row, col) -> (x, y) top-left corner
        self.piece_centers = {}   # (row, col) -> (x, y) center point
        
        # Create grid of cells (middle layer)
        for row in range(self._game.board_size):
            for col in range(self._game.board_size):
                x = grid_start_x + (col * cell_width)
                y = grid_start_y + (row * cell_height)
                
                # Store cell position
                self.cell_positions[(row, col)] = (x, y)
                self.piece_centers[(row, col)] = (
                    x + cell_width // 2,
                    y + cell_height // 2
                )
                
                # Create cell background (board cell image)
                cell_id = self.canvas.create_image(
                    x, y,
                    image=self.scaled_images['board_cell'],
                    anchor='nw',
                    tags=("cell", f"cell_{row}_{col}")
                )
                self.cell_images[(row, col)] = cell_id
                
                # Get current move
                move = self._game._current_moves[row][col]
                
                # Create piece if exists (top layer)
                if move.label:
                    is_winner = self._game.has_winner() and (row, col) in self._game.winner_combo
                    
                    if move.label == "X":
                        img_key = 'x_green' if is_winner else 'x_piece'
                    else:  # "O"
                        img_key = 'o_green' if is_winner else 'o_piece'
                    
                    piece_id = self.canvas.create_image(
                        x + self.piece_offset_x,
                        y + self.piece_offset_y,
                        image=self.scaled_images[img_key],
                        anchor='nw',
                        tags=("piece", f"piece_{row}_{col}")
                    )
                    self.piece_images[(row, col)] = piece_id
        
        # Lower the background to ensure it's behind everything
        self.canvas.tag_lower("background")
    
    def _on_canvas_click(self, event):
        """Handle canvas click events"""
        
        # Find which cell was clicked
        for (row, col), (x, y) in self.cell_positions.items():
            cell_width, cell_height = self.cell_size
            if (x <= event.x <= x + cell_width and 
                y <= event.y <= y + cell_height):
                self.play(row, col)
                break
    
    def _on_resize(self, event):
        """Handle window resize events"""
        if event.widget == self and event.width > 100:
            self._scale_board(event.width - 40)  # Subtract padding
    
    def play(self, row, col):
        """Handle player moves with animation"""
            
        move = Move(row, col, self._game.current_player.label)
        
        if self._game.is_valid_move(move):
            # Process game logic immediately (no delay)
            self._game.process_move(move)
            
            # Update game state display immediately
            if self._game.has_winner():
                self.score_tracker.update_score(self._game.current_player.label)
                msg = f'Player {self._game.current_player.label} Wins!'
                self._update_display(msg, self._game.current_player.color)
            elif self._game.is_tied():
                self.score_tracker.update_score("tie")
                self._update_display("Game Tied!", "#E74C3C")
            else:
                self._game.toggle_player()
                self._update_display(f"{self._game.current_player.label}'s turn")
            
            self.score_display.config(text=self.score_tracker.display_score())
            
            # Now handle the visual animation (purely cosmetic)
            self._animate_piece_placement(row, col, move)
    
    def _animate_piece_placement(self, row, col, move):
        """Animate piece placement (purely visual)"""
        self.animating = True
        
        # Get piece position
        x, y = self.cell_positions[(row, col)]
        target_x = x + self.piece_offset_x
        target_y = y + self.piece_offset_y
        
        # Create animated piece
        piece_img = self.scaled_images['x_piece'] if move.label == "X" else self.scaled_images['o_piece']
        piece_id = self.canvas.create_image(
            x, y,
            image=piece_img,
            anchor='nw',
            tags=("piece", f"piece_{row}_{col}", "animating")
        )
        
        # Store piece ID
        self.piece_images[(row, col)] = piece_id
        
        # Animate the piece
        self._animate_piece_move(piece_id, x, y, target_x, target_y, step=0)
        
        # After animation, handle win/tie state ONCE for the entire game
        if self._game.has_winner():
            self.after(600, self._handle_win_animation)  # Handles ALL winning pieces
        elif self._game.is_tied():
            self.after(600, self._animate_tie)  # Handles ALL pieces for tie
        else:
            self.after(600, lambda: self._finish_animation())
    
    def _animate_piece_move(self, piece_id, start_x, start_y, end_x, end_y, step=0):
        """Animate piece movement with bounce effect"""
        if step > 20:  # Animation complete
            self.canvas.coords(piece_id, end_x, end_y)
            self.canvas.dtag(piece_id, "animating")  # Remove animating tag
            return
        
        # Ease out bounce effect
        progress = step / 20
        bounce = 1 - math.exp(-5 * progress) * math.cos(10 * progress)
        
        # Calculate position with bounce
        current_x = start_x + (end_x - start_x) * bounce
        current_y = start_y + (end_y - start_y) * bounce
        
        # Scale effect
        scale = 0.1 + 0.9 * bounce
        self.canvas.scale(piece_id, start_x, start_y, scale, scale)
        self.canvas.coords(piece_id, current_x, current_y)
        
        self.canvas.after(20, lambda: self._animate_piece_move(
            piece_id, start_x, start_y, end_x, end_y, step + 1
        ))
    
    def _finish_animation(self):
        """Mark animation as complete"""
        self.animating = False

    def _handle_win_animation(self):
        """Handle win animation for all winning pieces"""
        # Update all winning pieces to green at once
        self._update_pieces_to_green()
    
    def _update_pieces_to_green(self):
        """Update all winning pieces to green version"""
        for (row, col) in self._game.winner_combo:
            if (row, col) in self.piece_images:
                move = self._game._current_moves[row][col]
                
                if move.label:
                    # Get current piece position
                    x, y = self.cell_positions[(row, col)]
                    target_x = x + self.piece_offset_x
                    target_y = y + self.piece_offset_y
                    
                    # Remove old piece
                    self.canvas.delete(self.piece_images[(row, col)])
                    
                    # Add green piece at exactly the same position
                    img_key = 'x_green' if move.label == "X" else 'o_green'
                    new_piece_id = self.canvas.create_image(
                        target_x,
                        target_y,
                        image=self.scaled_images[img_key],
                        anchor='nw',
                        tags=("piece", f"piece_{row}_{col}")
                    )
                    
                    # Store new piece reference
                    self.piece_images[(row, col)] = new_piece_id

    
    def _animate_piece_pulse(self, piece_id, center, step=0):
        """Animate piece with glow effect (no scaling issues)"""
        if step > 30:
            self._finish_animation()
            return
        
        # Alternate between normal and highlighted by adding/removing a glow outline
        if step % 6 < 3:
            # Add glow outline (create a halo effect)
            self.canvas.itemconfig(piece_id, state='normal')
            # Could also create a temporary outline or change opacity
        else:
            self.canvas.itemconfig(piece_id, state='normal')
        
        self.canvas.after(50, lambda: self._animate_piece_pulse(
            piece_id, center, step + 1
        ))
    
    def _animate_tie(self):
        """Animate a tie game with shake effect"""
        for (row, col), piece_id in self.piece_images.items():
            if piece_id:
                original_x, original_y = self.cell_positions[(row, col)]
                original_x += self.piece_offset_x
                original_y += self.piece_offset_y
                self._shake_piece(piece_id, original_x, original_y, 0)
        
        # Mark animation as complete after shake
        self.after(550, lambda: self._finish_animation())
    
    def _shake_piece(self, piece_id, original_x, original_y, step=0):
        """Shake a piece animation"""
        if step > 10:
            self.canvas.coords(piece_id, original_x, original_y)
            return
            
        # Calculate shake offset
        offset_x = 5 * math.sin(step * 2)
        offset_y = 5 * math.cos(step * 2)
        
        # Apply shake
        self.canvas.coords(piece_id, original_x + offset_x, original_y + offset_y)
        
        self.canvas.after(50, lambda: self._shake_piece(
            piece_id, original_x, original_y, step + 1
        ))
    
    def _update_display(self, msg, color="#34495E"):
        """Update the game status display"""
        self.display.config(text=msg, fg=color)
    
    def reset_board(self):
        """Reset the game board"""
            
        self._game.reset_game()
        
        # Redraw board
        self._scale_board(self.winfo_width() - 40)
        self._update_display("Ready to play!")
        self.score_display.config(text=self.score_tracker.display_score())
    
    def _center_window(self):
        """Center the window on screen"""
        self.update_idletasks()
        width = 500  # Default width
        height = 400  # Default height
        self.geometry(f'{width}x{height}')
        
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'+{x}+{y}')

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
    
    # Start the game
    board.mainloop()

if __name__ == "__main__":
    main()

















    