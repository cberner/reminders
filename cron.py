import datetime


def check_cron(schedule: str, current: datetime.datetime) -> bool:
    """
    Check if a cron schedule should run at the given time.
    
    Args:
        schedule: A cron schedule string in the format "{minute} {hour} {day of month} {month of year} {day of week}"
                 - Each field can be a number, *, comma-separated values (e.g., "1,2,3"), or */n
                 - Day of week field only accepts three-letter abbreviations (e.g., "MON", "TUE") or *
        current: The datetime to check against the schedule
        
    Returns:
        True if the schedule should run at the given time, False otherwise
    """
    current = current.replace(second=0, microsecond=0)
    parts = schedule.split()
    if len(parts) != 5:
        raise ValueError(f"Invalid cron schedule: {schedule}. Expected 5 parts.")
    
    minute, hour, day_of_month, month, day_of_week = parts
    
    if not _check_field(minute, current.minute, 0, 59):
        return False
    
    if not _check_field(hour, current.hour, 0, 23):
        return False
    
    if not _check_field(day_of_month, current.day, 1, 31):
        return False
    
    if not _check_field(month, current.month, 1, 12):
        return False
    
    if day_of_week == '*':
        pass  # Wildcard matches any day
    elif ',' in day_of_week:
        days = day_of_week.split(',')
        match_found = False
        for day in days:
            if day == '*':
                match_found = True
                break
            elif day.upper() in ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']:
                day_map = {
                    'MON': 0,
                    'TUE': 1,
                    'WED': 2,
                    'THU': 3,
                    'FRI': 4,
                    'SAT': 5,
                    'SUN': 6,
                }
                if current.weekday() == day_map[day.upper()]:
                    match_found = True
                    break
            else:
                try:
                    int(day)
                    raise ValueError(f"Day of week must be a three-letter abbreviation (MON, TUE, etc.), not a number: {day}")
                except ValueError as e:
                    if "Day of week must be" in str(e):
                        raise
                    raise ValueError(f"Invalid day of week: {day}. Must be a three-letter abbreviation (MON, TUE, etc.) or *")
        if not match_found:
            return False
    elif day_of_week.upper() in ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']:
        day_map = {
            'MON': 0,
            'TUE': 1,
            'WED': 2,
            'THU': 3,
            'FRI': 4,
            'SAT': 5,
            'SUN': 6,
        }
        if current.weekday() != day_map[day_of_week.upper()]:
            return False
    else:
        try:
            int(day_of_week)
            raise ValueError(f"Day of week must be a three-letter abbreviation (MON, TUE, etc.), not a number: {day_of_week}")
        except ValueError as e:
            if "Day of week must be" in str(e):
                raise
            raise ValueError(f"Invalid day of week: {day_of_week}. Must be a three-letter abbreviation (MON, TUE, etc.) or *")

    return True


def _check_field(field: str, current_value: int, min_value: int, max_value: int) -> bool:
    """
    Check if a field in the cron schedule matches the current value.
    
    Args:
        field: The field value from the cron schedule (can be a number or * or comma-separated values or */n)
        current_value: The current value to check against
        min_value: The minimum valid value for this field
        max_value: The maximum valid value for this field
        
    Returns:
        True if the field matches the current value, False otherwise
    """
    if field == '*':
        return True
    
    if ',' in field:
        values = field.split(',')
        for value in values:
            if _check_field(value, current_value, min_value, max_value):
                return True
        return False
    
    if field.startswith('*/'):
        try:
            divisor = int(field[2:])
            if divisor <= 0:
                raise ValueError(f"Divisor in {field} must be positive")
            return (current_value - min_value) % divisor == 0
        except ValueError as e:
            raise ValueError(f"Invalid slash notation: {field}. {str(e)}")
    
    try:
        field_value = int(field)
        if field_value < min_value or field_value > max_value:
            raise ValueError(f"Field value {field_value} is outside valid range {min_value}-{max_value}")
        return field_value == current_value
    except ValueError:
        raise ValueError(f"Invalid field value: {field}. Expected a number or *.")
