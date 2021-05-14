from board import Board
from qtypes import *



class Env:
    def __init__(self, board: Board,
                 initial_state: QState,
                 striga: Striga, witcher: Witcher):
        self.board = board
        self.striga = striga
        self.witcher = witcher
        self.state = initial_state

        self.attacked_positions = []
        self.hits = 0
        self.turn = 0
        self.game_res = None
        self.witcher_positions = self.board.to_numpy()

    ## todo cleanup!
    def advance(self):
        # witcher's turn
        if self.turn % 2 == 0:
            action = self.witcher.next_action(self.state)
            reward = 0.0
            new_state = self.state
            if isinstance(action, Movement):
                new_position = action.new_position
                prev_state = self.state
                new_state = QState(new_position, self.state.striga_position)
                if new_state.distance() < prev_state.distance():
                    reward = 5.0

                self.witcher_positions[new_position.y, new_position.x] += 1

            elif isinstance(action, HalfTurnAttack):
                self.attacked_positions = list(self.board.positions_around(new_state.witcher_position))
                if self.board.is_attacked(new_state.striga_position, self.attacked_positions):
                    # new_state = QState(self.state.witcher_position, self.board.castle_position)
                    reward = 10.

                    self.hits += 1
                    if self.hits >= 3:
                        self.game_res = GameResult.WITCHER

            self.witcher.set_reward(reward)
            self.state = new_state

        # striga's turn
        else:
            action = self.striga.next_action(self.state)
            if isinstance(action, Movement):
                self.state = QState(self.state.witcher_position, action.new_position)
            elif isinstance(action, Attack):
                self.attacked_positions = action.attacked_positions
                if self.board.is_attacked(self.state.witcher_position, self.attacked_positions):
                    ## we need to ask witcher for his next action in order
                    ## for him to see that he lost!
                    self.witcher.set_reward(-20.0)
                    self.witcher.next_action(self.state)
                    self.game_res = GameResult.STRIGA

        self.turn += 1
        if self.turn >= 1000:
            self.game_res = GameResult.STRIGA

