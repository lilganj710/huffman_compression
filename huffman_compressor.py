from __future__ import annotations
import argparse
import pickle
from collections import Counter
import heapq
from dataclasses import dataclass
from functools import total_ordering
from typing import Any


@dataclass
@total_ordering
class TreeNode:
    '''Node in the binary tree used for Huffman encoding
    Only leaf nodes contain one of the characters'''
    total_count: int
    ch: str | None = None
    left: TreeNode | None = None
    right: TreeNode | None = None

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, TreeNode):
            return False
        return self.total_count == other.total_count

    def __lt__(self, other: TreeNode) -> bool:
        return self.total_count < other.total_count


def get_huffman_tree(char_counts: dict[str, int]) -> TreeNode:
    '''Use the greedy algo described below to get the Huffman encoding tree'''
    cur_roots = [TreeNode(count, ch) for ch, count in char_counts.items()]
    heapq.heapify(cur_roots)
    while len(cur_roots) > 1:
        smallest_group = heapq.heappop(cur_roots)
        next_smallest = heapq.heappop(cur_roots)
        parent_node = TreeNode(
            smallest_group.total_count + next_smallest.total_count)
        parent_node.left = smallest_group
        parent_node.right = next_smallest
        heapq.heappush(cur_roots, parent_node)
    return cur_roots[0]


def huffman_encode(original: str) -> tuple[dict[str, int], int]:
    '''Given the original text, apply Huffman encoding.
    Recall the greedy algo: given subtrees containing char counts of
        groups of chars, combine the two least common char counts into a
        single tree. Repeat until only 1 tree remaining
    This tree can then be traversed to get a bit encoding for each char

    Return a dict of (char, encoding) plus the overall encoding of the
    original text
        I considered using a bytes-like buffer here, but I think an
        int should be fine. Can use bit-shift operations'''
    char_counts = Counter(original)
    tree_root = get_huffman_tree(char_counts)
    print(f'{char_counts["X"]=}, {char_counts["t"]=}')
    print(f'{tree_root.total_count=}')
    return {}, 0


def main():
    '''Read filename from input, optionally specify compressed output fname'''
    parser = argparse.ArgumentParser()
    parser.add_argument('in_fname')
    parser.add_argument(
        '--out_fname', default='compressed_out.huf', required=False)
    args = parser.parse_args()
    with open(args.in_fname, encoding='utf-8') as f:
        code_table, compressed_output = huffman_encode(f.read())
    with open(args.out_fname, 'wb+') as f:
        pickle.dump([code_table, compressed_output], f)


if __name__ == '__main__':
    main()
