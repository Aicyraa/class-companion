import mysql.connector as sql
from mysql.connector import errorcode
from utils.settings import Settings 
class Checker:

    @staticmethod
    async def check_db(cursor, db):
        try:
            print("Checking DB!")
            cursor.execute(f"USE {db}")
        except sql.Error as err:
            if err.errno == errorcode.ER_DB_ACCESS_DENIED:
                print("Something is wrong with your DB!")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print(f"{db} does not exist!")
                Checker.create_db(cursor, db)
                print(f"{db} created!")
            else:
                print(f"Error ==> {err}")

    @staticmethod
    async def check_table(cursor):

        cursor.execute(f'use {Settings.db}')

        try:
            print('Checking Table!')
            cursor.execute("SHOW TABLES LIKE 'schedules'")
            result = cursor.fetchone();
            if result:
                print('Table exist!')
            else:
                Checker.create_tb(cursor)
                print('table created!')
            
        except sql.Error as err:
                print(f"Error ==> {err}")

    @staticmethod
    def create_db(cursor, db: str):

        try:
            print('Creating DB!')
            cursor.execute(f"CREATE DATABASE {db}")
        except sql.Error as err:
            print(f"An error occured while creating the database! ==> {err}")

    @staticmethod
    def create_tb(cursor):

        
        try:
            print('Creating Table!')
            cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS `schedules` (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id BIGINT UNSIGNED NOT NULL,
                event_day ENUM('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday') NOT NULL,
                event VARCHAR(55) NOT NULL,
                time_of_event TIME NOT NULL
            ); ''')

        except sql.Error as err:
            print(f"An error occurred while creating the table! ==> {err}")
