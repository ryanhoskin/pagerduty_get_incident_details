#!/usr/bin/env python

import requests
import sys
import json

#Your PagerDuty API key.  A read-only key will work for this.
AUTH_TOKEN = 'mRw3SBLy6WxD4qVsJiGB'
#The API base url, make sure to include the subdomain
BASE_URL = 'https://pdt-ryan.pagerduty.com/api/v1'
#The service ID that you would like to query.  You can leave this blank.
service_id = ""
#The start date that you would like to search.
since = "2013-04-15"
#The end date that you would like to search.
until = "2013-05-02"

HEADERS = {
    'Authorization': 'Token token={0}'.format(AUTH_TOKEN),
    'Content-type': 'application/json',
}

def get_incidents(since, until, service_id=None):
    file_name = 'pagerduty_export.csv'

    params = {
        'service':service_id,
        'since':since,
        'until':until
    }

    all_incidents = requests.get(
        '{0}/incidents'.format(BASE_URL),
        headers=HEADERS,
        data=json.dumps(params)
    )

    print "Exporting incident data to " + file_name
    for incident in all_incidents.json()['incidents']:
        get_incident_details(incident["id"], str(incident["incident_number"]), incident["service"]["name"], file_name)
    print "Exporting has completed successfully."

def get_incident_details(incident_id, incident_number, service, file_name):
    start_time = ""
    end_time = ""
    summary = ""
    has_details = False
    has_summary = False
    output = incident_number + "," + service + ","

    f = open(file_name,'a')

    log_entries = requests.get(
        '{0}/incidents/{1}/log_entries?include[]=channel'.format(BASE_URL,incident_id),
        headers=HEADERS
    )

    for log_entry in log_entries.json()['log_entries']:
        if log_entry["type"] == "trigger":
            if log_entry["created_at"] > start_time:
                start_time = log_entry["created_at"]
                if ("summary" in log_entry["channel"]):
                    has_summary = True
                    summary = log_entry["channel"]["summary"]
                if ("details" in log_entry["channel"]):
                    has_details = True
                    details = log_entry["channel"]["details"]
        elif log_entry["type"] == "resolve":
            end_time = log_entry["created_at"]

    output += start_time + ","
    output += end_time
    if (has_summary):
        output += ",\"" + summary + "\""
    if (has_details):
        output += ",\"" + str(details) + "\""
    output += "\n"
    #print output
    f.write(output)

get_incidents(since = since, until = until, service_id = service_id)