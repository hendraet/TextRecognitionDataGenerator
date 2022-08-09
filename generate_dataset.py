import argparse
from pathlib import Path

import yaml
from tqdm import tqdm

from trdg.generators import GeneratorFromWikipedia
from trdg.generators.from_strings_custom import GeneratorFromStringsCustom


def main(args: argparse.Namespace):
    with open(args.dataset_config_path) as f:
        config = yaml.safe_load(f)

    dataset_dir = Path(config.pop('dataset_dir'))
    assert dataset_dir.exists(), f'Dataset directory {dataset_dir} does not exist!'
    label_path = dataset_dir / 'labels.txt'
    assert not label_path.exists(), f'Label file already exists!'
    (dataset_dir / 'images').mkdir(exist_ok=True)

    if args.generator_type == 'wikipedia':
        count = config['count']
        generator = GeneratorFromWikipedia(**config)
    elif args.generator_type == 'strings':
        string_file = Path(config.pop('string_file'))
        with string_file.open() as f:
            strings = tuple(line.strip() for line in f)
        count = len(strings)
        generator = GeneratorFromStringsCustom(strings=strings, **config)
    else:
        raise ValueError(f'Unknown generator type "{args.generator_type}"')

    for i, (image, label) in tqdm(enumerate(generator), desc='Saving samples'):
        sample_id = f"{{i:0{len(str(count))}d}}".format(i=i)
        filename = f'images/{sample_id}.png'
        image.save(dataset_dir / filename)
        with open(label_path, 'a') as f:
            f.write(f'{filename} {label}\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dataset_config_path', type=Path, help='Path to yaml that has configuration')
    parser.add_argument('-gt', '--generator_type', type=str, default='wikipedia', choices=['wikipedia', 'strings'],
                        help='Type of generator to use.')
    main(parser.parse_args())
