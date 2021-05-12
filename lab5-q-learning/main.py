import random
import typing
from dataclasses import dataclass
from enum import Enum

import matplotlib
from typing import List

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

matplotlib.rcParams["backend"] = "TkAgg"
plt.rcParams["image.cmap"] = "nipy_spectral"

ani = None

wall_color = 1
witcher_color = .6
striga_color = .15
attacked_color = .1


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

class GameResult(Enum):
    WITCHER = 1
    STRIGA = 2


@dataclass(eq=True, order=True)
class Movement(Action):
    new_position: Position


@dataclass(eq=True, order=True)
class Attack(Action):
    attacked_positions: List[Position]


@dataclass(eq=True, order=True)
class State:
    witcher_position: Position
    striga_position: Position

    def occupied_positions(self) -> List[Position]:
        return [self.witcher_position, self.striga_position]


class Board:
    def __init__(self, height: int, width: int,
                 castle_position: Position,
                 walls: List[Position]):
        self.height = height
        self.width = width
        self.castle_position = castle_position
        self.mask = [[None for _ in range(width)] for _ in range(height)]
        for p in walls:
            self.mask[p.y][p.x] = Obstacle.WALL

    def numpy_repr(self):
        M = np.zeros((self.height, self.width))
        for y in range(self.height):
            for x in range(self.width):
                if self.mask[y][x] == Obstacle.WALL:
                    M[y, x] = wall_color

        return M

    def __getitem__(self, key: Position):
        x, y = key.x, key.y
        return self.mask[y][x]

    def __setitem__(self, key: Position, value: Obstacle):
        x, y = key.x, key.y
        self.mask[y][x] = value

    def is_accessible(self, state: State, position: Position):
        x, y = position.x, position.y
        return 0 <= x < self.width and \
            0 <= y < self.height and \
            self.mask[y][x] is None and \
            position not in state.occupied_positions()

    def possible_moves(self, state: State, position: Position):
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if not (dx == dy == 0):
                    next_pos = position + Position(dx, dy)
                    if self.is_accessible(state, next_pos):
                        yield next_pos


class MovementScheme:
    def __init__(self, board: Board):
        self.board = board

    def make_move(self, state: State):
        raise NotImplementedError('Abstract method')


class StrigaDeterministicMovementScheme(MovementScheme):
    def __init__(self, board: Board, p: int):
        super().__init__(board)
        self.p = p

        self.current_radius = 0
        self.current_direction = 0
        self.directions = [
            [1, 1],
            [1, -1],
            [-1, -1],
            [-1, 1]
        ]

    def attacked_positions(self, current_position: Position):
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
        if self.current_radius >= self.p:
            attacked_positions = self.attacked_positions(current_pos)
            self.current_direction = (self.current_direction + 1) % 4
            self.current_radius = 0

            return Attack(attacked_positions)

        if self.board.is_accessible(state, next_pos):
            return Movement(next_pos)

        return Movement(next(self.board.possible_moves(state, current_pos)))


class WitcherMovementSchemeSARSA(MovementScheme):
    def __init__(self, board: Board):
        super().__init__(board)

    def make_move(self, state: State):
        moves = list(self.board.possible_moves(state, state.witcher_position))
        return Movement(moves[random.randint(0, len(moves) - 1)])


class Striga:
    def __init__(self, movement_scheme: MovementScheme):
        self.movement_scheme = movement_scheme

    def make_move(self, state: State):
        return self.movement_scheme.make_move(state)


class Witcher:
    def __init__(self, movement_scheme: MovementScheme):
        self.movement_scheme = movement_scheme

    def make_move(self, state: State):
        return self.movement_scheme.make_move(state)


class Game:
    def __init__(self, board: Board,
                 initial_state: State,
                 striga: Striga, witcher: Witcher):
        self.board = board
        self.striga = striga
        self.witcher = witcher
        self.state = initial_state

        self.attacked_positions = []
        self.striga_hp = 3
        self.turn = 0
        self.game_res = None

    def advance(self):
        # witcher
        if self.turn % 2 == 0:
            move = self.witcher.make_move(self.state)
            if isinstance(move, Movement):
                self.state = State(move.new_position, self.state.striga_position)
            elif isinstance(move, Attack):
                self.attacked_positions = move.attacked_positions
                for p in move.attacked_positions:
                    if p == self.state.striga_position:
                        self.striga_hp -= 1
                        self.state = State(self.state.witcher_position, self.board.castle_position)
                        if self.striga_hp <= 0:
                            self.game_res = GameResult.WITCHER
        # striga
        else:
            move = self.striga.make_move(self.state)
            if isinstance(move, Movement):
                self.state = State(self.state.witcher_position, move.new_position)
            elif isinstance(move, Attack):
                self.attacked_positions = move.attacked_positions
                for p in move.attacked_positions:
                    if p == self.state.witcher_position:
                        self.game_res = GameResult.STRIGA

        self.turn += 1
        if self.turn >= 1000:
            self.game_res = GameResult.STRIGA

    def visualize(self, turns=10):
        fig, ax = plt.subplots(figsize=(8, 8))
        done = False

        def update(i):
            nonlocal done
            if done:
                ax.set_title("Game over: {}".format(self.game_res), fontsize=20)
                ax.set_axis_off()
                return

            self.advance()

            im = self.board.numpy_repr()
            im[self.state.striga_position.y, self.state.striga_position.x] = striga_color
            im[self.state.witcher_position.y, self.state.witcher_position.x] = witcher_color
            for p in self.attacked_positions:
                im[p.y, p.x] = im[p.y, p.x] + attacked_color

            self.attacked_positions = []
            if self.game_res is not None:
                done = True

            ax.imshow(im)
            ax.set_title("Turn {}, striga_hp: {}".format(i, self.striga_hp), fontsize=20)
            ax.set_axis_off()

        global ani
        ani = animation.FuncAnimation(fig, update, frames=np.arange(0, turns), interval=50)
        plt.show()


def main():
    width = 7
    height = 7
    walls = [
        Position(width - 2, 0),
        Position(width - 2, 1),
        Position(width - 1, 1)
    ]
    castle_position = Position(width - 1, 0)
    board = Board(width, height, castle_position, walls)

    striga = Striga(StrigaDeterministicMovementScheme(board, 3))
    witcher = Witcher(WitcherMovementSchemeSARSA(board))

    initial_state = State(Position(0, 0), Position(3, 3))

    game = Game(board, initial_state, striga, witcher)

    game.visualize()


if __name__ == '__main__':
    main()
