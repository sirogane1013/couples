import argparse
import json
import pickle

import git
import scipy
from tqdm import tqdm

from graph import Graph
from .leave_out import leave_one_out, TooSmallCommitException


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "repository", type=str,
        help="Path to target repository."
    )
    parser.add_argument(
        "data", type=str,
        help="Path to data directory."
    )
    parser.add_argument(
        "-h", "--hexsha", type=str, default="HEAD",
        help="Commit hash of the project where experiment starts."
    )
    parser.add_argument(
        "-i", "--iteration", type=int, default=10,
        help="Number of commits to perform the experiment."
    )
    parser.add_argument(
        "-o", "--output", type=str, default="result.json",
        help="File name of output json."
    )
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    repo = git.Repo(args.repository)
    target_com = repo.commit(args.hexsha)
    parent_com = target_com.parents[0]
    results = []
    C = 0
    Cstar = 0
    m = 0
    r = 0
    for _ in tqdm(range(args.iteration)):
        with open(args.data + "/" + target_com.hexsha + "/index.pkl", mode='rb') as f:
            index = pickle.load(f)
        with open(args.data + "/" + parent_com.hexsha + "/matrix.npz", mode='rb') as f:
            coocc = scipy.sparse.load_npz(f)
        g = Graph(index, coocc)
        try:
            hexsha, mrr, recall, feedback, detail = leave_one_out(target_com, g)
            results.append({
                "hash": hexsha,
                "mrr": mrr,
                "recall": recall,
                "feedback": feedback,
                "detail": detail,
            })
            m += mrr
            r += recall
            C += 1
            if feedback > 0:
                Cstar += 1
        except TooSmallCommitException:
            pass
        target_com = target_com.parents[0]
        parent_com = parent_com.parents[0]

    mrr_t = m / C
    recall_t = r / C
    result_t = {
        "mrr_total": mrr_t,
        "recall_total": recall_t,
        "used_commits": C,
        "results": results,
    }
    with open(args.output, "w") as f:
        json.dump(result_t, f)


def print_result(result):
    print(
        "MRR: {}\n"
        "Recall: {}\n"
        "Number of Used Commits: {}\n".format(result["mrr_total"], result["recall_total"], result["used_commits"])
    )


if __name__ == '__main__':
    main()
