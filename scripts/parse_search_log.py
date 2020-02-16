import os
import re

import csv
from typing import Tuple, List


def parse_logs(log_content) -> Tuple[List[str], List[List]]:
    """returns the headers and rows for CSV output"""
    rows = []

    seed, stats = None, None
    stats_keys = ['SAVED', 'NOT OK', 'DUP', 'DUP_S', 'BLCKLST']

    for line in log_content.split(os.linesep):

        if 'Searching seed' in line:
            if seed is not None:
                rows.append(seed + stats)
            stats = [0 for _ in stats_keys]
            seed = [
                re.search("seed='([^']+)", line).group(1),
                re.search("query='([^']+)", line).group(1)
            ]
        elif seed is not None:
            for i, k in enumerate(stats_keys):
                if f'{k}:' in line:
                    stats[i] += 1
                    break
    # get the last seed as well
    if seed is not None: rows.append(seed + stats)

    return ['seed', 'query'] + stats_keys, rows


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', type=argparse.FileType('r'), required=True)
    parser.add_argument('-o', type=argparse.FileType('w'), default='-')
    args = parser.parse_args()

    headers, stats = parse_logs(args.i.read())
    w = csv.writer(args.o)
    w.writerow(headers)
    w.writerows(stats)
