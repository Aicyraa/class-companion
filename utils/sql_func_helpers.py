import mysql.connector as sql
from datetime import datetime
from utils.config import Settings
from utils.sql_func_reminder import Reminder_Query as rq

class Query:

    @staticmethod
    def insert_schedule(author: int, args: tuple):

        cnx = Settings.connection()
        cursor = cnx.cursor()

        day, event, Tformat = args
        time = rq.convert_to_24(Tformat)
      
        try:
            cursor.execute(f'USE {Settings.db}')
            cursor.execute('SELECT * FROM user WHERE user_discord_id = %s', (author,))
            
            if not cursor.fetchone():
                cursor.execute('INSERT INTO user (user_discord_id) VALUES (%s)', (author, ))
                cnx.commit()

            cursor.execute(
                    '''
                    INSERT INTO schedules (user_discord_id, event_day, event, event_time)
                    VALUES (%s, %s, %s, %s ); 
                    ''', (author, day, event, time))
            
            cnx.commit()

        except sql.Error as err: print(f'Error while inserting data! ==> {err}')
        finally:
            cursor.close()
            cnx.close()
    
    @staticmethod
    def fetch(author: int):
        
        cnx = Settings.connection()
        cursor = cnx.cursor()
        
        result = {}
        
        try:
            cursor.execute(f'USE {Settings.db}')
            for day in ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'): 
    
                cursor.execute('SELECT event, event_time FROM schedules WHERE user_discord_id = %s and event_day = %s; ', (author, day))  
                qeury_result = cursor.fetchall()

                if not qeury_result:
                    continue
                
                schedule = [f'{str(sched[0])} {str(rq.convert_to_12(sched[1]))}' for sched in qeury_result]
                result[day] = schedule

            return result
             
        except sql.Error as err: print(f'Error occur while viewing shedule: {err}')
        finally:
            cursor.close()
            cnx.close()

    @staticmethod
    def edit(author: int, old, new):
        
        cnx =  Settings.connection()
        cursor = cnx.cursor()
        
        try:
            cursor.execute(f'USE {Settings.db}')
            cursor.execute(
                '''
                UPDATE schedules
                SET event_day = %s, event = %s, event_time = %s
                WHERE event_day = %s AND event = %s AND event_time = %s AND user_discord_id = %s; 
                ''', (new[0], new[1], rq.convert_to_24(new[2]), old[0], old[1], rq.convert_to_24(old[2]), author))
            
            cnx.commit()
            return True
            
        except sql.Error as err: print(f'Error occur while updating the schedule: {err}')
        finally:
            cursor.close()
            cnx.close()
        

    @staticmethod
    def delete(author: int, day, event, time):
        
        cnx = Settings.connection()
        cursor = cnx.cursor()
        
        try:
            cursor.execute(f'USE {Settings.db}')
            cursor.execute('SELECT  FROM schedules WHERE user_discord_id = %s AND event_day = %s AND event = %s AND event_time = %s; ''', (author, day, event, time))
            if cursor.fetchone():
                cursor.execute('''DELETE FROM schedules WHERE user_discord_id = %s AND event_day = %s AND event = %s AND event_time = %s; ''', (author, day, event, time))
                cnx.commit()
                return True
        
        except sql.Error as err: print(f'Error occur deleting the schedule: {err}')
        finally:
            cursor.close()
            cnx.close()
            
    @staticmethod
    def insert_activity(guild_id: int, event, expiry):
        
        cnx = Settings.connection()
        cursor = cnx.cursor()
        
        try:
            cursor.execute(f'USE {Settings.db}')
            cursor.execute('''SELECT * FROM guilds WHERE guild_id = %s''', (guild_id, ))
            if not cursor.fetchone():
                cursor.execute('''INSERT INTO guilds (guild_id) VALUES (%s)''', (guild_id, ))
                cnx.commit()

            cursor.execute(
                """
                INSERT INTO activities (guild_id, activity_details, expiry_date)
                VALUES (%s, %s, %s) 
                """, (guild_id, event, expiry.strftime("%Y-%m-%d %H:%M:%S")))
            
            cnx.commit()

        except sql.Error as err: print(f"Error occur while inserting activies: {err}")
        finally:
             cursor.close()
             cnx.close()
                        
