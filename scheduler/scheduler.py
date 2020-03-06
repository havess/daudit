from crontab import CronTab
import json

CONFIG_PATH = 'config.json'
DAUDIT_COMMAND = 'python3 run_jobs.py'


def create_or_update_job_config(self, config, db_host, database, table, hour, freq_in_days):
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
        if len(self.cron.find_command(DAUDIT_COMMAND)) == 0:
            job = self.cron.new(command=DAUDIT_COMMAND)
            job.hour.every(1)
            self.cron.write()

    def schedule_job(self, db_host, database, table, hour=0, freq_in_days=1):
        if hour not in range(0, 24):
            return {"status": False, "message": "Hour must be in range [0, 24)"}

        with open(CONFIG_PATH, 'w+') as config_file:
            config_json = json.load(config_file)
            update_json = create_or_update_job_config(config_json, db_host, database, table, hour, freq_in_days)
            config_file.seek(0)
            config_file.write(json.dumps(update_json))
            config_file.truncate()

        return {"status": True, "message": ""}
