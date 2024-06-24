# test_multipropietarios_manager.py

import pytest
from unittest.mock import MagicMock, Mock
from multipropietarios import MultipropietariosManager
from variables_globales import CNE_COMPRAVENTA,CNE_REGULARIZACION_DEL_PATRIMONIO


@pytest.fixture
def manager():
    manager = MultipropietariosManager()
    manager.get_history = MagicMock(return_value=[])  
    manager.get_vigentes = MagicMock(return_value=[])
    manager.does_all_enajenantes_exist = MagicMock(return_value=False)
    manager.get_derecho_cecido = MagicMock(return_value=100)
    manager.get_enajenantes_to_omit = MagicMock(return_value=[])
    manager.get_enajenantes_with_updated_vigencia = MagicMock(return_value=[])
    
    manager.database = MagicMock()
    manager.cursor = MagicMock()
    manager.update_historic_multipropietarios = MagicMock()
    manager.push_multipropietario = MagicMock()
    manager.push_multipropietarios_not_to_omit = MagicMock()
    manager.add_multipropietarios_99 = MagicMock()
    manager.add_multipropietarios_8 = MagicMock()

    manager.delete_multipropietario = MagicMock()
    manager.update_multipropietario = MagicMock()

    manager.get_history = MagicMock(return_value=[])
    manager.get_vigentes = MagicMock(return_value=[])
    manager.push_multipropietario = MagicMock()

    return manager

def test_group_adquirentes(manager):
    adquirentes = [
        {"RUNRUT": "123", "porcDerecho": 50},
        {"RUNRUT": "456", "porcDerecho": 50},
        {"RUNRUT": "123", "porcDerecho": 20},
    ]
    expected = [
        {"RUNRUT": "123", "porcDerecho": 70},
        {"RUNRUT": "456", "porcDerecho": 50},
    ]
    assert manager.group_adquirentes(adquirentes) == expected

def test_process_no_history(manager):
    manager.push_multipropietario = MagicMock()
    data = {
        "bienRaiz": {"comuna": "Test", "manzana": "001", "predio": "0001"},
        "fechaInscripcion": "2023-06-23",
        "fojas": "10",
        "nroInscripcion": "1",
        "adquirentes": [{"RUNRUT": "123", "porcDerecho": 50}, {"RUNRUT": "456", "porcDerecho": 50}]
    }
    manager.process_no_history(data)
    assert manager.push_multipropietario.call_count == 2

def test_process_posterior_form(manager):
    manager.update_multipropietario = MagicMock()
    manager.push_multipropietario = MagicMock()
    data = {
        "bienRaiz": {"comuna": "Test", "manzana": "001", "predio": "0001"},
        "fechaInscripcion": "2023-06-23",
        "fojas": "10",
        "nroInscripcion": "1",
        "adquirentes": [{"RUNRUT": "123", "porcDerecho": 50}, {"RUNRUT": "456", "porcDerecho": 50}]
    }
    historia = [{"id": 1, "Ano_Inscripcion": "2022"}]
    manager.process_posterior_form(data, historia, "2022", "2023")
    assert manager.update_multipropietario.call_count == 1
    assert manager.push_multipropietario.call_count == 2

def test_process_same_year(manager):
    manager.delete_multipropietario = MagicMock()
    manager.push_multipropietario = MagicMock()
    data = {
        "bienRaiz": {"comuna": "Test", "manzana": "001", "predio": "0001"},
        "fechaInscripcion": "2023-06-23",
        "fojas": "10",
        "nroInscripcion": "1",
        "adquirentes": [{"RUNRUT": "123", "porcDerecho": 50}, {"RUNRUT": "456", "porcDerecho": 50}]
    }
    historia = [{"id": 1, "Ano_Inscripcion": "2023"}]
    manager.process_same_year(data, historia)
    assert manager.delete_multipropietario.call_count == 1
    assert manager.push_multipropietario.call_count == 2

