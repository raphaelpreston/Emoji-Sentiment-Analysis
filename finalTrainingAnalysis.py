import json
import pandas as pd
import sys
import csv

def replaceLineWith(s):
    sys.stdout.write('\r')
    sys.stdout.flush()
    sys.stdout.write(s)
    sys.stdout.flush()

# import the training results
analResults = {}
results = pd.read_csv("training_results.csv", index_col=0)
for index, row in results.iterrows():
    code = row['label']
    if code not in analResults:
        analResults[code] = {
            "n": 1,
            "joy": row['joy'],
            "tentative": row['tentative'],
            "confident": row['confident'],
            "analytical": row['analytical'],
            "sadness": row['sadness'],
            "fear": row['fear'],
            "anger": row['anger'],
        }
    else:
        analResults[code]["n"] += 1
        analResults[code]["joy"] += row['joy']
        analResults[code]["tentative"] += row['tentative']
        analResults[code]["confident"] += row['confident']
        analResults[code]["analytical"] += row['analytical']
        analResults[code]["sadness"] += row['sadness']
        analResults[code]["fear"] += row['fear']
        analResults[code]["anger"] += row['anger']

# compute averages
aves = ["code,n,joy,tentative,confident,analytical,sadness,fear,anger".split(",")]
for code, details in analResults.items():
    aves.append([
        code,
        details['n'],
        details["joy"],
        details["tentative"],
        details["confident"],
        details["analytical"],
        details["sadness"],
        details["fear"],
        details["anger"],
    ])

with open("training_results_metadata.csv","w+") as f:
    csvWriter = csv.writer(f, delimiter=',')
    csvWriter.writerows(aves)


