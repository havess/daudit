from crontab import CronTab
import json
import os
import sys
from datetime import datetime
from pytz import timezone

CONFIG_PATH = 'scheduler/config.json'
DAUDIT_COMMAND = '(cd /home/application/scheduler/ && echo "*** `date -u` ***" >> out.log && ./run_jobs.py >> out.log)'


def create_or_update_job_config(channel, config, db_host, database, table, hour, freq_in_days):
    key = '%s/%s/%s' % (db_host, database, table)
    if key in config:
        config[key]['hour_of_day'] = hour
        config[key]['channel_id'] = channel
        if freq_in_days > 0:
            config[key]['freq_in_days'] = freq_in_days
    else:
        config[key] = {
            'hour_of_day': hour,
            'freq_in_days': freq_in_days,
            'last_ran': "",
            'date_created': datetime.now().strftime("%d/%m/%Y %H:%M"),
            'channel_id': channel
        }
    return config


class DauditScheduler:
    def __init__(self):
        self.cron = CronTab(user=True)
        for job in self.cron.find_command(DAUDIT_COMMAND):
            self.cron.remove(job)
        job = self.cron.new(command=DAUDIT_COMMAND)
        job.every(1).minutes()
        self.cron.write()

    def get_job_list(self):
        with open(CONFIG_PATH, 'r+') as config_file:
            config_json = json.load(config_file)
            list_of_jobs = []
            for (key, val) in config_json.items():
                list_of_jobs.append(key + " " + str(val['hour_of_day']) + " " + str(val['freq_in_days']))
            return list_of_jobs

    def schedule_job(self, channel, db_host, database, table, hour=0, freq_in_days=1):
        if hour not in range(0, 24):
            return False, "Hour must be in range [0, 24)"

        # Ensure config file exists, if not then create it with appropriate empty JSON
        if os.path.isfile(CONFIG_PATH) and os.access(CONFIG_PATH, os.R_OK):
            print("Config file exists and is readable")
        else:
            with open(CONFIG_PATH, 'a+') as f:
                f.write(json.dumps({}))

        with open(CONFIG_PATH, 'r+') as f:
            config_json = json.load(f)
            update_json = create_or_update_job_config(channel, config_json, db_host, database, table, hour, freq_in_days)
            f.seek(0)
            f.write(json.dumps(update_json))
            f.truncate()

        return True, ""

    def update_job(self, channel, job_id, time, frequency):
        # Ensure config file exists
        if os.path.isfile(CONFIG_PATH) and os.access(CONFIG_PATH, os.R_OK):
            pass
        else:
            return False, "No jobs seem to exist, config file empty."

        host, database, table = job_id.split("/")

        with open(CONFIG_PATH, 'r+') as f:
            config_json = json.load(f)
            update_json = create_or_update_job_config(channel, config_json, host, database, table, time, frequency)
            f.seek(0)
            f.write(json.dumps(update_json))
            f.truncate()

        return True, ""

    def delete_job(self, job):
        # Ensure config file exists
        if os.path.isfile(CONFIG_PATH) and os.access(CONFIG_PATH, os.R_OK):
            pass
        else:
            return False, "No jobs seem to exist, config file empty."

        with open(CONFIG_PATH, 'r+') as f:
            config_json = json.load(f)
            print("CONFIG JSON", config_json)
            config_json.pop(job)
            f.seek(0)
            f.write(json.dumps(config_json))
            f.truncate()

        return True, ""
