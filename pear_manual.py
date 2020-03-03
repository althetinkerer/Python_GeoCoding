#!/usr/bin/python3.6

####    HERE IS A LIST OF WHAT WORKS IN THIS version    ###


#1. selects all rows in active projects
#2. creates folders and subfolders to the client\address + servce
#3. gets street view image 1 direction
#4. geocodes address, calcs elevation, gets geohash, calculates Lat and Long radians, calculates 4 points in BBox to a mile
#5. returns aerial and topo year list as json objects
#6. scrapes scrambled aerial photos and places in dir
#7. creates html file with aerials
#8. populates table prescreens with above parameters

####     80% Done                          #################

import mysql.connector
from mysql.connector import Error
import json
import requests
import mz2geohash
import math
import os
import sys
import google_streetview.api
import shutil
from docx import Document
from docx.shared import Inches

#from get_parcel import *
from get_histaerT import *

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  database="",
  password=""
)
if bool(mydb) != True:
    print("Database Connection not established to Pear!!")
else:
    print("Connected to Pear!")

####_____________________________________get existing data from projects and start

mycursor = mydb.cursor()

sql1 = "SELECT `project_id`, `project_address`, `project_city`, `project_state`, `project_zip`, `project_type`, `project_fee`, `client_id`, `client_name`, `client_contact` FROM `active_projects` ORDER BY `project_id` ASC LIMIT 5"

mycursor.execute(sql1)
projects = mycursor.fetchall()
counter = 0
for project in projects:
    counter += 1
    if counter == len(projects):
        break
    else:
        project_id = str(project[0])
        project_address = str(project[1])
        project_city = str(project[2])
        project_state = str(project[3])
        project_zip = str(project[4])
        project_type = str(project[5])
        project_fee = str(project[6])
        client_id = str(project[7])
        client_name = str(project[8])
        client_contact = str(project[9])
        full_address = project_address + str(", ") + project_city + str(", ") + project_state + str(", ") + project_zip

        folder_name = "/home/rob/public_html/pear/active_projects/" + client_name + "/" + full_address + " " + project_type
        #datasheet_file_path = folder_name + "/data-sheet.txt"

        photos_folder_name = "Photos"
        photos_folder_path = folder_name + "/" + photos_folder_name
            
        if(not os.path.exists(photos_folder_path)):
            os.makedirs(photos_folder_path)

        appendices_folder_name = "Appendices"
        appendices_folder_path = folder_name + "/" + appendices_folder_name
        appendices_source_path = "/home/rob/public_html/pear/pdf_files"

        if(not os.path.exists(appendices_folder_path)):
            os.makedirs(appendices_folder_path) 

        # get a list of all the files in source folder
        source_file_names = os.listdir(appendices_source_path)

        # Process each file object in the directory
        for source_file_name in source_file_names:

            try:

                # get the files name with it's full path
                source_file_path = os.path.join(appendices_source_path, source_file_name)

                # If the object is a sub-directory(not a file), skip it
                if not os.path.isfile(source_file_path):
                    continue

                # Get the file extension
                file_date, file_ext = os.path.splitext(source_file_path)

                # only copy '.pdf' files
                if file_ext.lower() == '.pdf':
                    shutil.copy2(source_file_path, appendices_folder_path)

            # If source and destination are same
            except shutil.SameFileError:
                print("Source and destination represents the same file.")
                # If there is any permission issue

            except PermissionError:
                print("Permission denied.")
                # For other errors

            except:
                print("Error occurred while copying file.")

###__________                     GET PARCEL            _______________################


####_____________________GET GEOFEATURES______________####################
        
        #geocode full_address
        geocodeQuery = str("http://www.service.com/geocode/lookup.json?q=") + str(full_address)
        rGeo = requests.get(geocodeQuery)

        geoData = rGeo.json()
        if geoData['features'] == []:
            print("error with geocoding.  Check address parameters!!")
        else:
            longitude = geoData['features'][0]['geometry']['coordinates'][0]
            latitude = geoData['features'][0]['geometry']['coordinates'][1]
#_______________________________________________________________________________________________________________get geohash

            ##Returns Geohash to the 12 value, not uesful for real estate..
            geohash12 = mz2geohash.encode((longitude,latitude))

            ##10 hash values is also too precise for real estate...but store this value for primary key usage and referencing other properties.
            geohash = geohash12[0:10:1]
#_______________________________________________________________________________________________________________get hist_aers

            get_histaerT(mydb,folder_name,latitude,longitude,geohash)
