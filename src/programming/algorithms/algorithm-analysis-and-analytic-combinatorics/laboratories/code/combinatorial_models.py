"""Combinatorial enumeration and elementary random-structure statistics."""
from __future__ import annotations
from collections import Counter
from functools import lru_cache
from itertools import permutations
from random import Random


def catalan(n: int) -> int:
    if n < 0:
        raise ValueError("nonnegative n required")
    vals = [1]
    for k in range(1, n+1):
        vals.append(sum(vals[i]*vals[k-1-i] for i in range(k)))
    return vals[n]


@lru_cache(maxsize=None)
def ordered_binary_tree_shapes(n: int) -> tuple:
    """Shapes: None is empty, (left,right) is a node. Safe only for small n."""
    if n == 0:
        return (None,)
    return tuple((a, b) for k in range(n)
                 for a in ordered_binary_tree_shapes(k)
                 for b in ordered_binary_tree_shapes(n-1-k))


def shape_from_insertions(keys: tuple[int, ...]):
    def insert(tree, key):
        if tree is None:
            return (key, None, None)
        root, left, right = tree
        if key < root:
            return (root, insert(left, key), right)
        if key > root:
            return (root, left, insert(right, key))
        return tree
    tree = None
    for k in keys:
        tree = insert(tree, k)
    def unlabel(tree):
        return None if tree is None else (unlabel(tree[1]), unlabel(tree[2]))
    return unlabel(tree)


def internal_path_length(tree, depth=0):
    if tree is None:
        return 0
    return depth + internal_path_length(tree[0], depth+1) + internal_path_length(tree[1], depth+1)


def bst_shape_distribution(n: int) -> Counter:
    if n > 8:
        raise ValueError("factorial exhaustive enumeration limited to n<=8")
    return Counter(shape_from_insertions(p) for p in permutations(range(n)))


def trie_statistics(keys: list[str]) -> tuple[int, list[int]]:
    """Return allocated nodes (including root) and character visits per lookup."""
    root: dict = {}
    node_count = 1
    for key in keys:
        node = root
        for ch in key:
            if ch not in node:
                node[ch] = {}
                node_count += 1
            node = node[ch]
    visits = []
    for key in keys:
        node, seen = root, 0
        for ch in key:
            seen += 1
            node = node[ch]
        visits.append(seen)
    return node_count, visits


def bucket_trial(m: int, b: int, seed: int) -> tuple[list[int], int]:
    if m < 0 or b < 1:
        raise ValueError("m must be nonnegative and b positive")
    rng = Random(seed)
    counts = [0] * b
    for _ in range(m):
        counts[rng.randrange(b)] += 1
    return counts, sum(x*(x-1)//2 for x in counts)
