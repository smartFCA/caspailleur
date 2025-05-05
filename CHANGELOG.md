# Changelog

## v0.2.2

### Fixes
Fix the bug with mining all implications instead of the stable ones (and vice versa) in `csp.mine_implications`.

Fix wrong references to `csp.api.MINE_CONCEPTS_COLUMN` and `csp.api.MINE_IMPLICATIONS_COLUMN` within `csp.api` module.

Update the computations of _conclusion_ column within `csp.mine_implications` function. 
Now _conclusion_ = _conclusion_full_ - subset-saturated(_premise_).
Before, the conclusion was computed as the difference of _conclusion_full_ and fully-saturated _premise_.
So might ended up being empty for some implications of Proper premise basis
(because the premises of such basis are "proper" in terms of subset-saturation and but the actual correct saturation).


### New functionality (frontend version)

Improvements for `csp.mine_concepts` function:
- Add _"new_extent"_ and _"new_intent"_ columns as options for `to_compute` parameter: 
<br>They show the reduced labeling of extents and intents. 
That is, what objects can be found in the extent of a concept that cannot be found in the extent of its any subconcept.
And what attributes can be found in the intent of a concept but not in the intent of its any superconcept.
- Add `sort_by_descending` parameter:
<br>This parameter sorts concepts (and their indices) in the output table by 
the support, delta-stability, size of the intent or size of the extent of a concept.
It allows to put the most frequent or the most stable concepts at the top of the dataframe, 
thus simplifying their visualisation.
- Remove "_proper_premises_" and "_pseudo_intents_" from the default value of `to_compute` parameter.
<br>The computation of _pseudo_intents_ often requires a lot of time, 
much more than the computation of any other column of the output dataframe. So it is better to be optional.
In any case, both _proper_premises_ and _pseudo_intents_ relate more to the idea of mining implications 
than that of mining concepts.
 

Improvements for `csp.mine_implications` function:
- Change the default values of `min_support` parameter to 1. 
Now, the function would not compute the abundance of controversal implications by default.
- Add "_delta_stability_" column to the output of the function.
<br>This parameter is not that important for analysing implications. However, it can still help ranking the implications.


### New functionality (backend version)

Implement function `csp.mine_equivalence_classes.iter_minimal_broad_clusterings_via_pyramidal_search(...)`
<br>that computes minimal broad non-overlapping clusterings with so-called "pyramidal search" 
(also known as "reverse preorder traversal"").
So the function give preference to clusterings based on the order in which the individual clusters appear in the input: 
the smaller is the index of a cluster, the earlier it will be tested for clustering.

### Refactoring

Add more structure to the code of  `csp.mine_concepts` function. Now it should be a bit more understandable.

### Auxiliary

Transfer GitHub repository for the package to smartFCA organisation account: https://github.com/smartFCA.


## v0.2.1 

### Fixes
Update the code to match the new syntaxis of `bitarray` package
(mostly renaming `ba.itersearch(...)` functions into `ba.search(...)` ).

Plus minor bugfixes.

### New functionality (backend version)

Add `support_surplus` parameter into  `iter_keys_of_intent` function.
Now one can find **∆-equivalent keys of an intent**,
that are minimal descriptions that describe the same objects as the intent 
plus at most `support_surplus` more additional objects.
The function in question is called `csp.mine_equivalence_classes.iter_keys_of_intent(...)`.

Implement **MRG-Exp** algorithm (Carpathia-G-Rare) for **Minimal Rare Itemset** mining.
A minimal rare itemset (or a minimal rare description) is a minimal subset of attributes
    that describes less than (or equal to) `max_support` objects.
The function is called `csp.mine_equivalence_classes.iter_minimal_rare_itemsets_via_mrgexp(...)`.

Implement **Clustering via MRG-Exp** algorithm for **Minimal Broad Clustering** mining.
A minimal broad clustering is a minimal subset of attributes that, together,
cover more than (or equal to) `min_coverage` objects.
The function is called `csp.mine_equivalence_classes.iter_minimal_broad_clusterings_via_mrgexp(...)`.

Add **level-wise equivalence class iteration**.
The level-wise optimisation is supposed to fasten up the iteration of the equivalence class.
However, currently, it only fastens up the iteration through the equivalence class of the maximal description
(that often describes no objects).   
The function is called `csp.mine_equivalence_classes.iter_equivalence_class_levelwise(...)`.
The older and more straightforward iteration procedure is implemented in 
`csp.mine_equivalence_classes.iter_equivalence_class(...)`.

### New functionality (frontend version)
Now `caspailleur` also downloads the context's metadata together with the context itself.
The function name stays the same: `csp.io.from_fca_repo(...)`.