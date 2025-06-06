from caspailleur import implication_bases as impbas
from caspailleur import mine_equivalence_classes as mec
from caspailleur import io
from bitarray import frozenbitarray as fbarray


def test_list_proper_premises_via_keys():
    n_attrs = 5
    intents = [set(), {0}, {2}, {3}, {0, 2}, {0, 3}, {1, 2}, {1, 2, 3}, {0, 1, 2, 3, 4}]
    intents = list(io.isets2bas(intents, n_attrs))
    keys_to_intents = mec.list_keys(intents)

    pprems_true = list(io.isets2bas([{1}, {4}, {2, 3}, {0, 1}, {0, 2, 3}], 5))

    pprems = dict(impbas.iter_proper_premises_via_keys(intents, keys_to_intents))
    assert set(pprems) == set(pprems_true)


def test_list_pseudo_intents_via_keys():
    pintents_true = [{1}, {0, 1, 2}, {2, 3}, {4}]
    intents = [set(), {0}, {2}, {3}, {0, 2}, {0, 3}, {1, 2}, {1, 2, 3}, {0, 1, 2, 3, 4}]
    keys_intent_map = [
        ([], 0), ([0], 1), ([1], 6), ([2], 2), ([3], 3), ([4], 8),
        ([0, 1], 8), ([0, 2], 4), ([0, 3], 5), ([1, 3], 7), ([2, 3], 7), ([0, 2, 3], 8)
    ]
    keys_intent_map = dict([(frozenset(k), v) for k, v in keys_intent_map])

    intents = list(io.isets2bas(intents, 5))
    pintents_true = list(io.isets2bas(pintents_true, 5))
    keys_intent_map = dict(zip(io.isets2bas(keys_intent_map.keys(), 5), keys_intent_map.values()))

    pintents = impbas.list_pseudo_intents_via_keys(keys_intent_map.items(), intents)
    assert {pintent for pintent, _ in pintents} == set(pintents_true)


def test_subset_saturate():
    intents = [fbarray('0000'), fbarray('0101'), fbarray('1111')]
    implications = [(fbarray('0100'), 1), (fbarray('0001'), 2)]
    saturated = impbas.subset_saturate(fbarray('0110'), implications, intents)
    assert saturated == fbarray('0111')

    saturated = impbas.subset_saturate(fbarray('0101'), implications, intents)
    assert saturated == fbarray('1111')
