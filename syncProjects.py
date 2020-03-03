#!/usr/bin/python3.6

#set to update every 30 minutes between 0600 - 1800 to assure new entries are included in Pear, Perm. etc...

import mysql.connector
from mysql.connector import Error
import os
import sys
import time
import datetime
from datetime import date, time, datetime, timedelta

##____________connect to production projects database

remoteProjects_db = mysql.connector.connect(
  host="localhost",
  user="root",
  database="",
  password=""
)

if bool(remoteProjects_db) != True:
	print("Database Connection not established to production db!!")
else:
	print("Connected to production projects!")

remoteCursor = remoteProjects_db.cursor()

###__________________________________________set Projects connection

Projects_db = mysql.connector.connect(
  host="localhost",
  user="root",
  database="projects",
  password=""
)
if bool(Projects_db) != True:
    print("Database Connection not established to Projects!!")
else:
    print("Connected to local projects!")

ProjectsCursor = Projects_db.cursor()
##_______________________________________________________get any new clients to sync to localhost

remoteQuery_C = "SELECT `client_id`, `client_name`, `client_contact`, `client_address`, `client_city`, `client_state`, `client_zip`, `client_email`, `client_phone` FROM `clients`"

remoteCursor.execute(remoteQuery_C)

remoteClients = remoteCursor.fetchall()

for client in remoteClients:
	client_id = client[0]
	client_name = client[1]
	client_contact = client[2]
	client_address = client[3]
	client_city = client[4]
	client_state = client[5]
	client_zip = client[6]
	client_email = client[7]
	client_phone = client[8]
	access_level = str("C")

	checkClient_id = "SELECT `client_id` FROM `clients`"

	ProjectsCursor.execute(checkClient_id)

	checkClient_rtr = ProjectsCursor.fetchall()
	
	if client_id not in checkClient_rtr:
		client_id = client_id + 1

	lastUser_sql = "SELECT `user_id` FROM `clients` ORDER BY `user_id` DESC LIMIT 1"

	ProjectsCursor.execute(lastUser_sql)

	lastUser_rtr = ProjectsCursor.fetchall()

	for z in lastUser_rtr:
		lastUser_id = int(z[0])
		print(lastUser_id)
		
	user_id = lastUser_id + 1 #sets next user_id from last id present

	updateClient_sql = "INSERT IGNORE INTO `clients` (`user_id`, `client_name`, `client_contact`, `client_address`, `client_city`, `client_state`, `client_zip`, `client_email`, `client_phone`, `client_id`, `access_level`) VALUES (%(client_id)s, %(client_name)s, %(client_contact)s, %(client_address)s, %(client_city)s, %(client_state)s, %(client_zip)s, %(client_email)s, %(client_phone)s, %(client_id)s, %(access_level)s)"

	ProjectsCursor.execute(updateClient_sql, {'user_id': user_id,  'client_name': client_name, 'client_contact': client_contact, 'client_address': client_address, 'client_city': client_city, 'client_state': client_state, 'client_zip': client_zip, 'client_email': client_email, 'client_phone': client_phone, 'client_id': client_id, 'access_level':access_level})

	lastUser_now = ProjectsCursor.lastrowid

	if lastUser_id == lastUser_now:
		print("No new rows were added")

	else:
		update_str_C = str(lastUser_now) + str("a row was added to clients table for ") + client_name + str(", ") + client_contact

		print(update_str_C)

		date_obj = datetime.now()
		date_stamp = date_obj.strftime("%B %d, %Y - %H:%M:%Z")
		line = "Updated at " + date_stamp + "by syncProjects\n\n" + update_str_C
		projectsLog = open("/home/rob/public_html/pear/remote_table_updates.txt", "a+")
		projectsLog.write(line)

#_____________________________SYNC LOCAL PROJECTS FROM LIVE___###

remoteQuery_P = "SELECT `project_id`, `project_address`, `project_city`, `project_state`, `project_zip`, `project_property_usage`, `project_type`, `property_details`, `interior_inspection`, `interior_contact_name`, `interior_contact_phone`, `interior_contact_email`, `project_invoice`, `project_fee`, `start_date`, `end_date`, `project_min_time`, `project_max_time`, `project_max_deadline`, `project_status`, `project_current_task`, `staff_id`, `client_id`, `staff_notifications`, `created`, `updated` FROM `projects`"

