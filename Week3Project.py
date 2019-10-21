#%% [markdown]
## Mapping Toronto Neighbourhoods
# This program scrapes the Toronto Wikipedia page on Toronto neighbourhoods, adds longitude and latitude, and then maps the neighbourhoods.

#%%
# All imports should be here
from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
from geopy.geocoders import Nominatim # module to convert an address into latitude and longitude values
from sklearn.cluster import KMeans 
import folium # plotting library


#%% [markdown]
### Get Data
# Use beautiful soup to scrape the data of Canadian postal codes,
# Find the wikitable in the soup and put it into postalTable
#################################################################################################################
page = requests.get('https://en.wikipedia.org/wiki/List_of_postal_codes_of_Canada:_M')
soup = BeautifulSoup(page.text,'html.parser')
#print(soup.prettify)
postalTable = soup.find('table', class_='wikitable')
# Had some memory trouble running program--so I'll be deleting large varibles
del soup
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
#################################################################################################################

#%%
list_postalTable = postalTable.text.split('\n')
length = int(len(list_postalTable)-2)
last = "NOPE"
i = -1 # cannot use enumerate in this particular case
df_postalTable = [] #actually a list at this point
for post, bor, neigh in zip(list_postalTable[7:length:5], list_postalTable[8:length:5], list_postalTable[9:length:5]):
#    print(f'{post}, {bor}, {neigh}')
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
del list_postalTable
df_postalTable

#%% [markdown]
### Adding Latitude and Longitude
# Uses nominatim with a fourquare agent to add the data to df_postalTable
#################################################################################################################
#%%
# Define a function to make this a little quicker
def latlong(neighbourhood):

    address = neighbourhood + ", Toronto, Canada"
#    return address
    geolocator = Nominatim(user_agent="foursquare_agent")
    loc = geolocator.geocode(address)
    return loc.latitude, loc.longitude

#%%
# Add latitude and longitude data
# A nested for-loop is used to iterate through the neighbourhoods in a borough until one that gives valid coordinates is found
# Exceptions are used as it is unclear whethere an address will work before trying it 
lats = []
longs = []
for i, (borough, neighbourhood) in enumerate(zip(df_postalTable['Borough'], df_postalTable['Neighbourhood'])):
#    print(f'{borough}, {neighbourhood}.')
    for n in neighbourhood.split(','):
        try:
            lat, long = latlong(n)
        except:
            try:
                lat, long = latlong(f'{n}, {borough}')
            except:
                continue
        break                                                    
    longs.append(long)
    lats.append(lat)
df_postalTable['Longitude'] = longs
df_postalTable['Latitude'] = lats

#%%
print(f'The shape of the table is: {df_postalTable.shape}')
df_postalTable.head(12)

#%% [markdown]
### Cluster the Neighborhoods
# I've decided simply to use kmeans similar to the Manhattan assignment.  However,
# I have dropped the number of clusters to four as I did not like the one-neighbourhood
# clusters.  Also, unlike with Manhattan, I am doing this by postcode rather than neighbour
# as that is how the assignment groups the data and trying to go down another level would
# seriously slow down this assignment.
##################################################################################################################

#%%
def FSExploreLoc(latitude=43.75880, longitude=-79.320197, CLIENT_ID = 'RJ2TAOE50JVYUTGUY0W0HNVMEWPHWN4LJJ2CSVJL1NYUY43P', CLIENT_SECRET = 'WV3VMFHZINCZWXWH1VKWWVWNFD3I1XWY2IFFXI5KJPGHUM3G', VERSION = '20180605', LIMIT = 100, RADIUS = 500):
    return f'https://api.foursquare.com/v2/venues/explore?client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}&ll={latitude},{longitude}&v={VERSION}&limit={LIMIT}&radius={RADIUS}'
# latitude and longitude defaults are set in case a set of inputs cause errors and workable inputs are needed
#Defaults are set for my foursquare account

#%%
def GetManyNearbyVenues(names, lats, longs, radius = 500, limit = 100):
    #ensure names is a list
    if type(names) == type('string'):
        names = names.split(',')
    l_venues = []
    # long is taken
    for name, lat, lng in zip(names, lats, longs):
        results = GetNearbyVenues(name, lat, lng, radius, limit)
        l_venues.append([(
            name,
            lat,
            lng,
            v['venue']['name'],
            v['venue']['location']['lat'],
            v['venue']['location']['lng'],
            v['venue']['categories'][0]['name']) for v in results])
    nearby_venues = pd.DataFrame([item for l_venues in l_venues for item in l_venues])
    nearby_venues.columns = ['Postcode',
            'Postcode Latitude','Postcode Longitude',
            'Venue',
            'Venue Latitude','Venue Longitude',
            'Venue Category']
    return nearby_venues
# split the function in two to make it more easily tested
def GetNearbyVenues(name, lat, lng, radius, limit):
    url = FSExploreLoc(lat, lng, LIMIT = limit, RADIUS = radius)
    try:
        return requests.get(url).json()["response"]['groups'][0]['items']
    except:
        print(f'Error at {name}, lat {lat} and lng {lng}')
        return(FSExploreLoc())

#%%
venues =GetManyNearbyVenues(df_postalTable.Postcode,df_postalTable.Latitude,df_postalTable.Longitude, 500, 100)

torontoVenues = pd.get_dummies(venues[['Venue Category']], prefix="",prefix_sep="")
torontoVenues['Postcode']=venues['Postcode']
fixedColumns = [torontoVenues.columns[-1]] + list(torontoVenues.columns[:-1])
torontoVenues = torontoVenues[fixedColumns]
torontoVenues = torontoVenues.groupby('Postcode').mean().reset_index()

