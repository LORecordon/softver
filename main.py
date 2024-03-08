from flask import Flask, redirect, render_template, request
from http_errors import HTTP_BAD_REQUEST, HTTP_NOT_FOUND
from service import RegisterManager
from settings import ALL_REGISTER_PAGE, CREATE_PAGE, JSON_FILE, REGISTER_PAGE, VIEW_BASE_URL

app = Flask(__name__)
app.template_folder = VIEW_BASE_URL
app.static_folder = VIEW_BASE_URL

registerManager = RegisterManager()

################
## CONTROLLER ##
################
@app.route('/register', methods=['POST'])
def post_register():
    text = request.form["textInput"]
    number = request.form["numInput"]
    if len(text) == 0:
        return render_template(CREATE_PAGE, error="El campo 'texto' no puede ser vacío", form = request.form), HTTP_BAD_REQUEST
    if not number:
        return render_template(CREATE_PAGE, error="El campo 'numero' no puede ser vacío", form = request.form), HTTP_BAD_REQUEST
    result = registerManager.post_register_to_db(text, number)
    return redirect('/register', result)

@app.route('/load_json', methods=['POST'])
def post_json():
    file = request.files["fileInput"]
    filename = file.filename
    if filename[-4:] != JSON_FILE:
        return render_template(CREATE_PAGE, file_error="La extensión del archivo debe ser .json", form = request.form), HTTP_BAD_REQUEST
    result = registerManager.process_json(file)
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
    return render_template(REGISTER_PAGE, data=register)

@app.errorhandler(HTTP_NOT_FOUND)
def page_not_found(e):
    return render_template(f'error/{HTTP_NOT_FOUND}.html'), HTTP_NOT_FOUND

if __name__ == '__main__':
    app.run(debug=True)