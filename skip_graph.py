#!/usr/bin/env python3
"""Skip Graph — distributed-friendly searchable overlay network."""
import random, sys

class SGNode:
    def __init__(self, key):
        self.key = key
        self.membership = ''.join(random.choice('01') for _ in range(16))
        self.neighbors = {}  # level -> (left, right)
    def __repr__(self): return f"SGNode({self.key})"

class SkipGraph:
    def __init__(self):
        self.nodes = {}
    def insert(self, key):
        node = SGNode(key)
        self.nodes[key] = node
        self._rebuild()
        return node
    def _rebuild(self):
        keys = sorted(self.nodes)
        for level in range(16):
            groups = {}
            for k in keys:
                prefix = self.nodes[k].membership[:level+1]
                groups.setdefault(prefix, []).append(k)
            for prefix, members in groups.items():
                for i, k in enumerate(members):
                    left = members[i-1] if i > 0 else None
                    right = members[i+1] if i < len(members)-1 else None
                    self.nodes[k].neighbors[level] = (left, right)
    def search(self, key):
        if key in self.nodes: return self.nodes[key]
        if not self.nodes: return None
        current = self.nodes[min(self.nodes)]
        for level in range(15, -1, -1):
            while level in current.neighbors:
                _, right = current.neighbors[level]
                if right and self.nodes[right].key <= key:
                    current = self.nodes[right]
                else: break
        return current
    def range_query(self, lo, hi):
        result = []
        start = self.search(lo)
        if not start: return result
        current = start
        while current and current.key <= hi:
            if current.key >= lo: result.append(current.key)
            if 0 in current.neighbors:
                _, right = current.neighbors[0]
                current = self.nodes[right] if right else None
            else: break
        return result

if __name__ == "__main__":
    sg = SkipGraph()
    for v in [10, 20, 30, 40, 50, 15, 25, 35]: sg.insert(v)
    print(f"Search 25: {sg.search(25)}")
    print(f"Range [15,35]: {sg.range_query(15, 35)}")
    print(f"Total nodes: {len(sg.nodes)}")
