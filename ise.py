""" Copyright (c) 2023 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at
           https://developer.cisco.com/docs/licenses
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied. 
"""

import base64
import json 
import requests
import urllib3
import os
from dotenv import load_dotenv

load_dotenv()

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from datetime import datetime

class ISE():

    def __init__(self):
        
        self.ise_host = os.environ['ISEHOST'] 
        self.ers_headers = self.get_authentication_headers(os.environ['ERS_USERNAME'], os.environ['ERS_PASSWORD'])
        self.sponsor_username = os.environ['SPONSOR_USERNAME']
        self.sponsor_headers = self.get_authentication_headers(os.environ['SPONSOR_USERNAME'], os.environ['SPONSOR_PASSWORD'])
        self.sponsor_portal_id = os.environ['PORTAL_ID']
        self.guest_ssid = os.environ['GUEST_SSID_NAME']
        self.location = os.environ['LOCATION']


    def get_authentication_headers(self, username, password):
        
        basic_auth_string = bytes.decode(base64.b64encode(str.encode(f"{username}:{password}")))
        headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': 'Basic ' + basic_auth_string
                }
        return headers 


    def make_rest_call(self, method, url_endpoint, headers, payload, method_name):

        resp = requests.request(method, f"{self.ise_host}:9060/ers/config/{url_endpoint}",
                            verify=False, headers=headers, data=payload)
        
        if resp.status_code == 201 or resp.status_code == 200:
            print("Success")
            try: 
                return resp.json()
            except json.decoder.JSONDecodeError:
                return resp

        else:
            print("Error during API call.")
            try:
                error = f'{resp.json()["ERSResponse"]["messages"][0]["title"]} in method: {method_name}'
            except Exception as e:
                print(resp) 
                error = resp   
            raise Exception(error)
            


    def create_guest_user(self, username, comment, firstname, lastname, email, phone_number, company, start_date, end_date, checked_in, host_email, building, purpose, hostname, badge_id):
        
        fromDate = datetime.strptime(start_date, '%Y-%m-%dT%H:%M')
        toDate = datetime.strptime(end_date, '%Y-%m-%dT%H:%M')
        date_delta = toDate - fromDate
        validDays = date_delta.days
        
        if validDays == 0:
            validDays = 1

        fromDateString = fromDate.strftime("%m/%d/%Y %H:%M")
        toDateString = toDate.strftime("%m/%d/%Y %H:%M")
        
        payload = json.dumps({
            "GuestUser" : {
                "id" : "", #is automatically set by ISE
                "name" : str(username),
                "guestType" : "Contractor (default)",
                "sponsorUserName" : self.sponsor_username,
                "reasonForVisit": purpose,
                "personBeingVisited": host_email,
                "guestInfo" : {
                    "userName" : str(username),
                    "firstName" : str(firstname),
                    "lastName" : str(lastname),
                    "emailAddress" : str(email),
                    "phoneNumber" : str(phone_number),
                    "password" : "", #is automatically set by ISE
                    "company" : company
                },
                "guestAccessInfo" : {
                    "validDays" : validDays,
                    "fromDate" : fromDateString,
                    "toDate" : toDateString,
                    "location" : self.location,
                    "ssid": "Guest-SSID"
                },
                "portalId" : self.sponsor_portal_id,
                "customFields": {
                    "checkedIn": checked_in,
                    "building": building,
                    "comment": comment,
                    "hostName": hostname,
                    "badgeId": badge_id,
                    "company" : company 
                }
                ,
            }
        })

        url_endpoint = 'guestuser'
        headers = self.sponsor_headers
        
        return self.make_rest_call('POST', url_endpoint, headers, payload, "create_guest_user")


    def checkin_user(self, user_id, badge_id):
        '''Checkin  user. '''

        print(f'---------------UPDATE GUEST USER BY ID: {user_id} --------------------')


        payload = json.dumps({
            "GuestUser" : {
                "guestType" : "Contractor (default)",
                "guestInfo":{},
                "guestAccessInfo" : {},
                "portalId" : self.sponsor_portal_id,
                "customFields":{
                    "ui_checkedin_text_label": True,
                    "ui_badgeid_text_label" : badge_id
                }
                }
            })

        url_endpoint = "guestuser/"+ user_id
        headers = self.sponsor_headers

        return self.make_rest_call('PUT', url_endpoint, headers, payload, "checkin_user")



    def checkout_user(self, user_id):
        '''Checkout user. '''

        print('---------------UPDATE GUEST USER BY ID: '+ user_id +' --------------------')


        payload = json.dumps({
            "GuestUser" : {
                "guestType" : "Contractor (default)",
                "guestInfo":{},
                "guestAccessInfo" : {},
                "portalId" : self.sponsor_portal_id,
                "customFields":{
                    "ui_checkedin_text_label": False
                }
                }
            })

        url_endpoint = "guestuser/"+ user_id
        headers = self.sponsor_headers

        return self.make_rest_call('PUT', url_endpoint, headers, payload, "checkout_user")


    def get_guest_users(self, filter=""):

        print('-------------------GET ALL GUEST USERS-------------------')

        url_endpoint = "guestuser" + filter
        headers = self.sponsor_headers
        payload = {}

        return self.make_rest_call('GET', url_endpoint, headers, payload, "get_guest_users")


    def get_guest_user_by_ID(self, userID):

        print('---------------GET GUEST USER BY ID: '+ userID +'--------------------')
        
        url_endpoint = "guestuser/" + userID
        headers = self.sponsor_headers
        payload = {}

        return self.make_rest_call('GET', url_endpoint, headers, payload, "get_guest_user_by_ID")


    def get_guest_based_on_username(self, name):

        print('------------------GET GUEST USER BY USERNAME: '+ name +'--------------')

        url_endpoint = "guestuser/name/" + name
        headers = self.sponsor_headers
        payload = {}

        return self.make_rest_call('GET', url_endpoint, headers, payload, "get_guest_based_on_username")


    def get_sponsor_portals(self):

        print('-----------------GET SPONSOR PORTALS----------------')
        
        url_endpoint = "sponsorportal"
        headers = self.ers_headers
        payload = {}

        return self.make_rest_call('GET', url_endpoint, headers, payload, "get_sponsor_portals")
    
    
    def get_guest_SSIDs(self):

        print('-----------------GET GUEST SSIDs----------------')
        
        url_endpoint = "guestssid"
        headers = self.ers_headers
        payload = {}

        return self.make_rest_call('GET', url_endpoint, headers, payload, "get_guest_SSIDs")
