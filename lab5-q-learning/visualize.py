import matplotlib.pyplot as plt
import matplotlib.animation as animation
from scipy.ndimage.filters import uniform_filter1d

from qtypes import Obstacle

plt.style.use('seaborn')
plt.rcParams["image.cmap"] = "rainbow"

witcher_color = .3
striga_color = .7
attacked_color = .5


def visualize(env, turns=100):
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
        im = env.board.numpy_repr(.2)
        im[env.state.striga_position.y, env.state.striga_position.x] = striga_color
        im[env.state.witcher_position.y, env.state.witcher_position.x] = witcher_color
        for p in env.attacked_positions:
            if env.board[p] != Obstacle.WALL:
                im[p.y, p.x] = min(im[p.y, p.x] + attacked_color, striga_color)

        env.attacked_positions = []
        if env.game_res is not None:
            done = True

        ax.imshow(im)
        ax.set_title("Turn {}, striga_hp: {}".format(i, 3 - env.hits), fontsize=20)
        ax.set_axis_off()

    ani = animation.FuncAnimation(fig, update, frames=turns, interval=10)
    plt.show()

    return ani


def show_training_results(hits, wins, lifetime, rewards, time):
    fig, ax = plt.subplots(2, 2, figsize=(14, 8))
    fig.tight_layout(pad=3.0)

    n = len(time) // 10
    hits = uniform_filter1d(hits, size=n)
    ax[0, 0].plot(time, hits, 'r')  # row=0, col=0
    ax[0, 0].set_title('Hits')

    ax[1, 0].plot(time, wins, 'b')  # row=1, col=0
    ax[1, 0].set_title('Win probability')

    lifetime = uniform_filter1d(lifetime, size=n)
    ax[0, 1].plot(time, lifetime, 'g')  # row=0, col=1
    ax[0, 1].set_title('Lifetime')

    rewards = uniform_filter1d(rewards, size=n)
    ax[1, 1].plot(time, rewards, 'k')  # row=1, col=1
    ax[1, 1].set_title('Rewards')

    plt.show()
