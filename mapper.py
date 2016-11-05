# -*- coding: utf-8 -*-
"""
Created on Wed Aug 10 10:41:03 2016

@author: nate
"""
import math
from s2sphere import LatLng, Angle, Cap, RegionCoverer
import geopy
from geopy.geocoders import Nominatim
from geopy.distance import VincentyDistance
import numpy as np
from PIL import Image
from matplotlib import pyplot as plt
# from matplotlib import interactive
from pgoapi import utilities as util
import parsers
import decimal
import geography

# these are the methods used by the turtle object when it is scanning.

#
#import matplotlib.pyplot as plt
#import matplotlib.image as mpimg
#from matplotlib import interactive
#import numpy as np
#from PIL import Image

#
#earth_radius = 3960.0
#degrees_to_radians = math.pi/180.0
#radians_to_degrees = 180.0/math.pi

#def deg2rad(deg):
#    return deg * (math.pi/180)
#  
#def getDistance(lat1,lon1,lat2,lon2):
#    R = 6371; # Radius of the earth in km
#    dLat = deg2rad(lat2-lat1)  #deg2rad below
#    dLon = deg2rad(lon2-lon1)
#    a = ( 
#    math.sin(dLat/2) * math.sin(dLat/2) +
#    math.cos(deg2rad(lat1)) * math.cos(deg2rad(lat2)) * 
#    math.sin(dLon/2) * math.sin(dLon/2) 
#    )
#    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
#    d = R * c #Distance in km
#    return d
#
#def change_in_latitude(kilos):
#    #    "Given a distance north, return the change in latitude."
#    miles = kilos * 0.621371    
#    return (miles/earth_radius)*radians_to_degrees
#
#def change_in_longitude(latitude, kilos):
#    #    "Given a latitude and a distance west, return the change in longitude."
#    # Find the radius of a circle around the earth at given latitude.
#    miles = kilos * 0.621371
#    r = earth_radius*math.cos(latitude*degrees_to_radians)
#    return (miles/r)*radians_to_degrees


class Mapper:
    def __init__(self,lat,long,plt,r=2,plot=True): # plot is for debugging
        self.plotEnabled = plot        
        self.centerLat = lat
        self.centerLong = long
        self.latitude = lat
        self.longitude = long
        self.radius = r
        self.radiusPoint = self.radius + self.latitude
        self.Points = []
        self.scanDist = .4# how often should it call get_map_objects() (in KM)
        self.scanDist2 = .9 # because I can't figure out this bug right now
        # bigger than .5
        if self.plotEnabled:        
            self.plt = plt
            
        
    def scan(self):
        def pointAtAngle(angle):
            # given: lat1, lon1, b = bearing in degrees, d = distance in kilometers
            origin = geopy.Point(self.latitude, self.longitude)
            destination = VincentyDistance(kilometers=self.radius).destination(origin, angle)
            lat2, lon2 = destination.latitude, destination.longitude
            return[lat2,lon2]
#            
#            angle = geography.deg2rad(angle)
#            x = math.cos(angle)*self.radius
#            y = math.sin(angle)*self.radius            
#            dlat = geography.change_in_latitude(y)
#            dlon = geography.change_in_longitude(self.latitude,x)
#            return [self.latitude+dlat,self.longitude+dlon]

        def flip(aList):
            temp = aList[1] 
            aList[1] = aList[0]
            aList[0] = temp
            return aList
            
        numScans = (self.radius * 2) / self.scanDist
        #print(numScans)
        points = []
        if self.plotEnabled:
            self.plt.pause(2)
        Flag = False
        aList = []
        for i in range(1,int(numScans/2)):
            angle = (i/numScans)*360
            point = pointAtAngle(angle)
            
            
            oppAngle = abs(angle - 360)
            oppPoint = pointAtAngle(oppAngle)

            self.plot(point[0],point[1],"r+")
            self.plot(oppPoint[0],oppPoint[1],"b+")

            aList = [point,oppPoint]
            if Flag:
                Flag = False
                aList = flip(aList)
                for i in aList:
                    if self.plotEnabled:
                        mercat = geography.merc(i)
                        x = mercat[0]
                        y = mercat[1]
                        points.append(i)
                        s = str(len(points)-1)
                        self.plt.text(x, y, s)
                    else:
                        points.append(i)
                self.genPointsBetween(points[len(points)-2],points[len(points)-1])


            else:
                Flag = True
                for i in aList:
                    if self.plotEnabled:
                        mercat = geography.merc(i)
                        x = mercat[0]
                        y = mercat[1]
                        points.append(i)
                        s = str(len(points)-1)
                        self.plt.text(x, y, s)
                    else:
                        points.append(i)
                self.genPointsBetween(points[len(points)-2],points[len(points)-1])
        return self.Points                


    def genPointsBetween(self,Dest,currentPos): 
        latitude = currentPos[0]
        longitude = currentPos[1]
        distance = geography.getDistance(latitude,longitude,Dest[0],Dest[1])                
        # TODO: get distance per unit time and just use that so it doesn't need
        # to call update() as much?
        steps = int(distance / self.scanDist2)
        print("generating "+str(steps)+" steps for "+str(distance)+ " Km." )
        
        if steps <= 1:
            return Dest

        stepLat = (Dest[0] - latitude) / steps
        stepLong = (Dest[1] - longitude) / steps
        point = []
        tempLong = longitude
        tempLat = latitude
        for i in range(0,steps):
        # TODO: verify this sytem for edge cases. 
            tempLong += stepLong
            tempLat += stepLat
            point = [tempLat,tempLong]            
            self.Points.append(point) 
            self.plot(point[0],point[1],"w+")        
        #self.Points.append([currentPos[0],currentPos[1]])
        #self.plot(point[0],point[1],"w+")
        return self.Points

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
#                
#    def plot(self,latitude,longitude,color):  
#        if self.plotEnabled:            
#            mapWidth = 5400;
#            mapHeight = 2262;
#            # get x value
#            x = (longitude+180)*(mapWidth/360)
#            # convert from degrees to radians
#            latRad = latitude*math.pi/180
#            # get y value
#            mercN = math.log(math.tan((math.pi/4)+(latRad/2)),math.e)
#            y = (mapHeight/2)-(mapWidth*mercN/(2*math.pi))
#            self.plt.plot(x,y,color)
#            self.plt.pause(0.05)
        

