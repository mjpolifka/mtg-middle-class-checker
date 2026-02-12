import time
import scrython
from pyrchidekt.api import getDeckById
# import architrice # does more sites, keep in back pocket

# This doesn't work, not sure why:
#import pyrchidekt
#deck = pyrchidekt.api.getDeckById(15983552)


#
#
#  Mana Crypt is a problem
#       it's never been printed non-rare, but it's also never been printed non-promo
#
#


while True:
    id = input("Enter Archidekt deck ID: ")

    if (id != "") & id.isnumeric():
        print("importing deck...")
        try:
            deck = getDeckById(id)
            print("Using deck: " + deck.name)
        except RuntimeError as e:
            print("Error: deck not found with id: " + str(id))
            quit()
        break


ignored_sets = [
    # Unusual Sets
    'SLD'  # Secret Lairs
    ,'SLP' # Secret Lair Showdown
    ,'SLC' # Secret Lair 30th Anniversary Countdown Kit
    ,'SPG' # Special Guests
    ,'HOP' # Planechase
    ,'PLST' # The List
    
    # Promos and Crap
    ,'PRM' # MTGO Promos
    ,'SCH' # Store Championships
    ,'F01' # Friday Night Magic 2001
    ,'F02' # Friday Night Magic 2002
    ,'F03' # Friday Night Magic 2003
    ,'F04' # Friday Night Magic 2004
    ,'F05' # Friday Night Magic 2005
    ,'F06' # Friday Night Magic 2006
    ,'F07' # Friday Night Magic 2007
    ,'F08' # Friday Night Magic 2008
    ,'F09' # Friday Night Magic 2009
    ,'F10' # Friday Night Magic 2010
    ,'F11' # Friday Night Magic 2011
    ,'F12' # Friday Night Magic 2012
    ,'F13' # Friday Night Magic 2013
    ,'F14' # Friday Night Magic 2014
    ,'F15' # Friday Night Magic 2015
    ,'JGP' # Judge Gift Cards 1998
    ,'G00' # Judge Gift Cards 2000
    ,'G01' # Judge Gift Cards 2001
    ,'G02' # Judge Gift Cards 2002
    ,'G03' # Judge Gift Cards 2003
    ,'G04' # Judge Gift Cards 2004
    ,'G05' # Judge Gift Cards 2005
    ,'G06' # Judge Gift Cards 2006
    ,'G07' # Judge Gift Cards 2007
    ,'G08' # Judge Gift Cards 2008
    ,'G09' # Judge Gift Cards 2009
    ,'G10' # Judge Gift Cards 2010
    ,'G11' # Judge Gift Cards 2011
    ,'J12' # Judge Gift Cards 2012
    ,'J13' # Judge Gift Cards 2013
    ,'J14' # Judge Gift Cards 2014
    ,'J15' # Judge Gift Cards 2015
    ,'J16' # Judge Gift Cards 2016
    ,'J17' # Judge Gift Cards 2017
    ,'J18' # Judge Gift Cards 2018
    ,'J22' # Jumpstart 22
    ,'J23' # Jumpstart 23
    ,'J24' # Jumpstart 24
    ,'J25' # Foundations Jumpstart
    ,'P08' # Magic Player Rewards 2008
    ,'P09' # Magic Player Rewards 2009
    ,'P10' # Magic Player Rewards 2010
    ,'P22' # Judge Gift Cards 2022
    ,'PZ1' # Legendary Cube Prize Pack
    ,'PZ2' # Treasure Chest
    ,'PIDW' # IDW Comics Insert
    ,'PURL' # Promos
    ,'PMEI' # Promos
    ,'PKLD' # Kaladesh Promos
    ,'PDGM' # Dragon's Maze Promos
    ,'PDTK' # Dragons of Tarkir Promos
    ,'PANA' # MTG Arena Promos
    ,'PHPR' # HarperPrism Book Promos
    ,'P30M' # 30th Anniversary Misc Promos
    ,'P30A' # 30th Anniversary Play Promos
    ,'PSVC' # Summer Vacation Promos 2022
    ,'PFDN' # Foundations Promos
    ,'RFIN' # FIN Promos
    ,'PF19' # MagicFest 2019
    ,'PF20' # MagicFest 2020
    ,'PF21' # MagicFest 2021
    ,'PF22' # MagicFest 2022
    ,'PF23' # MagicFest 2023
    ,'PF24' # MagicFest 2024
    ,'PF25' # MagicFest 2025
    ,'PLGM' # DCI Legend Membership
    ,'DCI'  # DCI Promos
    ,'PJAS' # Junior APAC Series
    ,'PJJT' # Japan Junior Tournament
    ,'PJSE' # Junior Series Europe
    ,'PSUS' # Junior Super Series
    ,'PUMA' # Ultimate Box Topper
    ,'PEWK' # Eternal Weekend
    ,'PCBB' # Cowboy Bebop
    ,'PL23' # Year of the Rabbit 2023
    ,'PL24' # Year of the Dragon 2024
    ,'PL25' # Year of the Snake 2025
    ,'PW21' # Wizards Play Network 2021
    ,'PW22' # Wizards Play Network 2022
    ,'PW23' # Wizards Play Network 2023
    ,'PW24' # Wizards Play Network 2024
    ,'PW25' # Wizards Play Network 2025
    ,'PLG20' # Love Your LGS 2020
    ,'PLG21' # Love Your LGS 2021
    ,'PLG22' # Love Your LGS 2022
    ,'PLG23' # Love Your LGS 2023
    ,'PLG24' # Love Your LGS 2024
    ,'PAL04' # Arena League 2004
    ,'PAL05' # Arena League 2005
    ,'PAL06' # Arena League 2006
    
    # Signature Spellbook/From the Vault/Commander Collection
    ,'SS1' # Signature Spellbook: Jace
    ,'SS2' # Signature Spellbook: Gideon
    ,'SS3' # Signature Spellbook: Chandra
    ,'V09' # From the Vault: Exiled
    ,'V12' # From the Vault: Realms
    ,'V13' # From the Vault: Twenty
    ,'DRB' # From the Vault: Dragons
    ,'CC1' # Commander Collection: Green
    ,'CC2' # Commander Collection: Black
    
    # Bonus Sheets
    ,'STA' # Strixhaven Bonus Sheet
    ,'BRR' # Brother's War Bonus Sheet
    ,'MUL' # March of the Machine Bonus Sheet
    ,'WOT' # Wilds of Eldrane Bonus Sheet
    ,'OTP' # Breaking News (Outlaws) Bonus Sheet
    ,'BIG' # The Big Score (Outlaws) Bonus Sheet
    ,'H2R' # Modern Horizons Bonus Sheet
    ,'FCA' # Final Fantasy Bonus Sheet
    ,'EOS' # Edge of Eternities Bonus Sheet
    ,'MAR' # Marvel Bonus Sheet
    ,'OMB' # Omenpaths Bonus Sheet
    
    # Masterpiece Series (Bonus Sheets Before Bonus Sheets)
    ,'EXP' # Zendikar Expeditions
    ,'MPS' # Kaladesh Inventions
    ,'MP2' # Amonkhet Invocations
    ,'ZNE' # Zendikar Rising Expeditions
    ,'MED' # Mythic Edition
        
    # Masters Editions (MTGO-only, doesn't count)
    ,'ME1' # Masters Edition
    ,'ME2' # Masters Edition 2
    ,'ME3' # Masters Edition 3
    ,'ME4' # Masters Edition 4
    ,'VMA' # Vintage Masters
    ,'TPR' # Tempest Remastered
    
    # Physical Masters (I think we're not counting these?)
    ,'MMA' # Modern Masters
    ,'MM2' # Modern Masters 2015
    ,'MM3' # Modern Masters 2017
    ,'EMA' # Eternal Masters
    ,'IMA' # Iconic Masters
    ,'A25' # Masters 25
    ,'UMA' # Ultimate Masters
    ,'CMM' # Commander Masters
    ,'2XM' # Double Masters
    ,'2X2' # Double Masters 2022
    
    # Remasters (I think we're not counting these?)
    ,'TSR' # Time Spiral Remastered
    ,'DMR' # Dominaria Remastered
    ,'RVR' # Ravnica Remastered
    ,'INR' # Innistrad Remastered
    ,'DBL' # Innistrad Double-Feature
    
    # Arena-Only Remasters
    ,'AKR' # Amonkhet Remasterd
    ,'KLR' # Kaladesh Remasterd
    ,'SIR' # Shadows over Innistrad Remasterd
    ,'SIS'  # Bonus Sheet
    ,'PIO' # Pioneer Masters # Arena-only
    
    # Commander Precons
    ,'C20' # Commander 2020 (Ikoria)
    ,'ZNC' # Zendikar Rising Commander Decks
    ,'KHC' # Kaldheim Commander Decks
    ,'C21' # Commander 2021 (Strixhaven)
    ,'AFC' # Dungeons & Dragons: Adventures in the Forgotten Realms Commander Decks
    ,'MIC' # Innistrad: Midnight Hunt Commander Decks
    ,'VOC' # Innistrad: Crimson Vow Commander Decks
    ,'NEC' # Kamigawa: Neon Dynasty Commander Decks
    ,'NCC' # Streets of New Capenna Commander Decks
    ,'DMC' # Dominaria United Commander Decks
    ,'BRC' # The Brothers' War Commander Decks
    ,'ONC' # Phyrexia: All Will Be One Commander Decks
    ,'MOC' # March of the Machine Commander Decks
    ,'LTC' # Lord of the Rings Commander Decks
    ,'WOC' # Wilds of Eldraine Commander Decks
    ,'LCC' # The Lost Caverns of Ixalan Commander Decks
    ,'MKC' # Murders at Karlov Manor Commander Decks
    ,'OTC' # Outlaws of Thunder Junction Commander Decks
    ,'M3C' # Modern Horizons 3 Commander Decks
    ,'BLC' # Bloomburrow Commander Decks
    ,'DSC' # Duskmourn: House of Horror Commander Decks
    ,'DRC' # Aetherdrift Commander Decks
    ,'TDC' # Tarkir: Dragonstorm/Commander decks
    ,'SCD' # Starter Commander Decks
    ,'CMA' # Commander Anthology
]

sequence = 1
for card in deck.cards:
    scry = scrython.cards.Search(unique="prints", q=card.card.oracle_card.name)
    for scry_card in scry.data():
        if scry_card['name'] == card.card.oracle_card.name: # Scryfall search isn't exact, searching "Harmonize" also finds "Mightform Harmonizer"
            if scry_card['rarity'] not in ["common", "uncommon"]:
                if scry_card['set'].upper() not in ignored_sets:
                    print("  " + scry_card['name'] + ": " + scry_card['set_name'] + " (" + str(scry_card['set']).upper() + ") [" + scry_card['collector_number'] + "] is a " + scry_card['rarity'] + " printing.")
    print("Card " + str(sequence) + " out of " + str(len(deck.cards)))
    sequence = sequence + 1
    time.sleep(0.1) # be nice to scryfall
