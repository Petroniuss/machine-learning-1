import typing

from board import Board
from qtypes import *


class WitcherMovementSchemeSARSA(MovementScheme):
    def __init__(self, board: Board,
                 learning_rate=.1,
                 experiment_rate=.1,
                 discount_factor=.1):
        self.board = board
        self.learning_rate = learning_rate
        self.experiment_rate = experiment_rate
        self.discount_factor = discount_factor

        self.Q = {}
        self.witcher_attack_action = HalfTurnAttack()

    def possible_actions(self, state: QState) -> List[Action]:
        moves = list(map(lambda p: Movement(p), self.board.possible_moves(state, state.witcher_position)))
        return moves + [self.witcher_attack_action]

    def pick_next_action(self, state: QState) -> typing.Tuple[Action, float]:
        # if you can't make any other move don't move
        best, best_score = Movement(state.witcher_position), 0.0
        for action in self.possible_actions(state):
            score = self.Q.get((state, action), 0.0)
            if score >= best_score:
                best = action
                best_score = score

        return best, best_score

    def next_action(self, state: QState):
        best, best_score = self.pick_next_action(state)
        print(best)

        r = 0.0
        if isinstance(best, HalfTurnAttack):
            pass
        elif isinstance(best, Movement):
            pass

        return best
