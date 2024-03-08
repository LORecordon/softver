from db import DatabaseConnection
import json

from http_errors import HTTP_BAD_REQUEST, HTTP_OK

class RegisterManager:
    def __init__(self):
        self.database = DatabaseConnection()
        self.cursor = self.database.connect()

    def post_register_to_db(self, name: str, num: int):
        try:
            string_sql = f"INSERT INTO registros (texto, numero) VALUES ('{name}', {num})"
            self.cursor.execute(string_sql)
            self.database.commit()
            return HTTP_OK
        except Exception as e:
            print("Ocurrio un error: " + e)
            return HTTP_BAD_REQUEST

    def get_all_registers(self):
        string_sql = 'SELECT * FROM registros'
        self.cursor.execute(string_sql)
        registers = self.cursor.fetchall()
        return registers

    def get_register_by_id(self, id: int):
        string_sql = f'SELECT * FROM registros WHERE id = {id}'
        self.cursor.execute(string_sql)
        register = self.cursor.fetchone()
        return register
    
    def process_json(self, file_object):
        try:
            file = file_object.read()
            all_registers = json.loads(file)
            string_sql = 'INSERT INTO registros (texto, numero) VALUES '
            for register in all_registers:
                string_sql += f"('{register['texto']}', {register['numero']}),"
            string_sql = string_sql[:-1]
            self.cursor.execute(string_sql)
            self.database.commit()
            return HTTP_OK
        except Exception as e:
            print("Ocurrio un error: " + e)
            return HTTP_BAD_REQUEST