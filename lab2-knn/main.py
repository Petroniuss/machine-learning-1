import numpy as np
import matplotlib
import matplotlib.pyplot as plt

from sklearn.datasets import make_moons, make_blobs

matplotlib.rcParams['contour.negative_linestyle'] = 'solid'

# Example settings
n_samples = 1000
n_dims = 2
n_classes = 3
island_fraction = 0.2
n_island_samples = int(island_fraction * n_samples)
blobs_params = dict(n_samples=n_samples, n_features=n_dims, random_state=0)


def data():
    # blue
    x_1 = make_blobs(centers=[[-.5, -.6], [-1, -1]], cluster_std=[.2, .2],
                     **blobs_params)[0]

    x_2 = make_blobs(centers=[[.1, -.5]], cluster_std=[.10],
                     n_samples=n_island_samples, n_features=n_dims, random_state=0)[0]

    x = np.concatenate((x_1, x_2), axis=0)

    # orange
    y = make_blobs(centers=[[-1.4, -1.0], [-1.8, -1.2]], cluster_std=[.2, .15],
                   **blobs_params)[0]

    # green
    z = make_blobs(centers=[[-.9, -.5], [-.2, -.3]], cluster_std=[.2, .2],
                   **blobs_params)[0]

    datasets = [x, y, z]
    colors = ['#4EACC5', '#FF9C34', '#4E9A06']
    plt.figure(1)

    for x, color in zip(datasets, colors):
        plt.scatter(x[:, 0], x[:, 1],
                    c=color, marker='.', s=10)

    plt.title("Data for KNN")
    plt.show()


def main():
    data()


if __name__ == '__main__':
    main()
