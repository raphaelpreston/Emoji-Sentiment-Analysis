#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: raphaelpreston
"""

# URL regex credit: 
# https://stackoverflow.com/questions/6038061/regular-expression-to-find-urls-within-a-string

import os
import json
import re
import sys
import html


DIR_PREFIX = "training_tweets/"
JSON_FNAME = "our_emojis.json"

def replaceLineWith(s):
    sys.stdout.write('\r')
    sys.stdout.flush()
    sys.stdout.write(s)
    sys.stdout.flush()

# compile all regexs
urlRe = re.compile(r"(http|ftp|https):\/\/([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?")
ampRe = re.compile(r"&amp;")
gtRe = re.compile(r"&gt;")
ltRe = re.compile(r"&lt;")
nbspRe = re.compile(r"&nbsp;")
sqtRe = re.compile(r"&quote;")
dqtRe = re.compile(r"&apos;")
nwsRe = re.compile(r"[\n\t\r]")
mentionRe = re.compile(r"@\w*(\s|\b)")
hashtagRe = re.compile(r"#\w*(\s|\b)")
englRe = re.compile(r"[^1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!()\".,;:\' ]")
spPuncRe = re.compile(r"\s([.,;:])")
multSpaceRe = re.compile(r"\s{2,}")

# get our emoji json data
with open(JSON_FNAME, "r") as f:
    ourEmojiData = json.load(f)

ourEmojiCodes = [code for code in ourEmojiData] # all our emoji codes
unImportedCodes = [code for code in ourEmojiCodes if not ourEmojiData[code]['imported']]
importedCodes = [code for code in ourEmojiCodes if ourEmojiData[code]['imported']]

# import everything that hasn't been set as imported
codesImported = 0
for code in importedCodes:
    print('Already imported and sanitized "{}"'.format(code))
for code in unImportedCodes:
    # print progress
    codesImported += 1
    print("Analyzing code {}/{}/{} ({})".format(codesImported, len(unImportedCodes), len(ourEmojiCodes), code))

    # import the tweets from all downloaded files
    myDir = os.listdir(os.fsencode("{}/raw/{}".format(DIR_PREFIX, code)))
    filesImported = 0
    allTweets = []
    for file in myDir: # read tweets into list
        fileName = os.fsdecode(file)
        if fileName != "desktop.ini": # stupid hidden files UGH
            filePath = "{}raw/{}/{}".format(DIR_PREFIX, code, fileName)
            try:
                with open(filePath, "r") as f:
                    myTweets = json.load(f)
                    allTweets.extend(myTweets)
                    filesImported += 1
                replaceLineWith("  Importing {}/{}".format(filesImported, len(myDir)))
            except Exception as e:
                print("\nFailed to read JSON from {}".format(filePath))

    if filesImported > 0:
        print()
        # clean all tweets for this emoji code
        cleanedTweets = []
        cleaned = 0
        for tweet in allTweets:
            cleaned += 1 

            # print progress
            replaceLineWith('  Sanitizing {}/{}/{}'.format(len(cleanedTweets), cleaned, len(allTweets)))

            newTweet = urlRe.sub("", tweet) # remove all links
            newTweet = mentionRe.sub(" ", newTweet)  # remove mentions
            newTweet = hashtagRe.sub(" ", newTweet)  # remove hashtags
            newTweet = ampRe.sub(" and ", newTweet) # replace HTML ampersands, add extra spaces
            newTweet = gtRe.sub(">", newTweet) # replace HTML greater than
            newTweet = ltRe.sub("<", newTweet) # replace HTML less than
            newTweet = nbspRe.sub(" ", newTweet) # replace HTML space
            newTweet = sqtRe.sub("\'", newTweet) # replace HTML single quotes
            newTweet = dqtRe.sub("\"", newTweet) # replace HTML double quotes
            newTweet = nwsRe.sub(" ", newTweet) # remove all non-space whitespace
            newTweet = englRe.sub("", newTweet) # keep only english characters and punctuation 
            newTweet = spPuncRe.sub(r"\1", newTweet) # remove spaces before ending punctuation
            newTweet = multSpaceRe.sub(" ", newTweet) # remove multiple whitespaces

            if newTweet and not newTweet.isspace():
                cleanedTweets.append(newTweet.strip())

        print()

        # update json data for this code
        ourEmojiData[code]['total-tweets'] = len(allTweets)
        ourEmojiData[code]['sanitized-tweets'] = len(cleanedTweets)
        ourEmojiData[code]['imported'] = True
        ourEmojiData[code]['cleaned'] = False

        # write all tweets for this code to new file
        with open("{}/sanitized/{}.json".format(DIR_PREFIX, code), "w+") as f:
            json.dump(cleanedTweets, f, indent=4)

    # update our emoji json after every code
    with open(JSON_FNAME, "w") as f:
        json.dump(ourEmojiData, f, indent=4)

print()
sys.stdout.flush()