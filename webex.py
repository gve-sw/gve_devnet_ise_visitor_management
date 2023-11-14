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

from webexteamssdk import WebexTeamsAPI
from utils import Utils
import json

class Webex():

    def __init__(self, webex_access_token):
        self.api = WebexTeamsAPI(access_token=webex_access_token)
   
    def get_me_details(self):
        return json.dumps(self.api.people.me(), default=lambda o: o.__dict__)
    

    '''
    Populates the host card template and sends a direct message to the host.
    '''
    def send_host_notifications(self, host_email, guest_name, company, phone_nr, building, time_range):
        host_card_content = self.prepare_host_notification_card(guest_name, company, phone_nr, building, time_range)
        self.send_webex_direct_message_card(host_email, host_card_content)


    '''
    Polulates the host card template based on provided values.
    '''
    def prepare_host_notification_card(self, guest_name, company, phone_nr, building, time_range):

        host_card = Utils.read_json('webex_card_templates/webex_card_host.json')
        host_card['body'][1]['columns'][1]['items'][0]['text'] = guest_name
        host_card['body'][2]['columns'][1]['items'][0]['text'] = company
        host_card['body'][3]['columns'][1]['items'][0]['text'] = phone_nr
        host_card['body'][4]['columns'][1]['items'][0]['text'] = building
        host_card['body'][5]['columns'][1]['items'][0]['text'] = time_range

        return host_card

    '''
    Populates the visitor card template and sends a direct message to the visitor.
    '''
    def send_visitor_notifications(self, visitor_email, host_name, building, date, ssid, username, password):

        visitor_card_content = self.prepare_visitor_notification_card(host_name, building, date, ssid, username, password)
        self.send_webex_direct_message_card(visitor_email, visitor_card_content)

    
    '''
    Polulates the visitor card template based on provided values.
    '''
    def prepare_visitor_notification_card(self, host_name, building, date, ssid, username, password):

        visitor_card = Utils.read_json('webex_card_templates/webex_card_visitor.json')
        visitor_card['body'][1]['columns'][1]['items'][0]['text'] = host_name
        visitor_card['body'][2]['columns'][1]['items'][0]['text'] = building
        visitor_card['body'][3]['columns'][1]['items'][0]['text'] = date
        visitor_card['body'][5]['columns'][1]['items'][0]['text'] = ssid
        visitor_card['body'][6]['columns'][1]['items'][0]['text'] = username
        visitor_card['body'][7]['columns'][1]['items'][0]['text'] = password

        return visitor_card


    '''
    Sends direct message with card to defined Webex recipient
    '''
    def send_webex_direct_message_card(self, toPersonEmail, card_content):

        self.api.messages.create(toPersonEmail=toPersonEmail, text="You received a Webex card.", attachments=[{
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": card_content
            }])


 

    
