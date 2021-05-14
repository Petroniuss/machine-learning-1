import random

from qtypes import *
import numpy as np


class Board:
    """
        This class holds a bunch of utilities..
    """

    def __init__(self, height: int, width: int,
                 castle_position: Position,
                 walls: List[Position]):
        self.height = height
        self.width = width
        self.castle_position = castle_position
        self.mask = [[None for _ in range(width)] for _ in range(height)]
        for p in walls:
            self.mask[p.y][p.x] = Obstacle.WALL

    def __getitem__(self, key: Position):
        x, y = key.x, key.y
        return self.mask[y][x]

    def __setitem__(self, key: Position, value: Obstacle):
        x, y = key.x, key.y
        self.mask[y][x] = value

    def is_accessible(self, state: QState, position: Position):
        x, y = position.x, position.y
        return self.is_within(position) and \
               self.mask[y][x] is None and \
               position not in state.occupied_positions()

    def filter_within(self, positions: List[Position]):
        return list(filter(lambda p: self.is_within(p), positions))

    def get_any_valid_movement(self, current_position: Position, state: QState):
        moves = list(self.possible_moves(state, current_position))
        if len(moves) < 1:
            return Movement(current_position)

        return Movement(moves[random.randint(0, len(moves) - 1)])

    def is_within(self, position: Position):
        x, y = position.x, position.y
        return 0 <= x < self.width and \
               0 <= y < self.height

    def positions_around(self, position: Position):
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if not (dx == dy == 0):
                    next_pos = position + Position(dx, dy)
                    if self.is_within(next_pos):
                        yield next_pos

    def possible_moves(self, state: QState, position: Position):
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if abs(dx) + abs(dy) == 1:
                    next_pos = position + Position(dx, dy)
                    if self.is_accessible(state, next_pos):
                        yield next_pos

    @staticmethod
    def is_attacked(position: Position, attacked_positions: List[Position]):
        for p in attacked_positions:
            if p == position:
                return True

        return False

    def to_numpy(self):
        return np.zeros((self.height, self.width))

    def numpy_repr(self, wall_value=1):
        M = np.zeros((self.height, self.width))
        for y in range(self.height):
            for x in range(self.width):
                if self.mask[y][x] == Obstacle.WALL:
                    M[y, x] = wall_value

        return M
