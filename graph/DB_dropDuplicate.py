from util import textUtil as tu
import pandas as pd

url_database = "/home/user/Desktop/230317/data_learnpair_tended.csv"
base = pd.read_csv(url_database,sep="|")
base.drop(base.columns[6], axis=1, inplace=True)
base.drop(base.columns[6], axis=1, inplace=True)

Col = ['category','input','output']
for column in Col:
    base[column] = base[column].apply(lambda x: str(tu.regexClean(x)).lower())

sLen = len(base)

idexist = [x['id'] for i,x in base.iterrows()]

base = base.drop_duplicates(subset=['category', 'input', 'output'])

cLen = len(base)

idexist = sorted(idexist)
idunic = [x['id'] for i,x in base.iterrows()]
idunic = sorted(idunic)

print (idexist)
print (idunic)

print (len(idexist))
print (len(idunic))

exclue = [x for x in idexist if x not in idunic]

print (exclue)
print (len(exclue))