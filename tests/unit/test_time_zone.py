from datetime import datetime
import pytz
from tzlocal import get_localzone


def show_time_conversion(destination_timezone="America/New_York"):
    """
    Demonstrate timezone conversion from local time to destination timezone
    """
    # 1. Get local timezone
    local_timezone = get_localzone()

    # 2. Get current local time (timezone-naive)
    local_time_naive = datetime.now()

    # 3. Make the local time timezone-aware
    local_time = local_time_naive.replace(tzinfo=local_timezone)

    # 4. Get destination timezone object
    dest_timezone = pytz.timezone(destination_timezone)

    # 5. Convert to destination timezone
    dest_time = local_time.astimezone(dest_timezone)

    # 6. Format and display results
    print(f"Local timezone: {local_timezone}")
    print(f"Current local time: {local_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(
        f"Time in {destination_timezone}: {dest_time.strftime('%Y-%m-%d %H:%M:%S %Z')}"
    )
    print(
        f"Time difference: {(dest_time.utcoffset() - local_time.utcoffset()).total_seconds() / 3600:.1f} hours"
    )


# Example usage
show_time_conversion("America/New_York")
