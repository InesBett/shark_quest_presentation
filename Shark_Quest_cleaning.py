#!/usr/bin/env python
# coding: utf-8

import pandas as pd
df = pd.read_excel("https://www.sharkattackfile.net/spreadsheets/GSAF5.xls")

data_1 = df.copy() #making first copy just in case


# # making a new data set with columns that we want to work with instead of dropping columns
# 
# Here's how and logic: To select multiple columns, use a list of column names within the selection brackets
#     The inner square brackets define a Python list with column names,
#     whereas the outer brackets are used to select the data from a pandas DataFrame.
#     The returned data type is a pandas DataFrame. This method does not affect the rows. so we retain original rows
# 
# # justification for keeping columns
# 
#     1)data: there might be a particular season for attacks -we want to avoid that
#     2)year: we may look at this long term or select a period of time later - say 10 years
#     3)type: as discussed - unprovoked attacks might signal how dangerous the shark type is
#     4)country and location: we want to circle the hotspots
#     5)injury: not sure but maybe fatal ones could be useful
#     6)species: to find which ones require conservation
#     # age and sex and all that - not required


to_use = data_1[["Year","Type","Country","State","Injury","Species "]].copy()

#next step is data cleaning and standardisation - column names require cleaning - "species "has a white space
to_use.columns = to_use.columns.str.replace(' ', '')
to_use.columns = to_use.columns.str.lstrip().str.rstrip()
to_use.columns = to_use.columns.str.lower()
to_use = to_use.drop_duplicates()

#cleaning
to_use['year'] = to_use['year'].astype(str).str.replace(".0", "")
to_use['year'] = to_use['year'].replace('nan', '0')
to_use['year'] = to_use['year'].astype(int)
to_use = to_use[to_use["year"] >= 2000] #we sorted the years starting in 2000 till the actual year because that is what we want to analyze
to_use = to_use.sort_values(by="year", ascending=True)
to_use = to_use[to_use["year"] < 2025]
unwanted= ["Invalid", "Watercraft", "Questionable", "Sea Disaster", "Under investigation", "Unverified","Unconfirmed", "Boat", "?"]
to_use= to_use[to_use["type"].apply(lambda x: x not in unwanted)]

to_use["type"] = to_use["type"].replace(" Provoked", "Provoked")

to_use = to_use.dropna(subset=["type"])
to_use.isna().sum()

to_use.duplicated().sum()
to_use.drop_duplicates(inplace=True)

#dropping nan values in country and location
to_use.dropna(subset = ['country', 'state'],inplace = True)

# categories of injury
injuries_1 = ["no injury", "rammed", "knocked"]
injuries_2 = ["lacer"]
injuries_3 = ["minor", "bitten", "injured", "puncture", "superficial", "cut", "pinched", "bruised", "gash",
             "mark", "struck", "torn"]
injuries_4 = ["major", "sever", "significant", "broken", "injuries", "injury", "multiple", "serious",
              "gashed", "avulsed", "large", "lost", "amputated"]
injuries_5 = ["fatal", "death"]
boat = ["boat", "hull", "dinghy", "kayak"]
scavenging = ["scavenging"]
all_injuries = injuries_1 + injuries_2 + injuries_3 + injuries_4 + injuries_5 + boat + scavenging

def injury_rating(j):

    """categorising entries in the injury column"""

    j = j.lower()
    for i in injuries_1:
        if i in j:
            return "no injury"
    for i in injuries_2:
        if i in j:
            return "lacerations"
    for i in injuries_3:
        if i in j:
            return "minor injuries"
    for i in injuries_4:
        if i in j:
            return "major injuries"
    for i in injuries_5:
        if i in j:
            return "fatal"
    for i in scavenging:
        if i in j:
            return "probably scavenging"
    for i in boat:
        if i in j:
            return "material damage"


# categorising injuries
to_use.dropna(subset="injury", inplace=True)
to_use["injury"] = to_use["injury"].apply(injury_rating)
to_use.dropna(subset="injury", inplace=True)

# categorising shark species

sharks = ["white shark", "tiger shark", "bull shark", "shortfin mako shark",
         "lemon shark", "oceanic whitetip shark", "blue shark", "galapagos shark", "caribbean reef shark",
         "dusky shark", "blacktip shark", "silky shark", "gray reef shark", "great hammerhead shark",
         "blacktip reef shark", "sevengill shark", "sixgill shark", "nurse shark",
         "sand tiger", "spotted wobbegong", "basking shark", "spinner shark", "bronze whaler", "blue pointer"]

def shark_species(value, sharks):
    for shark in sharks:
        if shark in value.lower():
            return shark



to_use.dropna(subset="species", inplace=True)
to_use["species"] = to_use["species"].apply(shark_species, args=(sharks,))
to_use["species"] = to_use["species"].replace("blue pointer", "shortfin mako shark")
to_use.dropna(subset="species", inplace=True)

country_counts = to_use['country'].value_counts().reset_index()
country_counts.columns = ['Country', 'Attack_Count']
top_countries = country_counts.head(10)

species_counts = to_use["species"][to_use["type"] == "Unprovoked"].value_counts().reset_index()
species_counts.columns= ["Species", "Unprovoked_Attacks"]
top_species = species_counts.head(10)

country_state_attacks= to_use.copy()
country_state_attacks.drop(columns= ["year", "injury", "species"])
unprovoked_attacks = country_state_attacks[country_state_attacks["type"] == "Unprovoked"]
attack_counts = unprovoked_attacks.groupby(["country", "state"]).size().reset_index(name='count')
attack_counts= attack_counts.sort_values(by= "count", ascending= False).head(10)
top_10_attacks_state= attack_counts.head(10)

north_carolina_sharks = to_use[to_use['state'] == "North Carolina"]
state_shark_counts = north_carolina_sharks['species'].value_counts().reset_index()
state_shark_counts.columns = ['Species', 'Attack_Count']
top_state_shark = state_shark_counts.head(10)
