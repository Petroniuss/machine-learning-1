from board import Board
from qtypes import *

import matplotlib

import matplotlib.pyplot as plt
import matplotlib.animation as animation

matplotlib.rcParams["backend"] = "TkAgg"
plt.rcParams["image.cmap"] = "nipy_spectral"


ani = None

witcher_color = .6
striga_color = .15
attacked_color = .1


class Game:
    def __init__(self, board: Board,
                 initial_state: QState,
                 striga: Striga, witcher: Witcher):
        self.board = board
        self.striga = striga
        self.witcher = witcher
        self.state = initial_state

        self.attacked_positions = []
        self.hits = 3
        self.turn = 0
        self.game_res = None
        self.witcher_positions = self.board.to_numpy()

    def advance(self):
        # witcher's turn
        if self.turn % 2 == 0:
            action = self.witcher.next_action(self.state)
            if isinstance(action, Movement):
                new_position = action.new_position
                self.state = QState(new_position, self.state.striga_position)
                self.witcher_positions[new_position.y, new_position.x] += 1

            elif isinstance(action, HalfTurnAttack):
                self.attacked_positions = list(self.board.positions_around(self.state.witcher_position))
                if self.board.is_attacked(self.state.striga_position, self.attacked_positions):
                    self.hits += 1
                    self.state = QState(self.state.witcher_position, self.board.castle_position)
                    if self.hits >= 3:
                        self.game_res = GameResult.WITCHER
        # striga's turn
        else:
            action = self.striga.next_action(self.state)
            if isinstance(action, Movement):
                self.state = QState(self.state.witcher_position, action.new_position)
            elif isinstance(action, Attack):
                self.attacked_positions = action.attacked_positions
                if self.board.is_attacked(self.state.witcher_position, self.attacked_positions):
                    self.game_res = GameResult.STRIGA

        self.turn += 1
        if self.turn >= 1000:
            self.game_res = GameResult.STRIGA

    def visualize(self, turns=100):
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
            ax.set_title("Turn {}, striga_hp: {}".format(i, self.hits), fontsize=20)
            ax.set_axis_off()

        global ani
        ani = animation.FuncAnimation(fig, update, frames=turns, interval=10)
        plt.show()
