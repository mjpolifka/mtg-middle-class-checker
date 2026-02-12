import scrython

cards = scrython.cards.Search(unique="prints", q="Brainstorm")

for card in cards.data():
    if card['rarity'] != "common":
        if card['rarity'] != "uncommon":
            print(card['set_name'] + " [" + card['collector_number'] + "] is a " + card['rarity'] + " printing.\n")