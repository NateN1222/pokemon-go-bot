# -*- coding: utf-8 -*-
import math
from pgoapi import utilities as util
import logging
import base64
from random import random, uniform
import time 
import geography 
radians_to_degrees = 180.0/math.pi    
degrees_to_radians = math.pi/180.0
earth_radius = 6371.0


# this class deals with reading the server's responses and dealing with 
# collected data. It could have been made a class, but I don't really see what
# the point of that would be since it really is an extension of class turtle

# to be honest, the turtle class was just getting a bit long 

#def deg2rad(deg):
#    return deg * (math.pi/180)
#
#
#def change_in_latitude(kilos):
#    return (kilos/earth_radius)*radians_to_degrees
#def change_in_longitude(latitude, kilos):
#    r = earth_radius*math.cos(latitude*degrees_to_radians)
#    return (kilos/r)*radians_to_degrees
#def pointAtAngle(angle,r,latitude,longitude):
#    angle = deg2rad(angle)
#    x = math.cos(angle)*r
#    y = math.sin(angle)*r
#    dlat = change_in_latitude(y)
#    dlon = change_in_longitude(latitude,x)
#    return [latitude+dlat,longitude+dlon,0]
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





 
#def getChunks(spawns):  
#    iterations = 5
#    def chunks(spawns):
#        maxDistance = .250
#        foundIndexes = []
#        output = []
#        for i in range(0,len(spawns)-1):
#            found = []
#            for j in range(0,len(spawns)-1):
#                skip = False
#                if j not in foundIndexes:
#                    d = getDistance(spawns[i]["latitude"],spawns[i]["longitude"],spawns[j]["latitude"],spawns[j]["longitude"])
#                    if d < maxDistance:
#                        found.append({"latitude":spawns[j]["latitude"],"longitude":spawns[j]["longitude"]})
#                else:
#                    skip = True
#            if found:
#                newPoint = avg(found)
#                output.append({"latitude":newPoint[0],"longitude":newPoint[1]})
#                foundIndexes.append(j)
#            elif skip:
#                output.append(i)
#        return output
#        
#    bigout = spawns    
#    for i in range(0,iterations):
#        length = len(bigout)
#        bigout = chunks(bigout)  
#        if len(bigout) == length:
#            break
#    temp = []
#    for i in bigout:
#        temp.append([i["latitude"],i["longitude"],0])
#    return temp


def getMapSearch(self,center,radius):            
    # idea: assign outlier value to each so you know how many points each one
    # is made of in the end in the "parents" entry
    lat1 = center[0]
    lon1 = center[1]
    # because we already have a wait in the update method    
    #self.plt.pause(3) # just because it's slightly more useful than time.sleep
    try:
        cell_ids = util.get_cell_ids(self.latitude,self.longitude)
        timestamps = [0,] * len(cell_ids) # for what purpose?
        theMap =self.player.get_map_objects(latitude = util.f2i(self.latitude), 
        longitude = util.f2i(self.longitude), 
        since_timestamp_ms = timestamps, 
        cell_id = cell_ids)
    except:
        logging.warn("Unexpexted response from get_map_objects")
        self.relog()
        return False

    try:
        cells = theMap["responses"]["GET_MAP_OBJECTS"]["map_cells"]
    except:
        logging.warn("Unexpexted response from get_map_objects")
        return False
        

    for i in cells:    
        if "forts" in i:
            for j in i["forts"]:
                lat2 = j["latitude"]
                lon2 = j["longitude"]
                if geography.isInRange(lat1,lon1,lat2,lon2,radius):
                    if "gym_points" in j:
                        if j["id"] not in self.foundGyms:
                            self.foundGyms[j["id"]] = 1
                            self.gyms.append(j)
                            self.plot(lat2,lon2,"gd")
                    else:
                        if j["id"] not in self.foundForts:
                            self.foundForts[j["id"]] = 1
                            self.forts.append(j)
                            self.plot(lat2,lon2,"rd")
        if "spawn_points" in i:
            for j in i["spawn_points"]:
                lat2 = j["latitude"]
                lon2 = j["longitude"]
                ID = str(lat2)+str(lon2)
                ID = base64.b64encode(bytes(ID,"UTF-8"))
                if geography.isInRange(lat1,lon1,lat2,lon2,radius):            
                    if ID not in self.foundSpawns:                        
                        self.spawns.append(j)
                        self.foundSpawns[ID] = 1
                        self.plot(lat2,lon2,"bd")

    
