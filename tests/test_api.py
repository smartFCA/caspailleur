import pandas as pd

from caspailleur import api


def assert_df_equality(df1: pd.DataFrame, df2: pd.DataFrame):
    assert list(df1.index) == list(df2.index)
    assert list(df1.columns) == list(df2.columns)
    for f in df1:
        assert list(df1[f]) == list(df2[f]), f"Problematic column: {f}"


def test_mine_descriptions():
    data = {'g1': ['a', 'b'], 'g2': ['b', 'c']}

    descriptions_data_true = pd.DataFrame({
        'description': [set(), {'a'}, {'b'}, {'c'}, {'a', 'b'}, {'a', 'c'}, {'b', 'c'}, {'a', 'b', 'c'}],
        'extent': [{'g1', 'g2'}, {'g1'}, {'g1', 'g2'}, {'g2'}, {'g1'}, set(), {'g2'}, set()],
        'intent': [{'b'}, {'a', 'b'}, {'b'}, {'b', 'c'}, {'a', 'b'}, {'a', 'b', 'c'}, {'b', 'c'}, {'a', 'b', 'c'}],
        'support': [2, 1, 2, 1, 1, 0, 1, 0],
        'delta_stability': [0, 0, 1, 0, 1, 0, 1, 0],
        'is_closed': [False, False, True, False, True, False, True, True],
        'is_key': [True, True, False, True, False, True, False, False],
        'is_passkey': [True, True, False, True, False, True, False, False],
        'is_proper_premise': [True, False, False, False, False, False, False, False],
        'is_pseudo_intent': [True, False, False, False, False, False, False, False]
    })
    descriptions_data = api.mine_descriptions(data, to_compute='all')
    assert_df_equality(descriptions_data, descriptions_data_true)

    # test min_support threshold
    for min_supp in [1, 2]:
        freq_df_true = descriptions_data_true[descriptions_data_true['support'] >= min_supp].reset_index(drop=True)
        freq_df = api.mine_descriptions(data, min_support=min_supp, to_compute='all')
        assert_df_equality(freq_df, freq_df_true)

    for min_supp in [0.5, 1.0]:
        freq_df_true = descriptions_data_true[descriptions_data_true['support']/len(data) >= min_supp].reset_index(drop=True)
        freq_df = api.mine_descriptions(data, min_support=min_supp, to_compute='all')
        assert_df_equality(freq_df, freq_df_true)


def test_iter_descriptions():
    data = {'g1': ['a', 'b'], 'g2': ['b', 'c']}

    descriptions_data = list(api.iter_descriptions(data))
    assert_df_equality(pd.DataFrame(descriptions_data), api.mine_descriptions(data))

    to_compute = ['description', 'extent', 'intent', 'is_proper_premise', 'is_pseudo_intent', 'delta_stability']
    descriptions_data = list(api.iter_descriptions(data, to_compute=to_compute))
    assert_df_equality(pd.DataFrame(descriptions_data), api.mine_descriptions(data, to_compute='all')[to_compute])


