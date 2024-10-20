# utils.py
from datetime import datetime
import pytz

est_tz = pytz.timezone("America/New_York")


def get_current_est_time():
    return datetime.now(est_tz)