def getClosestPokestop(self): # useful?
    d = 0    
    closest = -1
    forts = self.forts
    pass
    for i in forts:
        d = geography.getDistance(self.latitude,self.longitude,i["latitude"],i["longitude"])
        if d < closest:
            closest = d
            output = i
    self.DestID = output["id"]
    return [output["latitude"],output["longitude"],0]


def catch(self,spawn_id,encounter_id):
        
        # If for any reason we get an error on any of these calls, the bot 
        # should check to see if it has any pokeballs, and space in inventory
        # as well as in party.    
        # some code from https://github.com/PokemonGo        
    def normalized_reticle_size(factor):
        minimum = 1.0 
        maximum = 1.950
        return uniform(minimum + (maximum - minimum) * factor,maximum)   

    def spin_modifier(factor):
        minimum = 0.0
        maximum = 1.0
        return uniform(minimum + (maximum - minimum) * factor,maximum)
    time.sleep(2)
    debug = self.player.encounter(
        encounter_id = encounter_id, 
        spawn_point_id = spawn_id, 
        player_latitude = self.latitude, 
        player_longitude = self.longitude) 
    time.sleep(1)
    if debug["status_code"] != 1: # wasn't a success
        pass
            
    caught = False    
    startTime = time.time()
    
    availableBalls = []
    for i in self.ballTypes:
        if i[1] > 0:
            availableBalls.append(i) 
            
    counter = 0
    ballVars = [counter,self.ballTypes]
    while caught == False and (time.time()-startTime) <= self.waitTime:
        def getNextBall(ballInfo): 
            counter = ballInfo[0]
            availableBalls = ballInfo[1]
            amount = len(availableBalls)
            index = counter % amount
            
            counter = counter + 1
        
            if availableBalls[index][1] == 0:
                Flag = True            
                for i in availableBalls:
                    if i[1] > 0:
                        Flag = False
                if Flag:
                    self.ballTypes = availableBalls
                    return False
                #\availableBalls.pop(index)
                print("availableBalls:"+str(availableBalls)+", index:"+str(index)+ ", amount:"+str(amount))
                return getNextBall([counter,availableBalls])
            else:
                availableBalls[index][1] = availableBalls[index][1]-1   
                print("throwing ball type " + str(availableBalls[index][0]) + ".") 
                print("amount left:" + str(availableBalls[index][1]))
                self.ballTypes = availableBalls
                return [counter,availableBalls,availableBalls[index][0]]
            
            self.ballTypes = availableBalls # it shouldn't get here
            return [counter,availableBalls,availableBalls[index][0]]

        
        
        ballVars = getNextBall(ballVars)
        if ballVars != False:
            ballType = ballVars[2]
        else:
            logging.info("probably out of pokeballs")
            self.getJob()
            return False
        
        # let's say 1 in 10 is a miss 
        self.plt.pause(2)
        if self.tryNumber == 10:
            hit = False
            response = []
            response = self.player.catch_pokemon( 
            encounter_id = encounter_id,
            pokeball = ballType, #using normal pokeballs for now
            normalized_reticle_size = normalized_reticle_size(1),
            spawn_point_id = spawn_id,
            hit_pokemon = hit,
            spin_modifier = spin_modifier(1), # another one
            normalized_hit_position = 1)
            self.tryNumber = 1
            
        else: 
            hit = True
            response = ["error"]
            self.plt.pause(0.75)
            response = self.player.catch_pokemon( 
            encounter_id = encounter_id,
            pokeball = ballType, #using normal pokeballs for now
            normalized_reticle_size = normalized_reticle_size(1),
            spawn_point_id = spawn_id,
            hit_pokemon = hit,
            spin_modifier = spin_modifier(1), # another one
            normalized_hit_position = 1)
            self.tryNumber = self.tryNumber + 1
        if response["status_code"] == 3:
            logging.warn("Invalid args, pokemon fled or out of pokeballs.")
            time.sleep(5)
            self.getJob() # get job is not switching correctly?
            return
        if "status" in response['responses']['CATCH_POKEMON']:
            catchStatus = response["responses"]["CATCH_POKEMON"]
            statusCode = response["status_code"]            
            
            
