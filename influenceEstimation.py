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
