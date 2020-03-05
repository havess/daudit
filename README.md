# daudit
Data Auditing

To run slack bot:
1. Clone Daudit repo to /daudit
2. Go to slack workspace apps, create application and name it whatever you want ("Daudit" is our recommendation ;))
3. From /daudit Run `pip3 install -r requirements.txt`
4. In Slack app settings panel go to OAuth & Permissions:
    * Scroll down to the Bot Token Scopes section and click Add an OAuth Scope.
    * Add :
      * chat:write
      * channels:history
      * im:history
      * im:read
      * users:read
      * users:write
    
    * Scroll up and press the Install App to Workspace button
5. Run ```export SLACK_SIGNING_SECRET=your_signing_secret
 export SLACK_API_TOKEN=your_oauth_bot_user_token ```` 
6. Run `python3 app.py`
7. Subscribe to Events in the Event Subscriptions tab
    * Enable event handling with the switch.
    * In the Request URL field, enter your endpoint followed by '/slack/events'
      For example `https://010101.ngrok.io/slack/events`
    * Click Save Changes
    * Subscribe to :
      * message.im
      * message.channels
    * Click Save Changes
8. DM the Daudit bot under "Apps" in Slack. Try sending 'help'.
