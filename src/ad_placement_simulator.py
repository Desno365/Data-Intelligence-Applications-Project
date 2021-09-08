from typing import List

from src.ad import Ad
from src.constants import CATEGORIES
from src.slot import Slot


class AdPlacementSimulator:

    @staticmethod
    # ads = the list of ads available, every ad comes from an advertiser.
    # slates = the list of slates, one slate per category (a slate is a list of slots).
    def simulate_ad_placement(ads: List[Ad], slates: List[List[Slot]], iterations: int) -> None:

        # The auction must be simulated for each category.
        for x in range(CATEGORIES):
            # Per ogni categoria simulo la auction.
            # Auction ha bisogno di bid e quality di tutti gli advertiser per quella categoria.
            # Auction ha bisogno dello slate per quella categoria.
            # Attenzione che gli slot prominenace sono uguali per tutti gli slate.
            # La auction poi restituisce lo slate dato in input ma con pubblicità assegnate ad ogni slot e il prezzo per ogni slot.

            # Adesso abbiamo uno slate completo per la categoria.
            # Salviamo lo slate in una lista, per avere poi una lista completa con tutti gli slate per tutte le categorie.
            print("")

        # Monte Carlo:
        # Input: lista di slate con pubblicità assegnate e prezzi.
        # Ouput: dictionary che per ogni ad_id (univoco per advertiser) specifica numero medio di seed e nodi attivati.
        # Nota quindi: dividere per ad_id è equivalente a dividere per advertiser.
        # return dictionary