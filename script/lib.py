def parse_working_hours(whours):
    """
    Parse a working hours string in the format 'HH:MM-HH:MM' and return start and end as (h, m) tuples.
    """
    try:
        start_str, end_str = whours.split("-")
        start_h, start_m = map(int, start_str.strip().split(":"))
        end_h, end_m = map(int, end_str.strip().split(":"))
        return (start_h, start_m), (end_h, end_m)
    except Exception:
        print("Invalid --working-hours format. Use e.g. 8:00-16:30")
        import sys
        sys.exit(1)

def is_within_working_hours(dt, start_h, start_m, end_h, end_m):
    """
    Check if a datetime 'dt' is within the working hours defined by start_h, start_m, end_h, end_m.
    Handles overnight shifts (e.g. 22:00-06:00).
    """
    start = dt.replace(hour=start_h, minute=start_m, second=0, microsecond=0)
    end = dt.replace(hour=end_h, minute=end_m, second=0, microsecond=0)
    if end <= start:
        # Overnight shift (e.g. 22:00-06:00)
        return dt >= start or dt <= end
    else:
        return start <= dt <= end