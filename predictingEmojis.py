#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 28 21:48:08 2020

@author: isheerin
"""

import pandas as pd
import joblib as joblib
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import ToneAnalyzerV3

import json
from http.server import HTTPServer, BaseHTTPRequestHandler


## INPUTS
apiKEY = "opBx3zPqgE56cqb8LqK6HUJFipYv3xTRkrikHGHEEZcQ"
apiURL = 'https://api.us-south.tone-analyzer.watson.cloud.ibm.com/instances/266134d5-d618-4a4e-a1e8-28b0e728f50e'
testTweet = "Alright good night. Remember to wash off your face before you go to bed so you don't fuck up your real face any more."
modelPathname = "/Users/isheerin/Desktop/Emoji_Model.pkl"  # pathname to model


## Use your own api-key, and api website link
authenticator = IAMAuthenticator(apiKEY)
service = ToneAnalyzerV3(version='2020-05-25', authenticator=authenticator)
service.set_service_url(apiURL)



# function that takes tweet and  gets sentiment score from watson
def tweet_score(tweet): # input: string; return: vector
       
    # call watson api
    tone_chat = service.tone(tweet, content_type="text/plain", sentences=False).get_result()    
    return tone_chat

# prediction function
def predict_emoji(message, modelPathname): #input test string, pathname to model ; output: emoji (string)
    
    response = tweet_score(message)
    model = joblib.load(modelPathname)
    column_names = pd.Index(['joy', 'tentative', 'confident', 'analytical', 'sadness', 'fear', 'anger'])
    
    df = pd.DataFrame(columns = column_names)
    df = df.append(pd.Series(0, index=df.columns), ignore_index=True)
    
    if 'document_tone' in response:
            if 'tones' in response['document_tone']:
                for s in list(response['document_tone']['tones']):

                    if s['tone_id'] in df.columns:
                        df.loc[df.index[-1],s['tone_id']] = s['score']
                        
    return model.predict(df)


# Backend code START
class Serve(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == '/':
            self.path = '/index.html'

        try:
            file_to_open = open("predictingEmojis.py").read()
            self.send_response(200)
        except:
            file_to_open = "File Rafa found"
            self.send_response(404)

        self.end_headers()
        self.wfile.write(bytes(file_to_open, 'utf-8'))

    def do_POST(self):
        
        body = self.rfile.read(int(self.headers['Content-Length']))

        self.send_response(2000)
        self.end_headers()

        body = json.loads(body.decode())

        print(body['tweet'])

        result = predict_emoji(body['tweet'], modelPathname)
        print(result)

        self.wfile.write(bytes(result[0], 'utf-8'))


httpd = HTTPServer(('localhost', 8000), Serve)
httpd.serve_forever()
# Backend code END