#            if response["status_code"] == 3:
#                logging.warn("Invalid args. Pokemon may have fleed [bug]")
#                caught = True
            if response["responses"]["CATCH_POKEMON"]["status"] == 1:
                logging.info("--got a pokemon--")                    
                caught = True
                # status 4 = failed catch attempt (?)
            elif response["responses"]["CATCH_POKEMON"]["status"] == 4:
                logging.info("Missed a pokeball.")
            elif response["responses"]["CATCH_POKEMON"]["status"] == 2:
                logging.info("\n missed one. catch_pokemon status: "
                + str(catchStatus)+"\n server status_code: "+str(statusCode))
            else:                
                caught = True
                logging.warn("\n\n Error unhandled.\n catch_pokemon status: "
                + str(catchStatus)+"\n server status_code: "+str(statusCode)
                + "\n Full response:\n"+str(response)                
                +"\n moving on \n\n")
                time.sleep(5)
                return True    
            
                
    # TODO: only handle pokemon caught code. Otherwise just cycle through ball
    # type.
    if (time.time()-startTime) >= 180:
        # possibly it would be wise to implement a "failed" counter instead of
        # using a "timeout"
        
        logging.warn("\n encounter taking more than 3 minutes.")
        logging.wrn("possibly out of pokeballs.")
        time.sleep(5)
        self.getJob() # get job is not switching correctly?
        return False
        
        
def catchNearby(self,point):        

    if self.Grinding:
        d = geography.getDistance(self.lastpt[0],self.lastpt[1],point[0],point[1])
        if d >= .14:
            self.lastpt = [self.latitude,self.longitude]    
            self.plt.pause(1.5)
        else:
            return False
    else:
        return False
    try:
        cell_ids = util.get_cell_ids(self.latitude,self.longitude)
        timestamps = [0,] * len(cell_ids) # for what purpose?
        theMap =self.player.get_map_objects(latitude = util.f2i(self.latitude), 
        longitude = util.f2i(self.longitude), 
        since_timestamp_ms = timestamps, 
        cell_id = cell_ids)
    except:
        logging.warn("Unexpexted response from get_map_objects")
        self.relog() 
        return False

    try:
        cells = theMap["responses"]["GET_MAP_OBJECTS"]["map_cells"]
    except:
        logging.warn("Unexpexted response from get_map_objects")
        return False
    for i in cells:
        if "catchable_pokemons" in i:
            print("found some pokemon :")
            for j in i["catchable_pokemons"]:
                print(self.data.PokemonNames[j["pokemon_id"]])
                response = catch(self,j["spawn_point_id"],j["encounter_id"])
                if response == False:
                    break
                
                
def transferDupes(self,pokemon_info):
    # evolve them? also when it comes across one with higher CP it should 
    # release the "incumbent" one
    found = {}
    for i in pokemon_info:
        
        if "is_egg" not in i:
            if "inventory_item_data" in i: # why...?
                i = i["inventory_item_data"] 
            try:
                pokemon_id = i["pokemon_id"]
                unique_id = i["id"]
            except KeyError:
                debug = i
                pass

            cp = i["cp"]
            if pokemon_id not in found:
                found[pokemon_id] = [cp,unique_id]
            else: 
                if found[pokemon_id][0]  <= cp:
                
                    print("letting "+self.data.PokemonNames[pokemon_id]+" go." )                    
                    time.sleep(1)
                    self.player.release_pokemon(pokemon_id = unique_id)
                    # what if they are equal?
                elif found[pokemon_id][0] > cp:
                    print("letting "+self.data.PokemonNames[pokemon_id]+" go." )                    
                    self.player.release_pokemon(pokemon_id = found[pokemon_id][1])
                    found[pokemon_id] = [cp,unique_id]
                    time.sleep(1)

def keepOnlyBuffs(self,items):
    def throwAway(item):
        time.sleep(2)
        self.player.recycle_inventory_item(item_id = item["item_id"], 
                                           count = item["count"])                                           
    for i in items:
        if "item_id" in i:        
            item_id = i["item_id"]
            if item_id not in self.data.keepWhilePreparing:
                throwAway(i)
                
def keepOnlyBalls(self,items):
    def throwAway(item):
        time.sleep(2)
        if "count" not in item:
            return
        response = self.player.recycle_inventory_item(item_id = item["item_id"], 
                                           count = item["count"])
        
        print(type(response))
        # remember to check the results
    for i in items:
        if "item_id" in i:        
            item_id = i["item_id"]
            if str(item_id) not in self.data.keepWhileFarming:
                print("throwing away "+self.data.ItemNames[str(item_id)])
                throwAway(i)
                    
        
