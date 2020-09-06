# %%
import json
import string

from typing import Dict, Any, Optional, Iterable, List

# %%
# Load our dictionary
with open("words_dictionary.json") as jsonfile:
    dictionary: Dict[str, Any] = json.load(jsonfile)

# Which numbers correspond to which letters?
cipher_table: Dict[int, Optional[str]] = {number: None for number in range(1, 27)}

# %%
# Load in the puzzle
with open("page_8.json") as jsonfile:
    puzzle = json.load(jsonfile)

words: List[List[int]] = puzzle["words"]
# Can't map int -> str in JSON, so we used str -> str. Rectify that here
puzzle["known_keys"] = {int(key): value for key, value in puzzle["known_keys"].items()}

# %%
def possible_characters(cipher_table: Dict[int, Optional[str]]):
    for letter in string.ascii_lowercase:
        if letter not in cipher_table.values():
            yield letter


# %%
