from crontab import CronTab
import json
import os

CONFIG_PATH = 'config.json'
DAUDIT_COMMAND = '%s/run_jobs.py > %s/out.log 2>&1' % (os.getcwd(), os.getcwd())


def create_or_update_job_config(config, db_host, database, table, hour, freq_in_days):
    key = '%s:%s:%s' % (db_host, database, table)
    if key in config:
        config[key]['hour_of_day'] = min(hour, int(config[key]['hour_of_day']))
        config[key]['freq_in_days'] = min(freq_in_days, int(config[key]['freq_in_days']))
    else:
        config[key] = {'hour_of_day': hour, 'freq_in_days': freq_in_days, 'last_ran': ""}
    return config


class DauditScheduler:
    def __init__(self):
        self.cron = CronTab(user=True)
        for job in self.cron.find_command(DAUDIT_COMMAND):
            self.cron.remove(job)
        job = self.cron.new(command=DAUDIT_COMMAND)
        job.every(1).minutes()
        self.cron.write()

    def schedule_job(self, db_host, database, table, hour=0, freq_in_days=1):
        if hour not in range(0, 24):
            return {"status": False, "message": "Hour must be in range [0, 24)"}

        # Ensure config file exists, if not then create it with appropriate empty JSON
        if os.path.isfile(CONFIG_PATH) and os.access(CONFIG_PATH, os.R_OK):
            print("Config file exists and is readable")
        else:
            with open(CONFIG_PATH, 'a+') as f:
                f.write(json.dumps({}))

        with open(CONFIG_PATH, 'r+') as f:
            config_json = json.load(f)
            update_json = create_or_update_job_config(config_json, db_host, database, table, hour, freq_in_days)
            f.seek(0)
            f.write(json.dumps(update_json))
            f.truncate()

        return {"status": True, "message": ""}