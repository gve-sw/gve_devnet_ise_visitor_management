# gve_devnet_ise_visitor_management

This demo shows a visitor management based on the ISE guest users feature. Users can log into the visitor portal via their available Webex credentials. Thereby, accounts with different privileges are available – lobby and base user.   
The portal allows the creation and management of personal visitors for base users. Lobby users have access to all visitors. Additional filter and print features support the visitor workflow further.   
Invited visitors are informed about the invitation and associated access information. The user is informed about the successful completion of the process.

This demo can be used as an addition to the repository https://github.com/gve-sw/gve_devnet_ise_visitor_management_bot.

## Contacts
* Ramona Renner

## Solution Components
* ISE
* Webex

## Workflow

![/IMAGES/0image.png](/IMAGES/workflow.png)

## Architecture

![/IMAGES/0image.png](/IMAGES/arch.png)

## Prerequisites

## Webex Setup

### Register a Webex OAuth Integration

OAuth Integrations: Integrations are how you request permission to invoke the Webex REST API on behalf of a Webex Teams user. To do this securely, the API supports the OAuth2 standard, which allows third-party integrations to get a temporary access token for authenticating API calls.

To register an integration with Webex Teams:

1. Log in to developer.webex.com
2. Click on your avatar at the top of the page and then select `My Webex Apps`
3. Click `Create a New App`
4. Click `Create an Integration` to start the wizard
5. Fill in the following fields of the form:
*  Will this integration use a mobile SDK?: No
* Integration name
* Icon
* App Hub Description
* Redirect URI(s): http://localhost:5000/callback
* Scopes: Select "spark:messages_write","spark:people_read"
6. Click `Add Integration`
7. After successful registration, you'll be taken to a different screen containing your integration's newly created Client ID and Client Secret and more. Copy the secret, ID and OAuth Authorization URL and store them safely. Please note that the Client Secret will only be shown once for security purposes

