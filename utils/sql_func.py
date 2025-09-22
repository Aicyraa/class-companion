import mysql.connector as sql
from utils.settings import Settings

class Query:
    @staticmethod
    def insert(ctx, args: tuple):

        cnx = Settings.connection()
        cursor = cnx.cursor()
        uniqueID = ctx.author.id
        day, event, time = args

        try:
            cursor.execute(f'USE {Settings.db}')
            cursor.execute('SELECT * FROM user WHERE user_discord_id = %s', (uniqueID,))
            if not cursor.fetchone():
                print('success?')
                cursor.execute('INSERT INTO user (user_discord_id) VALUES (%s)', (uniqueID, ))
                cnx.commit()

            cursor.execute('''
                    INSERT INTO schedules (user_discord_id, event_day, event, event_time)
                    VALUES (%s, %s, %s, %s ); ''', (uniqueID, day, event, time))
            cnx.commit()
            print('success???')

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
