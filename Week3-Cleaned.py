#%%
from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
from geopy.geocoders import Nominatim # module to convert an address into latitude and longitude values
from sklearn.cluster import KMeans 
import folium # plotting library
from statistics import mean # why the hell isn't this function in by default?

#%% [markdown]
# Definitions
# This time I'm going to make better use of definitions so that the code is reusable

#%%
def PrepareSoup(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.text,'html.parser')
    return soup
#    return (soup.find('table', class_ = 'wikitable'))

def WikiToTable(tableSoup):
    #should be given soup.tbody data
    rows = tableSoup.find_all('tr')
    df = [] #list for now
    for r in rows:
        nRow = r.find_all('td')
        for i in range(len(nRow)):
            nRow[i] = nRow[i].text
        df.append(nRow)
    df = pd.DataFrame(df)
    return df

def FindWikitableWidth(wikitable, ref1,ref2):
    if type(wikitable)==str: # should then be a list
        return FindWikitableWidth(wikitable.split('\n'), ref1, ref2)
    for p1 in range(len(wikitable)):
        if wikitable[p1] == ref1:
            break
    for p2 in range(len(wikitable)):
        if wikitable[p2] == ref2:
            break
    return abs(p2 - p1)

def PrepTable(soup):
    ll = []
    for l in neighSeattle.find_all('td'):
        ll.append(l.text)
    return ll


#%%
# This shall probably be the least reliable function
def FixWikiTable(wikitable, l_wantedColumns, width=0, ref1="Nope", ref2="Nope"):
    # takes wikitable as a string with the header included
    # l_wantedColumns must include elements in the header desired
    # width contains the number of columns in the wikitable

    wikitable = wikitable.text.split('\n')
    for i, w in enumerate(wikitable):
        if w=='':
            del wikitable[i]

    if width==0:
        width = FindWikitableWidth(wikitable,ref1,ref2)    

    wanted = []
    for w in l_wantedColumns:
        for i,l in enumerate(wikitable):
            if l == w:
                wanted.append(i)
                break
    if len(wanted) != len(l_wantedColumns):
        print('ERROR: Not all wanted columns in list')
        return(0)
    length = len(wikitable)
    df = {} # currently a dictionary
    # need the i for some complex indexing here, so won't 
    for l, w in zip(l_wantedColumns, wanted):
        df[l] = wikitable[w :length :width]
#        print(f'{w} : {length} : {width}')
#        print(f'{w} length is {len(df[l])}')
#        print(wikitable[w :length :width])
#    df = pd.DataFrame(df)
    return df

#%%
# Takes a string or list of strings, and returns the same
# In case of receiving a list, uses recursion
def RobustMean(l):
    l.drop(labels = None, inplace = True)
    return mean(l)
#%%
def LatLong(address):
    if type (address) == list:
        lats = []
        longs = []
        for a in address:
            lat, lng = LatLong(a)

            lats.append(lat)
            longs.append(lng)
        return lats, longs
    slash = address.find('/')
    if address.find('/') != -1:
        lats = []
        longs = []
        for a in LatLong(address.split('/')):
            lat, lng = LatLong(a)
            lats.append(lat)
            longs.append(lng)
            return(RobustMean(lats),RobustMean(longs))
    geolocator = Nominatim(user_agent="foursquare_agent")
    try:
        loc = geolocator.geocode(address)
        return loc.latitude, loc.longitude
    except:
        print(f'ERROR AT: {address}')
        return -49.51, -128.34

#%%
def MultiConcatenate(ll, s, append = True):

    rList = [] # was getting crazy errors while modifying ll directly    
    # This function appends (by default) of pre-pends (...there's a word for that) a string to all elements in a list
    if append:
        if type(s) == str:
            for l in ll:
                rList.append(f'{l}, {s}')
        else:
            for l, s2 in zip(ll, s):
                rList.append(f'{l}, {s2}')
    else:
        if type(s) == str:
            for l in ll:
                rList.append(f'{l}{s}')
        else:    
            for l, s2 in zip(ll, s):
                rList.append(f'{l}, {s2}')
    return (rList)
#addresses = MultiConcatenate(neighSeattle['Neighborhood'], 'Seattle, WA, USA')
#addresses

#%%
def RemoveBrackets(s,t='all'):
    if t=='all':
        s = RemoveBrackets(s,'()')
        s = RemoveBrackets(s,'[]')
        s = RemoveBrackets(s,'{}') # off-coloring does not mean an error here
        return s
    while True:
        startCut = s.find(t[0])
        if startCut ==-1:
            break
        endCut = s.find(t[1]) +1
        s = f"{s[0:startCut]}{s[endCut:]}"
    return s

def RemoveSymbol(s,t):
    length = len(t)
    while True:
        startCut = s.find(t)
        if startCut ==-1:
            break
        endCut = startCut + length
        s = f"{s[0:startCut]}{s[endCut:]}"
    return s

