#%% [markdown]
## Where to Build a Gym
# Seattle has been enjoying steady growth, and thanks to the combination of strong manufacturing companies like Boeing and newer technology
# companies such as Microsoft and Amazon, this growth is likely to continue for the near future.  This creates opportunities not simply for
# those in the technology sector, but also more traditional businesses seeking to serve this new clientel.  Among these are gyms, which are
# not only resistant to outsourcing (for obvious reasons), but also especially popular among the young population that Seattle is attracting.
# This leaves a question of where to build new venue.

#%%
import requests
import csv
import pandas as pd
import numpy as np
from statistics import mean
from statistics import stdev
from geopy.geocoders import Nominatim # module to convert an address into latitude and longitude values
import math
import folium
from os import listdir  # used to gather names of files in folder
from shapely.geometry import Point, Polygon
import json
#from shapely.geometry import shape, mapping, Point, Polygon, MultiPolygon
import geojson
#from geojson import feature_collection
from pandas.io.json import json_normalize
from colour import Color

#%%
###########################################################################################################################
###########################################################################################################################
###########################################################################################################################
###########################################################################################################################


###########################################################################################################################
###########################################################################################################################
###########################################################################################################################
###########################################################################################################################


###########################################################################################################################
###########################################################################################################################
###########################################################################################################################
###########################################################################################################################

#%%
def FindClosest(lats, longs):
    closest = []
    for i1, (lat1, lng1) in enumerate(zip(lats, longs)):
        distances = []
        for i2, (lat2, lng2) in enumerate(zip(lats, longs)):
            if (i1==i2):
                continue
            d = Haversine(lat1,lng1,lat2,lng2)
            distances.append(d)
        closest.append(min(distances))
    return closest
#    point = shape(pt['geometry'])
#    return point.within(shape(multi['geometry'])):

def Haversine(lat1,lng1,lat2,lng2, unit = 'meters'):
    # Based on Nathan A. Rooy's function
    R = 6361000     # earth radius in meters

    phi_1=math.radians(lat1)
    phi_2=math.radians(lat2)
    delta_phi=math.radians(lat2-lat1)
    delta_lambda=math.radians(lng2-lng1)

    a=math.sin(delta_phi/2.0)**2+\
        math.cos(phi_1)*math.cos(phi_2)*\
        math.sin(delta_lambda/2.0)**2
    c=2*math.atan2(math.sqrt(a),math.sqrt(1-a))
    r = R * c
    if unit == 'meters':
        return r
    r = r / 1000
    if unit == 'km' or unit == 'kilometers':
        return r
    r = r * 0.621371
    if unit == 'miles':
        return r
    r = r / 5280 
    if unit == 'feet':
        return r

def Haversine(latlong1,latlong2, unit = 'meters'):
    # Based on Nathan A. Rooy's function
    R = 6361000     # earth radius in meters
    lat1,lng1 = latlong1[0], latlong1[1]
    lat2,lng2 = latlong2[0], latlong2[1]
    phi_1=math.radians(lat1)
    phi_2=math.radians(lat2)
    delta_phi=math.radians(lat2-lat1)
    delta_lambda=math.radians(lng2-lng1)

    a=math.sin(delta_phi/2.0)**2+\
        math.cos(phi_1)*math.cos(phi_2)*\
        math.sin(delta_lambda/2.0)**2
    c=2*math.atan2(math.sqrt(a),math.sqrt(1-a))
    r = R * c
    if unit == 'meters':
        return r
    r = r / 1000
    if unit == 'km' or unit == 'kilometers':
        return r
    r = r * 0.621371
    if unit == 'miles':
        return r
    r = r / 5280 
    if unit == 'feet':
        return r

def PrimitiveCenter(coordinates, flip = False):
# This function simply averages the X and Y coordinates of a json or geojson polygon.
# It is simple, but will favor the side with the most complicated geometry
    Xs, Ys = [],[]
    for pt in coordinates:
        Xs.append(pt[0])
        Ys.append(pt[1])
    if flip:
        return [mean(Ys),mean(Xs)]    
    return [mean(Xs),mean(Ys)]
