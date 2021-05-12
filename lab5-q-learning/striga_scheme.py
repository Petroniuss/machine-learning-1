import random

import numpy as np

from board import Board
from qtypes import *


class StrigaDeterministicMovementScheme(MovementScheme):
    """
        Walk around a square of length 'p'.
        Attack on every corner.
    """

    def __init__(self, board: Board, p: int):
        self.board = board
        self.p = p
        self.directions = [
            [0, 1],
            [1, 0],
            [0, -1],
            [-1, 0]
        ]

        self.current_p = 0
        self.current_direction = 0

    def next_action(self, state: QState):
        current_pos = state.striga_position
        dx, dy = self.directions[self.current_direction]
        next_pos = current_pos + Position(dx, dy)

        self.current_p += 1
        if self.current_p >= self.p:
            attacked_positions = self.get_attacked_positions(current_pos)
            self.current_direction = (self.current_direction + 1) % 4
            self.current_p = 0

            return Attack(attacked_positions)

        if self.board.is_accessible(state, next_pos):
            return Movement(next_pos)

        return self.board.get_any_valid_movement(state.striga_position, state)

    def get_attacked_positions(self, current_position: Position):
        dx, dy = self.directions[self.current_direction]
        positions = calculate_attacked_positions(current_position, dx, dy)

        return self.board.filter_within(positions)


class StrigaRandomMovementScheme(MovementScheme):
    """
        Move in a totally random fashion,
        attack with defined probability 3 fields in one of 4 directions.
    """
    def __init__(self, board: Board, p_attack=.25):
        self.board = board
        self.p_attack = p_attack
        self.directions = [
            [0, 1],
            [1, 0],
            [0, -1],
            [-1, 0]
        ]

    def get_attacked_positions(self, current_position: Position):
        dx, dy = self.directions[np.random.randint(0, 3)]
        positions = calculate_attacked_positions(current_position, dx, dy)

        return list(filter(lambda p: self.board.is_within(p), positions))

    def next_action(self, state: QState):
        if random.uniform(.0, 1.) < self.p_attack:
            return Attack(self.get_attacked_positions(state.striga_position))
        else:
            return self.board.get_any_valid_movement(state.striga_position, state)


def calculate_attacked_positions(current_position: Position, dx, dy):
    if dx == 0:
        return [
            current_position + Position(dx, dy),
            current_position + Position(dx - 1, 0),
            current_position + Position(dx + 1, 0)
        ]
    elif dy == 0:
        return [
            current_position + Position(dx, dy),
            current_position + Position(0, dy - 1),
            current_position + Position(0, dy + 1)
        ]
    else:
        raise Exception('Invalid state')
