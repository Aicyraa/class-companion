import mysql.connector as sql
import pytz
from utils.config import Settings
from datetime import datetime


class Reminder_Query:

    ph_time = pytz.timezone('Asia/Manila')

    @staticmethod
    def midnight_remind():

        result = {}
        cnx = Settings.connection()
        cursor = cnx.cursor()
        cursor.execute(f"USE {Settings.db}")
        cursor.execute("SELECT user_discord_id FROM user")
        today = datetime.now(Reminder_Query.ph_time).strftime("%A")

        for user in cursor.fetchall():
            print(today)
            user_id = user[0]
            storage = []
            cursor.execute(
                """
                SELECT schedules.event, schedules.event_time FROM schedules
                INNER JOIN user
                ON schedules.user_discord_id = user.user_discord_id
                WHERE schedules.user_discord_id = %s
                AND schedules.event_day = %s;""",
                (user_id, today)
            )


            for schedules in list(cursor.fetchall()):
                schedules = list(schedules)
                time = Reminder_Query.process_time(schedules.pop(-1))
                schedules.append(time)
                storage.append(schedules)
                
            result[user_id] = storage   
    
        return result

    @staticmethod
    def process_time(time):
        total_seconds = int(time.total_seconds())
        hours_24, remainder = divmod(total_seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        hours_12 = hours_24 % 12 or 12   # ensures always positive, converts correctly
        ampm = "AM" if hours_24 < 12 else "PM"
        fixed_format = f"{hours_12:02d}:{minutes:02d} {ampm}"
        return fixed_format
