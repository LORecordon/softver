import mysql.connector

from dotenv import load_dotenv
import os

load_dotenv()

class DatabaseConnection:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            cls._instance.conn = mysql.connector.connect(
                        host=os.getenv('MYSQL_HOST'),
                        port=os.getenv('MYSQL_PORT'),
                        user=os.getenv('MYSQL_USER'),
                        password=os.getenv('MYSQL_PASSWORD'),
                        database=os.getenv('MYSQL_DATABASE')
                    )
        return cls._instance
    
    def connect(self):
        return self.conn.cursor(dictionary=True)
    
    def commit(self):
        return self.conn.commit()