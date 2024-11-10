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
                print(f'{self.board[i][j]:3}', end='')
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
    
    def evaluate_position(self,verbose=False,move_string='',debug=False) -> int:
        """Evaluate the current board position for AI"""
        score = 0
        # Check for potential winning sequences
        sequences={'X':{3:0,4:0,5:0,6:0},'O':{3:0,4:0,5:0,6:0}}
        for player, multiplier in [(self.ai_player, 1), (self.human_player, -1.1)]:
            # Count sequences of different lengths
            for length in range(3, 7):
                count = self.count_sequences(player, length)
                if (length >= 6) & (count > 0):
                    factor =  10**9 #float('inf')
                else:
                    factor = 1
                score += count * multiplier * factor * (length ** 2)
                sequences[player][length] = count
                #if verbose:
                    #print(f'......player={player}, length={length}, count={count}, score={score}...')
        if verbose:
            print(f'{move_string}...score={score}')
        if debug:
            return score,sequences
            
        return score

    def count_sequences(self, player: str, length: int) -> int:
        """Count sequences of given length for a player"""
        count = 0
        
        # Check rows
        for i in range(12):
            for j in range(13 - length):
                if all(self.board[i][j+k] == player for k in range(length)):
                    count += 1
                    
        # Check columns
        for i in range(13 - length):
            for j in range(12):
                if all(self.board[i+k][j] == player for k in range(length)):
                    count += 1
                    
        # Check diagonals
        for i in range(13 - length):
            for j in range(13 - length):
                if all(self.board[i+k][j+k] == player for k in range(length)):
                    count += 1
                if all(self.board[i+k][j+length-1-k] == player for k in range(length)):
                    count += 1
                    
        return count

    def get_valid_moves(self,player: str) -> List[Tuple[int, int]]:
        """Get all valid moves for the current state"""
        tmp_player = self.current_player
        self.current_player = player
        valid_moves = []
        for i in range(12):
            for j in range(12):
                if self.is_valid_move(i, j):
                    if not np.any(self.board != ' ') or self.can_block(i, j, self.current_player):
                        valid_moves.append((i, j))

        self.current_player = tmp_player
        return valid_moves

    def minimax(self, depth: int, alpha: float, beta: float, is_maximizing: bool, verbose: bool = False,move_string: str = '') -> Tuple[int, Optional[Tuple[int, int]]]:
        """Minimax algorithm with alpha-beta pruning"""
        if depth == 0:
            return self.evaluate_position(verbose,move_string), None

        if is_maximizing:
            player = self.ai_player
        else:
            player = self.human_player
            
        valid_moves = self.get_valid_moves(player)
        if not valid_moves:
            return 0, None

        best_move = None
        if is_maximizing:
            max_eval = float('-inf')
            for move in valid_moves:
                #verbose = verbose | (depth == 3 & (move[1]==4 | move[1]==5))
                #if verbose:
                #    print('...'*(3-depth) + f'...{self.ai_player}==>{move}')
                self.board[move[0]][move[1]] = self.ai_player
                eval, _ = self.minimax(depth - 1, alpha, beta, False,verbose,move_string+f'{self.ai_player}=>{move}|')
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
                #if verbose:
                #    print('...'*(3-depth) + f'...{self.human_player}==>{move}')
                self.board[move[0]][move[1]] = self.human_player
                eval, _ = self.minimax(depth - 1, alpha, beta, True, verbose,move_string+f'{self.human_player}=>{move}|')
                self.board[move[0]][move[1]] = ' '
                
                if eval < min_eval:
                    min_eval = eval
                    best_move = move
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval, best_move

    def ai_move(self) -> Tuple[int, int]:
        """Make AI move using minimax algorithm"""
        print("\nAI is thinking...")
        best_eval, move = self.minimax(3, float('-inf'), float('inf'), True)
        if move is None:
            # Fallback to first valid move if minimax fails
            move = self.get_valid_moves()[0]
            print('...minimax failed...')
        else:
            print(f'...best_eval={best_eval}, move={move}...')
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