def test_mine_concepts():
    data = {'g1': ['a', 'b'], 'g2': ['b', 'c']}

    concepts_df_true = pd.DataFrame({
        'extent': [{'g1', 'g2'}, {'g1'}, {'g2'}, set()],
        'intent': [{'b'}, {'a', 'b'}, {'b', 'c'}, {'a', 'b', 'c'}],
        'new_extent': [set(), {'g1'}, {'g2'}, set()],
        'new_intent': [{'b'}, {'a'}, {'c'}, set()],
        'support': [2, 1, 1, 0],
        'delta_stability': [1, 1, 1, 0],
        'keys': [[set()], [{'a'}], [{'c'}], [{'a','c'}]],
        'passkeys': [[set()], [{'a'}], [{'c'}], [{'a', 'c'}]],
        'proper_premises': [[set()], [], [], []],
        'pseudo_intents': [[set()], [], [], []],
        'previous_concepts': [{1, 2}, {3}, {3}, set()],
        'next_concepts': [set(), {0}, {0}, {1, 2}],
        'sub_concepts': [{1, 2, 3}, {3}, {3}, set()],
        'super_concepts': [set(), {0}, {0}, {0, 1, 2}],
    })
    concepts_df = api.mine_concepts(data)
    assert_df_equality(concepts_df, concepts_df_true.drop(columns=['proper_premises', 'pseudo_intents']))

    concepts_df = api.mine_concepts(data, to_compute='all')
    assert_df_equality(concepts_df, concepts_df_true)

    stable_concepts_df_true = concepts_df_true[:3]
    for f in ['previous_concepts', 'next_concepts', 'sub_concepts', 'super_concepts']:
        stable_concepts_df_true[f] = stable_concepts_df_true[f] - {3}

    stable_concepts_df = api.mine_concepts(data, to_compute='all', min_delta_stability=1)
    assert_df_equality(stable_concepts_df, stable_concepts_df_true)

    stable_concepts_df = api.mine_concepts(data, to_compute='all', n_stable_concepts=3)
    assert_df_equality(stable_concepts_df, stable_concepts_df_true)

    stable_concepts_df = api.mine_concepts(data, to_compute='all', min_delta_stability=1, n_stable_concepts=3)
    assert_df_equality(stable_concepts_df, stable_concepts_df_true)

    ################
    # Test sorting #
    ################
    stable_concepts_df = api.mine_concepts(data, sort_by_descending='extent.size')
    assert sorted(stable_concepts_df['extent'].map(len), reverse=True) == list(stable_concepts_df['extent'].map(len))
    stable_concepts_df = api.mine_concepts(data, sort_by_descending='intent.size')
    assert sorted(stable_concepts_df['intent'].map(len), reverse=True) == list(stable_concepts_df['intent'].map(len))
    stable_concepts_df = api.mine_concepts(data, sort_by_descending='support')
    assert sorted(stable_concepts_df['support'], reverse=True) == list(stable_concepts_df['support'])
    stable_concepts_df = api.mine_concepts(data, sort_by_descending='delta_stability')
    assert sorted(stable_concepts_df['delta_stability'], reverse=True) == list(stable_concepts_df['delta_stability'])