def test_escenario_1_8(manager):

    data = {
        "bienRaiz": {
            "comuna": "mock_comuna",
            "manzana": "mock_manzana",
            "predio": "mock_predio"
        },
        "enajenantes": [
            {"RUNRUT": "mock_runrut_1", "porcDerecho": 50},
            {"RUNRUT": "mock_runrut_2", "porcDerecho": 50}
        ],
        "adquirentes": [
            {"RUNRUT": "mock_runrut_3", "porcDerecho": 50},
            {"RUNRUT": "mock_runrut_4", "porcDerecho": 50}
        ],
        "fechaInscripcion": "2023-01-01",
        "fojas": "mock_fojas",
        "nroInscripcion": "mock_nroInscripcion"
    }

    manager.escenario_1_8(data)


    manager.update_historic_multipropietarios.assert_called_once_with(data, [])
    manager.push_multipropietario.assert_any_call({
        "Comuna": data["bienRaiz"]["comuna"],
        "Manzana": data["bienRaiz"]["manzana"],
        "Predio": data["bienRaiz"]["predio"],
        "Fecha_Inscripcion": data["fechaInscripcion"],
        "Ano_Inscripcion": 2023,
        "Fojas": data["fojas"],
        "Numero_Inscripcion": data["nroInscripcion"],
        "RUN_RUT": "mock_runrut_3", 
        "Porcentaje_Derechos": 50,
        "Ano_Vigencia_Inicial": "2023"
    })
    manager.push_multipropietario.assert_any_call({
        "Comuna": data["bienRaiz"]["comuna"],
        "Manzana": data["bienRaiz"]["manzana"],
        "Predio": data["bienRaiz"]["predio"],
        "Fecha_Inscripcion": data["fechaInscripcion"],
        "Ano_Inscripcion": 2023,
        "Fojas": data["fojas"],
        "Numero_Inscripcion": data["nroInscripcion"],
        "RUN_RUT": "mock_runrut_4",  
        "Porcentaje_Derechos": 50,
        "Ano_Vigencia_Inicial": "2023"
    })
    manager.push_multipropietarios_not_to_omit.assert_called_once()




def test_group_adquirentes_y_historicos(manager):

    adquirentes = [
        {"RUN_RUT": "mock_runrut_1", "Porcentaje_Derechos": 30},
        {"RUN_RUT": "mock_runrut_2", "Porcentaje_Derechos": 40}
    ]
    
    enajenantes_historicos = [
        {"RUN_RUT": "mock_runrut_1", "Porcentaje_Derechos": 20},
        {"RUN_RUT": "mock_runrut_3", "Porcentaje_Derechos": 10}
    ]
    

    adquirentes_y_historicos = manager.group_adquirentes_y_historicos(adquirentes, enajenantes_historicos)
    

    assert len(adquirentes_y_historicos) == 3 

    expected_entries = {
        "mock_runrut_1": {"RUN_RUT": "mock_runrut_1", "Porcentaje_Derechos": 50},
        "mock_runrut_2": {"RUN_RUT": "mock_runrut_2", "Porcentaje_Derechos": 40},
        "mock_runrut_3": {"RUN_RUT": "mock_runrut_3", "Porcentaje_Derechos": 10}
    }
    
    for entry in adquirentes_y_historicos:
        run_rut = entry["RUN_RUT"]
        assert entry == expected_entries[run_rut]

def test_add_multipropietarios_99(manager):
    data_99 = {
        "CNE": 99,  
        "bienRaiz": {"comuna": "Test", "manzana": "001", "predio": "0001"},
        "fechaInscripcion": "2023-06-23",
        "fojas": "10",
        "nroInscripcion": "1",
        "adquirentes": [{"RUNRUT": "123", "porcDerecho": 50}, {"RUNRUT": "456", "porcDerecho": 50}]
    }

    manager.add_multipropietarios(data_99)

    manager.add_multipropietarios_99.assert_called_once_with(data_99)
    manager.add_multipropietarios_8.assert_not_called()

def test_add_multipropietarios_8(manager):
    data_8 = {
        "CNE": 8, 
        "bienRaiz": {"comuna": "Test", "manzana": "001", "predio": "0001"},
        "fechaInscripcion": "2023-06-23",
        "fojas": "10",
        "nroInscripcion": "1",
        "adquirentes": [{"RUNRUT": "123", "porcDerecho": 50}, {"RUNRUT": "456", "porcDerecho": 50}]
    }

    manager.add_multipropietarios(data_8)

    manager.add_multipropietarios_99.assert_not_called()
    manager.add_multipropietarios_8.assert_called_once_with(data_8)


def test_recalculate_derechos(manager):

    adquirentes = [
        {"RUNRUT": "123", "porcDerecho": 50},
        {"RUNRUT": "456", "porcDerecho": 50},
    ]

    recalculated_adquirentes = manager.recalculate_derechos(adquirentes)

    assert len(recalculated_adquirentes) == len(adquirentes)

    sum_derechos = sum(adq["porcDerecho"] for adq in recalculated_adquirentes)
    assert sum_derechos <= 100


    for adquirente in recalculated_adquirentes:
        assert adquirente["porcDerecho"] >= 0  
        assert adquirente["porcDerecho"] <= 100  

