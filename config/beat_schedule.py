from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'daily-attendance-summary': {
        'task': 'attendance.daily_summary',
        'schedule': crontab(hour=23, minute=0),  # Every day at 11pm
    },
    'flag-stale-applications': {
        'task': 'admissions.flag_stale_applications',
        'schedule': crontab(hour=8, minute=0),  # Every day at 8am
    },
}
