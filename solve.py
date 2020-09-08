#!/bin/env python3
# %%
import json
import itertools
import re
import logging as log
from datetime import datetime

import cProfile

from typing import Dict, Any, Optional, Iterable, List

# %%
# Load our dictionary
with open("words_alpha.txt") as txt:
    dictionary: str = txt.read()

# Which numbers correspond to which letters?
CipherTable = Dict[int, Optional[str]]

# Sequence of numbers that defines a word
WordDescriptor = List[int]

# How often does each number appear in our word descriptors?
FrequencyTable = Dict[int, int]

blank_cipher_table: CipherTable = {number: None for number in range(1, 27)}

# %%
def possible_characters(cipher_table: CipherTable):
    # Letters sorted by frequency
    for letter in "etaoinsrhdlucmfywgpbvkxqjz":
        if letter not in cipher_table.values():
            yield letter


def iter_cipher(
    cipher_table: CipherTable, frequency_table: FrequencyTable
) -> Iterable[CipherTable]:
    remaining_frequency_table: FrequencyTable = {
        key: value
        for key, value in frequency_table.items()
        if cipher_table[key] is None
    }
    best_value = 0
    best_key = 0
    for key, value in remaining_frequency_table.items():
        if value > best_value:
            best_key = key
            best_value = value
    for character in possible_characters(cipher_table):
        yield {**cipher_table, **{best_key: character}}


def get_frequency_table(word_descriptors: List[WordDescriptor]) -> FrequencyTable:
    frequency_table = {number: 0 for number in range(1, 27)}

    for word_descriptor in word_descriptors:
        for number in word_descriptor:
            frequency_table[number] += 1

    return frequency_table


def decipher_to_regex(
    cipher_table: CipherTable, word_descriptor: WordDescriptor
) -> str:
    return "".join(
        map(
            lambda x: cipher_table[x] if cipher_table[x] is not None else "[a-z]",  # type: ignore
            word_descriptor,
        )
    )


def regex_in_dictionary(regex: str) -> bool:
    global dictionary
    if re.search(regex, dictionary):
        return True
    return False


def deciphered_in_dictionary(
    cipher_table: CipherTable, word_descriptor: WordDescriptor
):
    regex = decipher_to_regex(cipher_table, word_descriptor)
    return regex_in_dictionary(regex)


def cipher_is_feasible(
    cipher_table: CipherTable, word_descriptors: List[WordDescriptor]
) -> bool:
    for word_descriptor in word_descriptors:
        if not deciphered_in_dictionary(cipher_table, word_descriptor):
            return False
    return True


def print_cipher(cipher_table: CipherTable):
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
# Load in the puzzle
with open("puzzler_codewords_volume_2/page_12.json") as jsonfile:
    puzzle = json.load(jsonfile)

# Can't map int -> str in JSON, so we used str -> str. Rectify that here
known_keys = {int(key): value for key, value in puzzle["known_keys"].items()}

starting_table: CipherTable = {**blank_cipher_table, **known_keys}
word_descriptors: List[WordDescriptor] = puzzle["words"]
frequency_table: FrequencyTable = get_frequency_table(word_descriptors)

# %%
cProfile.run("next(solve(starting_table, word_descriptors, frequency_table))")

# %%
