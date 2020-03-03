#!/usr/bin/python3.6
import mysql.connector
from mysql.connector import Error



###__________________________________________set pear db connection

# Pear_db = mysql.connector.connect(
#   host="localhost",
#   user="root",
#   database="",
#   password=""
# )
# if bool(Pear_db) != True:
#     print("Database Connection not established to Pear!!")
# else:
#     print("Connected to Pear!")

# PearCursor = Pear_db.cursor()

def pear_Parcel(PearCursor, property_address, geohash, latitude, longitude):

    project_address = "429 Elmwood Avenue"
    county = "Hunterdon"
    project_state = "NJ"
    project_zip = str("07040")
    geohash = "dr5ptzcgm3"
    PearScore = 0
    print("hi, PearGet_parcel")
    parcels = []
    if project_state == "NJ":

        pear_ParcelSQL1 = "SELECT * FROM njParcels WHERE GEOHASH = '" + geohash + "'"

        PearCursor.execute(pear_ParcelSQL1, {'GEOHASH':geohash})

        parcels = PearCursor.fetchall()
        if bool(parcels) == True:
            print("There is data!")

        for parcel in parcels:
            
            #print(parcel[0:])

            row_id = parcel[0]
            GIS_PIN = parcel[1]
            CD_CODE = parcel[2]
            BLOCK = parcel[3]
            LOT = parcel[4]
            QUALIFIER = parcel[5]
            PROP_CLASS = parcel[6]
            PROP_LOC = parcel[7]
            MUN_NAME = parcel[8]
            COUNTY = parcel[9]
            PROP_ZIP = parcel[10]
            OWNER_NAME = parcel[11]
            BLDG_DESC = parcel[12]
            LAND_DESC = parcel[13]
            CALC_ACRE = parcel[14]
            ADD_LOTS1 = parcel[15]
            ADD_LOTS2 = parcel[16]
            FAC_NAME = parcel[17]
            PROP_USE = parcel[18]
            BLDG_CLASS = parcel[19]
            DEED_DATE = parcel[20]
            YR_CONSTR = parcel[21]
            SALE_PRICE = parcel[22]
            DWELL = parcel[23]
            COMM_DWELL = parcel[24]
            LATITUDE = parcel[25]
            LONGITUDE = parcel[26]
            GEOHASH = parcel[27]
            Property_Sale_Records = parcel[28]

            print(parcel[0],parcel[1],parcel[2],parcel[3],parcel[4],parcel[5],parcel[6],parcel[7],parcel[8],parcel[9],parcel[10],parcel[11],parcel[12],parcel[13],parcel[14],parcel[15],parcel[16],parcel[17],parcel[18],parcel[19],parcel[20],parcel[21],parcel[22],parcel[23],parcel[24],parcel[25],parcel[26],parcel[27],parcel[28])

            if PROP_CLASS == str("4B"): # industrial, could include warehouses, reduces score
                PearScore += 75

            ##NOTE TO SELF: NEED TO ACCOUNT FOR YEAR BUILT VALUE, OTHER RETURNS HERE 

            elif PROP_CLASS == str("6B"): #petroleum refineries and high 
                PearScore += 100

            elif PROP_CLASS == str("4A"): #commercial - generic - many possible env usages
                PearScore += 60

            elif PROP_CLASS[0] == str("3"): #farm land
                PearScore += 30

            elif PROP_CLASS == str("1"): #vacant land
                PearScore += 25

            else:
                PearScore += 1

            #print("no match for " + project_address + " in " + project_zip + "\n")
            #print("the PEAR Score cannot be calculated with this module")


    if project_state == "NY":
        print("In time...")

    print(PearScore)
    # PearCursor.close()

    return parcels
#print(block,lot,property_ownwer,property_county)
#return get_parcel, parcel
