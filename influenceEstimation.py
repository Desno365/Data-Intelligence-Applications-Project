import Network
import numpy as np

def binary_strings(depth):
  if depth < 1:
    print('no')
    return
  if depth == 1:
    return ['0', '1']
  result = []
  for i in binary_strings(depth-1):
    result.append('0' + i)
    result.append('1' + i)
  result.sort()
  return result

def calculateActivations(nodes, adjacency_matrix):
    #enumerate all live edge graphs to calculate node activation probability
    #takes 1 minute to compute with a fully connected graph (with no self loops) with 5 nodes
    asdf = 0
    mask_list = binary_strings(int(np.sum(adjacency_matrix)))
    print(len(mask_list))
    for a in nodes:
      a.z = 0
      a.activation_probability = 0
    progress_index = 0
    for i in mask_list:
      progress_index += 1
      if progress_index%100000 == 0:
        print(progress_index)
      live = np.zeros((Network.n,Network.n))
      index = -1
      for j in range(Network.n):
        for jj in range(Network.n):
          if adjacency_matrix[j][jj] == 1:
            index += 1
            if i[index] == '1':
              # print(index)
              live[j][jj] = adjacency_matrix[j][jj]
      active_nodes = Network.calculate_activated_nodes([0], live)
      for node_index in active_nodes:
        nodes[node_index].activation_probability += 1/len(mask_list)

    ground_truth_activation_probabilities = []
    for a in nodes:
      ground_truth_activation_probabilities.append(a.activation_probability)
      print(a.activation_probability)

def monteCarloEstimation(iterations, seeds, ground_truth_activation_probabilities):
    # monte carlo sampling
    # iterations = 5

    # seeds = [0]
    average_active_nodes = 0
    for i in Network.nodes:
        i.z = 0
        i.activation_probability = 0
    for i in range(iterations):
        if i % 100000 == 0:
            print('progress: ', i)
        # active_nodes = []
        # print(active_nodes)
        live, p = Network.generate_live_edge_graph()
        active_nodes = Network.calculate_activated_nodes(seeds, live)
        active_nodes.sort()
        if i == 0:
            average_active_nodes = len(active_nodes)
        else:
            average_active_nodes = (average_active_nodes * (i) + len(active_nodes)) / (i + 1)
        for nod in active_nodes:
            Network.nodes[nod].z += 1

    error = 0
    for asd in range(len(Network.nodes)):
        print('number of activations: ', Network.nodes[asd].z, '\nactivation probability: ', Network.nodes[asd].z / iterations)
        if ground_truth_activation_probabilities:
            error += (ground_truth_activation_probabilities[asd] - Network.nodes[asd].z / iterations) ** 2
    if ground_truth_activation_probabilities:
        print('\naverage number of active nodes: ', average_active_nodes, '\ntotal squared error: ', error)
