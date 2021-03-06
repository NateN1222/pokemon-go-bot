# -*- coding: utf-8 -*-
"""
Created on Thu Aug  4 13:16:48 2016

@author: nate
"""
import turtle
import time
import os
import sys
import math
import logging
import data
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib import interactive
import numpy as np
from PIL import Image
# import Pokemon Go API lib
from pgoapi import pgoapi
from pgoapi import utilities as util
from geopy.geocoders import Nominatim
import s2sphere
import geography
import parsers
# this class deals with having multiple accounts. 
# multiple accounts have not been tested at once, so you can consider that 
# feature unimplemented. However, it would be easy to implement a system that
# cycles through accounts over time so you can 

logging.basicConfig(level=logging.INFO)
interactive(True)

sys.path.append(os.path.dirname(os.path.realpath(__file__))) # ...what


class hivemind:
    def __init__(self):
        self.turtles = []
        self.lat = lat
        self.long = long
        
        
    def save(self):
        for i in self.turtles:
            i.save()
        
        
    def load(self,accountID,lat,long):
        with open('csvdata/accounts.csv', 'r') as f:
            lines = f.readlines()
            f.close()
        
        line = lines[accountID]        
        
        lineData = []        
        chunk = ""
        
        line = line[:len(line)-3]
        for i in line:
            if i == ",":
                lineData.append(chunk)
                chunk = ""
            else:
                chunk = chunk + i
        lineData.append(chunk)        
        api = pgoapi.PGoApi()
        api.activate_signature("/home/nate/spyder workspace/pgo_unofficial/pgoapi/libencrypt.so")
        api.set_authentication(provider = "ptc",
        username = lineData[0], 
        password = lineData[1])
         
       # in CSV file, format is:
        # user,pass,lat,long
        turt = turtle.turtle(api,
        float(lineData[2]),
        float(lineData[3]),
        accountID,
        lineData[0],
        lineData[1],
        plt)
        time.sleep(1)
        turt.latitude = lat
        turt.longitude = long
        turt.player.set_position(lat,long,0)
        self.turtles.append(turt)

    def displayMap(self,latitude,longitude):
        
        # this is just a lat/long to mercator method right now.
        
        mapWidth    = 5400;
        mapHeight   = 2262;
            
        # get x value
        x = (longitude+180)*(mapWidth/360)
            
        # convert from degrees to radians
        latRad = latitude*math.pi/180
            
        # get y value
        mercN = math.log(math.tan((math.pi/4)+(latRad/2)),math.e)
        y = (mapHeight/2)-(mapWidth*mercN/(2*math.pi))
        
        img = Image.open("bigmercator.png")
        plt.plot(x,y,'ro')
        imgplot = plt.imshow(img)
        
    def tick(self): # update all active turtles
        hasTask = True
        for turt in self.turtles:
            hasTask = turt.update()
        return hasTask
            # if hasTask == False then the turtle doesn't have a task (no shit)

def genTrip():  
    # the point of this is to read path data generated by google earth.

    f = open("coords2.txt","r")
    line = f.read()
    f.close()
    dat = []
    word = ""
    
    for i in line:
        if i == "," or i == " ":
            dat.append(float(word))
            word = ""
        else:
            word = word + i
    
    latitudes = []
    longitudes = []
    altitudes = []
    trip = []
    
    for i in range(0,len(dat)-1,3):
        longitudes.append(dat[i])
    for i in range(1,len(dat)-1,3):
        latitudes.append(dat[i])
    for i in range(2,len(dat)-1,3):
        altitudes.append(dat[i])
    for i in range(0,len(latitudes)-1):
        trip.append([latitudes[i],longitudes[i],altitudes[i]])
    return trip # format [lat,long,alt]

        
        
        
        
        

lats = []
longs = []
plt.ion()
for lat,long,alt in genTrip():
    lats.append(lat)
    longs.append(long)
mapWidth    = 5400;
mapHeight   = 2262;
        
for i in range(0,len(lats)-1):
    latitude = lats[i]
    longitude = longs[i]
    x = (longitude+180)*(mapWidth/360)
            
    # convert from degrees to radians
    latRad = latitude*math.pi/180
            
    # get y value
    mercN = math.log(math.tan((math.pi/4)+(latRad/2)),math.e)
    y = (mapHeight/2)-(mapWidth*mercN/(2*math.pi))      
    
img = Image.open("bigmercator.png")
plt.imshow(img)
plt.show()


#trip = genTrip()
#for i in trip:
#    hive.turtles[0].Destinations.append(i)

point = [40.76808045, -73.9818973468278, 0.0]
lat = point[0]
long = point[1]

hive = hivemind()
hive.load(2,lat,long)

#geocoder = Nominatim()
#point = geocoder.geocode("1 Twins Way, Minneapolis")
#point = geocoder.geocode("830 5th Ave, New York, NY 10065")
#point = geocoder.geocode("Columbus Circle, New York, NY")
#long = point.longitude
#lat = point.latitude

geography.plot(hive.turtles[0],lat,long,"ks")

hive.turtles[0].search(lat,long)
Flag = True

while True:
    while Flag:    
        try:
            Flag = hive.tick()
        except Exception as ex:
            print("got an exception")
            hive.turtles[0].relog()
            logging.exception("exception:")
            time.sleep(10)
    Flag = True


print(len(hive.turtles[0].Destinations))

hive.turtles[0].Destinations = []
    
#while True:    
#    while len(self.Destinations > 0):    
#        dest = hive.turtles[0].forts.pop(0)
#        hive.turtles[0].setDestination(dest["latitude"],dest["longitude"],0)
#        print(len(hive.turtles[0].forts))
#        Flag = True   
#        while Flag:
#            try:
#                Flag = hive.tick()
#            except:
#                print("fuck")
#        time.sleep(3)
#        hive.turtles[0].player.fort_search(fort_id = dest["id"],
#        player_latitude = dest["latitude"],
#        player_longitude = dest["longitude"],
#        fort_latitude = dest["latitude"],
#        fortrue
#    while Flag:    
#        Flag = hive.tick()
#    hive.turtles[0].grind()


#closest = hive.turtles[0].getClosestPokestop() # this works as intended
#
#hive.turtles[0].Destinations.append(closest)
#hive.turtles[0].setDestination(0,0,0,nextDest = True)
#
#Flag = True
#while Flag:
#    Flag = hive.tick()
#
#hive.turtles[0].goShopping() # this does not work as intended.
#hive.turtles[0].save() 
#longitude = dest["longitude"])
#    hive.turtles[0].search(lat,long)
#    Flag = T

print("fin")
pass















