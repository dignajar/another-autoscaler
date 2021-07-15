import os
import schedule
import time
from aautoscaler import AAutoscaler

checkEvery = 5 # Check annotations every 5 seconds by default
if 'CHECK_EVERY' in os.environ:
	checkEvery = int(os.environ['CHECK_EVERY'])

aautoscaler = AAutoscaler()
schedule.every(checkEvery).seconds.do(aautoscaler.execute)
while True:
	schedule.run_pending()
	time.sleep(1)