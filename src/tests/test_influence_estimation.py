import Network
import time
from matplotlib import pyplot as plt
import Publisher
import ad
import auction.vcg_auction



# input n_nodes (number of nodes in the network)
# fc (the network is fully connected (self loops excluded))
import slot


def test_enumeration_estimation(n_nodes=3, fc=True, seeds=[0]):
    start_time = time.time()
    print('Run full enumeration and monte carlo, calculate error of estimation\n')
    network = Network.Network(n_nodes, fc)
    average_active_nodes, ground_truth_activations = network.calculateActivations(seeds)
    print('Network adjacency matrix:\n', network.adjacency_matrix)
    print('Average number of activated nodes and node activation probabilities (true values):\n', average_active_nodes, ground_truth_activations)

    estimated_average_active_nodes, estimated_activation_probabilities = network.monteCarloEstimation()
    print('Average number of activated nodes and node activation probabilities (estimated values):\n', estimated_average_active_nodes, estimated_activation_probabilities)

    error = network.evaluateError(ground_truth_activations, estimated_activation_probabilities)
    print('error on node activation probabilities: ', error)
    print('Execution time: ', time.time() - start_time, ' seconds')


def test_monte_carlo_speed():
    print('Time to execute 100 iteration of monte carlo on a fully connected network')
    n = []
    t = []
    for n_nodes in range(1, 1000, 10):
        print('testing with ', n_nodes, ' nodes')
        network = Network.Network(n_nodes, True)
        start_time = time.time()
        estimated_average_active_nodes, estimated_activation_probabilities = network.monteCarloEstimation(iterations=10)
        run_time = time.time() - start_time
        # print(n_nodes, ' nodes, ', time.time() - start_time, ' seconds')
        n.append(n_nodes)
        t.append(run_time)
    plt.plot(n, t)
    plt.show()


def test_monte_carlo():
    network = Network.Network(1, True)
    print(network.adjacency_matrix)
    _ = network.monteCarloEstimation(iterations=1)
    # for nod in active_nodes:
    #     network.nodes[nod].z += 1

def test_monte_carlo_with_publisher():
    network = Network.Network(100, False)
    publisher = Publisher.Publisher(network)

    ad_list = [ad.Ad(ad_id=i, ad_quality=0.5, ad_value=1) for i in range(10)]
    # print(len(ad_list))
    # publisher.generate_auctions(ad_list)
    # publisher.play_round(category=0, advertiser=0)

    # publisher.estimate_auction_effect(category=0, advertiser=0)


# test_monte_carlo()
# test_enumeration_estimation()
# test_monte_carlo_speed()
test_monte_carlo_with_publisher()

def test_best_ads():
    ad_list = [ad.Ad(ad_id=i, ad_quality=0.5, ad_value=1) for i in range(10)]
    slate = [slot.Slot(i, 0.5) for i in range(6)]
    a = auction.vcg_auction.VCGAuction(ad_list, slate)
    print(a.get_best_ads(a.available_ads))
    # a.compute_x_a(a.available_ads, slate, 1)

# test_best_ads()