import argparse
import pickle
from collections import Counter


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
    print(f'{char_counts["X"]=}, {char_counts["t"]=}')
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
