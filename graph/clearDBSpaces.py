from util import textUtil as tu
import pandas as pd

url_database = "/home/user/Downloads/data_learnpair.csv"
url_database_cleared = "/home/user/Downloads/data_learnpair_cleared.csv"


base = pd.read_csv(url_database,sep="|")
base.drop(base.columns[6], axis=1, inplace=True)
base.drop(base.columns[6], axis=1, inplace=True)

Col = ['category','input','output']
for column in Col:
    base[column] = base[column].apply(lambda x: tu.regexClean(x))

base.to_csv(url_database_cleared,sep="|",columns=["id","category","input","ouput","createdDate","userid"],index=False)