#________________________________________________________________________GET STREETVIEW IMAGERY

            headings = [0, 45, 90, 120, 180, 220, 280, 320, 360]

            for h in headings:

                coordinates = str(latitude) + ", " + str(longitude)
                size = str("640x640")
                location = coordinates
                heading = str(h)
                pitch = str("0")
                key = "AIzaSyAr-_5Tpb6djHIA1CL-VqttcGQBqxaQ0Mk"
                
                print(size, location, heading, pitch)
                
                google_data = [{'size':size, 'location':location, 'heading':heading, 'pitch':pitch, 'key':key}]

                results = google_streetview.api.results(google_data)
                
                # print(results.links)

                results.download_links(folder_name + "/" + "StreetView" + "/" + heading )

            print("StreetView in the project folder: " + str(folder_name) + "/" + "StreetView" + "/" + heading)

##try to get all GSV into 1 folder

            #GSVimg_folder_name = "Google StreetViews"
            #GSVimg_folder_path = folder_name + "/" + GSimg_folder_name
            #GSVimg_source_path = "/home/rob/public_html/pear/" + folder_name + "/" + "StreetView/"

            #creat folder path if not already exist____
            #if(not os.path.exists(GSVimg_folder_path)):
                #os.makedirs(GSVimg_folder_path)

            # get a list of all the files in source folder
           # GSV_file_names = os.listdir(appendices_source_path)

            # Process each file object in the directory
           # for source_file_name in source_file_names:

             #   try:
                    # get the files name with it's full path
                    #source_file_path = os.path.join(appendices_source_path, source_file_name)

#___________________________________________________________________________________________________________try elevation

            ##Use Google Maps API to Get Elevation
            elevationQuery = str("https://maps.googleapis.com/maps/api/elevation/json?locations=" + str(latitude) + "," + str(longitude) + "&key=Google Key")

            rElev = requests.get(elevationQuery)
            elevData = rElev.json()

            if elevData['results'] == []:
                Print("error with elevation!")

            else:
                elevation = str(elevData['results'][0]['elevation'])

####___________________________________________________________________________________________________TRIG FUNCTIONS

            LatRad = math.radians(latitude) #RETURNS RADIANS
            LongRad = math.radians(longitude) #RETURNS RADIANS
                    
            distance = 1 #in miles...NOTE: the higher value will scale out returned aerials or images, so will need to consider how to manage
            R = 3958.8 #Earth's radius in miles

            rAngular = distance/R #the angular radius of the query circle.

            #calculate lat/long mins for bounding box

            LatMinRad = LatRad - rAngular
            LatMaxRad = LatRad + rAngular
            Haver_bbox_lat_min = float(math.degrees(LatMinRad))
            Haver_bbox_lat_max = float(math.degrees(LatMaxRad))

####_______calculate the change in Longitude using known point's latitude and earth's angular distance___________####

            deltaLong = rAngular*math.sin(LatRad)/90

            LongMin = LongRad - deltaLong
            LongMax = LongRad + deltaLong
            Haver_bbox_lon_min = float(math.degrees(LongMin))
            Haver_bbox_lon_max = float(math.degrees(LongMax))

###____GET PARCEL

            #get_parcel(mydb,project_address,project_zip,latitude,longitude,geohash)
#_______________________________________________________________________________________________________EXIT TABLE UPDATE

            mycursor3 = mydb.cursor()  
                                
            sql3 = "INSERT IGNORE INTO `prescreens` (`client_id`, `client_name`, `client_contact`, `project_address`, `project_city`, `project_state`, `project_zip`, `full_address`, `latitude`, `longitude`, `elevation`, `geohash`, `LatRad`, `LongRad`, `Haver_bbox_lat_min`, `Haver_bbox_lat_max`, `Haver_bbox_lon_min`, `Haver_bbox_lon_max`) VALUES (%(client_id)s, %(client_name)s, %(client_contact)s, %(project_address)s, %(project_city)s, %(project_state)s, %(project_zip)s, %(full_address)s, %(latitude)s, %(longitude)s, %(elevation)s, %(geohash)s, %(LatRad)s, %(LongRad)s, %(Haver_bbox_lat_min)s, %(Haver_bbox_lat_max)s, %(Haver_bbox_lon_min)s, %(Haver_bbox_lon_max)s)"
                
            mycursor3.execute(sql3, { 'client_id': client_id, 'client_name': client_name, 'client_contact': client_contact, 'project_address': project_address, 'project_city': project_city, 'project_state': project_state, 'project_zip': project_zip, 'full_address': full_address, 'latitude': latitude, 'longitude': longitude, 'elevation': elevation, 'geohash': geohash, 'LatRad': LatRad, 'LongRad': LongRad, 'Haver_bbox_lat_min': Haver_bbox_lat_min, 'Haver_bbox_lat_max': Haver_bbox_lat_max, 'Haver_bbox_lon_min': Haver_bbox_lon_min, 'Haver_bbox_lon_max': Haver_bbox_lon_max})
            
            mycursor3.close()

    print("<li>" + full_address + "</li>")

mydb.commit()

mycursor.close()
mydb.close()