def test_process_no_history(manager):
    data = {
        "bienRaiz": {"comuna": "Test", "manzana": "001", "predio": "0001"},
        "fechaInscripcion": "2023-06-23",
        "fojas": "10",
        "nroInscripcion": "1",
        "adquirentes": [{"RUNRUT": "123", "porcDerecho": 50}, {"RUNRUT": "456", "porcDerecho": 50}]
    }

    manager.push_multipropietario = MagicMock()

    manager.process_no_history(data)

    assert manager.push_multipropietario.call_count == 2
    expected_calls = [
        {"Comuna": "Test", "Manzana": "001", "Predio": "0001", "Fecha_Inscripcion": "2023-06-23",
         "Ano_Inscripcion": 2023, "Fojas": "10", "Numero_Inscripcion": "1", "RUN_RUT": "123", "Porcentaje_Derechos": 50,
         "Ano_Vigencia_Inicial": "2023"},
        {"Comuna": "Test", "Manzana": "001", "Predio": "0001", "Fecha_Inscripcion": "2023-06-23",
         "Ano_Inscripcion": 2023, "Fojas": "10", "Numero_Inscripcion": "1", "RUN_RUT": "456", "Porcentaje_Derechos": 50,
         "Ano_Vigencia_Inicial": "2023"}
    ]

    for call_args, expected_data in zip(manager.push_multipropietario.call_args_list, expected_calls):
        assert call_args[0][0] == expected_data

def test_process_same_year(manager):

    data = {
        "bienRaiz": {"comuna": "Test", "manzana": "001", "predio": "0001"},
        "fechaInscripcion": "2023-06-23",
        "fojas": "10",
        "nroInscripcion": "1",
        "adquirentes": [{"RUNRUT": "123", "porcDerecho": 50}]
    }
    historia = [{"id": 1}]
    
    manager.delete_multipropietario = MagicMock()

    manager.process_same_year(data, historia)


    assert manager.delete_multipropietario.call_count == 1
    
    expected_delete_call = (1,)
    actual_delete_call = manager.delete_multipropietario.call_args[0]
    assert actual_delete_call == expected_delete_call

def test_does_all_enajenantes_exist(manager):
    data_true = {
        'enajenantes': [
            {"RUNRUT": "mock_runrut_1"},
            {"RUNRUT": "mock_runrut_2"}
        ]
    }

    enajenantes_historicos_true = [
        {"RUN_RUT": "mock_runrut_1"},
        {"RUN_RUT": "mock_runrut_2"},
        {"RUN_RUT": "mock_runrut_3"}
    ]


    manager.does_all_enajenantes_exist = MagicMock(return_value=True)

    assert manager.does_all_enajenantes_exist(data_true, enajenantes_historicos_true) is True

    manager.does_all_enajenantes_exist.assert_called_once_with(data_true, enajenantes_historicos_true)

