from datetime import datetime
from py.models import User, DayRecord
from typing import List, Dict


def add_daily_record(user: User, force=False) -> User:
    now_str = datetime.now().strftime("%d.%m.%y %H:%M")

    
    if not user.days and force:
        new_day = DayRecord(
            date=now_str,
            money=user.money,
            north=user.north.copy(),
            lim=user.lim.copy(),
            bp_level=user.bp_level,
            bp_exp=user.bp_exp
        )
        user.days.append(new_day)
        return user

    
    if any(day.date == now_str for day in user.days):
        return user

    
    new_day = DayRecord(
        date=now_str,
        money=user.money,
        north=user.north.copy(),
        lim=user.lim.copy(),
        bp_level=user.bp_level,
        bp_exp=user.bp_exp
    )
    user.days.append(new_day)
    return user



def calculate_differences(days: List[DayRecord]) -> List[Dict]:
    differences = []
    for i in range(1, len(days)):
        prev = days[i-1]
        curr = days[i]
        diff = {
            "date_prev": prev.date,
            "date_curr": curr.date,
            "money": curr.money - prev.money,
            "bp_level": curr.bp_level - prev.bp_level,
            "bp_exp": curr.bp_exp - prev.bp_exp,
            "north": {},
            "lim": {},
            "money_prev": prev.money,
            "bp_level_prev": prev.bp_level,
            "bp_exp_prev": prev.bp_exp,
            "north_prev": prev.north.copy(),
            "lim_prev": prev.lim.copy(),
            "money_after": curr.money,
            "bp_level_after": curr.bp_level,
            "bp_exp_after": curr.bp_exp,
            "north_after": curr.north.copy(),
            "lim_after": curr.lim.copy()
        }
        for key in curr.north:
            val_diff = curr.north[key] - prev.north.get(key, 0)
            if val_diff != 0:
                diff["north"][key] = val_diff
        for key in curr.lim:
            val_diff = curr.lim[key] - prev.lim.get(key, 0)
            if val_diff != 0:
                diff["lim"][key] = val_diff
        differences.append(diff)
    return differences
