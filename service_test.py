import pytest
import json
from unittest.mock import MagicMock, patch
import io

from http_errors import HTTP_OK
from service import RegisterManager  # Replace with the actual class name

@pytest.fixture
def manager():
    manager = RegisterManager()
    manager.cursor = MagicMock()
    manager.database = MagicMock()
    return manager

def test_post_register_to_db(manager):
    tipo_escritura = "1"
    comuna = "TestComuna"
    manzana = "TestManzana"
    predio = "TestPredio"
    enajenante = [{"RUNRUT": "12345678-9", "porcDerecho": 50}]
    adquiriente = [{"RUNRUT": "98765432-1", "porcDerecho": 50}]
    fojas = "100"
    fecha = "2023-01-01"
    nmro_inscripcion = "200"

    json_data = {
        "F2890": [
            {
                "CNE": 1,
                "bienRaiz": {
                    "comuna": comuna,
                    "manzana": manzana,
                    "predio": predio
                },
                "adquirentes": adquiriente,
                "enajenantes": enajenante,
                "fojas": fojas,
                "fechaInscripcion": fecha,
                "nroInscripcion": nmro_inscripcion
            }
        ]
    }

    json_str = json.dumps(json_data)

    with patch('io.StringIO', return_value=io.StringIO(json_str)):
        response = manager.post_register_to_db(tipo_escritura, comuna, manzana, predio, enajenante, adquiriente, fojas, fecha, nmro_inscripcion)
        assert response == HTTP_OK

        manager.cursor.execute.assert_called_once()
        manager.database.commit.assert_called_once()

def test_get_all_registers(manager):
    expected_registers = [("row1",), ("row2",)]
    manager.cursor.fetchall.return_value = expected_registers

    registers = manager.get_all_registers()

    manager.cursor.execute.assert_called_once_with('SELECT * FROM Registros')
    assert registers == expected_registers

def test_get_register_by_id(manager):
    expected_register = ("row",)
    id = 1
    manager.cursor.fetchone.return_value = expected_register

    register = manager.get_register_by_id(id)

    manager.cursor.execute.assert_called_once_with(f'SELECT * FROM Registros WHERE N_Atencion = {id}')
    assert register == expected_register

def test_get_multiprop(manager):
    comuna = "TestComuna"
    manzana = "TestManzana"
    predio = "TestPredio"
    expected_multipropietarios = [("row1",), ("row2",)]
    manager.cursor.fetchall.return_value = expected_multipropietarios

    multipropietarios = manager.get_multiprop(comuna, manzana, predio)

    manager.cursor.execute.assert_called_once_with(
        f"SELECT * FROM Multipropietarios WHERE Comuna = '{comuna}' AND Manzana = '{manzana}' AND Predio = '{predio}'"
    )
    assert multipropietarios == expected_multipropietarios

def test_filter_by_date(manager):
    multipropietarios = [
        {"Ano_Vigencia_Inicial": 2020, "Ano_Vigencia_Final": None},
        {"Ano_Vigencia_Inicial": 2019, "Ano_Vigencia_Final": 2022},
        {"Ano_Vigencia_Inicial": 2021, "Ano_Vigencia_Final": 2023},
    ]
    fecha = "2022"

    result = manager.filter_by_date(multipropietarios, fecha)

    expected_result = [
        {"Ano_Vigencia_Inicial": 2020, "Ano_Vigencia_Final": None},
        {"Ano_Vigencia_Inicial": 2019, "Ano_Vigencia_Final": 2022},
        {"Ano_Vigencia_Inicial": 2021, "Ano_Vigencia_Final": 2023},
    ]
    assert result == expected_result

def test_process_json(manager):
    json_data = {
        "F2890": [
            {
                "CNE": 1,
                "bienRaiz": {
                    "comuna": "TestComuna",
                    "manzana": "TestManzana",
                    "predio": "TestPredio"
                },
                "adquirentes": [{"RUNRUT": "98765432-1", "porcDerecho": 50}],
                "enajenantes": [{"RUNRUT": "12345678-9", "porcDerecho": 50}],
                "fojas": "100",
                "fechaInscripcion": "2023-01-01",
                "nroInscripcion": "200"
            }
        ]
    }
    manager.push_register = MagicMock()
    manager.add_multipropietarios = MagicMock()
    json_file = io.StringIO(json.dumps(json_data))

    result = manager.process_json(json_file)

    assert result == []
    manager.push_register.assert_called_once()
    manager.add_multipropietarios.assert_called_once()

def test_push_register(manager):
    cne = 1
    comuna = "TestComuna"
    manzana = "TestManzana"
    predio = "TestPredio"
    enajenantes = json.dumps([{"RUNRUT": "12345678-9", "porcDerecho": 50}])
    adquirentes = json.dumps([{"RUNRUT": "98765432-1", "porcDerecho": 50}])
    fojas = "100"
    fecha = "2023-01-01"
    nmro_inscripcion = "200"

    manager.push_register(cne, comuna, manzana, predio, enajenantes, adquirentes, fojas, fecha, nmro_inscripcion)

    string_sql = (
        f"INSERT INTO Registros (CNE, Comuna, Manzana, Predio, "
        f"Enajenantes, Adquirentes, Fojas, Fecha_Inscripcion, "
        f"Numero_Inscripcion) VALUES "
        f"('{cne}', '{comuna}', '{manzana}', '{predio}', "
        f"'{enajenantes}', '{adquirentes}', '{fojas}', "
        f"'{fecha}', '{nmro_inscripcion}')"
    )
    manager.cursor.execute.assert_called_once_with(string_sql)
    manager.database.commit.assert_called_once()

def test_order_json(manager):
    jsonfile = {
        "F2890": [
            {"fechaInscripcion": "2023-01-01"},
            {"fechaInscripcion": "2022-01-01"},
            {"fechaInscripcion": "2021-01-01"},
        ]
    }
    ordered_json = manager.order_json(jsonfile)

    expected_json = {
        "F2890": [
            {"fechaInscripcion": "2021-01-01"},
            {"fechaInscripcion": "2022-01-01"},
            {"fechaInscripcion": "2023-01-01"},
        ]
    }
    assert ordered_json == expected_json

