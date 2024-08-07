#!/usr/bin/python3
#
# Simple script to lookup my own IP using the Google checkip service and to compare this with the current domain setting
# in Cloudflare using the API. If the IP address has changed, update the DNS record.
# Script can be run periodically from cron.

import requests
import json
import argparse
import datetime

parser = argparse.ArgumentParser()
parser.add_argument("zone",help="Cloudflare zone to check or update")
parser.add_argument("token",help="API token to access the zone")
parser.add_argument("domain_name",help="Domain name to check and update")
args = parser.parse_args()

base_url = "https://api.cloudflare.com/client/v4/zones/" + args.zone
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer " + args.token
}

def find_record( name ):
    response = requests.get( url=base_url + "/dns_records", headers=headers )
    if response.status_code == 200:
        content = json.loads(response.content)
        if content["success"] == True:
            for record in content["result"]:
                if record["type"] == "A":
                    return (record["id"], { "name": record["name"], "content": record["content"], "type": record["type"] })

    return (None,None)

def update_dns_record( id, record ):
    response = requests.put( url=base_url + "/dns_records/" + id, headers=headers, data=json.dumps(record) )
    if response.status_code == 200:
        print(record["name"],"updated to",record["content"])

def find_myip():
    response = requests.get( url="https://api.ipify.org" )
    if response.status_code == 200:
        return response.content.decode('UTF-8')

myip = find_myip()

(id,record) = find_record( args.domain_name )

if id and record["content"] != myip:
    record["content"] = myip
    record["comment"] = "Updated " + datetime.datetime.now().replace(microsecond=0).isoformat()
    update_dns_record( id, record )
