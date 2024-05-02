from db import DatabaseConnection
import json

class MultipropietariosManager:
    def __init__(self):
        self.database = DatabaseConnection()
        self.cursor = self.database.connect()


    def add_multipropietarios_99(self, data):
        historia = self.get_history(data["bienRaiz"]["comuna"], data["bienRaiz"]["manzana"], data["bienRaiz"]["predio"])

        #NO HAY HISTORIA
        if len(historia) == 0:
            for i in data["adquirentes"]:
                temp_multiprop = {
                    "Comuna": data["bienRaiz"]["comuna"],
                    "Manzana": data["bienRaiz"]["manzana"],
                    "Predio": data["bienRaiz"]["predio"],
                    "Fecha_Inscripcion": data["fechaInscripcion"],
                    "Ano": data["fechaInscripcion"][0:4],
                    "Fojas": data["fojas"],
                    "Numero_Inscripcion": data["nroInscripcion"],
                    "RUN_RUT": i["RUNRUT"],
                    "Porcentaje_Derechos": i["porcDerecho"],
                    "Ano_Vigencia_Inicial": data["fechaInscripcion"][0:4]
                }
                self.push_multipropietario(temp_multiprop)

        else:
            ano_inscripcion_existente = historia[0]["Ano_Inscripcion"]
            ano_inscripcion_nueva = data["fechaInscripcion"][0:4]

            #LLEGA FORMULAIRO POSTERIOR
            if int(ano_inscripcion_existente) < int(ano_inscripcion_nueva):
                
                #actualizar vigencia de los anteriores
                ano_vigencia_final = int(ano_inscripcion_nueva) - 1
                for i in historia:
                    self.update_multipropietario(i["id"], {"Ano_Vigencia_Final": ano_vigencia_final})

                #agregar nuevos
                for i in data["adquirentes"]:
                    temp_multiprop = {
                        "Comuna": data["bienRaiz"]["comuna"],
                        "Manzana": data["bienRaiz"]["manzana"],
                        "Predio": data["bienRaiz"]["predio"],
                        "Fecha_Inscripcion": data["fechaInscripcion"],
                        "Ano": data["fechaInscripcion"][0:4],
                        "Fojas": data["fojas"],
                        "Numero_Inscripcion": data["nroInscripcion"],
                        "RUN_RUT": i["RUNRUT"],
                        "Porcentaje_Derechos": i["porcDerecho"],
                        "Ano_Vigencia_Inicial": data["fechaInscripcion"][0:4]
                    }
                    self.push_multipropietario(temp_multiprop)
            

            #LLEGA FORMULARIO PREVIO
            elif int(ano_inscripcion_existente) > int(ano_inscripcion_nueva):
                for i in data["adquirentes"]:
                    temp_multiprop = {
                        "Comuna": data["bienRaiz"]["comuna"],
                        "Manzana": data["bienRaiz"]["manzana"],
                        "Predio": data["bienRaiz"]["predio"],
                        "Fecha_Inscripcion": data["fechaInscripcion"],
                        "Ano": data["fechaInscripcion"][0:4],
                        "Fojas": data["fojas"],
                        "Numero_Inscripcion": data["nroInscripcion"],
                        "RUN_RUT": i["RUNRUT"],
                        "Porcentaje_Derechos": i["porcDerecho"],
                        "Ano_Vigencia_Inicial": data["fechaInscripcion"][0:4],
                        "Ano_Vigencia_Final": data(ano_inscripcion_existente) - 1
                    }
                    self.push_multipropietario(temp_multiprop)


    def add_multipropietarios_8(self, data):
        try:
            nro_enajenantes = len(data['enajenantes'])
        except KeyError:
            return False
        nro_adquirentes = len(data['adquirentes'])
        sum_derechos_adquirentes = 0
        for i in data['adquirentes']:
            sum_derechos_adquirentes += int(i['porcDerecho'])


        #ESCENARIO 1
        if sum_derechos_adquirentes == 100:
            enajenantes = self.get_history(data["bienRaiz"]["comuna"], data["bienRaiz"]["manzana"], data["bienRaiz"]["predio"])
            
            for i in data['enajenantes']:
                found = False
                for j in enajenantes:
                    if i['RUNRUT'] == j['RUN_RUT']:
                        found = True
                        break
                if not found:
                    print("enajenante no encontrado")
                    return False

            for i in enajenantes:
                self.update_multipropietario(i["id"], {"Ano_Vigencia_Final": int(data["fechaInscripcion"][0:4]) - 1})


            derecho_cedido = 0
            omitir = []
            for i in data['enajenantes']:
                for j in enajenantes:
                    if i['RUNRUT'] == j['RUN_RUT']:
                        derecho_cedido += int(j['Porcentaje_Derechos'])
                        omitir.append(j['RUN_RUT'])
                        j['Ano_Vigencia_Final'] = int(data['fechaInscripcion'][0:4]) - 1
                        break
            
            for i in data['adquirentes']:
                temp_multiprop = {
                    "Comuna": data["bienRaiz"]["comuna"],
                    "Manzana": data["bienRaiz"]["manzana"],
                    "Predio": data["bienRaiz"]["predio"],
                    "Fecha_Inscripcion": data["fechaInscripcion"],
                    "Ano": data["fechaInscripcion"][0:4],
                    "Fojas": data["fojas"],
                    "Numero_Inscripcion": data["nroInscripcion"],
                    "RUN_RUT": i["RUNRUT"],
                    "Porcentaje_Derechos": (int(i["porcDerecho"]) * derecho_cedido) / 100,
                    "Ano_Vigencia_Inicial": data["fechaInscripcion"][0:4]
                }
                self.push_multipropietario(temp_multiprop)

            for i in enajenantes:
                if i['RUN_RUT'] not in omitir:
                    temp_multiprop = {
                        "Comuna": i["Comuna"],
                        "Manzana": i["Manzana"],
                        "Predio": i["Predio"],
                        "Fecha_Inscripcion": data["fechaInscripcion"],
                        "Ano": data["fechaInscripcion"][0:4],
                        "Fojas": i["Fojas"],
                        "Numero_Inscripcion": data["nroInscripcion"],
                        "RUN_RUT": i["RUN_RUT"],
                        "Porcentaje_Derechos": i["Porcentaje_Derechos"],
                        "Ano_Vigencia_Inicial": data["fechaInscripcion"][0:4]
                    }
                    self.push_multipropietario(temp_multiprop)
            

            




        #ESCENARIO 2
        elif sum_derechos_adquirentes == 0:
            enajenantes = self.get_history(data["bienRaiz"]["comuna"], data["bienRaiz"]["manzana"], data["bienRaiz"]["predio"])
            
            for i in data['enajenantes']:
                found = False
                for j in enajenantes:
                    if i['RUNRUT'] == j['RUN_RUT']:
                        found = True
                        break
                if not found:
                    print("enajenante no encontrado")
                    return False

            for i in enajenantes:
                self.update_multipropietario(i["id"], {"Ano_Vigencia_Final": int(data["fechaInscripcion"][0:4]) - 1})


            derecho_cedido = 0
            omitir = []
            for i in data['enajenantes']:
                for j in enajenantes:
                    if i['RUNRUT'] == j['RUN_RUT']:
                        derecho_cedido += int(j['Porcentaje_Derechos'])
                        omitir.append(j['RUN_RUT'])
                        j['Ano_Vigencia_Final'] = int(data['fechaInscripcion'][0:4]) - 1
                        break
            
            for i in data['adquirentes']:
                temp_multiprop = {
                    "Comuna": data["bienRaiz"]["comuna"],
                    "Manzana": data["bienRaiz"]["manzana"],
                    "Predio": data["bienRaiz"]["predio"],
                    "Fecha_Inscripcion": data["fechaInscripcion"],
                    "Ano": data["fechaInscripcion"][0:4],
                    "Fojas": data["fojas"],
                    "Numero_Inscripcion": data["nroInscripcion"],
                    "RUN_RUT": i["RUNRUT"],
                    "Porcentaje_Derechos": derecho_cedido/nro_adquirentes,
                    "Ano_Vigencia_Inicial": data["fechaInscripcion"][0:4]
                }
                self.push_multipropietario(temp_multiprop)

            for i in enajenantes:
                if i['RUN_RUT'] not in omitir:
                    temp_multiprop = {
                        "Comuna": i["Comuna"],
                        "Manzana": i["Manzana"],
                        "Predio": i["Predio"],
                        "Fecha_Inscripcion": data["fechaInscripcion"],
                        "Ano": data["fechaInscripcion"][0:4],
                        "Fojas": i["Fojas"],
                        "Numero_Inscripcion": data["nroInscripcion"],
                        "RUN_RUT": i["RUN_RUT"],
                        "Porcentaje_Derechos": i["Porcentaje_Derechos"],
                        "Ano_Vigencia_Inicial": data["fechaInscripcion"][0:4]
                    }
                    self.push_multipropietario(temp_multiprop)

        #ESCENARIO 3
        if nro_adquirentes == 1 and nro_enajenantes == 1:
            print("escenario 3")
            pass

        #ESCENARIO 4
        else:
            print("escenario 4")
            pass



    def add_multipropietarios(self, data):
        tipoEscritura = data["CNE"]
        if tipoEscritura == 99:
            pass
            #self.add_multipropietarios_99(data)
        elif tipoEscritura == 8:
            self.add_multipropietarios_8(data)

    def get_history(self, comuna, manzana, predio):
        string_sql = f'SELECT * FROM Multipropietarios WHERE Comuna = {comuna} AND Manzana = {manzana} AND Predio = {predio}'
        self.cursor.execute(string_sql)
        history = self.cursor.fetchall()
        return history
    
    def get_multipropietario(self, comuna, manzana, predio, rut):
        string_sql = f'SELECT * FROM Multipropietarios WHERE Comuna = {comuna} AND Manzana = {manzana} AND Predio = {predio} AND RUN_RUT = {rut}'
        print(string_sql)
        self.cursor.execute(string_sql)
        multiprop = self.cursor.fetchall()
        return multiprop

    def push_multipropietario(self, multiprop):
        columnas = ", ".join(list(multiprop.keys()))
        valores = ", ".join(list(map(str, list(multiprop.values()))))

        string_sql = f"INSERT INTO Multipropietarios ({columnas}) VALUES ({valores})"

        print(string_sql)

    
    def update_multipropietario(self, row_id, multiprop):

        string_sql = f"UPDATE Multipropietarios SET " + ", ".join([f"{k} = {v}" for k, v in multiprop.items()]) + f" WHERE id = {row_id}"
        print(string_sql)

    


