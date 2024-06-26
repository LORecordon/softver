from db import DatabaseConnection
import json
from variables_globales import CNE_COMPRAVENTA,CNE_REGULARIZACION_DEL_PATRIMONIO

class MultipropietariosManager:
    def __init__(self):
        self.database = DatabaseConnection()
        self.cursor = self.database.connect()

    def group_adquirentes(self, adquirentes):
        #group repeated adquirentes maintaining the format
        adquirentes_grouped = []
        for adquirente in adquirentes:
            found = False
            for adquirente_grouped in adquirentes_grouped:
                if adquirente['RUNRUT'] == adquirente_grouped['RUNRUT']:
                    adquirente_grouped['porcDerecho'] += adquirente['porcDerecho']
                    found = True
                    break
            if not found:
                adquirentes_grouped.append(adquirente)
        return adquirentes_grouped
    
    def recalculate_derechos(self, adquirentes):
        sum_derechos = 0
        for adquirente in adquirentes:
            sum_derechos += int(adquirente['porcDerecho'])

        if sum_derechos <= 100:
            return adquirentes
        
        for adquirente in adquirentes:
            adquirente['porcDerecho'] = (int(adquirente['porcDerecho']) * 100) / sum_derechos
        return adquirentes
    


    def add_multipropietarios_99(self, data):
        historia = self.get_history(data["bienRaiz"]["comuna"], data["bienRaiz"]["manzana"], data["bienRaiz"]["predio"])

        #group repeated adquirentes
        data['adquirentes'] = self.group_adquirentes(data['adquirentes'])

        #make derechos sum 100
        data['adquirentes'] = self.recalculate_derechos(data['adquirentes'])    


        #NO HAY HISTORIA
        if len(historia) == 0:
            self.process_no_history(data)

        else:
            print("Hay historia")
            ano_inscripcion_existente = historia[0]["Ano_Inscripcion"]
            ano_inscripcion_nueva = data["fechaInscripcion"][0:4]

            #LLEGA FORMULAIRO POSTERIOR
            if int(ano_inscripcion_existente) < int(ano_inscripcion_nueva):
                print("Formulario posterior")
                self.process_posterior_form(data, historia, ano_inscripcion_existente, ano_inscripcion_nueva)
            

            #LLEGA FORMULARIO PREVIO
            elif int(ano_inscripcion_existente) > int(ano_inscripcion_nueva):
                print("Formulario previo")
                self.process_prev_form(data, ano_inscripcion_existente)

            elif int(ano_inscripcion_existente) == int(ano_inscripcion_nueva):
                print("Formulario Mismo año")
                self.process_same_year(data, historia)

    def process_no_history(self, data):
        for i in data["adquirentes"]:
            temp_multipropietario = {
                "Comuna": data["bienRaiz"]["comuna"],
                "Manzana": data["bienRaiz"]["manzana"],
                "Predio": data["bienRaiz"]["predio"],
                "Fecha_Inscripcion": data["fechaInscripcion"],
                "Ano_Inscripcion": int(data["fechaInscripcion"][0:4]),
                "Fojas": data["fojas"],
                "Numero_Inscripcion": data["nroInscripcion"],
                "RUN_RUT": i["RUNRUT"],
                "Porcentaje_Derechos": i["porcDerecho"],
                "Ano_Vigencia_Inicial": data["fechaInscripcion"][0:4]
            }
            self.push_multipropietario(temp_multipropietario)

    def process_posterior_form(self, data, historia, ano_inscripcion_existente, ano_inscripcion_nueva):
        if int(ano_inscripcion_nueva) == int(ano_inscripcion_existente):
            ano_vigencia_final = int(ano_inscripcion_nueva)
        else:
            ano_vigencia_final = int(ano_inscripcion_nueva) - 1

        for i in historia:
            self.update_multipropietario(i["id"], {"Ano_Vigencia_Final": ano_vigencia_final})
        for i in data["adquirentes"]:
            temp_multiproprietario = {
                "Comuna": data["bienRaiz"]["comuna"],
                "Manzana": data["bienRaiz"]["manzana"],
                "Predio": data["bienRaiz"]["predio"],
                "Fecha_Inscripcion": data["fechaInscripcion"],
                "Ano_Inscripcion": int(data["fechaInscripcion"][0:4]),
                "Fojas": data["fojas"],
                "Numero_Inscripcion": data["nroInscripcion"],
                "RUN_RUT": i["RUNRUT"],
                "Porcentaje_Derechos": i["porcDerecho"],
                "Ano_Vigencia_Inicial": data["fechaInscripcion"][0:4]
            }
            self.push_multipropietario(temp_multiproprietario)

    def process_prev_form(self, data, ano_inscripcion_existente):
        for i in data["adquirentes"]:
            temp_multiproprietario = {
                "Comuna": data["bienRaiz"]["comuna"],
                "Manzana": data["bienRaiz"]["manzana"],
                "Predio": data["bienRaiz"]["predio"],
                "Fecha_Inscripcion": data["fechaInscripcion"],
                "Ano_Inscripcion": int(data["fechaInscripcion"][0:4]),
                "Fojas": data["fojas"],
                "Numero_Inscripcion": data["nroInscripcion"],
                "RUN_RUT": i["RUNRUT"],
                "Porcentaje_Derechos": i["porcDerecho"],
                "Ano_Vigencia_Inicial": data["fechaInscripcion"][0:4],
                "Ano_Vigencia_Final": data(ano_inscripcion_existente) - 1
            }
            self.push_multipropietario(temp_multiproprietario)

    def process_same_year(self, data, historia):
        for i in historia:
            self.delete_multipropietario(i["id"])

        for i in data['adquirentes']:
            temp_multiproprietario = {
                "Comuna": data["bienRaiz"]["comuna"],
                "Manzana": data["bienRaiz"]["manzana"],
                "Predio": data["bienRaiz"]["predio"],
                "Fecha_Inscripcion": data["fechaInscripcion"],
                "Ano_Inscripcion": int(data["fechaInscripcion"][0:4]),
                "Fojas": data["fojas"],
                "Numero_Inscripcion": data["nroInscripcion"],
                "RUN_RUT": i["RUNRUT"],
                "Porcentaje_Derechos": i["porcDerecho"],
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
        for i in data['adquirentes']:
            sum_derechos_adquirentes += int(i['porcDerecho'])

        print("Suma de derechos adquirentes: ", sum_derechos_adquirentes)

        #ESCENARIO 1
        if sum_derechos_adquirentes == 100:
            print("escenario 1")
            self.escenario_1_8(data)

        #ESCENARIO 2
        elif sum_derechos_adquirentes == 0 and (nro_adquirentes > 1 or nro_enajenantes > 1):
            print("escenario 2")
            self.escenario_2_8(data, nro_adquirentes)

        #ESCENARIO 3
        elif nro_adquirentes == 1 and nro_enajenantes == 1 and (0 < sum_derechos_adquirentes < 100):
            print("escenario 3")
            self.escenario_3_8(data)

        #ESCENARIO 4
        else:
            print("escenario 4")
            self.escenario_4_8(data)

    def update_historic_multipropietarios(self, data, enajenantes_historicos):
        for enajenante_historico in enajenantes_historicos:
            if int(enajenante_historico["Ano_Vigencia_Inicial"]) == int(data["fechaInscripcion"][0:4]):
                self.delete_multipropietario(enajenante_historico["id"])
            else:
                self.update_multipropietario(enajenante_historico["id"], {"Ano_Vigencia_Final": int(data["fechaInscripcion"][0:4]) - 1})

    def does_all_enajenantes_exist(self, data, enajenantes_historicos):
        for enajenante_nuevo in data['enajenantes']:
            found = False
            for enajenante_historico in enajenantes_historicos:
                if enajenante_nuevo['RUNRUT'] == enajenante_historico['RUN_RUT']:
                    found = True
                    break
            if not found:
                print("enajenante no encontrado")
                return False
        return True
    
    def get_derecho_cecido(self, data, enajenantes_historicos):
        derecho_cedido = 0
        for enajenante_nuevo in data['enajenantes']:
            for enajenante_historico in enajenantes_historicos:
                if enajenante_nuevo['RUNRUT'] == enajenante_historico['RUN_RUT']:
                    derecho_cedido += int(enajenante_historico['Porcentaje_Derechos'])
                    enajenante_historico['Ano_Vigencia_Final'] = int(data['fechaInscripcion'][0:4]) - 1
                    break
        return derecho_cedido
    
    def get_enajenantes_to_omit(self, data, enajenantes_historicos):
        omitir = []
        for enajenante_nuevo in data['enajenantes']:
            for enajenante_historico in enajenantes_historicos:
                if enajenante_nuevo['RUNRUT'] == enajenante_historico['RUN_RUT']:
                    omitir.append(enajenante_historico['RUN_RUT'])
                    enajenante_historico['Ano_Vigencia_Final'] = int(data['fechaInscripcion'][0:4]) - 1
                    break
        return omitir
    
    def get_enajenantes_with_updated_vigencia(self, data, enajenantes_historicos):
        for enajenante_nuevo in data['enajenantes']:
            for enajenante_historico in enajenantes_historicos:
                if enajenante_nuevo['RUNRUT'] == enajenante_historico['RUN_RUT']:
                    enajenante_historico['Ano_Vigencia_Final'] = int(data['fechaInscripcion'][0:4]) - 1
                    break
        return enajenantes_historicos
    
    def push_multipropietarios_not_to_omit(self, data, enajenantes_historicos, omitir):
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
    
    def escenario_1_8(self, data):
        enajenantes_historicos = self.get_history(data["bienRaiz"]["comuna"], data["bienRaiz"]["manzana"], data["bienRaiz"]["predio"])
        enajenantes_historicos = self.get_vigentes(enajenantes_historicos)
        fake_derecho = None

        if not self.does_all_enajenantes_exist(data, enajenantes_historicos):
            if data['enajenantes'][0]['RUNRUT'] != 'IGNORE':
                self.escenario_1_8_2(data)
                return False
            else:
                fake_derecho = 100
        
        self.update_historic_multipropietarios(data, enajenantes_historicos)
    
        derecho_cedido = self.get_derecho_cecido(data, enajenantes_historicos)
        if fake_derecho:
            derecho_cedido = fake_derecho
        omitir = self.get_enajenantes_to_omit(data, enajenantes_historicos)
        enajenantes_historicos = self.get_enajenantes_with_updated_vigencia(data, enajenantes_historicos)

        for i in data['adquirentes']:
            for j in enajenantes_historicos:
                if i['RUNRUT'] == j['RUN_RUT']:
                    if i['RUNRUT'] in omitir:
                        continue
                    j['Porcentaje_Derechos'] += (int(i['porcDerecho']) * derecho_cedido) / 100
                    data['adquirentes'].remove(i)
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
        
        self.push_multipropietarios_not_to_omit(data, enajenantes_historicos, omitir)

    def escenario_1_8_2(self, data):
        #enajenantes fantasma
        """
        se ignoran los enajenantes que no existen en la base de datos
        """
        enajenantes_historicos = self.get_history(data["bienRaiz"]["comuna"], data["bienRaiz"]["manzana"], data["bienRaiz"]["predio"])
        enajenantes_historicos = self.get_vigentes(enajenantes_historicos)
        enajenantes_existentes = []
        for enajenante_nuevo in data['enajenantes']:
            for enajenante_historico in enajenantes_historicos:
                if enajenante_nuevo['RUNRUT'] == enajenante_historico['RUN_RUT']:
                    #replace RUN_RUT with RUNRUT
                    enajenante_historico['RUNRUT'] = enajenante_historico['RUN_RUT']

                    enajenantes_existentes.append(enajenante_historico)
                    break
        
        if len(enajenantes_existentes) == 0:
            #create fake enajenante with 100% rights
            enajenantes_existentes.append({'RUNRUT': 'IGNORE', 'Porcentaje_Derechos': '100'})

        data['enajenantes'] = enajenantes_existentes
        
        self.escenario_1_8(data)



    def escenario_2_8(self, data, nro_adquirentes):
        enajenantes_historicos = self.get_history(data["bienRaiz"]["comuna"], data["bienRaiz"]["manzana"], data["bienRaiz"]["predio"])
        enajenantes_historicos = self.get_vigentes(enajenantes_historicos)
            
        if not self.does_all_enajenantes_exist(data, enajenantes_historicos):
            self.escenario_2_8_2(data)
            return False
        
        self.update_historic_multipropietarios(data, enajenantes_historicos)

        derecho_cedido = self.get_derecho_cecido(data, enajenantes_historicos)
        omitir = self.get_enajenantes_to_omit(data, enajenantes_historicos)
        enajenantes_historicos = self.get_enajenantes_with_updated_vigencia(data, enajenantes_historicos)
        
        
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

        self.push_multipropietarios_not_to_omit(data, enajenantes_historicos, omitir)

    def escenario_2_8_2(self, data):
        enajenantes_historicos = self.get_history(data["bienRaiz"]["comuna"], data["bienRaiz"]["manzana"], data["bienRaiz"]["predio"])
        enajenantes_historicos = self.get_vigentes(enajenantes_historicos)

        enajenantes = data['enajenantes']

        #remove enajenantes that do not exist in the database
        enajenantes_existentes = []
        for enajenante_nuevo in enajenantes:
            for enajenante_historico in enajenantes_historicos:
                if enajenante_nuevo['RUNRUT'] == enajenante_historico['RUN_RUT']:
                    enajenantes_existentes.append(enajenante_nuevo)
                    break

        if len(enajenantes_existentes) == 0:
            return False
        
        data['enajenantes'] = enajenantes_existentes

        self.escenario_2_8(data, len(data['adquirentes']))



    def escenario_3_8(self, data):
        enajenantes_historicos = self.get_history(data["bienRaiz"]["comuna"], data["bienRaiz"]["manzana"], data["bienRaiz"]["predio"])
        enajenantes_historicos = self.get_vigentes(enajenantes_historicos)
        if not self.does_all_enajenantes_exist(data, enajenantes_historicos):
            self.escenario_3_8_2(data)
            return False

        derecho_cedido = 0
        rut_enajenante = ''

        for enajenante_nuevo in data['enajenantes']:
            for enajenante_historico in enajenantes_historicos:
                if enajenante_nuevo['RUNRUT'] == enajenante_historico['RUN_RUT']:
                    rut_enajenante = enajenante_nuevo['RUNRUT']
                    derecho_cedido = (float(enajenante_historico['Porcentaje_Derechos']) * float(enajenante_nuevo['porcDerecho'])) / 100
                    break

        print("enajenante cede: ", data['enajenantes'][0]['porcDerecho'], "\ total derecho: ", derecho_cedido)

        self.update_historic_multipropietarios(data, enajenantes_historicos)

        adquirente_historico = None
        derecho_original_adquirente = 0
        for multipropietario in enajenantes_historicos:
            if multipropietario['RUN_RUT'] == data['adquirentes'][0]['RUNRUT']:
                adquirente_historico = multipropietario
                derecho_original_adquirente == float(multipropietario['Porcentaje_Derechos'])
                break
            

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
                "Porcentaje_Derechos": derecho_cedido + derecho_original_adquirente,
                "Ano_Vigencia_Inicial": data["fechaInscripcion"][0:4]
            }
            self.push_multipropietario(temp_multipropietario)

        for enajenante_historico in enajenantes_historicos:
            if adquirente_historico:
                if enajenante_historico['RUN_RUT'] == adquirente_historico['RUN_RUT']:
                    continue
            if enajenante_historico['RUN_RUT'] == rut_enajenante:
                nuevo_derecho = float(enajenante_historico['Porcentaje_Derechos']) - derecho_cedido
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

    def escenario_3_8_2(self, data):
        enajenantes_historicos = self.get_history(data["bienRaiz"]["comuna"], data["bienRaiz"]["manzana"], data["bienRaiz"]["predio"])
        enajenantes_historicos = self.get_vigentes(enajenantes_historicos)

        adquirentes = data['adquirentes']
        enajenantes = data['enajenantes']

        #sum all rights
        sum_derechos_totales = 0
        for adquirente in adquirentes:
            sum_derechos_totales += float(adquirente['porcDerecho'])
        for enajenante_historico in enajenantes_historicos:
            sum_derechos_totales += float(enajenante_historico['Porcentaje_Derechos'])

        if sum_derechos_totales == 100:
            #push adquirentes
            for adquirente in adquirentes:
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
        
        elif sum_derechos_totales < 100:
            #push adquirentes
            for adquirente in adquirentes:
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
            
            #push enajenantes with derecho = 100 - sum_derechos_totales
            for enajenante_historico in enajenantes_historicos:
                temp_multiproprietario = {
                    "Comuna": enajenante_historico["Comuna"],
                    "Manzana": enajenante_historico["Manzana"],
                    "Predio": enajenante_historico["Predio"],
                    "Fecha_Inscripcion": enajenante_historico["Fecha_Inscripcion"],
                    "Ano_Inscripcion": enajenante_historico["Ano_Inscripcion"],
                    "Fojas": enajenante_historico["Fojas"],
                    "Numero_Inscripcion": enajenante_historico["Numero_Inscripcion"],
                    "RUN_RUT": enajenante_historico["RUN_RUT"],
                    "Porcentaje_Derechos": 100 - sum_derechos_totales,
                    "Ano_Vigencia_Inicial": data["fechaInscripcion"][0:4]
                }
                self.push_multipropietario(temp_multiproprietario)
        
        elif sum_derechos_totales > 100:
            self.update_historic_multipropietarios(data, enajenantes_historicos)
            for enajenante_historico in enajenantes_historicos:
                temp_multiproprietario = {
                    "Comuna": enajenante_historico["Comuna"],
                    "Manzana": enajenante_historico["Manzana"],
                    "Predio": enajenante_historico["Predio"],
                    "Fecha_Inscripcion": enajenante_historico["Fecha_Inscripcion"],
                    "Ano_Inscripcion": enajenante_historico["Ano_Inscripcion"],
                    "Fojas": enajenante_historico["Fojas"],
                    "Numero_Inscripcion": enajenante_historico["Numero_Inscripcion"],
                    "RUN_RUT": enajenante_historico["RUN_RUT"],
                    "Porcentaje_Derechos": float(enajenante_historico['Porcentaje_Derechos']) * (100 / sum_derechos_totales),
                    "Ano_Vigencia_Inicial": data["fechaInscripcion"][0:4]
                }
                self.push_multipropietario(temp_multiproprietario)

            for adquirente in adquirentes:
                temp_multiproprietario = {
                    "Comuna": data["bienRaiz"]["comuna"],
                    "Manzana": data["bienRaiz"]["manzana"],
                    "Predio": data["bienRaiz"]["predio"],
                    "Fecha_Inscripcion": data["fechaInscripcion"],
                    "Ano_Inscripcion": int(data["fechaInscripcion"][0:4]),
                    "Fojas": data["fojas"],
                    "Numero_Inscripcion": data["nroInscripcion"],
                    "RUN_RUT": adquirente["RUNRUT"],
                    "Porcentaje_Derechos": float(adquirente["porcDerecho"]) * (100 / sum_derechos_totales),
                    "Ano_Vigencia_Inicial": data["fechaInscripcion"][0:4]
                }
                self.push_multipropietario(temp_multiproprietario)

        return True

    def escenario_4_8(self, data):
        enajenantes_historicos = self.get_history(data["bienRaiz"]["comuna"], data["bienRaiz"]["manzana"], data["bienRaiz"]["predio"])
        enajenantes_historicos = self.get_vigentes(enajenantes_historicos)

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
                self.escenario_4_8_2(data)
                return False
    
        self.update_historic_multipropietarios(data, enajenantes_historicos)

        data['adquirentes'] = self.group_adquirentes(data['adquirentes'])
        nuevos_adquirentes = []
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
            nuevos_adquirentes.append(temp_multipropietario)

        nuevos_enajenantes_historicos = []
        for enajenante_historico in enajenantes_historicos:
            if enajenante_historico['RUN_RUT'] in rut_derecho_cedido.keys():
                print(f"actual: {int(enajenante_historico['Porcentaje_Derechos'])}")
                nuevo_derecho = int(enajenante_historico['Porcentaje_Derechos']) - rut_derecho_cedido[enajenante_historico['RUN_RUT']]
                print(f"nuevo: {nuevo_derecho}")
                if nuevo_derecho <= 0:
                    nuevo_derecho = 0
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
                    nuevos_enajenantes_historicos.append(temp_multipropietario)
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
                    nuevos_enajenantes_historicos.append(temp_multipropietario)
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
                nuevos_enajenantes_historicos.append(temp_multipropietario)

        total_derechos = 0
        for adquirente in nuevos_adquirentes:
            total_derechos += int(adquirente['Porcentaje_Derechos'])

        for enajenante_historico in nuevos_enajenantes_historicos:
            total_derechos += int(enajenante_historico['Porcentaje_Derechos'])

        adquirentes_y_historicos = self.group_adquirentes_y_historicos(nuevos_adquirentes, nuevos_enajenantes_historicos)

        if total_derechos == 100:
            for mp in adquirentes_y_historicos:
                if int(mp['Porcentaje_Derechos']) == 0:
                    continue
                self.push_multipropietario(mp)

        elif total_derechos < 100:
            multiprops_0_derechos = []
            for mp in adquirentes_y_historicos:
                if int(mp['Porcentaje_Derechos']) == 0:
                    multiprops_0_derechos.append(mp)
                else:
                    self.push_multipropietario(mp)

            for multiprop in multiprops_0_derechos:
                multiprop['Porcentaje_Derechos'] = (100-total_derechos) / len(multiprops_0_derechos)
                self.push_multipropietario(multiprop)

        elif total_derechos > 100:
            for mp in adquirentes_y_historicos:
                print(mp)
                if int(mp['Porcentaje_Derechos']) == 0:
                    continue
                mp['Porcentaje_Derechos'] = (int(mp['Porcentaje_Derechos']) * 100) / total_derechos
                self.push_multipropietario(mp)

    def group_adquirentes_y_historicos(self, adquirentes, enajenantes_historicos):
        adquirentes_y_historicos = []
        for enajenante_historico in enajenantes_historicos:
            adquirentes_y_historicos.append(enajenante_historico)

        for adquirente in adquirentes:
            found = False
            for adquirente_y_historico in adquirentes_y_historicos:
                if adquirente['RUN_RUT'] == adquirente_y_historico['RUN_RUT']:
                    adquirente_y_historico['Porcentaje_Derechos'] += int(adquirente['Porcentaje_Derechos'])
                    found = True
                    break

            if not found:
                adquirentes_y_historicos.append(adquirente)
        return adquirentes_y_historicos


    def escenario_4_8_2(self, data):
        enajenantes_historicos = self.get_history(data["bienRaiz"]["comuna"], data["bienRaiz"]["manzana"], data["bienRaiz"]["predio"])
        enajenantes_historicos = self.get_vigentes(enajenantes_historicos)

        temp_enajenantes_historicos = []
        for i in range(len(enajenantes_historicos)):
            temp_enajenantes_historicos.append(enajenantes_historicos[i])

        adquirentes = data['adquirentes']
        enajenantes = data['enajenantes']
        enajenantes_fantasma = []

        for enajenante_nuevo in enajenantes:
            found = False
            for enajenante_historico in enajenantes_historicos:
                if enajenante_nuevo['RUNRUT'] == enajenante_historico['RUN_RUT']:
                    found = True
                    break
            if not found:
                enajenantes_fantasma.append({
                    'Comuna': data['bienRaiz']['comuna'],
                    'Manzana': data['bienRaiz']['manzana'],
                    'Predio': data['bienRaiz']['predio'],
                    'Fecha_Inscripcion': data['fechaInscripcion'],
                    'Ano_Inscripcion': int(data['fechaInscripcion'][0:4]),
                    'Fojas': data['fojas'],
                    'Numero_Inscripcion': data['nroInscripcion'],
                    'RUN_RUT': enajenante_nuevo['RUNRUT'],
                    'Porcentaje_Derechos': enajenante_nuevo['porcDerecho'],
                    'Ano_Vigencia_Inicial': data['fechaInscripcion'][0:4]
                })

        for enajenante_historico in temp_enajenantes_historicos:
            for enajenante_nuevo in enajenantes:
                if enajenante_historico['RUN_RUT'] == enajenante_nuevo['RUNRUT']:
                    enajenante_historico['Porcentaje_Derechos'] -= int(enajenante_nuevo['porcDerecho'])
                    if enajenante_historico['Porcentaje_Derechos'] <= 0:
                        enajenante_historico['Porcentaje_Derechos'] = 0
                    break

        sum_derechos_totales = 0
        for adquirente in adquirentes:
            sum_derechos_totales += int(adquirente['porcDerecho'])
        for enajenante_historico in temp_enajenantes_historicos:
            sum_derechos_totales += int(enajenante_historico['Porcentaje_Derechos'])

        for adquirente in adquirentes:
            for enajenante_historico in temp_enajenantes_historicos:
                if adquirente['RUNRUT'] == enajenante_historico['RUN_RUT']:
                    adquirente['porcDerecho'] += enajenante_historico['Porcentaje_Derechos']
                    temp_enajenantes_historicos.remove(enajenante_historico)
                    break

        if sum_derechos_totales == 100:
            self.update_historic_multipropietarios(data, enajenantes_historicos)

            for enajenante_historico in temp_enajenantes_historicos:
                if enajenante_historico['Porcentaje_Derechos'] == 0:
                    continue

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

            #push adquirentes
            for adquirente in adquirentes:
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
        
        elif sum_derechos_totales < 100:
            self.update_historic_multipropietarios(data, enajenantes_historicos)

            multiprops_0_derechos = []
            for enajenante_historico in temp_enajenantes_historicos:
                if enajenante_historico['Porcentaje_Derechos'] == 0:
                    multiprops_0_derechos.append(enajenante_historico)
                    continue
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

            for adquirente in adquirentes:
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
            
            multiprops_0_derechos += enajenantes_fantasma
            for multiprop in multiprops_0_derechos:
                temp_multiproprietario = {
                    "Comuna": multiprop["Comuna"],
                    "Manzana": multiprop["Manzana"],
                    "Predio": multiprop["Predio"],
                    "Fecha_Inscripcion": data["fechaInscripcion"],
                    "Ano_Inscripcion": data["fechaInscripcion"][0:4],
                    "Fojas": multiprop["Fojas"],
                    "Numero_Inscripcion": multiprop["Numero_Inscripcion"],
                    "RUN_RUT": multiprop["RUN_RUT"],
                    "Porcentaje_Derechos": (100-sum_derechos_totales) / len(multiprops_0_derechos),
                    "Ano_Vigencia_Inicial": data["fechaInscripcion"][0:4]
                }
                self.push_multipropietario(temp_multiproprietario)

        elif sum_derechos_totales > 100:
            self.update_historic_multipropietarios(data, enajenantes_historicos)
            for enajenante_historico in temp_enajenantes_historicos:
                if enajenante_historico['Porcentaje_Derechos'] == 0:
                    continue

                temp_multiproprietario = {
                    "Comuna": enajenante_historico["Comuna"],
                    "Manzana": enajenante_historico["Manzana"],
                    "Predio": enajenante_historico["Predio"],
                    "Fecha_Inscripcion": enajenante_historico["Fecha_Inscripcion"],
                    "Ano_Inscripcion": enajenante_historico["Ano_Inscripcion"],
                    "Fojas": enajenante_historico["Fojas"],
                    "Numero_Inscripcion": enajenante_historico["Numero_Inscripcion"],
                    "RUN_RUT": enajenante_historico["RUN_RUT"],
                    "Porcentaje_Derechos": int(enajenante_historico['Porcentaje_Derechos']) * (100 / sum_derechos_totales),
                    "Ano_Vigencia_Inicial": data["fechaInscripcion"][0:4]
                }
                self.push_multipropietario(temp_multiproprietario)

            for adquirente in adquirentes:
                temp_multiproprietario = {
                    "Comuna": data["bienRaiz"]["comuna"],
                    "Manzana": data["bienRaiz"]["manzana"],
                    "Predio": data["bienRaiz"]["predio"],
                    "Fecha_Inscripcion": data["fechaInscripcion"],
                    "Ano_Inscripcion": int(data["fechaInscripcion"][0:4]),
                    "Fojas": data["fojas"],
                    "Numero_Inscripcion": data["nroInscripcion"],
                    "RUN_RUT": adquirente["RUNRUT"],
                    "Porcentaje_Derechos": int(adquirente["porcDerecho"]) * (100 / sum_derechos_totales),
                    "Ano_Vigencia_Inicial": data["fechaInscripcion"][0:4]
                }
                self.push_multipropietario(temp_multiproprietario)

    def add_multipropietarios(self, data):
        print("Processing multipropietarios: ", data)
        tipo_escritura = data["CNE"]
        if tipo_escritura == int(CNE_REGULARIZACION_DEL_PATRIMONIO):
            self.add_multipropietarios_99(data)
        elif tipo_escritura == int(CNE_COMPRAVENTA):
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

    def generate_push_query(self, multiprop):
        columnas = ", ".join(list(multiprop.keys()))
        valores = ", ".join(list(map(str, list(multiprop.values()))))
        
        strings = ['Fecha_Inscripcion', 'RUN_RUT']
        for string in strings:
            valores = valores.replace(f"{multiprop[string]}", f"'{multiprop[string]}'")
        string_sql = f"INSERT INTO Multipropietarios ({columnas}) VALUES ({valores})"
        return string_sql

    def generate_push_input_query(self, multiprop):
        columnas = ", ".join(multiprop.keys())
        valores = []
        for key, value in multiprop.items():
            if isinstance(value, str):
                valores.append(f"'{value}'")
            else:
                valores.append(str(value))
        valores_str = ", ".join(valores)
        string_sql = f"INSERT INTO Multipropietarios ({columnas}) VALUES ({valores_str})"
        return string_sql

    def procesar_input(self, multiprop):
        string_sql = self.generate_push_input_query(multiprop)
        print("Executing: ", string_sql)
        self.cursor.execute(string_sql)
        self.database.commit()

    def push_multipropietario(self, multiprop):
        try:
            string_sql = self.generate_push_query(multiprop)
            print("Executing: ", string_sql)
            self.cursor.execute(string_sql)
            self.database.commit()
        except:
            self.procesar_input(multiprop)

    def generate_update_query(self, row_id, multiprop):
        strings = ['Fecha_Inscripcion', 'RUN_RUT']
        for string in strings:
            if string in multiprop:
                multiprop[string] = f"'{multiprop[string]}'"
                                                               
        string_sql = f"UPDATE Multipropietarios SET " + ", ".join([f"{k} = {v}" for k, v in multiprop.items()]) + f" WHERE id = {row_id}"
        return string_sql
    
    def generate_update_input_query(self, row_id, multiprop):
        valores = []
        for key, value in multiprop.items():
            if isinstance(value, str):
                valores.append(f"'{value}'")
            else:
                valores.append(str(value))
        valores_str = ", ".join(valores)
        string_sql = f"UPDATE Multipropietarios SET " + valores_str + f" WHERE id = {row_id}"
        return string_sql
    
    def update_input(self, row_id, multiprop):
        string_sql = self.generate_update_input_query()
        print("Updating: ", row_id, multiprop)
        self.cursor.execute(string_sql)
        self.database.commit()

    def update_multipropietario(self, row_id, multiprop):
        try:
            string_sql = self.generate_update_query(row_id, multiprop)
            print("Updating: ", row_id, multiprop)
            self.cursor.execute(string_sql)
            self.database.commit()
        except:
            self.update_input(multiprop)

    def delete_multipropietario(self, row_id):
        string_sql = f"DELETE FROM Multipropietarios WHERE id = {row_id}"
        print("Executing: ", string_sql)
        self.cursor.execute(string_sql)
        self.database.commit()
