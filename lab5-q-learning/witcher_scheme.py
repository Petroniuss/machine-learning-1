from qtypes import *
import board


class WitcherMovementSchemeSARSA(WitcherScheme):
    def __init__(self, brd: board.Board, learning_rate=.9, experiment_rate=.1, discount_factor=.1):
        super().__init__(brd, learning_rate, experiment_rate, discount_factor)

        self.s1 = None
        self.a1 = None

    def next_action(self, state: QState):
        if self.a1 is None:
            self.s1 = state
            self.a1 = self.choose_action(state)

            return self.a1

        s2 = state
        a2 = self.choose_action(state)

        self.update(self.s1, s2, self.reward, self.a1, a2)

        self.s1 = s2
        self.a1 = a2

        return a2


class WitcherMovementSchemeQLearning(WitcherScheme):
    def __init__(self, brd: board.Board, learning_rate=.9, experiment_rate=.1, discount_factor=.1):
        super().__init__(brd, learning_rate, experiment_rate, discount_factor)
        self.s1 = None
        self.a1 = None

    def next_action(self, state: QState):
        if self.s1 is None:
            self.s1 = state
            self.a1 = self.choose_action(state)

            return self.a1

        s2 = state
        max_a = self.best_action(s2)

        self.update(self.s1, s2, self.reward, self.a1, max_a)

        self.s1 = s2
        self.a1 = self.choose_action(s2)

        return self.a1

