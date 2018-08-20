from apscheduler.schedulers.blocking import BlockingScheduler
import subprocess

sched = BlockingScheduler()

@sched.scheduled_job('interval', minutes=1)
def timed_job():
    subprocess.call('python manage.py send_mail', shell=True, close_fds=True)

@sched.scheduled_job('cron', day_of_week='mon-sun', hour=0, minute=0)
def scheduled_job():
    subprocess.call('python manage.py update_sitemap', shell=True, close_fds=True)

sched.start()