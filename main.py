from Network import *
import numpy as np

n = 50

iter = []

for j in range (5):
    network = Network(n)
    probs = []
    for i in range (10000):
        live_graph, prob = network.generate_live_edge_graph()
        probs.append(prob)

    print(j)
    print(np.mean(probs))
    iter.append(np.mean(probs))

print(iter)
