#%% [markdown]
## Mapping Toronto Neighbourhoods
# This program scrapes the Toronto Wikipedia page on Toronto neighbourhoods, adds longitude and latitude, and then maps the neighbourhoods.

#%%
from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np

#%% [markdown]
### Get Data
# Use beautiful soup to scrape the data of Canadian postal codes,
# Find the wikitable in the soup and put it into postalTable

page = requests.get('https://en.wikipedia.org/wiki/List_of_postal_codes_of_Canada:_M')
soup = BeautifulSoup(page.text,'html.parser')
#print(soup.prettify)
postalTable = soup.find('table', class_='wikitable')
#print(postalTable)
#print(postalTable.tbody.text)

#%% [markdown]
### Cleaning Data & Creating DataFrame
# Currently, postalTable.text represents each row of the wikitable as five entries separated by linebreaks.  The first two entries
# are blank, while the remaining three correspond to the columns of the wikitable.  Moreover, the first row contains headers rather 
# than column names.  This section will push this data into a list, and use a for loop w/ three indices to gather the data into
# a three-column list, which will then be converted to a dataframe.
# This function will simultaneously clean the data--skipping over postcodes with unassigned boroughs, grouping neighbourhoods that
# share a borough into a single neighbourhoods entry, and giving unassigned neighbourhoods their borough name.

#%%
list_postalTable = postalTable.text.split('\n')
length = int(len(array_postalTable)-2)
last = "NOPE"
i = -1 # cannot use enumerate in this particular case
df_postalTable = [] #actually a list at this point
for post, bor, neigh in zip(list_postalTable[7:length:5], list_postalTable[8:length:5], list_postalTable[9:length:5]):
    print(f'{post}, {bor}, {neigh}')
    if bor=='Not assigned':
        continue
    if post==last:
        if neigh == 'Not assigned':
            neigh = bor
        df_postalTable[i][2] = f'{df_postalTable[i][2]}, {neigh}'
        continue
    # else this is a new postal code, perhaps a new borough
    if neigh == 'Not assigned':
        neigh = bor
    df_postalTable.append([post, bor, neigh])
    i+=1
    last = post
df_postalTable = pd.DataFrame(df_postalTable)
df_postalTable.columns = ['Postcode','Borough','Neighbourhood']
df_postalTable
#%%
