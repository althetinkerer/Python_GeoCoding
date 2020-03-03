#!/usr/bin/python3.6
#########                    MODULE TO BE CALLED SEPERATE, STABLE     #####
import requests
import math
import json
import sys
import os


def get_histaerT(mydb, folder_name, latitude, longitude, geohash):

    distance = 1 #in miles

    num_columns = 3 #columns in html table

    #distance = distance * 1.609344
    lat = math.radians(latitude)
    lon = math.radians(longitude)

    radius  = 3959
        # Radius of the parallel at given latitude
    parallel_radius = radius*math.cos(lat)

    lat_min = lat - distance/radius
    lat_max = lat + distance/radius
    lon_min = lon - distance/parallel_radius
    lon_max = lon + distance/parallel_radius
    rad2deg = math.degrees

    bbox_lat_min = rad2deg(lat_min)
    bbox_lon_min = rad2deg(lon_min)
    bbox_lat_max = rad2deg(lat_max)
    bbox_lon_max = rad2deg(lon_max)

    url = ("https://www.historicaerials.com/api/available_layers")
    parallel_bbox_points = {'n': bbox_lat_max, 's': bbox_lat_min,'e': bbox_lon_max,'w':bbox_lon_min}

    print(parallel_bbox_points)

    response = requests.post(url, data = parallel_bbox_points).json()

    years_list = []
    if 'aerials' in response:
        for x in response['aerials']:
            years_list.append(x[0])

    aerial_list = json.dumps(years_list)
    print(aerial_list)
    
    #assign aerial folder name
    AERimg_folder_name = "Historic Aerials"
    AERimg_folder_path = folder_name + "/" + AERimg_folder_name
    html_file_path = folder_name + "/aerial-display.html"

    #creat folder path if not already exist____
    if(not os.path.exists(AERimg_folder_path)):
        os.makedirs(AERimg_folder_path)

    html_tag_list = ["<table>"]
    curr_column = 0

    for year in years_list:

        year_s = str(year)
        AERimg_file_path = AERimg_folder_path + "/" + year_s + ".jpg"
            
        if(os.path.isfile(AERimg_file_path)):
            print("image from " + year_s + " exists, skipping")
        else:
            print("fetching image from " + year_s)
            
            #create url to fetch image from, plug in year and lat/long bounds into template
            
            url = "https://tiles.historicaerials.com?service=WMS&request=GetMap&layers=" + \
                year_s + \
                "-US-NT&styles=&format=image%2Fjpeg&transparent=false&version=1.1.1&width=640" + \
                "&height=640" + \
                "&srs=EPSG%3&bbox=" + \
                str(bbox_lon_min) + \
                "," + \
                str(bbox_lat_min) + \
                "," + \
                str(bbox_lon_max) + \
                "," + \
                str(bbox_lat_max)
                
            r = requests.get(url, stream=True)
            if r.status_code == 200:
                with open(AERimg_file_path, 'wb') as f:
                    for chunk in r.iter_content():
                        f.write(chunk)
            else:
                print(request.url)
                print(url)

        if(curr_column == 0):
            html_tag_list.append("<tr>")
        html_tag_list.append("<td>")
                
        html_tag_list.append("<h3>" + year_s + "</h3>")
        AERimg_file_path_for_html = AERimg_folder_name + "/" + year_s + ".jpg"
        html_tag_list.append("<img src=\"" + AERimg_file_path_for_html + "\">")
                
        html_tag_list.append("</td>")
        if(curr_column == num_columns - 1):
            html_tag_list.append("</tr>")
            curr_column = 0
        
        else:
            curr_column = curr_column + 1

    html_tag_list.append("</table>")

    print("generating html file")
    with open(html_file_path, 'w') as f:
        for tag in html_tag_list:
            f.write(tag + "\n")

