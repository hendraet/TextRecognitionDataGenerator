import argparse
import itertools
import json
import random
from math import ceil
from pathlib import Path

from tqdm import tqdm


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('csv', type=Path)
    parser.add_argument('-s', '--suffix', type=str, default='', help='Suffix to add to resulting label file')
    parser.add_argument('-so', '--shuffle-off', action='store_true', default=False, help='Do not shuffle the samples')
    parser.add_argument('-f', '--replication-factor', type=float, default=1.0,
                        help='If set, will account for the replication factor and asserts that the same string is not '
                             'present in different splits')
    parser.add_argument('-rds', '--remove-duplicate-strings', action='store_true', default=False,
                        help='Create additional json for valid and testing that do not contain strings that are also '
                             'present in the training set')
    args = parser.parse_args()
    return args


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

    if args.replication_factor > 1.0:
        # Only works if the replicated datasets are concatenated and the samples are in the same order, i.e. if
        # GeneratorFromStringsCustom was used with the corresponding inflation factor
        orig_dataset_length = round(len(samples) / args.replication_factor)
        dataset_partitions = []
        i = 0
        while i < len(samples):
            dataset_partitions.append(samples[i:i + orig_dataset_length])
            i += orig_dataset_length

        # Had some help from: https://stackoverflow.com/a/40954220
        samples = [x for x in itertools.chain(*itertools.zip_longest(*dataset_partitions)) if x is not None]
        first_strings = [s['string'] for s in samples[:ceil(args.replication_factor)]]
        assert len(set(first_strings)) <= 1, 'Something went wrong :( (is your replication factor just slightly ' \
                                             'larger than the closest integer?)'
    elif not args.shuffle_off:
        random.shuffle(samples)
    out_dir = args.csv.parent
    suffix = f'_{args.suffix}' if len(args.suffix) > 0 else ''
    train_strings = set()
    for i, (name, split_factor) in tqdm(enumerate(zip(names, split_factors)), desc='Generating splits'):
        start = int(sum(split_factors[:i]) * len(samples))
        end = int(sum(split_factors[:i + 1]) * len(samples))
        samples_for_split = samples[start:end]

        if args.remove_duplicate_strings:
            if name == 'train':
                train_strings = set([s['string'] for s in samples_for_split])
            else:
                assert len(train_strings) > 0, 'Training samples were not created'
                duplicates = []
                clean_samples = []
                for s in samples_for_split:
                    if s['string'] in train_strings:
                        duplicates.append(s)
                    else:
                        clean_samples.append(s)
                print(f'Removed {len(duplicates)} duplicate samples from {name}')

                with open(out_dir / f'synth_lines{suffix}_{name}_dedup.json', 'w', encoding='utf8') as out_f:
                    json.dump(clean_samples, out_f, ensure_ascii=False, indent=2)

        with open(out_dir / f'synth_lines{suffix}_{name}.json', 'w', encoding='utf8') as out_f:
            json.dump(samples_for_split, out_f, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    main(get_args())
