import mysql.connector as sql
from datetime import datetime
from utils.config import Settings

class Query:

    @staticmethod
    def insert_schedule(ctx, args: tuple):

        cnx = Settings.connection()
        cursor = cnx.cursor()
        uniqueID = ctx.author.id
        day, event, tFormat = args
        time = datetime.strptime(tFormat, "%I%p").time() 
    
        try:
            cursor.execute(f'USE {Settings.db}')
            cursor.execute('SELECT * FROM user WHERE user_discord_id = %s', (uniqueID,))
            if not cursor.fetchone():
                cursor.execute('INSERT INTO user (user_discord_id) VALUES (%s)', (uniqueID, ))
                cnx.commit()

            cursor.execute('''
                    INSERT INTO schedules (user_discord_id, event_day, event, event_time)
                    VALUES (%s, %s, %s, %s ); ''', (uniqueID, day, event, time))
            cnx.commit()

        except sql.Error as err:
            print(f'Error while inserting data! ==> {err}')
        finally:
            cursor.close()
            cnx.close()
    
    @staticmethod
    def fetch():
        pass

    @staticmethod
    def edit():
        pass

    @staticmethod
    def delete():
        pass

    @staticmethod
    def insert_activity(guild_id, event, expiry):
        
        cnx = Settings.connection()
        cursor = cnx.cursor()

        cursor.execute(f'USE {Settings.db}')

        try:

            cursor.execute('''SELECT * FROM guilds WHERE guild_id = %s''', (guild_id, ))

            if not cursor.fetchone():
                cursor.execute('''INSERT INTO guilds (guild_id) VALUES (%s)''', (guild_id, ))
                cnx.commit()

            cursor.execute( """
                            INSERT INTO activities (guild_id, activity_details, expiry_date)
                            VALUES (%s, %s, %s) """, (guild_id, event, expiry.strftime("%Y-%m-%d %H:%M:%S")))
            cnx.commit()

        except sql.Error as err:
            print(f"Database Error: {err}")
        finally:
             cursor.close()
             cnx.close()
                        
