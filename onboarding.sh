#!/bin/bash



write_config() {
    descriptor="[${1}:${2}]"
    echo "${descriptor}\nDATABASE = ${2}\nHOST = ${1}\nUSERNAME = ${3}\nPASSWORD = ${4}" >> application/mysql_integration/configs/db_config.ini 
}

add_configs() {
echo ""
echo "Configure database credentials for databases you want Daudited"
echo ""
while :
do
    echo "Would you like to enter a new database configuration [y/n] ?"
    read answer
    if [ $answer = "n" ]
    then
        break
    else
        echo "Enter database host"
        read db_host
        echo "Enter database name"
        read db_name
        echo "Enter database user"
        read db_user
        echo "Enter database password"
        read db_password
        echo "Please confirm the following values [y/n]"
        echo "db_host: ${db_host}"
        echo "db_name: ${db_name}"
        echo "db_user: ${db_user}"
        echo "db_password: ${db_password}"
        read confirm
        if [ $confirm = "y" ]
        then
            echo "Awesome, adding this configuration"
            write_config $db_host $db_name $db_user $db_password
            echo ""
        else
            echo "Okay these values have been removed from your configuration"
            echo ""
        fi
    fi
done
echo ""
}

# Introduction to Onboarding
echo ""
echo "********************************************"
echo "Welcome to Daudit: Anomaly Detection For All"
echo "********************************************"
echo ""

# Configure Slack credentials
echo "Let's start with configuring Slack credentials"
echo ""
DAUDIT_INTERNAL_PASS=rootroot
echo "Please provide Slack Signing Secret"
read SLACK_SIGNING_SECRET
echo ""
echo "Please provide Bot User OAuth Access Token"
read SLACK_API_TOKEN

# Configure database credentials
add_configs

# Build the docker container
echo "Building Daudit docker container"
sleep 1
docker build -t daudit --progress=plain --build-arg slack_api_token=$SLACK_API_TOKEN --build-arg slack_sign_secret=$SLACK_SIGNING_SECRET --build-arg daudit_internal_pass=$DAUDIT_INTERNAL_PASS ./
echo "" 

# Launch the docker container
echo "Launching the Daudit docker container"
# TODO remove verbose logging when code complete
docker run --rm --name daudit -e PYTHONUNBUFFERED=0 -d -p 3000:3000 daudit

ip=$(curl https://checkip.amazonaws.com)
echo ""
echo "Please provide this ip when configuring Request URL's within Slack"
echo $ip

echo ""
echo "You're all set! Happy Dauditing!"

