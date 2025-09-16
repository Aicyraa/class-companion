import mysql.connector as sql
from mysql.connector import errorcode

class Sql:
    
    @staticmethod
    async def check_db(cursor, db):
        try:
            print('Trying!')
            cursor.execute(f'USE {db}')
        except sql.Error as err:
            if err.errno == errorcode.ER_DB_ACCESS_DENIED:
                print('Something is wrong with your DB!')
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print(f'{db} does not exist!')
                Sql.create_db(cursor, db)
                print(f'{db} created!')
            else:
                print(f'Error ==> {err}')   
    
    @staticmethod
    def create_db(cursor, db: str):
        try:
            cursor.execute(f'CREATE DATABASE {db}')
        except sql.Error as err:
            print(f'An error occured while creating the database! ==> {err}')

    @staticmethod
    def create_tb(cursor, db: str):
        pass            