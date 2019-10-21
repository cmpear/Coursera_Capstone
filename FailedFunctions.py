#%%
# FUNCTIONS RELATED TO LATITUDE AND LONGITUDE--NO ADDRESSS RETRIEVAL
def Inside(pt, poly):
    # This function will work for all convex polygons.  It is less reliable for concave polygons
    # The function takes a point and a polygon (composed of points).  It then treats that point as
    # being at the the origin, and divides all polygon points into quadrants, and finds the nearest
    # point in each quadrant.  If two or more are missing, the point is assumed to be outside.
    # If only one is missing, the function tests to see if a line drawn between two other functions crosses
    # through the empty quadrant.  If it does, the point is inside, otherwise outside.
    x = pt[0]
    y = pt[1]
    Xs = []
    Ys = []
    for p in poly[0][0]:
        newX = p[0]-x
        newY = p[1]-y
        if (newX==0) and (newY==0):
            return True
        Xs.append(newX)  # we are going to zero the Xs
        Ys.append(newY)  # and the Ys
    df = {}
    df['x'] = Xs
    df['y'] = Ys
    df = pd.DataFrame(df)
    # Quadrant 1
    these = (df.x > x) & (df.y > y)
    if sum(these)<1:
        q1 = 'None'
    elif sum(these)==1:
        q1 = [df.x[these], df.y[these]]
    else:
        q1 = Closest(x,y,df.x[these],df.y[these])
    # Quadrant 2
    these = (df.x < x) & (df.y > y)
    if sum(these)<1:
        q2 = 'None'
    elif sum(these)==1:
        q2 = [df.x[these], df.y[these]]
    else:
        q2 = Closest(x,y,df.x[these],df.y[these])
    # Quadrant 3
    these = (df.x < x) & (df.y < y)
    if sum(these)<1:
        q3 = 'None'
    elif sum(these)==1:
        q3 = [df.x[these], df.y[these]]
    else:
        q3 = Closest(x,y,df.x[these],df.y[these])
    # Quadrant 4
    these = (df.x > x) & (df.y < y)
    if sum(these)<1:
        q4 = 'None'
    elif sum(these)==1:
        q4 = [df.x[these], df.y[these]]
    else:
        q4 = Closest(x,y,df.x[these],df.y[these])
    # Missing None
    if type(q1) !=str and type(q2) !=str and type(q3) !=str and type(q4) !=str:
        return True
    # Easy Stop
    print(f'q1: {q1}, q2: {q2}, p3: {q3}, p4: {q4}')
    if (type(q1) == str) or (type(q3) == str):        
        if type(q2) == str or type(q4) == str:
            return False
    # Missing One--The difficult case
    if type(q1) == str:
        print('Quadrant 1 Empty')  
        return CrossQuadrant(1,q2[0], q2[1], q4[0], q4[1])
    if type(q2) == str:  
        print('Quadrant 2 Empty')  
        return CrossQuadrant(2,q1[0], q1[1], q3[0], q3[1])
    if type(q3) == str:  
        print('Quadrant 3 Empty')  
        return CrossQuadrant(3,q2[0], q2[1], q4[0], q4[1])
    if type(q4) == str:  
        print('Quadrant 4 Empty')  
        return CrossQuadrant(4,q1[0], q1[1], q3[0], q3[1])

def CrossQuadrant(quadrant, x1, y1, x2, y2, zeroX= 0, zeroY=0):
    x1 = float(x1 - zeroX)
    x2 = float(x2 - zeroY)
    y1 = float(y1 - zeroX)
    y2 = float(y2 - zeroY)
    iHat = x2 - x1
    jHat = y2 - y1
    # test for on the line
    print(f'x2: {x2}, iHat: {iHat}, y2: {y2}, jHat: {jHat}, x2/iHat: {x2/iHat}, y2/jHat: {y2/jHat}')
    if x2/iHat == y2/jHat:
        return True
    crossYFirst = x2/iHat < y2/jHat
    crossXFirst = x2/iHat > y2/jHat
    # if i is less than j, crosses y axis first--x reaches 0 first
    # otherwise, crosses the x axis first--y reaches 0 first
    q = WhatQuadrant(x1,y1)
    if quadrant == 1:
        if q == 2:
            return crossYFirst
        if q == 4:     # from quadrant 4, must first cross y axis
            return crossXFirst
    if quadrant == 2:
        if q == 1:
            return crossYFirst
        if q == 3:
            return crossXFirst
    if quadrant == 3:
        if q == 2:
            return crossXFirst
        if q == 4:
            return crossYFirst
    if quadrant == 4:
        if q == 1:
            return crossXFirst
        if q == 3:
            return crossYFirst
    print('ERROR: points in wrong quadrants')
    return 'ERROR: points in wrong quadrants'

def WhatQuadrant(x,y):
    if x>0:
        if y>0:
            return 1
        else:
            return 4
    else:
        if y>0:
            return 2
        else:
            return 3
    print('Point is on an axis, returning 0')
    return 0 # point

def Closest(lat1, lng1, lats, longs):
    if len(lats)==1:
        return lats[0], longs[0]
    dis = 6361000 * 3.1415  # no way any earthly distance will be more than Earth's circumfrance 
    for lat2, lng2 in zip(lats, longs):
        d = ((lat1 - lat2) ** 2 + (lng2 - lng1) ** 2) ** 0.5
        if d<dis:
            dis = d
            rLat = lat2
            rLong = lng2
    return float(rLat), float(rLong)




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