# URL regex credit: 
# https://stackoverflow.com/questions/6038061/regular-expression-to-find-urls-within-a-string

import os
import json
import re
import sys
import html
from langdetect import detect

def myPrint(s):
    sys.stdout.write('\r')
    sys.stdout.flush()
    sys.stdout.write(s)
    sys.stdout.flush()

DIR_PREFIX = "training_tweets/"

# compile all regexs
urlRe = re.compile(r"(http|ftp|https):\/\/([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?")
ampRe = re.compile(r"&amp;")
gtRe = re.compile(r"&gt;")
ltRe = re.compile(r"&lt;")
nbspRe = re.compile(r"&nbsp;")
nwsRe = re.compile(r"[\n\t\r]")
mentionRe = re.compile(r"@\w* ")
englRe = re.compile(r"[^1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!()\".,;:\' ]")
spPuncRe = re.compile(r"\s([.,;:])")
multSpaceRe = re.compile(r"\s{2,}")

# get all our emoji codes
with open("our_emojis.json", "r") as f:
    ourEmojiCodes = [code for code in json.load(f)]

codesImported = 0
for code in ourEmojiCodes:
    # print progress
    codesImported += 1
    print("Analyzing code {}/{} ({})".format(codesImported, len(ourEmojiCodes), code))

    # import the tweets from all downloaded files
    myDir = os.listdir(os.fsencode("{}/raw/{}".format(DIR_PREFIX, code)))
    filesImported = 0
    allTweets = []
    for file in myDir:
        # read tweets into list
        with open("{}/raw/{}/{}".format(DIR_PREFIX, code, os.fsdecode(file))) as f:
            myTweets = json.load(f)
            allTweets.extend(myTweets)
            filesImported += 1
        myPrint("  Importing {}/{}".format(filesImported, len(myDir)))

    if filesImported > 0:
        print()
        # clean all tweets for this code
        cleanedTweets = []
        cleaned = 0
        for tweet in allTweets:
            cleaned += 1

            # print progress
            myPrint('  Sanitizing {}/{}/{}'.format(len(cleanedTweets), cleaned, len(allTweets)))

            newTweet = urlRe.sub("", tweet) # remove all links
            newTweet = ampRe.sub("&", newTweet) # replace HTML ampersands
            newTweet = gtRe.sub(">", newTweet) # replace HTML greater than
            newTweet = ltRe.sub("<", newTweet) # replace HTML less than
            newTweet = nbspRe.sub(" ", newTweet) # replace HTML space
            newTweet = nwsRe.sub(" ", newTweet) # remove all non-space whitespace
            newTweet = mentionRe.sub("", newTweet)  # remove mentions
            newTweet = englRe.sub("", newTweet) # keep only english characters and punctuation 
            newTweet = spPuncRe.sub(r"\1", newTweet) # remove spaces before ending puncuation
            newTweet = multSpaceRe.sub(" ", newTweet) # remove multiple whitespaces
            # ensure language is english
            try:
                lang = detect(newTweet) # will throw exception on no content
                if lang == "en":
                    cleanedTweets.append(newTweet.strip())
            except:
                pass
        print()

    # write all tweets to new file
    with open("{}/cleaned/{}.json".format(DIR_PREFIX, code), "w+") as f:
        json.dump(cleanedTweets, f, indent=2)

    # move onto the next code

print()
sys.stdout.flush()