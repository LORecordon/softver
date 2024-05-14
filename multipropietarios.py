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
            print("No hay historia")
            for adquirente in data["adquirentes"]:
                temp_multipropietario = {
                    "Comuna": data["bienRaiz"]["comuna"],
                    "Manzana": data["bienRaiz"]["manzana"],
                    "Predio": data["bienRaiz"]["predio"],
                    "Fecha_Inscripcion": data["fechaInscripcion"],
                    "Ano_Inscripcion": int(data["fechaInscripcion"][0:4]),
                    "Fojas": data["fojas"],
                    "Numero_Inscripcion": data["nroInscripcion"],
                    "RUN_RUT": adquirente["RUNRUT"],
                    "Porcentaje_Derechos": adquirente["porcDerecho"],
                    "Ano_Vigencia_Inicial": data["fechaInscripcion"][0:4]
                }
                self.push_multipropietario(temp_multipropietario)

        else:
            print("Hay historia")
            ano_inscripcion_existente = historia[0]["Ano_Inscripcion"]
            ano_inscripcion_nueva = data["fechaInscripcion"][0:4]

            #LLEGA FORMULAIRO POSTERIOR
            if int(ano_inscripcion_existente) < int(ano_inscripcion_nueva):
                print("Formulario posterior")
                
                if int(ano_inscripcion_nueva) == int(ano_inscripcion_existente):
                    ano_vigencia_final = int(ano_inscripcion_nueva)
                else:
                    ano_vigencia_final = int(ano_inscripcion_nueva) - 1

                for propietario in historia:
                    self.update_multipropietario(propietario["id"], {"Ano_Vigencia_Final": ano_vigencia_final})

                for adquirente in data["adquirentes"]:
                    temp_multiproprietario = {
                        "Comuna": data["bienRaiz"]["comuna"],
                        "Manzana": data["bienRaiz"]["manzana"],
                        "Predio": data["bienRaiz"]["predio"],
                        "Fecha_Inscripcion": data["fechaInscripcion"],
                        "Ano_Inscripcion": int(data["fechaInscripcion"][0:4]),
                        "Fojas": data["fojas"],
                        "Numero_Inscripcion": data["nroInscripcion"],
                        "RUN_RUT": adquirente["RUNRUT"],
                        "Porcentaje_Derechos": i["porcDerecho"],
                        "Ano_Vigencia_Inicial": data["fechaInscripcion"][0:4]
                    }
                    self.push_multipropietario(temp_multiproprietario)
            

            #LLEGA FORMULARIO PREVIO
            elif int(ano_inscripcion_existente) > int(ano_inscripcion_nueva):
                print("Formulario previo")
                for adquirente in data["adquirentes"]:
                    temp_multiproprietario = {
                        "Comuna": data["bienRaiz"]["comuna"],
                        "Manzana": data["bienRaiz"]["manzana"],
                        "Predio": data["bienRaiz"]["predio"],
                        "Fecha_Inscripcion": data["fechaInscripcion"],
                        "Ano_Inscripcion": int(data["fechaInscripcion"][0:4]),
                        "Fojas": data["fojas"],
                        "Numero_Inscripcion": data["nroInscripcion"],
                        "RUN_RUT": adquirente["RUNRUT"],
                        "Porcentaje_Derechos": adquirente["porcDerecho"],
                        "Ano_Vigencia_Inicial": data["fechaInscripcion"][0:4],
                        "Ano_Vigencia_Final": data(ano_inscripcion_existente) - 1
                    }
                    self.push_multipropietario(temp_multiproprietario)

            elif int(ano_inscripcion_existente) == int(ano_inscripcion_nueva):
                print("Formulario Mismo año")
                for propietario in historia:
                    self.delete_multipropietario(propietario["id"])

                for adquirente in data['adquirentes']:
                    temp_multiproprietario = {
                        "Comuna": data["bienRaiz"]["comuna"],
                        "Manzana": data["bienRaiz"]["manzana"],
                        "Predio": data["bienRaiz"]["predio"],
                        "Fecha_Inscripcion": data["fechaInscripcion"],
                        "Ano_Inscripcion": int(data["fechaInscripcion"][0:4]),
                        "Fojas": data["fojas"],
                        "Numero_Inscripcion": data["nroInscripcion"],
                        "RUN_RUT": adquirente["RUNRUT"],
                        "Porcentaje_Derechos": adquirente["porcDerecho"],
                        "Ano_Vigencia_Inicial": data["fechaInscripcion"][0:4]
                    }
                    self.push_multipropietario(temp_multiproprietario)

    def add_multipropietarios_8(self, data):
        try:
            nro_enajenantes = len(data['enajenantes'])
        except KeyError:
            return False
        
        nro_adquirentes = len(data['adquirentes'])
        sum_derechos_adquirentes = 0
        for adquirente in data['adquirentes']:
            sum_derechos_adquirentes += int(adquirente['porcDerecho'])

        print("Suma de derechos adquirentes: ", sum_derechos_adquirentes)

        #ESCENARIO 1
        if sum_derechos_adquirentes == 100:
            print("escenario 1")
            enajenantes_historicos = self.get_history(data["bienRaiz"]["comuna"], data["bienRaiz"]["manzana"], data["bienRaiz"]["predio"])
            for enajenante_nuevo in data['enajenantes']:
                found = False
                for enajenante_historico in enajenantes_historicos:
                    if enajenante_nuevo['RUNRUT'] == enajenante_historico['RUN_RUT']:
                        found = True
                        break

                if not found:
                    print("enajenante no encontrado")
                    return False
            
            for enajenante_historico in enajenantes_historicos:
                if int(enajenante_historico["Ano_Inscripcion"]) == int(data["fechaInscripcion"][0:4]):
                    self.delete_multipropietario(enajenante_historico["id"])
                else:
                    self.update_multipropietario(enajenante_historico["id"], {"Ano_Vigencia_Final": int(data["fechaInscripcion"][0:4]) - 1})
        
            derecho_cedido = 0
            omitir = [] 
            for enajenante_nuevo in data['enajenantes']:
                for enajenante_historico in enajenantes_historicos:
                    if enajenante_nuevo['RUNRUT'] == enajenante_historico['RUN_RUT']:
                        derecho_cedido += int(enajenante_historico['Porcentaje_Derechos'])
                        omitir.append(enajenante_historico['RUN_RUT'])
                        enajenante_historico['Ano_Vigencia_Final'] = int(data['fechaInscripcion'][0:4]) - 1
                        break
            
            for adquirente in data['adquirentes']:
                temp_multiproprietario = {
                    "Comuna": data["bienRaiz"]["comuna"],
                    "Manzana": data["bienRaiz"]["manzana"],
                    "Predio": data["bienRaiz"]["predio"],
                    "Fecha_Inscripcion": data["fechaInscripcion"],
                    "Ano_Inscripcion": int(data["fechaInscripcion"][0:4]),
                    "Fojas": data["fojas"],
                    "Numero_Inscripcion": data["nroInscripcion"],
                    "RUN_RUT": adquirente["RUNRUT"],
                    "Porcentaje_Derechos": (int(adquirente["porcDerecho"]) * derecho_cedido) / 100,
                    "Ano_Vigencia_Inicial": data["fechaInscripcion"][0:4]
                }
                self.push_multipropietario(temp_multiproprietario)

            for enajenante_historico in enajenantes_historicos:
                if enajenante_historico['RUN_RUT'] not in omitir:
                    temp_multiproprietario = {
                        "Comuna": enajenante_historico["Comuna"],
                        "Manzana": enajenante_historico["Manzana"],
                        "Predio": enajenante_historico["Predio"],
                        "Fecha_Inscripcion": enajenante_historico["Fecha_Inscripcion"],
                        "Ano_Inscripcion": enajenante_historico["Ano_Inscripcion"],
                        "Fojas": enajenante_historico["Fojas"],
                        "Numero_Inscripcion": enajenante_historico["Numero_Inscripcion"],
                        "RUN_RUT": enajenante_historico["RUN_RUT"],
                        "Porcentaje_Derechos": enajenante_historico["Porcentaje_Derechos"],
                        "Ano_Vigencia_Inicial": data["fechaInscripcion"][0:4]
                    }
                    self.push_multipropietario(temp_multiproprietario)

        #ESCENARIO 2
        elif sum_derechos_adquirentes == 0 and (nro_adquirentes > 1 or nro_enajenantes > 1):
            print("escenario 2")
            enajenantes_historicos = self.get_history(data["bienRaiz"]["comuna"], data["bienRaiz"]["manzana"], data["bienRaiz"]["predio"])
            
            for enajenante_nuevo in data['enajenantes']:
                found = False
                for enajenante_historico in enajenantes_historicos:
                    if enajenante_nuevo['RUNRUT'] == enajenante_historico['RUN_RUT']:
                        found = True
                        break

                if not found:
                    print("enajenante no encontrado")
                    return False

            for enajenante_historico in enajenantes_historicos:
                if int(enajenante_historico["Ano_Inscripcion"]) == int(data["fechaInscripcion"][0:4]):
                    self.delete_multipropietario(enajenante_historico["id"])
                else:
                    self.update_multipropietario(enajenante_historico["id"], {"Ano_Vigencia_Final": int(data["fechaInscripcion"][0:4]) - 1})

            derecho_cedido = 0
            omitir = []
            for enajenante_nuevo in data['enajenantes']:
                for enajenante_historico in enajenantes_historicos:
                    if enajenante_nuevo['RUNRUT'] == enajenante_historico['RUN_RUT']:
                        derecho_cedido += int(enajenante_historico['Porcentaje_Derechos'])
                        omitir.append(enajenante_historico['RUN_RUT'])
                        enajenante_historico['Ano_Vigencia_Final'] = int(data['fechaInscripcion'][0:4]) - 1
                        break
            
            for adquirente in data['adquirentes']:
                temp_multiproprietario = {
                    "Comuna": data["bienRaiz"]["comuna"],
                    "Manzana": data["bienRaiz"]["manzana"],
                    "Predio": data["bienRaiz"]["predio"],
                    "Fecha_Inscripcion": data["fechaInscripcion"],
                    "Ano_Inscripcion": int(data["fechaInscripcion"][0:4]),
                    "Fojas": data["fojas"],
                    "Numero_Inscripcion": data["nroInscripcion"],
                    "RUN_RUT": adquirente["RUNRUT"],
                    "Porcentaje_Derechos": derecho_cedido/nro_adquirentes,
                    "Ano_Vigencia_Inicial": data["fechaInscripcion"][0:4]
                }
                self.push_multipropietario(temp_multiproprietario)

            for enajenante_historico in enajenantes_historicos:
                if enajenante_historico['RUN_RUT'] not in omitir:
                    temp_multiproprietario = {
                        "Comuna": enajenante_historico["Comuna"],
                        "Manzana": enajenante_historico["Manzana"],
                        "Predio": enajenante_historico["Predio"],
                        "Fecha_Inscripcion": enajenante_historico["Fecha_Inscripcion"],
                        "Ano_Inscripcion": enajenante_historico["Ano_Inscripcion"],
                        "Fojas": enajenante_historico["Fojas"],
                        "Numero_Inscripcion": enajenante_historico["Numero_Inscripcion"],
                        "RUN_RUT": enajenante_historico["RUN_RUT"],
                        "Porcentaje_Derechos": enajenante_historico["Porcentaje_Derechos"],
                        "Ano_Vigencia_Inicial": data["fechaInscripcion"][0:4]
                    }
                    self.push_multipropietario(temp_multiproprietario)

        #ESCENARIO 3
        elif nro_adquirentes == 1 and nro_enajenantes == 1 and (0 < sum_derechos_adquirentes < 100):
            print("escenario 3")
            enajenantes_historicos = self.get_history(data["bienRaiz"]["comuna"], data["bienRaiz"]["manzana"], data["bienRaiz"]["predio"])
            enajenantes_historicos = self.get_vigentes(enajenantes_historicos)
            derecho_cedido = 0
            rut_enajenante = ''
            for enajenante_nuevo in data['enajenantes']:
                found = False
                for enajenante_historico in enajenantes_historicos:
                    if enajenante_nuevo['RUNRUT'] == enajenante_historico['RUN_RUT']:
                        found = True
                        rut_enajenante = enajenante_nuevo['RUNRUT']
                        derecho_cedido = (int(enajenante_historico['Porcentaje_Derechos']) * int(enajenante_nuevo['porcDerecho'])) / 100
                        break

                if not found:
                    print("enajenante no encontrado")
                    return False

            for enajenante_historico in enajenantes_historicos:
                if int(enajenante_historico["Ano_Vigencia_Inicial"]) == int(data["fechaInscripcion"][0:4]):
                    self.delete_multipropietario(enajenante_historico["id"])
                else:
                    self.update_multipropietario(enajenante_historico["id"], {"Ano_Vigencia_Final": int(data["fechaInscripcion"][0:4]) - 1})

            for enajenante_nuevo in data['adquirentes']:
                temp_multipropietario = {
                    "Comuna": data["bienRaiz"]["comuna"],
                    "Manzana": data["bienRaiz"]["manzana"],
                    "Predio": data["bienRaiz"]["predio"],
                    "Fecha_Inscripcion": data["fechaInscripcion"],
                    "Ano_Inscripcion": int(data["fechaInscripcion"][0:4]),
                    "Fojas": data["fojas"],
                    "Numero_Inscripcion": data["nroInscripcion"],
                    "RUN_RUT": enajenante_nuevo["RUNRUT"],
                    "Porcentaje_Derechos": derecho_cedido,
                    "Ano_Vigencia_Inicial": data["fechaInscripcion"][0:4]
                }
                self.push_multipropietario(temp_multipropietario)

            for enajenante_historico in enajenantes_historicos:
                if enajenante_historico['RUN_RUT'] == rut_enajenante:
                    nuevo_derecho = int(enajenante_historico['Porcentaje_Derechos']) - derecho_cedido
                    if nuevo_derecho == 0:
                        continue

                    if int(enajenante_historico["Ano_Inscripcion"]) == int(data["fechaInscripcion"][0:4]):
                        temp_multipropietario = {
                            "Comuna": enajenante_historico["Comuna"],
                            "Manzana": enajenante_historico["Manzana"],
                            "Predio": enajenante_historico["Predio"],
                            "Fecha_Inscripcion": enajenante_historico["Fecha_Inscripcion"],
                            "Ano_Inscripcion": enajenante_historico["Ano_Inscripcion"],
                            "Fojas": enajenante_historico["Fojas"],
                            "Numero_Inscripcion": enajenante_historico["Numero_Inscripcion"],
                            "RUN_RUT": enajenante_historico["RUN_RUT"],
                            "Porcentaje_Derechos": nuevo_derecho,
                            "Ano_Vigencia_Inicial": data["fechaInscripcion"][0:4]
                        }
                        self.push_multipropietario(temp_multipropietario)
                    else:
                        temp_multipropietario = {
                            "Comuna": enajenante_historico["Comuna"],
                            "Manzana": enajenante_historico["Manzana"],
                            "Predio": enajenante_historico["Predio"],
                            "Fecha_Inscripcion": data["fechaInscripcion"],
                            "Ano_Inscripcion": data["fechaInscripcion"][0:4],
                            "Fojas": enajenante_historico["Fojas"],
                            "Numero_Inscripcion": enajenante_historico["Numero_Inscripcion"],
                            "RUN_RUT": enajenante_historico["RUN_RUT"],
                            "Porcentaje_Derechos": nuevo_derecho,
                            "Ano_Vigencia_Inicial": data["fechaInscripcion"][0:4]
                        }
                        self.push_multipropietario(temp_multipropietario)
                else:
                    temp_multipropietario = {
                        "Comuna": enajenante_historico["Comuna"],
                        "Manzana": enajenante_historico["Manzana"],
                        "Predio": enajenante_historico["Predio"],
                        "Fecha_Inscripcion": enajenante_historico["Fecha_Inscripcion"],
                        "Ano_Inscripcion": enajenante_historico["Ano_Inscripcion"],
                        "Fojas": enajenante_historico["Fojas"],
                        "Numero_Inscripcion": enajenante_historico["Numero_Inscripcion"],
                        "RUN_RUT": enajenante_historico["RUN_RUT"],
                        "Porcentaje_Derechos": enajenante_historico['Porcentaje_Derechos'],
                        "Ano_Vigencia_Inicial": data["fechaInscripcion"][0:4]
                    }
                    self.push_multipropietario(temp_multipropietario)

        #ESCENARIO 4
        else:
            print("escenario 4")
            enajenantes_historicos = self.get_history(data["bienRaiz"]["comuna"], data["bienRaiz"]["manzana"], data["bienRaiz"]["predio"])
            rut_derecho_cedido = {}

            for enajenante_nuevo in data['enajenantes']:
                found = False
                for enajenante_historico in enajenantes_historicos:
                    if enajenante_nuevo['RUNRUT'] == enajenante_historico['RUN_RUT']:
                        found = True
                        rut_derecho_cedido[enajenante_nuevo['RUNRUT']] = int(enajenante_nuevo['porcDerecho'])
                        break

                if not found:
                    print("enajenante no encontrado")
                    return False


            for enajenante_historico in enajenantes_historicos:
                if int(enajenante_historico["Ano_Inscripcion"]) == int(data["fechaInscripcion"][0:4]):
                    self.delete_multipropietario(enajenante_historico["id"])
                else:
                    self.update_multipropietario(enajenante_historico["id"], {"Ano_Vigencia_Final": int(data["fechaInscripcion"][0:4]) - 1})

            for adquirente in data['adquirentes']:
                temp_multipropietario = {
                    "Comuna": data["bienRaiz"]["comuna"],
                    "Manzana": data["bienRaiz"]["manzana"],
                    "Predio": data["bienRaiz"]["predio"],
                    "Fecha_Inscripcion": data["fechaInscripcion"],
                    "Ano_Inscripcion": int(data["fechaInscripcion"][0:4]),
                    "Fojas": data["fojas"],
                    "Numero_Inscripcion": data["nroInscripcion"],
                    "RUN_RUT": adquirente["RUNRUT"],
                    "Porcentaje_Derechos": adquirente["porcDerecho"],
                    "Ano_Vigencia_Inicial": data["fechaInscripcion"][0:4]
                }
                self.push_multipropietario(temp_multipropietario)


            for enajenante_historico in enajenantes_historicos:
                if enajenante_historico['RUN_RUT'] in rut_derecho_cedido.keys():
                    print(f"actual: {int(enajenante_historico['Porcentaje_Derechos'])}")
                    nuevo_derecho = int(enajenante_historico['Porcentaje_Derechos']) - rut_derecho_cedido[enajenante_historico['RUN_RUT']]
                    print(f"nuevo: {nuevo_derecho}")
                    if nuevo_derecho == 0:
                        continue

                    if int(enajenante_historico["Ano_Inscripcion"]) == int(data["fechaInscripcion"][0:4]):
                        temp_multipropietario = {
                            "Comuna": enajenante_historico["Comuna"],
                            "Manzana": enajenante_historico["Manzana"],
                            "Predio": enajenante_historico["Predio"],
                            "Fecha_Inscripcion": enajenante_historico["Fecha_Inscripcion"],
                            "Ano_Inscripcion": enajenante_historico["Ano_Inscripcion"],
                            "Fojas": enajenante_historico["Fojas"],
                            "Numero_Inscripcion": enajenante_historico["Numero_Inscripcion"],
                            "RUN_RUT": enajenante_historico["RUN_RUT"],
                            "Porcentaje_Derechos": nuevo_derecho,
                            "Ano_Vigencia_Inicial": data["fechaInscripcion"][0:4]
                        }
                        self.push_multipropietario(temp_multipropietario)
                    else:
                        temp_multipropietario = {
                            "Comuna": enajenante_historico["Comuna"],
                            "Manzana": enajenante_historico["Manzana"],
                            "Predio": enajenante_historico["Predio"],
                            "Fecha_Inscripcion": data["fechaInscripcion"],
                            "Ano_Inscripcion": data["fechaInscripcion"][0:4],
                            "Fojas": enajenante_historico["Fojas"],
                            "Numero_Inscripcion": enajenante_historico["Numero_Inscripcion"],
                            "RUN_RUT": enajenante_historico["RUN_RUT"],
                            "Porcentaje_Derechos": nuevo_derecho,
                            "Ano_Vigencia_Inicial": data["fechaInscripcion"][0:4]
                        }
                        self.push_multipropietario(temp_multipropietario)
                else:
                    temp_multipropietario = {
                        "Comuna": enajenante_historico["Comuna"],
                        "Manzana": enajenante_historico["Manzana"],
                        "Predio": enajenante_historico["Predio"],
                        "Fecha_Inscripcion": enajenante_historico["Fecha_Inscripcion"],
                        "Ano_Inscripcion": enajenante_historico["Ano_Inscripcion"],
                        "Fojas": enajenante_historico["Fojas"],
                        "Numero_Inscripcion": enajenante_historico["Numero_Inscripcion"],
                        "RUN_RUT": enajenante_historico["RUN_RUT"],
                        "Porcentaje_Derechos": enajenante_historico['Porcentaje_Derechos'],
                        "Ano_Vigencia_Inicial": data["fechaInscripcion"][0:4]
                    }
                    self.push_multipropietario(temp_multipropietario)


    def add_multipropietarios(self, data):
        print("Processing multipropietarios: ", data)


        tipoEscritura = data["CNE"]
        if tipoEscritura == 99:
            self.add_multipropietarios_99(data)
        elif tipoEscritura == 8:
            self.add_multipropietarios_8(data)

    def get_history(self, comuna, manzana, predio):
        string_sql = f'SELECT * FROM Multipropietarios WHERE Comuna = {comuna} AND Manzana = {manzana} AND Predio = {predio}'
        self.cursor.execute(string_sql)
        history = self.cursor.fetchall()
        return history
    
    def get_vigentes(self, multiprops):
        vigentes = []
        for m in multiprops:
            if m["Ano_Vigencia_Final"] == None:
                vigentes.append(m)
        return vigentes
    
    def get_multipropietario(self, comuna, manzana, predio, rut):
        string_sql = f'SELECT * FROM Multipropietarios WHERE Comuna = {comuna} AND Manzana = {manzana} AND Predio = {predio} AND RUN_RUT = {rut}'
        self.cursor.execute(string_sql)
        multiprop = self.cursor.fetchall()
        return multiprop

    def push_multipropietario(self, multiprop):
        columnas = ", ".join(list(multiprop.keys()))
        valores = ", ".join(list(map(str, list(multiprop.values()))))
        
        strings = ['Fecha_Inscripcion', 'RUN_RUT']
        for string in strings:
            valores = valores.replace(f"{multiprop[string]}", f"'{multiprop[string]}'")

        string_sql = f"INSERT INTO Multipropietarios ({columnas}) VALUES ({valores})"
        print("Executing: ", string_sql)
        self.cursor.execute(string_sql)
        self.database.commit()

    
    def update_multipropietario(self, row_id, multiprop):
        print("Updating: ", row_id, multiprop)
        strings = ['Fecha_Inscripcion', 'RUN_RUT']
        for string in strings:
            if string in multiprop:
                multiprop[string] = f"'{multiprop[string]}'"
                                                               
        string_sql = f"UPDATE Multipropietarios SET " + ", ".join([f"{k} = {v}" for k, v in multiprop.items()]) + f" WHERE id = {row_id}"
        self.cursor.execute(string_sql)
        self.database.commit()


    def delete_multipropietario(self, row_id):
        string_sql = f"DELETE FROM Multipropietarios WHERE id = {row_id}"
        print("Executing: ", string_sql)
        self.cursor.execute(string_sql)
        self.database.commit()

    


