import datetime
import yaml
import sys
from dateutil import parser
from croniter import croniter

from cron import check_cron
from update_reminders import parse_schedule


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
