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

        today = datetime.now(Reminder_Query.ph_time).strftime("%A")
        
        result = {}
        
        try:
            cursor.execute(f'USE {Settings.db}')
            cursor.execute('SELECT user_discord_id FROM user')
            
            for (user,) in cursor.fetchall():
                storage = []
                cursor.execute(
                    """
                    SELECT schedules.event, schedules.event_time FROM schedules
                    INNER JOIN user
                    ON schedules.user_discord_id = user.user_discord_id
                    WHERE schedules.user_discord_id = %s
                    AND schedules.event_day = %s; """, (user, today))
                
                for *details, time in list(cursor.fetchall()):
                    details.append(tc.convert_to_12(time))
                    print('details => ', details)
                    storage.append(details)
                
                print('storage => ', storage)
                if not storage: # prevents from sending notification if there is no schedule
                    continue
                
                result[user] = storage # added event to result dict

        except sql.Error as err: print(f'Error occur while fetching schedule: {err}')
        finally:
            cursor.close()
            cnx.close()

        print('result => ', result)
        return result
    
    @staticmethod
    def activity_remind():

        cnx = Settings.connection()
        cursor = cnx.cursor()
        
        result = {}   
        
        try:
            cursor.execute(f'USE {Settings.db}')
            cursor.execute('SELECT guild_id FROM guilds')
            
            for (guild_id,) in cursor.fetchall():
                storage = []
                cursor.execute(
                    '''
                    SELECT activities.activity_details, activities.expiry_date FROM activities
                    INNER JOIN guilds
                    ON activities.guild_id = guilds.guild_id
                    WHERE activities.guild_id = %s; ''', (guild_id, ))
            
                for event in cursor.fetchall():
                    storage.append(event)

                if not storage:
                    continue
                
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

        try: 
            cursor.execute(f'''USE {Settings.db}''')
            cursor.execute('''DELETE FROM activities WHERE expiry_date <= NOW(); ''')
            cnx.commit()
        except sql.Error as err: print(f'Error occur while deleting {err}')
        finally:
            cursor.close()
            cnx.close()

    # for time convertion
    
   