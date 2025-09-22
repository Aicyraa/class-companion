import mysql.connector as sql
from utils.settings import Settings

class Query:
    @staticmethod
    def insert(ctx, args):

        cnx = Settings.connection()
        cursor = cnx.cursor()

        try:
            cursor.execute(f'''
            INSERT INTO schedules (user_id, event_day, event, time_of_event)
            VALUES (%s, %s , %s ,%s); ''', (ctx.author.id, args[0], args[1], args[2]))
            Settings.connection()
        except sql.Error as err:
            print(f'Error ==> {err}')
        finally:
            cursor.close()

        print('Send!??')    
    
    @staticmethod
    def fetch():
        pass

    @staticmethod
    def edit():
        pass

    @staticmethod
    def delete():
        pass
