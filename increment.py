import sys
from typing import List

import git
from scipy.sparse import csr_matrix, coo_matrix


def increment(repo: git.Repo, origin_hex: str, index: List[str], coocc: csr_matrix) \
        -> (List[str], csr_matrix, str):
    diffs = None
    hexsha = ""
    for c in repo.iter_commits():
        if len(c.parents) == 0:
            print("Commit not found: {}".format(origin_hex))
            sys.exit(1)
        if c.parents[0].hexsha.startswith(origin_hex):
            diffs = c.parents[0].diff(c)
            hexsha = c.hexsha
            break

    added_files = []
    modified_files = []
    deleted_files = []
    renamed_files_a = []
    renamed_files_b = []
    for d in diffs:
        if d.change_type == 'A':
            added_files.append(d.a_path)
        elif d.change_type == 'M':
            modified_files.append(d.a_path)
        elif d.change_type == 'D':
            deleted_files.append(d.a_path)
        elif d.change_type == 'R':
            renamed_files_a.append(d.a_path)
            renamed_files_b.append(d.b_path)
    new_index = index + added_files
    new_index = list(filter(lambda x: x not in deleted_files, new_index))
    c = coo_matrix(coocc)
    row = []
    col = []
    data = []
    # modify
    for i, j, v in zip(c.row, c.col, c.data):
        if index[i] in deleted_files or index[j] in deleted_files:
            continue
        row.append(new_index.index(index[i]))
        col.append(new_index.index(index[j]))
        if (index[i] in modified_files or index[i] in renamed_files_a) and (
                index[j] in modified_files or index[j] in renamed_files_a):
            data.append(v + 1)
        else:
            data.append(v)
    # add
    for i, _ in enumerate(added_files):
        idx = len(index) - len(deleted_files) + i
        row.append(idx)
        col.append(idx)
        data.append(1)
        for f in set(modified_files) | set(renamed_files_a):
            row.append(new_index.index(f))
            col.append(idx)
            data.append(1)
            row.append(idx)
            col.append(new_index.index(f))
            data.append(1)
    # rename
    for ra, rb in zip(renamed_files_a, renamed_files_b):
        new_index[new_index.index(ra)] = rb

    incremented_coocc = csr_matrix((data, (row, col)),
                                   shape=[len(new_index), len(new_index)])
    r_index, r_coocc = sort_coocc(new_index, incremented_coocc)
    return r_index, r_coocc, hexsha


def sort_coocc(index: List[str], coocc: csr_matrix) \
        -> (List[str], csr_matrix):
    sorted_index = sorted(index)

    def convert_index(from_i):
        return sorted_index.index(index[from_i])

    c = coo_matrix(coocc)
    row = []
    col = []
    data = []
    for i, j, v in zip(c.row, c.col, c.data):
        row.append(convert_index(i))
        col.append(convert_index(j))
        data.append(v)
    sorted_coocc = csr_matrix((data, (row, col)), shape=[len(index), len(index)])

    return sorted_index, sorted_coocc
