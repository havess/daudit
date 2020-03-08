#!/usr/bin/env python3

import json
import requests
from datetime import datetime

# TODO The port should not be hard-coded, it should be determined through some sort of Daudit config
DAUDIT_PORT = 3010
DAUDIT_URL = "http://127.0.0.1:%d/daudit/jobs" % DAUDIT_PORT
CONFIG_PATH = 'config.json'


def main():
    with open(CONFIG_PATH, 'r+') as config_file:
        config_json = json.load(config_file)
        print("Sending the following jobs:")
        list_of_jobs = []
        hour = datetime.now().hour
        for (key, value) in config_json.items():
            if value["hour_of_day"] == hour:
                list_of_jobs.append({"id": key})
                config_json[key]['last_ran'] = datetime.now().strftime("%d/%m/%Y %H:%M")
                print("\t%s" % key)

        # Send the jobs
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


if __name__ == "__main__":
    try:
        print("Running jobs that are scheduled...")
        main()
    except KeyboardInterrupt:
        print("INTERRUPT")
