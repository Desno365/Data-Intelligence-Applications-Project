from typing import Dict, List

from src.slot import Slot

SocialInfluenceType = Dict[int, Dict[int, Dict[str, float]]]
SlateType = List[Slot]
ActivationProbabilitiesType = List[List[float]] or None
