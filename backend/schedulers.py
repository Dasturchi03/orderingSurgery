<<<<<<< HEAD
import logging
=======
>>>>>>> 81dc4b2 (Initial commit)
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import date, timedelta
from .models import SurgeryDay


<<<<<<< HEAD
logger = logging.getLogger('__main__')


=======
>>>>>>> 81dc4b2 (Initial commit)
def mark_surgery_days_uneditable():
    today = date.today() - timedelta(days=1)
    try:
        surgery_days = SurgeryDay.objects.filter(date=today)
        for day in surgery_days:
            day.editable = False
            day.save()
<<<<<<< HEAD
        logger.info(f"Updated SurgeryDay editable to False for {today}")
    except Exception as e:
        logger.info(f"Error while updating SurgeryDay: {e}")
=======
        print(f"Updated SurgeryDay editable to False for {today}")
    except Exception as e:
        print(f"Error while updating SurgeryDay: {e}")
>>>>>>> 81dc4b2 (Initial commit)


def start_scheduler():
    scheduler = BackgroundScheduler()
<<<<<<< HEAD
    scheduler.add_job(mark_surgery_days_uneditable, 'cron', hour=16, minute=0)
    scheduler.start()
    logger.info("Scheduler started")
=======
    scheduler.add_job(mark_surgery_days_uneditable, 'cron', hour=15, minute=0)
    scheduler.start()
    print("Scheduler started")
>>>>>>> 81dc4b2 (Initial commit)
