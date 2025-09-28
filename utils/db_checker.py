import mysql.connector as sql
from mysql.connector import errorcode
from utils.config import Settings


class Checker:

    @staticmethod
    async def check_db(db):

        cnx = Settings.connection()
        cursor = cnx.cursor()

        try:
            cursor.execute(f"USE {db}")
        except sql.Error as err:
            if err.errno == errorcode.ER_DB_ACCESS_DENIED:
                print("Something is wrong with your DB!")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print(f"{db} does not exist!")
                Checker.create_db(cursor, db)
            else:
                print(f"Error ==> {err}")

    @staticmethod
    def create_db(cursor, db: str):

        try:
            cursor.execute(f"CREATE DATABASE {db}")
            print("DB created!")
        except sql.Error as err:
            print(f"An error occured while creating the database! ==> {err}")
        finally:
            cursor.close()

    @staticmethod
    async def check_table():

        cnx = Settings.connection()
        cursor = cnx.cursor()
        cursor.execute(f"use {Settings.db}")

        try:

            cursor.execute("SHOW TABLES")
            if not cursor.fetchall():
                print("Tables not exist!")
                Checker.create_tb(cursor)

        except sql.Error as err:
            print(f"Error ==> {err}")

    @staticmethod
    def create_tb(cursor):

        try:

            # for users
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS `user` (
                user_id INT AUTO_INCREMENT UNIQUE,
                user_discord_id BIGINT UNSIGNED PRIMARY KEY,
                registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP               
            ) """
            )

            # for guild table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXIST `guilds` (
                    id AUTO_INCREMENT UNIQUE,
                    guild_id BIGINT UNSIGNED PRIMARY KEY,
                    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP      
                )
            """
            )

            # for schedules
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS `schedules` (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_discord_id BIGINT UNSIGNED NOT NULL,
                event_day ENUM('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday') NOT NULL,
                event VARCHAR(55) NOT NULL,
                event_time TIME NOT NULL,
                           
                CONSTRAINT fk_parent FOREIGN KEY(user_discord_id) REFERENCES user(user_discord_id)
            ); """
            )

            # for activities
            cursor.execute(
                """ 
                CREATE TABLE IF NOT EXISTS `activities` (
                id AUTO_INCREMENT PRIMARY KEY,
                guild_id BIGINT UNSIGNED NOT NULL,
                activity_details VARCHAR(150) NOT NULL.
                expiry_date DATETIME NOT NULL
                
                CONSTAIN fk_parent FOREIGN KEY(guild_id) REFERENCES guilds(guild_id)
            ); """
            )

            print("Table created!")

        except sql.Error as err:
            print(f"An error occurred while creating the table! ==> {err}")
        finally:
            cursor.close()
