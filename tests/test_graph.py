import unittest

from scipy.sparse import csr_matrix

from graph import Graph


class MyTestCase(unittest.TestCase):
    def test_guide(self):
        # A--B--C
        #    |
        #    D--E
        in_idx = ["A", "B", "C", "D", "E"]
        in_mat = csr_matrix([
            [0, 1, 0, 0, 0],
            [1, 0, 1, 1, 0],
            [0, 1, 0, 0, 0],
            [0, 1, 0, 0, 1],
            [0, 0, 0, 1, 0],
        ])
        graph = Graph(in_idx, in_mat)
        in_src = ["A"]
        in_cut = 2
        exp_tgt = ["A", "B", "C", "D"]
        act_tgt = graph.guide(in_src, in_cut)
        self.assertEqual(exp_tgt, act_tgt)

        in_src = ["A", "E"]
        in_cut = 1
        exp_tgt = ["A", "B", "D", "E"]
        act_tgt = graph.guide(in_src, in_cut)
        self.assertEqual(exp_tgt, act_tgt)


if __name__ == '__main__':
    unittest.main()
