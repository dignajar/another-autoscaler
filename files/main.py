import os
import schedule
import time
from ascheduler import AScheduler

checkEvery = 5 # Check annotations every 5 seconds by default
if 'CHECK_EVERY' in os.environ:
    checkEvery = int(os.environ['CHECK_EVERY'])

ascheduler = AScheduler()
schedule.every(checkEvery).seconds.do(ascheduler.execute)
while True:
    schedule.run_pending()
    time.sleep(1)