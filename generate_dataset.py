import argparse
from pathlib import Path

from tqdm import tqdm

from trdg.generators import GeneratorFromWikipedia

import yaml


def main(args: argparse.Namespace):
    with open(args.dataset_config_path) as f:
        config = yaml.safe_load(f)

    dataset_dir = Path(config.pop('dataset_dir'))
    assert dataset_dir.exists(), f'Dataset directory {dataset_dir} does not exist!'
    label_path = dataset_dir / 'labels.txt'
    assert not label_path.exists(), f'Label file already exists!'
    (dataset_dir / 'images').mkdir(exist_ok=True)

    generator = GeneratorFromWikipedia(**config)
    for i, (image, label) in tqdm(enumerate(generator), desc='Saving samples'):
        sample_id = f"{{i:0{len(str(config['count']))}d}}".format(i=i)
        filename = f'images/{sample_id}.png'
        image.save(dataset_dir / filename)
        with open(label_path, 'a') as f:
            f.write(f'{filename} {label}\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dataset_config_path', type=Path, help='Path to yaml that has configuration')
    main(parser.parse_args())
