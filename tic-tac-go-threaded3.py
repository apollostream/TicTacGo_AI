import numpy as np
from typing import Tuple, Optional, List
import threading
import queue
import copy
import time
from dataclasses import dataclass

@dataclass
class BoardState:
    board: np.ndarray
    last_move: Tuple[int, int]
    evaluation: float = 0.0

class TicTacGo:
    def __init__(self):
        self.board = np.full((12, 12), ' ')
        self.current_player = 'X'
        self.winner = None
        self.ai_player = 'O'
        self.human_player = 'X'
        
        # Threading components
        self.thinking_thread = None
        self.stop_thinking = threading.Event()
        self.board_updated = threading.Event()
        self.move_ready = threading.Event()
        self.best_moves = {}  # Dictionary to store pre-computed moves for different board states
        self.current_analysis = None
        self.lock = threading.Lock()
        
        # Start continuous background thinking
        self.start_continuous_thinking()

    def start_continuous_thinking(self):
        """Start the continuous background analysis thread"""
        self.thinking_thread = threading.Thread(target=self.continuous_analysis)
        self.thinking_thread.daemon = True
        self.thinking_thread.start()

    def continuous_analysis(self):
        """Continuously analyze possible board states"""
        while not self.stop_thinking.is_set():
            with self.lock:
                current_board = copy.deepcopy(self.board)
            
            # Generate possible player moves
            valid_moves = self.get_valid_positions()
            
            # Analyze each possible player move
            for player_move in valid_moves:
                # Check if we've been interrupted by a real player move
                if self.board_updated.is_set():
                    self.board_updated.clear()
                    break
                
                # Create hypothetical board state after player move
                test_board = copy.deepcopy(current_board)
                row, col = player_move
                test_board[row][col] = self.human_player
                
                # Find and evaluate AI responses to this potential move
                best_response = self.find_best_response(test_board)
                
                # Store the analyzed response
                board_hash = self.hash_board(test_board)
                with self.lock:
                    self.best_moves[board_hash] = best_response
            
            # Small sleep to prevent CPU overload
            time.sleep(0.1)

    def find_best_response(self, board_state: np.ndarray) -> Tuple[int, int]:
        """Enhanced move finding with better threat detection"""
        # First check for immediate winning move
        winning_move = self.find_winning_move(board_state, self.ai_player)
        if winning_move:
            return winning_move
            
        # Then check for moves we must block
        blocking_move = self.find_winning_move(board_state, self.human_player)
        if blocking_move:
            return blocking_move
            
        # Look for moves that block 5-in-a-row
        blocking_five = self.find_sequence_move(board_state, self.human_player, 5)
        if blocking_five:
            return blocking_five
            
        # Look for moves that complete our 5-in-a-row
        making_five = self.find_sequence_move(board_state, self.ai_player, 5)
        if making_five:
            return making_five
            
        # Look for moves that block 4-in-a-row
        blocking_four = self.find_sequence_move(board_state, self.human_player, 4)
        if blocking_four:
            return blocking_four
            
        # Default to positional evaluation if no immediate threats
        return self.find_strategic_move(board_state)

    def find_winning_move(self, board: np.ndarray, player: str) -> Optional[Tuple[int, int]]:
        """Find a move that immediately wins or blocks a win"""
        valid_moves = self.get_valid_moves_for_state(board)
        for move in valid_moves:
            row, col = move
            board[row][col] = player
            if self.check_winner_for_state(board) == player:
                board[row][col] = ' '
                return move
            board[row][col] = ' '
        return None

    def find_sequence_move(self, board: np.ndarray, player: str, length: int) -> Optional[Tuple[int, int]]:
        """Find a move that blocks or creates a sequence of given length"""
        valid_moves = self.get_valid_moves_for_state(board)
        for move in valid_moves:
            row, col = move
            if self.would_complete_sequence(board, row, col, player, length):
                return move
        return None

    def would_complete_sequence(self, board: np.ndarray, row: int, col: int, player: str, length: int) -> bool:
        """Check if placing a piece would complete a sequence of given length"""
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]  # horizontal, vertical, diagonals
        
        board[row][col] = player
        for dx, dy in directions:
            count = 1
            # Check forward
            r, c = row + dx, col + dy
            while 0 <= r < 12 and 0 <= c < 12 and board[r][c] == player:
                count += 1
                r, c = r + dx, c + dy
            
            # Check backward
            r, c = row - dx, col - dy
            while 0 <= r < 12 and 0 <= c < 12 and board[r][c] == player:
                count += 1
                r, c = r - dx, c - dy
                
            if count >= length:
                board[row][col] = ' '
                return True
                
        board[row][col] = ' '
        return False

    def find_strategic_move(self, board: np.ndarray) -> Tuple[int, int]:
        """Find the best strategic move when no immediate threats exist"""
        best_score = float('-inf')
        best_move = None
        valid_moves = self.get_valid_moves_for_state(board)
        
        for move in valid_moves:
            row, col = move
            score = self.evaluate_strategic_position(board, row, col)
            if score > best_score:
                best_score = score
                best_move = move
        
        return best_move if best_move else valid_moves[0]

    def evaluate_strategic_position(self, board: np.ndarray, row: int, col: int) -> float:
        """Evaluate a position for strategic value"""
        score = 0
        
        # Prefer center positions
        score += 10 * (6 - abs(row - 5.5) - abs(col - 5.5))
        
        # Value positions that could lead to sequences
        board[row][col] = self.ai_player
        for length in range(3, 6):
            if self.count_potential_sequences(board, row, col, self.ai_player, length):
                score += length * length * 10
        board[row][col] = ' '
        
        # Penalty for moves that help opponent
        board[row][col] = self.human_player
        for length in range(3, 6):
            if self.count_potential_sequences(board, row, col, self.human_player, length):
                score -= length * length * 15
        board[row][col] = ' '
        
        return score

    def count_potential_sequences(self, board: np.ndarray, row: int, col: int, player: str, length: int) -> int:
        """Count potential sequences that could be formed through this position"""
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        count = 0
        
        for dx, dy in directions:
            # Count pieces in both directions
            pieces = 1
            gaps = 0
            
            # Check forward
            r, c = row + dx, col + dy
            while 0 <= r < 12 and 0 <= c < 12 and gaps < 2 and pieces < length:
                if board[r][c] == player:
                    pieces += 1
                elif board[r][c] == ' ':
                    gaps += 1
                else:
                    break
                r, c = r + dx, c + dy
            
            # Check backward
            r, c = row - dx, col - dy
            while 0 <= r < 12 and 0 <= c < 12 and gaps < 2 and pieces < length:
                if board[r][c] == player:
                    pieces += 1
                elif board[r][c] == ' ':
                    gaps += 1
                else:
                    break
                r, c = r - dx, c - dy
            
            if pieces >= length - gaps:
                count += 1
                
        return count

    def hash_board(self, board: np.ndarray) -> str:
        """Create a unique hash for the board state"""
        return ''.join(board.flatten())

    def make_move(self, row: int, col: int, player: str) -> bool:
        """Make a move and notify the thinking thread of board update"""
        if not self.is_valid_move(row, col):
            return False
            
        with self.lock:
            if self.board[row][col] == ' ':
                opponent_exists = np.any(self.board == ('O' if player == 'X' else 'X'))
                if not opponent_exists or self.can_block(row, col, player):
                    self.board[row][col] = player
                    # Notify thinking thread of board update
                    self.board_updated.set()
                    return True
        return False

    def get_ai_move(self) -> Tuple[int, int]:
        """Get the best available move for the current board state"""
        with self.lock:
            board_hash = self.hash_board(self.board)
            
            # Check if we have a pre-computed move for this board state
            if board_hash in self.best_moves:
                return self.best_moves[board_hash]
            
            # If no pre-computed move, calculate one now
            return self.find_best_response(copy.deepcopy(self.board))

    def play_game(self):
        print("Welcome to Tic-Tac-Go!")
        print("You are X and the computer is O")
        print("To win, get 6 in a row horizontally, vertically, or diagonally")
        print("You can block the opponent by placing your mark adjacent to theirs")
        print("Dots (.) show valid moves for your turn")
        
        while True:
            self.print_board()
            
            if self.current_player == self.human_player:
                print("\nYour turn (X)")
                while True:
                    try:
                        row = int(input("Enter row (0-11): "))
                        col = int(input("Enter column (0-11): "))
                        
                        if (row, col) in self.get_valid_positions():
                            self.make_move(row, col, self.current_player)
                            break
                        else:
                            print("\nInvalid move! Please choose a position marked with a dot (.)")
                    except ValueError:
                        print("Please enter valid numbers!")
            else:
                move = self.get_ai_move()
                row, col = move
                print(f"\nAI plays at row {row}, column {col}")
                success = self.make_move(row, col, self.current_player)
                if not success:
                    print("AI made an invalid move! This shouldn't happen.")
                    break
            
            winner = self.check_winner()
            if winner:
                self.print_board()
                if winner == self.human_player:
                    print("\nCongratulations! You win!")
                else:
                    print("\nAI wins!")
                break
                
            if self.is_board_full():
                self.print_board()
                print("\nGame is a draw!")
                break
                
            self.current_player = 'O' if self.current_player == 'X' else 'X'

    def __del__(self):
        """Clean up the thinking thread when the game ends"""
        self.stop_thinking.set()
        if self.thinking_thread and self.thinking_thread.is_alive():
            self.thinking_thread.join()

