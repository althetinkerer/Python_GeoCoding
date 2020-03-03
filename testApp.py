#!/usr/bin/python3.6

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
import hashlib, binascii
from random import choice
from string import ascii_uppercase

#import PearSearch Python file
import pearSearch

from flask import Flask, render_template, redirect, jsonify, session, request, make_response, url_for, escape, Response
from flask_json import FlaskJSON, JsonError, json_response, as_json


DEBUG = True
testApp = Flask(__name__)
FlaskJSON(testApp)
testApp.config.from_object(__name__)
testApp.config["SECRET_KEY"] = "Goldghostgravy0001"

john = "richard"
#print(john)

###__________________________________________set pear db connection
Pear_db = mysql.connector.connect(
  host="localhost",
  user="root",
  database="",
  password=""
)
if bool(Pear_db) != True:
    print("Database Connection not established to Pear!!")
else:
    print("Connected to Pear!")

PearCursor = Pear_db.cursor()

###__________________________________________set admin db connection

SalemAdmin_db = mysql.connector.connect(
  host="localhost",
  user="root",
  database="",
  password=""
)
if bool(SalemAdmin_db) != True:
    print("Database Connection not established to ADMIN!")
else:
    print("Connected to Admin!")

AdminCursor = SalemAdmin_db.cursor()

###__________________________________________set Projects connection

# Projects_db = mysql.connector.connect(
#   host="localhost",
#   user="root",
#   database="",
#   password=""
# )
# if bool(Projects_db) != True:
#     print("Database Connection not established to Projects!!")
# else:
#     print("Connected to local projects!")

# ProjectsCursor = Projects_db.cursor()

#_______________________________________________define dashboard data sums here

def SumFunctions():
    AdminCursor = SalemAdmin_db.cursor()
    sumSQL = "SELECT SUM(`invoice_amount`) FROM invoices"
    AdminCursor.execute(sumSQL)
    summary = AdminCursor.fetchone()
    for sum in summary:
        i = int(round(sum))
        return i
    return i


#SumFunctions() #IMPORTANT, MUST CALL FUNCTION WITH () SYMBOL IN JINJA TEMPLATE VIEW, calling here just displays value in terminal window locally

#@testApp.route("/client_dashboard/<user>")
#def client_dashboard(client_name):
 #   PearCursor = Pear_db.cursor()
  #  cp_SQL = "SELECT * FROM active_projects WHERE `client_name` = %(client_name)s ORDER BY `project_no` ASC"
#    PearCursor.execute(cp_SQL, {'client_name':client_name})
 #   client_projects = PearCursor.fetchall()

  #  return render_template("client_dashboard.html", client_name=client_name) #projects=projects)
    
   # PearCursor.close()
    #AdminCursor.close()

def hash_password(password):
    #-------Hash a password for storing.
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), 
                                salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    return (salt + pwdhash).decode('ascii')
 
def verify_password(stored_password, provided_password):
    #-------Verify a stored password against one provided by user"""
    salt = stored_password[:64]
    stored_password = stored_password[64:]
    pwdhash = hashlib.pbkdf2_hmac('sha512', 
                                  provided_password.encode('utf-8'), 
                                  salt.encode('ascii'), 
                                  100000)
    pwdhash = binascii.hexlify(pwdhash).decode('ascii')
    return pwdhash == stored_password

#_______________________sets default start
@testApp.route("/")
def index():
    #---------If user is not logged in, go back to login, if Yes => go back to Proper Page-------
    if session.get('user'):
        user = session.get('user')
        if (user[11] == 'A'):
            return redirect(url_for('SalemHub'))
        elif (user[11] == 'C'):
            return redirect(url_for('ClientHub'))
        else:                
            return redirect(url_for('StaffPage')) ## new route for Staff         
    else:
        return redirect(url_for('login'))

####________Login______
@testApp.route("/login")
def login():
    #---------If user is already logged in, go back to Proper Page-------
    if session.get('user'):
        user = session.get('user')
        if (user[11] == 'A'):
            return redirect(url_for('SalemHub'))
        elif (user[11] == 'C'):
            return redirect(url_for('ClientHub'))
        else:
            return redirect(url_for('StaffPage')) ## new route for Staff   

    else:
        return render_template('login.html')

