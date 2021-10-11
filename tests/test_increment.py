import unittest
from typing import List

import git
from scipy.sparse import csr_matrix

from increment import increment, sort_coocc


class IncrementTest(unittest.TestCase):
    def setUp(self):
        super().setUp()

    def test_increment(self):
        repo: git.Repo = git.Repo("./resource/repo4test")
        hexsha: str = "0a48a702ed292db1ad7ef878fc8dfbbe6c113639"
        index: List[str] = ["fileA", "fileB"]
        matrix: csr_matrix = csr_matrix([
            [1, 1],
            [1, 1],
        ])
        index, matrix, hexsha = \
            self.increment_and_assert(repo, index, matrix, hexsha,
                                      ["fileA", "fileB", "fileC"],
                                      csr_matrix([
                                          [2, 1, 1],
                                          [1, 1, 0],
                                          [1, 0, 1],
                                      ]),
                                      "8652aaa2ccb537e0f47432061a75c3aeca71a311")
        index, matrix, hexsha = \
            self.increment_and_assert(repo, index, matrix, hexsha,
                                      ["fileAR", "fileB", "fileC", "fileD"],
                                      csr_matrix([
                                          [3, 1, 1, 1],
                                          [1, 1, 0, 0],
                                          [1, 0, 1, 0],
                                          [1, 0, 0, 1],
                                      ]),
                                      "8f5b3ad22905e4c92a4d73b2791aed76d4afd68e")
        index, matrix, hexsha = \
            self.increment_and_assert(repo, index, matrix, hexsha,
                                      ["fileAR", "fileC", "fileD", "fileE"],
                                      csr_matrix([
                                          [3, 1, 1, 0],
                                          [1, 1, 0, 0],
                                          [1, 0, 1, 0],
                                          [0, 0, 0, 1],
                                      ]),
                                      "d0e718916df15cbcb6a474815a6346028b6f9a2b")
        index, matrix, hexsha = \
            self.increment_and_assert(repo, index, matrix, hexsha,
                                      ["fileAR", "fileC", "fileD", "fileE"],
                                      csr_matrix([
                                          [4, 2, 1, 0],
                                          [2, 2, 0, 0],
                                          [1, 0, 1, 0],
                                          [0, 0, 0, 1],
                                      ]),
                                      "be65bc0dc0390cc07cd08bfbb72fe40710699224")
        index, matrix, hexsha = \
            self.increment_and_assert(repo, index, matrix, hexsha,
                                      ["fileAR", "fileCR", "fileD", "fileE"],
                                      csr_matrix([
                                          [5, 3, 1, 0],
                                          [3, 3, 0, 0],
                                          [1, 0, 1, 0],
                                          [0, 0, 0, 1],
                                      ]),
                                      "f4e1f461184ceacb75ed80268e6aff4995493644")
        index, matrix, hexsha = \
            self.increment_and_assert(repo, index, matrix, hexsha,
                                      ["fileAR", "fileCR", "fileE"],
                                      csr_matrix([
                                          [6, 3, 0],
                                          [3, 3, 0],
                                          [0, 0, 1],
                                      ]),
                                      "510193339b5d246abe98f75dc157637d20537995")
        index, matrix, hexsha = \
            self.increment_and_assert(repo, index, matrix, hexsha,
                                      ["fileARR", "fileCR", "fileER"],
                                      csr_matrix([
                                          [7, 3, 1],
                                          [3, 3, 0],
                                          [1, 0, 2],
                                      ]),
                                      "9c581e105a348188fabd4eea8753a6263dee73da")
        index, matrix, hexsha = \
            self.increment_and_assert(repo, index, matrix, hexsha,
                                      ["fileARRR", "fileER"],
                                      csr_matrix([
                                          [8, 1],
                                          [1, 2],
                                      ]),
                                      "14aea80b915d6da1d330057e5666768c26ffb2e6")

    def test_sort_coocc(self):
        in_idx = ["B", "C", "A"]
        in_mat = csr_matrix([
            [2, 1, 0],
            [1, 2, 2],
            [0, 2, 3],
        ])
        exp_idx = ["A", "B", "C"]
        exp_mat = csr_matrix([
            [3, 0, 2],
            [0, 2, 1],
            [2, 1, 2],
        ])
        act_idx, act_mat = sort_coocc(in_idx, in_mat)

        self.assertEqual(exp_idx, act_idx)
        # exp_mat == act_mat
        #   for efficiency issue, we should use below expression
        #   https://stackoverflow.com/questions/30685024
        self.assertTrue((exp_mat != act_mat).nnz == 0)

    def increment_and_assert(self, repo: git.Repo,
                             in_index: List[str], in_mat: csr_matrix, in_hex: str,
                             exp_idx: List[str], exp_mat: csr_matrix, exp_hex: str) \
            -> (List[str], csr_matrix, str):
        act_idx, act_mat, act_hex = increment(repo, in_hex, in_index, in_mat)
        self.assertEqual(exp_idx, act_idx)
        self.assertTrue((exp_mat != act_mat).nnz == 0)
        self.assertEqual(exp_hex, act_hex)
        return act_idx, act_mat, act_hex


if __name__ == '__main__':
    unittest.main()
