# import python modules 
import requests
import datetime
import urllib3
import json
import mariadb
import re
import logging
import sys
import os
import config
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# Configure Logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.DEBUG,
    handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler()
    ],
    encoding="utf-8",
    format="{asctime} - {levelname} - {message}",
    style="{",
    datefmt="%Y-%m-%d %H:%M",
)



# Establish database connection
try:
    connection= mariadb.connect(
        user=config.db_user,
        password=config.db_password,
        host=config.db_host,
        database=config.database
    )
    cursor= connection.cursor()
except mariadb.Error as e:
    logger.critical(f"Can't connect to database server: {e}")
    sys.exit()

# NetBrain Login script

body = {
    "username" : config.nb_user,      
    "password" : config.nb_password 
}

nb_url = config.nb_url         

# Set proper headers
headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}    
login_url = "/ServicesAPI/API/V1/Session"

def add_data(timestamp, device, interface, intf_status):
    # Add result to database function
    try:
        statement = """INSERT INTO status(timestamp, device, interface, status) VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE timestamp=%s, status=%s"""
        data = (timestamp, device, interface, intf_status, timestamp, intf_status)
        cursor.execute(statement, data)
        connection.commit()
        logger.info(f"Successfully added entry to database {timestamp} | {device} | {interface} | {intf_status}")
    except mariadb.Error as e:
        logger.error(f"Error adding entry to database {timestamp} | {device} | {interface} | Error Message: {e}")


# Login to NetBrain and get token
try:
    # Do the HTTP request
    response = requests.post(nb_url + login_url, headers=headers, data = json.dumps(body), verify=False)
    # Check for HTTP codes other than 200
    if response.status_code == 200:
        # Decode the JSON response into a dictionary and use the data
        js = response.json()
        # Put token into variable to use later
        token = js['token']
        headers["Token"] = token
    else:
        logger.error("Get token failed! - " + str(response.text))
except Exception as e:
    logger.error(f"Get token failed! - {e}")


# Set Tenant and Domain
set_domain_url = "/ServicesAPI/API/V1/Session/CurrentDomain"

body = {
    "domainId": config.domainID,
    "tenantId": config.tenantID
}

try:
    # Do the HTTP request
    response = requests.put(nb_url + set_domain_url, data=json.dumps(body), headers=headers, verify=False)
    # Check for HTTP codes other than 200
    if response.status_code == 200:
        # Decode the JSON response into a dictionary and use the data
        result = response.json()
        logger.info("Set domain and tenant successful")
    elif response.status_code != 200:
        logger.error("Set Tenant Failed - " + str(response.text))

except Exception as e: 
    logger.error(str(e))



# Get ADT Results
adt_url = "/ServicesAPI/API/V3/TAF/Lite/adt/data"

payload = {
    "endpoint": config.taf_endpoint,
    "passkey": config.taf_passkey
}


try:
    # Do the HTTP request
    response = requests.post(nb_url + adt_url, data=json.dumps(payload), headers=headers, verify=False)
    # Check for HTTP codes other than 200
    if response.status_code == 200:
        # Decode the JSON response into a dictionary and use the data
        result = response.json()
        logger.info("Get ADT data successful")

    elif response.status_code != 200:
        logger.warning("Get ADT data failed - " + str(response.text))

except Exception as e: 
    logger.error(str(e))

# Local Compliance results for testing/debugging
compliance_results = []

# Loop through ADT table row by row
for row in result["rows"]:
    devicename = row[0]["value"]
    interface = row[2]["value"]
    intf_status = row[3]["value"]
    timestamp = datetime.datetime.now()

    logger.debug(f"Device: {devicename} | Interface: {interface} | Status: {intf_status}")
    add_data(timestamp.strftime("%Y-%m-%d %H:%M:%S"), devicename, interface, intf_status)


# Close Database connection
cursor.close()
connection.close()
logger.info("Run complete")