#%%
def FSExploreLoc(latitude=43.75880, longitude=-79.320197, CLIENT_ID = 'RJ2TAOE50JVYUTGUY0W0HNVMEWPHWN4LJJ2CSVJL1NYUY43P', CLIENT_SECRET = 'WV3VMFHZINCZWXWH1VKWWVWNFD3I1XWY2IFFXI5KJPGHUM3G', VERSION = '20180605', LIMIT = 100, RADIUS = 500):
    return f'https://api.foursquare.com/v2/venues/explore?client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}&ll={latitude},{longitude}&v={VERSION}&limit={LIMIT}&radius={RADIUS}'
# latitude and longitude defaults are set in case a set of inputs cause errors and workable inputs are needed
#Defaults are set for my foursquare account

#%%
def GetManyNearbyVenues(names, lats, longs, radius = 500, limit = 100, nType = 'Neighborhood'):
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
    nearby_venues.columns = [f'{nType}',
            f'{nType} Latitude',f'{nType} Longitude',
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
def return_most_common_venues(row, num_top_venues):
    row_categories = row.iloc[1:]
    row_categories_sorted = row_categories.sort_values(ascending=False)
    
    return row_categories_sorted.index.values[0:num_top_venues]

#%%
# generalized version of return_most-common_values
def TopX(row, num_top_venues, skiprows = 0):
    row_categories = row.iloc[skiprows:]
    row_categories_sorted = row_categories.sort_values(ascending=False)
    return row_categories_sorted.index.values[0:num_top_venues]

#%%
def TopVenues(df, num_top_venues = 5, keep = 1):
# df: has "keep" rows of front data, followed by many rows of numeric data to be ranked
    indicators = ['st', 'nd', 'rd']
    # create columns according to number of top venues
    columns = list(df.columns[0:keep])
#,'Cluster']
    for ind in np.arange(num_top_venues):
        try:
            columns.append('{}{} Most Common Venue'.format(ind+1, indicators[ind]))
        except:
            columns.append('{}th Most Common Venue'.format(ind+1))
    # create a new dataframe
    df_sorted = pd.DataFrame(columns=columns)
    for k in list(df.columns[0:keep]):
        df_sorted[k] = df[k]
    for ind in np.arange(df.shape[0]):
        df_sorted.iloc[ind, keep:] = TopX(df.iloc[ind, :], num_top_venues, skiprows = keep)
    return df_sorted
#%%
def MoveToFront(ll,c):
    if type(c) == list:
        c.reverse()
        for item in c:
            ll = MoveToFront(ll, item)
        return ll
    for i, l in enumerate(ll):
        if l == c:
            # i is at position c in the list
            break
    if i == len(ll):
        return ([ll[i]] + (ll[0:i]))
    return ([ll[i]] + list(ll[0:i]) + list(ll[i+1:]))


#%%
neighSeattle = PrepareSoup('https://en.wikipedia.org/wiki/List_of_neighborhoods_in_Seattle')
neighSeattle = neighSeattle.find('tbody')
neighSeattle = WikiToTable(neighSeattle)
neighSeattle = neighSeattle.loc[:,0:1]
neighSeattle.columns = ['Neighborhood','Parent District']
neighSeattle.drop(index = 0, axis = 0, inplace = True)
neighSeattle = neighSeattle[neighSeattle['Parent District']!='Seattle\n'].reset_index()
neighSeattle.drop(columns = 'index', inplace = True)
neighSeattle


#%%
for i, (n,p) in enumerate(zip(neighSeattle['Neighborhood'], neighSeattle['Parent District'])):
# Some neighborhoods have multiple names or spill into multiple districts
# GPS differences between these are miniscule
# So for simplicity, we are reducing each to one

    cutOff = n.find('/')
    if cutOff != -1:
        n = n[0:cutOff]
    cutOff = n.find('&')
    if cutOff != -1:
        n = n[0:cutOff]
    cutOff = p.find('/')
    if cutOff != -1:
        p = p[0:cutOff]
    n = RemoveSymbol(n,'\n')
    n = RemoveBrackets(n)
    p = RemoveSymbol(p,'\n')
    p = RemoveBrackets(p)

    neighSeattle.loc[i,'Neighborhood'] = n
    neighSeattle.loc[i,'Parent District'] = p
neighSeattle


#%%
#addresses = MultiConcatenate(neighSeattle['Neighborhood'],neighSeattle['Parent District'])
#addresses = MultiConcatenate(addresses, 'Seattle, WA, USA')
addresses = MultiConcatenate(neighSeattle['Neighborhood'], 'Seattle, WA, USA')
#addresses
#%%
lats, longs = LatLong(addresses)
neighSeattle['Latitude'] = lats
neighSeattle['Longitude'] = longs
neighSeattle

#%%
# There should be approximately 8 neighborhoods that did not work
# these errors will be dropped
neighSeattle = neighSeattle[neighSeattle['Latitude']!=-49.51].reset_index()
neighSeattle.drop(columns = 'index', inplace = True)
#neighSeattle.drop(columns = 'level_0', inplace = True)
neighSeattle

#neighSeattle.drop(labels = -49.51, axis = 0)

#%%
venuesSeattle = GetManyNearbyVenues(neighSeattle.Neighborhood,neighSeattle.Latitude,neighSeattle.Longitude, nType = 'Neighborhood')

del neighSeattle

venuesSeattle = venuesSeattle[venuesSeattle['Venue Category']!='Neighborhood']
# there are two neighborhood venues, they cause errors, neighborhoods should not be members of themselves
venuesSeattle.reset_index(inplace=True)
venuesSeattle.drop(columns = 'index', inplace = True)
venuesSeattle.shape

#%%
groupVenuesSeattle = pd.get_dummies(venuesSeattle[['Venue Category']], prefix="",prefix_sep="")
groupVenuesSeattle['Neighborhood']=venuesSeattle['Neighborhood']
groupVenuesSeattle['Latitude'] = venuesSeattle['Neighborhood Latitude']
groupVenuesSeattle['Longitude'] = venuesSeattle['Neighborhood Longitude']
fixedColumns = MoveToFront(groupVenuesSeattle.columns, ['Neighborhood','Latitude','Longitude'])
groupVenuesSeattle = groupVenuesSeattle[fixedColumns]
groupVenuesSeattle = groupVenuesSeattle.groupby('Neighborhood').mean().reset_index()
groupVenuesSeattle.shape

#%%
del venuesSeattle
neighVenuesSeattle = TopVenues(groupVenuesSeattle, keep = 3)

#%%
kclusters = 4  #Reduced number of clusters--two clusters had only one member before

# the iloc[:,1:] removes the neighborhood column, which we do not want for kmeans
kmeans = KMeans (n_clusters = kclusters, random_state=0).fit(groupVenuesSeattle.iloc[:,1:])


neighVenuesSeattle['Cluster'] = kmeans.labels_
fixColumns = MoveToFront(neighVenuesSeattle.columns, ['Neighborhood','Cluster'])
neighVenuesSeattle = neighVenuesSeattle[fixColumns]
del groupVenuesSeattle
del fixColumns

#%%
print('Cluster 0')
print(neighVenuesSeattle.loc[neighVenuesSeattle['Cluster'] == 0,:])

print('Cluster 1')
print(neighVenuesSeattle.loc[neighVenuesSeattle['Cluster'] == 1,:])

print('Cluster 2')
print(neighVenuesSeattle.loc[neighVenuesSeattle['Cluster'] == 2,:])

print('Cluster 3')
print(neighVenuesSeattle.loc[neighVenuesSeattle['Cluster'] == 3,:])

#%%
latitude = mean(neighVenuesSeattle.Latitude)
longitude = mean(neighVenuesSeattle.Longitude)
# better the center of my neighborhoods than the center of Seattle
#%%
tClusterMap = folium.Map(location=[latitude, longitude], zoom_start=12) # generate map centred around Ecco

cluster = 0
these = neighVenuesSeattle.Cluster == cluster
for neigh, lat, lng, common in zip(neighVenuesSeattle.Neighborhood[these],neighVenuesSeattle.Latitude[these],neighVenuesSeattle.Longitude[these],neighVenuesSeattle['1st Most Common Venue']):
    folium.CircleMarker(
        [lat, lng],
        radius=5,
        popup=f'({neigh}, Venue: {common})',
        fill=True,
        color='blue',
        fill_color='blue',
        fill_opacity=0.6
        ).add_to(tClusterMap)

cluster = 1
these = neighVenuesSeattle.Cluster == cluster
for neigh, lat, lng, common in zip(neighVenuesSeattle.Neighborhood[these],neighVenuesSeattle.Latitude[these],neighVenuesSeattle.Longitude[these],neighVenuesSeattle['1st Most Common Venue']):
    folium.CircleMarker(
        [lat, lng],
        radius=5,
        popup=f'({neigh}, Venue: {common})',
        fill=True,
        color='red',
        fill_color='red',
        fill_opacity=0.6
        ).add_to(tClusterMap)

cluster = 2
these = neighVenuesSeattle.Cluster == cluster
for neigh, lat, lng, common in zip(neighVenuesSeattle.Neighborhood[these],neighVenuesSeattle.Latitude[these],neighVenuesSeattle.Longitude[these],neighVenuesSeattle['1st Most Common Venue']):
    folium.CircleMarker(
        [lat, lng],
        radius=5,
        popup=f'({neigh}, Venue: {common})',
        fill=True,
        color='green',
        fill_color='green',
        fill_opacity=0.6
        ).add_to(tClusterMap)

cluster = 3
these = neighVenuesSeattle.Cluster == cluster
for neigh, lat, lng, common in zip(neighVenuesSeattle.Neighborhood[these],neighVenuesSeattle.Latitude[these],neighVenuesSeattle.Longitude[these],neighVenuesSeattle['1st Most Common Venue']):
    folium.CircleMarker(
        [lat, lng],
        radius=5,
        popup=f'({neigh}, Venue: {common})',
        fill=True,
        color='purple',
        fill_color='purple',
        fill_opacity=0.6
        ).add_to(tClusterMap)

tClusterMap

#%%
