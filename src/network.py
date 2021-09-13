import math
from datetime import datetime
from typing import List

import numpy as np
import random
from src import constants
from src.slot import Slot


class Node:
    def __init__(self, category):
        self.id = -1
        self.category = category
        self.z = 0
        self.activation_probability = 0

    def show_ad(self, slate):
        for ad in range(len(slate)):
            if random.random() < self.activation_probability:
                return ad
        return -1


class Network:
    @staticmethod
    def prettyPrintSocialInfluence(socialInfluence):
        print("### social influence report ###")
        print('### start ###')
        for ad in socialInfluence.keys():
            print('ad id: ', ad)
            for category in socialInfluence[ad].keys():
                print('category: ', category, 'seeds: ', socialInfluence[ad][category]['seeds'], ' activatedNodes: ', socialInfluence[ad][category]['activatedNodes'])
        print('### end ###')

    def __init__(self, n, fc):
        self.adjacency_matrix = np.zeros((n, n))
        self.nodes = []
        self.n = n
        self.click_probabilities = np.zeros((n, n))
        self.cross_category_edges = [[0 for _ in constants.categories] for _ in constants.categories]
        self.activation_realization = [[0 for _ in constants.categories] for _ in constants.categories]
        # Create n nodes
        for i in range(self.n):
            newNode = Node(random.choice(constants.categories))
            newNode.id = i
            self.nodes.append(newNode)

        # Create adj matrix
        if fc:
            self.adjacency_matrix = np.ones((n, n), dtype=int)
        else:
            # using network connectivity
            # for i in range(self.n):
            #     for ii in range(self.n):
            #         self.adjacency_matrix[i][ii] = 1 if random.random() < constants.network_connectivity else 0
            # using number of neighbours
            for i in range(self.n):
                extracted_node = []
                for ii in range(10):
                    self.adjacency_matrix[i][math.floor(random.random()) * self.n] = 1
                    self.cross_category_edges[self.nodes[i].category][self.nodes[ii].category] += 1
        for i in range(n):
            self.adjacency_matrix[i][i] = 0

        self.weight_matrix = np.zeros((len(constants.categories), len(constants.categories)))
        for i in range(len(constants.categories)):
            for ii in range(len(constants.categories)):
                self.weight_matrix[i][ii] = random.random()




    def generate_live_edge_graph(self, activation_probabilities=None):
        self.activation_realization = [[0 for _ in constants.categories] for _ in constants.categories]
        if activation_probabilities is None:
            activation_probabilities = self.weight_matrix
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
                edge_activation_probability = activation_probabilities[self.nodes[i].category][self.nodes[ii].category]
                if sample < edge_activation_probability:
                    live_edge_adjacency_matrix[i][ii] = 1
                    self.activation_realization[self.nodes[i].category][self.nodes[ii].category] += 1

                    if probability == 0:
                        probability = edge_activation_probability
                    else:
                        probability = probability * edge_activation_probability
                # If the edge does not activate
                else:
                    if probability == 0:
                        probability = 1 - edge_activation_probability
                    else:
                        probability = probability * (1 - edge_activation_probability)

        return live_edge_adjacency_matrix, probability

    # calculate activated nodes in the live edge graph (with recursion)
    # def depth_first_search(self, root, activated_nodes, live_edge_adjacency_matrix):
    #   for k in range(self.n):
    #     if live_edge_adjacency_matrix[root][k] == 1:
    #       if k not in activated_nodes:
    #         activated_nodes.append(k)
    #         self.depth_first_search(k, activated_nodes, live_edge_adjacency_matrix)
    #   return activated_nodes
    # # calculate activated nodes in the live edge graph (with stack)
    def depth_first_search(self, activated_nodes, live_edge_adjacency_matrix):
        seeds = activated_nodes.copy()
        for seed in seeds:
            stack = []
            stack.append(seed)
            while len(stack):
                s = stack.pop()
                for k in range(self.n):
                    if live_edge_adjacency_matrix[s][k] == 1:
                        if k not in activated_nodes:
                            activated_nodes.append(k)
        return activated_nodes

    # # input seeds (nodes that start the cascade)
    # # input live_edge_adjacency_matrix (definition of the active edges in the graph)
    # # output activated_nodes (list of int indicating the activated nodes)
    # def calculate_activated_nodes(self, seeds, live_edge_adjacency_matrix):
    #   activated_nodes = seeds.copy()
    #   for i in seeds:
    #     activated_nodes = self.depth_first_search(i, activated_nodes, live_edge_adjacency_matrix)
    #   return activated_nodes


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
    def monteCarloEstimation(self, seeds=[0], iterations=100, activation_probabilities=None):
        # monte carlo sampling
        # reset previously calculated values
        average_active_nodes = {}
        for category in constants.categories:
            if category not in average_active_nodes.keys():
                average_active_nodes[category] = 0
        for i in self.nodes:
            i.z = 0
            i.activation_probability = 0

        for i in range(iterations):
            # generate live edge graph and calculate activated nodes
            live, p = self.generate_live_edge_graph(activation_probabilities=activation_probabilities)
            active_nodes = self.depth_first_search(seeds, live)
            active_nodes.sort()
            for node in active_nodes:
                average_active_nodes[self.nodes[node].category] += 1
            # update node activation counts
            for nod in active_nodes:
                self.nodes[nod].z += 1
        for category in average_active_nodes.keys():
            average_active_nodes[category] = average_active_nodes[category] / iterations
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

    # TODO ad quality depends on advertiser
    def estimateSocialInfluence(self, slates: List[List[Slot]], iterations: int = 100, use_estimated_qualities=False, estimated_activation_probabilities=None):

        avg_active_nodes = 0
        # average number of seeds throughout all the iterations
        avg_n_seeds = {}
        avg_n_seeds_per_ad_id = {}
        avg_active_nodes_per_ad_id = {}
        # built return dictionary
        r = {}
        for slate in slates:
            for slot in slate:
                r[slot.assigned_ad.ad_id] = {}
                for category in constants.categories:
                    r[slot.assigned_ad.ad_id][category] = {}
                    r[slot.assigned_ad.ad_id][category]['seeds'] = 0
                    r[slot.assigned_ad.ad_id][category]['activatedNodes'] = 0

        for i in range(iterations):
            # calculate seed activation (users that click on ads)
            seeds_per_ad_id = {}  # seeds for ad_id, seeds for advertiser, dictionary with ad_id -> seed list
            seeds = {}
            time = datetime.now()
            seeds_per_ad_id = self.calculateSeeds(slates=slates, use_estimated_qualities=use_estimated_qualities)
            elapsed_time = datetime.now() - time
            # print(f'calculate seeds time: {elapsed_time}')
            for ad_id in seeds_per_ad_id.keys():  # keys are ad_ids
                # calculate how many nodes are activated by the given seeds
                total_seeds = []
                for category in range(constants.CATEGORIES):
                    for node in seeds_per_ad_id[ad_id][category]:
                        total_seeds.append(node)
                time = datetime.now()
                activated_nodes, node_estimated_activation_probabilities = self.monteCarloEstimation(seeds=total_seeds, iterations=1, activation_probabilities=estimated_activation_probabilities)
                elapsed_time = datetime.now() - time
                print(f'one monte carlo iteration takes {elapsed_time}')
                # print(estimated_activation_probabilities)
                # calculate average number of seeds and of activated nodes for every ad_id
                if ad_id not in avg_n_seeds_per_ad_id.keys():
                    avg_n_seeds_per_ad_id[ad_id] = {}
                if ad_id not in avg_active_nodes_per_ad_id.keys():
                    avg_active_nodes_per_ad_id[ad_id] = {}
                for category in constants.categories:
                    if category not in avg_n_seeds_per_ad_id[ad_id].keys():
                        avg_n_seeds_per_ad_id[ad_id][category] = 0
                    avg_n_seeds_per_ad_id[ad_id][category] += len(seeds_per_ad_id[ad_id][category])
                    if category not in avg_active_nodes_per_ad_id[ad_id].keys():
                        avg_active_nodes_per_ad_id[ad_id][category] = 0
                    avg_active_nodes_per_ad_id[ad_id][category] += activated_nodes[category]
        for ad_id in avg_n_seeds_per_ad_id.keys():
            for category in avg_n_seeds_per_ad_id[ad_id].keys():
                avg_n_seeds_per_ad_id[ad_id][category] = avg_n_seeds_per_ad_id[ad_id][category] / iterations
                avg_active_nodes_per_ad_id[ad_id][category] = avg_active_nodes_per_ad_id[ad_id][category] / iterations

        for ad_id in avg_n_seeds_per_ad_id.keys():
            for category in constants.categories:
                r[ad_id][category]['seeds'] = avg_n_seeds_per_ad_id[ad_id][category]
                r[ad_id][category]['activatedNodes'] = avg_active_nodes_per_ad_id[ad_id][category]
        return r

    def calculateSeeds(self, slates: List[List[Slot]], use_estimated_qualities=False):
        seeds_per_ad_id = {}  # seeds for ad_id, seeds for advertiser, dictionary with ad_id -> category -> seed list
        for slate in slates:
            for slot in slate:
                seeds_per_ad_id[slot.assigned_ad.ad_id] = {}
                for category in range(constants.CATEGORIES):
                    seeds_per_ad_id[slot.assigned_ad.ad_id][category] = []
        count_seeds = 0
        seeds = []
        for node in self.nodes:
            slate = slates[node.category]
            for position in slate:
                current_ad = position.assigned_ad
                if use_estimated_qualities:
                    quality = current_ad.estimated_quality
                else:
                    quality = current_ad.real_quality
                activation_probability = quality * constants.SLOT_VISIBILITY
                sample = random.random()
                if sample < activation_probability:  # if the node clicks the ad
                    seeds.append(node.id)
                    count_seeds += 1
                    # add this node as seed for the ad it clicked on
                    seeds_per_ad_id[position.assigned_ad.ad_id][node.category].append(node.id)
                    break

        count = 0
        for ad_id in seeds_per_ad_id.keys():
            for category in range(constants.CATEGORIES):
                count += len(seeds_per_ad_id[ad_id][category])
        assert count == count_seeds
        assert len(seeds) == count_seeds
        return seeds_per_ad_id

    def network_report(self):
        nodes_per_category = {}
        for category in range(constants.CATEGORIES):
            nodes_per_category[category] = 0
        for node in self.nodes:
            nodes_per_category[node.category] += 1
        return nodes_per_category
