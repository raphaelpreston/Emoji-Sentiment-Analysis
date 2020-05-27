import watsonTools
import json
import sys
import time
import os

DIR_PREFIX = "training_tweets/"
JSON_FNAME = "our_emojis.json"

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
trainedCodes = [code for code in cleanedCodes if ourEmojiData[code].get('trained-tweets', 0) > 0]
dontTrainCodes = [code for code in importedCodes if ourEmojiData[code].get('dont-train', False)]
codesToTrain = [code for code in cleanedCodes if code not in dontTrainCodes]

# --- for testing
codesToTrain = codesToTrain[:4]
# ---

# load in all the clean tweets for each code
cleanTweets = {code: [] for code in ourEmojiCodes}
for code in cleanedCodes:
    with open("{}cleaned/{}.json".format(DIR_PREFIX, code)) as f:
        cleanTweets[code] = json.load(f)

# load in all the tweets already trained
tweetsTrained = {code: [] for code in ourEmojiCodes}
for code in trainedCodes:
    fPath = "{}trained/{}.json".format(DIR_PREFIX, code)
    if os.path.exists(fPath):
        with open(fPath, 'r') as f:
            tweetsTrained[code] = json.load(f)
    else:
        input("Code {} had {} trained tweets but no file with the trained" \
              "tweets. Restting count and continuing on keypress.".format(code, ourEmojiData[code]['trained-tweets']))
        ourEmojiData[code]['trained-tweets'] = 0


totalToTrain = 15 # the total number of tweets to train this round
print("Training {} tweets for {} untrained codes. That's about {} tweets per code:".format(
    totalToTrain, len(codesToTrain), totalToTrain // len(codesToTrain)
))

# get sentiments from each code in batches
numNewTweetsTrained = {code: 0 for code in codesToTrain} # num of tweets trained per originally untrained code
tweetsTrainedThisRound = 0
currCodeIndex = 0
while tweetsTrainedThisRound < totalToTrain:

    code = codesToTrain[currCodeIndex]

    # print progress
    replaceLineWith(", ".join([
        "{} ({}/{}/{})".format(
            c,
            numNewTweetsTrained[c], # tweets trained this round
            len(tweetsTrained[c]), # total tweets trained for this code
            ourEmojiData[c]['clean-tweets'] # num clean tweets available to train
        ) for c in codesToTrain
    ]))

    numTweetsTrained = numNewTweetsTrained[code]
    totalTweetsTrained = len(tweetsTrained[code])
    if numTweetsTrained < ourEmojiData[code]['clean-tweets']: # there are more tweets to train
        tweet = cleanTweets[code][totalTweetsTrained]

        # train and save results of training for next tweet
        watsonTools.scores_from_tweets_to_df([tweet], code, "training_results.csv")

        # update data
        if 'trained-tweets' in ourEmojiData[code]:
            ourEmojiData[code]['trained-tweets'] += 1
        else:
            ourEmojiData[code]['trained-tweets'] = 0
        tweetsTrained[code].append(tweet)

        # re-write our JSON info
        with open(JSON_FNAME, "w") as f:
            json.dump(ourEmojiData, f, indent=4)
        
        # re-write the tweets that have been trained for this code
        with open('{}trained/{}.json'.format(DIR_PREFIX, code), 'w') as f:
            json.dump(tweetsTrained[code], f, indent=4)
        
        numNewTweetsTrained[code] += 1
        tweetsTrainedThisRound += 1

    # wrap to next code
    currCodeIndex = (currCodeIndex + 1 ) % len(codesToTrain)

# flush out a newline
sys.stdout.write("\n")
sys.stdout.flush()


    