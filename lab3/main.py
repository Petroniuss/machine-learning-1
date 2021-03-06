import string

import matplotlib.pyplot as plt

from PIL import Image
from sklearn.decomposition import PCA
import glob
import os
import numpy as np

kazar_dataset_dir = 'datasets/kazar'
img_normalized_size = (100, 100)


def convert_img_to_vector(img):
    return np.asarray(img).reshape((-1, 1)) / 255.0


def convert_img_vector_to_img(img_vector):
    M = img_vector.reshape(img_normalized_size) * 255.0

    return Image.fromarray(M)


def load_dataset(dataset_dir):
    """
        assumes '${class_name}_.*'
    """
    dataset = []
    for path in glob.glob(f'{dataset_dir}/*'):
        img = Image.open(path)
        file_name = os.path.basename(path)
        class_name = file_name.partition('_')[0]

        dataset.append((class_name, img))
    return dataset


def normalize_dataset(dataset: list[string, Image]):
    """
        :return labels - list of strings,
                X      - images in matrix, each column is an image
    """
    labels, normalized_data = [], []
    for class_name, img in dataset:
        resized_img = img.resize(img_normalized_size)
        normalized_img = resized_img.convert('L')
        img_vector = convert_img_to_vector(normalized_img)

        labels.append(class_name)
        normalized_data.append(img_vector)

    return np.array(labels), np.hstack(normalized_data)


def show_dataset(y, X):
    fig, axes = plt.subplots(3, 8, figsize=(8, 4),
                             subplot_kw={'xticks': [], 'yticks': []},
                             gridspec_kw=dict(hspace=0.25, wspace=0.05))
    fig.suptitle('Dataset')

    for i, ax in enumerate(axes.flat):
        v = X[:, i]
        img = convert_img_vector_to_img(v)
        ax.imshow(img, interpolation='nearest')
        ax.set_xlabel(y[i])

    plt.show()


### -------------------- PCA -----------------------


def mean_img_show(X):
    mean = np.mean(X, axis=1)
    mean_img = convert_img_vector_to_img(mean)

    plt.imshow(mean_img.resize((480, 480)))
    plt.show()


def principal_components_show(X):
    pca = PCA().fit(X.T)

    # plot explained variance
    plt.plot(np.cumsum(pca.explained_variance_ratio_))
    plt.xlabel('number of components')
    plt.ylabel('explained variance');
    plt.show()

    fig, axes = plt.subplots(3, 8, figsize=(8, 4),
                             subplot_kw={'xticks': [], 'yticks': []},
                             gridspec_kw=dict(hspace=0.25, wspace=0.05))
    fig.suptitle('Principal Components in Feature Space')

    for i, ax in enumerate(axes.flat):
        var = pca.explained_variance_ratio_[i] * 100
        comp = pca.components_[i]

        img = convert_img_vector_to_img(comp / np.max(comp))
        ax.imshow(img, interpolation='nearest')

        ax.set_xlabel(f'{var:.2f}%')

    plt.show()


def pca_dimensionality_reduction_show(y, X, n_dims=[16, 4], n_samples=8):
    imgs = []
    for i in range(n_samples):
        v = X[:, i]
        img = convert_img_vector_to_img(v)
        imgs.append(img)

    for dims in n_dims:
        pca = PCA(n_components=dims).fit(X.T)
        projected = pca.inverse_transform(pca.transform(X.T)).T
        for i in range(n_samples):
            v = projected[:, i]
            img = convert_img_vector_to_img(v)
            imgs.append(img)

    fig, axes = plt.subplots(3, n_samples, figsize=(8, 4),
                             subplot_kw={'xticks': [], 'yticks': []},
                             gridspec_kw=dict(hspace=0.25, wspace=0.05))
    fig.suptitle('Dimensionality reduction using PCA')

    ys = ['Input data'] + list(map(lambda x: f'{x} features', n_dims))

    for i, ax in enumerate(axes.flat):
        if i % n_samples == 0:
            ax.set_ylabel(ys[i // n_samples])
        ax.imshow(imgs[i], interpolation='nearest')
        ax.set_xlabel(y[i % n_samples])

    plt.show()


def pca_2d(y, X):
    pca = PCA(2)
    projected = pca.fit_transform(X.T)

    for class_name in set(y):
        xs, ys = [], []
        for i in range(len(y)):
            if y[i] == class_name:
                xs.append(projected[i, 0])
                ys.append(projected[i, 1])

        plt.scatter(xs, ys, label=class_name)

    plt.xlabel('Component 1')
    plt.ylabel('Component 2')
    plt.title('Dimensionality reduction to 2D')
    plt.legend()
    plt.show()


def main():
    ds = load_dataset(kazar_dataset_dir)
    y, X = normalize_dataset(ds)

    show_dataset(y, X)
    mean_img_show(X)
    principal_components_show(X)

    pca_dimensionality_reduction_show(y, X)
    pca_2d(y, X)


if __name__ == '__main__':
    main()
