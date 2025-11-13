from collections import Counter
import json


with open("./data/words.json", "r") as f:
    words = json.load(f)
special = ["ORDER", "INPUT", "VOCAB", "LOGIC", "LINKS", "CHAIN", "MERGE", "GAMES", "CLAIM", "WORDS"]
mostsp = "WORDS"
letter_list = list(Counter("".join(words)).elements())
print(len(letter_list))