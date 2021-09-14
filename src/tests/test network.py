from src import network

net = network.Network(20, False)
net.generate_live_edge_graph()
print(net.activation_realization)
print(net.adjacency_matrix)
print(net.cross_category_edges)