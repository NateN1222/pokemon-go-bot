# -*- coding: utf-8 -*-
"""
Created on Sat Jul 30 11:37:51 2016

@author: nate
"""

import time
import os
import sys
import math
import logging
import data
import numpy as np
from PIL import Image
from random import random, uniform
import parsers
import mapper
import geography
#import matplotlib.pyplot as plt

# add directory of this file to PATH, so that the package will be found
# import Pokemon Go API lib
from pgoapi import pgoapi
from pgoapi import utilities as util
from geopy.geocoders import Nominatim
import s2sphere
from s2sphere import LatLng, Angle, Cap, RegionCoverer

# idea: save different credentials in a text file (non-volatile memory)
# so you can choose profiles

# idea: have bots walk around looking for rare pokemon. When it finds one,
# another bot will spawn and catch it

# idea: when starting, 

# idea: sell an app that collects the daily bonus every day

# idea: symetrical number space? like a normal graph but with symettry 

#logging.basicConfig(filename='example.log',level=logging.DEBUG)
def deadReckon(lat,lng,dn,de):
    # Earth’s radius, sphere
    R=6378137
    # Coordinate offsets in radians
    dLat = dn/R
    dLon = de/(R*math.cos(math.pi*lat/180))
    # OffsetPosition, decimal degrees
    latO = lat + dLat * 180/math.pi
    lonO = lng + dLon * 180/math.pi
    return([latO,lonO])
    
def getDistance(lat1,lon1,lat2,lon2):
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
    return d;


def deg2rad(deg):
  return deg * (math.pi/180)

    
def get_cell_ids(lat, long, radius = 10):# I don't understand this at all!
    origin = s2sphere.CellId.from_lat_lng(s2sphere.LatLng.from_degrees(lat, long)).parent(15)
    walk = [origin.id()]
    right = origin.next()
    left = origin.prev()

    # Search around provided radius
    for i in range(radius):
        walk.append(right.id())
        walk.append(left.id())
        right = right.next()
        left = left.prev()

    # Return everything
    return sorted(walk)


class turtle:
    # turtle will be a geographical turtle useful for controlling the player
    # Position should be stored in a text file.
    # We should generate a route and stick with it, but also have a landmark finding routine
    
    def __init__(self,turtle,lat,long,ID,user,passw,plt): # turtle is a reference to the api object
        # TODO: make it add the user/pass to .csv if it isn't already there
        # so much shit here. is this really neccessary? kind of...
    
        self.startTime = int(round(time.time() * 1000))
        self.chillAt = self.startTime + 4*60*60*1000

        self.plt = plt        
        self.data = data.Data()        
        self.plotEnabled = True
        
        self.user = user    
        self.passw = passw
        self.ID = ID
        
        self.tryNumber = 1 # used to make sure every 10th pokeball is missed

        self.lastTime = int(round(time.time() * 1000))
    
        self.minimum = 0  #for random number generating
        
        self.searches = 1
        
        self.Grinding = False
        self.Searching = False  
        self.runningErrands = False        

        self.totalSearches = 0

        self.ScanResults = []        
        
        self.player = turtle
        self.longitude = long
        self.latitude = lat

        self.stepsPerKm = 25
        self.steps = 0# this gets overwritten
        self.center = []
        self.radius = 2
        self.gyms = []
        self.forts = []
        self.spawns = []
        self.spawnChunks = []
        self.foundForts = {}
        self.foundGyms = {}
        self.foundSpawns = {}
        self.pokeballs = 0
        self.ballTypes = []
        self.noTask = True
        
        self.rateKph = 14 # when trying to not get flagged as driving
        self.fastRateKph = 30 # when you don't care if you get flagged for driving
        self.walkingRateKph = 14
        self.timePerKm = int(1 / self.rateKph * 60 * 60 * 1000) # in milliseconds
        self.stepTime = int(self.timePerKm / self.stepsPerKm)

        self.lastpt = [self.latitude,self.longitude]
        self.Points = []
        self.Destinationlat = 0
        self.Destinationlong = 0
        self.fort = {}        
        self.destID = 0
        
        self.Pokedata = {"spawns":{},"forts":{},"gyms":{},"pokemon":{}}
        self.Destinations = []
        self.waitTime = 180        
        
        self.player.login("ptc", # returns true if a success
        self.user,
        self.passw,
        self.latitude,
        self.longitude,
        0,
        False)
        #self.getJob() instead call after search complete
        time.sleep(5)