####________Add New User: available only under Admin______
@testApp.route("/add_user_form")
def addUserForm():
     #---------Only pass if user is Admin-------
    if session.get('user') is None:
        return redirect(url_for('login'))
    user = session.get('user')    

    if user[11] != 'A':        
        return redirect(url_for('SalemHub'))
    else:
        return render_template('add_user_form.html')
        
#_______________________________logout?
@testApp.route("/logout")
def logout():
     #---------If user is already logged in, go back to index-------
    if session.get('user'):
        session.pop('user')
    return redirect(url_for('SalemHub')) 

####________Login Check______

@testApp.route("/login_check", methods=['POST'])
def loginCheck():
    #---------If user is already logged in, go back to index-------
    if session.get('user'):
        return redirect(url_for('SalemHub')) 
    else:
        #----Login Check Code and Update Session Variable
        #--Prepare another connection since the User data is stored in projects database

        email = request.form['email'] # for POST form method
        password = request.form['password']
        
        print(email, password)
        
        authQuery = "SELECT * FROM `clients` where client_email='" + email +"' limit 1"
        AdminCursor.execute(authQuery)
        user = AdminCursor.fetchone()
   
        if user:
            print("DB=>", user[2])
            print("Formula=>", hash_password(password))
        
            if verify_password(user[2], password): 
                print("Successful User login!")  
                #--- Update Session Variable ####
                session['user'] = user
                #--user[11] = access_level: A,S,C
                if (user[11] == 'A'):
                    return redirect(url_for('SalemHub'))
                elif (user[11] == 'C'):
                    return redirect(url_for('ClientHub'))
                else:
                    return redirect(url_for('StaffPage')) ## new route for Staff
                ##would need to add routes here for users with A, S, C access_level from clients_table...if, elif, else?

            else:
                print("Login Failed:")
                return redirect(url_for('login'))
        print("Login Failed:")
        return redirect(url_for('login'))

####________Add User From New User Page with email and password______
@testApp.route("/add_user", methods=['POST'])
def addUser():
     #---------Only proceed if user is Admin-------
    if session.get('user') is None:
        return redirect(url_for('login'))
    user = session.get('user')    

    if user[11] != 'A':        
        return redirect(url_for('SalemHub'))
  
    #----Login Check Code and Update Session Variable
    #--Prepare another connection since the User data is stored in projects database

    email = request.form['email'] # for POST form method
    password = request.form['password']
    
    print(email, password)
    
    # Insert Query into Clients
    addQuery = "INSERT INTO `clients` (client_email, password, client_id, access_level)"
    addQuery += " VALUES ('" + email +"', '" + hash_password(password) + "', 500, 'C')"
    
    print(addQuery)
    # It is better to put under Try/Catch statement
    try:
        AdminCursor.execute(addQuery)
        AdminCursor.commit()

        # Check Result
        print(AdminCursor.rowcount, "Record inserted successfully into Clients table")
        # ProjectsCursor.close()

    except mysql.connector.Error as error:
        print("Failed to insert record into Clients table {}".format(error))
        return render_template('add_user_form.html', error= "Failed to insert record into Clients table")
    finally:
        return redirect(url_for('SalemHub'))
        
@testApp.route("/SalemHub")
def SalemHub():
    #---------If user is not logged in, go back to login-------
    if session.get('user') is None:
        return redirect(url_for('login'))

    else:
        user = session.get('user')
        if (user[11] != 'A'):
            return render_template("403.html")  
            
        # ClientsSQL = "SELECT * FROM clients ORDER BY `client_name` DESC LIMIT 5"
        ClientsSQL = "SELECT * FROM clients ORDER BY `client_name`"
        AdminCursor.execute(ClientsSQL)
        clients = AdminCursor.fetchall()
        
        # AdminCursor = SalemAdmin_db.cursor()
        InvoicesSQL = "SELECT * FROM invoices ORDER BY `invoice_no` ASC"
        AdminCursor.execute(InvoicesSQL)
        invoices = AdminCursor.fetchall()
        
        PearCursor = Pear_db.cursor()
        prescreenSQL = "SELECT * FROM prescreens ORDER BY `prescreen_no` DESC"
        PearCursor.execute(prescreenSQL)
        prescreens = PearCursor.fetchall()
    
        SumFunctions()

        #update to PearForm.html
        return render_template("SalemHub.html", AdminCursor=AdminCursor, PearCursor=PearCursor, SumFunctions=SumFunctions, john=john, clients=clients, invoices=invoices) #projects=projects)
              
