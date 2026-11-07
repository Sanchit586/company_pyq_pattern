"""Losslessly compress completed search checkpoints when local storage is scarce."""
import gzip
import os
from pathlib import Path

from record_combination_search import DIRECTORY


def main():
    directory = (DIRECTORY / 'raw').resolve()
    saved = count = 0
    for path in sorted(directory.glob('*.jsonl')):
        if path.resolve().parent != directory:
            raise ValueError('Checkpoint escaped the intended directory')
        original = path.read_bytes()
        packed = gzip.compress(original, compresslevel=9, mtime=0)
        target = path.with_suffix('.jsonl.gz')
        temporary = target.with_suffix('.gz.tmp')
        temporary.write_bytes(packed)
        if gzip.decompress(temporary.read_bytes()) != original or path.read_bytes() != original:
            raise ValueError('Checkpoint verification failed; original retained')
        os.replace(temporary, target)
        path.unlink()
        saved += len(original) - len(packed)
        count += 1
    print(f'Losslessly compressed {count} checkpoints; saved {saved:,} bytes.')


if __name__ == '__main__':
    main()
