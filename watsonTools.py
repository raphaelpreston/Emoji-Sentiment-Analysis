#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 21 21:12:01 2020

@author: isheerin, raphaelpreston
"""
import pandas as pd
import sklearn as sk
import numpy as np
import os
from sklearn.multiclass import OneVsRestClassifier
from sklearn.svm import SVC
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import ToneAnalyzerV3

from myWatsonInfo import API_KEY, URL


## Use your own api-key, and api website link. put in myWatsonInfo.py
authenticator = IAMAuthenticator(API_KEY)
service = ToneAnalyzerV3(version='2020-05-25', authenticator=authenticator)
service.set_service_url(URL)


# function that takes tweet and gets sentiment score from watson
def tweet_score(tweet): # input: string; return: vector
       
    # call watson api
    tone_chat = service.tone(tweet, content_type="text/plain", sentences=False).get_result()    
    return tone_chat


# creates multilabel classfication model from csv
def multi_class_model_train_from_csv(pathname): #input: string of path to file; output: model
    df_data = pd.read_csv(pathname)
    scores = df_data.iloc[:,0:len(df_data.columns)-1]
    labels = df_data.iloc[:,-1]
    
    # intitialize model and fit data
    clf = OneVsRestClassifier(SVC())
    
    # train model
    clf = clf.fit(scores, labels)
    
    # return model object
    return clf

# creates multilabel classification model from dataframe
def multi_class_model_train_from_dataframe(df): # input: dataframe object with data, output: model
    scores = df.loc[:, df.columns != 'label']
    labels = df.loc[:, 'label']
    
    # intitialize model and fit data
    clf = OneVsRestClassifier(SVC())
    
    # train model
    clf = clf.fit(scores, labels)
    
    # return model object
    return clf    


# prediction function
def predict_emoji(message, model, column_names): #input string, model, names of columns of dataframe; output: emoji (string)
    response = tweet_score(message)
    
    df = pd.DataFrame(columns = column_names)
    df = df.append(pd.Series(0, index=df.columns), ignore_index=True)
    if 'document_tone' in response:
            if 'tones' in response['document_tone']:
                for s in list(response['document_tone']['tones']):

                    if s['tone_id'] in df.columns:
                        df.loc[df.index[-1],s['tone_id']] = s['score']
                        
    return model.predict(df)

# create data csv for model from raw data csv
# pathname 1: csv: tweets, emoji
# pathname 2: where to save second csv
def scores_csv_from_raw_data(pathname1, pathname2): #input: string, string
    
    # initialize data frames
    df_raw = pd.read_csv(pathname1)
    df_scores = pd.DataFrame()
    
    # get sentiment scores and add to dataframe
    for i in range(len(df_raw)) : 
        scores = tweet_score(df_raw.iloc[i, 0])
        df_scores.loc[i] = scores + [df_raw.iloc[i, 1]]
        
    # save dataframe to csv
    df_scores.to_csv(pathname2)
    
    
# tweets is array of strings (all messages for training), label is string of label
# only one label at a time
# could call function multiple times and append resulting dataframes
# output is dataframe
# pathtoCSV is the path to the input/output CSV file
def scores_from_tweets_to_df(tweets, label, pathToCSV=None):

    # import from pathToCSV if there's already a file there
    if pathToCSV is None or not os.path.exists(pathToCSV):
        df_scores = pd.DataFrame()
    else:
        try:
            df_scores = pd.read_csv(pathToCSV, index_col=0)
        except:
            df_scores = pd.DataFrame()
    
    for t in tweets:
        # check to see if we've already analyzed this tweet
        if 'tweet' in df_scores and t in df_scores['tweet'].values:
            existed = True
            ind = df_scores[df_scores['tweet'] == t].index[0]
            row = df_scores.iloc[ind]
            tones = ['joy','confident','tentative','sadness','analytical','anger','fear']
            response = {
                'document_tone': {
                    'tones': [{'score': row[tone], 'tone_id': tone} for tone in tones if row[tone] != 0]
                }
            }
        else: # otherwise, query watson
            response = tweet_score(t)
            existed = False
        if 'document_tone' in response:
            if 'tones' in response['document_tone']:
                if 'label' not in df_scores.columns:
                    df_scores.loc[:,'label'] = pd.Series(0, index=df_scores.index)
                if 'tweet' not in df_scores.columns:
                    df_scores.loc[:,'tweet'] = pd.Series(0, index=df_scores.index)
                df_scores = df_scores.append(pd.Series(0, index=df_scores.columns), ignore_index=True)
                for s in list(response['document_tone']['tones']):

                    if s['tone_id'] in df_scores.columns:
                        df_scores.loc[df_scores.index[-1],s['tone_id']] = s['score']
                    
                    else:
                        df_scores.loc[:,s['tone_id']] = pd.Series(0, index=df_scores.index)
                        df_scores.loc[df_scores.index[-1],s['tone_id']] = s['score']
                    
                df_scores.loc[df_scores.index[-1], 'label'] = label
                df_scores.loc[df_scores.index[-1], 'tweet'] = t
    
    # save the file to the same path
    if pathToCSV is not None:
        df_scores.to_csv(pathToCSV)
    return existed # to keep track of how many calls were actually made


if __name__ == "__main__": # don't run if just imported
    # sample response: {'document_tone': {'tones': [{'score': 0.84639, 'tone_id': 'tentative', 'tone_name': 'Tentative'}]}}
    tweet = "It has a character that is similar to Jet from Cowboy Bebop that might also be voiced by the same actor. A little bit of comfort"

    scores_from_tweets_to_df([tweet], 'code1', "training_results.csv")


    # ## Examples
    # pathname1 = ""
    # pathname2 = ""
    # message = "Hi I love pandas! Do you like pandas?"
    # message2 = "Where is the cereal? I need my cereal"
    # test = [message, message2]

    # # Examples running
    # df = scores_from_tweets_to_df(test, "100cool")
    # model = multi_class_model_train_from_dataframe(df)
    # result = predict_emoji("I like elephants", model, df.columns)
    # print(result)


