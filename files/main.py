import os
import schedule
import time
from aautoscaler import AAutoscaler
from logs import Logs

checkEvery = 5  # Check annotations every 5 seconds by default
if 'CHECK_EVERY' in os.environ:
    checkEvery = int(os.environ['CHECK_EVERY'])

mode = 'daemon'
if 'MODE' in os.environ:
    mode = os.environ['MODE']

aautoscaler = AAutoscaler()
if mode == 'daemon':
    schedule.every(checkEvery).seconds.do(aautoscaler.execute)
    while True:
        schedule.run_pending()
        time.sleep(1)
else:
    Logs(self.__class__.__name__).info({'message': 'Running once then exit.'})
    aautoscaler.execute()
