import argparse
import json
import os
import pickle

import git
import numpy
import scipy
from tqdm import tqdm
from networkx.readwrite import json_graph

from increment import increment
from reader import read_input
from util.git import find_child


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
    parser.add_argument(
        "-d", "--destination", type=str, default="./data",
        help="Destination of output."
    )
    parser.add_argument(
        "-o", "--overwrite", action='store_true',
        help="Overwrite if data exists."
    )
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    print("reading input...")
    reader = read_input(args.couples)
    dest_prefix = args.destination
    index, coocc = reader.get_files_coocc()
    repo = git.Repo(args.repository)
    hexsha = args.hexsha
    commit = repo.commit(hexsha)
    for _ in tqdm(range(args.iteration)):
        path = dest_prefix + "/" + hexsha
        if args.overwrite or not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
            with open(path + "/index.pkl", mode='wb') as f:
                export_index(f, index)
            with open(path + "/matrix.npz", mode='wb') as f:
                export_matrix(f, coocc)
            index, coocc, hexsha = increment(repo, hexsha, index, coocc)
        else:
            with open(path + "/index.pkl", mode='rb') as f:
                index = pickle.load(f)
            with open(path + "/matrix.npz", mode='rb') as f:
                coocc = scipy.sparse.load_npz(f)
            commit = find_child(repo, hexsha)
            hexsha = commit.hexsha


def export_index(f, index):
    pickle.dump(index, f)


def export_matrix(f, matrix):
    scipy.sparse.save_npz(f, matrix)


def export_graph(f, graph):
    def support_int32_default(o):
        if isinstance(o, numpy.int32):
            return o.item()
        raise TypeError(repr(o) + " is not JSON serializable")

    g_json = json_graph.node_link_data(graph)
    json.dump(g_json, f, indent=2, default=support_int32_default)


if __name__ == '__main__':
    main()
