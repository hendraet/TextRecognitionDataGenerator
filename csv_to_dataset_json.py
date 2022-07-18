import argparse
import json
import random
from pathlib import Path

from tqdm import tqdm


def main(args: argparse.Namespace):
    with open(args.csv) as f:
        lines = f.readlines()

    samples = []
    for line in tqdm(lines, desc='Processing label file'):
        path, label = line.strip().split(' ', 1)
        samples.append({'string': label, 'path': path})

    split_factors = [0.8, 0.1, 0.1]
    assert sum(split_factors) == 1, 'Split factors must sum to 1'
    names = ['train', 'valid', 'test']

    random.shuffle(samples)
    out_dir = args.csv.parent
    suffix = f'_{args.suffix}' if len(args.suffix) > 0 else ''
    for i, (name, split_factor) in tqdm(enumerate(zip(names, split_factors)), desc='Generating splits'):
        start = int(sum(split_factors[:i]) * len(samples))
        end = int(sum(split_factors[:i + 1]) * len(samples))
        with open(out_dir / f'synth_lines{suffix}_{name}.json', 'w') as out_f:
            json.dump(samples[start:end], out_f)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('csv', type=Path)
    parser.add_argument('-s', '--suffix', type=str, default='', help='Suffix to add to resulting label file')
    main(parser.parse_args())