#%%
###########################################################################################################################
###########################################################################################################################
###########################################################################################################################
###########################################################################################################################
###########################################################################################################################
###########################################################################################################################

#%%  FUNCTIONS RETRIEVING LATITUDE AND LONGITUDE VIA ADDRESSES

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
    if slash != -1:
        address = address[0:slash]
    del slash
    dash = address.find('-')
    if dash != -1:
        lats = []
        longs = []
        comma = address.find(',')
        remainder = address[comma:]
        for a in address[0:comma].split('-'):
            lat, lng = LatLong(f'{a}{remainder}')
            if lat == -49.51 and lng == -128.34:
                continue
            else:
                lats.append(lat)
                longs.append(lng)
        return mean(lats), mean(longs)
    geolocator = Nominatim(user_agent="foursquare_agent")
    try:
        loc = geolocator.geocode(address)
        return loc.latitude, loc.longitude
    except:
        print(f'ERROR AT: {address}')
        return -49.51, -128.34

def GetManyNearbyVenues(names, lats, longs, limit = 100,  radius = 500, radi = 0,nType = 'Neighborhood'):
# This function is designed to work with a single or varying radi
    if type(radi) == int:
        return GetManyNearbyVenuesSingleRadius(names,lats,longs,limit,radius,nType)
    else:
#        print("Multiple Radi")
        return GetManyNearbyVenuesMultiRadi(names = names, lats = lats, longs = longs, limit = limit, radi = radi, nType = nType)

def GetManyNearbyVenuesMultiRadi(names, lats, longs, limit, radi, nType):
    if type(names) == str:
        names = names.split(',')
    l_venues = []
    # long is taken
#    print('Starting Loop')
    for name, lat, lng, radius in zip(names, lats, longs, radi):
        results = GetNearbyVenues(name, lat, lng, radius, limit)
#        print(results)
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

def GetManyNearbyVenuesSingleRadius(names, lats, longs, limit, radius,nType):
    #ensure names is a list
    if type(names) == str:
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

def FSExploreLoc(latitude=43.75880, longitude=-79.320197, CLIENT_ID = 'RJ2TAOE50JVYUTGUY0W0HNVMEWPHWN4LJJ2CSVJL1NYUY43P', CLIENT_SECRET = 'WV3VMFHZINCZWXWH1VKWWVWNFD3I1XWY2IFFXI5KJPGHUM3G', VERSION = '20180605', LIMIT = 100, RADIUS = 500):
    return f'https://api.foursquare.com/v2/venues/explore?client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}&ll={latitude},{longitude}&v={VERSION}&limit={LIMIT}&radius={RADIUS}'


def FSVenueSearch(venueCategory,latitude=43.75880, longitude=-79.320197, CLIENT_ID = 'RJ2TAOE50JVYUTGUY0W0HNVMEWPHWN4LJJ2CSVJL1NYUY43P', CLIENT_SECRET = 'WV3VMFHZINCZWXWH1VKWWVWNFD3I1XWY2IFFXI5KJPGHUM3G', VERSION = '20180605', LIMIT = 100, RADIUS = 500):
    return f'https://api.foursquare.com/v2/venues/search?client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}&ll={latitude},{longitude}&v={VERSION}&query={venueCategory}&radius={RADIUS}&limit={LIMIT}'

def FSVenueSearch(venueCategory, latlong, CLIENT_ID = 'RJ2TAOE50JVYUTGUY0W0HNVMEWPHWN4LJJ2CSVJL1NYUY43P', CLIENT_SECRET = 'WV3VMFHZINCZWXWH1VKWWVWNFD3I1XWY2IFFXI5KJPGHUM3G', VERSION = '20180605', LIMIT = 100, RADIUS = 500):
    return f'https://api.foursquare.com/v2/venues/search?client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}&ll={latlong[0]},{latlong[1]}&v={VERSION}&query={venueCategory}&radius={RADIUS}&limit={LIMIT}'

