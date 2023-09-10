from dsplot.graph import Graph


def draw(data):
    graph = Graph(data, directed=True)
    graph.plot()