@testApp.route("/PearForm")
def PearForm():
    #---------If user is not logged in, go back to login-------
    if session.get('user') is None:
        return redirect(url_for('login'))

    else:
        user = session.get('user')
        if (user[11] != 'A'):
            return render_template("403.html")  

        # AdminCursor = SalemAdmin_db.cursor()    
        # ClientsSQL = "SELECT * FROM clients ORDER BY `client_name` DESC LIMIT 5"
        ClientsSQL = "SELECT * FROM clients ORDER BY `client_name`"
        AdminCursor.execute(ClientsSQL)
        clients = AdminCursor.fetchall()
                
        InvoicesSQL = "SELECT * FROM invoices ORDER BY `invoice_no` ASC"
        AdminCursor.execute(InvoicesSQL)
        invoices = AdminCursor.fetchall()
        
        PearCursor = Pear_db.cursor()
        prescreenSQL = "SELECT * FROM prescreens ORDER BY `prescreen_no` DESC"
        PearCursor.execute(prescreenSQL)
        prescreens = PearCursor.fetchall()
    
        SumFunctions()

        #update to PearForm.html
        return render_template("PearForm.html", AdminCursor=AdminCursor, PearCursor=PearCursor, SumFunctions=SumFunctions, john=john, clients=clients, invoices=invoices) #projects=projects)
              
@testApp.route("/ClientHub")
def ClientHub():
    #---------If user is not logged in, go back to login-------
    if session.get('user') is None:
        return redirect(url_for('login'))

    else:
        user = session.get('user')
        #Permission Check
        if (user[11] != 'A' and user[11] != 'C'):
            return render_template("403.html")  #dummy file  

        # ClientsSQL = "SELECT * FROM clients ORDER BY `client_name` DESC LIMIT 5"
        # ProjectsCursor.execute(ClientsSQL)
        # clients = ProjectsCursor.fetchall()
        
        # AdminCursor = SalemAdmin_db.cursor()
        # InvoicesSQL = "SELECT * FROM invoices ORDER BY `invoice_no` ASC"
        # AdminCursor.execute(InvoicesSQL)
        # invoices = AdminCursor.fetchall()
        
        # PearCursor = Pear_db.cursor()
        # prescreenSQL = "SELECT * FROM prescreens ORDER BY `prescreen_no` DESC"
        # PearCursor.execute(prescreenSQL)
        # prescreens = PearCursor.fetchall()
    
        # SumFunctions()
        
        return render_template("clientHub.html", user=user) #projects=projects)
        
        # ProjectsCursor.close()
        # AdminCursor.close()
        # PearCursor.close()
        
@testApp.route("/staff")
def StaffPage():
    #---------Before every action, check Session: User for proper action-------
    
    if session.get('user'):
        user = session.get('user')
        
        if (user[11] == 'S'):
            return render_template("staff.html")
        else:
            return render_template("403.html")                 
    else:
        return redirect(url_for('login')) 
        
@testApp.route("/projects")
def projects():
    #---------If user is not logged in, go back to login-------
    if session.get('user') is None:
        return redirect(url_for('login'))

    PearCursor = Pear_db.cursor()
    ProjectsSQL = "SELECT * FROM active_projects ORDER BY `project_no` ASC"
    PearCursor.execute(ProjectsSQL)
    projects = PearCursor.fetchall()
    #in view section put if session.user['admin'], then show {% block admin_count %} or some shit like that, if session.user['staff'], then show {% block staff_count %}
    
    return render_template("projects.html", SumFunctions=SumFunctions, john=john, projects=projects)
    
    PearCursor.close()

@testApp.route("/PearResults")
def PearResults():
    #---------If user is not logged in, go back to login-------
    if session.get('user') is None:
        return redirect(url_for('login'))

    results = pearSearch.main()
    print("results:", results)
    return render_template("PearResults_New.html", PearResults=results)
    
