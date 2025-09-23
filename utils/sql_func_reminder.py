import  mysql.connector as sql 
from utils.config import Settings
from  datetime import datetime

class Reminder_Query():

    @staticmethod
    def midnight_remind():

        cnx = Settings.connection()
        cursor = cnx.cursor()

        cursor.execute('SELECT user_discord_id FROM user')

        for user in cursor.fetchall():
            cursor.execute('''
                SELECT schedules.event_day, schedules.event, schedules.event_time FROM schedules
                INNER JOIN user
                ON schedules.user_discord_id REFERENCES user.user_discord_id
                WHERE schedules.user_discord_id = %s''', (user, ))

        return cursor.fetchall()