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

# Import Section
from flask import Flask, render_template, request, url_for, redirect, session
import json
from requests_oauthlib import OAuth2Session
from datetime import datetime
from dotenv import load_dotenv, set_key
import os
import ise
from utils import Utils
from webex import Webex

load_dotenv()

app = Flask(__name__)
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
app.secret_key = os.urandom(24)


'''
Step 1: Route for login and logout page
'''
@app.route("/")
@app.route('/?logout=<logout>',  methods=["GET"])
def login():
    '''
    Step 1: User Authorization.
    Redirect the user/resource owner to the OAuth provider (i.e. Webex Teams)
    using a URL with a few key OAuth parameters.
    '''
    
    logout_old_session = request.args.get('logout')
    
    if logout_old_session:
        prompt = "select_account"
    else:
        prompt = None

    teams = OAuth2Session(CLIENT_ID, scope=SCOPE, redirect_uri=request.base_url + REDIRECT_URI_ENDPOINT)
    authorization_url, state = teams.authorization_url(AUTHORIZATION_BASE_URL, prompt=prompt)

    # State is used to prevent CSRF, keep this for later.
    session['oauth_state'] = state

    print("Step 1: User Authorization. Session state:", state)

    return redirect(authorization_url)


'''
Step 2: User authorization, this happens on the provider.
'''
@app.route("/callback", methods=["GET"])
def callback():
    '''
    Step 2: Retrieving an access token.
    The user has been redirected back from the provider to your registered
    callback URL. With this redirection comes an authorization code included
    in the redirect URL. We will use that to obtain an access token.
    '''
    try:
        auth_code = OAuth2Session(CLIENT_ID, state=session['oauth_state'], redirect_uri=request.base_url)
        token = auth_code.fetch_token(AUTH_TOKEN_URL, client_secret=CLIENT_SECRET,
                                    authorization_response=request.url)

        '''
        At this point you can fetch protected resources but lets save
        the token and show how this is done from a persisted token
        '''

        session['oauth_token'] = token

        print("Step 2: Retrieving an access token.")
    
    except Exception as e:
        print(e)
        return redirect(url_for('login'))
    
    return redirect(url_for('.started'))

'''
Step 3: Save token and personal data. Check domain of user.
'''
@app.route("/started", methods=["GET"])
def started():
    global ALLOWED_DOMAINS
    try:
        print("Step 3: Set token and get person data")

        webex_token = session['oauth_token']
        session['token'] = webex_token['access_token']
        session['expires_at']  = webex_token['expires_at']
        
        webex_api = Webex(session['token'])
        
        user_data = webex_api.get_me_details()
        session['me'] = user_data 

        for email in json.loads(user_data)['_json_data']['emails']:
            email_domain = email.split("@")[1]
            if email_domain in ALLOWED_DOMAINS:
                return redirect("/lobby?success=False&error=False&message=''")
             
    except Exception as e:
        print(e)
    
    print("User is missing permissions to access the visitor management based on the email domain provided.")
    return redirect('/?logout=true', code=302)