@testApp.route("/addFormData", methods=['POST'])
def addFormData():
    #---------If user is not logged in, go back to login-------
    if session.get('user') is None:
        return redirect(url_for('login'))

    else:
        user = session.get('user')
        if (user[11] != 'A'):
            return render_template("403.html")  

        #________Form Field_____________________________
        address = request.form['address'] 
        
        city = request.form['city']
        state = request.form['state']
        zipcode = request.form['zipcode']
        targetdb = request.form['targetdb']
        print("targetdb", targetdb)

        # AdminCursor = SalemAdmin_db.cursor()    
        # ClientsSQL = "SELECT * FROM clients ORDER BY `client_name` DESC LIMIT 5"

        #_____________Add Prescreens or active_projects
        # To be decided where to put
        # mycursor3 = mydb.cursor()
    
        #Dummy Client Info
        client_id = 1
        client_name = 'Salem Environmental LLC'  
        client_contact = 'Rob Heinze'  
        full_address =  '389 Dover Rd South, Toms River, NJ, 08757'
        latitude = 39.94027801791003
        longitude = -73.927879
        elevation = 17.1051559
        # geohash = "dr5ptzcgm3"
        geohash = ''.join(choice(ascii_uppercase) for i in range(12))
        LatRad = 0.7101978660
        LongRad = -1.2902848721
        Haver_bbox_lat_min = 40.676868
        Haver_bbox_lat_max = 40.705814
        Haver_bbox_lon_min = -73.927986
        Haver_bbox_lon_max = -73.927773
        project_no = 10678
        project_type = 'ESR'
        user_id=0

        if (targetdb == 'prescreens'):
                            
            sql3 = "INSERT INTO `prescreens` (`client_id`, `client_name`, `client_contact`, `project_address`,\
                `project_city`, `project_state`, `project_zip`, `full_address`, `latitude`, `longitude`, `elevation`,\
                `geohash`, `LatRad`, `LongRad`, `Haver_bbox_lat_min`, `Haver_bbox_lat_max`, `Haver_bbox_lon_min`,\
                `Haver_bbox_lon_max`)\
            VALUES (%(client_id)s, %(client_name)s, %(client_contact)s, %(project_address)s, %(project_city)s,\
                %(project_state)s, %(project_zip)s, %(full_address)s, %(latitude)s, %(longitude)s, %(elevation)s,\
                %(geohash)s, %(LatRad)s, %(LongRad)s, %(Haver_bbox_lat_min)s, %(Haver_bbox_lat_max)s,\
                %(Haver_bbox_lon_min)s, %(Haver_bbox_lon_max)s)"
                
            PearCursor.execute(sql3, { 'client_id': client_id, 'client_name': client_name, 'client_contact': client_contact,\
                'project_address': address, 'project_city': city, 'project_state': state, 'project_zip': zipcode,\
                'full_address': full_address, 'latitude': latitude, 'longitude': longitude, 'elevation': elevation,\
                'geohash': geohash, 'LatRad': LatRad, 'LongRad': LongRad, 'Haver_bbox_lat_min': Haver_bbox_lat_min,\
                'Haver_bbox_lat_max': Haver_bbox_lat_max, 'Haver_bbox_lon_min': Haver_bbox_lon_min, 'Haver_bbox_lon_max': Haver_bbox_lon_max})
            Pear_db.commit()

        elif (targetdb == 'active_projects'):
            sql3 = "INSERT INTO `active_projects` (`client_id`, `client_name`, `client_contact`, `project_address`,\
                `project_city`, `project_state`, `project_zip`, `project_type`, `user_id`)\
            VALUES (%(client_id)s, %(client_name)s, %(client_contact)s, %(project_address)s, %(project_city)s,\
                %(project_state)s, %(project_zip)s, %(project_type)s, %(user_id)s)"
                
            PearCursor.execute(sql3, {'client_id': client_id, 'client_name': client_name, 'client_contact': client_contact,\
                'project_address': address, 'project_city': city, 'project_state': state, 'project_zip': zipcode, 'project_type': project_type,\
                'user_id': user_id})
            Pear_db.commit()

        #redirect to PearResult
        return redirect(url_for('PearResults'))
    

####_____________________________________get existing data from projects and start

if __name__ == "__main__":
    testApp.run(host="127.0.0.1", port=5001, debug=True)