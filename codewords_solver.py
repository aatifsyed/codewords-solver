#!/bin/env python3
# %%
import argparse
import itertools
import json
import logging as log
import re

from datetime import datetime
from distutils.util import strtobool
from pprint import pprint
from typing import Dict, Any, Optional, Iterable, List, Generator

# %%
# Which numbers correspond to which letters?
CipherTable = Dict[int, Optional[str]]

# Sequence of numbers that defines a word
WordDescriptor = List[int]

# How often does each number appear in our word descriptors?
FrequencyTable = Dict[int, int]

# %%
def possible_characters(cipher_table: CipherTable):
    """What characters have not been filled in this table, in popularity order.

    Args:
        cipher_table (CipherTable): [description]

    Yields:
        [str]: character
    """
    # Letters sorted by frequency
    for letter in "etaoinsrhdlucmfywgpbvkxqjz":
        if letter not in cipher_table.values():
            yield letter


def iter_cipher(cipher_table: CipherTable, frequency_table: FrequencyTable):
    """Yields cipher tables that have the most frequently appearing key filled in (by a popular letter)

    Args:
        cipher_table (CipherTable): [description]
        frequency_table (FrequencyTable): [description]

    Yields:
        [CipherTable]: [description]
    """
    # Take out the keys which have already been covered
    remaining_frequency_table: FrequencyTable = {
        key: value
        for key, value in frequency_table.items()
        if cipher_table[key] is None
    }
    # Now get the most frequent
    best_value = 0
    best_key = 0
    for key, value in remaining_frequency_table.items():
        if value > best_value:
            best_key = key
            best_value = value

    # Now iterate over characters that could fill that
    for character in possible_characters(cipher_table):
        yield {**cipher_table, **{best_key: character}}


def get_frequency_table(word_descriptors: List[WordDescriptor]) -> FrequencyTable:
    """Count the number of times each key appears in the puzzle

    Args:
        word_descriptors (List[WordDescriptor]): The puzzle

    Returns:
        FrequencyTable: [description]
    """
    frequency_table = {number: 0 for number in range(1, 27)}

    for word_descriptor in word_descriptors:
        for number in word_descriptor:
            frequency_table[number] += 1

    return frequency_table


def decipher_to_regex(
    cipher_table: CipherTable, word_descriptor: WordDescriptor
) -> str:
    """Turn a list of numbers into a regex, leaving [:alpha:] if the cipher isn't known for that key

    Args:
        cipher_table (CipherTable): [description]
        word_descriptor (WordDescriptor): [description]

    Returns:
        str: [description]
    """
    return "".join(
        map(
            lambda x: cipher_table[x] if cipher_table[x] is not None else "[a-z]",  # type: ignore
            word_descriptor,
        )
    )


def deciphered_in_dictionary(
    cipher_table: CipherTable, word_descriptor: WordDescriptor
) -> bool:
    """Could this word be deciphered into a valid dictionary word?

    Args:
        cipher_table (CipherTable): [description]
        word_descriptor (WordDescriptor): [description]

    Returns:
        bool: [description]
    """
    global dictionary
    regex = decipher_to_regex(cipher_table, word_descriptor)
    return bool(re.search(regex, dictionary))


def cipher_is_feasible(
    cipher_table: CipherTable, word_descriptors: List[WordDescriptor]
) -> bool:
    """Given this cipher table, could all puzzle rows/columns be real words?

    Args:
        cipher_table (CipherTable): [description]
        word_descriptors (List[WordDescriptor]): [description]

    Returns:
        bool: [description]
    """
    for word_descriptor in word_descriptors:
        if not deciphered_in_dictionary(cipher_table, word_descriptor):
            return False
    return True


def print_cipher(cipher_table: CipherTable):
    """Utility function for conditionally printing

    Args:
        cipher_table (CipherTable): [description]
    """
    global args
    if args.print:
        print(datetime.now().strftime("%H:%M:%S"), end=" ")
        for i in range(1, 27):
            print(cipher_table[i] if cipher_table[i] is not None else "_", end="")
        print()


# %%
def solve(
    cipher_table: CipherTable,
    word_descriptors: List[WordDescriptor],
    frequency_table: FrequencyTable,
):
    """Recurse/backtrack to find a solution. The whole point of this program.

    Args:
        cipher_table (CipherTable): [description]
        word_descriptors (List[WordDescriptor]): [description]
        frequency_table (FrequencyTable): [description]

    Yields:
        [type]: [description]
    """
    if cipher_is_feasible(cipher_table, word_descriptors):
        if None not in cipher_table.values():
            # Found a full cipher table that works
            yield cipher_table
        else:
            # We've still got work to do
            for cipher_table in iter_cipher(cipher_table, frequency_table):
                print_cipher(cipher_table)
                yield from solve(cipher_table, word_descriptors, frequency_table)


# %%
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Backtracking solver for codewords")
    parser.add_argument(
        "--dictionary", default="words_alpha.txt", dest="dictionary_path"
    )
    parser.add_argument("--puzzle", required=True, dest="puzzle_path")
    parser.add_argument(
        "--print",
        help="Print out progress as we backtrace",
        dest="print",
        action="store_true",
    )
    parser.add_argument(
        "--exhaust", help="Exhaustive search", dest="exhaust", action="store_true"
    )

    args = parser.parse_args(
        ["--puzzle", "puzzler_codewords_volume_2/page_12.json", "--print", "--exhaust"]
        if "__IPYTHON__" in vars(__builtins__)
        else None
    )

    # Load in our dictionary
    with open(args.dictionary_path) as txt:
        dictionary: str = txt.read()

    # Load in our puzzle
    with open(args.puzzle_path) as jsonfile:
        puzzle = json.load(jsonfile)

    # Can't map int -> str in JSON, so we used str -> str. Rectify that here
    known_keys = {int(key): value for key, value in puzzle["known_keys"].items()}

    blank_cipher_table: CipherTable = {number: None for number in range(1, 27)}
    starting_table: CipherTable = {**blank_cipher_table, **known_keys}
    word_descriptors: List[WordDescriptor] = puzzle["words"]
    frequency_table: FrequencyTable = get_frequency_table(word_descriptors)

    solutions: List[CipherTable]= []

    t0 = datetime.now()
    for solution in solve(blank_cipher_table, word_descriptors, frequency_table):
        print("Found solution:")
        pprint(solution)
        solutions.append(solution)
        if args.exhaust or bool(strtobool(input("Continue search?"))):
            continue
        else:
            break

    print(f"found {len(solutions)} solutions, took {datetime.now() - t0}")

# %%
