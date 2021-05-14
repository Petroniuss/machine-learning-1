import numpy as np

from qtypes import *
import board


class WitcherMovementSchemeSARSA(WitcherScheme):
    def __init__(self, brd: board.Board, learning_rate=.9, experiment_rate=.1, discount_factor=.1):
        super().__init__(brd, learning_rate, experiment_rate, discount_factor)

        self.s1 = None
        self.a1 = None

    def choose_action(self, state: QState):
        if np.random.uniform(0, 1) < self.experiment_rate:
            return self.random_action(state)
        else:
            return self.pick_next_action(state)

    def update(self, s1, s2, r, a1, a2):
        predict = self.Q.get((s1, a1), 0.0)
        target = r + self.discount_factor * self.Q.get((s2, a2), 0.0)
        self.Q[(s1, a1)] = predict + self.learning_rate * (target - predict)

    def next_action(self, state: QState):
        if self.a1 is None:
            self.s1 = state
            self.a1 = self.pick_next_action(state)

            return self.a1

        s2 = state
        a2 = self.choose_action(state)

        self.update(self.s1, s2, self.reward, self.a1, a2)

        self.s1 = s2
        self.a1 = a2

        return a2
