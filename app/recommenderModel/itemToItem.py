import pandas as pd

data = pd.read_csv('wolf.csv')
print(data.head())

data['contentId'] = data['contentId'].astype(str) 
DfMatrix = pd.pivot_table(data, values='like', index='userId', columns='contentId')
print(DfMatrix.head())

DfMatrix=DfMatrix.fillna(0) 
#NaN values need to get replaced by 0, meaning they have not been purchased yet.
DfMatrixNorm3 = (DfMatrix-DfMatrix.min())/(DfMatrix.max()-DfMatrix.min())
print(DfMatrixNorm3.head())

DfResetted = DfMatrix.reset_index().rename_axis(None, axis=1) 
print(DfResetted.head() )
#Now each row represents one customer`s buying behaviour: 1 means the customer has purchased, NaN the customer has not yet purchased it

DfMatrix.shape
df=DfResetted 
df=df.fillna(0) 
print(df.head())

DfCounterShortName = df.drop(['userId'], axis=1) 
print(DfCounterShortName.head())

import numpy as np
DfCounterShortNameNorm = DfCounterShortName/np.sqrt(np.square(DfCounterShortName).sum(axis=0))   
print("Norm", DfCounterShortNameNorm.head())

ItemItemSim = DfCounterShortNameNorm.transpose().dot(DfCounterShortNameNorm) 
print(ItemItemSim.head())

ItemNeighbours = pd.DataFrame(index=ItemItemSim.columns,columns=range(1,10))
print(ItemNeighbours.head())

for i in range(0,len(ItemItemSim.columns)): 
    ItemNeighbours.iloc[i,:9] = ItemItemSim.iloc[0:,i].sort_values(ascending=False)[:9].index 
    #we only have 9 items, so we can max recommend 9 items (itself included) 
print(ItemNeighbours.head())

ItemNeighbours.head().iloc[:11,1:9]
#it needs to start at position 1, because position 0 is item itself

# You might want to export this result to Excel now
ItemNeighbours.to_excel('wolf-result.xlsx')