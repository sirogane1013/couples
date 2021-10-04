from typing import BinaryIO
import yaml
import sys
import io
import re
from argparse import Namespace
from scipy.sparse import csr_matrix


def _parse_coocc_matrix(matrix):
    data = []
    indices = []
    indptr = [0]
    for row in matrix:
        for k, v in sorted(row.items()):
            data.append(v)
            indices.append(k)
        indptr.append(indptr[-1] + len(row))
    return csr_matrix((data, indices, indptr), shape=(len(matrix),) * 2)


class Reader(object):
    def __init__(self):
        self.data = None

    def read(self, fileobj: BinaryIO):
        yaml.reader.Reader.NON_PRINTABLE = re.compile(r"(?!x)x")
        try:
            loader = yaml.CLoader
        except AttributeError:
            print(
                "Warning: failed to import yaml.CLoader, falling back to slow yaml.Loader"
            )
            loader = yaml.Loader
        try:
            wrapper = io.TextIOWrapper(fileobj, encoding="utf-8")
            data = yaml.load(wrapper, Loader=loader)
        except (UnicodeEncodeError, UnicodeDecodeError, yaml.reader.ReaderError) as e:
            print(
                "\nInvalid unicode in the input: %s\nPlease filter it through "
                "fix_yaml_unicode.py" % e
            )
            sys.exit(1)
        if data is None:
            print("\nNo data has been read - has Hercules crashed?")
            sys.exit(1)
        self.data = data

    def get_files_coocc(self):
        coocc = self.data["Couples"]["files_coocc"]
        return coocc["index"], _parse_coocc_matrix(coocc["matrix"])

    def get_name(self):
        return self.data["hercules"]["repository"]


def read_input(input_file: str) -> Reader:
    stream = open(input_file, "rb")
    try:
        reader = Reader()
        reader.read(stream)
    finally:
        stream.close()

    return reader
