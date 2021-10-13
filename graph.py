import sys
from typing import List, Union
from enum import Enum

import networkx as nx
from scipy.sparse import csr_matrix


class GraphType(Enum):
    BASIC = "basic"
    SUPPORT = "support"
    CONFIDENCE = "confidence"
    CONFIDENCE_REV = "confidence_rev"

    def __str__(self):
        return self.value


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
        elif graph_type == GraphType.CONFIDENCE_REV:
            g = nx.DiGraph()
            for i in range(matrix.shape[0]):
                for (j, w) in zip(matrix[i].indices, matrix[i].data):
                    conf = w / matrix[i, i]
                    g.add_edge(i, j, weight=(1 - conf))
        else:
            print("Unsupported graph type: {}".format(graph_type))
            sys.exit(1)
        self.g = g
        self.graph_type = graph_type
        self.index = index

    def get_graph(self):
        return self.g

    def guide(self, sources: List[str], cutoff: Union[int, float] = 2):
        target_indexes = []
        if self.graph_type == GraphType.CONFIDENCE_REV:
            for s in sources:
                s_i = self.index.index(s)
                targets, _ = nx.single_source_dijkstra(self.g, s_i, cutoff=cutoff)
                target_indexes.extend(targets.keys())
                name_sorted = sorted([self.index[t_i] for t_i in target_indexes])
                return sorted(name_sorted, key=lambda x: targets[self.index.index(x)])
        else:
            for s in sources:
                s_i = self.index.index(s)
                target_indexes.extend(nx.single_source_shortest_path(self.g, s_i, cutoff))
            return sorted([self.index[t_i] for t_i in target_indexes])