def test_escenario_3_8_2(manager):
    data = {
        "bienRaiz": {
            "comuna": "TestComuna",
            "manzana": "TestManzana",
            "predio": "TestPredio"
        },
        "enajenantes": [
            {"RUNRUT": "mock_runrut_1", "porcDerecho": 20},
            {"RUNRUT": "mock_runrut_2", "porcDerecho": 30}
        ],
        "adquirentes": [
            {"RUNRUT": "mock_runrut_3", "porcDerecho": 40},
            {"RUNRUT": "mock_runrut_4", "porcDerecho": 10}
        ],
        "fechaInscripcion": "2023-01-01",
        "fojas": "mock_fojas",
        "nroInscripcion": "mock_nroInscripcion"
    }

    manager.get_history.return_value = [
        {"Comuna": "TestComuna", "Manzana": "TestManzana", "Predio": "TestPredio", "Fecha_Inscripcion": "2022-01-01",
         "Ano_Inscripcion": 2022, "Fojas": "mock_fojas", "Numero_Inscripcion": "mock_nroInscripcion", "RUN_RUT": "mock_runrut_1", "Porcentaje_Derechos": 20,
         "Ano_Vigencia_Inicial": "2022"},
        {"Comuna": "TestComuna", "Manzana": "TestManzana", "Predio": "TestPredio", "Fecha_Inscripcion": "2022-01-01",
         "Ano_Inscripcion": 2022, "Fojas": "mock_fojas", "Numero_Inscripcion": "mock_nroInscripcion", "RUN_RUT": "mock_runrut_2", "Porcentaje_Derechos": 30,
         "Ano_Vigencia_Inicial": "2022"}
    ]

    manager.get_vigentes.return_value = [
        {"Comuna": "TestComuna", "Manzana": "TestManzana", "Predio": "TestPredio", "Fecha_Inscripcion": "2022-01-01",
         "Ano_Inscripcion": 2022, "Fojas": "mock_fojas", "Numero_Inscripcion": "mock_nroInscripcion", "RUN_RUT": "mock_runrut_1", "Porcentaje_Derechos": 20,
         "Ano_Vigencia_Inicial": "2022"},
        {"Comuna": "TestComuna", "Manzana": "TestManzana", "Predio": "TestPredio", "Fecha_Inscripcion": "2022-01-01",
         "Ano_Inscripcion": 2022, "Fojas": "mock_fojas", "Numero_Inscripcion": "mock_nroInscripcion", "RUN_RUT": "mock_runrut_2", "Porcentaje_Derechos": 30,
         "Ano_Vigencia_Inicial": "2022"}
    ]


    manager.escenario_3_8_2(data)

    expected_calls = [
        {"Comuna": "TestComuna", "Manzana": "TestManzana", "Predio": "TestPredio", "Fecha_Inscripcion": "2023-01-01",
         "Ano_Inscripcion": 2023, "Fojas": "mock_fojas", "Numero_Inscripcion": "mock_nroInscripcion", "RUN_RUT": "mock_runrut_3",
         "Porcentaje_Derechos": 40 * (100 / 100), "Ano_Vigencia_Inicial": "2023"},
        {"Comuna": "TestComuna", "Manzana": "TestManzana", "Predio": "TestPredio", "Fecha_Inscripcion": "2023-01-01",
         "Ano_Inscripcion": 2023, "Fojas": "mock_fojas", "Numero_Inscripcion": "mock_nroInscripcion", "RUN_RUT": "mock_runrut_4",
         "Porcentaje_Derechos": 10 * (100 / 100), "Ano_Vigencia_Inicial": "2023"}
    ]

    assert manager.push_multipropietario.call_count == 2
    for call_args, expected_data in zip(manager.push_multipropietario.call_args_list, expected_calls):
        assert call_args[0][0] == expected_data

    manager.update_historic_multipropietarios.assert_not_called()

def test_escenario_4_8(manager):
    data = {
        "bienRaiz": {
            "comuna": "TestComuna",
            "manzana": "TestManzana",
            "predio": "TestPredio"
        },
        "enajenantes": [
            {"RUNRUT": "mock_runrut_1", "porcDerecho": 20},
            {"RUNRUT": "mock_runrut_2", "porcDerecho": 30}
        ],
        "adquirentes": [
            {"RUNRUT": "mock_runrut_3", "porcDerecho": 40},
            {"RUNRUT": "mock_runrut_4", "porcDerecho": 10}
        ],
        "fechaInscripcion": "2023-01-01",
        "fojas": "mock_fojas",
        "nroInscripcion": "mock_nroInscripcion"
    }

    manager.escenario_4_8(data)

    expected_calls = [
        {
            "Comuna": data["bienRaiz"]["comuna"],
            "Manzana": data["bienRaiz"]["manzana"],
            "Predio": data["bienRaiz"]["predio"],
            "Fecha_Inscripcion": data["fechaInscripcion"],
            "Ano_Inscripcion": 2023,
            "Fojas": data["fojas"],
            "Numero_Inscripcion": data["nroInscripcion"],
            "RUN_RUT": "mock_runrut_3", 
            "Porcentaje_Derechos": 40,
            "Ano_Vigencia_Inicial": "2023"
        },
        {
            "Comuna": data["bienRaiz"]["comuna"],
            "Manzana": data["bienRaiz"]["manzana"],
            "Predio": data["bienRaiz"]["predio"],
            "Fecha_Inscripcion": data["fechaInscripcion"],
            "Ano_Inscripcion": 2023,
            "Fojas": data["fojas"],
            "Numero_Inscripcion": data["nroInscripcion"],
            "RUN_RUT": "mock_runrut_4",  
            "Porcentaje_Derechos": 10,
            "Ano_Vigencia_Inicial": "2023"
        }
    ]

    assert manager.push_multipropietario.call_count == 2
    for call_args, expected_data in zip(manager.push_multipropietario.call_args_list, expected_calls):
        assert call_args[0][0] == expected_data

    manager.update_historic_multipropietarios.assert_called_once_with(data, [])
    manager.push_multipropietarios_not_to_omit.assert_called_once()