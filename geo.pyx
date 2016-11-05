# -*- coding: utf-8 -*-
"""
Created on Wed Aug 17 12:08:35 2016

@author: nate
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Aug 15 11:53:55 2016

@author: nate
"""
import math



earth_radius = 3960.0
degrees_to_radians = math.pi/180.0
radians_to_degrees = 180.0/math.pi


# methods that deal purely with geography

def plot(self,latitude,longitude,color):  
    # this is shittier than google maps but it helps debugging a lot.
    # Contains the math that converts lat/long to a mercator projection so
    # we can plot on a mercator projection.
    # perhaps it should be an option to enable the map or not
    mapWidth = 5400;
    mapHeight = 2262;
    # get x value
    x = (longitude+180)*(mapWidth/360)
    # convert from degrees to radians
    latRad = latitude*math.pi/180
    # get y value
    mercN = math.log(math.tan((math.pi/4)+(latRad/2)),math.e)
    y = (mapHeight/2)-(mapWidth*mercN/(2*math.pi))
    self.plt.plot(x,y,color)
    #self.plt.pause(0.05)
    
def deg2rad(deg):
    return deg * (math.pi/180)

def change_in_latitude(kilos):
    return (kilos/earth_radius)*radians_to_degrees

def change_in_longitude(latitude, kilos):
    r = earth_radius*math.cos(latitude*degrees_to_radians)
    return (kilos/r)*radians_to_degrees

def pointAtAngle(angle,r,latitude,longitude):
    angle = deg2rad(angle)
    x = math.cos(angle)*r
    y = math.sin(angle)*r
    dlat = change_in_latitude(y)
    dlon = change_in_longitude(latitude,x)
    return [latitude+dlat,longitude+dlon,0]

def getDistance(lat1,lon1,lat2,lon2):
    R = 6371; # Radius of the earth in km
    dLat = deg2rad(float(lat2)-float(lat1))  #deg2rad below
    dLon = deg2rad(lon2-lon1)
    a = ( 
    math.sin(dLat/2) * math.sin(dLat/2) +
    math.cos(deg2rad(lat1)) * math.cos(deg2rad(lat2)) * 
    math.sin(dLon/2) * math.sin(dLon/2) 
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = R * c #Distance in km
    return d
    


def avg(data): 
    # finds the average of lat/long coords, taken from stack overflow :P
    X = 0
    Y = 0
    Z = 0
    for coord in data:
        lat = coord["latitude"] * math.pi / 180
        lon = coord["longitude"] * math.pi / 180
        a = math.cos(lat) * math.cos(lon)
        b = math.cos(lat) * math.sin(lon)
        c = math.sin(lat)
        
        X = a + X
        Y = b + Y
        Z = c + Z
    X /= len(data)
    Y /= len(data)
    Z /= len(data)
    lon = math.atan2(Y,X)
    hyp = ((X*X)+(Y*Y))**0.5
    lat = math.atan2(Z,hyp)
    return [(lat*180)/math.pi,(lon*180)/math.pi]
    
def getChunks(spawns):# a quick* chunking algorithm that chunks the spawns
# *it was quick for me to make at least
    iterations = 5   
    def chunks(spawns):
        maxDistance = .250
        foundIndexes = []
        output = []
        for i in range(0,len(spawns)-1):
            found = []
            for j in range(0,len(spawns)-1):
                skip = False
                if j not in foundIndexes:
                    d = getDistance(spawns[i]["latitude"],spawns[i]["longitude"],spawns[j]["latitude"],spawns[j]["longitude"])
                    if d < maxDistance:
                        found.append({"latitude":spawns[j]["latitude"],"longitude":spawns[j]["longitude"]})
                else:
                    skip = True
            if found:
                newPoint = avg(found)
                output.append({"latitude":newPoint[0],"longitude":newPoint[1]})
                foundIndexes.append(j)
            elif skip:
                output.append(i)
        return output
        
    bigout = spawns    
    for i in range(0,iterations):
        length = len(bigout)
        bigout = chunks(bigout)  
        if len(bigout) == length:
            break
    temp = []
    for i in bigout:
        try:
            temp.append([i["latitude"],i["longitude"],0])
        except:
            pass 
        
    return temp
    
def isInRange(lat1,lon1,lat2,lon2,radius):
    # this prevents the bot from leaving a circle by only paying attention
    # to landmarks within the scanned circle        
    R = 6371; # Radius of the earth in km
    dLat = deg2rad(lat2-lat1)  #deg2rad below
    dLon = deg2rad(lon2-lon1)
    a = ( 
    math.sin(dLat/2) * math.sin(dLat/2) +
    math.cos(deg2rad(lat1)) * math.cos(deg2rad(lat2)) * 
    math.sin(dLon/2) * math.sin(dLon/2) 
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = R * c #Distance in km
    if d <= radius:        
        return True
    else:
        return False
        
def merc(point): # to mercator
    latitude = point[0] 
    longitude = point[1]
    mapWidth = 5400;
    mapHeight = 2262;
    # get x value
    x = (longitude+180)*(mapWidth/360)
    # convert from degrees to radians
    latRad = latitude*math.pi/180
    # get y value
    mercN = math.log(math.tan((math.pi/4)+(latRad/2)),math.e)
    y = (mapHeight/2)-(mapWidth*mercN/(2*math.pi))
    return[x,y]

def generateSpiral(center,radius=.5,passDistance=.05): # for catching
    lat = center[0]
    long = center[1]

    turns = int(radius/passDistance)
    deltaAngle = turns*360 
    dperTurn = (radius/turns)/4

    if deltaAngle < 360:
        return False
    r = 0
    points = []
#    xs = []
#    ys = []
    for i in range(0,deltaAngle+90,90):
        r = r + dperTurn
        point = pointAtAngle(i,r,lat,long)
        points.append(point)
#        point = merc(point)
#        xs.append(point[0])        
#        ys.append(point[1])
#        if len(xs) >= 2:
#             plt.pause(0.05)
#             plt.plot([xs[len(xs)-1],xs[len(xs)-2]],[ys[len(ys)-1],ys[len(ys)-2]])
    return points