#%%
###########################################################################################################################
###########################################################################################################################
###########################################################################################################################
###########################################################################################################################
###########################################################################################################################
###########################################################################################################################

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
    
def BoolToIndex(ll):
    these = []
    for i, l in enumerate(ll):
        if l:
            these.append(i)
    return these

def fileToName(name):
    dot = name.find('.')
    name = name[0:dot]
    if name.find('_')!=-1:
        name = [f'{n.capitalize()}' for n in name.split('_')]
        name2 = ''
        for n in name:
            name2 = f'{name2} {n}'
            name = name2[1:]
    else:
        name = name.capitalize()
    return name

#%%
###########################################################################################################################
###########################################################################################################################
###########################################################################################################################
###########################################################################################################################


###########################################################################################################################
###########################################################################################################################
###########################################################################################################################
###########################################################################################################################


###########################################################################################################################
###########################################################################################################################
###########################################################################################################################
###########################################################################################################################
#%% [markdown]
### Data Gathering
#   To examine the question of where to build, we will examine three sources of data.  The first of these is a map of Seattle's districts in
# the geojson that was assembled by Zillow.  The second is data projecting the growth of key urban centers and villages assembled by the
# Seattle government.  The third is data on where gyms are located, using Foursquare.
#   To combine these datasets, we will be using Zillow's list of neighborhoods as the boundaries they provide are the most reliable.  We will
# then be using the pt.within() method to place the Seattle Government's data on villages and urban centers into Zillow's neighborhoods.  We
# will similarly get gym counts for each Zillow neighborhood.

#%% [markdown]
#### Data Gathering: Seattle Government Data
#   Seattle's government data was in pdf format.  Unfortunately, the tabula module was unable to extract useable data from most of the pages,
# so we instead relied on more traditional forms of data-entry, and read then read the data from a csv file.  Then using Nominatim, we acquire
# GPS coordinates for each district, and individually correct any erroneous coordinates.  Finally, zillow's geojson files are checked to see
# where each urban center or village is located within the zillow neighborhoods.  The final product is the panda's dataframe geoSeattleGrowth

#%%
# Gather the data
###########################################################################################################################
###########################################################################################################################

seattleGrowth = pd.read_csv('seattleGrowth.csv', delimiter=',')  # this will be deleted later to save space

#seattleGrowth = pd.DataFrame(seattleGrowth)

addresses = MultiConcatenate(seattleGrowth['Community'], 'Seattle, WA, USA')
lats, longs = LatLong(addresses)
seattleGrowth['Latitude']=lats
seattleGrowth['Longitude']=longs


# FIX PROBLEMATIC NEIGHBORHOODS
these = BoolToIndex(seattleGrowth['Community'] == 'West Seattle Junction')
seattleGrowth.loc[these,['Latitude','Longitude']] = [47.562216,-122.386808]
these = BoolToIndex(seattleGrowth['Community'] == 'Ballard')
seattleGrowth.loc[these,['Latitude','Longitude']] = [47.679512, -122.387534]
these = BoolToIndex(seattleGrowth['Community'] == 'Roosevelt')
seattleGrowth.loc[these,['Latitude','Longitude']] = [47.678048, -122.315720]
these = BoolToIndex(seattleGrowth['Community'] == 'Greater Duwamish')
seattleGrowth.loc[these,['Latitude','Longitude']] = [47.554512, -122.313516]
these = BoolToIndex(seattleGrowth['Community'] == 'Pike/Pine')  # east of highway, not pike marketplace
seattleGrowth.loc[these,['Latitude','Longitude']] = [47.614652, -122.319427]
these = BoolToIndex(seattleGrowth['Community'] == 'Commercial Core')# basically downtown
seattleGrowth.loc[these,['Latitude','Longitude']] = [47.605132, -122.335159]
these = BoolToIndex(seattleGrowth['Community'] == 'Ballard-Interbay-Northend') # original point was just outside district.
seattleGrowth.loc[these,['Latitude','Longitude']] = [47.640944, -122.381903]
these = BoolToIndex(seattleGrowth['Community'] == 'Denny Triangle') # point was on line w/ downtown, moved to NW corner of Denny Park.
seattleGrowth.loc[these,['Latitude','Longitude']] = [47.619689, -122.342360]
these = BoolToIndex(seattleGrowth['Community'] == 'Upper Queen Anne') # was not even in Seattle...
seattleGrowth.loc[these,['Latitude','Longitude']] = [47.632160, -122.356903]
these = BoolToIndex(seattleGrowth['Community'] == 'Capital hill') # was not even in Seattle...
seattleGrowth.loc[these,['Latitude','Longitude']] = [47.623164, -122.322014]

