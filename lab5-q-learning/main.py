from dataclasses import dataclass
from enum import Enum


@dataclass
class Position:
    x: int
    y: int

    def __add__(self, other):
        return Position(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Position(self.x - other.x, self.y - other.y)


class Obstacle(Enum):
    WALL = 1


class Action:
    pass


@dataclass(eq=True, order=True)
class Movement(Action):
    new_position: Position


@dataclass(eq=True, order=True)
class Attack(Action):
    attacked_positions: list[Position]


@dataclass(eq=True, order=True)
class State:
    witcher_position: Position
    striga_position: Position

    def occupied_positions(self) -> list[Position]:
        return [self.witcher_position, self.striga_position]


class Board:
    def __init__(self, height: int, width: int,
                 castle_position: Position,
                 walls: list[Position]):
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

    def is_accessible(self, state: State, position: Position):
        x, y = position.x, position.y
        return self.mask[y][x] is None and position not in state.occupied_positions()

    def possible_moves(self, state: State, position: Position):
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if not (dx == dy == 0):
                    next_pos = position + Position(dx, dy)
                    if self.is_accessible(state, next_pos):
                        yield next_pos


class StrigaMovementScheme:
    def __init__(self, board: Board):
        self.board = board

    def make_move(self, state: State):
        raise NotImplementedError("abstract method!")


class DeterministicMovementScheme(StrigaMovementScheme):
    def __init__(self, board: Board, radius: int, attack_freq):
        super().__init__(board)
        self.radius = radius
        self.attack_freq = attack_freq

        self.current_radius = 0
        self.current_direction = 0
        self.directions = [
            [1, 1],
            [1, -1],
            [-1, -1],
            [-1, 1]
        ]

    def attack(self, current_position: Position):
        dx, dy = self.directions[self.current_direction]
        ddx = -1 if dx == 1 else 1
        ddy = -1 if dy == 1 else 1

        return [
            current_position + Position(dx, dy),
            current_position + Position(dx + ddx, dy),
            current_position + Position(dx, dy + ddy)
        ]

    def make_move(self, state: State):
        current_pos = state.striga_position
        dx, dy = self.directions[self.current_direction]
        next_pos = current_pos + Position(dx, dy)

        self.current_radius += 1
        if self.current_radius >= self.radius:
            attack = self.attack(current_pos)
            self.current_direction = (self.current_direction + 1) % 4
            self.current_radius = 0

            return attack

        if self.board.is_accessible(state, next_pos):
            return next_pos

        return Movement(next(self.board.possible_moves(state, current_pos)))
