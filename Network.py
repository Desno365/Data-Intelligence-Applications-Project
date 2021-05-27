import numpy as np
import random
random.seed(1337)


categories = [0, 1, 2, 3, 4]


class Node():

    def __init__(self, category):
        self.category = category
        self.z = 0
        self.activation_probability = 0

    def show_ad(self):
        # Decide if the node will turn into a seed after being shown the ad
        # Per il momento assunto che ritorni il clicked slot, altrimenti modificare il publisher
        print("todo")

class Network():

    def __init__(self, n):
        self.adjacency_matrix = np.zeros((n, n))
        self.nodes = []
        self.n = n
        self.click_probabilities = np.zeros((n, n))

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
                self.weight_matrix[i][ii] = 0.5

    def generate_live_edge_graph(self):
        live_edge_adjacency_matrix = np.zeros((self.n, self.n))
        probability = 0
        for i in range(self.n):
            for ii in range(self.n):
                if self.adjacency_matrix[i][ii] == 0:
                    # If the edge does not exist, skip
                    continue
                # Generate a random sample. If the weight of an edge is bigger than the sample, it activates
                # and becomes a live edge (if it was connected in the first place)
                # Then, calculate the probability of this live edge graph.
                sample = random.random()
                # If the edge activates
                if sample < self.weight_matrix[self.nodes[i].category][self.nodes[ii].category]:
                    live_edge_adjacency_matrix[i][ii] = self.adjacency_matrix[i][ii]

                    if probability == 0:
                        probability = self.weight_matrix[self.nodes[i].category][self.nodes[ii].category]
                    else:
                        probability = probability * self.weight_matrix[self.nodes[i].category][self.nodes[ii].category]
                # If the edge does not activate
                else:
                    if probability == 0:
                        probability = 1 - self.weight_matrix[self.nodes[i].category][self.nodes[ii].category]
                    else:
                        probability = probability * (1 - self.weight_matrix[self.nodes[i].category][
                            self.nodes[ii].category])

        return live_edge_adjacency_matrix, probability

    #calculate activated nodes in the live edge graph
    def depth_first_search(root, activated_nodes, live_edge_adjacency_matrix):
      # print(seeds)
      for k in range(Network.n):
        if live_edge_adjacency_matrix[root][k] == 1:
          if k not in activated_nodes:
            activated_nodes.append(k)
            Network.depth_first_search(k, activated_nodes, live_edge_adjacency_matrix)
      return activated_nodes

    def calculate_activated_nodes(seeds, live_edge_adjacency_matrix):
      activated_nodes = seeds.copy()
      # print(seeds)
      for i in seeds:
        activated_nodes = Network.depth_first_search(i, activated_nodes, live_edge_adjacency_matrix)
      # print(seeds)
      return activated_nodes