# [Previous methods remain the same: print_board, is_valid_move, can_block, 
# check_winner, is_board_full, evaluate_position_for_state, etc.]
    def print_board(self):
        """Updated print_board method with correct state display"""
        valid_positions = self.get_valid_positions()
        
        print('   ', end='')
        for i in range(12):
            print(f' {i:2}', end='')
        print('\n    ' + '-' * 36)
        
        for i in range(12):
            print(f'{i:2} |', end=' ')
            for j in range(12):
                if self.board[i][j] != ' ':
                    print(f'{self.board[i][j]:3}', end='')
                elif (i, j) in valid_positions and self.current_player == self.human_player:
                    print(f'{".":3}', end='')
                else:
                    print(f'{" ":3}', end='')
            print()

    def is_valid_move(self, row: int, col: int) -> bool:
        if row < 0 or row >= 12 or col < 0 or col >= 12:
            return False
        return self.board[row][col] == ' '
    
    def can_block(self, row: int, col: int, player: str) -> bool:
        opponent = 'O' if player == 'X' else 'X'
        for i in range(max(0, row-1), min(12, row+2)):
            for j in range(max(0, col-1), min(12, col+2)):
                if self.board[i][j] == opponent:
                    return True
        return False
    
    def check_winner(self) -> Optional[str]:
        # Check rows, columns and diagonals for 6 in a row
        for i in range(12):
            for j in range(7):
                if all(self.board[i][j+k] == 'X' for k in range(6)): return 'X'
                if all(self.board[i][j+k] == 'O' for k in range(6)): return 'O'
                    
        for i in range(7):
            for j in range(12):
                if all(self.board[i+k][j] == 'X' for k in range(6)): return 'X'
                if all(self.board[i+k][j] == 'O' for k in range(6)): return 'O'
                    
        for i in range(7):
            for j in range(7):
                if all(self.board[i+k][j+k] == 'X' for k in range(6)): return 'X'
                if all(self.board[i+k][j+k] == 'O' for k in range(6)): return 'O'
                    
        for i in range(7):
            for j in range(5, 12):
                if all(self.board[i+k][j-k] == 'X' for k in range(6)): return 'X'
                if all(self.board[i+k][j-k] == 'O' for k in range(6)): return 'O'
                    
        return None
    
    def is_board_full(self) -> bool:
        return not np.any(self.board == ' ')

    def check_winner_for_state(self, board_state) -> Optional[str]:
        """Version of check_winner that works with a provided board state"""
        # Same logic as check_winner but uses provided board_state instead of self.board
        for i in range(12):
            for j in range(7):
                if all(board_state[i][j+k] == 'X' for k in range(6)): return 'X'
                if all(board_state[i][j+k] == 'O' for k in range(6)): return 'O'
        
        for i in range(7):
            for j in range(12):
                if all(board_state[i+k][j] == 'X' for k in range(6)): return 'X'
                if all(board_state[i+k][j] == 'O' for k in range(6)): return 'O'
        
        for i in range(7):
            for j in range(7):
                if all(board_state[i+k][j+k] == 'X' for k in range(6)): return 'X'
                if all(board_state[i+k][j+k] == 'O' for k in range(6)): return 'O'
        
        for i in range(7):
            for j in range(5, 12):
                if all(board_state[i+k][j-k] == 'X' for k in range(6)): return 'X'
                if all(board_state[i+k][j-k] == 'O' for k in range(6)): return 'O'
        
        return None

    def get_valid_moves_for_state(self, board_state) -> List[Tuple[int, int]]:
        """Version of get_valid_moves that works with a provided board state"""
        valid_moves = []
        blocking_moves = []
        
        for i in range(12):
            for j in range(12):
                if board_state[i][j] == ' ':
                    if self.can_block_for_state(i, j, self.ai_player, board_state):
                        blocking_moves.append((i, j))
                    elif not np.any(board_state != ' '):
                        valid_moves.append((i, j))
        
        return blocking_moves + valid_moves if blocking_moves else valid_moves

    def can_block_for_state(self, row: int, col: int, player: str, board_state) -> bool:
        """Version of can_block that works with a provided board state"""
        opponent = 'O' if player == 'X' else 'X'
        for i in range(max(0, row-1), min(12, row+2)):
            for j in range(max(0, col-1), min(12, col+2)):
                if board_state[i][j] == opponent:
                    return True
        return False

    def minimax_for_state(self, board_state, depth: int, alpha: float, beta: float, is_maximizing: bool) -> Tuple[int, Optional[Tuple[int, int]]]:
        """Version of minimax that works with a provided board state"""
        if depth == 0:
            return self.evaluate_position_for_state(board_state), None

        valid_moves = self.get_valid_moves_for_state(board_state)
        if not valid_moves:
            return 0, None

        best_move = None
        if is_maximizing:
            max_eval = float('-inf')
            for move in valid_moves:
                board_state[move[0]][move[1]] = self.ai_player
                eval, _ = self.minimax_for_state(board_state, depth - 1, alpha, beta, False)
                board_state[move[0]][move[1]] = ' '
                
                if eval > max_eval:
                    max_eval = eval
                    best_move = move
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval, best_move
        else:
            min_eval = float('inf')
            for move in valid_moves:
                board_state[move[0]][move[1]] = self.human_player
                eval, _ = self.minimax_for_state(board_state, depth - 1, alpha, beta, True)
                board_state[move[0]][move[1]] = ' '
                
                if eval < min_eval:
                    min_eval = eval
                    best_move = move
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval, best_move

    def evaluate_position_for_state(self, board_state) -> int:
        """Version of evaluate_position that works with a provided board state"""
        score = 0
        for i in range(12):
            for j in range(12):
                if board_state[i][j] == ' ':
                    # Check if this position completes a winning sequence
                    board_state[i][j] = self.human_player
                    if self.check_winner_for_state(board_state) == self.human_player:
                        score -= 10000
                    board_state[i][j] = self.ai_player
                    if self.check_winner_for_state(board_state) == self.ai_player:
                        score += 10000
                    board_state[i][j] = ' '
                    
                    # Value center positions more
                    center_value = (6 - abs(i - 5.5) - abs(j - 5.5)) * 10
                    score += center_value
        
        return score

    def get_valid_positions(self) -> List[Tuple[int, int]]:
        """Return all valid positions for the current player"""
        valid_positions = []
        for i in range(12):
            for j in range(12):
                if self.is_valid_move(i, j):
                    if not np.any(self.board != ' ') or self.can_block(i, j, self.current_player):
                        valid_positions.append((i, j))
        return valid_positions

if __name__ == "__main__":
    game = TicTacGo()
    game.play_game()
