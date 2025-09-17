import mysql.connector as sql
from mysql.connector import errorcode

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
    async def check_table(cursor, tb):
        try:
            cursor.execute("SELECT {tb}")
        except sql.Error as err:
            if err.errno == errorcode.ER_NO_SUCH_TABLE:
                Checker.create_tb(cursor, tb)
            else:
                print(f"Error ==> {err}")

    @staticmethod
    def create_db(cursor, db: str):
        try:
            cursor.execute(f"CREATE DATABASE {db}")
        except sql.Error as err:
            print(f"An error occured while creating the database! ==> {err}")

    @staticmethod
    def create_tb(cursor, tb: str):
        try:
            cursor.execute("CREATE TABLE {tb}")
        except sql.Error as err:
            print(f"An error occured while creating the database! ==> {err}")
