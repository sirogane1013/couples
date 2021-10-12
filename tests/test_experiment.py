import unittest
from unittest.mock import MagicMock, patch

from experiment.leave_out import leave_one_out


class ExperimentTest(unittest.TestCase):

    @patch(
        "experiment.leave_out.get_modified",
        return_value=["A", "B", "C"]
    )
    def test_leave_one_out(self, get_modified_mock):
        commit = MagicMock()
        commit.hexsha = "MOCK"
        graph = MagicMock()
        graph.guide = MagicMock(side_effect=[
            ["B", "M", "F"],  # leave out "B"
            [],  # leave out "C"
            ["E", "A"],  # leave out "A"
        ])
        exp_hexsha = "MOCK"
        exp_feedback = 2 / 3
        exp_mrr = (1 + 1 / 2) / (3 * exp_feedback)
        exp_recall = 2 / 3
        exp_details = [
            {
                "target": "B",
                "rank": 1
            },
            {
                "target": "C",
                "rank": 2
            },
            {
                "target": "A",
                "rank": -1
            },
        ]
        act_hexsha, act_mrr, act_recall, act_feedback, act_details = leave_one_out(commit, graph)
        self.assertEqual(exp_hexsha, act_hexsha)
        self.assertEqual(exp_mrr, act_mrr)
        self.assertEqual(exp_recall, act_recall)
        self.assertEqual(exp_feedback, act_feedback)


if __name__ == '__main__':
    unittest.main()
