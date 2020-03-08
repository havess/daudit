#!/bin/bash

write_config() {
    descriptor="[${1}:${2}]"
    echo "${descriptor}\nDATABASE = ${2}\nHOST = ${1}\nUSERNAME = ${3}\nPASSWORD = ${4}" >> application/mysql_integration/configs/db_config.ini 
}

add_configs() {
while :
do
    echo "Would you like to enter a new database configuration [y/n] ?"
    read answer
    if [ $answer = "n" ]
    then
        break
    else
        echo "\nEnter database host"
        read db_host
        echo "\nEnter database name"
        read db_name
        echo "\nEnter database user"
        read db_user
        echo "\nEnter database password"
        read db_password
        write_config $db_host $db_name $db_user $db_password
    fi
done
echo "Alrighty then, give us a moment while we start Daudit for you"
}

echo "***WELCOME TO DAUDIT!***\n"
echo "Follow the following instructions to set up Daudit"
sleep 5

DAUDIT_INTERNAL_PASS=rootroot
echo \nPlease provide Slack Signing Secret
read SLACK_SIGNING_SECRET
echo \nPlease provide Bot User OAuth Access Token
read SLACK_API_TOKEN

add_configs

docker build -t daudit --build-arg slack_api_token=$SLACK_API_TOKEN --build-arg slack_sign_secret=$SLACK_SIGNING_SECRET --build-arg daudit_internal_pass=$DAUDIT_INTERNAL_PASS ./
docker run --rm --name daudit -d -p 3000:3000 daudit

ip=$(curl https://checkip.amazonaws.com)
echo "\n***YOUR IP ADDRESS TO SUPPLY TO EVENT SUBSCRIPTION***"
echo $ip

echo ALL SET!

