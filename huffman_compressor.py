from __future__ import annotations
import argparse
import pickle
from collections import Counter
import heapq
from dataclasses import dataclass
from functools import total_ordering
from typing import Any
from bitarray import bitarray, frozenbitarray


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

    def __repr__(self) -> str:
        return f'{self.total_count=}, {self.ch=}'


def get_huffman_tree(char_counts: dict[str, int]) -> TreeNode:
    '''Use the greedy algo described below to get the Huffman encoding tree
    Note that the first bit has to be 1, else shifts may have no effect'''
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
    overall_parent = TreeNode(cur_roots[0].total_count)
    overall_parent.right = cur_roots[0]
    return overall_parent


def get_prefix_code_table(tree_root: TreeNode) -> dict[str, bitarray]:
    '''Do a DFS on the Huffman binary tree, where moving left adds a 0 bit,
    moving right adds a 1 bit. Use this to get the prefix code for each char'''
    prefix_code_table: dict[str, bitarray] = {}
    cur_prefix = bitarray()

    def traverse_from(cur_node: TreeNode) -> None:
        '''Recursively traverse from cur_node. If cur_node is a leaf,
        then save the cur_prefix in the prefix_code_table'''
        if cur_node.left is None and cur_node.right is None:
            if cur_node.ch is None:
                raise ValueError(f'{cur_node=} leaf, but no char')
            prefix_code_table[cur_node.ch] = cur_prefix.copy()
        if cur_node.left is not None:
            cur_prefix.append(0)
            traverse_from(cur_node.left)
            cur_prefix.pop()
        if cur_node.right is not None:
            cur_prefix.append(1)
            traverse_from(cur_node.right)
            cur_prefix.pop()

    traverse_from(tree_root)
    return prefix_code_table


def huffman_encode(original: str) -> tuple[dict[str, bitarray], bitarray]:
    '''Given the original text, apply Huffman encoding.
    Recall the greedy algo: given subtrees containing char counts of
        groups of chars, combine the two least common char counts into a
        single tree. Repeat until only 1 tree remaining
    This tree can then be traversed to get a bit encoding for each char

    Return a dict of (char, encoding) plus the overall encoding of the
    original text

    Which particular encoding format? Some considerations:
        I considered using an int + bit-shift, but that's too slow
        Bytes-like buffer is fast, but each char >= 1 byte --> no compression
        Perhaps int, read successive bits, then convert to chr once > 1 byte
        But 00001 and 001 are the same int. Perhaps a list of bits instead?
        list of bits --> barely any compression in the final file
    Eventually settled on the 3rd party bitarray
        Doesn't appear to be a native bitarray in Python'''
    char_counts = Counter(original)
    tree_root = get_huffman_tree(char_counts)
    prefix_code_table = get_prefix_code_table(tree_root)
    compressed = bitarray()
    for ch in original:
        compressed.extend(prefix_code_table[ch])
    return prefix_code_table, compressed


def decode(compressed_fname: str) -> str:
    '''The compressed output should be a pickled (code_table, compressed str)
    After unpickling, I should be able to iterate through and recover the
    original file'''
    with open(compressed_fname, 'rb') as f:
        code_table, compressed_output = pickle.load(f)
        code_table: dict[str, bitarray]
        compressed_output: bitarray
    chs_by_prefix = {
        frozenbitarray(code): ch for ch, code in code_table.items()}
    uncompressed_chs: list[str] = []
    bit_buffer = bitarray()
    for bit in compressed_output:
        bit_buffer.append(bit)
        frozen_buffer = frozenbitarray(bit_buffer)
        if frozen_buffer in chs_by_prefix:
            uncompressed_chs.append(chs_by_prefix[frozen_buffer])
            bit_buffer = bitarray()
    return ''.join(uncompressed_chs)


def main():
    '''Read filename from input, optionally specify compressed output fname'''
    parser = argparse.ArgumentParser()
    parser.add_argument('in_fname')
    parser.add_argument(
        '--out_fname', default='compressed_out.huf', required=False)
    args = parser.parse_args()
    with open(args.in_fname, encoding='utf-8') as f:
        og_file_text = f.read()
    code_table, compressed_output = huffman_encode(og_file_text)
    with open(args.out_fname, 'wb+') as f:
        pickle.dump([code_table, compressed_output], f)
    recovered_uncompressed = decode(args.out_fname)
    print(f'{len(og_file_text)=}, {len(recovered_uncompressed)=}')
    assert recovered_uncompressed == og_file_text


if __name__ == '__main__':
    main()
