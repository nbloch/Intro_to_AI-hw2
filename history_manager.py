import operator

from Reversi.board import GameState, OPPONENT_COLOR, BOARD_COLS, BOARD_ROWS, EM


class HistoryManager:
    def __init__(self):
        self.board = self.flatten_board(GameState().board)
        self.opening_list = []
        with open(r"Reversi/book.gam", "r") as opening_file:
            games = opening_file.readlines()
            opening_hist = dict()
            for game in games:
                opening = game[:30]
                if opening not in opening_hist:
                    opening_hist[opening] = 1
                else:
                    opening_hist[opening] += 1
            sorted_hist = sorted(opening_hist.items(), key=operator.itemgetter(1), reverse=True)
            for entry in sorted_hist[:70]:
                self.opening_list.append(str(entry[0]) + " " + str(entry[1]))


        self.history_string = ""
        self.first_char = "+"

    def update(self, new_board=None, new_move=None):
        """

        :param list new_board:
        :param tuple new_move:
        :return: None
        """
        if new_board is None and new_move is None:
            raise Exception("Not enough parameters")
        elif new_board is not None and new_move is not None:
            raise Exception("Too many parameters")

        if new_board is not None:
            for x in range(BOARD_COLS):
                for y in range(BOARD_ROWS):
                    if self.board[x][y] == EM and new_board[x][y] != EM:
                        self.history_string += (self.first_char + self.col2letter(y) + str(x + 1))
                        self.board[x][y] = "+"
                        self.first_char = "+" if self.first_char == "-" else "-"
                        break  # no need to continue, the method should be called after each move...
        elif new_move is not None:
            if self.board[new_move[0]][new_move[1]] != EM:
                return
            self.history_string += (self.first_char + self.col2letter(new_move[1]) + str(new_move[0] + 1))
            self.board[new_move[0]][new_move[1]] = "+"
            self.first_char = "+" if self.first_char == "-" else "-"

    def get_next_move(self):
        next_mv = ""
        history_str_len = self.history_string.__len__()
        for game in self.opening_list:
            if game.startswith(self.history_string):
                next_mv = game[history_str_len + 1:history_str_len + 3]
                break
        if next_mv == "":
            return None
        return int(next_mv[1]) - 1, self.letter2col(next_mv[0])

    @staticmethod
    def flatten_board(board: list):
        for x in range(BOARD_COLS):
            for y in range(BOARD_ROWS):
                if board[x][y] != EM:
                    board[x][y] = "+"
        return board

    @staticmethod
    def col2letter(c):
        return chr(ord('a') + c)

    @staticmethod
    def letter2col(l):
        return ord(l) - ord('a')
