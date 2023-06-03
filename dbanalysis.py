import pandas as pd
from itertools import chain
import csv


# def replacer(row):
#     row = row.replace("[","").replace("]","")
#     return row
df = pd.read_csv('1.csv', delimiter=';')
df2 = df.loc[:, ["salary","keyskills"]]
# df2 = df2.apply(replacer,axis="columns")
for i, row in df2.iterrows():
    skillstring = df2.iat[i,1]
    
    skillstring = skillstring.replace("[","").replace("]","").replace("'","").split(',')
    print(type(skillstring))
    print(skillstring)

