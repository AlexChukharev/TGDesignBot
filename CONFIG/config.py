import json


def load_config(path: str):
    with open(path, "r") as file:
        return json.load(file)
    
CONFIG = load_config("./CONFIG/config.json")
TAGS_RU = load_config("./CONFIG/tags_tree.json")
TAGS_EN = load_config("./CONFIG/tags_tree_en.json")

def get_tags_tree(lang: str):
    if lang == "ru":
        return TAGS_RU
    else:
        return TAGS_EN