'''
Route to create new visitors.
'''
@app.route('/create_visitor',  methods=["GET", "POST"])
def create_visitor():
    try:
        global LOBBY_USERS

        if 'token' in session:

            host_email = json.loads(session['me'])['_json_data']['emails'][0]
            host_name = json.loads(session['me'])['_json_data']['displayName'] 

            if Utils.is_visitor_management_admin(LOBBY_USERS, host_email) != None:
                host_name = host_name + " (Lobby)"

            if request.method == 'POST':
                
                building = request.form.get("building-select")            
                phone_number = request.form.get("phone-number-input")
                company = request.form.get("company-input")
                comment = request.form.get("comment-input")
                email = request.form.get("email-input")
                check_in = request.form.get("checking-toggle") == 'on' 
                badge_id = request.form.get("input-badge-id")         
                purpose = request.form.get("purpose-select")
                firstname = request.form.get("first-name-input")
                lastname = request.form.get("last-name-input")
                now_date_string = datetime.now().strftime("%m%d%Y_%H%M%S")
                username = f"{firstname}_{lastname}_{now_date_string}".replace(" ", "")
                start_date = request.form.get("start-date")
                end_date = request.form.get("end-date")
                visit_date = start_date + "-" + end_date

                ise.create_guest_user(username, comment, firstname, lastname, email, phone_number, company, start_date, end_date, check_in, host_email, building, purpose, host_name, badge_id)

                created_user = ise.get_guest_based_on_username(username)

                if email != "" and email != host_email:
                    username = created_user['GuestUser']['guestInfo']['userName']
                    password = created_user['GuestUser']['guestInfo']['password']
                    ssid = created_user['GuestUser']['guestAccessInfo']['ssid']
                    
                    webex_api = Webex(session['token'])
                    webex_api.send_visitor_notifications(email, host_name, building, visit_date, ssid, username, password)
                
                return redirect("/lobby?success=True&error=False&message=The guest user was successfully created and notified via Webex.")

            return render_template('add_visitor.html', host_email=host_email, host_name=host_name, hiddenLinks=False)
        
        else:
            return redirect(url_for('login'))

    except Exception as e: 
        print("Error")
        print(e) 
        return render_template('add_visitor.html', error="True", host_email="", host_name="", message=e)


'''
Route to add/remove lobby/admin users to the system.
'''
@app.route('/addLobbyUser',  methods=["GET", "POST"])
def addLobbyUser():
    try:
        global LOBBY_USERS

        lobby_user_string = request.form.get('input-lobby-users').replace(" ","")
        LOBBY_USERS = lobby_user_string.split(",")

        os.environ['LOBBY_USERS'] = lobby_user_string
        set_key(".env", "LOBBY_USERS", os.environ["LOBBY_USERS"])

        return redirect("/lobby?success=True&error=False&message=Successfully changed lobby user settings.")
    
    except Exception as e: 
        print(f"Error: {e}")
        return redirect(f"/lobby?success=False&error=True&&message={e}")



'''
Route to handle check ins or visitors.
'''
@app.route('/checkin',  methods=["GET", "POST"])
def checkin():
    try:
        global LOBBY_USERS

        if 'token' in session:

            logged_in_user_email = json.loads(session['me'])['_json_data']['emails'][0]
        
            user_id = request.form.get('input-user-id')
            badge_id = request.form.get("input-badge-id")
            host_email = request.form.get("input-host-email")

            ise.checkin_user(user_id, badge_id)

            if logged_in_user_email != host_email:

                user_details = ise.get_guest_user_by_ID(user_id)
                
                guest_first_name = user_details['GuestUser']['guestInfo']['firstName']
                guest_last_name = user_details['GuestUser']['guestInfo']['lastName']
                guest_name = f"{guest_first_name} {guest_last_name}"
                company = user_details['GuestUser']['customFields'].get('ui_company_text_label','')
                phone_nr = user_details['GuestUser']['guestInfo'].get('phoneNumber','')
                building = user_details['GuestUser']['customFields'].get('ui_building_text_label','')
                from_date = user_details['GuestUser']['guestAccessInfo']['fromDate']
                to_date = user_details['GuestUser']['guestAccessInfo']['toDate']
                time_range = f"{from_date} - {to_date}"

                webex_api = Webex(session['token'])
                webex_api.send_host_notifications(host_email, guest_name, company, phone_nr, building, time_range)

            return redirect("/lobby?success=True&error=False&message=Successfully checked in guest.")

        else:
            return redirect(url_for('login'))

    except Exception as e: 
        print(f"Error: {e}")
        return redirect(f"/lobby?success=False&error=True&&message={e}")


'''
Route to handle check out of visitor 
'''
@app.route('/checkout',  methods=["GET", "POST"])
@app.route('/checkout?user_id=<user_id>',  methods=["GET", "POST"])
def checkout():
    try:
    
        user_id = request.args.get('user_id')
        ise.checkout_user(user_id)

        return redirect("/lobby?success=True&error=False&message=Successfully checked out guest.")

    except Exception as e: 
        print(f"Error: {e}")
        return redirect(f"/lobby?success=False&error=True&message={e}")


