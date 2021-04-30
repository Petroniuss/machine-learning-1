import collections
import random

import sklearn
from sklearn import preprocessing
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from tabulate import tabulate

menu_dataset_dir = 'datasets/menu.csv'


def load_dataset(dataset_dir):
    def serving_size_to_numeric(value):
        oz_value, _, _ = str(value).partition(' ')
        return float(oz_value)

    # labels by category
    df = pd.read_csv(dataset_dir)
    print(tabulate(df.head(), headers='keys', tablefmt='psql'))

    mapper = {}
    labels = []
    categories = []
    for i, category in enumerate(set(df['Category'])):
        mapper[category] = i
        categories.append(category)

    for category in df['Category']:
        labels.append(mapper[category])

    df.pop('Category')
    df.pop('Item')
    df.pop('Total Fat (% Daily Value)')
    df.pop('Saturated Fat (% Daily Value)')
    df.pop('Cholesterol (% Daily Value)')
    df.pop('Sodium (% Daily Value)')
    df.pop('Carbohydrates (% Daily Value)')
    df.pop('Dietary Fiber (% Daily Value)')

    df['Serving Size'] = df['Serving Size'].apply(serving_size_to_numeric)

    ## dividing by serving size
    # colsToDivide = list(df.columns.values)
    # colsToDivide.remove('Serving Size')
    # df.loc[:, colsToDivide] = df.loc[:, colsToDivide].div(df['Serving Size'], axis=0)

    # for now we can map all columns to float within 0.0 - 1.0
    values = df.values
    min_max_scaler = preprocessing.MinMaxScaler()
    x_scaled = min_max_scaler.fit_transform(values)
    df = pd.DataFrame(x_scaled, columns=df.columns)
    print(tabulate(df.head(), headers='keys', tablefmt='psql'))

    return df, np.array(labels), categories


def train_kmeans(X, init):
    kmeans = KMeans(n_clusters=5, n_init=1, max_iter=1, init=init)

    state = None
    i = 0
    ys = []
    while True:
        kmeans.fit(X)

        labels = kmeans.labels_
        centroids = kmeans.cluster_centers_

        if np.array_equal(state, labels):
            break

        kmeans.init = centroids
        state = labels

        inertia = kmeans.inertia_
        score = sklearn.metrics.davies_bouldin_score(X, labels)
        i += 1

        ys.append(score)
        print(i, inertia, score)

    print('-' * 100, end='\n\n')

    return ys


def train_kmeans_plus_plus(X):
    return train_kmeans(X, 'k-means++')


def train_kmeans_random(X):
    return train_kmeans(X, 'random')


def train_kmeans_sample(X):
    init = np.random.uniform(0.0, 1.0, (5, X.shape[1]))
    return train_kmeans(X, init)


def plot_kmeans_iterations(X, n_iters=50):
    algorithms = [
        train_kmeans_plus_plus,
        train_kmeans_random,
        train_kmeans_sample,
    ]
    results = [[] for _ in range(3)]
    names = ['k-means++', 'random', 'uniform']

    max_iterations = 0
    for i, algorithm in enumerate(algorithms):
        for _ in range(n_iters):
            ys = algorithm(X)
            results[i].append(ys)

            max_iterations = max(len(ys), max_iterations)

    # make sure that all arrays have the same size
    xs = list(range(1, max_iterations + 1))
    for i in range(3):
        for j in range(n_iters):
            last = results[i][j][-1]
            while len(results[i][j]) < max_iterations:
                results[i][j].append(last)

    # calculate mean and std
    means = [None for _ in range(3)]
    stds = [None for _ in range(3)]
    for i in range(3):
        values = np.array(results[i])
        means[i] = np.mean(values, axis=0)
        stds[i] = np.std(values, axis=0)

    # finally plot!
    for algorithm_name, mean, std in zip(names, means, stds):
        plt.errorbar(xs, mean, std, label=algorithm_name, capsize=3, marker='o')

    plt.xlabel('Number of iterations', fontsize=18)
    plt.ylabel('Davies-Bouldin Score', fontsize=18)
    plt.legend()
    plt.show()


# results make me wonder - I probably should've done better job
# at preparing the initial data since it appears that there isn't any global minimum
def plot_k_means_for_various_k(X, k_min=3, k_max=25, n_iters=10):
    ks = list(range(k_min, k_max + 1))
    means, stds = [], []
    for k in ks:
        results = []
        for _ in range(n_iters):
            kmeans = KMeans(n_clusters=k, init='k-means++')
            kmeans.fit(X)

            labels = kmeans.labels_
            score = sklearn.metrics.davies_bouldin_score(X, labels)
            results.append(score)

        means.append(np.mean(results))
        stds.append(np.std(results))

    plt.errorbar(ks, means, stds, label='k-means++', capsize=3, marker='o')

    plt.xlabel('K', fontsize=18)
    plt.ylabel('Davies-Bouldin Score', fontsize=18)
    plt.legend()
    plt.show()


def plot_pca_2d(X, labels, k, centers=False):
    projected = PCA(2).fit_transform(X)
    c = list(range(k))

    cs = []
    for i in range(X.shape[0]):
        cs.append(c[labels[i]])

    if centers:
        plt.scatter(projected[:, 0], projected[:, 1], label=labels, marker='D', c=cs, s=60, cmap='rainbow')
    else:
        plt.scatter(projected[:, 0], projected[:, 1], label=labels, c=cs, cmap='rainbow')


def plot_k_means_clusters(df, k=6, init='k-means++'):
    X = df.values
    kmeans = KMeans(n_clusters=k, init=init)
    kmeans.fit(X)

    labels = kmeans.labels_
    centers = kmeans.cluster_centers_
    counter = collections.Counter(labels)
    df = pd.DataFrame(centers, columns=df.columns)

    # todo characterize results
    print('Elements in clusters')
    for key, value in sorted(counter.items()):
        print(f'{key}: {value}')

    print(tabulate(df.head(), headers='keys', tablefmt='psql'))

    plot_pca_2d(X, labels, k)
    plot_pca_2d(centers, np.array(range(k)), k, centers=True)
    plt.xlabel('Component X', fontsize=18)
    plt.ylabel('Component Y', fontsize=18)
    plt.title('By Clusters', fontsize=22)
    plt.show()


def plot_categories(X, k, category_labels):
    plot_pca_2d(X, category_labels, k)
    plt.xlabel('Component X', fontsize=18)
    plt.ylabel('Component Y', fontsize=18)
    plt.title('By Categories', fontsize=22)
    plt.show()


def main():
    # 3, 121
    random.seed(3)
    df, category_labels, category_names = load_dataset(menu_dataset_dir)
    X = df.values

    plot_kmeans_iterations(X)
    plot_k_means_for_various_k(X)
    plot_k_means_clusters(df, k=6)
    plot_categories(X, len(category_names), category_labels)


if __name__ == '__main__':
    main()
