import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

from sklearn.datasets import make_blobs
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler

matplotlib.rcParams['contour.negative_linestyle'] = 'solid'

n_samples = 1000
n_dims = 2
n_classes = 3
island_fraction = 0.2
mesh_step_size = .02
n_island_samples = int(island_fraction * n_samples)
blobs_params = dict(n_samples=n_samples, n_features=n_dims, random_state=0)

names = [
    'KNN with k = 1 and euclidean metric',
    'KNN with k = 13 and euclidean metric',
    'KNN with k = 1 and mahalanobis metric',
    'KNN with k = 9, euclidean metric and voting with weighted points',
]

chosen_classifiers = [
    'Euclidean metric',
    'Mahalanobis metric',
    'Euclidean, weighted'
]

space_colors = ['orange', 'coral', 'lightgreen']
cls_colors = ['darkorange', 'crimson', 'green']

cmap_space = ListedColormap(space_colors)
cmap_cls = ListedColormap(cls_colors)


def init_classifiers(X):
    return [
        KNeighborsClassifier(n_neighbors=1),
        KNeighborsClassifier(n_neighbors=13),
        KNeighborsClassifier(n_neighbors=1, metric='mahalanobis', metric_params={'V': np.cov(X.T)}),
        KNeighborsClassifier(n_neighbors=9, weights='distance')]


def init_classifier_con_with_name(X, clf_name):
    if clf_name == chosen_classifiers[0]:
        return lambda k: KNeighborsClassifier(n_neighbors=k)
    elif clf_name == chosen_classifiers[1]:
        return lambda k: KNeighborsClassifier(n_neighbors=k, metric='mahalanobis', metric_params={'V': np.cov(X.T)})
    else:
        return lambda k: KNeighborsClassifier(n_neighbors=k, weights='distance')


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
    """
        Part 1.
    """
    classifiers = init_classifiers(X)
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

    def set_lims():
        ax.set_xlim(xx.min(), xx.max())
        ax.set_ylim(yy.min(), yy.max())
        ax.set_xticks(())
        ax.set_yticks(())

    set_lims()
    i += 1

    for name, clf in zip(names, classifiers):
        ax = plt.subplot(1, len(classifiers) + 1, i)
        clf.fit(X, y)
        Z = clf.predict(np.c_[xx.ravel(), yy.ravel()])
        Z = Z.reshape(xx.shape)

        ax.pcolormesh(xx, yy, Z, cmap=cmap_space, shading='auto')
        ax.scatter(X[:, 0], X[:, 1], c=y, cmap=cmap_cls,
                   edgecolors='k', alpha=.2)

        ax.set_title(name)
        set_lims()
        i += 1

    plt.tight_layout()
    plt.show()


def evaluate_k(X, y, clf, repeats=5):
    def eval_single():
        X_train, X_test, y_train, y_test = \
            train_test_split(X, y, test_size=.2)

        clf.fit(X_train, y_train)
        score = clf.score(X_test, y_test)
        return score

    scores = [eval_single() for _ in range(repeats)]

    return np.mean(scores), np.std(scores)


def pick_best_k(X_train, y_train, clf_con):
    scores = [evaluate_k(X_train, y_train, clf_con(k)) for k in range(1, 21)]

    errors = [(1 - x[0]) * 100 for x in scores]

    return np.argmax(list(map(lambda x: x[0], scores))) + 1, errors


def unzip(lst):
    return [list(tpl) for tpl in zip(*lst)]


def eval_classifier(X, y, clf_name, repeats=5):
    print('-' * 24 + f' {clf_name} ' + '-' * 24)

    def eval_single():
        clf_con = init_classifier_con_with_name(X, clf_name)
        X_train, X_test, y_train, y_test = \
            train_test_split(X, y, test_size=.2)
        k, errs = pick_best_k(X_train, y_train, clf_con)
        print(k)

        clf = clf_con(k)
        clf.fit(X_train, y_train)
        score = clf.score(X_test, y_test)

        return score, errs

    scores, errors = unzip([eval_single() for _ in range(repeats)])

    errors = np.vstack([err for err in errors])
    mean_error = np.mean(errors, axis=0)

    return np.mean(scores), np.std(scores), mean_error


def evaluate_classifiers(X, y):
    """
        Exercise 2.
    """
    mns, stds = [], []
    # plot errors with respect to k
    plt.figure(figsize=(12, 6))
    for i, clf_name in enumerate(chosen_classifiers):
        mn, std, mean_error = eval_classifier(X, y, clf_name)
        mns.append(mn * 100)
        stds.append(std * 100)

        plt.plot(np.arange(1, 21), mean_error, color=cls_colors[i], linestyle='dashed', marker='o',
                 markerfacecolor=space_colors[i], markersize=10, label=clf_name)

    plt.title('Error Rate K Value')
    plt.xlabel('K Value')
    plt.ylabel('Mean Error [%]')
    plt.legend(loc="upper right")
    plt.show()

    # plot accuracy
    inds = np.arange(len(chosen_classifiers))
    fig, ax = plt.subplots()
    bar = ax.bar(inds, mns, .35, yerr=stds)
    ax.axhline(0, color='grey', linewidth=0.8)
    ax.set_ylabel('Mean accuracy [%]')
    ax.set_xticks(inds)
    ax.set_xticklabels(chosen_classifiers)
    ax.bar_label(bar, label_type='center')
    ax.bar_label(bar, labels=['±%.2f' % e for e in stds],
                 padding=8, color='b', fontsize=14)

    plt.show()


# plot a couple of things!

def main():
    X, y = init_data()
    visualize_space(X, y)
    evaluate_classifiers(X, y)


if __name__ == '__main__':
    main()
