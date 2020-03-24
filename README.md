# Daudit Set Up

Welcome to Daudit, a data auditing tool built on top of Slack to help you quickly uncover anomalies that may have been introduced to your database before they wreak havoc on your applications. Setting up Daudit will take very little time. Follow these steps!

  

### Prerequisites

1. The machine you are installing Daudit has docker on it.

2. The machine you are installing Daudit is in the same VPC as your database, or you have enabled VPC peering, or have allowed database access from your the machine's ip address.

3. Have a Slack account / workspace for your team.

  

### Steps

1. Go to your Slack [workspace]([https://api.slack.com/](https://api.slack.com/)) and click on **Your Apps** in the top right hand corner.

2. Click **Create New App**, we recommend naming it **Daudit** and add it your team's workspace.

3. Under **Features**, click **OAuth & Permissions** and under the **Bot Token Scopes** section add the following OAuth scopes:

-  `chat:write`

-  `channels:history`

-  `im:history`

-  `im:read`

-  `users:read`

-  `users:write`

-  `app_mentions:read`

-  `channels:read`

  

	Scroll up and press the **Install App to Workspace** button

4. Git clone or download the Daudit [repo]([https://github.com/havess/daudit](https://github.com/havess/daudit)) onto your EC2 instance (or machine you plan to run Daudit from)

5. Run the following:

-  `cd daudit`

-  `sh onboarding.sh`

6. The onboarding script will ask for your **Slack Signing Secret** and **Bot User OAuth Access Token**

- Your slack signing secret can be found under **Basic Information** under the **Settings** tab.

- Your access token can be found from the **OAuth & Permissions** tab, labelled as **Bot User OAuth Access Token**

7. The onboarding script will build and start Daudit within a docker container (named daudit) on your host. At the end, the script will output the IP address of your host machine. In Slack, under the **Features** tab, click **Event Subscriptions**. In the **Request URL** field, enter `http://{IP_address}:3000/slack/events` as the endpoint.

8. On the same page, expand the **Subscribe to bot events** and add the following events:

-  `message.channels`

-  `message.im`

-  `app_mention`

9. Go into your Slack workspace, go to a channel you would like to run Daudit in , run `@Daudit help` and you will receive a response from Daudit with a list of possible commands (similar to a Linux man page). If you named your application something other than Daudit, then use that name instead of Daudit when you type a command.
