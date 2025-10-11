import mysql.connector as sql
import pytz
from utils.config import Settings
from datetime import datetime
from utils.time_converter import Time_Converter as tc

class Reminder_Query:

    ph_time = pytz.timezone('Asia/Manila')

    @staticmethod
    def schedule_remind(): # function for fetching reminders

        cnx = Settings.connection()
        cursor = cnx.cursor()
        cursor.execute(f'USE {Settings.db}')

        cursor.execute('SELECT user_discord_id FROM user')
        result = {}
        today = datetime.now(Reminder_Query.ph_time).strftime("%A")
        
        try:
            for (user,) in cursor.fetchall():
                storage = []
                cursor.execute(
                    """
                    SELECT schedules.event, schedules.event_time FROM schedules
                    INNER JOIN user
                    ON schedules.user_discord_id = user.user_discord_id
                    WHERE schedules.user_discord_id = %s
                    AND schedules.event_day = %s; 
                    """, (user, today))

                user_schedule = list(cursor.fetchall())  
                
                if not user_schedule:
                    continue
                
                for details in user_schedule:
                    schedules = list(details) # convert details into list
                    time = tc.convert_to_12(schedules.pop(-1))

                    schedules.append(time)
                    storage.append(schedules)
                    
                result[user] = storage # added event to storage

        except sql.Error as err: print(f'Error occur while fetching schedule: {err}')
        finally:
            cursor.close()
            cnx.close()

        return result
    
    @staticmethod
    def activity_remind():

        cnx = Settings.connection()
        cursor = cnx.cursor()
        
        cursor.execute(f'USE {Settings.db}')
        cursor.execute('SELECT guild_id FROM guilds')

        result = {}   

        try:
            for (guild_id,) in cursor.fetchall(): 
                storage = []
                cursor.execute(
                    '''
                    SELECT activities.activity_details, activities.expiry_date FROM activities
                    INNER JOIN guilds
                    ON activities.guild_id = guilds.guild_id;
                    ''')
            
                for event in cursor.fetchall():
                    storage.append(event)

                result[guild_id] = storage # added event in result dict
            
        except sql.Error as err: print(f'Error occur while fetching activities: {err}')
        finally:
            cursor.close()
            cnx.close()

        return result

    @staticmethod
    def check_date():
        
        cnx = Settings.connection()
        cursor = cnx.cursor()

        cursor.execute(f'''USE {Settings.db}''')

        try: cursor.execute('''DELETE FROM activities WHERE expiry_date <= NOW(); ''')
        except sql.Error as err: print(f'Error occur while deleting {err}')
        finally:
            cursor.close()
            cnx.close()

    # for time convertion
    
   