#%%
# Place the Data into a cleaned-up dataset
###########################################################################################################################
###########################################################################################################################

geoSeattleGrowth = pd.DataFrame()
geoSeattleGrowth['Neighborhood']        = list(fileToName(f) for f in listdir('geojson'))
geoSeattleGrowth['growth_2015-2030']    = [0] * geoSeattleGrowth.shape[0]
geoSeattleGrowth['beingBuilt']          = [0] * geoSeattleGrowth.shape[0]
geoSeattleGrowth['total2015']           = [0] * geoSeattleGrowth.shape[0]
geoSeattleGrowth['recentBuilt']         = [0] * geoSeattleGrowth.shape[0]
geoSeattleGrowth['total2019']           = [0] * geoSeattleGrowth.shape[0]
geoSeattleGrowth['fileName'] = listdir('geojson')


these= [True] * seattleGrowth.shape[0]

# just want a list of true bools of equal length to seattleGrowth

for k, f in enumerate(geoSeattleGrowth.fileName):
    with open (f'geojson\\{f}') as geo:
        neighborhood = json.load(geo)
        neighborhood = Polygon(neighborhood['coordinates'][0][0])
    for i, (x,y) in enumerate(zip(seattleGrowth.Longitude, seattleGrowth.Latitude)):
#   In X,Y coordinates, it is LONGITUDE and latitude...Eastwest before NorthSouth
        if these[i]:
            pt = Point(x,y)
            if pt.within(Polygon(neighborhood)):
                geoSeattleGrowth.loc[k,'growth_2015-2030']  += seattleGrowth.loc[i,'Estimated_Growth_2015-2035']
                geoSeattleGrowth.loc[k,'beingBuilt']        += seattleGrowth.loc[i,'Being_Built']
                geoSeattleGrowth.loc[k,'total2015']         += seattleGrowth.loc[i,'Total_Units_2015']                
                geoSeattleGrowth.loc[k,'recentBuilt']       += seattleGrowth.loc[i,'Units_Built_2016-2019']
                geoSeattleGrowth.loc[k,'total2019']         += seattleGrowth.loc[i,'Total_Units_2019']
#                geoNeighborhood[i] = fileToName(f)
                these[i]=False
#seattleGrowth['GeoNeighborhood']= geoNeighborhood
#seattleGrowth[['Community','GeoNeighborhood', 'Latitude','Longitude']]

del seattleGrowth
geoSeattleGrowth.head()

#%%
# SHRINK DATASET TO NEIGHBORHOODS OF INTEREST
#these = geoSeattleGrowth['total2019']>0
#geoSeattleGrowth = geoSeattleGrowth[these]
#del these
#geoSeattleGrowth

#%%
###########################################################################################################################
###########################################################################################################################
###########################################################################################################################
###########################################################################################################################
###########################################################################################################################
###########################################################################################################################

