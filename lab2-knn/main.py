import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

from sklearn.datasets import make_blobs
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler

matplotlib.rcParams['contour.negative_linestyle'] = 'solid'

# Example settings
n_samples = 1000
n_dims = 2
n_classes = 3
island_fraction = 0.2
mesh_step_size = .2
n_island_samples = int(island_fraction * n_samples)
blobs_params = dict(n_samples=n_samples, n_features=n_dims, random_state=0)
names = [
    'KNN with k = 1 and euclidean metric',
    'KNN with k = 13 and euclidean metric',
    'KNN with k = 1 and mahalanobis metric',
    'KNN with k = 9, euclidean metric and voting by weighting points',
]
classifiers = []

# Create color maps
space_colors = ['orange', 'coral', 'lightgreen']
cls_colors = ['darkorange', 'crimson', 'green']

cmap_space = ListedColormap(space_colors)
cmap_cls = ListedColormap(cls_colors)


def init_classifiers(X):
    classifiers.extend([
        KNeighborsClassifier(n_neighbors=1),
        KNeighborsClassifier(n_neighbors=13),
        KNeighborsClassifier(n_neighbors=1, metric='mahalanobis', metric_params={'V': np.cov(X.T)}),
        KNeighborsClassifier(n_neighbors=9, weights='distance')])


def init_data():
    # red
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
    plt.figure(1)

    for x, color in zip(datasets, cls_colors):
        plt.scatter(x[:, 0], x[:, 1],
                    c=color, marker='.', s=10)

    plt.title("Data for KNN")
    plt.show()

    X = np.concatenate(datasets, axis=0)
    cls_labels = [np.full(cls.shape[0], class_idx) for class_idx, cls in enumerate(datasets)]
    cls_labels = np.concatenate(cls_labels, axis=0)

    return X, cls_labels


def visualize_space(X, y):
    plt.figure(figsize=(27, 9))
    X = StandardScaler().fit_transform(X)
    x_min, x_max = X[:, 0].min() - .5, X[:, 0].max() + .5
    y_min, y_max = X[:, 1].min() - .5, X[:, 1].max() + .5
    xx, yy = np.meshgrid(np.arange(x_min, x_max, mesh_step_size),
                         np.arange(y_min, y_max, mesh_step_size))

    i = 1
    ax = plt.subplot(1, len(classifiers) + 1, i)
    ax.set_title("Data")
    ax.scatter(X[:, 0], X[:, 1], c=y, cmap=cmap_cls,
               edgecolors='k', alpha=.5)
    ax.set_xlim(xx.min(), xx.max())
    ax.set_ylim(yy.min(), yy.max())
    ax.set_xticks(())
    ax.set_yticks(())

    i += 1

    for name, clf in zip(names, classifiers):
        ax = plt.subplot(1, len(classifiers) + 1, i)
        clf.fit(X, y)
        score = clf.score(X, y)
        Z = clf.predict(np.c_[xx.ravel(), yy.ravel()])

        Z = Z.reshape(xx.shape)
        ax.contourf(xx, yy, Z, cmap=cmap_space)

        ax.scatter(X[:, 0], X[:, 1], c=y, cmap=cmap_cls,
                   edgecolors='k', alpha=.2)

        ax.set_xlim(xx.min(), xx.max())
        ax.set_ylim(yy.min(), yy.max())
        ax.set_xticks(())
        ax.set_yticks(())
        ax.set_title(name)
        ax.text(xx.max() - .3, yy.min() + .3, ('%.2f' % score).lstrip('0'),
                size=15, horizontalalignment='right')
        i += 1

    plt.tight_layout()
    plt.show()


def main():
    X, y = init_data()
    init_classifiers(X)
    visualize_space(X, y)


if __name__ == '__main__':
    main()
