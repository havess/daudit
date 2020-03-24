#!/usr/bin/env python3

import json
import requests
import os
from datetime import datetime

# TODO The port should not be hard-coded, it should be determined through some sort of Daudit config
DAUDIT_PORT = 3000
DAUDIT_URL = "http://127.0.0.1:%d/daudit/jobs" % DAUDIT_PORT
CONFIG_PATH = 'config.json'


def main():
    # Ensure config file exists, if not then create it with appropriate empty JSON
    if os.path.isfile(CONFIG_PATH) and os.access(CONFIG_PATH, os.R_OK):
        with open(CONFIG_PATH, 'r+') as config_file:
            config_json = json.load(config_file)
            list_of_jobs = []
            hour = datetime.now().hour
            print("\tJobs to queue:")
            for (key, value) in config_json.items():
                if value["hour_of_day"] == hour:
                    list_of_jobs.append({
                        "id": key,
                        "date_created": value['date_created'],
                        "channel_id": value['channel_id']
                    })
                    value['last_ran'] = datetime.now().strftime("%d/%m/%Y %H:%M")
                    print("\t * %s" % key)

            # Send the jobs only if there are any to send
            if len(list_of_jobs) > 0:
                r = requests.post(url=DAUDIT_URL, json=list_of_jobs)

                print("\tResponse from Daudit: " + str(r.status_code))
                if r.status_code == 200:
                    print("\tJobs successfully posted to run on Daudit!")
                else:
                    print("\tERROR: jobs not successfully posted on Daudit!")

                # Update last ran field in file
                config_file.seek(0)
                config_file.write(json.dumps(config_json))
                config_file.truncate()
            else:
                print("\tNONE - No jobs to run at this hour.")
    else:
        print("\tConfig file does not exist. Please schedule a job first.")


if __name__ == "__main__":
    try:
        print("Scanning all scheduled jobs...")
        main()
    except KeyboardInterrupt:
        print("INTERRUPT")