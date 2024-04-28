import pytest
from http_errors import HTTP_OK
from service import RegisterManager

register_manager = RegisterManager()
id_to_search = None

@pytest.fixture(scope="session", autouse=True)
def setup():
    print("Se borraran registros")
    string_sql = 'DELETE FROM registros'
    register_manager.cursor.execute(string_sql)

def test_create_register():
    result = register_manager.post_register_to_db("hola", 1234)
    assert result == HTTP_OK

def test_get_all_registers():
    global id_to_search
    data = register_manager.get_all_registers()
    if len(data) == 0:
        assert False 
    id_to_search = data[0]["id"]
    is_same_text = data[0]["texto"] == "hola" 
    is_same_number = data[0]["numero"] == 1234 
    assert is_same_text and is_same_number 

def test_get_register():
    global id_to_search
    if id_to_search == None:
        assert False
    data = register_manager.get_register_by_id(id_to_search)
    is_same_text = data["texto"] == "hola" 
    is_same_number = data["numero"] == 1234 
    assert is_same_text and is_same_number

##### COMO NO SE TESTEA LA FUNCIÓN DE SUBIDA DE JSON Y LOS EXCEPT EL PORCENTAJE NO SERA 100%

