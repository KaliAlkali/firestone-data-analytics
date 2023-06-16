import json
import time
import requests
import zipfile
import os
import random

###Open the history fetched from %AppData% Overwolf
matchhistory = open("user-match-history.json", "r")

data = json.load(matchhistory)

###Build the list of replay IDs to review based on deck name. Other attributes recorded in the appdata file may be included.
reviewlist = []

###Filterlist. Enter attributes here to pull games from characteristics present in the %appdata% file
for x in data:
    if x["playerDeckName"] == "I%20don't%20want%20to%20be%20evil":
        id = x["reviewId"]
        reviewlist.append(id)
    else:
        pass

matchhistory.close()

lambdaserver = "https://itkmxena7k2kkmkgpevc6skcie0tlwmk.lambda-url.us-west-2.on.aws"
firestonefiles = "http://xml.firestoneapp.com/"


downloadedlist = []

### Begin the quasi-DDOS attack
for id in reviewlist:

    ###Pull the filekey from the lambda ep
    lambdares = requests.get(str(lambdaserver + "//" + id))

    ###Store as JSON
    lambdaresjson = lambdares.json()

    ###Parse JSON
    filekey = lambdaresjson['replayKey']

    ###Download filekey from S3 bucket
    filedownload = requests.get(str(firestonefiles + filekey))

    print("Downloaded " + filekey)

    ####Begin local file manipulation
    filename = filekey[-20:]

    ###Write the downloaded file to the compressed section of the XML files
    f = open(os.path.join("xmlfiles/compressed", filename), 'wb')

    f.write((filedownload.content))

    f.close()

    ###Uncompress
    with zipfile.ZipFile(str(os.path.join("xmlfiles/compressed/" + filename)), 'r') as zip_ref:
        zip_ref.extractall(str(os.path.join("xmlfiles/uncompressed/" + filename)))
    
    print("Uncompressed " + filename)

    downloadedlist.append(filename)

    ###Sleepytime to make sure other people can make requests and I don't get blocked by cloudflare for this
    sleepytime = random.randint(0, 3)

    time.sleep(sleepytime)
    
    
###final check to make sure you got everything
if len(reviewlist) != len(downloadedlist):
    print("Something somewhere has gone wrong and all your games could not be fetched.")
