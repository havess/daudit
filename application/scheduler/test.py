from scheduler import DauditScheduler

def main():
    scheduler = DauditScheduler()
    scheduler.schedule_job("LOLdb", "testing", "test2", hour=2)

if __name__ == "__main__":
    try:
        print("Running test job to schedule...")
        main()
    except KeyboardInterrupt:
        print("INTERRUPT")