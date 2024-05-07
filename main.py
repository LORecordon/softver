from flask import Flask, redirect, render_template, request
from http_errors import HTTP_BAD_REQUEST, HTTP_NOT_FOUND
from service import RegisterManager
from settings import ALL_REGISTER_PAGE, CREATE_PAGE, JSON_FILE, REGISTER_PAGE, VIEW_BASE_URL, FIND_PAGE, SEARCH_PAGE, AFTER_PAGE
import json

app = Flask(__name__)
app.template_folder = VIEW_BASE_URL
app.static_folder = VIEW_BASE_URL

registerManager = RegisterManager()

################
## CONTROLLER ##
################
@app.route('/register', methods=['POST'])
def post_register():
    tipoEscritura = request.form["tipoEscrituraInput"]
    comuna = request.form["comunaInput"]
    manzana = request.form["manzanaInput"]
    predio = request.form["predioInput"]
    fojas = request.form["fojasInput"]
    fecha = request.form["dateInput"]
    nmroInscripcion = request.form["inscriptionNumberInput"]

    enajenantes_rut = request.form.getlist('enajenantesRutInput[]')
    enajenantes_derecho = request.form.getlist('enajenantesDerechoInput[]')
    adquirentes_rut = request.form.getlist('adquirenteRutInput[]')
    adquirentes_derecho = request.form.getlist('adquirenteDerechoInput[]')

    enajenantes = []
    for i in range(len(enajenantes_rut)):
        enajenante = {
            'RUNRUT': enajenantes_rut[i],
            'porcDerecho': enajenantes_derecho[i]
        }
        enajenantes.append(enajenante)

    adquirentes = []
    for i in range(len(adquirentes_rut)):
        adquirente = {
            'RUNRUT': adquirentes_rut[i],
            'porcDerecho': adquirentes_derecho[i]
        }
        adquirentes.append(adquirente)

    if not tipoEscritura:
        return render_template(CREATE_PAGE, error="El campo 'tipo de escritura' no puede ser vacío", form = request.form), HTTP_BAD_REQUEST
    if not comuna:
        return render_template(CREATE_PAGE, error="El campo 'comuna' no puede ser vacío", form = request.form), HTTP_BAD_REQUEST
    if not manzana:
        return render_template(CREATE_PAGE, error="El campo 'manzana' no puede ser vacío", form = request.form), HTTP_BAD_REQUEST
    if not predio:
        return render_template(CREATE_PAGE, error="El campo 'predio' no puede ser vacío", form = request.form), HTTP_BAD_REQUEST
    
    if (adquirentes[0]["RUNRUT"]) == "":
        return render_template(CREATE_PAGE, error="El campo 'rut adquirente' no puede ser vacío", form = request.form), HTTP_BAD_REQUEST
    if (adquirentes[0]["porcDerecho"]) == "":
        return render_template(CREATE_PAGE, error="El campo 'derecho adquirente' no puede ser vacío", form = request.form), HTTP_BAD_REQUEST
    if not fojas:
        return render_template(CREATE_PAGE, error="El campo 'fojas' no puede ser vacío", form = request.form), HTTP_BAD_REQUEST
    if not fecha:
        return render_template(CREATE_PAGE, error="El campo 'fecha' no puede ser vacío", form = request.form), HTTP_BAD_REQUEST
    if not nmroInscripcion:
        return render_template(CREATE_PAGE, error="El campo 'numero de inscripción' no puede ser vacío", form = request.form), HTTP_BAD_REQUEST



    result = registerManager.post_register_to_db(tipoEscritura, comuna, manzana, predio, enajenantes, adquirentes, fojas, fecha, nmroInscripcion)
    return redirect('/register', result)

@app.route('/load_json', methods=['POST'])
def post_json():
    file = request.files["fileInput"]
    filename = file.filename
    if filename[-4:] != JSON_FILE:
        return render_template(CREATE_PAGE, file_error="La extensión del archivo debe ser .json", form = request.form), HTTP_BAD_REQUEST
    result = registerManager.process_json(file)
    return render_template(AFTER_PAGE, data=result)
    return redirect('/register', result)


################
#### VIEWS #####
################
@app.route('/')
def index():
    return get_all_registers()

@app.route('/create')
def create_register():
    return render_template(CREATE_PAGE, form={"textInput": '', "numInput": ''})

@app.route('/register')
def get_all_registers():
    registers = registerManager.get_all_registers()
    return render_template(ALL_REGISTER_PAGE, data=registers)

@app.route('/register/<id>')
def get_register_by_id(id):
    register = registerManager.get_register_by_id(id)
    
    register['Enajenantes'] = json.loads(register['Enajenantes'])
    register['Adquirentes'] = json.loads(register['Adquirentes'])


    print("enaj :",register['Enajenantes'] )
    print("adq :",register['Adquirentes'])

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
        return render_template(FIND_PAGE, error="El campo 'comuna' no puede ser vacío", form = request.form), HTTP_BAD_REQUEST
    if not manzana:
        return render_template(FIND_PAGE, error="El campo 'manzana' no puede ser vacío", form = request.form), HTTP_BAD_REQUEST
    if not predio:
        return render_template(FIND_PAGE, error="El campo 'predio' no puede ser vacío", form = request.form), HTTP_BAD_REQUEST
    if not fecha:
        return render_template(FIND_PAGE, error="El campo 'fecha' no puede ser vacío", form = request.form), HTTP_BAD_REQUEST
    


    multiprop = registerManager.get_multiprop(comuna, manzana, predio, fecha)
    return render_template(SEARCH_PAGE, data=multiprop)

@app.errorhandler(HTTP_NOT_FOUND)
def page_not_found(e):
    return render_template(f'error/{HTTP_NOT_FOUND}.html'), HTTP_NOT_FOUND

if __name__ == '__main__':
    app.run(debug=True)