#        fuck = self.player.mark_tutorial_complete(
#        tutorials_completed = [True, True, True],
#        send_marketing_emails = True,
#        send_push_notifications = False)
        
    def relog(self):
        
        api = pgoapi.PGoApi()
        api.activate_signature("/home/nate/spyder workspace/pgo_unofficial/pgoapi/libencrypt.so")
        api.set_authentication(provider = "ptc",
        username = self.user, 
        password = self.passw) 
        self.player = api        
        #self.__init__(api,self.latitude,self.longitude,self.ID,self.user,self.passw,self.plt)
        time.sleep(15)
        wait = 0      
        success = False
        while success == False:        
            success = self.player.login("ptc", # returns true if a success
            self.user,
            self.passw,
            self.latitude,
            self.longitude,
            0,
            False)
            wait = wait + 5
            time.sleep(wait)
        return True        
    def Chill(self): # essentially just pretend like we are taking a break.
        # this should improve stability enough for me to leave it on over long
        # periods of time.
        print("turtle is chilling.")
        self.save()
        self.startTime = int(round(time.time() * 1000))
        self.chillAt = self.startTime + 5*60*60*1000
        time.sleep(60*60)

        self.relog()
        return True

        # call the constructor again?
    def changeSpeed(self,speedKph):        
        self.rateKph = speedKph
        self.timePerKm = int(1 / speedKph * 60 * 60 * 1000) # in milliseconds
        self.stepTime = int(self.timePerKm / self.stepsPerKm)
        
    def save(self):  
        # dump all of our found data into a CSV file so we can analyze it later
        # also write account position so we don't forget where we left off
    
        def appendCSV(line,file):
            with open(file, "a") as myfile:
                myfile.write(line)
        def readRow(row,file): # TODO: this
            pass
            
            
        f = open('csvdata/accounts.csv', 'r')
        line = self.user + "," + self.passw + "," + str(self.latitude) + "," + str(self.longitude) + "\n"
        lines = f.readlines()
        lines[self.ID] = line
        f.close()    
        
        f = open("csvdata/accounts.csv","w")
        linesStr = ""
        for i in lines:
            linesStr = linesStr+i
        f.write(linesStr)
        f.close()

        line = ""

        for key,value in self.Pokedata["pokemon"].items():
            appendCSV(str(key)+","+str(value[0])+","+str(value[2])+"\n","csvdata/pokemon.csv")
        
    def to_lat_lng(self): # lat lng is an s2sphere class.
        temp = s2sphere.LatLng(self.latitude,self.longitude) # unused
        return temp
            
    def updateTime(self): # returns the elapsed time, updates lastTime.   
        #currentTime = int(time.time()*1000)
        currentTime = int(round(time.time() * 1000))
        if self.lastTime > currentTime: # it is a new day, maybe this is where
            # we should collect daily bonuses
            elapsedTime = 0
        else:
            if not(self.lastTime + self.stepTime > currentTime):
                elapsedTime = currentTime - self.lastTime
                self.lastTime = currentTime
                return elapsedTime
        return 0
    def prepareForGym(self): 
    # this should be something that the user must call.
        pass
    def getJob(self):
        # this should be able to just check the current state completely based
        # upon inventory (can we grind or not?)
    
    
    
        print("amount of destinations:" + str(len(self.Destinations)))
        
        self.Searching = False
        self.noTask = False
        inventory = parsers.getInventory(self)
        totalBalls = 0        
        for i in self.ballTypes:
            totalBalls += i[1]
        
        print("amount of pokeballs:" + str(totalBalls))

        #parsers.transferDupes(self,inventory["pokemon_info"])        
        parsers.keepOnlyBalls(self,inventory["items"])
        if totalBalls <= 10:
            print("less than 10 pokeballs. switching to shop mode.")
            self.Destinations = []
            self.Points = []

            #TODO: if we find a type of ball, add it to the "use ball" list
            self.changeSpeed(self.fastRateKph)
            self.Grinding = False
            self.runningErrands = True
            self.runErrands()
            return False
            
        elif len(self.Destinations) == 0:
            print("no destinations. switching to catch mode.")            
            self.Destinations = []
            self.Points = []
            self.changeSpeed(self.walkingRateKph)
            chunks = geography.getChunks(self.spawns)
            for i in chunks:
                for j in geography.generateSpiral(i):
                    self.Destinations.append(j)
                
            self.Grinding = True
            self.runningErrands = False
            return False
        
        print("no issues found. Continuing current task.")
        return True
            
    def update(self): # move to next point if it has been long enough
        
        if int(round(time.time() * 1000)) > self.chillAt:# what about 12:00am?
            self.Chill()
            return True
   
        if self.noTask:
            self.getJob()
            
        if self.Searching:
            return self.updateSearch()

            
        if(self.updateTime() >= self.stepTime):
            if len(self.Points) != 0:                
                point = self.Points.pop(0)
                self.player.set_position(point[0],point[1],0)
                
                self.latitude = point[0]
                self.longitude = point[1]
                self.plot(self.latitude,self.longitude,"b+")
                logging.info("step " + str(self.steps-(len(self.Points)))
                + " out of " + str(self.steps))
                
                parsers.catchNearby(self,point)
                
                #return True
            else:
                if len(self.Destinations) == 0:
                    self.noTask = True
                    if self.Grinding:
                        self.getJob()   
                    if self.runningErrands:
                        self.runningErrands = False         
                    #return True # false
                else:
                    dest = self.Destinations.pop(0)

                    if self.runningErrands:
                        self.goShopping(self.fort)
                        self.fort = dest[3]
                    self.setDestination(0,0,0,destination = dest)
                    #return True
                    
        else: # hasn't been long enough
            if len(self.Points) == 0:
                if len(self.Destinations) == 0:
                    if self.runningErrands:
                        self.goShopping(self.fort)
                    if self.Grinding:
                        self.getJob()                        
                        #return True
                else:
                    dest = self.Destinations.pop(0)
                    if self.runningErrands:
                        self.goShopping(self.fort)
                        self.fort = dest[3]
                    self.setDestination(0,0,0,destination = dest)
                    #return True
        return True
        # moves to the next point        
        # will get errors over large distances            
    def setDestination(self,dlat,dlong,dalt,destination = [],nextDest = False):
        # sets the destination and generates points. This will over write the 
        # current set of points
        # TODO: something with altitude
        if destination:
            dlat = destination[0]
            dlong = destination[1]
            dalt = 0
        if nextDest:
            dest = self.Destinations.pop()
            dlat = dest[0]
            dlong = dest[1]
            dalt = 0
        distance = geography.getDistance(self.latitude,self.longitude,dlat,dlong)                
        tripTime = self.timePerKm * distance        
        # TODO: get distance per unit time and just use that so it doesn't need
        # to call update() as much?        
        logging.info("New destination. distance (Km) = " + str(distance))
        logging.info("Trip will take "+str(int(tripTime / 1000))+" seconds")
            
        self.steps = int(distance * self.stepsPerKm)
        if self.steps == 0:
            self.steps = 1
            self.stepTime = tripTime

        self.Points = []
        self.Destinationlat = dlat
        self.Destinationlong = dlong
        stepLat = (dlat -self.latitude) / self.steps
        stepLong = (dlong - self.longitude) / self.steps
        point = []
        tempLong = self.longitude
        tempLat = self.latitude
        for i in range(0,self.steps):
        # TODO: verify this sytem for edge cases. 
            tempLong += stepLong
            tempLat += stepLat
            point = [tempLat,tempLong]            
            self.Points.append(point) 

    def search(self,lat,long,r=2):
        # when searching, the bot does things that aren't really "human"
        self.Searching = True
        self.noTask = False
        self.center = [lat,long]
        self.radius = r
        self.player.set_position(lat,long,0) # this will do a "big jump"
        # we should also set the speed to the maximum for us not to get banned
        mapObj = mapper.Mapper(lat,long,self.plt,r=r)
        self.Destinations = mapObj.scan()      
        #self.setDestination(0,0,0,0,nextDest=True)
    def updateSearch(self):
        if len(self.Destinations) > 0 and self.Searching == True:        
            logging.info("Amount of points left in search: "+str(len(self.Destinations)))
            self.plt.pause(4) # a constant because speed isn't important.
            # You can set this to whatever you want realitively safely, just
            # keep the diameter of your scan in mind and don't go too crazy
            dest = self.Destinations.pop()
            self.player.set_position(dest[0],dest[1],0)
            self.latitude = dest[0]
            self.longitude = dest[1]
            self.plot(self.latitude,self.longitude,"y+")
            parsers.getMapSearch(self,self.center,self.radius)
        else:
            self.Searching = False
            self.getJob()
            return False
        # TODO: handle errors with the api calls
        return True
    def grind(self):
        # sets a plan to start catching pokemon
        # TODO: check inventory and handle error conditions (no search, 
        # network error)
        try:
            dest = self.spawnChunks.pop(4)
        except:
            return False
        
        if self.Searching == False:
            if dest == None or dest == []:
                    return False# haven't searched
            self.Grinding = True

        trip = geography.generateSpiral(dest)
        self.Destinations = trip
        self.save()
        return True
        
    def runErrands(self):
        # run to the pokebega to get some eggs and pokeballs

        self.Destinations = []
        self.searches = 0
        # TODO: order forts by how close they are. And handle what happens when
        # inventory is full.
        
        # idea: get a "prepare for gym" method. This throws away all pokeballs
        # and fills inventory with potions and revives.
        
        # idea: when searching, get the most dense region and go to all 
        # pokestops in that region. It could even use the same chunk routine
        # as the spawns do.
        #debug = self.forts
        fort = geography.getChunks(self.forts)
        fort = fort[0]
        inRange = geography.pokestopsInRange(self,fort[0],fort[1],self.forts)
        for i in inRange:
            self.Destinations.append([i["latitude"],i["longitude"],0,i])

        self.Destinations = self.Destinations            
            
        self.runningErrands = True    
        self.Grinding = False
        
    def goShopping(self,fort):
        self.plt.pause(3)
                
        try:        
            response = self.player.fort_search(fort_id = fort["id"],
            player_latitude = self.latitude,
            player_longitude = self.longitude,
            fort_latitude = fort["latitude"],
            fort_longitude = fort["longitude"])
            self.searches = self.searches + 1
        except:
            pass
        
        if self.searches >= self.totalSearches:
            self.searches = 1
            self.getJob()
        
        if self.Destinations == []:
            self.noTask = True
            self.runningErrands = False
    # methods that deal purely with geography
        
    def evadeBan(self):
        pass # attempt and fail to spin a pokestop 40 times.

    def campLure(self):
        pass # when we get a lure, deploy it and then walk around it until it 
        # until it expires

            
        
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
        
