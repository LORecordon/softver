from flask import Flask, redirect, render_template, request
from http_errors import HTTP_BAD_REQUEST, HTTP_NOT_FOUND
from service import RegisterManager
from settings import (
    ALL_REGISTER_PAGE, CREATE_PAGE, JSON_FILE, REGISTER_PAGE, VIEW_BASE_URL,
    FIND_PAGE, SEARCH_PAGE, AFTER_PAGE
)
import json
from variables_globales import CNE_COMPRAVENTA,CNE_REGULARIZACION_DEL_PATRIMONIO

app = Flask(__name__)
app.template_folder = VIEW_BASE_URL
app.static_folder = VIEW_BASE_URL

register_manager = RegisterManager()

@app.route('/register', methods=['POST'])
def post_register():
    tipo_escritura = request.form["tipoEscrituraInput"]
    comuna = request.form["comunaInput"]
    manzana = request.form["manzanaInput"]
    predio = request.form["predioInput"]
    fojas = request.form["fojasInput"]
    fecha = request.form["dateInput"]
    nmro_inscripcion = request.form["inscriptionNumberInput"]

    enajenantes_rut = request.form.getlist('enajenantesRutInput[]')
    enajenantes_derecho = request.form.getlist('enajenantesDerechoInput[]')
    adquirentes_rut = request.form.getlist('adquirenteRutInput[]')
    adquirentes_derecho = request.form.getlist('adquirenteDerechoInput[]')
    
    enajenantes = generate_enajenantes(tipo_escritura, enajenantes_rut, enajenantes_derecho)
    adquirentes = generate_adquirentes(adquirentes_rut, adquirentes_derecho)

    errors = check_form_fields(tipo_escritura, comuna, manzana, predio, fojas, fecha, nmro_inscripcion, enajenantes, adquirentes)
    if errors:
        return render_template(CREATE_PAGE, error=errors, form=request.form), HTTP_BAD_REQUEST

    result = register_manager.post_register_to_db(tipo_escritura, comuna, manzana, predio, enajenantes, adquirentes, fojas, fecha, nmro_inscripcion)
    return redirect('/register', result)

def check_form_fields(tipo_escritura, comuna, manzana, predio, fojas, fecha, nmro_inscripcion, enajenantes, adquirentes):
    if not tipo_escritura:
        return "El campo 'tipo de escritura' no puede ser vacío"
    if not comuna:
        return "El campo 'comuna' no puede ser vacío"
    if not manzana:
        return "El campo 'manzana' no puede ser vacío"
    if not predio:
        return "El campo 'predio' no puede ser vacío"
    
    if tipo_escritura == CNE_COMPRAVENTA:
        if not enajenantes[0]["RUNRUT"]:
            return "El campo 'rut enajenantes' no puede ser vacío"
        if not enajenantes[0]["porcDerecho"]:
            return "El campo 'derecho enajenantes' no puede ser vacío"
        
    if not adquirentes[0]["RUNRUT"]:
        return "El campo 'rut adquirente' no puede ser vacío"
    if not adquirentes[0]["porcDerecho"]:
        return "El campo 'derecho adquirente' no puede ser vacío"
    if not fojas:
        return "El campo 'fojas' no puede ser vacío"
    if not fecha:
        return "El campo 'fecha' no puede ser vacío"
    if not nmro_inscripcion:
        return "El campo 'numero de inscripción' no puede ser vacío"
    
    return ""

def generate_enajenantes(tipo_escritura, enajenantes_rut, enajenantes_derecho):
    if tipo_escritura == CNE_REGULARIZACION_DEL_PATRIMONIO:
        enajenantes = []
    else:
        enajenantes = [{'RUNRUT': rut, 'porcDerecho': derecho} for rut, derecho in zip(enajenantes_rut, enajenantes_derecho)]
    return enajenantes

def generate_adquirentes(adquirentes_rut, adquirentes_derecho):
    adquirentes = [{'RUNRUT': rut, 'porcDerecho': derecho} for rut, derecho in zip(adquirentes_rut, adquirentes_derecho)]
    return adquirentes

@app.route('/load_json', methods=['POST'])
def post_json():
    file = request.files["fileInput"]
    filename = file.filename
    if not filename.endswith(JSON_FILE):
        return render_template(CREATE_PAGE, file_error="La extensión del archivo debe ser .json", form=request.form), HTTP_BAD_REQUEST
    
    result = register_manager.process_json(file)
    return render_template(AFTER_PAGE, data=result)

@app.route('/')
def list_registers():
    return get_all_registers()

@app.route('/create')
def create_register():
    return render_template(CREATE_PAGE, form={"textInput": '', "numInput": ''})

@app.route('/register')
def get_all_registers():
    registers = register_manager.get_all_registers()
    return render_template(ALL_REGISTER_PAGE, data=registers)

@app.route('/register/<id>')
def get_register_by_id(id):
    register = register_manager.get_register_by_id(id)
    register['Enajenantes'] = json.loads(register['Enajenantes'])
    register['Adquirentes'] = json.loads(register['Adquirentes'])
    return render_template(REGISTER_PAGE, data=register)

@app.route('/find')
def find():
    return render_template(FIND_PAGE, form={"textInput": '', "numInput": ''})

@app.route('/search', methods=['POST'])
def find_register():
    comuna = request.form["comunaInput"]
    manzana = request.form["manzanaInput"]
    predio = request.form["predioInput"]
    fecha = request.form["fInput"]

    if not comuna:
        return render_template(FIND_PAGE, error="El campo 'comuna' no puede ser vacío", form=request.form), HTTP_BAD_REQUEST
    if not manzana:
        return render_template(FIND_PAGE, error="El campo 'manzana' no puede ser vacío", form=request.form), HTTP_BAD_REQUEST
    if not predio:
        return render_template(FIND_PAGE, error="El campo 'predio' no puede ser vacío", form=request.form), HTTP_BAD_REQUEST
    if not fecha:
        return render_template(FIND_PAGE, error="El campo 'fecha' no puede ser vacío", form=request.form), HTTP_BAD_REQUEST

    multiprop = register_manager.get_multiprop(comuna, manzana, predio)
    filtered_multiprop = register_manager.filter_by_date(multiprop, fecha)
    return render_template(SEARCH_PAGE, data=filtered_multiprop)

@app.errorhandler(HTTP_NOT_FOUND)
def page_not_found(e):
    return render_template(f'error/{HTTP_NOT_FOUND}.html'), HTTP_NOT_FOUND

if __name__ == '__main__':
    app.run(debug=True)
