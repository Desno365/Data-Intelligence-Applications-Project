from src import constants, network
from src.advertiser.greedy_learning_advertiser import GreedyLearningAdvertiser
from src.advertiser.stochastic_stationary_advertiser import StochasticStationaryAdvertiser
from src.utils import Utils


# ################ Constants. ################ #
NUMBER_OF_STOCHASTIC_ADVERTISERS = constants.SLATE_DIMENSION + 1

# ################ Prepare context: Network. ################ #
network_instance = network.Network(constants.number_of_nodes, False)


# ################ Print slates. ################ #
print("Slates:")
for slate in constants.slates:
    Utils.print_array(slate)


# ################ Prepare context: Advertisers. ################ #
advertisers = [StochasticStationaryAdvertiser(ad_real_qualities=None) for _ in range(NUMBER_OF_STOCHASTIC_ADVERTISERS)]
greedy_learner = GreedyLearningAdvertiser(network=network_instance, use_estimated_activations=False,
                                          ad_real_qualities=[0.8 for _ in range(constants.CATEGORIES)], ad_value=1)
greedy_learner.set_rival_ads(rival_ads=[advertiser.ad for advertiser in advertisers])
greedy_learner.set_slates(slates=constants.slates)
advertisers.append(greedy_learner)


# ################ Print ads. ################ #
print("Ads:")
for advertiser in advertisers:
    print('ad id', advertiser.id, 'bids', advertiser.ad.bids)
for advertiser in advertisers:
    print('ad id', advertiser.id, 'qualities', advertiser.ad.estimated_qualities)


# ################ Run experiment. ################ #
print('starting experiment')
greedy_ad = greedy_learner.participate_real_auction()
print('experiment over')


# ################ Plot result. ################ #
greedy_learner.plot_gain_history_in_single_day()
