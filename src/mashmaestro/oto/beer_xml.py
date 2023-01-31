from .paths import download_path, processed_path


def grist():
    from pathlib import Path

    from pybeerxml.parser import Parser

    try1 = Path(download_path)
    bxmls = try1.iterdir()
    parser = Parser()
    recipe_mapping = {}
    for b in bxmls:
        recipes = parser.parse(b)
        recipe = recipes[0]
        recipe_total = sum(map(lambda ferm: ferm.amount, recipe.fermentables))
        grains = {
            grain.name: {"billpct": grain.amount / recipe_total, "amount": grain.amount}
            for grain in recipe.fermentables
        }

        recipe_mapping[b] = grains
    return recipe_mapping


def grist_dump():
    """#TODO future idea about ratios and onhand quantity"""
    mapping = grist()
    import json
    from pathlib import Path

    mapping2 = {}
    for m in mapping.keys():
        mapping2[str(m)] = mapping[m]

    with open(Path(processed_path, "grist.json"), "w") as fp:
        json.dump(mapping2, fp)