def getInventory(self):
    # TODO: handle inventory full, egg hatched, no pokeballs, full pokemon,
    # making use of items, etc.        
        
    time.sleep(3)
    
    Flag = True    
    while Flag:
        try:
            inventory = self.player.get_inventory()
            Flag = False
        except:
            logging.warn("Unknown response from turtle.player.get_inventory()")
            logging.warn("trying again...")
            time.sleep(4)
            return True
        try:
            success = inventory["responses"]["GET_INVENTORY"]["success"]
            inventory = inventory["responses"]["GET_INVENTORY"]["inventory_delta"]["inventory_items"]
        except:
            logging.warn("unhandled response from get_inventory()")
            raise
            time.sleep(30)
            return True
    
    candy = []
    items = []
    pokemon_info = []
    incubators = []
    eggs = []
    self.ballTypes = [[1,0],[2,0],[3,0],[4,0]]
    Flag = True
    for i in inventory: # guess who didn't know about 'if "str" in dict'?
        try:
            candy_item = i["inventory_item_data"]["candy"]
            candy.append(candy_item)
        except KeyError:
            pass
        try:
            item_entry = i["inventory_item_data"]["item"]
            item_id = i["inventory_item_data"]["item"]["item_id"]
            if item_id == 1:
                #self.pokeballs = i["inventory_item_data"]["item"]["count"]
                self.ballTypes[0][1] = i["inventory_item_data"]["item"]["count"]
                Flag = False
            elif item_id == 2:
                self.ballTypes[1][1] = i["inventory_item_data"]["item"]["count"]
                Flag = False
            elif item_id == 3:
                self.ballTypes[2][1] = i["inventory_item_data"]["item"]["count"]
                Flag = False
            elif item_id == 4:
                self.ballTypes[3][1] = i["inventory_item_data"]["item"]["count"]               
                Flag = False
            items.append(item_entry)
        except KeyError:
            pass
        try:             
            pokemon = i["inventory_item_data"]["pokemon_data"]
            pokemon_info.append(pokemon)
        except KeyError:
            pass
        try:
            # TODO: something with this data
            incubators = i["inventory_item_data"]["egg_incubators"]["egg_incubator"]
        except KeyError:
            pass
    self.save()
    # TODO:
    # - handle eggs
    # - handle pokemon full by getting rid of duplicates (keep one with highest 
    # CP), do not evolve them to keep pokemon on hand condensed
    # - handle inventory full by throwing out lower rank items (make a totem
    # pole of priorities) so that you end up at the end game inventory
    # - if a nearby pokemon is "good", (not caught before? rare above a 
    # percent?) do a spiral search
    # - improve stability to make this in theory autonomous

    time.sleep(4)
    response = self.player.get_hatched_eggs()
    print(response)    
    time.sleep(4)
    
    temp = []    
    eggs = []
    for i in pokemon_info:
        if "is_egg" in i:
            eggs.append(i)
        else:
            temp.append(i)
    # item ID can also be 901    
    #test2 = self.player.use_item_egg_incubator(item_id=901,pokemon_id=)
    time.sleep(4)
    pokemon_info = temp
    if len(pokemon_info) >= 220: # higher = less stability more efficiency
        transferDupes(self,pokemon_info)
    if Flag:
        pass # didn't find a single pokemon     
            
    return {"incubator":incubators,"candy":candy,"items":items,"pokemon_info":pokemon_info,"success":success}                

#def generateSpiral(center,radius,passDistance): # for catching
#    lat = center[0]
#    long = center[1]
#
#    turns = int(radius/passDistance)
#    deltaAngle = turns*360 
#    dperTurn = (radius/turns)/4
#
#    if deltaAngle < 360:
#        return False
#    r = 0
#    points = []
##    xs = []
##    ys = []
#    for i in range(0,deltaAngle+90,90):
#        r = r + dperTurn
#        point = pointAtAngle(i,r,lat,long)
#        points.append(point)
##        point = merc(point)
##        xs.append(point[0])        
##        ys.append(point[1])
##        if len(xs) >= 2:
##             plt.pause(0.05)
##             plt.plot([xs[len(xs)-1],xs[len(xs)-2]],[ys[len(ys)-1],ys[len(ys)-2]])
#    return points
#    
#lat = 44.6999139904832    
#long = -93.230903855411
#center = [lat,long]
#fucc = generateSpiral(center,.5,.05)