#%% [markdown]
### Data Gathering: Venue Data
#   Ideally, we would gather a list of Seattle Gyms from a single query, or by querring each neighborhood individually.  Unfortunatley,
# querries are made within a radius of a GSP coordinate, and neither Seattle nor its neighborhoods are circles.  Further, a single query
# to FourSquare can only return upto 50 venues.  Thus, we divided Seattle into 12 overlapping circular regions to query, and then removed
# any duplicate venues that arose from the overlap of these.  At the end, the gym counts for each neighborhood are added to the 
# geoSeattleGrowth dataset.


#%%
# Get the circles for acquiring venues
###########################################################################################################################
###########################################################################################################################
northernCenter      = [47.668000, -122.328000]
southernCenter      = [47.540000, -122.321886]
westernCenter       = [47.637000, -122.376500] #at North Queen Anne
westernCenter2      = [47.656000, -122.406000]
easternCenter       = [47.650000, -122.275500]
northernCenter2     = [47.706000, -122.342000]
seattleCoreLatLong  = [47.619000, -122.353000]
seattleCoreLatLong2 = [47.611500, -122.346000]
seattleCoreLatLong3 = [47.611000, -122.333518]
valleyGap           = [47.626251, -122.345750]
dennyGap            = [47.618070, -122.338533]
freemontGap         = [47.650936, -122.352430]

rNorth2 = Haversine(northernCenter2, northernCenter) * 1.40
rWest = Haversine(westernCenter, seattleCoreLatLong) * 0.87
rWest2 = Haversine(westernCenter2, westernCenter)/2**0.5 * 1.2
rEast = Haversine(easternCenter, seattleCoreLatLong) * 0.85
rSouth = Haversine(southernCenter, seattleCoreLatLong) * .90
rCore = 700
rCore2 = 600
rCore3 = 500
rValley = 600
rDenny = 650
rFreemont = 500

# originally used two centers, but northern center had two many gyms, now using four centers
#%%
# Query each circle
###########################################################################################################################
###########################################################################################################################

targetCategory = 'Gym'

url = FSVenueSearch(targetCategory,latlong =  northernCenter2, RADIUS = rNorth2)
seattleVenues = requests.get(url).json()['response']['venues']
seattleVenues = json_normalize(seattleVenues)
seattleVenues = seattleVenues[['id','name','location.lat','location.lng']]
print(f'North {seattleVenues.shape}')

url = FSVenueSearch(targetCategory,latlong =  valleyGap, RADIUS = rValley)
valleyVenues = requests.get(url).json()['response']['venues']
valleyVenues = json_normalize(valleyVenues)
valleyVenues = valleyVenues[['id','name','location.lat','location.lng']]
print(f'Valley {valleyVenues.shape}')

seattleVenues = valleyVenues.append(valleyVenues)
print(f'Venues: {seattleVenues.shape}')
del valleyVenues

url = FSVenueSearch(targetCategory,latlong =  dennyGap, RADIUS = rDenny)
dennyVenues = requests.get(url).json()['response']['venues']
dennyVenues = json_normalize(dennyVenues)
dennyVenues = dennyVenues[['id','name','location.lat','location.lng']]
print(f'Denny {dennyVenues.shape}')

seattleVenues = seattleVenues.append(dennyVenues)
print(f'Venues: {seattleVenues.shape}')
del dennyVenues

url = FSVenueSearch(targetCategory,latlong =  freemontGap, RADIUS = rFreemont)
freemontVenues = requests.get(url).json()['response']['venues']
freemontVenues = json_normalize(freemontVenues)
freemontVenues = freemontVenues[['id','name','location.lat','location.lng']]
print(f'Denny {freemontVenues.shape}')

seattleVenues = seattleVenues.append(freemontVenues)
print(f'Venues: {seattleVenues.shape}')
del freemontVenues

url = FSVenueSearch(targetCategory,latlong =  seattleCoreLatLong, RADIUS = rCore)
coreSeattleVenues = requests.get(url).json()['response']['venues']
coreSeattleVenues = json_normalize(coreSeattleVenues)
coreSeattleVenues = coreSeattleVenues[['id','name','location.lat','location.lng']]
print(f'Core {coreSeattleVenues.shape}')

