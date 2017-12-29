import time

import abstract
from Reversi.consts import BOARD_COLS, BOARD_ROWS, OPPONENT_COLOR, EM
from utils import INFINITY, MiniMaxWithAlphaBetaPruning


class Player(abstract.AbstractPlayer):
    def __init__(self, setup_time, player_color, time_per_k_turns, k):
        abstract.AbstractPlayer.__init__(self, setup_time, player_color, time_per_k_turns, k)
        self.clock = time.time()
        # We are simply providing (remaining time / remaining turns) for each turn in round.
        # Taking a spare time of 0.05 seconds.
        self.turns_remaining_in_round = self.k
        self.time_remaining_in_round = self.time_per_k_turns
        self.time_for_current_move = self.time_remaining_in_round / self.turns_remaining_in_round - 0.05

    def get_move(self, game_state, possible_moves):
        self.clock = time.time()
        self.time_for_current_move = self.time_remaining_in_round / self.turns_remaining_in_round - 0.05

        if len(possible_moves) == 1:
            return possible_moves[0]

        best_move = self.iterative_deepening(game_state)

        if self.turns_remaining_in_round == 1:
            self.turns_remaining_in_round = self.k
            self.time_remaining_in_round = self.time_per_k_turns
        else:
            self.turns_remaining_in_round -= 1
            self.time_remaining_in_round -= (time.time() - self.clock)

        return best_move

    def iterative_deepening(self, state):
        alpha_beta = MiniMaxWithAlphaBetaPruning(self.utility, self.color, self.no_more_time, False)
        depth = 1
        optimal_move = None
        while True:
            _, move = alpha_beta.search(state, depth, -INFINITY, INFINITY, True)
            if move is None:
                break
            optimal_move = move
            depth += 1

        return optimal_move

    def utility(self, state):
        delta_tiles = self.get_delta_tiles(state)
        if delta_tiles == INFINITY or delta_tiles == -INFINITY:
            return delta_tiles
        mobility = self.get_mobility(state)
        potential_mobility = self.get_potential_mobility(state)
        corner_ratio = self.get_corner_ratio(state)

        number_of_tiles = self.get_tiles_count(state)

        return number_of_tiles * delta_tiles / 32 + (64 - number_of_tiles) * (
                mobility + potential_mobility + 4 * corner_ratio) / 32

    def get_delta_tiles(self, state):
        my_u = 0
        op_u = 0
        for x in range(BOARD_COLS):
            for y in range(BOARD_ROWS):
                if state.board[x][y] == self.color:
                    my_u += 1
                if state.board[x][y] == OPPONENT_COLOR[self.color]:
                    op_u += 1

        if my_u == 0:
            # I have no tools left
            return -INFINITY
        elif op_u == 0:
            # The opponent has no tools left
            return INFINITY
        else:
            diff = my_u - op_u
            if len(state.get_possible_moves()) == 0:
                if diff > 0:
                    return INFINITY
                elif diff < 0:
                    return -INFINITY
            return my_u - op_u

    def get_mobility(self, state):
        """
        Get the player's number of possible move of the given state
        :param GameState state: the state to verify
        :return int:
        """
        state_color = state.curr_player
        state.curr_player = self.color
        possible_moves = len(state.get_possible_moves())
        state.curr_player = state_color
        return possible_moves

    def get_potential_mobility(self, state):
        """

        :param GameState state:
        :return:
        """
        potential_mobility = 0
        for x in range(BOARD_COLS):
            for y in range(BOARD_ROWS):
                if state.board[x][y] == self.color and self.is_adjacent_to_empty_field(state, x, y):
                    potential_mobility += 1
        return potential_mobility

    def is_adjacent_to_empty_field(self, state, x, y):
        """
        Check if there is an empty field next to the given tile
        :param GameState state:
        :param int x:
        :param int y:
        :return bool:
        """
        for x_adj in [x - 1, x, x + 1]:
            for y_adj in [y - 1, y, y + 1]:
                if not (self.is_in_board(x_adj, y_adj)):
                    continue

                if state.board[x_adj][y_adj] == EM:
                    return True

        return False

    def is_in_board(self, x, y):
        """
        :param int y:
        :param int x:
        :return bool:
        """
        return 1 <= x <= BOARD_ROWS - 1 and 1 <= y <= BOARD_COLS - 1

    def get_corner_ratio(self, state):
        """

        :param GameState state:
        :return double:
        """
        my_corner_tiles = 0
        op_corner_tiles = 0
        for x, y in [[0, 0], [0, BOARD_COLS - 1], [BOARD_ROWS - 1, 0], [BOARD_ROWS - 1, BOARD_COLS - 1]]:
            if state.board[x][y] == self.color:
                my_corner_tiles += 1
            elif state.board[x][y] == OPPONENT_COLOR[self.color]:
                op_corner_tiles += 1

        return my_corner_tiles - op_corner_tiles

    def no_more_time(self):
        return (time.time() - self.clock) >= self.time_for_current_move

    def get_tiles_count(self, state):
        tile = 0
        for row in state.board:
            for box in row:
                if box != EM:
                    tile += 1
        return tile

    def __repr__(self):
        return '{} {}'.format(abstract.AbstractPlayer.__repr__(self), 'alpha_beta')
