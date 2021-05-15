import numpy as np
import random


categories = [0, 1, 2, 3, 4]


class Node():

    def __init__(self, category):
        self.category = category
        self.z = 0
        self.activation_probability = 0

    def show_ad(self):
        # Decide if the node will turn into a seed after being shown the ad
        print("todo")

class Network():

    def __init__(self, adjacency_matrix, n):
        self.adjacency_matrix = adjacency_matrix
        self.nodes = []
        self.n = n

        # Create n nodes
        for i in range (self.n):
            self.nodes.append(Node(random.choice(categories)))

        # Create adj matrix
        for i in range (self.n):
            for ii in range(self.n):
                self.adjacency_matrix[i][ii] = random.getrandbits(1)

        self.weight_matrix = np.zeros((len(categories), len(categories)))
        for i in range(len(categories)):
            for ii in range(len(categories)):
                self.weight_matrix[i][ii] = 0.1

    def generate_live_edge_graph(self):
        live_edge_adjacency_matrix = np.zeros((self.n, self.n))
        probability = 0
        for i in range(self.n):
            for ii in range(self.n):
                # Generate a random sample. If the weight of an edge is bigger than the sample, it activates
                # and becomes a live edge (if it was connected in the first place)
                # Then, calculate the probability of this live edge graph.
                sample = random.random()
                # If the edge activates
                if sample < self.weight_matrix[self.nodes[i].category][self.nodes[ii].category]:
                    live_edge_adjacency_matrix[i][ii] = self.adjacency_matrix[i][ii]
                    # Update probability only if the edge exists
                    if self.adjacency_matrix[i][ii] == 1:
                        if probability == 0:
                            probability = self.weight_matrix[self.nodes[i].category][self.nodes[ii].category]
                        else:
                            probability = probability * self.weight_matrix[self.nodes[i].category][self.nodes[ii].category]
                # If the edge does not activate
                else:
                    if self.adjacency_matrix[i][ii] == 1:
                        if probability == 0:
                            probability = 1 - self.weight_matrix[self.nodes[i].category][self.nodes[ii].category]
                        else:
                            probability = probability * (1 - self.weight_matrix[self.nodes[i].category][
                                self.nodes[ii].category])

        return live_edge_adjacency_matrix, probability


