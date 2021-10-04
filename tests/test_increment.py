import unittest

import git
from scipy.sparse import csr_matrix

from increment import increment, sort_coocc


class IncrementTest(unittest.TestCase):
    def setUp(self):
        super().setUp()

    def test_increment(self):
        repo = git.Repo("./resource/test_repo")
        origin_hex = "2205a5f44fa0a450c978a600d478935f159d6e27"
        in_index = ["A", "B"]
        in_mat = csr_matrix([
            [1, 1],
            [1, 1],
        ])
        exp_idx = ["A", "B"]
        exp_mat = csr_matrix([
            [2, 2],
            [2, 2],
        ])
        exp_hex = "0f0a9bb941f5443392ad659d113205ab1ea3ff71"
        act_idx, act_mat, act_hex = increment(repo, origin_hex, in_index, in_mat)
        self.assertEqual(exp_idx, act_idx)
        self.assertTrue((exp_mat != act_mat).nnz == 0)
        self.assertEqual(exp_hex, act_hex)

        exp_idx = ["A", "B", "C"]
        exp_mat = csr_matrix([
            [2, 2, 0],
            [2, 2, 0],
            [0, 0, 1],
        ])
        exp_hex = "f69f5b8a351a25013834cb4a3893a2f94aa9f718"
        act_idx, act_mat, act_hex = increment(repo, act_hex, act_idx, act_mat)
        self.assertEqual(exp_idx, act_idx)
        self.assertTrue((exp_mat != act_mat).nnz == 0)
        self.assertEqual(exp_hex, act_hex)

        exp_idx = ["B", "C", "RA"]
        exp_mat = csr_matrix([
            [2, 0, 2],
            [0, 1, 0],
            [2, 0, 3],
        ])
        exp_hex = "cc332a3b870dec2c6015b27ab02b63ed55acd5f2"
        act_idx, act_mat, act_hex = increment(repo, act_hex, act_idx, act_mat)
        self.assertEqual(exp_idx, act_idx)
        self.assertTrue((exp_mat != act_mat).nnz == 0)
        self.assertEqual(exp_hex, act_hex)

        exp_idx = ["B", "RA"]
        exp_mat = csr_matrix([
            [2, 2],
            [2, 3],
        ])
        exp_hex = "7ecc52433843041a1d6c8747191c33e9581003af"
        act_idx, act_mat, act_hex = increment(repo, act_hex, act_idx, act_mat)
        self.assertEqual(exp_idx, act_idx)
        self.assertTrue((exp_mat != act_mat).nnz == 0)
        self.assertEqual(exp_hex, act_hex)

        exp_idx = ["D", "RA", "RB"]
        exp_mat = csr_matrix([
            [1, 1, 1],
            [1, 4, 3],
            [1, 3, 3],
        ])
        exp_hex = "ab0755128e8caf69189056a2c5832e597d93e670"
        act_idx, act_mat, act_hex = increment(repo, act_hex, act_idx, act_mat)
        self.assertEqual(exp_idx, act_idx)
        self.assertTrue((exp_mat != act_mat).nnz == 0)
        self.assertEqual(exp_hex, act_hex)

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


if __name__ == '__main__':
    unittest.main()
