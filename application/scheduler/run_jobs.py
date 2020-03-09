#!/usr/bin/env python3

import json
import requests
import os
from datetime import datetime
from pytz import timezone

# TODO The port should not be hard-coded, it should be determined through some sort of Daudit config
DAUDIT_PORT = 3000
DAUDIT_URL = "http://127.0.0.1:%d/daudit/jobs" % DAUDIT_PORT
CONFIG_PATH = 'config.json'


def main():
    # Ensure config file exists, if not then create it with appropriate empty JSON
    if os.path.isfile(CONFIG_PATH) and os.access(CONFIG_PATH, os.R_OK):
        with open(CONFIG_PATH, 'r+') as config_file:
            config_json = json.load(config_file)
            print("Sending the following jobs:")
            list_of_jobs = []
            tz = 'US/Eastern'
            hour = datetime.now(timezone(tz)).hour
            for (key, value) in config_json.items():
                # TODO: Make it so that we check if a job should be run based on last ran
                # if value["hour_of_day"] == hour:
                list_of_jobs.append({"id": key})
                # TODO: Also need date_col and channel_id (whatever channel)
                config_json[key]['last_ran'] = datetime.now().strftime("%d/%m/%Y %H:%M")
                print("\t%s" % key)

            # Send the jobs
            print("Current time (%s): %s" % (datetime.now(), tz))
            print("Sending: " + str(list_of_jobs))
            r = requests.post(url=DAUDIT_URL, json=list_of_jobs)

            print("Response from Daudit: " + str(r.status_code))
            if r.status_code == 200:
                print("Jobs successfully posted to run on Daudit!")
            else:
                print("ERROR: jobs not successfully posted on Daudit!")

            # Update last ran field in file
            config_file.seek(0)
            config_file.write(json.dumps(config_json))
            config_file.truncate()
    else:
        print("Config file does not exist. Please schedule a job first.")


if __name__ == "__main__":
    try:
        print("Running jobs that are scheduled...")
        main()
    except KeyboardInterrupt:
        print("INTERRUPT")
