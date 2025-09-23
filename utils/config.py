import os
import mysql.connector as sql
from dotenv import load_dotenv
load_dotenv()

class Settings:

    config = { 
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD')
    }

    @staticmethod
    def connection():
        return sql.connect(**Settings.config)

    token = os.getenv('TOKEN') 
    db = os.getenv('DB_NAME')