import argparse
import logging
import shutil
from pathlib import Path

from tqdm import tqdm


def move_image(img_path: Path, root_dir: Path, batch_size: int, num_batches: int) -> Path:
    image_id = int(img_path.stem)
    new_sub_dir_id = image_id // batch_size
    new_sub_dir_id = f"{{i:0{len(str(num_batches))}d}}".format(i=new_sub_dir_id)
    new_sub_dir = root_dir / str(new_sub_dir_id)
    new_sub_dir.mkdir(parents=True, exist_ok=True)
    new_img_path = new_sub_dir / img_path.name
    shutil.move(img_path, new_img_path)

    return new_img_path


def fix_sub_dir(sub_dir: Path, batch_size: int = 10000):
    label_file = sub_dir / 'labels.txt'
    assert label_file.exists()
    original_label_file = label_file.with_name('original_labels.txt')
    assert not original_label_file.exists()

    with label_file.open() as f:
        lines = f.readlines()

    new_samples = []
    num_batches = len(lines) // batch_size
    for line in tqdm(lines, desc='Processing samples'):
        img_path, label = line.strip().split(' ', 1)
        img_path = sub_dir / img_path
        if not img_path.exists():
            logging.warning(f'{img_path} does not exist.')
            continue

        new_image_path = move_image(img_path, sub_dir, batch_size, num_batches)
        relative_path = new_image_path.relative_to(sub_dir)
        new_samples.append((relative_path, label))

    shutil.move(label_file, original_label_file)
    with label_file.open('w') as f:
        for sample in new_samples:
            f.write(f'{sample[0]} {sample[1]}\n')

    return new_samples


def main(args: argparse.Namespace):
    label_filename = (args.dataset_dir / 'labels.txt')
    assert not label_filename.exists()

    all_samples = []
    for f in tqdm(args.dataset_dir.iterdir(), desc='Processing sub-directories'):
        if not f.is_dir() or args.filter not in f.name:
            continue
        sub_dir_samples = fix_sub_dir(f, batch_size=args.bsz)
        adpated_samples = [f'{Path(f.name) / s[0]} {s[1]}' for s in sub_dir_samples]
        all_samples.extend(adpated_samples)

    with label_filename.open('w') as f:
        f.write('\n'.join(all_samples))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dataset_dir', type=Path, help='Path to root of dataset')
    parser.add_argument('--bsz', type=int, help='How many samples the sub directories should contain', default=10000)
    parser.add_argument('--filter', type=str, help='Only process directories containing the substring', default='batch')
    main(parser.parse_args())
