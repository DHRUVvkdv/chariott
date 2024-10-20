from datetime import datetime
import pytz

est_tz = pytz.timezone("America/New_York")


def get_current_est_time():
    return datetime.now(est_tz)


def parse_est_datetime(dt_string: str) -> datetime:
    try:
        # Try parsing as ISO format with timezone info
        dt = datetime.fromisoformat(dt_string)
        if dt.tzinfo is None:
            # If parsed successfully but timezone is not set, assume EST
            dt = est_tz.localize(dt)
        else:
            # If timezone is set, convert to EST
            dt = dt.astimezone(est_tz)
    except ValueError:
        # If parsing fails, try parsing as naive datetime and assume EST
        dt = datetime.fromisoformat(dt_string)
        dt = est_tz.localize(dt)

    return dt


def format_est_datetime(dt: datetime) -> str:
    # Ensure the datetime is in EST
    est_dt = dt.astimezone(est_tz)

    # Format to ISO 8601 format with timezone info
    return est_dt.isoformat()
