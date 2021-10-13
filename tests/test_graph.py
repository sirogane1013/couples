import unittest

from scipy.sparse import csr_matrix

from graph import Graph, GraphType


class GraphTest(unittest.TestCase):
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

    def test_guide_with_CONFIDENCE_REV(self):
        # A--B--C
        #    |
        #    D--E
        # (A,B) = 1-0.5,  (B,A) = 1-0.25,
        # (B,C) = 1-0.25, (C,B) = 1-1.0,
        # (B,D) = 1-0.5,  (D,B) = 1-0.5,
        # (D,E) = 1-1.0,  (E,D) = 1-1.0,
        in_idx = ["A", "B", "C", "D", "E"]
        in_mat = csr_matrix([
            [2, 1, 0, 0, 0],
            [1, 4, 1, 2, 0],
            [0, 1, 1, 0, 0],
            [0, 2, 0, 4, 4],
            [0, 0, 0, 4, 4],
        ])
        graph = Graph(in_idx, in_mat, GraphType.CONFIDENCE_REV)
        in_src = ["A"]
        in_cut = 1.0
        exp_tgt = ["A", "B", "D", "E"]
        act_tgt = graph.guide(in_src, in_cut)
        self.assertEqual(exp_tgt, act_tgt)

        in_src = ["B"]
        in_cut = 1.0
        exp_tgt = ["B", "D", "E", "A", "C"]
        act_tgt = graph.guide(in_src, in_cut)
        self.assertEqual(exp_tgt, act_tgt)


if __name__ == '__main__':
    unittest.main()
