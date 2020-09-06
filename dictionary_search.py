#!/bin/env python3
# %%
import re
import json

# Load up the file
with open("words_dictionary.json") as jsonfile:
    dictionary: dict = json.load(jsonfile)

# %%
pattern = input("Describe the word as a regex:\n")
number_of_matches = 0
for word in dictionary.keys():
    if re.match(pattern, word):
        print(word)
        number_of_matches += 1
print(f"Completed search, found {number_of_matches} matches")

# %%