#    
#geocoder = Nominatim()
#point = geocoder.geocode("16710 Interlachen Blvd Lakeville Minnesota")
#long = point.longitude
#lat = point.latitude
##test = get_cell_ids(lat,long)    
#img = Image.open("bigmercator.png")
#plt.imshow(img)
#plt.ion()
#plt.show()
#
#mapper = Mapper(lat,long,plt)
#mapper.scan()
    
    
    
    
    
    
    
#        def genPointsBetween(self,currentPos,Dest,Points=[],scanDist=.2,distanceToDest = 69): # 69 = biggest number
#        if Points == []:
#            print("here")
#            scanDist = self.scanDist
#            Points.append(currentPos)
#            distanceToDest = getDistance(currentPos[0],currentPos[1],Dest[0],Dest[1])
#
#
#        def nextPointAtAngle(angle):
#            #angle = deg2rad(angle)
#            x = math.cos(angle)*scanDist
#            y = math.sin(angle)*scanDist          
#            dlat = change_in_latitude(y)
#            dlon = change_in_longitude(currentPos[0],x)
#            return [currentPos[0]+dlat,currentPos[1]+dlon]
#        def angleAtPoint(currentPos,point):
#            # if we get errors here, than we don't need any scans between
#            # these points because they are close enough already?
#            try:
#                opp = decimal.Decimal(abs(currentPos[1] - point[1]))
#                adj = decimal.Decimal(abs(currentPos[0] - point[0]))
#                angleRadians = math.atan(opp/adj)
#                return angleRadians
#            except:
#                print("accept")
#                return True
#                
#        angle = angleAtPoint(currentPos,Dest)
#        
#        if type(angle) == bool:
#            Points.append(Dest)            
#            self.plot(Dest[0],Dest[1],"w+")
#            return Points
#        else:
#            nextPoint = nextPointAtAngle(angle)
#        # if it's farther than the destination, just round off at the 
#        # destination and return
#        lastDist = distanceToDest
#        distanceToDest = getDistance(currentPos[0],currentPos[1],Dest[0],Dest[1])
#        distanceToNext = getDistance(currentPos[0],currentPos[1],nextPoint[0],nextPoint[1])
#        print(str(lastDist))
#        print(str(distanceToDest))
#        if lastDist < distanceToDest:
#            return Points
#        else:
#            #lastDist = distanceToDest
#            Points.append(nextPoint)
#            self.plot(nextPoint[0],nextPoint[1],"w+")
#            return self.genPointsBetween(nextPoint,Dest,Points=Points,scanDist=scanDist,distanceToDest=distanceToDest)
#   
    
    
#                x1 = orderedPoints[len(orderedPoints)-1][1]
#                y1 = orderedPoints[len(orderedPoints)-1][0]
#                x2 = orderedPoints[len(orderedPoints)-2][1]
#                y2 = orderedPoints[len(orderedPoints)-2][0]            
#                p = merc([x1,y1])                    
#                x1 = p[0]                    
#                y1 = p[1]
#                p = merc([x2,y2])
#                x2 = p[0]
#                y2 = p[1]        
#                self.plt.plot([x1, x2], [y1, y2], color='k', linestyle='-', linewidth=2)
    
    
    
    
#            def merc(point): # to mercator
#            latitude = point[0] 
#            longitude = point[1]
#            mapWidth = 5400;
#            mapHeight = 2262;
#            # get x value
#            x = (longitude+180)*(mapWidth/360)
#            # convert from degrees to radians
#            latRad = latitude*math.pi/180
#            # get y value
#            mercN = math.log(math.tan((math.pi/4)+(latRad/2)),math.e)
#            y = (mapHeight/2)-(mapWidth*mercN/(2*math.pi))
#            return[x,y]
#        
    
    
    
    
    
    
    
    
    
    