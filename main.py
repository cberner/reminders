import base64
import datetime
import json
import os
from dateutil import parser
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from cron import check_cron


RETRY_TIMEOUT = 24*60*60


def check_ndays_schedule(start_date: datetime.date, event_date: datetime.date, frequency_days: int) -> bool:
    if event_date < start_date:
        return False

    if (event_date - start_date).days % frequency_days != 0:
        return False

    return True


def check_day_of_week(event_date: datetime.date, day_of_week: int) -> bool:
    return event_date.isoweekday() == day_of_week


def email_cloud_function(event, context):
    # Messages in pubsub are base64 encoded. Also support events with the keys directly in them, to make testing easier
    if 'data' in event:
        event = json.loads(base64.b64decode(event['data']).decode('utf-8'))
        results = []
        for reminder in event['reminders']:
            result = process_reminder(reminder, context)
            results.append(result)
        return results
    else:
        print("WARNING! received empty event")


def process_reminder(event, context):
    event_timestamp = parser.parse(context.timestamp)
    timezone = event.get('timezone')
    
    if timezone:
        import pytz
        if event_timestamp.tzinfo is not None:
            event_timestamp = event_timestamp.astimezone(pytz.timezone(timezone))
        else:
            event_timestamp = pytz.timezone('UTC').localize(event_timestamp)
            event_timestamp = event_timestamp.astimezone(pytz.timezone(timezone))
    
    normalized_timestamp = event_timestamp.replace(second=0, microsecond=0)
    event_date = normalized_timestamp.date()
    
    if 'cron_schedule' in event:
        cron_schedule = event['cron_schedule']
        if not check_cron(cron_schedule, normalized_timestamp.replace(tzinfo=None)):
            # for debugging
            # print(f"Skipping {event['subject']}: Schedule: {cron_schedule}. Now: {normalized_timestamp}")
            return "Skipped"
        else:
            # print(f"Sending {event['subject']}: Schedule: {cron_schedule}. Now: {normalized_timestamp}")
            pass

    if 'required_day_of_week' in event:
        if not check_day_of_week(event_date, event['required_day_of_week']):
            return "Skipped"

    if 'schedule' in event:
        schedule = event['schedule']
        assert schedule['unit'] == 'day'
        start_date = datetime.date.fromisoformat(schedule['start'])
        if not check_ndays_schedule(start_date, event_date, schedule['frequency']):
            return "Skipped"

    event_timestamp = parser.parse(context.timestamp)
    event_age = (datetime.datetime.now(datetime.timezone.utc) - event_timestamp).total_seconds()
    if event_age > RETRY_TIMEOUT:
        print('Dropped event {} ({}sec old)'.format(context.event_id, event_age))
        return 'Timeout'

    message = Mail(
        from_email=event['from'],
        to_emails=event['to'],
        subject=event['subject'],
        html_content=event['html_content'] or ' ')  # SendGrid does not support empty body

    client = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
    response = client.send(message)
    if response.status_code != 202:
        raise Exception("Sending email failed. Status code: {}".format(response.status_code))

    return "Done"
