import sys
from typing import List
from enum import Enum

import networkx as nx
from scipy.sparse import csr_matrix


class GraphType(Enum):
    BASIC = 1
    SUPPORT = 2
    CONFIDENCE = 3


class Graph:
    def __init__(self, index: List[str], matrix: csr_matrix, graph_type: GraphType = GraphType.BASIC):
        if graph_type == GraphType.BASIC:
            g = nx.Graph()
            for i in range(matrix.shape[0]):
                for j in matrix[i].indices:
                    g.add_edge(i, j)
        elif graph_type == GraphType.SUPPORT:
            g = nx.Graph()
            for i in range(matrix.shape[0]):
                for (j, w) in zip(matrix[i].indices, matrix[i].data):
                    g.add_edge(i, j, weight=w)
        elif graph_type == GraphType.CONFIDENCE:
            g = nx.DiGraph()
            for i in range(matrix.shape[0]):
                for (j, w) in zip(matrix[i].indices, matrix[i].data):
                    conf = w / matrix[i, i]
                    g.add_edge(i, j, weight=conf)
        else:
            print("Unsupported graph type: {}".format(graph_type))
            sys.exit(1)
        self.g = g
        self.index = index

    def get_graph(self):
        return self.g

    def guide(self, sources: List[str], cutoff: int = 2):
        target_indexes = []
        for s in sources:
            s_i = self.index.index(s)
            target_indexes.extend(nx.single_source_shortest_path(self.g, s_i, cutoff))
        return sorted([self.index[t_i] for t_i in target_indexes])
