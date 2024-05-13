from db import DatabaseConnection
import json
import datetime
from multipropietarios import MultipropietariosManager


from http_errors import HTTP_BAD_REQUEST, HTTP_OK

class RegisterManager:
    def __init__(self):
        self.database = DatabaseConnection()
        self.cursor = self.database.connect()
    #values = numeroAtencion, tipoEscritura, comuna, manzana, predio, enajenante, adquirente, fojas, fecha, nmroInscripcion
    def post_register_to_db(self, tipoEscritura, comuna, manzana, predio, enajenante, adquiriente, fojas, fecha, nmroInscripcion):
        try:
            serializedEnajenante = json.dumps(enajenante)
            serializedAdquirente = json.dumps(adquiriente)
            
            string_sql = f"INSERT INTO Registros (CNE, Comuna, Manzana, Predio, Enajenantes, Adquirentes, Fojas, Fecha_Inscripcion, Numero_Inscripcion) VALUES ('{tipoEscritura}', '{comuna}', '{manzana}', '{predio}', '{serializedEnajenante}', '{serializedAdquirente}', '{fojas}', '{fecha}', '{nmroInscripcion}')"
            self.cursor.execute(string_sql)
            self.database.commit()

            return HTTP_OK
        except Exception as e:
            print("Ocurrio un error: ",e)
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
        multiprop = self.cursor.fetchall()
        print(multiprop)
        multiprops = []
        for i in multiprop:
            anoSplit = int(fecha)
            fechaInscripcion = i['Fecha_Inscripcion']
            year = fechaInscripcion.year
            anoVigenciaFinal = i['Ano_Vigencia_Final']
            if anoVigenciaFinal != None:
                if year < anoSplit and anoVigenciaFinal > anoSplit:
                    multiprops.append(i)
            else:
                anoVigenciaInicial = i['Ano_Vigencia_Inicial']
                if anoVigenciaInicial != None:
                    if year <= anoSplit and anoVigenciaInicial >= anoSplit:
                        multiprops.append(i)
                else:
                    if year <= anoSplit:
                        multiprops.append(i)

        return multiprops
    
    def process_json(self, file_object):   
        try:
            file = file_object.read()
            all_registers = json.loads(file)
            errors = []
            for register in all_registers["F2890"]:
                cne = register["CNE"]
                comuna = register["bienRaiz"]["comuna"]
                manzana = register["bienRaiz"]["manzana"]
                predio = register["bienRaiz"]["predio"]
                if "enajenantes" in register.keys():
                    enajenantes = json.dumps(register["enajenantes"])
                    enan = register["enajenantes"]
                else:
                    enajenantes = json.dumps([])
                    enan = []
                if "adquirentes" in register.keys():
                    adquirentes = json.dumps(register["adquirentes"])
                    registeredAdquirentes = register["adquirentes"]
                else:
                    adquirentes = json.dumps([])
                    registeredAdquirentes = []
                fojas = register["fojas"]
                fecha = register["fechaInscripcion"]
                nmroInscripcion = register["nroInscripcion"]
                
                if type(cne) != int or type(comuna) != int or type(manzana) != int or type(predio) != int or type(enajenantes) != str or type(adquirentes) != str or type(fojas) != int or type(fecha) != str or type(nmroInscripcion) != int:

                    errors.append(register)
                    continue
                

                #month = int(fecha.split('-')[1])
                #day = int(fecha.split('-')[2])
                #if month > 12 or month < 1 or day < 1 or day > 31:
                #    errors.append(register)
                #    continue

                string_sql = f"INSERT INTO Registros (CNE, Comuna, Manzana, Predio, Enajenantes, Adquirentes, Fojas, Fecha_Inscripcion, Numero_Inscripcion) VALUES ('{cne}', '{comuna}', '{manzana}', '{predio}', '{enajenantes}', '{adquirentes}', '{fojas}', '{fecha}', '{nmroInscripcion}')"
                self.cursor.execute(string_sql)
                self.database.commit()

                mmgr = MultipropietariosManager()
                mmgr.add_multipropietarios(register)

                

            return errors
                

        except Exception as e:
            print("Ocurrio un error: ",e)
            return HTTP_BAD_REQUEST
    
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