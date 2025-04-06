import datetime
import yaml
import sys
import re
from dateutil import parser
from croniter import croniter

from cron import check_cron

def parse_schedule(schedule: str) -> (str, dict, int):
    if schedule.startswith('starting'):
        match = re.match(r'starting\s+(?P<start>.+)\s+every\s+(?P<days>[0-9]{1,3})\s+days\s+at\s+(?P<hours>[0-9]{1,2}):(?P<minutes>[0-9]{2})', schedule)
        start = match.group('start')
        days = int(match.group('days'))
        hours = int(match.group('hours'))
        minutes = int(match.group('minutes'))

        start_date = parser.parse(start).date().isoformat()

        cron = f'{minutes} {hours} * * *'

        return cron, {'start': start_date, 'frequency': days, 'unit': 'day'}, None

    if schedule.startswith('on'):
        match = re.match(r'on\s+(?P<ordinal>[a-zA-Z1-5]+)\s+(?P<dayofweek>[a-zA-Z]{3,4})\s+in\s+(?P<month>[a-zA-Z]{3,4}|every month)\s+at\s+(?P<hours>[0-9]{1,2}):(?P<minutes>[0-9]{2})', schedule)
        ordinal = match.group('ordinal')
        day_of_week = match.group('dayofweek').lower()
        month = match.group('month')
        if month == "every month":
            month = "*"
        else:
            month = parser.parse(month).month
        hours = int(match.group('hours'))
        minutes = int(match.group('minutes'))

        if ordinal == '1st':
            day_range = '1-7'
        elif ordinal == '2nd':
            day_range = '8-14'
        elif ordinal == '3rd':
            day_range = '15-21'
        elif ordinal == '4th':
            day_range = '22-28'
        else:
            raise Exception("unsupported ordinal: " + ordinal)

        cron = f'{minutes} {hours} {day_range} {month} *'

        if day_of_week.startswith('mon'):
            day_of_week = 1
        elif day_of_week.startswith('tue'):
            day_of_week = 2
        elif day_of_week.startswith('wed'):
            day_of_week = 3
        elif day_of_week.startswith('thu'):
            day_of_week = 4
        elif day_of_week.startswith('fri'):
            day_of_week = 5
        elif day_of_week.startswith('sat'):
            day_of_week = 6
        elif day_of_week.startswith('sun'):
            day_of_week = 7
        else:
            raise Exception("unsupported day of week: " + day_of_week)

        return cron, {}, day_of_week

    return schedule, {}, None


def check_with_croniter(cron_schedule, current_time):
    """
    Replicates the logic in main.py that uses croniter.get_next() to determine if a reminder should run.
    
    Args:
        cron_schedule: A cron schedule string
        current_time: The datetime to check
        
    Returns:
        True if the schedule should run at the given time, False otherwise
    """
    normalized_time = current_time.replace(second=0, microsecond=0)
    cron_iter = croniter(cron_schedule, normalized_time - datetime.timedelta(minutes=1))
    next_execution = cron_iter.get_next(datetime.datetime)
    return normalized_time == next_execution


def main():
    try:
        with open('reminders.yaml', 'r') as f:
            config = yaml.safe_load(f)
            yaml_file = 'reminders.yaml'
    except FileNotFoundError:
        with open('example.yaml', 'r') as f:
            config = yaml.safe_load(f)
            yaml_file = 'example.yaml'
    
    print(f"Using schedules from {yaml_file}")
    
    schedules = []
    for recipient in config['recipients']:
        for reminder in recipient['reminders']:
            schedules.append(reminder['schedule'])
    
    cron_schedules = []
    for schedule in schedules:
        cron, extra_schedule, day_of_week = parse_schedule(schedule)
        cron_schedules.append((schedule, cron))
        print(f"Schedule: '{schedule}' => Cron: '{cron}'")
    
    start_date = datetime.datetime(2025, 1, 1, 0, 0)
    end_date = datetime.datetime(2025, 12, 31, 23, 59)
    current_date = start_date
    
    total_checks = 0
    total_discrepancies = 0
    
    while current_date <= end_date:
        for original_schedule, cron_schedule in cron_schedules:
            cron_result = check_cron(cron_schedule, current_date)
            croniter_result = check_with_croniter(cron_schedule, current_date)
            
            total_checks += 1
            if cron_result != croniter_result:
                total_discrepancies += 1
                print(f"Discrepancy found for '{original_schedule}' (cron: '{cron_schedule}') at {current_date}:")
                print(f"  cron.check_cron: {cron_result}")
                print(f"  croniter.get_next: {croniter_result}")
        
        current_date += datetime.timedelta(minutes=1)
    
    print(f"\nTotal checks performed: {total_checks}")
    print(f"Total discrepancies found: {total_discrepancies}")
    print(f"Discrepancy rate: {(total_discrepancies / total_checks) * 100:.4f}%")


if __name__ == '__main__':
    main()
