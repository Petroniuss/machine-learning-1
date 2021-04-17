import string

from PIL import Image
from sklearn.decomposition import PCA
import glob
import os
import numpy as np

kazar_dataset_dir = 'datasets/kazar'
img_normalized_size = (120, 120)


# todo we could also crop images from kazar dataset

def convert_img_to_vector(img):
    return np.asarray(img).reshape((-1, 1))


def convert_img_vector_to_img(img_vector):
    M = img_vector.reshape(img_normalized_size)

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


### -------------------- PCA -----------------------
def mean_image(X):
    mean = np.mean(X, axis=1)
    return convert_img_vector_to_img(mean)


def main():
    ds = load_dataset(kazar_dataset_dir)
    y, X = normalize_dataset(ds)
    print(y, X.shape)

    mean_image(X).show()


if __name__ == '__main__':
    main()