'''
Route for the lobby view
'''
@app.route('/lobby?success=<success>&error=<error>&message=<message>')
@app.route('/lobby', methods=["GET","POST"]) 
def lobby():

    try:
        global LOBBY_USERS
        is_lobby_user = False
        error = request.args.get('error')
        success = request.args.get('success')
        message = request.args.get('message')

        if 'me' in session:
            
            host_email = json.loads(session['me'])['_json_data']['emails'][0]
            host_name = json.loads(session['me'])['_json_data']['displayName']

            today_str = Utils.get_today_str("%Y-%m-%d")
            users_details = []
            
            if Utils.is_visitor_management_admin(LOBBY_USERS, host_email) != None:
                filter=""
                host_name = host_name + " (Lobby)"
                is_lobby_user = True
            else:
                filter = f"?filter=personBeingVisited.EQ.{host_email}"
            
            users = ise.get_guest_users(filter=filter)

            for user in users['SearchResult']['resources']:
                ise_user_id = user['id']
                user_details = ise.get_guest_user_by_ID(ise_user_id)
                users_details.append(user_details['GuestUser'])
    
            return render_template("lobby.html", users_details = users_details, error=error, message=message, today_str=today_str, host_name=host_name, success=success, lobby_users=",".join(LOBBY_USERS), is_lobby_user=is_lobby_user)

        else:
            return redirect(url_for('login'))

    except Exception as e: 
        print(f"Error: {e}")
        return render_template("lobby.html", users_details = [], error="True", message=e, today_str=today_str, host_name=host_name, success="False", lobby_users=",".join(LOBBY_USERS), is_lobby_user=is_lobby_user)



'''
Retrieve the available sponsor portals + guest SSIDs and corresponding information (including ID)
'''
@app.route('/sponsorportals', methods=["GET"])
def sponsorPortals():
    try:
        print('--------RETRIEVING SPONSOR PORTALS----------')
        sponsorPortals = ise.get_sponsor_portals()
        guestSSIDs = ise.get_guest_SSIDs()
        
        return render_template("sponsorPortals.html", sponsorPortals = sponsorPortals, guestSSIDs=guestSSIDs)
    
    except Exception as e: 
        print(f"Error: {e}")
        return render_template("sponsorPortals.html", error="True", message=e, sponsorPortals = [], guestSSIDs=[])


if __name__ == "__main__":
    
    #Visitor Management
    LOBBY_USERS = os.environ['LOBBY_USERS'].split(",")
    ALLOWED_DOMAINS = os.environ['ALLOWED_DOMAINS'].split(",")

    #Webex oAuth
    CLIENT_ID = os.environ['CLIENT_ID'] 
    CLIENT_SECRET = os.environ['CLIENT_SECRET']
    REDIRECT_URI_ENDPOINT = os.environ['REDIRECT_URI_ENDPOINT']  
    AUTHORIZATION_BASE_URL = os.environ['AUTHORIZATION_BASE_URL']
    AUTH_TOKEN_URL = os.environ['AUTH_TOKEN_URL']
    SCOPE = json.loads(os.environ['SCOPE']) 

    #ISE 
    ISEHOST = os.environ['ISEHOST'] 
    ERS_USERNAME = os.environ['ERS_USERNAME']
    ERS_PASSWORD = os.environ['ERS_PASSWORD']
    SPONSOR_USERNAME = os.environ['SPONSOR_USERNAME']
    SPONSOR_PASSWORD = os.environ['SPONSOR_PASSWORD']
    PORTAL_ID = os.environ['PORTAL_ID']
    LOCATION = os.environ['LOCATION']
    GUEST_SSID = os.environ['GUEST_SSID_NAME']

    ise = ise.ISE()
    
    app.run(host='0.0.0.0', debug=True)