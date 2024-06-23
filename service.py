from db import DatabaseConnection
import json
import datetime
from multipropietarios import MultipropietariosManager
import math
from datetime import datetime
import io
from itertools import cycle
from variables_globales import ALLOWED

from http_errors import HTTP_BAD_REQUEST, HTTP_OK

class RegisterManager:
    def __init__(self):
        self.database = DatabaseConnection()
        self.cursor = self.database.connect()

    def post_register_to_db(self, tipo_escritura, comuna, manzana, predio, enajenante, adquiriente, fojas, fecha, nmro_inscripcion):
        try:
            serialized_enajenante = json.dumps(enajenante)
            serialized_adquiriente = json.dumps(adquiriente)
            
            string_sql = (
                f"INSERT INTO Registros (CNE, Comuna, Manzana, Predio, "
                f"Enajenantes, Adquirentes, Fojas, Fecha_Inscripcion, "
                f"Numero_Inscripcion) VALUES "
                f"('{tipo_escritura}', '{comuna}', '{manzana}', '{predio}', "
                f"'{serialized_enajenante}', '{serialized_adquiriente}', "
                f"'{fojas}', '{fecha}', '{nmro_inscripcion}')"
            )
            
            # self.cursor.execute(string_sql)
            # self.database.commit()

            register = {"F2890": [{"CNE": int(tipo_escritura),"bienRaiz": {"comuna": comuna,"manzana": manzana,"predio": predio},
                        "adquirentes": adquiriente, "enajenantes": enajenante,
                        "fojas": fojas,"fechaInscripcion": fecha,"nroInscripcion": nmro_inscripcion}]}

            json_str = json.dumps(register)
            file_object = io.StringIO(json_str)
            self.process_json(file_object)

            return HTTP_OK
        
        except Exception as e:
            print("Ocurrio un error:", e)
            return HTTP_BAD_REQUEST

    def get_all_registers(self):
        string_sql = 'SELECT * FROM Registros'
        self.cursor.execute(string_sql)
        registers = self.cursor.fetchall()
        return registers

    def get_register_by_id(self, id: int):
        string_sql = f'SELECT * FROM Registros WHERE N_Atencion = {id}'
        self.cursor.execute(string_sql)
        register = self.cursor.fetchone()
        return register
    
    def get_multiprop(self, comuna, manzana, predio):
        string_sql = f'SELECT * FROM Multipropietarios WHERE Comuna = {comuna} AND Manzana = {manzana} AND Predio = {predio}'
        self.cursor.execute(string_sql)
        multipropietarios = self.cursor.fetchall()
        return multipropietarios
    
    def filter_by_date(self, multipropietarios, fecha):
        multipropietarios_filtrados = []
        for multipropietario in multipropietarios:
            año = int(fecha)
            año_inicial = multipropietario['Ano_Vigencia_Inicial']
            año_final = multipropietario['Ano_Vigencia_Final']

            if año_final == None:
                if año_inicial <= año:
                    multipropietarios_filtrados.append(multipropietario)
            else:
                if año_inicial <= año <= año_final:
                    multipropietarios_filtrados.append(multipropietario)
    
    def process_json(self, file_object):   
        try:
            file = file_object.read()
            all_registers = json.loads(file)
            all_registers = self.order_json(all_registers)

            errors = []

            for register in all_registers["F2890"]:
                cne = register["CNE"]
                comuna = register["bienRaiz"]["comuna"]
                manzana = register["bienRaiz"]["manzana"]
                predio = register["bienRaiz"]["predio"]

                enajenantes = json.dumps(register.get("enajenantes", []))
                adquirentes = json.dumps(register.get("adquirentes", []))
                fojas = register["fojas"]
                fecha = register["fechaInscripcion"]
                nmro_inscripcion = register["nroInscripcion"]

                if not all(isinstance(val, (int, str)) for val in [cne, comuna, manzana, predio, enajenantes, adquirentes, fojas, fecha, nmro_inscripcion]):
                    errors.append(register)
                    continue

                self.push_register(cne,comuna,manzana,predio,enajenantes,adquirentes,fojas,fecha,nmro_inscripcion)
                mmgr = MultipropietariosManager()
                mmgr.add_multipropietarios(register)

            return errors

        except Exception as e:
            print("Ocurrio un error: ", e)
            return HTTP_BAD_REQUEST
        
    def push_register(self,cne,comuna,manzana,predio,enajenantes,adquirentes,fojas,fecha,nmro_inscripcion):
        string_sql = (
            f"INSERT INTO Registros (CNE, Comuna, Manzana, Predio, "
            f"Enajenantes, Adquirentes, Fojas, Fecha_Inscripcion, "
            f"Numero_Inscripcion) VALUES "
            f"('{cne}', '{comuna}', '{manzana}', '{predio}', "
            f"'{enajenantes}', '{adquirentes}', '{fojas}', "
            f"'{fecha}', '{nmro_inscripcion}')"
        )
        self.cursor.execute(string_sql)
        self.database.commit()
        
    def order_json(self, jsonfile):
        data = jsonfile["F2890"]
        data = sorted(data, key=lambda x: x["fechaInscripcion"])
        jsonfile["F2890"] = data
        return jsonfile

    def db_calculator(self, rut):
        reversed_digits = map(int, reversed(str(rut)))
        factors = cycle(range(2, 8))
        s = sum(d * f for d, f in zip(reversed_digits, factors))
        return (-s) % 11 if (-s) % 11 < 10 else 'K'
    
    def dv_checker(self, rut):
        rut = rut.upper()
        rut = rut.replace(".","")
        separated_rut = rut.split("-")
        print(separated_rut)
        db = str(self.db_calculator(separated_rut[0]))
        print(type(db), db, type(separated_rut[1]), separated_rut[1])
        if db == separated_rut[1]:
            return True
        else:
            return False
        
    def rut_checker(self, rut):
        return set(rut) <= ALLOWED