remoteCursor.execute(remoteQuery_P)

remoteProjects = remoteCursor.fetchall()

for project in remoteProjects:
	project_id = project[0]
	project_address = project[1]
	project_city = project[2]
	project_state = project[3]
	project_zip = project[4]
	project_property_usage = project[5]
	project_type = project[6]
	property_details = project[7]
	interior_inspection = project[8]
	interior_contact_name = project[9]
	interior_contact_phone = project[10]
	interior_contact_email = project[11]
	project_invoice = project[12]
	project_fee = project[13]
	start_date = project[14]
	end_date = project[15]
	project_min_time = project[16]
	project_max_time = project[17]
	project_max_deadline = project[18]
	project_status = project[19]
	project_current_task = project[20]
	staff_id = project[21]
	client_id = project[22]
	staff_notifications = project[23]
	created = project[24]
	updated = project[25]

	lastProject_sql = "SELECT `project_id` FROM `projects` ORDER BY `project_id` DESC LIMIT 1"

	ProjectsCursor.execute(lastProject_sql)

	lastProject_rtr = ProjectsCursor.fetchall()

	for z in lastProject_rtr:
		lastProject_id = int(z[0])

	project_id = lastProject_id + 1

	updateProject_sql = "INSERT IGNORE INTO `projects` (`project_id`, `project_address`, `project_city`, `project_state`, `project_zip`, `project_property_usage`, `project_type`, `property_details`, `interior_inspection`, `interior_contact_name`, `interior_contact_phone`, `interior_contact_email`, `project_invoice`, `project_fee`, `start_date`, `end_date`, `project_min_time`, `project_max_time`, `project_max_deadline`, `project_status`, `project_current_task`, `staff_id`, `client_id`, `staff_notifications`, `created`, `updated`) VALUES (%(project_id)s, %(project_address)s, %(project_city)s, %(project_state)s, %(project_zip)s, %(project_property_usage)s, %(project_type)s, %(property_details)s, %(interior_inspection)s, %(interior_contact_name)s, %(interior_contact_phone)s, %(interior_contact_email)s, %(project_invoice)s, %(project_fee)s, %(start_date)s, %(end_date)s, %(project_min_time)s, %(project_max_time)s, %(project_max_deadline)s, %(project_status)s, %(project_current_task)s, %(staff_id)s, %(client_id)s, %(staff_notifications)s, %(created)s, %(updated)s)"

	ProjectsCursor.execute(updateProject_sql, {'project_id': project_id, 'project_address': project_address, 'project_city': project_city, 'project_state': project_state, 'project_zip': project_zip, 'project_property_usage': project_property_usage, 'project_type': project_type, 'property_details': property_details, 'interior_inspection': interior_inspection, 'interior_contact_name': interior_contact_name, 'interior_contact_phone': interior_contact_phone, 'interior_contact_email': interior_contact_email, 'project_invoice': project_invoice, 'project_fee': project_fee, 'start_date': start_date, 'end_date': end_date, 'project_min_time': project_min_time, 'project_max_time': project_max_time, 'project_max_deadline': project_max_deadline, 'project_status': project_status, 'project_current_task': project_current_task, 'staff_id': staff_id, 'client_id': client_id, 'staff_notifications': staff_notifications, 'created': created, 'updated':updated})

	lastProject_now = ProjectsCursor.lastrowid

	if lastProject_id == lastProject_now:
		print("No new rows were added")

	else:
		update_str_P = str(lastUser_now) + "a row was added for to clients table for " + client_name + ", " + client_contact

		print(update_str_P)

		date_obj = datetime.now()
		date_stamp = date_obj.strftime("%B %d, %Y - %H:%M:%Z")
		line = "Updated at " + date_stamp + "per Python syncProjects\n\n" + update_str_P
		projectsLog.write(line)

	Projects_db.commit()

projectsLog.close()
ProjectsCursor.close()
Projects_db.close()
remoteCursor.close()
remoteProjects_db.close()