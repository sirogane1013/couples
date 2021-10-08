import sys
from typing import List

import git
from scipy.sparse import csr_matrix, coo_matrix


def increment(repo: git.Repo, origin_hex: str, index: List[str], coocc: csr_matrix) \
        -> (List[str], csr_matrix, str):
    child = get_child(repo, origin_hex)
    diffs = child.parents[0].diff(child)
    hexsha = child.hexsha

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
    new_index = [e for e in new_index if e not in deleted_files]
    c = coo_matrix(coocc)
    row = [new_index.index(index[e]) for i, e in enumerate(c.row) if
           not (index[c.row[i]] in deleted_files or index[c.col[i]] in deleted_files)]
    col = [new_index.index(index[e]) for i, e in enumerate(c.col) if
           not (index[c.row[i]] in deleted_files or index[c.col[i]] in deleted_files)]
    data = [e for i, e in enumerate(c.data) if
            not (index[c.row[i]] in deleted_files or index[c.col[i]] in deleted_files)]
    # modify
    # duplicate indices are implicitly summed
    # https://docs.scipy.org/doc/scipy/reference/generated/scipy.sparse.coo_matrix.html
    for one in set(modified_files) | set(renamed_files_a):
        for other in set(modified_files) | set(renamed_files_a):
            row.append(new_index.index(one))
            col.append(new_index.index(other))
            data.append(1)
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


def get_child(repo: git.Repo, hexsha: str) \
        -> git.Commit:
    c = repo.commit()
    while True:
        if len(c.parents) == 0:
            print("Commit not found: {}".format(hexsha))
            sys.exit(1)
        if c.parents[0].hexsha.startswith(hexsha):
            return c
        c = c.parents[0]


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
