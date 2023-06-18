import json
import pandas as pd
import xml.etree.ElementTree as ET
import os
import glob
from scipy.stats import chisquare

cwd = str(os.getcwd() + '/')

cardjsonloc = str(cwd + 'firestonecardlibrary.json')

cardlib = open(cardjsonloc, "r")

jsonlib = json.load(cardlib)

basichplist = ["Ghoul Charge", "Reinforce", "Demon Claws", "Shapeshift", "Steady Shot", "Fireblast", "Lesser Heal", "Dagger Mastery", "Totemic Call", "Life Tap", "Armor Up!"]

cardlib.close()

cardlibdf = pd.json_normalize((jsonlib))

###Hero power manipulation and isolating the basic HPs

heropowersdf = pd.DataFrame()

heropowersdf = cardlibdf.loc[cardlibdf['type']=='Hero_power']

heropowersdf = heropowersdf.dropna(axis=1, how='all')

basichplist = ["Ghoul Charge", "Reinforce", "Demon Claws", "Shapeshift", "Steady Shot", "Fireblast", "Lesser Heal", "Dagger Mastery", "Totemic Call", "Life Tap", "Armor Up!"]

basichpsdf = pd.DataFrame()

basichpsdf = heropowersdf.loc[heropowersdf['name'].isin(basichplist)]

basichpsdf = basichpsdf.dropna(axis=1, how='all')

def renounceident(file):
    renounceid = "OG_118e"
    data = ET.parse((cwd + "xmlfiles/uncompressed/" + file + ".xml.zip/replay.xml"))
    root = data.getroot()
    for child in root.iter():
        if "cardID" in child.attrib:
            if child.attrib['cardID'] == renounceid:
                return file
            else:
                pass
        else:
            pass
    return


replays = []

rootdir = cwd + "xmlfiles/uncompressed/*.xml.zip"
for replayfile in glob.glob(rootdir):
    replays.append(replayfile[68:80])

renouncereplays = []

for replay in replays:
    filecheck = renounceident(replay)
    if filecheck:
        renouncereplays.append(filecheck)
    else:
        pass

###Pull class that you transformed into

def find_last_index(search_list, search_item):
    return len(search_list) - 1 - search_list[::-1].index(search_item)

def renouncechange(file):
    renouncecardid = "OG_118"
    data = ET.parse((cwd + "xmlfiles/uncompressed/" + file + ".xml.zip/replay.xml"))
    root = data.getroot()
    buildlist = []
    hpidlist = basichpsdf['id'].to_list()
    for child in root.iter():
        if 'cardID' in child.attrib:
            if child.attrib['cardID'] == renouncecardid:
                buildlist.append(renouncecardid)
            else:
                pass
            if child.attrib['cardID'] in hpidlist:
                heropower = child.attrib['cardID']
                buildlist.append(heropower)
            else:
                pass
    listindex = find_last_index(buildlist, renouncecardid)
    try:
        hpid = buildlist[listindex + 1]
    except IndexError:
        hpid = buildlist[listindex - 1]
    valuedf = pd.DataFrame(basichpsdf.loc[basichpsdf['id'] == hpid])
    valuedf['gameid'] = file
    return(valuedf)


transform = pd.DataFrame()

for game in renouncereplays:
    event = renouncechange(game)
    transform = pd.concat([transform, event])

###Chisq test

###Create classlist for indexing
classlist = basichpsdf['playerClass'].drop_duplicates().to_list()

###Had to manually delete "Neutral" and "Warlock" as neither would appear and lst.remove() was deleting whole list for some reason
del classlist[10]
del classlist [1]

observedfreqdf = pd.DataFrame({'Freq' : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]}, index = classlist)

for row in transform.iterrows():
    observedfreqdf.loc[row[1]['playerClass']] = (observedfreqdf.loc[row[1]['playerClass']] + 1)

trials = observedfreqdf['Freq'].to_list()

test = chisquare(observedfreqdf['Freq'])
print('results of chisquare test are: ')
print(test)