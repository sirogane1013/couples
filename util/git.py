import sys

import git


def get_modified(commit: git.Commit):
    diffs = commit.parents[0].diff(commit)
    return [d.a_path for d in diffs if d.change_type == 'M']


def find_child(repo: git.Repo, hexsha: str) \
        -> git.Commit:
    c = repo.commit()
    while True:
        if len(c.parents) == 0:
            print("Commit not found: {}".format(hexsha))
            sys.exit(1)
        if c.parents[0].hexsha.startswith(hexsha):
            return c
        c = c.parents[0]
