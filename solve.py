# %%
import json
import string
import itertools
import re
import logging as log
from datetime import datetime

from typing import Dict, Any, Optional, Iterable, List

# %%
# Load our dictionary
with open("words_dictionary.json") as jsonfile:
    dictionary: Dict[str, Any] = json.load(jsonfile)

# Which numbers correspond to which letters?
CipherTable = Dict[int, Optional[str]]

# Sequence of numbers that defines a word
WordDescriptor = List[int]

blank_cipher_table: CipherTable = {number: None for number in range(1, 27)}

# %%
def possible_characters(cipher_table: CipherTable):
    for letter in string.ascii_lowercase:
        if letter not in cipher_table.values():
            yield letter


def iter_cipher(cipher_table: CipherTable) -> Iterable[CipherTable]:
    next_empty_key = {value: key for key, value in cipher_table.items()}[None]
    for character in possible_characters(cipher_table):
        yield {**cipher_table, **{next_empty_key: character}}


def decipher_to_regex(
    cipher_table: CipherTable, word_descriptor: WordDescriptor
) -> str:
    return (
        "^"
        + "".join(
            map(
                lambda x: cipher_table[x] if cipher_table[x] is not None else "[a-z]",  # type: ignore
                word_descriptor,
            )
        )
        + "$"
    )


def regex_in_dictionary(regex: str) -> bool:
    global dictionary
    for word in dictionary:
        if re.match(regex, word):
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
    print(
        datetime.now().strftime("%H:%M:%S")
        + "".join(map(lambda x: "_" if x is None else x, cipher_table.values()))
    )


# %%
def solve(cipher_table: CipherTable, word_descriptors: List[WordDescriptor]):
    if cipher_is_feasible(cipher_table, word_descriptors):
        if None not in cipher_table.values():
            # Found a full cipher table that works
            yield cipher_table
        else:
            # We've still got work to do
            for cipher_table in iter_cipher(cipher_table):
                print_cipher(cipher_table)
                yield from solve(cipher_table, word_descriptors)


# %%
# Load in the puzzle
with open("page_8.json") as jsonfile:
    puzzle = json.load(jsonfile)

word_descriptors: List[WordDescriptor] = puzzle["words"]
# Can't map int -> str in JSON, so we used str -> str. Rectify that here
known_keys = {int(key): value for key, value in puzzle["known_keys"].items()}
# %%
