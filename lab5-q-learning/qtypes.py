from dataclasses import dataclass
from enum import Enum

from typing import List


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


@dataclass(eq=True, order=True, frozen=True)
class QState:
    witcher_position: Position
    striga_position: Position

    def occupied_positions(self) -> List[Position]:
        return [self.witcher_position, self.striga_position]


class MovementScheme:
    def next_action(self, state: QState) -> Action:
        raise NotImplementedError('Abstract method')


class Striga:
    def __init__(self, movement_scheme: MovementScheme):
        self.movement_scheme = movement_scheme

    def next_action(self, state: QState):
        return self.movement_scheme.next_action(state)


class Witcher:
    """
    We should be able to measure witcher's progress somehow.
    """
    def __init__(self, movement_scheme: MovementScheme):
        self.movement_scheme = movement_scheme

    def next_action(self, state: QState):
        return self.movement_scheme.next_action(state)
