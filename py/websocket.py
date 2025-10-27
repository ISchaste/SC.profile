from fastapi import WebSocket, WebSocketDisconnect
from py.auth import load_user, save_user, sessions
from py.utils import add_daily_record
from datetime import datetime

def calculate_today_changes(user):
    today_str = datetime.now().strftime("%d.%m.%y %H:%M")
    today_changes = {}
    if user.days:
        last_day = user.days[-1]
        if last_day.date[:8] == today_str[:8]:
            if user.money != last_day.money:
                today_changes["Деньги"] = user.money - last_day.money
            if user.bp_level != last_day.bp_level:
                today_changes["BP уровень"] = user.bp_level - last_day.bp_level
            if user.bp_exp != last_day.bp_exp:
                today_changes["BP опыт"] = user.bp_exp - last_day.bp_exp
            for k, v in user.north.items():
                if v != last_day.north.get(k, 0):
                    today_changes[k] = v - last_day.north.get(k, 0)
            for k, v in user.lim.items():
                if v != last_day.lim.get(k, 0):
                    today_changes[k] = v - last_day.lim.get(k, 0)
    return today_changes

async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    
    session_id = websocket.cookies.get("session_id")
    if not session_id or session_id not in sessions:
        await websocket.close(code=403)
        return

    login = sessions[session_id]
    user = load_user(login)
    if user:
        await websocket.send_json({
            **user.model_dump(),
            "today_changes": calculate_today_changes(user)
        })

    try:
        while True:
            data = await websocket.receive_json()
            user = load_user(login)
            if not user:
                await websocket.close()
                return

            today_changes = {}

            for key in ["money", "bp_level", "bp_exp"]:
                old_val = getattr(user, key)
                new_val = data.get(key, old_val)
                if new_val != old_val:
                    setattr(user, key, new_val)
                    today_changes[key] = new_val - old_val

            for category in ["north", "lim"]:
                if category in data:
                    for item, value in data[category].items():
                        old_val = getattr(user, category).get(item, 0)
                        if value != old_val:
                            getattr(user, category)[item] = value
                            today_changes[f"{category}_{item}"] = value - old_val

            if today_changes:
                user = add_daily_record(user)
                save_user(user)

            await websocket.send_json({
                **user.model_dump(),
                "today_changes": today_changes
            })

    except WebSocketDisconnect:
        pass
