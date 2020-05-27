#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: raphaelpreston
"""

import json
import sys
import enchant
from statistics import median


DIR_PREFIX = "training_tweets/"
JSON_FNAME = "our_emojis.json"
ENGL_DICT = enchant.Dict("en_US")

def replaceLineWith(s):
    sys.stdout.write('\r')
    sys.stdout.flush()
    sys.stdout.write(s)
    sys.stdout.flush()


# get our emoji json data
with open(JSON_FNAME, "r") as f:
    ourEmojiData = json.load(f)

ourEmojiCodes = [code for code in ourEmojiData] # all our emoji codes
importedCodes = [code for code in ourEmojiCodes if ourEmojiData[code]['imported']]
cleanedCodes = [code for code in importedCodes if ourEmojiData[code]['cleaned']]
unCleanedCodes = [code for code in importedCodes if not ourEmojiData[code]['cleaned']]

# cleanedTweets = []
codesCleaned = 0
lengths = []
# skip cleanedCodes
i = 0
for code in cleanedCodes:
    i += 1
    print('Already cleaned "{} ({}/{})"'.format(code, i, len(cleanedCodes)))
# clean imported tweets that haven't been cleaned
for code in unCleanedCodes:
    codesCleaned += 1

    print("Code {}/{}/{}/{} ({})".format(codesCleaned, len(unCleanedCodes), len(importedCodes), len(ourEmojiCodes), code))

    # import the tweets from the sanitized file
    fileName = "{}sanitized/{}.json".format(DIR_PREFIX, code)
    try:
        with open(fileName, "r") as f:
            allTweets = json.load(f)
    except Exception as e:
        print("\nFailed to read JSON from {}".format(fileName))
    
    # clean all tweets for this emoji code
    cleanedTweets = set() # ensure unique
    analyzed = 0
    for tweet in allTweets:
        analyzed += 1

        # print progress
        replaceLineWith('  Cleaning {}/{}/{}'.format(len(cleanedTweets), analyzed, len(allTweets)))

        words = tweet.split(' ')
        if len(words) > 5: # at least 5 words
            incoherentWords = len([w for w in words if not ENGL_DICT.check(w)])
            if incoherentWords < 1: # no incoherent words
                cleanedTweets.add(tweet)
                lengths.append(len(words))

    print()

    # update json data for this code
    ourEmojiData[code]['cleaned'] = True
    ourEmojiData[code]['dont-train'] = False
    ourEmojiData[code]['clean-tweets'] = len(cleanedTweets)
    ourEmojiData[code]['clean-tweet-median-length'] =  median(lengths)

    # sort tweets by length
    cleanedTweets = sorted(cleanedTweets, key=len, reverse=True)

    # write all tweets for this code to new file
    with open("{}/cleaned/{}.json".format(DIR_PREFIX, code), "w+") as f:
        json.dump(cleanedTweets, f, indent=4)

    # update our emoji json after every code
    with open(JSON_FNAME, "w") as f:
        json.dump(ourEmojiData, f, indent=4)

print()
sys.stdout.flush()