> To read more about Webex Integrations & Authorization and to find information about the different scopes, you can find information [here](https://developer.webex.com/docs/integrations)


## ISE Setup

This demo can be used as an addition to the repository https://github.com/gve-sw/gve_devnet_ise_visitor_management_bot. If you already set up the demo, you can skip this section ("ISE setup") since the required settings are already executed.


#### ISE REST APIs
1. Login to your ISE PAN using the admin or other SuperAdmin user.
2. Navigate to `Administration > System > Settings` and select `API Settings` from the left panel.
3. Navigate to `API Service Settings` and enable the ERS APIs by enabling **ERS (Read/Write)**.
4. Do not enable CSRF unless you know how to use the tokens.
5. Select **Save** to save your changes.    


    > The following ISE Administrator Groups allow REST API access:
        * SuperAdmin: Read/Write
        * ERSAdmin: Read/Write
        * ERSOperator: Read Only


#### Create REST API Users
You can use the default ISE admin account for ERS APIs since it has SuperAdmin privileges. However, it is recommended to create separate users with the ERS Admin (Read/Write) or ERS Operator (Read-Only) privileges to use the ERS APIs, so you can separately track and audit their activities.

1. Navigate to `Administration > System > Admin Access`
2. Choose `Administrators > Admin Users` from the left pane
3. Choose `+Add > Create an Admin User` to create a new user with the ers-admin and ers-operator admin groups.

### Create a Sponsor Account

In order to work with guest accounts, you need to set up an additional sponsor account that is able to use the API. Sponsor accounts are needed to perform CRUD operations guest accounts.

1. In ISE, go to `Administration > Identity Management > Identities > Users`   
2. Click `+Add` to add a new user for the ALL_ACCOUNTS user group   
3. This sponsor will have visibility of ALL Guests in the system. If you wanted to limit it then you could use a different group.   
4. Click on `Submit` to save the new account   


### Give the Sponsor Group Access to the API
Under the sponsor group (ALL_ACCOUNTS) add ERS API access permission:

1. In ISE, go to `Work Centers > Guest Access > Portals & Components > Sponsor Groups > ALL_ACCOUNTS`
2. Under `Sponsor Can`, check the box for `Access Cisco ISE guest accounts using the programmatic interface (Guest REST API)`
3. Scroll to the top and click `Save`


### Add Local Location to Guest Locations and Add Guest SSID

The time zone where guests register for your Wi-Fi needs to match your local time zone:

1. In ISE, go to `Work Centers > Guest Access > Settings > Guest Locations and SSIDs`

2. Pick a name for your time zone and select the appropriate entry from the time zone list (e.g. Germany and CET), then scroll to the bottom and click `Save`

3. Add the name of your SSID for guest accounts (e.g. Guest-SSID)


### Create custom fields
Create custom fields in ISE: 

1. Go to: `Work Centers > Guest Access > Settings > Custom Fields > Fill in Custom field name > Choose Data type > Click Add > Click: Save` for the following fields:

* checkedIn
* building
* comment
* hostName
* company
* badgeId

All fields are of type string.


### Access to Sponsor Portal Test Page

1. Go to `Work Centers > Guest Access > Portals & Components > Sponsor Portals > Sponsored Portal (default) > Portal Page Customization > Portal test URL`
2. Use the credentials of the sponsor account created in a previous step (see section "Create a Sponsor Account").
3. Login once to enable the portal.
4. Click on `Manage accounts` to review all accounts. 


### (Optional) Set up Purge Policy for Expired Guest Users

Keep the number of required requests in the backend for showing available guest users small by configuring a short time frame for purging of expired guest users. More information can be found [here](https://www.cisco.com/c/en/us/support/docs/security/identity-services-engine/215931-ise-guest-account-management.html#:~:text=Guest%20Purge%20Policies,the%20next%20purge%20will%20occur.)


## Installation/Configuration

1. Make sure Python 3 and Git are installed in your environment, and if not, you may download Python 3 [here](https://www.python.org/downloads/) and [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) as described [here](https://docs.python.org/3/tutorial/venv.html).
2. Create and activate a virtual environment for the project ([Instructions](https://docs.python.org/3/tutorial/venv.html)).
3. Access the created virtual environment folder   

    ```cd [add name of virtual environment here]``` 

4. Clone this Github repository:
    ```git clone [add github link here]```
    * For Github link: In Github, click on the clone or download button in the upper part of the page > click the copy icon
    * Or simply download the repository as a zip file using 'Download ZIP' button and extract it
5. Access the downloaded folder:

    ```cd gve_devnet_ise_visitor_management```   

6. Install all dependencies:

    ```pip3 install -r requirements.txt```  

7. Fill in the environment variables in the env. file:

```
LOBBY_USERS="<Comma separated list of users with admin privileges>"
ALLOWED_DOMAINS="<Comma separated list of allowed domains to access the portal e.g., cisco.com>"

CLIENT_ID="<Client ID of Webex OAuth integration, see section "Register a Webex OAuth Integration">"    
CLIENT_SECRET="<Client secret of Webex OAuth integration, see section "Register a Webex OAuth integration">" 

REDIRECT_URI_ENDPOINT=callback
AUTHORIZATION_BASE_URL=https://webexapis.com/v1/authorize
AUTH_TOKEN_URL=https://webexapis.com/v1/access_token
SCOPE=["spark:messages_write","spark:people_read"]

ISEHOST="https://<ISE hostname/IP>​" 

ERS_USERNAME="<ISE username, see "Create REST API Users" section>"
ERS_PASSWORD="<ISE password, see "Create REST API Users" section>"

SPONSOR_USERNAME="<username of internal user for sponsor access. See the "Create a Sponsor Account" section>"
SPONSOR_PASSWORD="<password of internal user for sponsor access. See the "Create a Sponsor Account" section>"

PORTAL_ID="<ID of sponsor portal, see hint below>"

LOCATION="<Location of the company, see "Add Local Location to Guest Locations and Guest SSID" section>"
GUEST_SSID_NAME="<Name of the guest SSID to share with visitors, see "Add Local Location to Guest Locations and Guest SSID" section>"   
```   

> Hint: Get a list of all available sponsor portals and their associated IDs by accessing `localhost:5000/sponsorportals` via the browser after starting the application without a set sponsor portal id environment variable.


## Usage

To run the code, use the command:
```
$ python3 app.py
```

# Screenshots

![/IMAGES/0image.png](/IMAGES/screenshot.png)


### Limitations

* An user can not send a Webex notification to himself or herself
* The demo currently only supports one Webex email per user. In the case of Webex accounts with multiple emails per user, only the first email is used.


### Reference

* The demo uses the vanilla/plain JavaScript table sorter by tofsjonas at https://github.com/tofsjonas/sortable


### LICENSE

Provided under Cisco Sample Code License, for details see [LICENSE](LICENSE.md)

### CODE_OF_CONDUCT

Our code of conduct is available [here](CODE_OF_CONDUCT.md)

### CONTRIBUTING

See our contributing guidelines [here](CONTRIBUTING.md)

#### DISCLAIMER:
<b>Please note:</b> This script is meant for demo purposes only. All tools/ scripts in this repo are released for use "AS IS" without any warranties of any kind, including, but not limited to their installation, use, or performance. Any use of these scripts and tools is at your own risk. There is no guarantee that they have been through thorough testing in a comparable environment and we are not responsible for any damage or data loss incurred with their use.
You are responsible for reviewing and testing any scripts you run thoroughly before use in any non-testing environment.