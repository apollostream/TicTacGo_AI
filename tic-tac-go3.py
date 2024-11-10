import numpy as np
from typing import Tuple, Optional, List

class TicTacGo:
    def __init__(self):
        self.board = np.full((12, 12), ' ')
        self.current_player = 'X'
        self.winner = None
        self.ai_player = 'O'
        self.human_player = 'X'
        
    def print_board(self):
        print('   ', end='')
        for i in range(12):
            print(f' {i:2}', end='')
        print('\n    ' + '-' * 36)
        
        for i in range(12):
            print(f'{i:2} |', end=' ')
            for j in range(12):
                print(f'{self.board[i][j]:2}', end='')
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
    
    def make_move(self, row: int, col: int, player: str) -> bool:
        if not self.is_valid_move(row, col):
            return False
            
        if self.board[row][col] == ' ':
            opponent_exists = np.any(self.board == ('O' if player == 'X' else 'X'))
            if not opponent_exists or self.can_block(row, col, player):
                self.board[row][col] = player
                return True
        return False

    def get_sequence_count(self, row: int, col: int, player: str) -> int:
        """Count the longest possible sequence that could be formed through this position"""
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]  # horizontal, vertical, diagonal, anti-diagonal
        max_sequence = 0
        
        for dx, dy in directions:
            sequence = 1
            # Check forward
            r, c = row + dx, col + dy
            while 0 <= r < 12 and 0 <= c < 12 and (self.board[r][c] == player or self.board[r][c] == ' '):
                sequence += 1
                r, c = r + dx, c + dy
            # Check backward
            r, c = row - dx, col - dy
            while 0 <= r < 12 and 0 <= c < 12 and (self.board[r][c] == player or self.board[r][c] == ' '):
                sequence += 1
                r, c = r - dx, c - dy
            max_sequence = max(max_sequence, sequence)
        return max_sequence

    def evaluate_position(self) -> int:
        """Enhanced evaluation function"""
        score = 0
        
        # Check for immediate threats (5 in a row)
        for i in range(12):
            for j in range(12):
                if self.board[i][j] == ' ':
                    # Check if this position completes a winning sequence
                    self.board[i][j] = self.human_player
                    if self.check_winner() == self.human_player:
                        score -= 10000  # Very high priority to block winning moves
                    self.board[i][j] = self.ai_player
                    if self.check_winner() == self.ai_player:
                        score += 10000  # Very high priority to make winning moves
                    self.board[i][j] = ' '
                    
                    # Evaluate potential sequences
                    ai_potential = self.get_sequence_count(i, j, self.ai_player)
                    human_potential = self.get_sequence_count(i, j, self.human_player)
                    
                    if ai_potential >= 6:
                        score += 1000
                    if human_potential >= 6:
                        score -= 1000
                    
                    # Value center positions more
                    center_value = (6 - abs(i - 5.5) - abs(j - 5.5)) * 10
                    score += center_value
        
        return score

    def get_valid_moves(self) -> List[Tuple[int, int]]:
        """Get all valid moves, prioritizing blocking moves"""
        valid_moves = []
        blocking_moves = []
        
        for i in range(12):
            for j in range(12):
                if self.is_valid_move(i, j):
                    if self.can_block(i, j, self.current_player):
                        blocking_moves.append((i, j))
                    elif not np.any(self.board != ' '):
                        valid_moves.append((i, j))
                        
        return blocking_moves + valid_moves if blocking_moves else valid_moves

    def minimax(self, depth: int, alpha: float, beta: float, is_maximizing: bool) -> Tuple[int, Optional[Tuple[int, int]]]:
        """Enhanced minimax algorithm"""
        winner = self.check_winner()
        if winner == self.ai_player:
            return 10000, None
        elif winner == self.human_player:
            return -10000, None
        elif depth == 0:
            return self.evaluate_position(), None

        valid_moves = self.get_valid_moves()
        if not valid_moves:
            return 0, None

        best_move = None
        if is_maximizing:
            max_eval = float('-inf')
            for move in valid_moves:
                self.board[move[0]][move[1]] = self.ai_player
                eval, _ = self.minimax(depth - 1, alpha, beta, False)
                self.board[move[0]][move[1]] = ' '
                
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
                self.board[move[0]][move[1]] = self.human_player
                eval, _ = self.minimax(depth - 1, alpha, beta, True)
                self.board[move[0]][move[1]] = ' '
                
                if eval < min_eval:
                    min_eval = eval
                    best_move = move
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval, best_move

    def ai_move(self) -> Tuple[int, int]:
        """Enhanced AI move selection"""
        print("\nAI is thinking...")
        
        # First, check for immediate winning move
        for i in range(12):
            for j in range(12):
                if self.is_valid_move(i, j):
                    self.board[i][j] = self.ai_player
                    if self.check_winner() == self.ai_player:
                        self.board[i][j] = ' '
                        return (i, j)
                    self.board[i][j] = ' '
        
        # Then, check for immediate blocking needs
        for i in range(12):
            for j in range(12):
                if self.is_valid_move(i, j):
                    self.board[i][j] = self.human_player
                    if self.check_winner() == self.human_player:
                        self.board[i][j] = ' '
                        return (i, j)
                    self.board[i][j] = ' '
        
        # If no immediate threats, use minimax
        _, move = self.minimax(4, float('-inf'), float('inf'), True)
        if move is None:
            # Fallback to first valid move if minimax fails
            move = self.get_valid_moves()[0]
        return move

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
    
    def play_game(self):
        print("Welcome to Tic-Tac-Go!")
        print("You are X and the computer is O")
        print("To win, get 6 in a row horizontally, vertically, or diagonally")
        print("You can block the opponent by placing your mark adjacent to theirs")
        
        while True:
            self.print_board()
            
            if self.current_player == self.human_player:
                print("\nYour turn (X)")
                while True:
                    try:
                        row = int(input("Enter row (0-11): "))
                        col = int(input("Enter column (0-11): "))
                        
                        if self.make_move(row, col, self.current_player):
                            break
                        else:
                            print("\nInvalid move! The space must be empty and either:")
                            print("1. Be adjacent to an opponent's mark (blocking move)")
                            print("2. Be any empty space if no opponent marks exist")
                    except ValueError:
                        print("Please enter valid numbers!")
            else:
                row, col = self.ai_move()
                self.make_move(row, col, self.current_player)
                print(f"\nAI plays at row {row}, column {col}")
            
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

if __name__ == "__main__":
    game = TicTacGo()
    game.play_game()
