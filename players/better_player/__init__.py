import copy
import time

import abstract
from Reversi.board import GameState, OPPONENT_COLOR, BOARD_COLS, BOARD_ROWS, EM
from utils import INFINITY
from history_manager import HistoryManager


class Player(abstract.AbstractPlayer):
    def __init__(self, setup_time, player_color, time_per_k_turns, k):
        abstract.AbstractPlayer.__init__(self, setup_time, player_color, time_per_k_turns, k)
        self.clock = time.time()

        # We are simply providing (remaining time / remaining turns) for each turn in round.
        # Taking a spare time of 0.05 seconds.
        self.turns_remaining_in_round = self.k
        self.time_remaining_in_round = self.time_per_k_turns
        self.time_for_current_move = self.time_remaining_in_round / self.turns_remaining_in_round - 0.05
        self.hist_mgr = HistoryManager()

    def get_move(self, game_state, possible_moves):
        """

        :param GameState game_state:
        :param possible_moves:
        :return: Tuple of (x,y)
        """
        self.clock = time.time()
        self.time_for_current_move = self.time_remaining_in_round / self.turns_remaining_in_round - 0.05

        self.hist_mgr.update(new_board=game_state.board)
        if len(possible_moves) == 1:
            self.hist_mgr.update(new_move=possible_moves[0])
            return possible_moves[0]

        hist_mgr_out = self.hist_mgr.get_next_move()
        if hist_mgr_out is not None:
            self.hist_mgr.update(new_move=hist_mgr_out)
            return hist_mgr_out

        best_move = possible_moves[0]
        next_state = copy.deepcopy(game_state)
        next_state.perform_move(best_move[0], best_move[1])
        # Choosing an arbitrary move
        # Get the best move according the utility function
        for move in possible_moves:
            new_state = copy.deepcopy(game_state)
            new_state.perform_move(move[0], move[1])
            if self.utility(new_state) > self.utility(next_state):
                next_state = new_state
                best_move = move

        if self.turns_remaining_in_round == 1:
            self.turns_remaining_in_round = self.k
            self.time_remaining_in_round = self.time_per_k_turns
        else:
            self.turns_remaining_in_round -= 1
            self.time_remaining_in_round -= (time.time() - self.clock)

        self.hist_mgr.update(new_move=best_move)
        return best_move


    def utility(self, state):
        delta_tiles = self.get_delta_tiles(state)
        if delta_tiles == INFINITY or delta_tiles == -INFINITY:
            return delta_tiles
        mobility = self.get_mobility(state)
        potential_mobility = self.get_potential_mobility(state)
        corner_ratio = self.get_corner_ratio(state)

        return 3 * delta_tiles + mobility + potential_mobility + 4 * corner_ratio


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

    def __repr__(self):
        return '{} {}'.format(abstract.AbstractPlayer.__repr__(self), 'better')
