#!/bin/bash
echo "Welcome to Daudit, we'll take it from here"
DAUDIT_INTERNAL_PASS=rootroot
echo Please provide Slack Signing Secret
read SLACK_SIGNING_SECRET
echo Please provide Slack Api Token
read SLACK_API_TOKEN
docker build -t daudit --build-arg slack_api_token=$SLACK_API_TOKEN --build-arg slack_sign_secret=$SLACK_SIGNING_SECRET --build-arg daudit_internal_pass=$DAUDIT_INTERNAL_PASS ./
docker run --rm -d -p 3000:3000 daudit
echo All set!
