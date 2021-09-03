import numpy as np
import random
import constants
import ad
import bids_enum
import slot
import auction.vcg_auction
# random.seed(1337)


class Node:
    def __init__(self, category):
        self.id = -1
        self.category = category
        self.z = 0
        self.activation_probability = 0
        # value goes between 0 and infinity, 0 means the user never clicks anything
        # infinity means the user clicks all ads with p = ad quality
        self.click_propensity = constants.click_propensities[category]

    def show_ad(self, slate):
        for ad in range(len(slate)):
            if random.random() < self.activation_probability:
                return ad
        return -1


class Network:
    def __init__(self, n, fc):
        self.adjacency_matrix = np.zeros((n, n))
        self.nodes = []
        self.n = n
        self.click_probabilities = np.zeros((n, n))

        # Create n nodes
        for i in range(self.n):
            newNode = Node(random.choice(constants.categories))
            newNode.id = i
            self.nodes.append(newNode)

        # Create adj matrix
        if fc:
            self.adjacency_matrix = np.ones((n, n), dtype=int)
        else:
            for i in range(self.n):
                for ii in range(self.n):
                    self.adjacency_matrix[i][ii] = 1 if random.random() < constants.network_connectivity else 0
        for i in range(n):
            self.adjacency_matrix[i][i] = 0

        self.weight_matrix = np.zeros((len(constants.categories), len(constants.categories)))
        for i in range(len(constants.categories)):
            for ii in range(len(constants.categories)):
                self.weight_matrix[i][ii] = 0.1

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

    # input seeds (nodes that start the cascade)
    # input live_edge_adjacency_matrix (definition of the active edges in the graph)
    # output activated_nodes (list of int indicating the activated nodes)
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
            # print(active_nodes)
            active_nodes.sort()
            # print(active_nodes)
            # update average number of activated nodes
            if i == 0:
                average_active_nodes = len(active_nodes)
            else:
                average_active_nodes = (average_active_nodes * (i) + len(active_nodes)) / (i + 1)
            # update node activation counts
            for nod in active_nodes:
                self.nodes[nod].z += 1
            # progress print for very long calculations
            if i % 100000 == 0 and i != 0:
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

    # input ad_quality (the likelihood of clicking the ad once it is observed)
    # input iterations (the number of monte carlo iterations to perform)
    # output seeds (the nodes that clicked the ads and became seeds)
    # output activated_nodes (the average number of nodes that have been activated by the seeds)
    # output activation_probabilities (the probability that a node from a given category is activated given the seeds)
    def monte_carlo_with_pseudo_nodes_1(self, ad_quality, iterations=100):
        # combine click propensity with ad quality
        # determine seeds
        seeds = []
        for node in self.nodes:
            # ad quality goes between 0 and 1
            # 0 means the ad is not clickable
            # 1 means users are forced to click the ad
            activation_probability = ad_quality ** (1 / node.click_propensity)
            sample = random.random()
            if sample < activation_probability:
                seeds.append(node.id)
        activated_nodes, activation_probalities = self.monteCarloEstimation(seeds, iterations)
        return seeds, activated_nodes, activation_probalities

    def monte_carlo_with_pseudo_nodes_2(self, ad_quality, iterations=100):
        # combine click propensity with ad quality
        # determine seeds
        seeds = []
        for node in self.nodes:
            # ad quality goes between 0 and 1
            # 0 means the ad is not clickable
            # 1 means users are forced to click the ad
            activation_probability = ad_quality * node.click_propensity
            sample = random.random()
            if sample < activation_probability:
                seeds.append(node.id)
        activated_nodes, activation_probalities = self.monteCarloEstimation(seeds, iterations)
        return seeds, activated_nodes, activation_probalities

    def monte_carlo_with_pseudo_nodes_3(self, activation_probability, iterations=100):
        # combine click propensity with ad quality
        # determine seeds
        seeds = []
        for node in self.nodes:
            # ad quality goes between 0 and 1
            # 0 means the ad is not clickable
            # 1 means users are forced to click the ad
            # activation_probability = ad_quality_table[advertiser, category]
            sample = random.random()
            if sample < activation_probability:
                seeds.append(node.id)
        activated_nodes, activation_probalities = self.monteCarloEstimation(seeds, iterations)
        return seeds, activated_nodes, activation_probalities


    # TODO ad quality depends on advertiser
    def MC_pseudoNodes_freshSeeds(self, ad_quality, iterations=100, slates=[]):
        avg_active_nodes = 0
        avg_n_seeds = {}
        avg_n_seeds_per_campaign = {}
        avg_active_nodes_per_campaign = {}
        for i in range(iterations):
            seeds_for_capmaign = {}
            seeds = {}
            activation_probalities_per_campaign = {}
            for node in self.nodes:
                # ad quality goes between 0 and 1
                # 0 means the ad is not clickable
                # 1 means users are forced to click the ad
                # by this implementation all ads are shown to everybody with effectively the same relevance
                if not slates:
                    activation_probability = ad_quality[node.category]
                    sample = random.random()
                    if sample < activation_probability:
                        if node.category not in seeds.keys():
                            seeds[node.category] = []
                        seeds[node.category].append(node.id)
                # node category determines slate / ad relevance
                # extract samples in order and determine seeds for each campaign
                # take slates from publisher, passed as input (slates)
                else:
                    slate = slates[node.category]
                    is_seed = False
                    for position in slate:
                        activation_probability = ad_quality[node.category]*position.slot_prominence
                        sample = random.random()
                        if sample < activation_probability:
                            if position.assigned_ad.ad_id not in seeds_for_capmaign.keys():
                                seeds_for_capmaign[position.assigned_ad.ad_id] = []
                            seeds_for_capmaign[position.assigned_ad.ad_id].append(node.id)
                            is_seed = True
                            break
            # with slates
            # print('these are the seeds: ', seeds_for_capmaign)
            for campaign in seeds_for_capmaign.keys():
                print(campaign)
                activated_nodes, activation_probalities = self.monteCarloEstimation(seeds_for_capmaign[campaign], 1)
                if campaign not in avg_n_seeds_per_campaign.keys():
                    avg_n_seeds_per_campaign[campaign] = 0
                else:
                    avg_n_seeds_per_campaign[campaign] += len(seeds_for_capmaign[campaign])
                if campaign not in avg_active_nodes_per_campaign.keys():
                    avg_active_nodes_per_campaign[campaign] = 0
                else:
                    avg_active_nodes_per_campaign[campaign] += activated_nodes
            # without slates
            cumulated_seeds = []
            for a in seeds.keys():
                for ii in seeds[a]:
                    cumulated_seeds.append(ii)
            nodes, probabilities = self.monteCarloEstimation(cumulated_seeds, 1)
            for a in range(len(ad_quality)):
                if a not in avg_n_seeds.keys():
                    avg_n_seeds[a] = 0
                avg_n_seeds[a] += len(seeds[list(seeds.keys())[a]])
            avg_active_nodes += nodes
        # with slates
        for campaign in seeds_for_capmaign.keys():
            avg_n_seeds_per_campaign[campaign] = avg_n_seeds_per_campaign[campaign] / iterations
            avg_active_nodes_per_campaign[campaign] = avg_active_nodes_per_campaign[campaign] / iterations
        # without slates
        for i in avg_n_seeds.keys():
            avg_n_seeds[i] = avg_n_seeds[i] / iterations
        avg_active_nodes = avg_active_nodes / iterations
        if slates:
            return avg_active_nodes_per_campaign, avg_n_seeds_per_campaign
        else:
            return avg_n_seeds, avg_active_nodes
