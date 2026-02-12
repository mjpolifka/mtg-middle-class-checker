from pyrchidekt.api import getDeckById

deck = getDeckById(1)

for category in deck.categories:
    print(f"{category.name}")
    for card in category.cards:
        print(f"\t{card.quantity} {card.card.oracle_card.name}")
    print("")