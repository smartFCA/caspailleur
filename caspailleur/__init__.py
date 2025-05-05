from .implication_bases import iter_proper_premises_via_keys, list_pseudo_intents_via_keys
from .mine_equivalence_classes import list_intents_via_LCM, list_keys, list_passkeys, list_stable_extents_via_gsofia
from .order import sort_intents_inclusion, inverse_order
from .indices import linearity_index, distributivity_index

from .api import iter_descriptions, mine_descriptions, mine_concepts, mine_implications

__version__ = '0.2.2'
