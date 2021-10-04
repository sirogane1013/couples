import argparse

import git
from tqdm import tqdm

from graph import Graph
from increment import increment
from reader import read_input


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "repository", type=str,
        help="Path to target repository."
    )
    parser.add_argument(
        "couples", type=str,
        help="Path to hercules output (couples.yaml)."
    )
    parser.add_argument(
        "hexsha", type=str,
        help="Commit hash of the project when couples.yaml was generated."
    )
    parser.add_argument(
        "-i", "--iteration", type=int, default=10,
        help="Number of commits to perform the experiment."
    )
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    print("reading input...")
    reader = read_input(args.couples)
    index, coocc = reader.get_files_coocc()
    repo = git.Repo(args.repository)
    hexsha = args.hexsha
    for _ in tqdm(range(args.iteration)):
        graph = Graph(index, coocc)
        index, coocc, hexsha = increment(repo, hexsha, index, coocc)


if __name__ == '__main__':
    main()
