from db import DatabaseConnection
import json
import datetime
from multipropietarios import MultipropietariosManager
import math
from datetime import datetime
import io

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
    
    def get_multiprop(self, comuna, manzana, predio, fecha):
        string_sql = f'SELECT * FROM Multipropietarios WHERE Comuna = {comuna} AND Manzana = {manzana} AND Predio = {predio}'
        self.cursor.execute(string_sql)
        multipropietarios = self.cursor.fetchall()
        print(multipropietarios)
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

        return multipropietarios_filtrados
    
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

                mmgr = MultipropietariosManager()
                mmgr.add_multipropietarios(register)

            return errors

        except Exception as e:
            print("Ocurrio un error: ", e)
            return HTTP_BAD_REQUEST
        
    def order_json(self, jsonfile):
        data = jsonfile["F2890"]
        data = sorted(data, key=lambda x: x["fechaInscripcion"])
        jsonfile["F2890"] = data
        return jsonfile
 
    
    def pprocess_json(self, file_object):
        try:
            file = file_object.read()
            all_registers = json.loads(file)
            string_sql = 'INSERT INTO Registros (texto, numero) VALUES '
            for register in all_registers:
                string_sql += f"('{register['texto']}', {register['numero']}),"

            string_sql = string_sql[:-1]
            self.cursor.execute(string_sql)
            self.database.commit()

            return HTTP_OK
        
        except Exception as e:
            print("Ocurrio un error: ",e)
            return HTTP_BAD_REQUEST