del venues
#torontoVenues

#%%
kclusters = 4  #Reduced number of clusters--two clusters had only one member before
torontoClusters = torontoVenues.drop('Postcode', axis=1)

kmeans = KMeans (n_clusters = kclusters, random_state=0).fit(torontoClusters)
del torontoClusters
#kmeans.labels_

#%%
def return_most_common_venues(row, num_top_venues):
    row_categories = row.iloc[1:]
    row_categories_sorted = row_categories.sort_values(ascending=False)
    
    return row_categories_sorted.index.values[0:num_top_venues]


#%%
num_top_venues = 5

indicators = ['st', 'nd', 'rd']

# create columns according to number of top venues
columns = ['Postcode','Cluster']
for ind in np.arange(num_top_venues):
    try:
        columns.append('{}{} Most Common Venue'.format(ind+1, indicators[ind]))
    except:
        columns.append('{}th Most Common Venue'.format(ind+1))


# create a new dataframe
postcode_venues_sorted = pd.DataFrame(columns=columns)
postcode_venues_sorted['Postcode'] = torontoVenues['Postcode']
postcode_venues_sorted['Cluster'] = kmeans.labels_

for ind in np.arange(torontoVenues.shape[0]):
    postcode_venues_sorted.iloc[ind, 2:] = return_most_common_venues(torontoVenues.iloc[ind, :], num_top_venues)

#postcode_venues_sorted.insert(0, 'Cluster Labels', kmeans.labels_)

#postcode_venues_sorted.head()


#%%
torontoSortedVenues = postcode_venues_sorted.join(df_postalTable.set_index('Postcode'), on='Postcode')
fixedColumns =[ torontoSortedVenues.columns[0]] + list(torontoSortedVenues.columns[-4:-2]) + [torontoSortedVenues.columns[1]] + list(torontoSortedVenues.columns[2:7]) + list (torontoSortedVenues.columns[9:11])
#print(fixedColumns)
torontoSortedVenues=torontoSortedVenues[fixedColumns]
torontoSortedVenues
#df_postalTable.join(postcode_venues_sorted.set_index('Postcode'), on='Postcode')

#%%
# Clearing up space
# Need to get a desktop
# Other deletions scattered thoughout code for efficiency
del kmeans
del postcode_venues_sorted
del df_postalTable
del fixedColumns
del torontoVenues

#%% [markdown]
### Examining Toronto Neighbourhood Clusters
#################################################################################################################
#### Cluster 0

#%%
torontoSortedVenues.loc[torontoSortedVenues['Cluster'] ==0, list(torontoSortedVenues.columns[0:2]) + list(torontoSortedVenues.columns[4:9])]
#%% [markdown]
#### Cluster 1

#%%
torontoSortedVenues.loc[torontoSortedVenues['Cluster'] ==1, list(torontoSortedVenues.columns[0:2]) + list(torontoSortedVenues.columns[4:9])]

#%% [markdown]
#### Cluster 2
#%%
torontoSortedVenues.loc[torontoSortedVenues['Cluster'] ==2, list(torontoSortedVenues.columns[0:2]) + list(torontoSortedVenues.columns[4:9])]

#%% [markdown]
#### Cluster 3

#%%
torontoSortedVenues.loc[torontoSortedVenues['Cluster'] ==3, list(torontoSortedVenues.columns[0:2]) + list(torontoSortedVenues.columns[4:9])]

#%% [markdown]
### Putting Clusters on Map
# Map sometimes has trouble loading.
#################################################################################################################

#%%
tClusterMap = folium.Map(location=[43.68809, -79.3940935], zoom_start=12) # generate map centred around Ecco

cluster = 0
these = torontoSortedVenues.Cluster == cluster
for lat, lng in zip(torontoSortedVenues.Latitude[these],torontoSortedVenues.Longitude[these]):
    folium.CircleMarker(
        [lat, lng],
        radius=5,
        popup=f'({lat}, {lng})',
        fill=True,
        color='blue',
        fill_color='blue',
        fill_opacity=0.6
        ).add_to(tClusterMap)
cluster = 1
these = torontoSortedVenues.Cluster == cluster
for lat, lng in zip(torontoSortedVenues.Latitude[these],torontoSortedVenues.Longitude[these]):
    folium.CircleMarker(
        [lat, lng],
        radius=5,
        popup=f'({lat}, {lng})',
        fill=True,
        color='red',
        fill_color='red',
        fill_opacity=0.6
        ).add_to(tClusterMap)
cluster = 2
these = torontoSortedVenues.Cluster == cluster
for lat, lng in zip(torontoSortedVenues.Latitude[these],torontoSortedVenues.Longitude[these]):
    folium.CircleMarker(
        [lat, lng],
        radius=5,
        popup=f'({lat}, {lng})',
        fill=True,
        color='green',
        fill_color='green',
        fill_opacity=0.6
        ).add_to(tClusterMap)
cluster = 3
these = torontoSortedVenues.Cluster == cluster
for lat, lng in zip(torontoSortedVenues.Latitude[these],torontoSortedVenues.Longitude[these]):
    folium.CircleMarker(
        [lat, lng],
        radius=5,
        popup=f'({lat}, {lng})',
        fill=True,
        color='brown',
        fill_color='brown',
        fill_opacity=0.6
        ).add_to(tClusterMap)

# display map
tClusterMap
#%%