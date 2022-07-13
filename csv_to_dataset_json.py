import argparse
import json
from pathlib import Path


def main(args: argparse.Namespace):
    with open(args.csv) as f:
        lines = f.readlines()

    samples = []
    for line in lines:
        path, label = line.strip().split(' ', 1)
        samples.append({'string': label, 'path': path})

    split_factors = [0.7, 0.1, 0.2]
    names = ['train', 'valid', 'test']

    out_dir = args.csv.parent
    for i, (name, split_factor) in enumerate(zip(names, split_factors)):
        start = int(sum(split_factors[:i]) * len(samples))
        end = int(sum(split_factors[:i + 1]) * len(samples))
        with open(out_dir / f'synth_lines_{name}.json', 'w') as out_f:
            json.dump(samples[start:end], out_f)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('csv', type=Path)
    main(parser.parse_args())
