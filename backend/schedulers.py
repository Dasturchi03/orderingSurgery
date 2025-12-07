from apscheduler.schedulers.background import BackgroundScheduler
from datetime import date, timedelta
from .models import SurgeryDay


logger = logging.getLogger('__main__')


def mark_surgery_days_uneditable():
    today = date.today() - timedelta(days=1)
    try:
        surgery_days = SurgeryDay.objects.filter(date=today)
        for day in surgery_days:
            day.editable = False
            day.save()
        logger.info(f"Updated SurgeryDay editable to False for {today}")
    except Exception as e:
        logger.info(f"Error while updating SurgeryDay: {e}")


def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(mark_surgery_days_uneditable, 'cron', hour=16, minute=0)
    scheduler.start()
    logger.info("Scheduler started")
