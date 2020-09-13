# %%
import re
import json

# %%
with open("words_alpha.txt") as f:
    memory = f.read()

with open("words_dictionary.json") as jsonfile:
    dictionary = json.load(jsonfile)

# %%
def regex_in_dictionary(regex: str) -> bool:
    global dictionary
    for word in dictionary:
        if re.match(regex, word):
            return True
    return False

# %%
p = r"b...tiful"

# %%
%timeit re.findall(p, memory)

# %%
%timeit regex_in_dictionary(p)
