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

    def __init__(self, n, fc):
        self.adjacency_matrix = np.zeros((n, n))
        self.nodes = []
        self.n = n
        self.click_probabilities = np.zeros((n, n))

        # Create n nodes
        for i in range (self.n):
            self.nodes.append(Node(random.choice(categories)))

        # Create adj matrix
        if fc:
            self.adjacency_matrix = np.ones((n, n), dtype=int)
        else:
            for i in range (self.n):
                for ii in range(self.n):
                    self.adjacency_matrix[i][ii] = random.getrandbits(1)
        for i in range(n):
            self.adjacency_matrix[i][i] = 0

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
    def depth_first_search(self, root, activated_nodes, live_edge_adjacency_matrix):
      # print(seeds)
      for k in range(self.n):
        if live_edge_adjacency_matrix[root][k] == 1:
          if k not in activated_nodes:
            activated_nodes.append(k)
            self.depth_first_search(k, activated_nodes, live_edge_adjacency_matrix)
      return activated_nodes

    def calculate_activated_nodes(self, seeds, live_edge_adjacency_matrix):
      activated_nodes = seeds.copy()
      # print(seeds)
      for i in seeds:
        activated_nodes = self.depth_first_search(i, activated_nodes, live_edge_adjacency_matrix)
      # print(seeds)
      return activated_nodes

    # this is too big to calculate for depth more than 5
    # def binary_strings(depth):
    #   if depth < 1:
    #     print('no')
    #     return
    #   if depth == 1:
    #     return ['0', '1']
    #   result = []
    #   for i in binary_strings(depth-1):
    #     result.append('0' + i)
    #     result.append('1' + i)
    #   result.sort()
    #   return result

    # measure exact activations by complete enumeration
    # input: seeds (the nodes that start the influence cascade)
    # output: average (average number of nodes activated by seeds in each simulation);
    # output: ground_truth_activation_probabilities (activation probability of each node)
    def calculateActivations(self, seeds):
        # enumerate all live edge graphs to calculate node activation probability
        # takes 1 minute to compute with a fully connected graph (with no self loops) with 5 nodes
        # print(2 ** (self.n * (self.n - 1))) #number of live edge graphs to enumerate
        # reset previously calculated values
        for a in self.nodes:
            a.activation_probability = 0

        progress_index = 1  # track loop progress for very long computations
        average = 0  # number of nodes activated by seed on average

        # loop over all possible live edge graphs
        for live_edge_graph_index in range(2 ** (self.n * (self.n - 1))):
            #####################################################################################################
            live_edges = []  # which edges are active in the live edge graph
            # there are at most n*(n-1) edges (no self loops)
            for a in range(self.n * (self.n - 1)):
                live_edges.append('0')
            binary_string = "{0:b}".format(live_edge_graph_index)  # binary string of live_edge_graph_index
            live_edges[-len(binary_string):] = list(binary_string)
            #####################################################################################################
            live = np.zeros((self.n, self.n), dtype=np.int8)  # adjacency matrix for the live edge graph
            edge_index = -1
            # create live edge graph corresponding to the current live_edge_graph_index
            for j in range(self.n):
                for jj in range(self.n):
                    if self.adjacency_matrix[j][jj] == 1:
                        edge_index += 1
                        if live_edges[edge_index] == '1':
                            live[j][jj] = self.adjacency_matrix[j][jj]
            # print(live)
            #####################################################################################################
            # calculate the probability of the current live edge graph
            probability = 0
            for i in range(self.n):
                for ii in range(self.n):
                    if live[i][ii] == 1:
                        if probability == 0:
                            probability = self.weight_matrix[self.nodes[i].category][self.nodes[ii].category]
                        else:
                            probability = probability * self.weight_matrix[self.nodes[i].category][
                                self.nodes[ii].category]
                    elif live[i][ii] == 0:
                        if probability == 0:
                            probability = 1 - self.weight_matrix[self.nodes[i].category][
                                self.nodes[ii].category]
                        else:
                            probability = probability * (1 - self.weight_matrix[self.nodes[i].category][
                                self.nodes[ii].category])
                    else:
                        print('big no no', type(live[i][ii]), live[i][ii])
                        break

            #####################################################################################################
            active_nodes = self.calculate_activated_nodes(seeds, live)
            average += len(active_nodes)

            for node_index in active_nodes:
                # this is only true for weights = 0.5
                # self.nodes[node_index].activation_probability += 1 / (2 ** (self.n * (self.n - 1)))
                self.nodes[node_index].activation_probability += probability
            #####################################################################################################
            progress_index += 1
            if progress_index % 100000 == 0:
                print(progress_index)
        #####################################################################################################
        average = average / (2 ** (self.n * (self.n - 1)))
        ground_truth_activation_probabilities = []
        for a in self.nodes:
            ground_truth_activation_probabilities.append(a.activation_probability / self.nodes[seeds[0]].activation_probability)
            # print(a.activation_probability)
        # print('average number of activated nodes: ', average)
        return average, ground_truth_activation_probabilities

    # calculate the influence generated by the seeds using approximated monte carlo method
    # input: seeds (the nodes that start the influence cascade)
    # input: iterations (how many iterations of the simulation to do)
    # [more iterations takes more time and gives more accurate results]
    # output: average_active_nodes (average number of active nodes in all the simulations)
    # output: estimated_activation_probabilities (estimated activation probability for each node in the network)
    def monteCarloEstimation(self, seeds=[0], iterations=100):
        # monte carlo sampling
        # reset previously calculated values
        average_active_nodes = 0
        for i in self.nodes:
            i.z = 0
            i.activation_probability = 0

        for i in range(iterations):
            # generate live edge graph and calculate activated nodes
            live, p = self.generate_live_edge_graph()
            active_nodes = self.calculate_activated_nodes(seeds, live)
            active_nodes.sort()
            # update average number of activated nodes
            if i == 0:
                average_active_nodes = len(active_nodes)
            else:
                average_active_nodes = (average_active_nodes * (i) + len(active_nodes)) / (i + 1)
            # update node activation counts
            for nod in active_nodes:
                self.nodes[nod].z += 1
            # progress print for very long calculations
            if i % 100000 == 0:
                print('progress: ', i)
        estimated_activation_probabilities = []
        for i in range(self.n):
            ap = self.nodes[i].z / iterations
            self.nodes[i].activation_probability = ap
            estimated_activation_probabilities.append(ap)

        return average_active_nodes, estimated_activation_probabilities

    # calculate the error of the estimated probabilities wrt the ground truth if available
    # input: ground truth
    # input: estimations
    # output: sum of squares error on activation probabilities
    def evaluateError(self, ground_truth_activation_probabilities, estimated_activation_probabilities):
        error = 0
        for asd in range(len(self.nodes)):
            error += (ground_truth_activation_probabilities[asd] - estimated_activation_probabilities[asd]) ** 2
        return error


