from __future__ import annotations
import argparse
import pickle
from collections import Counter
import heapq
from dataclasses import dataclass
from functools import total_ordering
from typing import Any
from io import BytesIO


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


def get_prefix_code_table(tree_root: TreeNode) -> dict[str, bytes]:
    '''Do a DFS on the Huffman binary tree, where moving left adds a 0 bit,
    moving right adds a 1 bit. Use this to get the prefix code for each char'''
    prefix_code_table: dict[str, bytes] = {}
    cur_prefix = 0

    def traverse_from(cur_node: TreeNode) -> None:
        '''Recursively traverse from cur_node. If cur_node is a leaf,
        then save the cur_prefix in the prefix_code_table'''
        nonlocal cur_prefix
        if cur_node.left is None and cur_node.right is None:
            if cur_node.ch is None:
                raise ValueError(f'{cur_node=} leaf, but no char')
            num_bytes, remainder = divmod(cur_prefix.bit_length(), 8)
            num_bytes += int(remainder)
            num_bytes = max(num_bytes, 1)
            prefix_code_table[cur_node.ch] = cur_prefix.to_bytes(
                num_bytes, byteorder='big', signed=False)
        if cur_node.left is not None:
            cur_prefix = (cur_prefix << 1) | 0
            traverse_from(cur_node.left)
            cur_prefix = cur_prefix >> 1
        if cur_node.right is not None:
            cur_prefix = (cur_prefix << 1) | 1
            traverse_from(cur_node.right)
            cur_prefix = cur_prefix >> 1

    traverse_from(tree_root)
    return prefix_code_table


def huffman_encode(original: str) -> tuple[dict[str, bytes], BytesIO]:
    '''Given the original text, apply Huffman encoding.
    Recall the greedy algo: given subtrees containing char counts of
        groups of chars, combine the two least common char counts into a
        single tree. Repeat until only 1 tree remaining
    This tree can then be traversed to get a bit encoding for each char

    Return a dict of (char, encoding) plus the overall encoding of the
    original text
        I considered using an int + bit-shift, but that's too slow. I think
        I need a bytes-like buffer here

    Wait though...if every char gets >= 1 byte, then there's no compression
        over the original. I need a bitwise buffer'''
    char_counts = Counter(original)
    tree_root = get_huffman_tree(char_counts)
    prefix_code_table = get_prefix_code_table(tree_root)
    compressed_buffer = BytesIO()
    for ch in original:
        compressed_buffer.write(prefix_code_table[ch])
    return prefix_code_table, compressed_buffer


def main():
    '''Read filename from input, optionally specify compressed output fname'''
    parser = argparse.ArgumentParser()
    parser.add_argument('in_fname')
    parser.add_argument(
        '--out_fname', default='compressed_out.huf', required=False)
    args = parser.parse_args()
    with open(args.in_fname, encoding='utf-8') as f:
        code_table, compressed_output = huffman_encode(f.read())
        print(f'{compressed_output.tell()=}')
    with open(args.out_fname, 'wb+') as f:
        pickle.dump([code_table, compressed_output], f)


if __name__ == '__main__':
    main()
