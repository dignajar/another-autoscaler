import schedule
import time
from logic import Logic

logic = Logic()

schedule.every(1).seconds.do(logic.execute)
while True:
    schedule.run_pending()
    time.sleep(1)