from db import DatabaseConnection


class MultipropietariosManager:
    def __init__(self):
        self.database = DatabaseConnection()
        self.cursor = self.database.connect()


    def add_multipropietarios_99(self, json):
        historia = self.get_history(json["bienRaiz"]["comuna"], json["bienRaiz"]["manzana"], json["bienRaiz"]["predio"])

        #NO HAY HISTORIA
        if len(historia) == 0:
            for i in json["adquirentes"]:
                temp_multiprop = {
                    "Comuna": json["bienRaiz"]["comuna"],
                    "Manzana": json["bienRaiz"]["manzana"],
                    "Predio": json["bienRaiz"]["predio"],
                    "Fecha_Inscripcion": json["fechaInscripcion"],
                    "Ano": json["fechaInscripcion"][0:4],
                    "Fojas": json["fojas"],
                    "Numero_Inscripcion": json["nroInscripcion"],
                    "RUN_RUT": i["RUNRUT"],
                    "Porcentaje_Derechos": i["porcDerecho"],
                    "Ano_Vigencia_Inicial": json["fechaInscripcion"][0:4]
                }
                self.push_multipropietario(temp_multiprop)

        else:
            ano_inscripcion_existente = historia[0]["Ano_Inscripcion"]
            ano_inscripcion_nueva = json["fechaInscripcion"][0:4]

            #LLEGA FORMULAIRO POSTERIOR
            if int(ano_inscripcion_existente) < int(ano_inscripcion_nueva):
                
                #actualizar vigencia de los anteriores
                ano_vigencia_final = int(ano_inscripcion_nueva) - 1
                for i in historia:
                    self.update_multipropietario(i["id"], {"Ano_Vigencia_Final": ano_vigencia_final})

                #agregar nuevos
                for i in json["adquirentes"]:
                    temp_multiprop = {
                        "Comuna": json["bienRaiz"]["comuna"],
                        "Manzana": json["bienRaiz"]["manzana"],
                        "Predio": json["bienRaiz"]["predio"],
                        "Fecha_Inscripcion": json["fechaInscripcion"],
                        "Ano": json["fechaInscripcion"][0:4],
                        "Fojas": json["fojas"],
                        "Numero_Inscripcion": json["nroInscripcion"],
                        "RUN_RUT": i["RUNRUT"],
                        "Porcentaje_Derechos": i["porcDerecho"],
                        "Ano_Vigencia_Inicial": json["fechaInscripcion"][0:4]
                    }
                    self.push_multipropietario(temp_multiprop)
            

            #LLEGA FORMULARIO PREVIO
            elif int(ano_inscripcion_existente) > int(ano_inscripcion_nueva):
                for i in json["adquirentes"]:
                    temp_multiprop = {
                        "Comuna": json["bienRaiz"]["comuna"],
                        "Manzana": json["bienRaiz"]["manzana"],
                        "Predio": json["bienRaiz"]["predio"],
                        "Fecha_Inscripcion": json["fechaInscripcion"],
                        "Ano": json["fechaInscripcion"][0:4],
                        "Fojas": json["fojas"],
                        "Numero_Inscripcion": json["nroInscripcion"],
                        "RUN_RUT": i["RUNRUT"],
                        "Porcentaje_Derechos": i["porcDerecho"],
                        "Ano_Vigencia_Inicial": json["fechaInscripcion"][0:4],
                        "Ano_Vigencia_Final": int(ano_inscripcion_existente) - 1
                    }
                    self.push_multipropietario(temp_multiprop)


    def add_multipropietarios_8(self, json):
        pass


    def add_multipropietarios(self, json):
        tipoEscritura = json["CNE"]
        if tipoEscritura == 99:
            self.add_multipropietarios_99(json)
        elif tipoEscritura == 8:
            self.add_multipropietarios_8(json)

    def get_history(self, comuna, manzana, predio):
        string_sql = f'SELECT * FROM Multipropietarios WHERE Comuna = {comuna} AND Manzana = {manzana} AND Predio = {predio}'
        self.cursor.execute(string_sql)
        history = self.cursor.fetchall()
        return history

    def push_multipropietario(self, multiprop):
        columnas = ", ".join(list(multiprop.keys()))
        valores = ", ".join(list(map(str, list(multiprop.values()))))

        string_sql = f"INSERT INTO Multipropietarios ({columnas}) VALUES ({valores})"

        print(string_sql)

    
    def update_multipropietario(self, row_id, multiprop):

        string_sql = f"UPDATE Multipropietarios SET " + ", ".join([f"{k} = {v}" for k, v in multiprop.items()]) + f" WHERE id = {row_id}"
        print(string_sql)

    