##_____________________________________________________GET TOPOS

     ## get list of years of topo maps
    topo_years = []
                
    if 'topos' in response:
        for topo in response['topos']:
            topo_years.append(topo[0])
                        
    topo_list = json.dumps(topo_years)
    print(topo_list)

    #assign aerial folder name
    TOPOimg_folder_name = "Topographic Maps"
    TOPOimg_folder_path = folder_name + "/" + TOPOimg_folder_name
    html_file_pathT = folder_name + "/topo-display.html"

    #creat folder path if not already exist____
    if(not os.path.exists(TOPOimg_folder_path)):
        os.makedirs(TOPOimg_folder_path)

    html_tag_listT = ["<table>"]
    curr_columnT = 0
    
    #will be returned as response
    available_topo_years = []

    for year_t in topo_years:

        year = year_t[1:5:1]

        if year > str("2000"):            
            print("Topo from " + str(year) + "and has no value, skipped!")
            continue
            
        elif year < str("1972"):            
            print("Topo from " + str(year) + "and has no value, skipped!")
            continue
            
        else:
            year_ts = str(year)
            TOPOimg_file_path = TOPOimg_folder_path + "/" + year_ts + ".jpg"
                
            if(os.path.isfile(TOPOimg_file_path)):
                print("image from " + year_ts + " exists, skipping")                
            else:
                print("fetching image from " + year_ts)
                
                #create urlT to fetch image from, plug in year and lat/long bounds into template
                
                urlT = "https://tiles.historicaerials.com?service=WMS&request=GetMap&layers=T" + \
                    year_ts + \
                    "-US-NT&styles=&format=image%2Fjpeg&transparent=false&version=1.1.1&width=800" + \
                    "&height=800" + \
                    "&srs=EPSG%3A4326&bbox=" + \
                    str(bbox_lon_min) + \
                    "," + \
                    str(bbox_lat_min) + \
                    "," + \
                    str(bbox_lon_max) + \
                    "," + \
                    str(bbox_lat_max)
                    
                rTopo = requests.get(urlT, stream=True)
                if rTopo.status_code == 200:
                    with open(TOPOimg_file_path, 'wb') as f:
                        for chunk in rTopo.iter_content():
                            f.write(chunk)
                else:
                    print(request.urlT)
                    print(urlT)

            if(curr_columnT == 0):
                html_tag_listT.append("<tr>")
            html_tag_listT.append("<td>")
                    
            html_tag_listT.append("<h3>" + year_ts + "</h3>")
            TOPOimg_file_path_for_html = TOPOimg_folder_name + "/" + year_ts + ".jpg"
            html_tag_listT.append("<img src=\"" + TOPOimg_file_path_for_html + "\">")
                    
            html_tag_listT.append("</td>")
            available_topo_years.append(year) #add to image list
            if(curr_columnT == num_columns - 1):
                html_tag_listT.append("</tr>")
                curr_columnT = 0
            
            else:
                curr_columnT = curr_columnT + 1

        html_tag_listT.append("</table>")

        print("generating html file")
        with open(html_file_pathT, 'w') as f:
            for tag in html_tag_listT:
                f.write(tag + "\n")

    mycursor2 = mydb.cursor()  
                                
    sql2 = "UPDATE `prescreens` SET `aerial_list` = %(aerial_list)s, `topo_list` = %(topo_list)s WHERE geohash = %(geohash)s"
                
    mycursor2.execute(sql2, { 'aerial_list': aerial_list, 'topo_list': topo_list, 'geohash':geohash})
            
    mydb.commit()
    # mycursor2.close()
           
    return { 
        'aerial_list': years_list, 
        'topo_list': available_topo_years, 
        'geohash':geohash,
        'AERimg_folder': AERimg_folder_name,
        'TOPOimg_folder': TOPOimg_folder_name
    }

#######____rob-salem-note: 1-23-20 -A WAY TO DISPLAY THESE ON MAIN '/' index OF FLASK APP IS HUGE.  TILE DISPLAY SIMIALR TO THIS FUNCTION