#def getSearch(self):            
#    self.plt.pause(3) # just because it's slightly more useful than time.sleep
#    try:
#        cell_ids = util.get_cell_ids(self.latitude,self.longitude)
#        timestamps = [0,] * len(cell_ids) # for what purpose?
#        theMap =self.player.get_map_objects(latitude = util.f2i(self.latitude), 
#        longitude = util.f2i(self.longitude), 
#        since_timestamp_ms = timestamps, 
#        cell_id = cell_ids)
#    except:
#        logging.warn("Unexpexted response from get_map_objects")
#        return False
#
#    try:
#        cells = theMap["responses"]["GET_MAP_OBJECTS"]["map_cells"]
#    except:
#        logging.warn("Unexpexted response from get_map_objects")
#        return False
#    self.plt.pause(1)
                

#    self.plt.pause(3) # just because it's slightly more useful than time.sleep
#    try:
#        cell_ids = util.get_cell_ids(self.latitude,self.longitude)
#        timestamps = [0,] * len(cell_ids) # for what purpose?
#        theMap =self.player.get_map_objects(latitude = util.f2i(self.latitude), 
#        longitude = util.f2i(self.longitude), 
#        since_timestamp_ms = timestamps, 
#        cell_id = cell_ids)
#    except:
#        logging.warn("Unexpexted response from get_map_objects")
#        return False
#
#    try:
#        cells = theMap["responses"]["GET_MAP_OBJECTS"]["map_cells"]
#    except:
#        logging.warn("Unexpexted response from get_map_objects")
#        return False
#
#    forts = []        
#    gyms = []
#    pokemon = []
#    #catchable = {}
#    spawns = []
#    for i in cells:
#        if "catchable_pokemons" in i:
#            print("found some pokemon :")
#            for j in i["catchable_pokemons"]:
#                print(self.data.PokemonNames[j["pokemon_id"]])
#                self.catch(j["spawn_point_id"],j["encounter_id"])                       
#        if "nearby_pokemons" in i:
#            cell_id = i["s2_cell_id"]
#            for j in i["nearby_pokemons"]:
#                pokemon.append([j["pokemon_id"],j["encounter_id"],cell_id])
#                
#        if "forts" in i:
#            for j in i["forts"]:
#                if "guard_pokemon_id" in j:
#                    gyms.append(j)
#                else:
#                    forts.append(j)
#        if "spawn_points" in i:
#            cell_id = i["s2_cell_id"]
#            for j in i["spawn_points"]:
#                app = j
#                app["s2_cell_id"] = cell_id
#                spawns.append(app)
#    
#    for i in pokemon:
#        if i[1] in self.Pokedata["pokemon"]:
#            pass
#        else:
#            self.Pokedata["pokemon"][i[1]] = i
#
#    for i in forts:
#        if i["id"] in self.Pokedata["forts"]:
#            pass
#        else:
#            self.Pokedata["forts"][i["id"]] = i
#            # feels like this might take a bit of time to calculate...            
#            dist = getDistance(self.latitude,self.longitude,i["latitude"],i["longitude"])
#            if dist < self.closestFort[3]:
#                self.clostestFort = [i["latitude"],i["longitude"],i["id"],dist]
#                
#    for i in gyms:
#        if i["id"] in self.Pokedata["gyms"]:
#            pass
#        else:
#            self.Pokedata["gyms"][i["id"]] = i
#    # each cell ID is a dictionary key inside of the spawns key.
#    # all of the spawns within that cell are appended to a list inside of 
#    # the cell ID's key's entry. Maybe this is inefficient?
#    
#    return self.Pokedata
#                
                
                # This block of code provides a quick little input option.
                # incase you're a nerd and want to play a text based pokemon go
#                print("catch any?")
#                flag = True                
#                while flag:               
#                    inp = input("[y/n] :")
#                    if inp == "y":
#                        flag = False                        
#                        flag2 = True
#                        print("which one?")
#                        while flag2:                        
#                            toCatch = input("name :")     
#                            if toCatch in self.data.PokemonIds:
#                                if self.data.PokemonIds[toCatch] in catchable:
#                                    self.catch(catchable[self.data.PokemonIds[toCatch]]["spawn_point_id"],catchable[self.data.PokemonIds[toCatch]]["encounter_id"])
#                                    flag2 = False
#                                else:
#                                    print("haven't encountered that.")
#                            else:
#                                print("not a pokemon.")
#                    elif inp == "n":
#                        flag = False