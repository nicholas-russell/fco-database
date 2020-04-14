from datetime import date, timedelta
from math import ceil
from decimal import Decimal


def calc_new_volunteer_expiry(hours, current, members):
    added_days = ceil(Decimal(14/members) * hours)
    print(added_days)
    if current is None:
        return date.today() + timedelta(days=added_days)
    else:
        return current + timedelta(days=added_days)