def test_mine_implications():
    """
    data = {'g1': ['a', 'b'], 'g2': ['b', 'c']}

    impls_df_true = pd.DataFrame({
        'premise': [set()],
        'conclusion': [{'b'}],
        'conclusion_full': [{'b'}],
        'extent': [{'g1', 'g2'}],
        'support': 2
    })

    impls_df = api.mine_implications(data, 'Proper Premise')
    assert_df_equality(impls_df, impls_df_true)

    impls_df = api.mine_implications(data, 'Pseudo-Intent')
    assert_df_equality(impls_df, impls_df_true)

    for basis_name in ['Duquenne-Guigues', 'Minimum', 'Canonical']:
        impls_df = api.mine_implications(data, basis_name)
        assert_df_equality(impls_df, impls_df_true)

    for basis_name in ['Canonical Direct', 'Karell']:
        impls_df = api.mine_implications(data, basis_name)
        assert_df_equality(impls_df, impls_df_true)

    impls_df_true_unit = pd.DataFrame({
        'premise': [set()],
        'conclusion': ['b'],
        'conclusion_full': [{'b'}],
        'extent': [{'g1', 'g2'}],
        'support': 2
    })
    impls_df = api.mine_implications(data, 'Proper Premise', unit_base=True)
    assert_df_equality(impls_df, impls_df_true_unit)

    impls_df = api.mine_implications(data, 'Proper Premise', unit_base=True,
                                     to_compute=['premise', 'conclusion', 'extent'])
    assert_df_equality(impls_df, impls_df_true_unit[['premise', 'conclusion', 'extent']])

    # TODO: Add refined tests for implication (and especially unit) base
    """
    # Recreate NewZealand context from FCA context repository
    data = {
        'Stewart Island': ['Hiking', 'Observing Nature', 'Sightseeing Flights'],
        'Te Anau': ['Hiking', 'Observing Nature', 'Sightseeing Flights', 'Jet Boating'],
        'Oamaru': ['Hiking', 'Observing Nature'],
        'Queenstown': ['Hiking', 'Sightseeing Flights', 'Jet Boating', 'Wildwater Rafting']
    }
    for original_object, duplicates in {
        'Stewart Island': ['Fjordland NP', 'Invercargill', 'Milford Sound', 'MT. Aspiring NP', 'Dunedin'],
        'Oamaru': ['Otago Peninsula', 'Haast', 'Catlins'],
        'Queenstown': ['Wanaka']
    }.items():
        for duplicate in duplicates:
            data[duplicate] = data[original_object]

    # Test (stable) proper premises on NewZealand data
    impls_df_true = pd.DataFrame({
        'premise': [set(), {'Jet Boating'}, {'Wildwater Rafting'}],
        'conclusion': [{'Hiking'}, {'Sightseeing Flights'}, {'Jet Boating', 'Sightseeing Flights'}],
        'conclusion_full': [{'Hiking'}, {'Jet Boating', 'Hiking', 'Sightseeing Flights'},
                            {'Wildwater Rafting', 'Jet Boating', 'Hiking', 'Sightseeing Flights'}],
        'extent': [{
            'Stewart Island', 'Te Anau', 'Oamaru', 'Queenstown', 'Fjordland NP',
            'Invercargill', 'Milford Sound', 'MT. Aspiring NP', 'Dunedin', 'Otago Peninsula',
            'Haast', 'Catlins', 'Wanaka'},
            {'Queenstown', 'Wanaka', 'Te Anau'},
            {'Queenstown', 'Wanaka'}
        ]
    })
    impls_df = api.mine_implications(data, 'Proper Premise',
                                     to_compute=['premise', 'conclusion', 'conclusion_full', 'extent'])
    assert_df_equality(impls_df, impls_df_true)

    impls_df = api.mine_implications(data, 'Proper Premise', min_delta_stability=2,
                                     to_compute=['premise', 'conclusion', 'conclusion_full', 'extent'])
    assert_df_equality(impls_df, impls_df_true.iloc[[0, 2]].reset_index(drop=True))

    # Test (stable) pseudo-intents on NewZealand data
    impls_df_true = pd.DataFrame({
        'premise': [set(), {'Hiking', 'Wildwater Rafting'}, {'Hiking', "Jet Boating"}],
        'conclusion': [{'Hiking'}, {'Jet Boating', 'Sightseeing Flights'}, {'Sightseeing Flights'}],
        'conclusion_full': [{'Hiking'}, {'Wildwater Rafting', 'Jet Boating', 'Hiking', 'Sightseeing Flights'},
                            {'Jet Boating', 'Hiking', 'Sightseeing Flights'}],
        'extent': [{
            'Stewart Island', 'Te Anau', 'Oamaru', 'Queenstown', 'Fjordland NP',
            'Invercargill', 'Milford Sound', 'MT. Aspiring NP', 'Dunedin', 'Otago Peninsula',
            'Haast', 'Catlins', 'Wanaka'},
            {'Queenstown', 'Wanaka'},
            {'Queenstown', 'Wanaka', 'Te Anau'},
        ]
    })
    impls_df = api.mine_implications(data, 'Pseudo-Intent',
                                     to_compute=['premise', 'conclusion', 'conclusion_full', 'extent'])
    assert_df_equality(impls_df, impls_df_true)

    impls_df = api.mine_implications(data, 'Pseudo-Intent', min_delta_stability=2,
                                     to_compute=['premise', 'conclusion', 'conclusion_full', 'extent'])
    assert_df_equality(impls_df, impls_df_true.iloc[[0, 1]].reset_index(drop=True))

    # Test for fixing the bug I have faced in "https://mdaquin.github.io/d/recipes_ing.csv" dataset.
    # (the dataset got updated during the fix of the bug)
    # 'Conclusion' column was computed based using pseudo-intents.
    # Because of that, some conclusions of Proper-Premise basis were empty.
    # Now, conclusions of implications are computed with
    itemsets = [
        {2, 3, 4}, {1, 2, 3}, {2}, {2, 3}, {1, 3}, set(), {1, 2, 4}, {3}, {1, 2}, {1, 2, 3, 4},
        {2, 4}, {4}, {1}, {0, 2}, {1, 4}, {1, 3, 4}, {3, 4}, {0, 1, 2, 3, 4}, {0}, {0, 2, 3},
        {0, 1, 2, 4}, {0, 4}
    ]
    impls_df = api.mine_implications(itemsets, 'Proper Premise', to_compute=['conclusion', 'support', 'delta_stability'])
    assert (impls_df['conclusion'].map(len) > 0).all()
    assert list(impls_df['support']) == [2, 2, 2, 1]
    assert list(impls_df['delta_stability']) == [1, 1, 1, 1]
