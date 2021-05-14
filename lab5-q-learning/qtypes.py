import random
from abc import ABC
from dataclasses import dataclass
from enum import Enum

from typing import List

import numpy as np


@dataclass(eq=True, order=True, frozen=True)
class Position:
    x: int
    y: int

    def __add__(self, other):
        return Position(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Position(self.x - other.x, self.y - other.y)


class GameResult(Enum):
    WITCHER = 1
    STRIGA = 2


class Obstacle(Enum):
    WALL = 1


class Action:
    pass


@dataclass(eq=True, order=True, frozen=True)
class Movement(Action):
    new_position: Position


@dataclass(eq=True, order=True, frozen=True)
class Attack(Action):
    attacked_positions: List[Position]


@dataclass(eq=True, order=True, frozen=True)
class HalfTurnAttack(Action):
    pass


witcher_attack_action = HalfTurnAttack()


@dataclass(eq=True, order=True, frozen=True)
class QState:
    witcher_position: Position
    striga_position: Position

    def occupied_positions(self) -> List[Position]:
        return [self.witcher_position, self.striga_position]

    def distance(self):
        dv = self.striga_position - self.witcher_position
        return abs(dv.x) + abs(dv.y)


class MovementScheme:
    def next_action(self, state: QState) -> Action:
        raise NotImplementedError('Abstract method')


class Striga:
    def __init__(self, movement_scheme: MovementScheme):
        self.movement_scheme = movement_scheme

    def next_action(self, state: QState):
        return self.movement_scheme.next_action(state)


class WitcherScheme(MovementScheme, ABC):
    def __init__(self, board,
                 learning_rate=.1,
                 experiment_rate=.1,
                 discount_factor=.1):
        self.board = board
        self.learning_rate = learning_rate
        self.experiment_rate = experiment_rate
        self.discount_factor = discount_factor

        self.Q = {}
        self.reward = None

    def set_reward(self, reward):
        self.reward = reward

    def all_possible_actions(self, state: QState) -> List[Action]:
        moves = list(map(lambda p: Movement(p), self.board.possible_moves(state, state.witcher_position)))
        return moves + [witcher_attack_action, Movement(state.witcher_position)]

    def choose_action(self, state: QState):
        if np.random.uniform(0, 1) < self.experiment_rate:
            return self.random_action(state)
        else:
            return self.best_action(state)

    def random_action(self, state):
        actions = self.all_possible_actions(state)
        return actions[random.randint(0, len(actions) - 1)]

    def update(self, s1, s2, r, a1, a2):
        predict = self.Q.get((s1, a1), 0.0)
        target = r + self.discount_factor * self.Q.get((s2, a2), 0.0)
        self.Q[(s1, a1)] = predict + self.learning_rate * (target - predict)

    def best_action(self, state: QState) -> Action:
        # if you can't make any other move don't move
        best, best_score = None, None
        for action in self.all_possible_actions(state):
            score = self.Q.get((state, action), 0.0)
            if best_score is None or score >= best_score:
                best = action
                best_score = score

        return best


class Witcher:
    """
        We should be able to measure witcher's progress somehow.
    """

    def __init__(self, scheme: WitcherScheme):
        self.scheme = scheme

    def set_reward(self, reward):
        self.scheme.set_reward(reward)

    def next_action(self, state: QState):
        return self.scheme.next_action(state)
