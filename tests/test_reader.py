import unittest

from scipy.sparse import csr_matrix

from reader import read_input


class ReaderTest(unittest.TestCase):
    def setUp(self):
        self.reader = read_input("./resource/couples_sample.yaml")
        super().setUp()

    def test_get_name(self):
        self.assertEqual(self.reader.get_name(), "sample")

    def test_get_files_coocc(self):
        exp = csr_matrix([
            [2, 1, 2],
            [1, 2, 2],
            [2, 2, 3],
        ])
        _, act = self.reader.get_files_coocc()
        # exp == act
        #   for efficiency issue, we should use below expression
        #   https://stackoverflow.com/questions/30685024
        self.assertTrue((exp != act).nnz == 0)


if __name__ == '__main__':
    unittest.main()
