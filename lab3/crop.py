from PIL import Image

import glob

kazar_dataset_dir = 'datasets/kazar'

crop_boundaries = (0, 200, 400, 480)


def crop_images(dataset_dir):
    """
        assumes '${class_name}_.*'
    """
    for path in glob.glob(f'{dataset_dir}/*'):
        img = Image.open(path)
        img.crop(crop_boundaries)
        img.save(path)


if __name__ == '__main__':
    crop_images(kazar_dataset_dir)
