import json
import requests
from datetime import datetime

CONFIG_PATH = 'config.json'
DAUDIT_COMMAND = 'python3 run_jobs.py'
# TODO The port should not be hard-coded, it should be determined through config
DAUDIT_URL = "localhost:3000"

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
        requests.post(url=DAUDIT_URL, data=list_of_jobs)

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
