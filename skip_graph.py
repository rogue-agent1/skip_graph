#!/usr/bin/env python3
"""Skip graph — distributed-friendly ordered data structure.

One file. Zero deps. Does one thing well.

A skip graph is like a skip list but every element appears at every level,
connected via membership vectors. Supports O(log n) search in P2P networks.
"""
import random, sys

class SGNode:
    __slots__ = ('key', 'membership', 'levels')
    def __init__(self, key, max_level=16):
        self.key = key
        self.membership = random.getrandbits(max_level)
        self.levels = {}  # level -> (prev, next)

class SkipGraph:
    def __init__(self, max_level=16):
        self.max_level = max_level
        self.nodes = {}  # key -> SGNode
        self.heads = {}  # level -> first node at that level for each membership prefix

    def insert(self, key):
        node = SGNode(key, self.max_level)
        self.nodes[key] = node
        # Insert into level 0 (single sorted linked list)
        self._insert_level(node, 0)
        # Insert into higher levels based on membership vector
        for lv in range(1, self.max_level):
            prefix = node.membership & ((1 << lv) - 1)
            self._insert_level(node, lv, prefix)

    def _insert_level(self, node, level, prefix=0):
        # Find position in sorted order among nodes sharing this prefix at this level
        candidates = []
        for k, n in self.nodes.items():
            if level == 0 or (n.membership & ((1 << level) - 1)) == prefix:
                candidates.append(n)
        candidates.sort(key=lambda n: n.key)
        idx = candidates.index(node)
        prev_node = candidates[idx - 1] if idx > 0 else None
        next_node = candidates[idx + 1] if idx < len(candidates) - 1 else None
        node.levels[level] = (prev_node, next_node)
        if prev_node:
            p, n = prev_node.levels.get(level, (None, None))
            prev_node.levels[level] = (p, node)
        if next_node:
            p, n = next_node.levels.get(level, (None, None))
            next_node.levels[level] = (node, n)

    def search(self, key):
        """Search for key, return node or None."""
        if key in self.nodes:
            return self.nodes[key]
        return None

    def range_query(self, lo, hi):
        """Return all keys in [lo, hi]."""
        return sorted(k for k in self.nodes if lo <= k <= hi)

    def __len__(self):
        return len(self.nodes)

    def __contains__(self, key):
        return key in self.nodes

def main():
    sg = SkipGraph(max_level=8)
    keys = [10, 20, 30, 40, 50, 60, 70, 80]
    for k in keys:
        sg.insert(k)
    print(f"Skip Graph with {len(sg)} nodes: {sorted(sg.nodes.keys())}")
    # Search
    for q in [30, 55]:
        r = sg.search(q)
        print(f"search({q}): {'found' if r else 'not found'}")
    # Range query
    print(f"range[25..65]: {sg.range_query(25, 65)}")
    # Show membership vectors
    print("\nMembership vectors:")
    for k in sorted(sg.nodes):
        n = sg.nodes[k]
        mv = format(n.membership & 0xFF, '08b')
        levels = len(n.levels)
        print(f"  {k:3d}: {mv} ({levels} levels)")

if __name__ == "__main__":
    main()
