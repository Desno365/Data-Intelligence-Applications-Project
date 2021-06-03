import Network
import influenceEstimation

network = Network.Network(3, fc = True)
seeds = [0]
average_active_nodes, ground_truth_activations = network.calculateActivations(seeds)
print(network.adjacency_matrix)
print(average_active_nodes, ground_truth_activations)

estimated_average_active_nodes,estimated_activation_probabilities = network.monteCarloEstimation()
print(estimated_average_active_nodes, estimated_activation_probabilities)

error = network.evaluateError(ground_truth_activations, estimated_activation_probabilities)
print('error: ', error)