#!/usr/bin/python3.6
import mysql.connector
from mysql.connector import Error
import requests
import math
import json
import sys
import mz2geohash

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  database="",
  password=""
)

if bool(mydb) == False:
    print("Connection error")
    sys.exit(1)
else:
    continue

try:
    file = open("address.txt", "a+")
    #for i in file:
    for i in file.readlines():
        full_address = (i[0:])
    


    # STEP #1 -- geocode address

    query = ("http://www.geocode.com/geocode/lookup.json?")    
    payload = {'q':full_address}
    r = requests.get(query,params=payload).json()
    
    d = r['features'][0]['geometry']['coordinates']
    geocode_result = {"lat":d[1],"lon":d[0]}
    #print(geocode_result)
    
    InputLat = float(d[1])
    InputLong = float(d[0])
    
    #calculate angular radians from input decimel degress
    LatRad = math.radians(InputLat) #for latitude from loop
    LongRad = math.radians(InputLong) #for longitude from loop
    print("The Latitude and longitude for input is: ",LatRad, LongRad,"RADIANS<br>)"
    #calculate lat/long mins for bounding box
    
    ####     ELEVATION VALUE      #######
    
    loc_str = str(geocode_result['lat']) + "," + str(geocode_result['lon'])
    
    
    query = 'http://geo.epropertyfacts.com/elevation/lookup.json'
    payload = {'locations':loc_str}
    
            # request elevation
    r = requests.get(query,params=payload).json()
    
    lat_lon = [r['results'][0]['latitude'],r['results'][0]['longitude']]
                #elevation = r['results'][0]['elevation']
                # convert from meters to feet
    elevation = round(float(r['results'][0]['elevation']) / 0.3048,2)
                #print(json.dumps({'elevation':elevation}))
    geocode_result['elevation'] = elevation
    geocode_result['elevation_units'] = 'feet'
    geohash = mz2geohash.encode((d[0],d[1]))
    #print(geohash)
    
    
    
    geocode_line = ", " + str(d[1]) + ", " + str(d[0]) + ", " + str(elevation) + ", " + str(geohash) + ", " + str(LatRad) + ", " + str(LongRad)
    #print(geocode_line)
    file.write(geocode_line)
    
    file.close()
    print("<strong>Latitude: </strong>" + str(d[1]) + "<br>" + "<strong>Longitude: </strong>" + str(d[0]) + "<br>" + "<strong>Site Elevation in feet: </strong>" + str(elevation) + "<br><strong>Geohash: </strong>" + str(geohash))
    ####    ADDED FOR RADIAN VALUE TO QUERY TABLE ########

except IOError as e:
    print("I/O error(): ".format(e.errno, e.strerror))
except ValueError:
    print("Could not convert data to an integer.")
except:
    print("Unexpected error:", sys.exc_info())
    raise



#print(json.dumps(geocode_result))
    # return results in json format

