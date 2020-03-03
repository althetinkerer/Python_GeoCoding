#!/usr/bin/python3.6

import mysql.connector
from mysql.connector import Error
import datetime
import json
import requests
import mz2geohash
import math
import os
import sys
import google_streetview.api
import shutil

from flask import Flask, render_template, redirect, jsonify, request, make_response, url_for, escape, Response
from flask_json import FlaskJSON, JsonError, json_response, as_json
from datetime import datetime

#db
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields, ValidationError, pre_load

#_______________________________________WTFORMS
from wtforms import Form, TextField, TextAreaField, StringField, SubmitField


DEBUG = True
SalemApp = Flask(__name__)
db = SQLAlchemy(SalemApp)
FlaskJSON(SalemApp)

SalemApp.config.from_object(__name__)
SalemApp.config["SECRET_KEY"] = ""
SalemApp.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
SalemApp.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:@localhost/db"


##### Model #####

class Project(db.Model):
    __tablename__ = 'projects'
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.Text)
    type = db.Column(db.String(100))
    max_deadline = db.Column(db.DateTime, default=datetime.now)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'),
        nullable=False)
    # client = db.relationship('Client', cascade = "all,delete", backref = "children")
    # client = db.relationship('Client', back_populates='projects')

class Client(db.Model):
    __tablename__ = 'clients'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    contact = db.Column(db.String(100))

    projects = db.relationship('Project', uselist=False, backref='client')

##### SCHEMAS #####

class ClientSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()
    contact = fields.Str()
    
class ProjectSchema(Schema):
    id = fields.Int(dump_only=True)
    address = fields.Str()
    type = fields.Str()
    client_id = fields.Int()
    max_deadline = fields.Date()
    client = fields.Nested(ClientSchema)

project_schema = ProjectSchema()
projects_schema = ProjectSchema(many=True)

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="" 
)

if bool(mydb) != True:
    print("Database Connection not established to Pear!!")
else:
    print("Connected to Pear!")

mycursor = mydb.cursor()

#_______________________sets default start
@SalemApp.route("/")
def index():
    return render_template('index.html', index=index)

###____________________________________________________________________________PEarForm
@SalemApp.route("/PearForm")
def PearForm():

    full_address = ""

    project_address = form.get('prpject_address')
    project_city = form.get('project_city')
    project_state = form.get('project_state')
    project_zip = form.get('project_zipcode')

    full_address = project_address + str(", ") + project_city + str(", ") + project_state + str(", ") + project_zip

    return render_template("PearForm.html", project_address=project_address, project_city=project_city, project_state=project_state, project_zipcode=project_zipcode, full_address=full_address, form=get.form, PearForm=PearForm)

####_____________________________________get existing data from projects and start
@SalemApp.route("/projects")
def SalemProjects():
    #---------If user is not logged in, go back to login-------
    # if session.get('user') is None:
    #     return redirect(url_for('login'))
    
    # ProjectsQuery = "SELECT * FROM `projects` ORDER BY `id` ASC"
    # mycursor.execute(ProjectsQuery)
    # projects = mycursor.fetchall()
    #for project in projects:
        #return project
    
    # mycursor.close() : mycursor and mydb should be closed at this moment because Inside projects.html template it will iterate the values.
    # mydb.close(): And there was a syntax error inside projects.html like {% start of block %}, {% end of block %}, and missing of '{% endif %}'

    return render_template('projects.html')
            #mycursor3 = mydb.cursor()  
                                
           # sql3 = "INSERT INTO `prescreens` (`client_id`, `client_name`, `client_contact`, `project_address`, `project_city`, `project_state`, `project_zip`, `full_address`, `latitude`, `longitude`, `elevation`, `geohash`, `LatRad`, `LongRad`, `Haver_bbox_lat_min`, `Haver_bbox_lat_max`, `Haver_bbox_lon_min`, `Haver_bbox_lon_max`) VALUES (%(client_id)s, %(client_name)s, %(client_contact)s, %(project_address)s, %(project_city)s, %(project_state)s, %(project_zip)s, %(full_address)s, %(latitude)s, %(longitude)s, %(elevation)s, %(geohash)s, %(LatRad)s, %(LongRad)s, %(Haver_bbox_lat_min)s, %(Haver_bbox_lat_max)s, %(Haver_bbox_lon_min)s, %(Haver_bbox_lon_max)s)"
                
            #mycursor3.execute(sql3, { 'client_id': client_id, 'client_name': client_name, 'client_contact': client_contact, 'project_address': project_address, 'project_city': project_city, 'project_state': project_state, 'project_zip': project_zip, 'full_address': full_address, 'latitude': latitude, 'longitude': longitude, 'elevation': elevation, 'geohash': geohash, 'LatRad': LatRad, 'LongRad': LongRad, 'Haver_bbox_lat_min': Haver_bbox_lat_min, 'Haver_bbox_lat_max': Haver_bbox_lat_max, 'Haver_bbox_lon_min': Haver_bbox_lon_min, 'Haver_bbox_lon_max': Haver_bbox_lon_max})
            
            #mycursor3.close()
    

@SalemApp.route("/api/projects", methods=['GET'])
def getProjects():
    #---------If user is not logged in, go back to login-------
    # if session.get('user') is None:
    #     return redirect(url_for('login'))
    p_id = request.args.get('id')
    p_address = request.args.get('address')
    p_type = request.args.get('type')
    c_name = request.args.get('client[name]')
    c_contact = request.args.get('client[contact]')
    p_deadline = request.args.get('max_deadline')
    
    if not p_id:
        p_id=""
    if not p_address:
        p_address=""
    if not p_type:
        p_type=""
    if not c_name:
        c_name=""
    if not c_contact:
        c_contact=""
    if not p_deadline:
        p_deadline=""
    
   
    id_search = "%{}%".format(p_id)
    address_search = "%{}%".format(p_address)
    type_search = "%{}%".format(p_type)
    cname_search = "%{}%".format(c_name)
    ccontact_search = "%{}%".format(c_contact)
    deadline_search = "%{}%".format(p_deadline)

    projects = Project.query.filter(
        Project.id.like(id_search),
        Project.address.like(address_search),
        Project.type.like(type_search),
        Project.max_deadline.like(deadline_search),
        Client.name.like(cname_search),
        Client.contact.like(ccontact_search)
        ).join(Client).order_by(Project.id.asc())
    
    result = projects_schema.dump(projects)
    return  {"result": result}
    

#Update Project Info From Grid
@SalemApp.route("/api/projects/<int:id>", methods=['PUT'])
def updateProject(id):
    
    p_address = request.form.get('address')
    p_type = request.form.get('type')
    
    project = Project.query.get(id)
    project.type = p_type
    project.address = p_address
    db.session.commit()
    result = project_schema.dump(project)
    return  {"result": result}

#Remove Project From Grid
@SalemApp.route("/api/projects/<int:id>", methods=['DELETE'])
def deleteProject(id):
    
    project = Project.query.get(id)

    db.session.delete(project)
    db.session.commit()
    
    return  {"result": "success"}


if __name__ == "__main__":
    SalemApp.run(host="127.0.0.1", port=8000, debug=True)