seattleVenues = seattleVenues.append(coreSeattleVenues)
print(f'Venues: {seattleVenues.shape}')
del coreSeattleVenues

url = FSVenueSearch(targetCategory,latlong =  seattleCoreLatLong2, RADIUS = rCore2)
coreSeattleVenues2 = requests.get(url).json()['response']['venues']
coreSeattleVenues2 = json_normalize(coreSeattleVenues2)
coreSeattleVenues2 = coreSeattleVenues2[['id','name','location.lat','location.lng']]
print(f'South Core {coreSeattleVenues2.shape}')

seattleVenues = seattleVenues.append(coreSeattleVenues2)
print(f'Venues: {seattleVenues.shape}')
del coreSeattleVenues2

url = FSVenueSearch(targetCategory,latlong =  seattleCoreLatLong3, RADIUS = rCore3)
coreSeattleVenues3 = requests.get(url).json()['response']['venues']
coreSeattleVenues3 = json_normalize(coreSeattleVenues3)
coreSeattleVenues3 = coreSeattleVenues3[['id','name','location.lat','location.lng']]
print(f'Southeast Core {coreSeattleVenues3.shape}')

seattleVenues = seattleVenues.append(coreSeattleVenues3)
print(f'Venues: {seattleVenues.shape}')
del coreSeattleVenues3

url = FSVenueSearch(targetCategory,latlong =  westernCenter, RADIUS = rWest)
westernSeattleVenues = requests.get(url).json()['response']['venues']
westernSeattleVenues = json_normalize(westernSeattleVenues)
westernSeattleVenues = westernSeattleVenues[['id','name','location.lat','location.lng']]
print(f'West {westernSeattleVenues.shape}')

seattleVenues = seattleVenues.append(westernSeattleVenues)
print(f'Venues: {seattleVenues.shape}')
del westernSeattleVenues

url = FSVenueSearch(targetCategory,latlong =  westernCenter2, RADIUS = rWest2)
westernSeattleVenues2 = requests.get(url).json()['response']['venues']
westernSeattleVenues2 = json_normalize(westernSeattleVenues2)
westernSeattleVenues2 = westernSeattleVenues2[['id','name','location.lat','location.lng']]
print(f'Far West {westernSeattleVenues2.shape}')

seattleVenues = seattleVenues.append(westernSeattleVenues2)
print(f'Venues: {seattleVenues.shape}')
del westernSeattleVenues2

url = FSVenueSearch(targetCategory,latlong =  easternCenter, RADIUS = rEast)
easternSeattleVenues = requests.get(url).json()['response']['venues']
easternSeattleVenues = json_normalize(easternSeattleVenues)
easternSeattleVenues = easternSeattleVenues[['id','name','location.lat','location.lng']]
print(f'East {easternSeattleVenues.shape}')

seattleVenues = seattleVenues.append(easternSeattleVenues)
print(f'Venues: {seattleVenues.shape}')
del easternSeattleVenues

url = FSVenueSearch(targetCategory,latlong =  southernCenter, RADIUS = rSouth)
southSeattleVenues = requests.get(url).json()['response']['venues']
southSeattleVenues = json_normalize(southSeattleVenues)
southSeattleVenues = southSeattleVenues[['id','name','location.lat','location.lng']]
print(f'South {southSeattleVenues.shape}')

seattleVenues = seattleVenues.append(southSeattleVenues)
print(f'Venues: {seattleVenues.shape}')
del southSeattleVenues

seattleVenues.drop_duplicates(inplace = True)
print(f'Final Venues: {seattleVenues.shape}')

#%%
# Put venue counts in zilllow geoSeattleGrowth
###########################################################################################################################
###########################################################################################################################
these = [True] * len(seattleVenues)
venueNeighborhood = ['    000'] * len(seattleVenues)
venueCount = [0] * geoSeattleGrowth.shape[0]

