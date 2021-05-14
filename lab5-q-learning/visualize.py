import matplotlib.pyplot as plt
import matplotlib.animation as animation

from qtypes import Obstacle

plt.rcParams["image.cmap"] = "nipy_spectral"

witcher_color = .6
striga_color = .15
attacked_color = .1


def visualize(env, turns=1000):
    fig, ax = plt.subplots(figsize=(8, 8))
    done = False

    def update(i):
        print(i)
        nonlocal done
        if done:
            ax.set_title("Game over: {}".format(env.game_res), fontsize=20)
            ax.set_axis_off()
            return

        env.advance()
        im = env.board.numpy_repr()
        im[env.state.striga_position.y, env.state.striga_position.x] = striga_color
        im[env.state.witcher_position.y, env.state.witcher_position.x] = witcher_color
        for p in env.attacked_positions:
            if env.board[p] != Obstacle.WALL:
                im[p.y, p.x] = im[p.y, p.x] + attacked_color

        env.attacked_positions = []
        if env.game_res is not None:
            done = True

        ax.imshow(im)
        ax.set_title("Turn {}, striga_hp: {}".format(i, 3 - env.hits), fontsize=20)
        ax.set_axis_off()

    ani = animation.FuncAnimation(fig, update, frames=turns, interval=10)
    plt.show()

    return ani