for k, f in enumerate(geoSeattleGrowth.fileName):
    with open (f'geojson\\{f}') as geo:
        neighborhood = json.load(geo)
        neighborhood = Polygon(neighborhood['coordinates'][0][0])
    for i, (lat,lng) in enumerate(zip(seattleVenues['location.lat'],seattleVenues['location.lng'])):

        if these[i]:
            pt = Point(lng,lat) # X IS LONGITUDE, y is latitude

            if pt.within(Polygon(neighborhood)):
                these[i] = False  #prevents repeats, cannot put earlier, else it will ruin the for-loop
                venueNeighborhood[i] = fileToName(f)

                venueCount[k] = venueCount[k] +1


geoSeattleGrowth['GymCounts'] = venueCount
geoSeattleGrowth.head()

#%%
zGeoSeattleGrowth = {}
# string data
for c in geoSeattleGrowth.columns[0:1]:
    zGeoSeattleGrowth[c] = geoSeattleGrowth[c]
# numeric data to zscores
for c in geoSeattleGrowth.columns[1:6]:
    zGeoSeattleGrowth[c] = (geoSeattleGrowth[c] - mean(geoSeattleGrowth[c]))/stdev(geoSeattleGrowth[c])
for c in geoSeattleGrowth.columns[6:]:
    zGeoSeattleGrowth[c] = geoSeattleGrowth[c]
zGeoSeattleGrowth = pd.DataFrame(zGeoSeattleGrowth)
zGeoSeattleGrowth.head()

#%%
###########################################################################################################################
###########################################################################################################################
###########################################################################################################################
###########################################################################################################################
###########################################################################################################################
###########################################################################################################################
#%%
#### Gather Data: Zillow Neighborhood Geojson
#   Up until now, we had simply been pulling in geojson files for individual neighborhoods as needed.  However, some of the
# mapping functions work much better with a single FeatureCollection of neighborhoods than separate files.  Here, we joined
# the Geojson files together, then wrote them to a new file.  To speed up the program, the program was then simply modified
# to read the combined geojson directly.

#%%
# Making the Geojson file.  Commented out as not currently in use
###########################################################################################################################
###########################################################################################################################

#features = []
#for name, file in zip(zGeoSeattleGrowth['Neighborhood'], zGeoSeattleGrowth['fileName']):
#
##for file in listdir('geojson'):   # keep these commented out unless you want all Seattle neighborhoods
##    name = fileToName(file)       # keep these commented out unless you want all Seattle neighborhoods
#
#    path = f'geojson\\{file}'
#    with open(path) as f:
#        coordinates = json.load(f)
#    coordinates = coordinates['coordinates'][0]
#    nFeature = {'type': "Feature", "properties": {"name": name}, "geometry": {"type": "Polygon", "coordinates": [] }, "id": name}
#    nFeature['geometry']['coordinates'] = coordinates
#    features.append(nFeature)
#
#geoSeattleNeighborhoods = {"type" : "FeatureCollection", "features": []}
#geoSeattleNeighborhoods['features']=features
#with open('seattleNeighborhoods.txt','w') as outfile:
#    json.dump(geoSeattleNeighborhoods,outfile)
#geoSeattleNeighborhoods = json.dumps(geoSeattleNeighborhoods)

#%%
# Read the combind geojson file into seattleNeighborhoods.geojson
###########################################################################################################################
###########################################################################################################################

with open('seattleNeighborhoods.geojson') as file:
    geoSeattleNeighborhoods = json.load(file)

#%%
###########################################################################################################################
###########################################################################################################################
###########################################################################################################################
###########################################################################################################################


###########################################################################################################################
###########################################################################################################################
###########################################################################################################################
###########################################################################################################################


###########################################################################################################################
###########################################################################################################################
###########################################################################################################################
###########################################################################################################################
#%% [markdown]
### Data Analysis
#
###########################################################################################################################
###########################################################################################################################

#%%
zGeoSeattleGrowth.

#%%
neighSeattleMap = folium.Map(seattleCoreLatLong, zoom_start=12) # generate map centred around Ecco

#style_function = (lambda feature : dict(fillColor = feature, color = 'purple', fillOpacity = 0.5))

neighSeattleMap.choropleth(
    geo_data = geoSeattleNeighborhoods,
    data = zGeoSeattleGrowth,
    columns = ['Neighborhood','growth_2015-2030'],
    key_on = 'feature.id',
    fill_color='YlOrRd'
)

#for col, f in zip(gymColorIndex, zGeoSeattleGrowth.fileName):
#    with open (f'geojson\\{f}') as f2:
#        this = json.load(f2)
#    this['features'] = {'color': str(colors[i])}
#    print(this)
#    this['features']['color'] = 'red'
#    color = str(colors[i])
#    style_function = lambda this: dict(fillColor = col, color = col, fillOpacity = 0.3)
#    folium.GeoJson(this,
#     style_function= style_function
#     ).add_to(neighSeattleMap)
for neigh in geoSeattleNeighborhoods['features']:
    coord = neigh['geometry']['coordinates'][0]
    name = neigh['id']
    pt = PrimitiveCenter(coord, flip = True)
    print(pt)
#    del coord
    folium.CircleMarker(
        pt,
        radius = 5,
        popup = name,
        fill = True,
        color = 'red',
        fill_color = 'orange',
        fill_opacity = 0.5
    ).add_to(neighSeattleMap)

for venue, lat, lng in zip(seattleVenues['name'], seattleVenues['location.lat'],seattleVenues['location.lng']):
        folium.CircleMarker(
        [lat,lng],
        radius = 4,
        popup= venue,
        fill = True,
        color = 'purple',
        fill_color = 'purple',
        fill_opacity=.6
    ).add_to(neighSeattleMap)

neighSeattleMap
# checking the coverage of our two zones to search Seattle for gyms


#%%
folium.Circle(
    northernCenter2,
    radius = rNorth2,
    color = 'green',
    fill_color = 'green',
    fill_opacity=0.2
).add_to(neighSeattleMap)
folium.Circle(
    valleyGap,
    radius = rValley,
    color = 'green',
    fill_color = 'green',
    fill_opacity=0.2
).add_to(neighSeattleMap)
folium.Circle(
    dennyGap,
    radius = rDenny,
    color = 'green',
    fill_color = 'green',
    fill_opacity=0.2
).add_to(neighSeattleMap)
folium.Circle(
    freemontGap,
    radius = rFreemont,
    color = 'green',
    fill_color = 'green',
    fill_opacity=0.2
).add_to(neighSeattleMap)
folium.Circle(
    seattleCoreLatLong,
    radius = rCore,
    color = 'green',
    fill_color = 'green',
    fill_opacity=0.2
).add_to(neighSeattleMap)
folium.Circle(
    seattleCoreLatLong2,
    radius = rCore2,
    color = 'green',
    fill_color = 'green',
    fill_opacity=0.2
).add_to(neighSeattleMap)
folium.Circle(
    seattleCoreLatLong3,
    radius = rCore3,
    color = 'green',
    fill_color = 'green',
    fill_opacity=0.2
).add_to(neighSeattleMap)
folium.Circle(
    easternCenter,
    radius = rEast,
    color = 'green',
    fill_color = 'green',
    fill_opacity=0.2
).add_to(neighSeattleMap)
folium.Circle(
    westernCenter,
    radius = rWest,
    color = 'green',
    fill_color = 'green',
    fill_opacity=0.2
).add_to(neighSeattleMap)
folium.Circle(
    westernCenter2,
    radius = rWest2,
    color = 'green',
    fill_color = 'green',
    fill_opacity=0.2
).add_to(neighSeattleMap)
folium.Circle(
    southernCenter,
    radius = rSouth,
    color = 'green',
    fill_color = 'green',
    fill_opacity=0.2
).add_to(neighSeattleMap)

neighSeattleMap
#%%
